import json
from datetime import datetime
from typing import Optional
import httpx

from src.connectors.lyfta.auth import LyftaAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.workout_records import ExerciseMetadataRecord


BASE_URL = "https://my.lyfta.app"


def _parse_id_list(raw: Optional[str]) -> list[int]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        return [int(x) for x in parsed]
    except (json.JSONDecodeError, ValueError, TypeError):
        return []


class LyftaExerciseMetadataConnector(BaseConnector[ExerciseMetadataRecord]):
    connector_name = "lyfta"

    def __init__(self, auth: LyftaAuthConnector):
        self._auth = auth

    async def fetch(self, since: datetime, until: datetime) -> list[dict]:
        exercises: list[dict] = []
        page = 1

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    f"{BASE_URL}/api/v1/exercises",
                    headers=self._auth.headers,
                    params={"limit": 100, "page": page},
                    timeout=15,
                )
                response.raise_for_status()
                payload = response.json()

                page_exercises = payload.get("exercises", [])
                if not page_exercises:
                    break
                exercises.extend(page_exercises)

                total_pages = payload.get("total_pages", 1)
                if page >= total_pages:
                    break
                page += 1

        return exercises

    def transform(self, raw_data: list[dict]) -> list[ExerciseMetadataRecord]:
        records = []

        for item in raw_data:
            name = item.get("name")
            if name is None:
                continue

            records.append(
                ExerciseMetadataRecord(
                    name=name.strip(),
                    image_url=item.get("image_name"),
                    equipment_ids=_parse_id_list(item.get("equipment_id")),
                    body_part_ids=_parse_id_list(item.get("body_part_id")),
                    target_muscle_ids=_parse_id_list(item.get("Target_muscles_id")),
                    synergist_muscle_ids=_parse_id_list(item.get("Synergist_muscles_id")),
                )
            )

        return records