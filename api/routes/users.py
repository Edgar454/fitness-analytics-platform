import os

import boto3

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.src.config import Config
from ingestion.src.database import get_db
from api.models.credentials import (
    CredentialCreate,
    CredentialResponse,
)
from api.models.user import UserCreate, UserResponse
from api.services.credentials_service import CredentialService
from api.services.auth_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def get_kms_client():
    return boto3.client("kms")


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    return UserService(db)


def get_credential_service(
    db: AsyncSession = Depends(get_db),
) -> CredentialService:
    return CredentialService(
        db=db,
        kms_client=get_kms_client(),
        kms_key_id=os.environ["KMS_CREDENTIALS_KEY_ID"],
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post(
    "/{user_id}/credentials",
    response_model=CredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credential(
    user_id: int,
    data: CredentialCreate,
    service: CredentialService = Depends(get_credential_service),
):
    return await service.create_credential(
        user_id=user_id,
        provider=data.provider,
        credentials=data.credentials,
    )


@router.get(
    "/{user_id}/credentials",
    response_model=list[CredentialResponse],
)
async def get_credentials(
    user_id: int,
    service: CredentialService = Depends(get_credential_service),
):
    return await service.get_user_credentials(user_id)