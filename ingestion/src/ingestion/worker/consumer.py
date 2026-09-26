import json
import logging
from datetime import datetime

from ingestion.src.database import DatabaseConnector
from ingestion.src.models.fitness.user import Provider
from ingestion.src.ingestion.worker.processor import process_job


logger = logging.getLogger(__name__)


async def consume(
    provider_name: str,
    sqs_client,
    queue_url: str,
    db_connector: DatabaseConnector,
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

    logger.info(
        "SQS consumer started | provider=%s",
        provider_name,
    )

    while True:
        response = await sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=wait_time,
        )

        messages = response.get("Messages", [])

        if not messages:
            logger.debug("No messages received")
            continue

        for message in messages:
            try:
                body = json.loads(message["Body"])
                job_id = int(body["job_id"])
                provider = Provider(provider_name)

                logger.info(
                    "Received ingestion job | job_id=%s | provider=%s",
                    job_id,
                    provider_name,
                )

                
                logger.info(
                        "Processing ingestion job | job_id=%s",
                        job_id,
                )

                await process_job(
                        job_id=job_id,
                        provider=provider,
                        db_connector=db_connector,
                        kms_client=kms_client,
                        redis_client=redis_client,
                        since=since,
                        until=until,
                    )

                logger.info(
                    "Ingestion job completed | job_id=%s",
                    job_id,
                )

                await sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message["ReceiptHandle"],
                )

                logger.info(
                    "SQS message deleted | job_id=%s",
                    job_id,
                )

            except Exception:
                logger.exception(
                    "Failed to process SQS message"
                )