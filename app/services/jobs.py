import uuid
from typing import Optional

from ..db import SessionLocal
from ..models import Project, ProjectStatus
from .. import storage


def create_project_with_upload(fileobj, filename: str, content_type: str, duration_hint_sec: Optional[float] = None):
    """Store uploaded file to MinIO and create a Project row. Returns the Project instance.

    `fileobj` should be a Starlette UploadFile or a file-like object.
    """
    session = SessionLocal()
    try:
        project_id = "prj_" + uuid.uuid4().hex[:12]
        key = f"{project_id}/source/{filename}"
        bucket = "uploads"

        # ensure bucket exists
        storage.ensure_bucket(bucket)

        # upload file stream
        storage.upload_fileobj(bucket, key, fileobj, content_type=content_type)

        source_url = storage.object_s3_url(bucket, key)

        proj = Project(
            id=project_id,
            filename=filename,
            content_type=content_type,
            source_video_url=source_url,
            duration_sec=duration_hint_sec,
            status=ProjectStatus.queued,
        )
        session.add(proj)
        session.commit()
        session.refresh(proj)
        return proj
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
