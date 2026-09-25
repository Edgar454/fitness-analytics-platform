from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.src.models.ingestion.jobs import IngestionJob


async def get_job(
    db: AsyncSession,
    job_id: int,
) -> IngestionJob:
    """
    Retrieve an ingestion job by ID.

    Raises:
        ValueError: If the job does not exist.
    """

    stmt = sa.select(IngestionJob).where(
        IngestionJob.id == job_id
    )

    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if job is None:
        raise ValueError(
            f"Ingestion job {job_id} not found"
        )

    return job


async def add_job_event(
    db: AsyncSession,
    job_id: int,
    event_type: str,
    source: str,
    message: str | None = None,
    error: str | None = None,
    records_processed: int | None = None,
) -> None:
    """
    Request a job lifecycle transition.

    PostgreSQL is responsible for:
    - locking the job
    - validating the transition
    - inserting the immutable event
    - updating the job snapshot
    """

    await db.execute(
        sa.text(
            """
            SELECT ingestion.add_job_event(
                :job_id,
                :event_type,
                :source,
                :message,
                :error,
                :records_processed
            )
            """
        ),
        {
            "job_id": job_id,
            "event_type": event_type,
            "source": source,
            "message": message,
            "error": error,
            "records_processed": records_processed,
        },
    )

    await db.commit()


async def start_job(
    db: AsyncSession,
    job_id: int,
) -> None:
    """
    QUEUED → PROCESSING
    """

    await add_job_event(
        db=db,
        job_id=job_id,
        event_type="PROCESSING_STARTED",
        source="worker",
    )


async def complete_job(
    db: AsyncSession,
    job_id: int,
    records_processed: int,
) -> None:
    """
    PROCESSING → COMPLETED
    """

    await add_job_event(
        db=db,
        job_id=job_id,
        event_type="COMPLETED",
        source="worker",
        records_processed=records_processed,
    )


async def fail_job(
    db: AsyncSession,
    job_id: int,
    error: str,
) -> None:
    """
    PROCESSING → FAILED
    """

    await add_job_event(
        db=db,
        job_id=job_id,
        event_type="FAILED",
        source="worker",
        error=error,
    )


async def retry_job(
    db: AsyncSession,
    job_id: int,
) -> None:
    """
    FAILED → QUEUED
    """

    await add_job_event(
        db=db,
        job_id=job_id,
        event_type="RETRY",
        source="worker",
    )