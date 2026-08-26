import asyncio
import httpx
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.body_measurement_record import BodyMeasurementRecord
from src.rate_limiter.redis_admission import RedisAdmissionController



API_BASE = "https://health.googleapis.com/v4/users/me/dataTypes"


def _format_weight(body: dict) -> Optional[tuple[Decimal, str]]:
    weight_grams = body.get("weightGrams")
    if weight_grams is None:
        return None
    return Decimal(weight_grams) / Decimal(1000), "kg"


def _format_body_fat(body: dict) -> Optional[tuple[Decimal, str]]:
    percentage = body.get("percentage")
    if percentage is None:
        return None
    return Decimal(str(percentage)), "%"


def _format_height(body: dict) -> Optional[tuple[Decimal, str]]:
    height_mm = body.get("heightMillimeters")
    if height_mm is None:
        return None
    return Decimal(height_mm) / Decimal(1000), "m"


DATA_TYPE_CONFIG = {
    "weight": {"measure_name": "weight", "json_key": "weight", "format_fn": _format_weight},
    "body-fat": {"measure_name": "bodyfat", "json_key": "bodyFat", "format_fn": _format_body_fat},
    "height": {"measure_name": "height", "json_key": "height", "format_fn": _format_height},
}


class GoogleHealthBodyMeasurementConnector(BaseConnector[BodyMeasurementRecord]):
    """Version async — les 3 types sont fetchés en parallèle via asyncio.gather."""

    connector_name = "google_health"

    def __init__(self, auth: GoogleAuthConnector ,admission: RedisAdmissionController):
        self._auth = auth
        self._admission = admission

    async def fetch(self, since: datetime, until: datetime) -> list[dict]:
        async with httpx.AsyncClient() as client:
            results = await asyncio.gather(
                *[self._fetch_data_type(client, data_type, since, until) for data_type in DATA_TYPE_CONFIG]
            )

        raw_points: list[dict] = []
        for points in results:
            raw_points.extend(points)
        return raw_points

    async def _fetch_data_type(
        self, client: httpx.AsyncClient, data_type: str, since: datetime, until: datetime
    ) -> list[dict]:
        points: list[dict] = []
        page_token: str | None = None
        token = await self._auth.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        filter_field = data_type.replace("-", "_")
        filter_expr = (
            f'{filter_field}.sample_time.physical_time >= "{since.strftime("%Y-%m-%dT%H:%M:%SZ")}" AND '
            f'{filter_field}.sample_time.physical_time < "{until.strftime("%Y-%m-%dT%H:%M:%SZ")}"'
        )
        params = {"filter": filter_expr}

        while True:
            if page_token:
                params["pageToken"] = page_token

            async with self._admission.acquire():
                response = await client.get(
                    f"{API_BASE}/{data_type}/dataPoints",
                    headers=headers,
                    params=params,
                    timeout=15,
                )
                response.raise_for_status()
                payload = response.json()

            for point in payload.get("dataPoints", []):
                point["_data_type"] = data_type
                points.append(point)

            page_token = payload.get("nextPageToken")
            if not page_token:
                break

        return points

    def transform(self, raw_data: list[dict]) -> list[BodyMeasurementRecord]:
        seen: set[tuple[str, str, str]] = set()
        records: list[BodyMeasurementRecord] = []

        for point in raw_data:
            data_type = point["_data_type"]
            config = DATA_TYPE_CONFIG[data_type]
            body = point[config["json_key"]]

            timestamp_str = body.get("sampleTime", {}).get("physicalTime")
            if timestamp_str is None:
                continue

            try:
                formatted = config["format_fn"](body)
            except NotImplementedError:
                continue
            if formatted is None:
                continue

            value, unit = formatted
            measured_at = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            dedup_key = (config["measure_name"], timestamp_str, str(value))
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            records.append(
                BodyMeasurementRecord(
                    measured_at=measured_at,
                    measure_type_name=config["measure_name"],
                    value=value,
                    unit=unit,
                    source="google_health",
                )
            )

        return records