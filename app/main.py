from fastapi import FastAPI
from .db import init_db
from . import storage
from .routes import jobs


app = FastAPI(title="Clipper API - scaffold")


@app.on_event("startup")
def on_startup():
    init_db()
    # Ensure the uploads bucket exists in MinIO for presigned URLs
    try:
        storage.ensure_bucket("uploads")
    except Exception:
        # non-fatal here; bucket creation may be handled elsewhere
        pass


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(jobs.router, prefix="/jobs")
