import asyncio
import os
from datetime import datetime, timedelta

from src.config import Config
from src.database import RDSConnector

from src.connectors.lyfta.auth import LyftaAuthConnector
from src.connectors.lyfta.workout_connector import LyftaWorkoutConnector
from src.loaders.workout import load_workout_sessions

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.google_health.neat_connector import GoogleHealthNeatConnector
from src.connectors.google_health.body_measurement_connector import (
    GoogleHealthBodyMeasurementConnector,
)
from src.loaders.neat import load_neat
from src.loaders.body_measurement import load_body_measurements

from src.connectors.fatsecret.auth import FatSecretAuthConnector
from src.connectors.fatsecret.nutrition_connector import FatSecretNutritionConnector
from src.loaders.nutrition import load_nutrition


db_connector = RDSConnector(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args=Config.get_ssl_connect_args(),
)


async def run_workout(
    since: datetime,
    until: datetime,
):
    auth = LyftaAuthConnector(
        api_key=os.environ["LYFTA_API_KEY"],
    )

    connector = LyftaWorkoutConnector(auth=auth)

    records = await connector.run(since, until)

    print(f"\n[workout] records transformed: {len(records)}")

    async with db_connector.session() as db:
        written = await load_workout_sessions(db, records)

    print(f"[workout] sessions written: {written}")

    return written


async def run_body_measurement(
    since: datetime,
    until: datetime,
    auth: GoogleAuthConnector,
):
    connector = GoogleHealthBodyMeasurementConnector(auth=auth)

    records = await connector.run(since, until)

    print(
        f"\n[body_measurement] "
        f"records transformed: {len(records)}"
    )

    async with db_connector.session() as db:
        written = await load_body_measurements(db, records)

    print(f"[body_measurement] rows written: {written}")

    return written


async def run_neat(
    since: datetime,
    until: datetime,
    auth: GoogleAuthConnector,
):
    connector = GoogleHealthNeatConnector(auth=auth)

    records = await connector.run(since, until)

    print(f"\n[neat] records transformed: {len(records)}")

    async with db_connector.session() as db:
        written = await load_neat(db, records)

    print(f"[neat] rows written: {written}")

    return written


async def run_nutrition(
    since: datetime,
    until: datetime,
):
    auth = FatSecretAuthConnector(
        consumer_key=os.environ["FATSECRET_CONSUMER_KEY"],
        consumer_secret=os.environ["FATSECRET_CONSUMER_SECRET"],
        access_token=os.environ["FATSECRET_ACCESS_TOKEN"],
        access_token_secret=os.environ["FATSECRET_ACCESS_TOKEN_SECRET"],
    )

    connector = FatSecretNutritionConnector(auth=auth)

    records = await connector.run(since, until)

    print(f"\n[nutrition] records transformed: {len(records)}")

    async with db_connector.session() as db:
        written = await load_nutrition(db, records)

    print(f"[nutrition] rows written: {written}")

    return written


async def main():
    until = datetime.utcnow()
    since = until - timedelta(days=14)

    print(
        f"Fenêtre : "
        f"{since.isoformat()} -> {until.isoformat()}"
    )

    google_auth = GoogleAuthConnector(
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
    )

    results = await asyncio.gather(
        run_workout(since, until),
        run_body_measurement(since, until, google_auth),
        run_neat(since, until, google_auth),
        run_nutrition(since, until)
        
    )

    print("\nResults:")
    print(f"[workout]          {results[0]}")
    print(f"[body_measurement] {results[1]}")
    print(f"[neat]              {results[2]}")
    print(f"[nutrition]         {results[3]}")

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())