from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.measurements import PhotoView, ProgressPhoto


class PhotoService:
    ALLOWED_MIME_TYPES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(
        self,
        bucket_name: str,
        region: str,
    ):
        self.bucket_name = bucket_name

        self.s3 = boto3.client(
            "s3",
            region_name=region,
        )

    async def upload(
        self,
        session: AsyncSession,
        file: UploadFile,
        view: PhotoView,
    ) -> ProgressPhoto:

        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported image type.",
            )

        extension = self.ALLOWED_MIME_TYPES[file.content_type]

        s3_key = (
            f"progress/"
            f"{view.value}/"
            f"{uuid4()}{extension}"
        )

        content = await file.read()

        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Image exceeds the maximum allowed size.",
            )

        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type,
            )

        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to upload image.",
            ) from exc

        photo = ProgressPhoto(
            view=view,
            s3_key=s3_key,
            mime_type=file.content_type,
            uploaded_at=datetime.now(timezone.utc),
        )

        try:
            session.add(photo)
            await session.commit()
            await session.refresh(photo)

        except Exception:
            await session.rollback()

            # S3 succeeded but DB failed.
            # Remove the orphaned object.
            try:
                self.s3.delete_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                )
            except (BotoCoreError, ClientError):
                # Don't hide the original DB exception.
                pass

            raise

        return photo