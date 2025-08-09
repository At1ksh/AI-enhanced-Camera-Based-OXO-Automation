import pandas as pd
import re
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from utils.ocr_utils import run_ocr

router = APIRouter()

# ✅ Load and normalize CSV
VIN_DF = pd.read_csv("data/VINSpecification.csv")
VIN_DF.columns = VIN_DF.columns.str.strip()
for col in VIN_DF.columns:
    VIN_DF[col] = VIN_DF[col].astype(str).str.strip()

VIN_MAP = {row["VIN_NUMBER"]: row.to_dict() for _, row in VIN_DF.iterrows()}

@router.post("/verify_vin")
async def verify_vin(file: UploadFile = File(...)):
    try:
        all_texts = run_ocr(await file.read())
        combined_text = " ".join(all_texts).upper()

        print("\n=== OCR RAW TEXT ===")
        print(combined_text)
        print("====================")

        vin_match = re.search(r"\bS[A-Z0-9]{16}\b", combined_text)
        if not vin_match:
            return JSONResponse(content={"status": "not_found", "detected_texts": all_texts})

        full_vin = vin_match.group(0)
        vin_last6 = full_vin[-6:]

        row = VIN_MAP.get(vin_last6, None)
        if row is None:
            return JSONResponse(content={
                "status": "not_found",
                "vin_last6": vin_last6,
                "full_vin_detected": full_vin
            })

        return JSONResponse(content={
            "status": "success",
            "vin": vin_last6,
            "case_spec": row.get("CASE SPECIFICATION", "UNKNOWN"),
            "engine_number": row.get("ENGINE_NUMBER", "UNKNOWN"),
            "full_vin_number": row.get("FULL_VIN_NUMBER", full_vin)
        })

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
