from pydantic import BaseModel
from typing import Optional


class JobCreateRequest(BaseModel):
    filename: str
    content_type: str
    duration_hint_sec: Optional[float] = None


class JobCreateResponse(BaseModel):
    project_id: str
    source_url: str
    status: str
    max_size_mb: int = 2048
