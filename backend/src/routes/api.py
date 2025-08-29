from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List
import io
import pandas as pd
from ..services.processing import (
    handle_upload_hyperv, handle_upload_exchange, handle_upload_s3,
    handle_upload_mapping, make_hyperv_report, make_exchange_report,
    make_s3_report, make_summary_report
)

router = APIRouter(prefix="/api")

@router.post("/upload/hyperv")
async def upload_hyperv(file: UploadFile = File(...)):
    try:
        handle_upload_hyperv(await file.read())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload/exchange")
async def upload_exchange(file: UploadFile = File(...)):
    try:
        handle_upload_exchange(await file.read())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload/s3")
async def upload_s3(file: UploadFile = File(...)):
    try:
        handle_upload_s3(await file.read())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload/bin-mapping")
async def upload_mapping(files: List[UploadFile] = File(...)):
    try:
        file_bytes = [await f.read() for f in files]
        filenames = [f.filename for f in files]
        handle_upload_mapping(file_bytes, filenames)
        return {"status": "ok", "files": filenames}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports/hyperv")
async def report_hyperv():
    return JSONResponse(make_hyperv_report())

@router.get("/reports/exchange")
async def report_exchange():
    return JSONResponse(make_exchange_report())

@router.get("/reports/s3")
async def report_s3():
    return JSONResponse(make_s3_report())

@router.get("/reports/summary")
async def report_summary():
    return JSONResponse(make_summary_report())

def _to_excel_bytes(rows: list[dict]) -> bytes:
    if not rows:
        df = pd.DataFrame(columns=["Наименование компании","БИН","Наименование услуги","Количество"])
    else:
        df = pd.DataFrame(rows)
    buff = io.BytesIO()
    with pd.ExcelWriter(buff, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Отчет")
    buff.seek(0)
    return buff.getvalue()

@router.get("/export/{reportType}")
async def export_report(reportType: str):
    rt = reportType.lower()
    if rt == "hyperv":
        rows = make_hyperv_report()
        fname = "report_hyperv.xlsx"
    elif rt == "exchange":
        rows = make_exchange_report()
        fname = "report_exchange.xlsx"
    elif rt == "s3":
        rows = make_s3_report()
        fname = "report_s3.xlsx"
    elif rt == "summary":
        rows = make_summary_report()
        fname = "report_summary.xlsx"
    else:
        raise HTTPException(status_code=400, detail="unknown reportType")

    data = _to_excel_bytes(rows)
    return StreamingResponse(io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={fname}"})
