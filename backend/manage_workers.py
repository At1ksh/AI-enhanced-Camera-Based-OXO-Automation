import os
import pandas as pd
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()
WORKER_FILE = "data/CalLineWorkerSheet.csv"

class Worker(BaseModel):
    name: str
    pno: str
    department: str
  
@router.post("/upload_cal_worker")
async def upload_worker(worker: Worker):
    try:
        if os.path.exists(WORKER_FILE):
            df = pd.read_csv(WORKER_FILE)

            # 🔧 Normalize column names to avoid duplicates
            df.columns = [c.strip() for c in df.columns]

            # 🔒 Trim extra/invalid columns if present
            expected_cols = ["Name", "P.No", "Department"]
            df = df[[c for c in df.columns if c in expected_cols]]
        else:
            df = pd.DataFrame(columns=["Name", "P.No", "Department"])

        match = df["P.No"].astype(str).str.strip() == worker.pno.strip()
        if match.any():
            df.loc[match, ["Name", "Department"]] = [worker.name, worker.department]
        else:
            new_row = pd.DataFrame([{
                "Name": worker.name,
                "P.No": worker.pno,
                "Department": worker.department
            }])
            df = pd.concat([df, new_row], ignore_index=True)

        # 🔒 Save only valid columns in correct order
        df = df[["P.No", "Name", "Department"]]  # Optional reorder
        df.to_csv(WORKER_FILE, index=False)
        return JSONResponse({"status": "success", "message": "Worker uploaded/updated"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@router.get("/workers")
async def get_all_workers():
    try:
        if not os.path.exists(WORKER_FILE):
            return JSONResponse({"workers": []})

        df = pd.read_csv(WORKER_FILE)
        df = df.fillna("").astype(str)
        df.rename(columns={
            "P.No": "pno",
            "Name": "name",
            "Department": "department"
        }, inplace=True)

        return JSONResponse({"workers": df.to_dict(orient="records")})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.delete("/remove_worker/{pno}")
async def delete_worker(pno: str):
    try:
        if not os.path.exists(WORKER_FILE):
            return JSONResponse({"status": "error", "message": "Worker file not found"}, status_code=404)

        df = pd.read_csv(WORKER_FILE)
        df = df[df["P.No"].astype(str).str.strip() != pno.strip()]
        df.to_csv(WORKER_FILE, index=False)
        return JSONResponse({"status": "success", "message": f"Worker {pno} deleted"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
