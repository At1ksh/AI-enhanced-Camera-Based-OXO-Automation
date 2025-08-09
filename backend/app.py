from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# ✅ Import your existing routes
from routes.verify_person import router as verify_person_router
from routes.verify_vin import router as verify_vin_router
from routes.get_case_spec import router as get_case_spec_router  # <-- NEW
from routes.process_component import router as process_component_router
from routes.initialize_audit import router as initializer_audit_router 
from routes.finalize_audit import router as finalize_audit_router
from routes.recieve_new_kspec import router as recieve_kspec_router
from routes.manage_kspecs import router as manage_kspecs_router
from routes.manage_vins import router as manage_vins_router
from routes.manage_workers import router as manage_workers_router
app = FastAPI()

# ✅ Serve static files (images, reference files, models)
# This ensures URLs like http://<ip>:8000/data/reference_images/... work
app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/health")
async def health_check():
    return{"status":"ok"}

# ✅ Include all routes
app.include_router(verify_person_router)
app.include_router(verify_vin_router)
app.include_router(get_case_spec_router)  # <-- NEW
app.include_router(process_component_router)
app.include_router(initializer_audit_router)
app.include_router(finalize_audit_router)
app.include_router(recieve_kspec_router)
app.include_router(manage_kspecs_router)
app.include_router(manage_vins_router)
app.include_router(manage_workers_router)

