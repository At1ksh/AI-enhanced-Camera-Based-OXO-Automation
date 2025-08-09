import os
import json
import shutil
import csv
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

RESULTS_DIR = "results"
WHO_DATA_PATH = "data/WhoData.csv"
os.makedirs(RESULTS_DIR, exist_ok=True)

@router.post("/initialize_audit")
async def initialize_audit(
    full_vin: str = Form(...),
    short_vin: str = Form(...),
    case_spec: str = Form(...),
    variant: str = Form(...),
    engine_number: str = Form(...),
    person_name: str = Form(...),
    person_pno: str = Form(...),
    person_department: str = Form(...),
    components: str = Form(...)  # JSON string of {interior:[], exterior:[], loose:[]}
):
    try:
        # ✅ 1. Remove existing folders if they match VIN
        for folder_name in os.listdir(RESULTS_DIR):
            folder_path_check = os.path.join(RESULTS_DIR, folder_name)
            if os.path.isdir(folder_path_check):
                if folder_name.startswith(full_vin) and (' (Ongoing)' in folder_name or ' (Done)' in folder_name):
                    print(f"Deleting existing folder: {folder_name}")
                    shutil.rmtree(folder_path_check)

        # ✅ 2. Create Results Folder
        folder_name = f"{full_vin} (Ongoing)"
        folder_path = os.path.join(RESULTS_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # ✅ 3. Write InfoBeforeScan.txt
        comps = json.loads(components)
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        day_name = current_time.strftime("%A")

        lines = [
            f"Audit Started: {timestamp}",
            f"Day: {day_name}",
            "",
            f"Person Pno: {person_pno}",
            f"Person Name: {person_name}",
            f"Person Department: {person_department}",
            f"Full VIN: {full_vin}",
            f"Short VIN: {short_vin}",
            f"Case Spec: {case_spec}",
            f"Variant: {variant}",
            f"Engine Number: {engine_number}",
            "",
            "Components to Check:",
        ]
        for section, items in comps.items():
            lines.append(f"[{section.upper()}]")
            lines.extend([f"- {name}" for name in items])
            lines.append("")

        info_path = os.path.join(folder_path, "InfoBeforeScan.txt")
        with open(info_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # ✅ 4. Update WhoData.csv
        updated = False
        rows = []

        # Read existing data if file exists
        if os.path.exists(WHO_DATA_PATH):
            with open(WHO_DATA_PATH, mode="r", encoding="utf-8", newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)

        # Update existing VIN row if present
        for idx, row in enumerate(rows):
            if row and row[0] == full_vin:
                rows[idx] = [full_vin, short_vin, person_pno, person_name, "Ongoing"]
                updated = True
                break

        # Append if not found
        if not updated:
            rows.append([full_vin, short_vin, person_pno, person_name, "Ongoing"])

        # Write back
        with open(WHO_DATA_PATH, mode="w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        return JSONResponse({
            "status": "success",
            "folder_created": folder_path,
            "info_file": info_path
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
