import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.src.models.fitness.user import Provider, UserCredential


class CredentialService:
    def __init__(
        self,
        db: AsyncSession,
        kms_client,
        kms_key_id: str,
    ):
        self.db = db
        self.kms_client = kms_client
        self.kms_key_id = kms_key_id

    async def create_credential(
        self,
        user_id: int,
        provider: Provider,
        credentials: dict[str, Any],
    ) -> UserCredential:

        payload = json.dumps(credentials).encode("utf-8")

        response = self.kms_client.encrypt(
            KeyId=self.kms_key_id,
            Plaintext=payload,
        )

        credential = UserCredential(
            user_id=user_id,
            provider=provider,
            encrypted_payload=response["CiphertextBlob"],
            active=True,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(credential)

        await self.db.commit()
        await self.db.refresh(credential)

        return credential

    async def get_user_credentials(
        self,
        user_id: int,
    ) -> list[UserCredential]:

        result = await self.db.execute(
            select(UserCredential)
            .where(UserCredential.user_id == user_id)
            .order_by(UserCredential.created_at)
        )

        return list(result.scalars().all())