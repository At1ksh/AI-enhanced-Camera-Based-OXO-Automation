import pandas as pd
import re
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from utils.ocr_utils import run_ocr

router = APIRouter()

# ✅ Load and normalize CSV
WORKER_DF = pd.read_csv("data/CalLineWorkerSheet.csv")
WORKER_DF.columns = WORKER_DF.columns.str.strip()
WORKER_DF["P.No"] = WORKER_DF["P.No"].astype(str).str.strip()
WORKER_DF["Name"] = WORKER_DF["Name"].astype(str).str.strip()
WORKER_DF["Department"] = WORKER_DF["Department"].astype(str).str.strip()

VALID_PNOS = set(WORKER_DF["P.No"])

@router.post("/verify_person")
async def verify_person(file: UploadFile = File(...)):
    try:
        all_texts = run_ocr(await file.read())
        combined_text = " ".join(all_texts).lower()

        print("\n=== OCR RAW TEXT ===")
        print(combined_text)
        print("====================")

        candidates = list(re.findall(r"\b\d{5,7}\b", combined_text))
        print(f"Detected candidate numbers: {candidates}")

        best_match, best_score = None, -1
        for match in candidates:
            index = combined_text.find(match)
            context = combined_text[max(0, index - 20): index + len(match) + 20]
            score = 0
            if "p.no" in context or "p no" in context or "p." in context or "p " in context:
                score += 3
            if "ticket" in context:
                score += 2

            if score > best_score:
                best_score = score
                best_match = match

        print(f"✅ Best match (based on scoring): {best_match}, score: {best_score}")

        if best_match and best_match in VALID_PNOS:
            row = WORKER_DF.loc[WORKER_DF["P.No"] == best_match].iloc[0]
            return JSONResponse(content={
                "status": "verified",
                "pno": best_match,
                "name": row.get("Name", "Unknown"),
                "department": row.get("Department", "Unknown")
            })

        print("❌ No matching P.No found in CSV.")
        return JSONResponse(content={
            "status": "not_found",
            "detected": candidates
        })

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
