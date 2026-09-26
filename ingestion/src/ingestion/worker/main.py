import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

import aioboto3
from redis.asyncio import Redis

from ingestion.src.database import db_connector
from ingestion.src.ingestion.worker.consumer import consume


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    provider = os.environ["WORKER_PROVIDER"]
    queue_url = os.environ["QUEUE_URL"]
    redis_url = os.environ["REDIS_URL"]
    aws_region = os.environ["AWS_REGION"]

    logger.info("Starting ingestion worker")
    logger.info("Provider: %s", provider)
    logger.info("Queue: %s", queue_url)
    logger.info("AWS region: %s", aws_region)

    redis_client = Redis.from_url(
        redis_url,
        decode_responses=False,
    )

    aws_session = aioboto3.Session()

    until = datetime.now(timezone.utc)
    since = until - timedelta(days=14)

    logger.info(
        "Ingestion window: %s -> %s",
        since.isoformat(),
        until.isoformat(),
    )

    async with (
        aws_session.client(
            "sqs",
            region_name=aws_region,
        ) as sqs_client,
        aws_session.client(
            "kms",
            region_name=aws_region,
        ) as kms_client,
    ):
        logger.info("AWS clients initialized")
        logger.info("Starting SQS consumer")

        await consume(
            provider_name=provider,
            sqs_client=sqs_client,
            queue_url=queue_url,
            db_connector=db_connector,
            kms_client=kms_client,
            redis_client=redis_client,
            since=since,
            until=until,
        )

    await redis_client.aclose()

    logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())