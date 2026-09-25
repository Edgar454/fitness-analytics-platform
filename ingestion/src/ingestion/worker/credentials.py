import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.src.models.fitness.user import Provider, UserCredential


async def get_decrypted_credentials(
    db: AsyncSession,
    kms_client,
    user_id: int,
    provider: Provider,
) -> dict[str, Any]:
    """
    Retrieve the active credentials for a user/provider pair
    and decrypt the stored payload using AWS KMS.
    """

    stmt = (
        select(UserCredential)
        .where(
            UserCredential.user_id == user_id,
            UserCredential.provider == provider,
            UserCredential.active.is_(True),
        )
        .order_by(UserCredential.created_at.desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    credential = result.scalar_one_or_none()

    if credential is None:
        raise ValueError(
            f"No active credentials found for "
            f"user {user_id} and provider {provider.value}"
        )

    response = await kms_client.decrypt(
        CiphertextBlob=credential.encrypted_payload,
    )

    try:
        credentials = json.loads(
            response["Plaintext"].decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"Invalid credential payload for "
            f"user {user_id} and provider {provider.value}"
        ) from exc

    if not isinstance(credentials, dict):
        raise ValueError(
            f"Credential payload for "
            f"user {user_id} and provider {provider.value} "
            f"must be a dictionary"
        )

    return credentials