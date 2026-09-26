from datetime import datetime

from ingestion.src.database import DatabaseConnector

from ingestion.src.models.fitness.user import Provider
from ingestion.src.models.ingestion.jobs import JobStatus

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
    retry_job,
)


async def process_job(
    job_id: int,
    provider: Provider,
    db_connector: DatabaseConnector,
    kms_client,
    redis_client,
    since: datetime,
    until: datetime,
) -> int:

    async with db_connector.session() as db:
        job = await get_job(
            db=db,
            job_id=job_id,
        )

        if job.status == JobStatus.FAILED:
            await retry_job(db, job_id)

        await start_job(db, job_id)

    try:
        async with db_connector.session() as db:
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
                    job.user_id,
                )

                records_processed += written

    except Exception as exc:
        async with db_connector.session() as db:
            await fail_job(
                db=db,
                job_id=job_id,
                error=str(exc),
            )
        raise

    async with db_connector.session() as db:
        await complete_job(
            db=db,
            job_id=job_id,
            records_processed=records_processed,
        )

    return records_processed