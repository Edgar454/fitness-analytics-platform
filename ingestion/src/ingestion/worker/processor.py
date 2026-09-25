from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.src.models.fitness.user import Provider

from ingestion.src.ingestion.worker.credentials import (
    get_decrypted_credentials,
)
from ingestion.src.ingestion.worker.handlers import (
    build_ingestion_handlers,
)
from ingestion.src.ingestion.worker.lifecycle import (
    complete_job,
    fail_job,
    get_job,
    start_job,
)


async def process_job(
    job_id: int,
    provider: Provider,
    db: AsyncSession,
    kms_client,
    redis_client,
    since: datetime,
    until: datetime,
) -> int:

    job = await get_job(
        db=db,
        job_id=job_id,
    )

    await start_job(
        db=db,
        job_id=job_id,
    )

    try:

        credentials = await get_decrypted_credentials(
            db=db,
            kms_client=kms_client,
            user_id=job.user_id,
            provider=provider,
        )

        handlers = build_ingestion_handlers(
            provider=job.connector,
            connector_config=credentials,
            redis_client=redis_client,
        )

        records_processed = 0

        for handler in handlers:
            records = await handler.connector.run(
                since=since,
                until=until,
            )

            written = await handler.loader(
                db,
                records,
            )

            records_processed += written

        await complete_job(
            db=db,
            job_id=job_id,
            records_processed=records_processed,
        )

        return records_processed

    except Exception as exc:
        await fail_job(
            db=db,
            job_id=job_id,
            error=str(exc),
        )
        raise