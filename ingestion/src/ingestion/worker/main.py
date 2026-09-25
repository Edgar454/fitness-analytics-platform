import asyncio
import os
from datetime import datetime, timedelta, timezone

import aioboto3
from redis.asyncio import Redis

from ingestion.src.database import db_connector
from ingestion.src.ingestion.worker.consumer import consume


async def main() -> None:
    provider = os.environ["WORKER_PROVIDER"]
    queue_url = os.environ["QUEUE_URL"]

    redis_url = os.environ["REDIS_URL"]
    aws_region = os.environ["AWS_REGION"]

    redis_client = Redis.from_url(
        redis_url,
        decode_responses=False,
    )

    aws_session = aioboto3.Session()

    until = datetime.now(timezone.utc)
    since = until - timedelta(days=14)

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
        await consume(
            provider_name=provider,
            sqs_client=sqs_client,
            queue_url=queue_url,
            session_factory=db_connector,
            kms_client=kms_client,
            redis_client=redis_client,
            since=since,
            until=until,
        )

    await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())