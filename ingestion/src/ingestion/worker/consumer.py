import asyncio
import json
import logging
import os
import signal
from datetime import datetime

from redis import asyncio as redis_asyncio

from ingestion.src.database import DatabaseConnector
from ingestion.src.models.fitness.user import Provider
from ingestion.src.ingestion.worker.processor import process_job


logger = logging.getLogger(__name__)


async def _process_message(
    message: dict,
    provider_name: str,
    sqs_client,
    queue_url: str,
    db_connector: DatabaseConnector,
    kms_client,
    redis_client: redis_asyncio.Redis,
    since: datetime,
    until: datetime,
) -> None:
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

        if os.getenv("LOAD_TEST") == "true":
            await asyncio.sleep(30)

    except Exception:
        logger.exception(
            "Failed to process SQS message"
        )


async def consume(
    provider_name: str,
    sqs_client,
    queue_url: str,
    db_connector: DatabaseConnector,
    kms_client,
    redis_client: redis_asyncio.Redis,
    since: datetime,
    until: datetime,
    wait_time: int = 20,
    max_concurrency: int = 5,
) -> None:
    """
    Continuously consume ingestion jobs from an SQS queue.

    Up to ``max_concurrency`` jobs are processed concurrently.

    Messages are deleted only after successful job processing.
    Failed jobs are left in SQS so they can become visible again
    after the visibility timeout.

    On shutdown, no new jobs are accepted and active jobs are
    allowed to finish before the worker exits.
    """

    logger.info(
        "SQS consumer started | provider=%s | max_concurrency=%s",
        provider_name,
        max_concurrency,
    )

    shutdown_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    def request_shutdown() -> None:
        logger.info(
            "Shutdown requested | provider=%s",
            provider_name,
        )
        shutdown_event.set()

    loop.add_signal_handler(signal.SIGTERM, request_shutdown)
    loop.add_signal_handler(signal.SIGINT, request_shutdown)

    active_tasks: set[asyncio.Task] = set()

    while not shutdown_event.is_set():

        if len(active_tasks) >= max_concurrency:
            _, active_tasks = await asyncio.wait(
                active_tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )

        available_slots = max_concurrency - len(active_tasks)

        response = await sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=min(10, available_slots),
            WaitTimeSeconds=wait_time,
        )

        messages = response.get("Messages", [])

        if not messages:
            logger.debug("No messages received")
            continue

        for message in messages:
            if shutdown_event.is_set():
                break

            task = asyncio.create_task(
                _process_message(
                    message=message,
                    provider_name=provider_name,
                    sqs_client=sqs_client,
                    queue_url=queue_url,
                    db_connector=db_connector,
                    kms_client=kms_client,
                    redis_client=redis_client,
                    since=since,
                    until=until,
                )
            )

            active_tasks.add(task)

    logger.info(
        "Consumer stopping | waiting for %s active task(s)",
        len(active_tasks),
    )

    if active_tasks:
        await asyncio.gather(*active_tasks)

    logger.info(
        "SQS consumer stopped | provider=%s",
        provider_name,
    )