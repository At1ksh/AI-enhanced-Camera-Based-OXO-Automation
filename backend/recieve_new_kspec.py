import os
import json
import shutil
import uuid
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

router = APIRouter()

# Base paths
BASE_DATA_DIR = "data"  # Relative to project root
REFERENCE_DIR = os.path.join(BASE_DATA_DIR, "reference_images")
MODELS_DIR = os.path.join(BASE_DATA_DIR, "models")
MAIN_IMAGES_DIR = os.path.join(BASE_DATA_DIR, "main_images")
CASE_SPECS_FILE = os.path.join(BASE_DATA_DIR, "CaseSpecifications.json")

def to_relative_url(abs_path: str):
    """Convert an absolute file path to a relative FastAPI static URL."""
    # Convert to forward slashes and make relative to data directory
    if os.path.isabs(abs_path):
        rel_path = os.path.relpath(abs_path, os.path.abspath(BASE_DATA_DIR)).replace("\\", "/")
        return f"data/{rel_path}"
    else:
        # Already relative, just ensure it starts with data/
        clean_path = abs_path.replace("\\", "/")
        if not clean_path.startswith("data/"):
            return f"data/{clean_path}"
        return clean_path

@router.post("/recievenewkspec")
async def recieve_new_kspec(kspec_metadata: str = Form(...)):
    try:
        kspec_data = json.loads(kspec_metadata)
        model_code = kspec_data.get("modelCode", f"MODEL_{uuid.uuid4().hex[:6]}")

        # === Ensure folders exist ===
        os.makedirs(REFERENCE_DIR, exist_ok=True)
        os.makedirs(MODELS_DIR, exist_ok=True)
        os.makedirs(MAIN_IMAGES_DIR, exist_ok=True)

        # === Copy Main Image ===
        if kspec_data.get("mainImagePath") and os.path.exists(kspec_data["mainImagePath"]):
            target_dir = os.path.join(MAIN_IMAGES_DIR, model_code)
            os.makedirs(target_dir, exist_ok=True)

            source_path = kspec_data["mainImagePath"]
            # Rename main image with descriptive name
            file_ext = os.path.splitext(source_path)[1]
            new_filename = f"car_main{file_ext}"
            target_path = os.path.join(target_dir, new_filename)
            
            print(f"ðŸ“¸ Copying main image: {source_path} â†’ {target_path}")
            shutil.copy2(source_path, target_path)
            kspec_data["mainImagePath"] = to_relative_url(target_path)
            print(f"ðŸ“¸ Main image URL: {kspec_data['mainImagePath']}")
        else:
            print(f"âš ï¸ Main image not found or not specified: {kspec_data.get('mainImagePath')}")

        # === Handle Components ===
        all_subcomponents = []

        # First, collect subcomponents from the root level (if any)
        root_subcomponents = kspec_data.get("subComponents", [])
        
        for comp in kspec_data.get("components", []):
            comp_name = comp["name"].replace(" ", "")
            ref_dir = os.path.join(REFERENCE_DIR, model_code, comp_name)
            model_dir = os.path.join(MODELS_DIR, model_code, comp_name)
            os.makedirs(ref_dir, exist_ok=True)
            os.makedirs(model_dir, exist_ok=True)

            # --- Copy Component Main Image ---
            if comp.get("mainImage") and os.path.exists(comp["mainImage"]):
                source_path = comp["mainImage"]
                # Rename component image with descriptive name
                file_ext = os.path.splitext(source_path)[1]
                new_filename = f"{comp_name}_main{file_ext}"
                target_path = os.path.join(ref_dir, new_filename)
                
                print(f"ðŸ–¼ï¸ Copying component image: {source_path} â†’ {target_path}")
                shutil.copy2(source_path, target_path)
                comp["mainImage"] = to_relative_url(target_path)
                print(f"ðŸ–¼ï¸ Component image URL: {comp['mainImage']}")
            else:
                print(f"âš ï¸ Component main image not found: {comp.get('mainImage')}")

            # --- Copy Model Files ---
            pipeline = comp.get("pipelineConfig", {})
            model_name_mapping = {
                "YOLO_DONTDETECT": "dontdetect",
                "YOLO_ROIDETECT": "roi_detect", 
                "YOLO_SIMPLEDETECT": "simple_detect"
            }
            
            for model_key in ["YOLO_DONTDETECT", "YOLO_ROIDETECT", "YOLO_SIMPLEDETECT"]:
                model_path = pipeline.get(model_key)
                if model_path and model_path != "SKIP" and os.path.exists(model_path):
                    source_path = model_path
                    # Rename model with descriptive name
                    file_ext = os.path.splitext(source_path)[1]
                    model_type = model_name_mapping[model_key]
                    new_filename = f"{comp_name}_{model_type}{file_ext}"
                    target_path = os.path.join(model_dir, new_filename)
                    
                    print(f"ðŸ¤– Copying model {model_key}: {source_path} â†’ {target_path}")
                    shutil.copy2(source_path, target_path)
                    # For models, use relative path (not URL) for file system access
                    pipeline[model_key] = os.path.relpath(target_path).replace("\\", "/")
                    print(f"ðŸ¤– Model path updated: {pipeline[model_key]}")
                elif model_path and model_path != "SKIP":
                    print(f"âš ï¸ Model file not found: {model_path}")

            # --- Copy Subcomponents from individual components (if any) ---
            for sub_idx, sub in enumerate(comp.get("subComponents", [])):
                if sub.get("referenceImage") and os.path.exists(sub["referenceImage"]):
                    source_path = sub["referenceImage"]
                    # Rename reference image with descriptive name
                    file_ext = os.path.splitext(source_path)[1]
                    sub_name = sub.get("name", f"subcomp_{sub_idx}").replace(" ", "_").lower()
                    new_filename = f"{comp_name}_{sub_name}{file_ext}"
                    target_path = os.path.join(ref_dir, new_filename)
                    
                    print(f"ðŸ“Ž Copying reference image: {source_path} â†’ {target_path}")
                    shutil.copy2(source_path, target_path)
                    sub["referenceImage"] = to_relative_url(target_path)
                    print(f"ðŸ“Ž Reference image URL: {sub['referenceImage']}")
                all_subcomponents.append(sub)

        # --- Copy Subcomponents from root level ---
        for sub_idx, sub in enumerate(root_subcomponents):
            # Find the component this subcomponent belongs to
            comp_name = sub.get("component", "Unknown").replace(" ", "")
            ref_dir = os.path.join(REFERENCE_DIR, model_code, comp_name)
            os.makedirs(ref_dir, exist_ok=True)
            
            if sub.get("referenceImage") and os.path.exists(sub["referenceImage"]):
                source_path = sub["referenceImage"]
                # Rename reference image with descriptive name
                file_ext = os.path.splitext(source_path)[1]
                sub_name = sub.get("name", f"subcomp_{sub_idx}").replace(" ", "_").lower()
                new_filename = f"{comp_name}_{sub_name}{file_ext}"
                target_path = os.path.join(ref_dir, new_filename)
                
                print(f"ðŸ“Ž Copying root subcomponent reference image: {source_path} â†’ {target_path}")
                shutil.copy2(source_path, target_path)
                sub["referenceImage"] = to_relative_url(target_path)
                print(f"ðŸ“Ž Root subcomponent reference image URL: {sub['referenceImage']}")
            all_subcomponents.append(sub)

        # === Load existing CaseSpecifications.json ===
        if os.path.exists(CASE_SPECS_FILE):
            with open(CASE_SPECS_FILE, "r", encoding="utf-8") as f:
                case_specs = json.load(f)
        else:
            case_specs = {}

        # === Append or Update Model ===
        case_specs[model_code] = {
            "modelName": kspec_data["modelName"],
            "variantName": kspec_data["variantName"],
            "totalInterior": kspec_data["totalInterior"],
            "totalExterior": kspec_data["totalExterior"],
            "totalLoose": kspec_data["totalLoose"],
            "mainImagePath": kspec_data["mainImagePath"],
            "components": kspec_data["components"],
            "subComponents": all_subcomponents
        }

        # === Save back to CaseSpecifications.json ===
        with open(CASE_SPECS_FILE, "w", encoding="utf-8") as f:
            json.dump(case_specs, f, indent=2, ensure_ascii=False)

        return JSONResponse({
            "success": True,
            "message": "KSpec uploaded and appended to CaseSpecifications.json successfully",
            "model_code": model_code,
            "components_count": len(kspec_data.get("components", [])),
            "total_models": len(case_specs),
            "case_specs_file": CASE_SPECS_FILE.replace("\\", "/")
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)