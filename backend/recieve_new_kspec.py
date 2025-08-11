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
    if os.path.isabs(abs_path):
        rel_path = os.path.relpath(abs_path, os.path.abspath(BASE_DATA_DIR)).replace("\\", "/")
        return f"data/{rel_path}"
    else:
        clean_path = abs_path.replace("\\", "/")
        if not clean_path.startswith("data/"):
            return f"data/{clean_path}"
        return clean_path


# ---------- helpers for dedupe/normalization ----------
def _norm(s: str):
    return (s or "").strip().lower()


def _sub_key(sub: dict):
    # use (component, name) pair as identity
    return (_norm(sub.get("component")), _norm(sub.get("name")))


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
            file_ext = os.path.splitext(source_path)[1]
            new_filename = f"car_main{file_ext}"
            target_path = os.path.join(target_dir, new_filename)

            print(f"📸 Copying main image: {source_path} → {target_path}")
            shutil.copy2(source_path, target_path)
            kspec_data["mainImagePath"] = to_relative_url(target_path)
            print(f"📸 Main image URL: {kspec_data['mainImagePath']}")
        else:
            print(f"⚠️ Main image not found or not specified: {kspec_data.get('mainImagePath')}")

        # === Handle Components ===
        all_subcomponents = []

        components = kspec_data.get("components", [])
        # count nested subcomponents
        nested_count = sum(len(c.get("subComponents", [])) for c in components)
        # root-level list from payload
        root_subcomponents = kspec_data.get("subComponents", [])

        # 🔒 If any nested subs exist, ignore the root list to prevent double counting
        if nested_count > 0:
            root_subcomponents = []

        seen = set()  # for de-duplication across all sources

        for comp in components:
            comp_name_raw = comp["name"]
            comp_dir_name = comp_name_raw.replace(" ", "")
            ref_dir = os.path.join(REFERENCE_DIR, model_code, comp_dir_name)
            model_dir = os.path.join(MODELS_DIR, model_code, comp_dir_name)
            os.makedirs(ref_dir, exist_ok=True)
            os.makedirs(model_dir, exist_ok=True)

            # --- Copy Component Main Image ---
            if comp.get("mainImage") and os.path.exists(comp["mainImage"]):
                source_path = comp["mainImage"]
                file_ext = os.path.splitext(source_path)[1]
                new_filename = f"{comp_dir_name}_main{file_ext}"
                target_path = os.path.join(ref_dir, new_filename)

                print(f"🖼️ Copying component image: {source_path} → {target_path}")
                shutil.copy2(source_path, target_path)
                comp["mainImage"] = to_relative_url(target_path)
                print(f"🖼️ Component image URL: {comp['mainImage']}")
            else:
                print(f"⚠️ Component main image not found: {comp.get('mainImage')}")

            # --- Copy Model Files ---
            pipeline = comp.get("pipelineConfig", {})
            model_name_mapping = {
                "YOLO_DONTDETECT": "dontdetect",
                "YOLO_ROIDETECT": "roi_detect",
                "YOLO_SIMPLEDETECT": "simple_detect",
            }

            for model_key in ["YOLO_DONTDETECT", "YOLO_ROIDETECT", "YOLO_SIMPLEDETECT"]:
                model_path = pipeline.get(model_key)
                if model_path and model_path != "SKIP" and os.path.exists(model_path):
                    source_path = model_path
                    file_ext = os.path.splitext(source_path)[1]
                    model_type = model_name_mapping[model_key]
                    new_filename = f"{comp_dir_name}_{model_type}{file_ext}"
                    target_path = os.path.join(model_dir, new_filename)

                    print(f"🤖 Copying model {model_key}: {source_path} → {target_path}")
                    shutil.copy2(source_path, target_path)
                    pipeline[model_key] = os.path.relpath(target_path).replace("\\", "/")
                    print(f"🤖 Model path updated: {pipeline[model_key]}")
                elif model_path and model_path != "SKIP":
                    print(f"⚠️ Model file not found: {model_path}")

            # --- Copy Subcomponents from individual components (if any) ---
            for sub_idx, sub in enumerate(comp.get("subComponents", [])):
                # ensure component field is set for consistent keys
                sub.setdefault("component", comp_name_raw)

                if sub.get("referenceImage") and os.path.exists(sub["referenceImage"]):
                    source_path = sub["referenceImage"]
                    file_ext = os.path.splitext(source_path)[1]
                    sub_name_slug = sub.get("name", f"subcomp_{sub_idx}").replace(" ", "_").lower()
                    new_filename = f"{comp_dir_name}_{sub_name_slug}{file_ext}"
                    target_path = os.path.join(ref_dir, new_filename)

                    print(f"📎 Copying reference image: {source_path} → {target_path}")
                    shutil.copy2(source_path, target_path)
                    sub["referenceImage"] = to_relative_url(target_path)
                    print(f"📎 Reference image URL: {sub['referenceImage']}")

                # dedupe guard
                k = _sub_key(sub)
                if k not in seen:
                    seen.add(k)
                    all_subcomponents.append(sub)

        # --- Copy Subcomponents from root level (only if we didn't ignore them) ---
        for sub_idx, sub in enumerate(root_subcomponents):
            comp_dir_name = sub.get("component", "Unknown").replace(" ", "")
            ref_dir = os.path.join(REFERENCE_DIR, model_code, comp_dir_name)
            os.makedirs(ref_dir, exist_ok=True)

            if sub.get("referenceImage") and os.path.exists(sub["referenceImage"]):
                source_path = sub["referenceImage"]
                file_ext = os.path.splitext(source_path)[1]
                sub_name_slug = sub.get("name", f"subcomp_{sub_idx}").replace(" ", "_").lower()
                new_filename = f"{comp_dir_name}_{sub_name_slug}{file_ext}"
                target_path = os.path.join(ref_dir, new_filename)

                print(f"📎 Copying root subcomponent reference image: {source_path} → {target_path}")
                shutil.copy2(source_path, target_path)
                sub["referenceImage"] = to_relative_url(target_path)
                print(f"📎 Root subcomponent reference image URL: {sub['referenceImage']}")

            # dedupe guard
            k = _sub_key(sub)
            if k not in seen:
                seen.add(k)
                all_subcomponents.append(sub)

        # --- Rebuild each component's subComponents from deduped flat list (keeps counts in sync) ---
        by_comp = {}
        for s in all_subcomponents:
            by_comp.setdefault(s.get("component"), []).append(s)

        for c in components:
            c_name = c["name"]
            c["subComponents"] = by_comp.get(c_name, [])
            c["totalSubComponents"] = len(c["subComponents"])

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
            "components": components,                  # use synced components
            "subComponents": all_subcomponents,        # deduped canonical flat list
        }

        # === Save back to CaseSpecifications.json ===
        with open(CASE_SPECS_FILE, "w", encoding="utf-8") as f:
            json.dump(case_specs, f, indent=2, ensure_ascii=False)

        return JSONResponse({
            "success": True,
            "message": "KSpec uploaded and appended to CaseSpecifications.json successfully",
            "model_code": model_code,
            "components_count": len(components),
            "total_models": len(case_specs),
            "case_specs_file": CASE_SPECS_FILE.replace("\\", "/"),
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
