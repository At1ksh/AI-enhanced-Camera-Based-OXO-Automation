
import os
import pandas as pd
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()
VIN_FILE = "data/VINSpecification.csv"

class VINSpec(BaseModel):
    vin: str
    engineNumber: str
    caseSpecCode: str

@router.post("/upload_vin_spec")
async def upload_vin(payload: VINSpec):
    try:
        full_vin = payload.vin.strip()
        short_vin = full_vin[-6:].strip()
        engine_number = payload.engineNumber.strip()
        case_spec = payload.caseSpecCode.strip()

        # Load or create DataFrame
        if os.path.exists(VIN_FILE):
            df = pd.read_csv(VIN_FILE)
        else:
            df = pd.DataFrame(columns=["VIN_NUMBER", "CASE SPECIFICATION", "ENGINE_NUMBER", "FULL_VIN_NUMBER"])

        # Update if short VIN exists
        match = df["VIN_NUMBER"].astype(str).str.strip() == short_vin
        if match.any():
            df.loc[match, ["CASE SPECIFICATION", "ENGINE_NUMBER", "FULL_VIN_NUMBER"]] = [case_spec, engine_number, full_vin]
        else:
            df.loc[len(df)] = [short_vin, case_spec, engine_number, full_vin]

        df.to_csv(VIN_FILE, index=False)
        return JSONResponse({"status": "success", "message": "VIN updated/added"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.get("/list_all_vins")
async def list_all_vins():
    try:
        df = pd.read_csv(VIN_FILE)
        df = df.fillna("").astype(str)
        records = df.to_dict(orient="records")
        return JSONResponse(records)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.delete("/remove_all_vins")
async def remove_all_vins():
    try:
        if os.path.exists(VIN_FILE):
            # Overwrite with just the headers
            df = pd.DataFrame(columns=["VIN_NUMBER", "CASE SPECIFICATION", "ENGINE_NUMBER", "FULL_VIN_NUMBER"])
            df.to_csv(VIN_FILE, index=False)
            return JSONResponse({"status": "success", "message": "All VINs deleted"})
        else:
            return JSONResponse({"status": "success", "message": "VIN file did not exist — nothing to delete"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    
@router.delete("/remove_vin/{short_vin}")  # <- match frontend
async def delete_vin(short_vin: str):
    try:
        if not os.path.exists(VIN_FILE):
            return JSONResponse({"status": "error", "message": "VIN file not found"}, status_code=404)

        df = pd.read_csv(VIN_FILE)
        df = df[df["VIN_NUMBER"].astype(str).str.strip() != short_vin.strip()]
        df.to_csv(VIN_FILE, index=False)
        return JSONResponse({"status": "success", "message": f"VIN {short_vin} deleted"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.get("/vins")
async def list_short_vins():
    try:
        if not os.path.exists(VIN_FILE):
            return JSONResponse({"vins": []})
        
        df = pd.read_csv(VIN_FILE)
        short_vins = df["VIN_NUMBER"].dropna().astype(str).str.strip().tolist()
        return JSONResponse({"vins": short_vins})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
