import asyncio
import json
from datetime import datetime, timedelta, timezone

from ingestion.src.database import RDSConnector
from ingestion.src.models.fitness.user import Provider
from ingestion.src.ingestion.worker.processor import process_job


async def consume(
    provider_name: str,
    sqs_client,
    queue_url: str,
    session_factory: RDSConnector,
    kms_client,
    redis_client,
    since: datetime,
    until: datetime,
    wait_time: int = 20,
) -> None:
    """
    Continuously consume ingestion jobs from an SQS queue.

    Messages are deleted only after successful job processing.
    Failed jobs are left in SQS so they can become visible again
    after the visibility timeout.
    """

    while True:
        response = await sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=wait_time,
        )

        messages = response.get("Messages", [])

        if not messages:
            continue

        for message in messages:
            try:
                body = json.loads(message["Body"])
                job_id = int(body["job_id"])

                provider = Provider(provider_name)

                async with session_factory() as db:
                    await process_job(
                        job_id=job_id,
                        provider=provider,
                        db=db,
                        kms_client=kms_client,
                        redis_client=redis_client,
                        since=since,
                        until=until,
                    )

                await sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message["ReceiptHandle"],
                )

            except Exception as exc:
                # Do NOT delete the message.
                # SQS will make it visible again after the
                # visibility timeout.
                print(
                    f"Failed to process SQS message: {exc}"
                )