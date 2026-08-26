import asyncio
from datetime import datetime, date as date_
from decimal import Decimal
from typing import Optional
import httpx

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.neat_record import NeatRecord
from src.rate_limiter.redis_admission import RedisAdmissionController

API_BASE = "https://health.googleapis.com/v4/users/me/dataTypes"
DATA_SOURCE_FAMILY = "google-sources"


def _format_steps(rollup_value: dict) -> Optional[tuple[Decimal, str]]:
    count_sum = rollup_value.get("countSum")
    if count_sum is None:
        return None
    return Decimal(count_sum), "steps"


def _format_total_calories(rollup_value: dict) -> Optional[tuple[Decimal, str]]:
    kcal_sum = rollup_value.get("kcalSum")
    if kcal_sum is None:
        return None
    return Decimal(str(kcal_sum)), "kcal"


def _format_active_minutes(rollup_value: dict) -> Optional[tuple[Decimal, str]]:
    by_level = rollup_value.get("activeMinutesRollupByActivityLevel", [])
    if not by_level:
        return None
    total = sum(
        (Decimal(entry["activeMinutesSum"]) for entry in by_level if "activeMinutesSum" in entry),
        start=Decimal(0),
    )
    return total, "minutes"


DATA_TYPE_CONFIG = {
    "steps": {"json_key": "steps", "neat_field": "steps", "format_fn": _format_steps},
    "total-calories": {"json_key": "totalCalories", "neat_field": "calories_burned", "format_fn": _format_total_calories},
    "active-minutes": {"json_key": "activeMinutes", "neat_field": "active_minutes", "format_fn": _format_active_minutes},
}


class GoogleHealthNeatConnector(BaseConnector[NeatRecord]):
    """
    Version async. Les 3 dataTypes sont indépendants -> fetch en parallèle
    via asyncio.gather plutôt qu'en séquence, gain réel car purement I/O-bound.
    """

    connector_name = "google_health"

    def __init__(self, auth: GoogleAuthConnector, admission: RedisAdmissionController):
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

        body = {
            "range": {
                "start": {"date": {"year": since.year, "month": since.month, "day": since.day}},
                "end": {"date": {"year": until.year, "month": until.month, "day": until.day}},
            },
            "windowSizeDays": 1,
            "dataSourceFamily": f"users/me/dataSourceFamilies/{DATA_SOURCE_FAMILY}",
        }

        while True:
            if page_token:
                body["pageToken"] = page_token
                
            async with self._admission.acquire() :
                    response = await client.post(
                        f"{API_BASE}/{data_type}/dataPoints:dailyRollUp",
                        headers=headers,
                        json=body,
                        timeout=15,
                    )
                    response.raise_for_status()
                    payload = response.json()

            for point in payload.get("rollupDataPoints", []):
                point["_data_type"] = data_type
                points.append(point)

            page_token = payload.get("nextPageToken")
            if not page_token:
                break

        return points

    def transform(self, raw_data: list[dict]) -> list[NeatRecord]:
        pivoted = self._pivot(raw_data)
        return [NeatRecord(date=day, source="google_health", **fields) for day, fields in pivoted.items()]

    def _pivot(self, raw_data: list[dict]) -> dict[date_, dict]:
        pivoted: dict[date_, dict] = {}

        for point in raw_data:
            data_type = point["_data_type"]
            config = DATA_TYPE_CONFIG[data_type]
            rollup_value = point.get(config["json_key"])
            if rollup_value is None:
                continue

            formatted = config["format_fn"](rollup_value)
            if formatted is None:
                continue
            value, _unit = formatted

            civil = point.get("civilStartTime", {}).get("date")
            if civil is None:
                continue
            day = date_(civil["year"], civil["month"], civil["day"])

            field_name = config["neat_field"]
            if field_name in ("steps", "active_minutes", "sleep_minutes", "resting_hr"):
                value = int(value)

            pivoted.setdefault(day, {})[field_name] = value

        return pivoted