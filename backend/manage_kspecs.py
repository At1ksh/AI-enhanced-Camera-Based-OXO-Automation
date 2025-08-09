# routes/manage_kspecs.py

import os
import json
import shutil
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

CASE_SPECS_FILE = "data/CaseSpecifications.json"
REFERENCE_DIR = "data/reference_images"
MODELS_DIR = "data/models"
MAIN_IMAGES_DIR = "data/main_images"

@router.get("/kspecs")
async def list_kspecs():
    try:
        if not os.path.exists(CASE_SPECS_FILE):
            return JSONResponse({"kspecs": []})

        with open(CASE_SPECS_FILE, "r", encoding="utf-8") as f:
            specs = json.load(f)

        response = []
        for model_code, data in specs.items():
            response.append({
                "modelCode": model_code,
                "variantName": data.get("variantName", "Unknown")
            })

        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    
@router.get("/kspec/{model_code}")
async def get_full_kspec(model_code: str):
    try:
        if not os.path.exists(CASE_SPECS_FILE):
            return JSONResponse({"error": "CaseSpecifications.json not found"}, status_code=404)

        with open(CASE_SPECS_FILE, "r", encoding="utf-8") as f:
            specs = json.load(f)

        if model_code not in specs:
            return JSONResponse({"error": f"KSpec {model_code} not found"}, status_code=404)

        return JSONResponse(specs[model_code])

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.delete("/kspec/{model_code}")
async def delete_kspec(model_code: str):
    try:
        if not os.path.exists(CASE_SPECS_FILE):
            return JSONResponse({"status": "error", "message": "CaseSpecifications.json not found"}, status_code=404)

        with open(CASE_SPECS_FILE, "r", encoding="utf-8") as f:
            case_specs = json.load(f)

        if model_code not in case_specs:
            return JSONResponse({"status": "error", "message": f"KSpec {model_code} not found"}, status_code=404)

        # Remove from dictionary
        del case_specs[model_code]

        # Save updated file
        with open(CASE_SPECS_FILE, "w", encoding="utf-8") as f:
            json.dump(case_specs, f, indent=2, ensure_ascii=False)

        # Optionally delete folders
        for base in [REFERENCE_DIR, MODELS_DIR, MAIN_IMAGES_DIR]:
            path = os.path.join(base, model_code)
            if os.path.exists(path):
                shutil.rmtree(path)

        return JSONResponse({"status": "success", "message": f"KSpec {model_code} deleted."})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
