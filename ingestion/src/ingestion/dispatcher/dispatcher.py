# src/dispatcher/dispatcher.py

import asyncio
import os
from datetime import timedelta

from src.database import RDSConnector
from src.config import Config

from src.ingestion.dispatcher.utils import (
    create_job,
    get_active_users,
    get_sqs_client,
)


ACTIVE_USER_WINDOW_DAYS = int(
    os.environ.get("ACTIVE_USER_WINDOW_DAYS", "30")
)


db_connector = RDSConnector(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args=Config.get_ssl_connect_args(),
)


async def dispatch() -> None:
    """
    Find active users and enqueue one ingestion job per
    active credential/provider.
    """

    active_within = timedelta(days=ACTIVE_USER_WINDOW_DAYS)

    sqs_client = get_sqs_client()

    async with db_connector.session() as db:
        users = await get_active_users(
            db=db,
            active_within=active_within,
        )

        print(f"Found {len(users)} active users.")

        jobs_created = 0

        for user in users:
            user_id = user["user_id"]
            providers = user["providers"]

            for provider in providers:
                try:
                    job_id = await create_job(
                        db=db,
                        sqs_client=sqs_client,
                        user_id=user_id,
                        connector=provider,
                    )

                    jobs_created += 1

                    print(
                        f"Created job {job_id} "
                        f"for user={user_id}, "
                        f"connector={provider}"
                    )

                except Exception as exc:
                    print(
                        f"Failed to create job "
                        f"for user={user_id}, "
                        f"connector={provider}: {exc}"
                    )

    print(f"Dispatcher finished. Jobs created: {jobs_created}")


def main() -> None:
    asyncio.run(dispatch())


if __name__ == "__main__":
    main()