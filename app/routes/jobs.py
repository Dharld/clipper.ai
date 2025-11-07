from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from ..schemas import JobCreateResponse
from ..services import jobs as job_service
from typing import Optional

router = APIRouter()


@router.post("/create", response_model=JobCreateResponse)
async def create_job(
    file: UploadFile = File(...), duration_hint_sec: Optional[float] = Form(None)
):
    """Create a new project by accepting a multipart file upload and storing it in MinIO.
    Returns the created project id and stored source URL.
    """
    try:
        proj = job_service.create_project_with_upload(file, file.filename, file.content_type, duration_hint_sec)
        return JobCreateResponse(project_id=proj.id, source_url=proj.source_video_url, status=proj.status.value, max_size_mb=2048)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
