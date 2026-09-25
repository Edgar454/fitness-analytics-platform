from redis.asyncio import Redis

from ingestion.src.ingestion.worker.models import IngestionHandler

from ingestion.src.connectors.lyfta.auth import LyftaAuthConnector
from ingestion.src.connectors.lyfta.workout_connector import LyftaWorkoutConnector

from ingestion.src.connectors.fatsecret.auth import FatSecretAuthConnector
from ingestion.src.connectors.fatsecret.nutrition_connector import (
    FatSecretNutritionConnector,
)

from ingestion.src.connectors.google_health.auth import GoogleAuthConnector
from ingestion.src.connectors.google_health.neat_connector import (
    GoogleHealthNeatConnector,
)
from ingestion.src.connectors.google_health.body_measurement_connector import (
    GoogleHealthBodyMeasurementConnector,
)

from ingestion.src.loaders.workout import load_workout_sessions
from ingestion.src.loaders.nutrition import load_nutrition
from ingestion.src.loaders.neat import load_neat
from ingestion.src.loaders.body_measurement import load_body_measurements

from ingestion.src.rate_limiter.redis_admission import RedisAdmissionController
from ingestion.src.ingestion.worker.config import ADMISSION_CONFIGS


def build_ingestion_handlers(
    provider: str,
    connector_config: dict,
    redis_client: Redis,
) -> list[IngestionHandler]:

    if provider not in ADMISSION_CONFIGS:
        raise ValueError(f"Unsupported ingestion provider: {provider}")

    admission = RedisAdmissionController(
        redis=redis_client,
        config=ADMISSION_CONFIGS[provider],
    )

    if provider == "lyfta":
        auth = LyftaAuthConnector(**connector_config)

        connector = LyftaWorkoutConnector(
            auth=auth,
            admission=admission,
        )

        return [
            IngestionHandler(
                connector=connector,
                loader=load_workout_sessions,
            )
        ]

    if provider == "fatsecret":
        auth = FatSecretAuthConnector(**connector_config)

        connector = FatSecretNutritionConnector(
            auth=auth,
            admission=admission,
        )

        return [
            IngestionHandler(
                connector=connector,
                loader=load_nutrition,
            )
        ]

    if provider == "google_health":
        auth = GoogleAuthConnector(**connector_config)

        neat_connector = GoogleHealthNeatConnector(
            auth=auth,
            admission=admission,
        )

        body_measurement_connector = GoogleHealthBodyMeasurementConnector(
            auth=auth,
            admission=admission,
        )

        return [
            IngestionHandler(
                connector=neat_connector,
                loader=load_neat,
            ),
            IngestionHandler(
                connector=body_measurement_connector,
                loader=load_body_measurements,
            ),
        ]

    raise ValueError(f"Unsupported ingestion provider: {provider}")