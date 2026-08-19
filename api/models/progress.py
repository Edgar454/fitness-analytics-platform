# schemas/progress.py

from datetime import datetime

from pydantic import BaseModel

from ingestion.src.models.body import PhotoView
from .common import ListResponse

class ProgressPhotoQuery(BaseModel):
    view: PhotoView | None = None

class ProgressPhotoResponse(BaseModel):
    id: int
    view: PhotoView | None = None
    mime_type: str | None = None
    uploaded_at: datetime
    url: str

class ProgressPhotoListResponse(
    ListResponse[ProgressPhotoResponse]
):
    pass