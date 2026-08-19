# routers/photos.py

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.src.db import get_session
from ingestion.src.models.body import PhotoView
from api.models.progress import ProgressPhotoResponse
from api.services.photo_service import PhotoService

router = APIRouter(
    prefix="/progress/photos",
    tags=["Progress Photos"],
)


@router.post("", response_model=ProgressPhotoResponse)
async def upload_progress_photo(
    file: UploadFile = File(...),
    view: PhotoView = Form(...),
    session: AsyncSession = Depends(get_session),
):
    return await PhotoService.upload(
        session=session,
        file=file,
        view=view,
    )