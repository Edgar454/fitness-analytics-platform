from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
import httpx

from src.connectors.lyfta.auth import LyftaAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.workout_records import WorkoutSessionRecord, WorkoutSetRecord, WorkoutPrRecord
from src.rate_limiter.redis_admission import RedisAdmissionController



BASE_URL = "https://my.lyfta.app"


def _to_decimal(value: Optional[str]) -> Optional[Decimal]:
    if value is None or value == "":
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _to_int(value: Optional[str]) -> Optional[int]:
    dec = _to_decimal(value)
    return int(dec) if dec is not None else None


def _fix_double_escaped_unicode(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        return value.encode("latin-1").decode("unicode_escape")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return value


RECORD_TYPE_METRIC = {
    "1": "estimated_1rm",
    "2": "max_weight",
    "3": "max_volume",
    "4": "max_reps",
}


class LyftaWorkoutConnector(BaseConnector[WorkoutSessionRecord]):
    """
    Version async. Pagination séquentielle conservée (chaque page dépend du
    total_pages retourné par la précédente, pas de parallélisation naturelle
    sans connaître le nombre de pages à l'avance).
    """

    connector_name = "lyfta"

    def __init__(self, auth: LyftaAuthConnector , admission: RedisAdmissionController):
        self._auth = auth
        self._admission = admission

    async def fetch(self, since: datetime, until: datetime) -> list[dict]:
        workouts: list[dict] = []
        page = 1

        async with httpx.AsyncClient() as client:
            while True:
                async with self._admission.acquire():
                    response = await client.get(
                        f"{BASE_URL}/api/v1/workouts",
                        headers=self._auth.headers,
                        params={"limit": 100, "page": page},
                    timeout=15,
                    )
                    response.raise_for_status()
                    payload = response.json()

                page_workouts = payload.get("workouts", [])
                if not page_workouts:
                    break

                stop = False
                for workout in page_workouts:
                    perform_date = datetime.strptime(workout["workout_perform_date"], "%Y-%m-%d %H:%M:%S")
                    if perform_date < since:
                        stop = True
                        continue
                    if perform_date <= until:
                        workouts.append(workout)

                if stop:
                    break

                total_pages = payload.get("total_pages", 1)
                if page >= total_pages:
                    break
                page += 1

        return workouts

    def transform(self, raw_data: list[dict]) -> list[WorkoutSessionRecord]:
        sessions: list[WorkoutSessionRecord] = []

        for workout in raw_data:
            performed_at = datetime.strptime(workout["workout_perform_date"], "%Y-%m-%d %H:%M:%S")

            sets: list[WorkoutSetRecord] = []
            prs: list[WorkoutPrRecord] = []

            for exercise in workout.get("exercises", []):
                exercise_name = exercise.get("excercise_name")
                if exercise_name is None:
                    continue
                exercise_name = _fix_double_escaped_unicode(exercise_name).strip()

                for i, raw_set in enumerate(exercise.get("sets", []), start=1):
                    weight = _to_decimal(raw_set.get("weight"))
                    reps = _to_int(raw_set.get("reps"))
                    rir = _to_decimal(raw_set.get("rir"))

                    sets.append(
                        WorkoutSetRecord(
                            exercise_name=exercise_name,
                            set_number=i,
                            weight=weight or 0,
                            reps=reps,
                            is_warmup=None,
                            rir=rir,
                            performed_at=performed_at,
                        )
                    )

                    if raw_set.get("record_type") is not None:
                        types = str(raw_set["record_type"]).split(",")
                        values = str(raw_set.get("record_value", "")).split(",")

                        for record_type, raw_value in zip(types, values):
                            record_value = _to_decimal(raw_value.strip())
                            if record_value is None:
                                continue
                            metric = RECORD_TYPE_METRIC.get(record_type.strip())
                            if metric is None:
                                continue
                            prs.append(
                                WorkoutPrRecord(
                                    exercise_name=exercise_name,
                                    metric=metric,
                                    value=record_value,
                                    achieved_at=performed_at,
                                )
                            )

            sessions.append(
                WorkoutSessionRecord(
                    date=performed_at,
                    started_at=performed_at,
                    ended_at=None,
                    duration=None,
                    sources="lyfta",
                    notes=_fix_double_escaped_unicode(workout.get("title")),
                    sets=sets,
                    prs=prs,
                )
            )

        return sessions