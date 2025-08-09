import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from fastapi import Request

router = APIRouter()

# ✅ Load JSON DB once at startup
with open("data/CaseSpecifications.json", "r") as f:
    CASE_SPECS_DB = json.load(f)

# ✅ Your server base URL (adjust later when deployed)


def convert_case_spec_for_frontend(case_spec_data: dict, base_url: str):
    """
    Converts backend JSON to a frontend-friendly grouped config.
    Groups by Interior, Exterior, Loose for direct React Native use.
    """
    grouped_configs = {
        "interior": {},
        "exterior": {},
        "loose": {}
    }

    components = case_spec_data.get("components", [])
    subcomponents = case_spec_data.get("subComponents", [])

    for comp in components:
        comp_name = comp["name"]
        comp_type = comp["type"].lower()  # interior/exterior/loose

        # Collect parts & reference images
        parts = []
        refs = []
        for sub in subcomponents:
            if sub["component"] == comp_name:
                parts.append(sub["name"])
                refs.append(f"{base_url}/{sub['referenceImage']}")

        grouped_configs[comp_type][comp_name] = {
            "name": comp_name,
            "image": f"{base_url}/{comp.get('mainImage', case_spec_data['mainImagePath'])}",
            "parts": parts,
            "referenceImages": [f"{img}" for img in refs]
        }

    return grouped_configs

@router.get("/get_case_spec")
async def get_case_spec(request: Request,case_code: str = Query(..., description="Case Specification Code, e.g., KB121")):
    try:
        BASE_URL = f"http://{request.url.hostname}:8000"
        case_data = CASE_SPECS_DB.get(case_code)
        if not case_data:
            return JSONResponse(content={"status": "not_found"}, status_code=404)

        frontend_config = convert_case_spec_for_frontend(case_data, BASE_URL)

        return JSONResponse(content={
            "status": "success",
            "caseSpec": case_code,
            "modelName": case_data["modelName"],
            "variantName": case_data["variantName"],
            "mainImagePath": f"{BASE_URL}/{case_data['mainImagePath']}",
            "frontendConfig": frontend_config,
            "fullData": case_data  # Full raw JSON for debugging or backend use
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
