from __future__ import annotations
import io
from typing import List, Dict
import pandas as pd
from math import ceil

from .filters import EXCLUDE_VMOWNERS, EXCLUDE_CUSTOMERS, EXCLUDE_S3_OWNERS, any_regex_match
from .naming import get_hyperv_service_name, get_exchange_service_name, get_s3_service_name
from ..utils.excel import read_excel_to_df, to_int_ceil, normalize_str
from ..utils.state import AppState, DataStore

# ------------------ Upload handlers ------------------

def handle_upload_hyperv(file_bytes: bytes):
    df = read_excel_to_df(io.BytesIO(file_bytes))
    # required columns
    required = ["VMOwner", "CPUCount", "MemoryGB", "IOPS", "CapacityGB"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Hyper-V: отсутствует столбец '{col}'")

    # Normalize types
    df["VMOwner"] = df["VMOwner"].apply(normalize_str)
    df = df[~df["VMOwner"].apply(lambda x: any_regex_match(x, EXCLUDE_VMOWNERS))].copy()

    # numeric validations
    for col in ["CPUCount", "MemoryGB", "IOPS", "CapacityGB"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # CapacityGB round up
    df["CapacityGB"] = df["CapacityGB"].apply(lambda x: int(ceil(float(x))))

    AppState.update(hyperv=df.to_dict(orient="records"))
    AppState.clear_reports()


def handle_upload_exchange(file_bytes: bytes):
    df = read_excel_to_df(io.BytesIO(file_bytes))
    required = ["CustomerName", "LineDescription", "CurrentPeriod"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Exchange: отсутствует столбец '{col}'")

    df["CustomerName"] = df["CustomerName"].apply(normalize_str)
    df = df[~df["CustomerName"].isin(EXCLUDE_CUSTOMERS)].copy()

    df["CurrentPeriod"] = pd.to_numeric(df["CurrentPeriod"], errors="coerce").fillna(0).astype(int)
    df["LineDescription"] = df["LineDescription"].apply(normalize_str)

    AppState.update(exchange=df.to_dict(orient="records"))
    AppState.clear_reports()


def handle_upload_s3(file_bytes: bytes):
    df = read_excel_to_df(io.BytesIO(file_bytes), header=None)
    # Expecting: B=owner (index 1), C must include "Tenants" (index 2), E=volume (index 4)
    if df.shape[1] < 5:
        raise ValueError("S3: слишком мало столбцов, ожидается минимум 5 (A..E)")

    # keep rows where C contains "Tenants"
    df = df[df[2].astype(str).str.contains("Tenants", case=False, na=False)].copy()

    # rename for clarity
    df = df.rename(columns={1: "Owner", 4: "VolumeGB"})

    df["Owner"] = df["Owner"].apply(normalize_str)
    df = df[~df["Owner"].apply(lambda x: any_regex_match(x, EXCLUDE_S3_OWNERS))].copy()

    df["VolumeGB"] = pd.to_numeric(df["VolumeGB"], errors="coerce").fillna(0)
    df["VolumeGB"] = df["VolumeGB"].apply(lambda x: int(ceil(float(x))))

    AppState.update(s3=df.to_dict(orient="records"))
    AppState.clear_reports()

# ------------------ Mapping upload ------------------

def read_mapping(file_bytes: bytes) -> Dict[str, dict]:
    df = read_excel_to_df(io.BytesIO(file_bytes))
    cols = [c.lower() for c in df.columns]
    # Try to detect columns
    name_col = None
    bin_col = None
    key_col = None
    for c in df.columns:
        lc = c.lower()
        if "наименование" in lc or "company" in lc or "организац" in lc:
            name_col = c
        if "бин" in lc or "bin" in lc:
            bin_col = c
        if "ключ" in lc or "key" in lc:
            key_col = c
    if not name_col or not bin_col:
        # fallback to first two columns
        name_col = df.columns[0]
        bin_col = df.columns[1] if df.shape[1] > 1 else df.columns[0]

    if key_col is None:
        # if no explicit key, assume first column is the key
        key_col = df.columns[0]

    mp = {}
    for _, row in df.iterrows():
        key = str(row.get(key_col, "")).strip()
        company = str(row.get(name_col, "")).strip()
        bin_code = str(row.get(bin_col, "")).strip()
        if key:
            mp[key] = {"company_name": company or key, "bin": bin_code or ""}
    return mp


def handle_upload_mapping(file_list: List[bytes], filenames: List[str]):
    map_h, map_e, map_s = {}, {}, {}
    for fb, fn in zip(file_list, filenames):
        low = (fn or "").lower()
        mp = read_mapping(fb)
        if "hyper" in low:
            map_h.update(mp)
        elif "exchange" in low or "mail" in low:
            map_e.update(mp)
        elif "s3" in low:
            map_s.update(mp)
    st = AppState.get()
    if map_h:
        st.map_hyperv = map_h
    if map_e:
        st.map_exchange = map_e
    if map_s:
        st.map_s3 = map_s
    AppState.clear_reports()

# ------------------ Reports ------------------

def make_hyperv_report() -> List[dict]:
    st = AppState.get()
    if st.report_hyperv:
        return st.report_hyperv

    df = pd.DataFrame(st.hyperv)
    if df.empty:
        st.report_hyperv = []
        return st.report_hyperv

    # Aggregate per owner
    agg = df.groupby(["VMOwner", "IOPS"], as_index=False).agg({
        "CPUCount": "sum",
        "MemoryGB": "sum",
        "CapacityGB": "sum",
    })

    rows = []
    for _, r in agg.iterrows():
        owner = r["VMOwner"]
        iops = int(r["IOPS"])

        # mapping
        m = st.map_hyperv.get(owner) or {"company_name": owner, "bin": ""}

        # 3 service rows per owner/io ps
        if r["CapacityGB"] > 0:
            rows.append({
                "Наименование компании": m["company_name"],
                "БИН": m["bin"],
                "Наименование услуги": get_hyperv_service_name("disk", iops),
                "Количество": int(r["CapacityGB"])
            })
        if r["CPUCount"] > 0:
            rows.append({
                "Наименование компании": m["company_name"],
                "БИН": m["bin"],
                "Наименование услуги": get_hyperv_service_name("cpu", iops),
                "Количество": int(r["CPUCount"])
            })
        if r["MemoryGB"] > 0:
            rows.append({
                "Наименование компании": m["company_name"],
                "БИН": m["bin"],
                "Наименование услуги": get_hyperv_service_name("memory", iops),
                "Количество": int(r["MemoryGB"])
            })

    # sort
    rows.sort(key=lambda x: (x["Наименование компании"], x["Наименование услуги"]))
    st.report_hyperv = rows
    return rows


def make_exchange_report() -> List[dict]:
    st = AppState.get()
    if st.report_exchange:
        return st.report_exchange
    df = pd.DataFrame(st.exchange)
    if df.empty:
        st.report_exchange = []
        return st.report_exchange

    df["ServiceName"] = df["LineDescription"].apply(get_exchange_service_name)
    agg = df.groupby(["CustomerName", "ServiceName"], as_index=False)["CurrentPeriod"].sum()

    rows = []
    for _, r in agg.iterrows():
        cust = r["CustomerName"]
        m = st.map_exchange.get(cust) or {"company_name": cust, "bin": ""}
        rows.append({
            "Наименование компании": m["company_name"],
            "БИН": m["bin"],
            "Наименование услуги": r["ServiceName"],
            "Количество": int(r["CurrentPeriod"]),
        })

    rows.sort(key=lambda x: (x["Наименование компании"], x["Наименование услуги"]))
    st.report_exchange = rows
    return rows


def make_s3_report() -> List[dict]:
    st = AppState.get()
    if st.report_s3:
        return st.report_s3

    df = pd.DataFrame(st.s3)
    if df.empty:
        st.report_s3 = []
        return st.report_s3

    df["ServiceName"] = df["Owner"].apply(get_s3_service_name)
    agg = df.groupby(["Owner", "ServiceName"], as_index=False)["VolumeGB"].sum()

    rows = []
    for _, r in agg.iterrows():
        owner = r["Owner"]
        m = st.map_s3.get(owner) or {"company_name": owner, "bin": ""}
        rows.append({
            "Наименование компании": m["company_name"],
            "БИН": m["bin"],
            "Наименование услуги": r["ServiceName"],
            "Количество": int(r["VolumeGB"]),
        })

    rows.sort(key=lambda x: (x["Наименование компании"], x["Наименование услуги"]))
    st.report_s3 = rows
    return rows


def make_summary_report() -> List[dict]:
    st = AppState.get()
    if st.report_summary:
        return st.report_summary

    rows = make_hyperv_report() + make_exchange_report() + make_s3_report()
    # already normalized, just sort by company
    rows.sort(key=lambda x: (x["Наименование компании"], x["Наименование услуги"]))
    st.report_summary = rows
    return rows
