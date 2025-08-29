import pandas as pd
from math import ceil

def read_excel_to_df(file_bytes: bytes, **kwargs) -> pd.DataFrame:
    return pd.read_excel(file_bytes, engine="openpyxl", **kwargs)

def to_int_ceil(series):
    return series.apply(lambda x: int(ceil(float(x))))

def normalize_str(x) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and pd.isna(x):
        return ""
    return str(x).strip()
