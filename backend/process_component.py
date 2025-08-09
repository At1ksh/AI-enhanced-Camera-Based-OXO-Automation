import os
import cv2
import numpy as np
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from fuzzywuzzy import fuzz
import json

from utils.ocr_utils import run_ocr  # ✅ Your existing OCR utility

router = APIRouter()

# ✅ Load Case Specs DB
with open("data/CaseSpecifications.json", "r") as f:
    CASE_SPECS_DB = json.load(f)

BASE_URL = "http://172.20.10.2:8000"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

MODEL_CACHE = {}

# ============================== #
# ✅ UTILS
# ============================== #
def load_yolo_obb(model_path: str):
    if model_path not in MODEL_CACHE:
        MODEL_CACHE[model_path] = YOLO(model_path)
    return MODEL_CACHE[model_path]

def run_yolo_obb(model_path: str, img: np.ndarray):
    model = load_yolo_obb(model_path)
    results = model.predict(img, verbose=False)
    detections = []
    boxes = []
    for r in results:
        names = r.names
        for obb in r.obb:
            cls_id = int(obb.cls[0].item())
            conf = float(obb.conf[0].item())
            detections.append({"class": names[cls_id].lower(), "confidence": conf})
            boxes.append(obb.xyxyxyxy.cpu().numpy())  # 4-point rotated bbox
    return detections, boxes

def crop_highest_conf_roi(img: np.ndarray, boxes: list):
    """
    Crop highest confidence rotated box ROI and return perspective-transformed ROI.
    """
    if not boxes:
        return img  # No cropping if no ROI

    # Take first highest-conf box (already highest conf from YOLO ordering)
    points = boxes[0].reshape(4, 2).astype(np.float32)

    # Order points for perspective transform
    rect = np.zeros((4, 2), dtype="float32")
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]      # top-left
    rect[2] = points[np.argmax(s)]      # bottom-right
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]   # top-right
    rect[3] = points[np.argmax(diff)]   # bottom-left

    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxWidth = int(max(widthA, widthB))
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
    return warped

def convert_to_bw(img: np.ndarray):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.merge([gray, gray, gray])  # keep 3 channels

def parse_csv(val: str):
    return [v.strip().lower() for v in val.split(",") if v.strip() and v.lower() != "skip"]

# ============================== #
# ✅ MAIN PIPELINE
# ============================== #
@router.post("/process_component")
async def process_component(
    file: UploadFile = File(...),
    case_spec: str = Form(...),
    component: str = Form(...),
    part_name: str = Form(...),
    full_vin: str = Form(...)
):
    try:
        # ✅ Load image
        img_bytes = await file.read()
        img_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        
        # ✅ Store original image copy for final saving
        img_copy = img.copy()

        # ✅ Get pipeline config
        comp_config = next(
            (c for c in CASE_SPECS_DB[case_spec]["components"] if c["name"] == component),
            None
        )
        if not comp_config:
            return JSONResponse({"status": "error", "message": "Component config not found"}, status_code=400)

        pipeline = comp_config["pipelineConfig"]
        processed_img = img.copy()
        verdict = "ok"
        debug_step = ""
        debug_info = {}

        # === YOLO_DONTDETECT ===
        if verdict == "ok" and pipeline["YOLO_DONTDETECT"] != "SKIP":
            detections, _ = run_yolo_obb(pipeline["YOLO_DONTDETECT"], processed_img)
            blocked = parse_csv(pipeline["YOLO_DONTDETECTANNOTATION"])
            detected_classes = [d["class"] for d in detections]
            debug_info["dont_detected"] = detected_classes
            if any(cls in blocked for cls in detected_classes):
                verdict, debug_step = "notok", "YOLO_DONTDETECT"

        # === YOLO_ROIDETECT ===
        if verdict == "ok" and pipeline["YOLO_ROIDETECT"] != "SKIP":
            detections, boxes = run_yolo_obb(pipeline["YOLO_ROIDETECT"], processed_img)
            debug_info["roi_detected"] = [d["class"] for d in detections]
            if detections:
                processed_img = crop_highest_conf_roi(processed_img, boxes)
            else:
                verdict, debug_step = "notok", "YOLO_ROIDETECT"

        # === YOLO_CONVERTTOBW ===
        if verdict == "ok" and pipeline["YOLO_CONVERTTOBW"] == "YES":
            processed_img = convert_to_bw(processed_img)

        # === YOLO_SIMPLEDETECT ===
        if verdict == "ok" and pipeline["YOLO_SIMPLEDETECT"] != "SKIP":
            detections, _ = run_yolo_obb(pipeline["YOLO_SIMPLEDETECT"], processed_img)
            required = parse_csv(pipeline["YOLO_SIMPLEDETECTANNOTATION"])
            detected_classes = [d["class"] for d in detections]
            debug_info["simple_detected"] = detected_classes
            
            # If annotation is "SKIP", act like DONTDETECT - fail if anything is detected
            if pipeline["YOLO_SIMPLEDETECTANNOTATION"].strip().upper() == "SKIP":
                if detections:  # If any detections found, fail
                    verdict, debug_step = "notok", "YOLO_SIMPLEDETECT"
            else:
                # Normal behavior - check if all required classes are detected
                if not all(req in detected_classes for req in required):
                    verdict, debug_step = "notok", "YOLO_SIMPLEDETECT"

        # === OCR_DETECT ===
        if verdict == "ok" and pipeline["OCR_DETECT"] != "SKIP":
            texts = [t.lower() for t in run_ocr(img_bytes)]
            required = parse_csv(pipeline["OCR_DETECTANNOTATION"])
            debug_info["ocr_texts"] = texts
            matched = all(any(fuzz.partial_ratio(req, text) > 70 for text in texts) for req in required)
            if not matched:
                verdict, debug_step = "notok", "OCR_DETECT"

        # ✅ Save Results (only original image with verdict-based naming)
        save_dir = os.path.join(RESULTS_DIR, f"{full_vin} (Ongoing)", component)
        os.makedirs(save_dir, exist_ok=True)
        safe_name = part_name.replace(" ", "_")

        result_path = os.path.join(save_dir, f"{verdict.upper()}-{safe_name}.jpg")
        cv2.imwrite(result_path, img_copy)

        return JSONResponse({
            "status": "success",
            "verdict": verdict,
            "debug_step": debug_step,
            "debug_info": debug_info,
            "saved_image": f"{BASE_URL}/{result_path.replace(os.sep, '/')}"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
