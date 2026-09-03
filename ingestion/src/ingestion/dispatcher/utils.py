# src/dispatcher/utils.py

import json
import os

from datetime import datetime, timedelta, timezone
from typing import Any

import boto3
import sqlalchemy as sa

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.fitness.user import User
from src.models.fitness.user import UserCredential
from src.models.ingestion.jobs import IngestionJob


QUEUE_BY_CONNECTOR = {
    "google_health": os.environ["GOOGLE_HEALTH_QUEUE_URL"],
    "fatsecret": os.environ["FATSECRET_QUEUE_URL"],
    "lyfta": os.environ["LYFTA_QUEUE_URL"],
}


def get_sqs_client():
    return boto3.client("sqs")


async def get_active_users(
    db: AsyncSession,
    active_within: timedelta,
) -> list[dict[str, Any]]:
    """
    Return active users together with the providers for which
    they currently have an active credential.

    No credential payload is loaded or decrypted here.
    """

    cutoff = datetime.now(timezone.utc) - active_within

    stmt = (
        select(
            User.id.label("user_id"),
            User.last_active,
        )
        .where(User.last_active >= cutoff)
    )

    result = await db.execute(stmt)
    users = result.all()

    if not users:
        return []

    user_ids = [row.user_id for row in users]

    credential_stmt = (
        select(
            UserCredential.user_id,
            UserCredential.provider,
        )
        .where(
            UserCredential.user_id.in_(user_ids),
            UserCredential.active.is_(True),
        )
    )

    credential_result = await db.execute(credential_stmt)

    providers_by_user: dict[int, set[str]] = {}

    for user_id, provider in credential_result.all():
        providers_by_user.setdefault(user_id, set()).add(
            provider.value
        )

    return [
        {
            "user_id": row.user_id,
            "last_active": row.last_active,
            "providers": providers_by_user.get(
                row.user_id,
                set(),
            ),
        }
        for row in users
    ]


async def create_job(
    db: AsyncSession,
    sqs_client,
    user_id: int,
    connector: str,
) -> int:
    """
    Create a job and enqueue it.

    Job lifecycle:

        CREATED
            ↓
        SQS message
            ↓
        QUEUED

    The SQS message contains only the job ID.
    """

    if connector not in QUEUE_BY_CONNECTOR:
        raise ValueError(f"Unknown connector: {connector}")

    # Create the job in its initial state.
    job = IngestionJob(
        user_id=user_id,
        connector=connector,
        status="CREATED",
        attempt_count=0,
        records_processed=0,
        created_at=datetime.now(timezone.utc),
    )

    db.add(job)

    # Execute INSERT so PostgreSQL generates job.id.
    await db.flush()

    job_id = job.id

    # Persist CREATED before attempting to enqueue.
    await db.commit()

    queue_url = QUEUE_BY_CONNECTOR[connector]

    try:
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(
                {
                    "job_id": job_id,
                }
            ),
        )
    except Exception:
        # Job remains CREATED.
        # It can be retried by the dispatcher later.
        raise

    # SQS accepted the message.
    # Now let PostgreSQL perform the state transition:
    #
    # CREATED + CREATED → QUEUED
    await db.execute(
        sa.text(
            """
            SELECT ingestion.add_job_event(
                :job_id,
                :event_type,
                :source
            )
            """
        ),
        {
            "job_id": job_id,
            "event_type": "CREATED",
            "source": "dispatcher",
        },
    )

    await db.commit()

    return job_id