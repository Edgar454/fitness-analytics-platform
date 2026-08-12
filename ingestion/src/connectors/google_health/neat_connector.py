from datetime import datetime, date as date_
from decimal import Decimal
from typing import Optional
import requests

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.neat_record import NeatRecord

API_BASE = "https://health.googleapis.com/v4/users/me/dataTypes"

# Source unique forcée pour éviter le double comptage entre plateformes
# (on a observé FITBIT + deux applications HEALTH_CONNECT rapporter des
# événements qui se chevauchent pour le même intervalle). Valeurs supportées
# selon la doc REST : "all-sources" (défaut), "google-wearables", "google-sources".
# À vérifier laquelle correspond réellement à Health Connect côté téléphone —
# aucune des trois n'a l'air de matcher "HEALTH_CONNECT" littéralement.
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
    # Somme des trois niveaux d'intensité (LIGHT/MODERATE/VIGOROUS) en une
    # seule métrique, cohérent avec le champ unique active_minutes attendu
    # côté daily_health. Si on veut la granularité par intensité plus tard,
    # il faudra trois metric_name séparés plutôt qu'une somme ici.
    by_level = rollup_value.get("activeMinutesRollupByActivityLevel", [])
    total = sum(Decimal(entry["activeMinutesSum"]) for entry in by_level if "activeMinutesSum" in entry)
    if not by_level:
        return None
    return total, "minutes"


# Mapping dataType Google Health (kebab-case dans l'URL) -> config.
#   json_key    : clé du champ "union" dans la réponse rollup.
#   metric_name : nom de métrique utilisé dans NeatRecord.metric_name.
#   format_fn   : extrait (value, unit) depuis le rollup_value du type.
# steps, total-calories et active-minutes vérifiés manuellement sur une vraie
# réponse dailyRollUp. sleep et resting_hr restent à investiguer.
DATA_TYPE_CONFIG = {
    "steps": {
        "json_key": "steps",
        "metric_name": "steps",
        "format_fn": _format_steps,
    },
    "total-calories": {
        "json_key": "totalCalories",
        "metric_name": "calories_burned",
        "format_fn": _format_total_calories,
    },
    "active-minutes": {
        "json_key": "activeMinutes",
        "metric_name": "active_minutes",
        "format_fn": _format_active_minutes,
    },
}


class GoogleHealthNeatConnector(BaseConnector[NeatRecord]):
    """
    Connector NEAT s'appuyant sur la Google Health API, via l'action dailyRollUp
    (steps/active-minutes/total-calories/etc. ne supportent pas `list`, seulement
    rollup/dailyRollUp). Une source unique (DATA_SOURCE_FAMILY) est forcée pour
    éviter le double comptage entre plateformes concurrentes (Fitbit, Health Connect).
    """

    connector_name = "google_health"

    def __init__(self, auth: GoogleAuthConnector):
        self._auth = auth

    def fetch(self, since: datetime, until: datetime) -> list[dict]:
        raw_points: list[dict] = []
        for data_type in DATA_TYPE_CONFIG:
            raw_points.extend(self._fetch_data_type(data_type, since, until))
        return raw_points

    def _fetch_data_type(self, data_type: str, since: datetime, until: datetime) -> list[dict]:
        points: list[dict] = []
        page_token: str | None = None
        headers = {"Authorization": f"Bearer {self._auth.get_access_token()}"}

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

            response = requests.post(
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
        records: list[NeatRecord] = []

        for point in raw_data:
            data_type = point["_data_type"]
            config = DATA_TYPE_CONFIG[data_type]
            rollup_value = point.get(config["json_key"])
            if rollup_value is None:
                continue

            formatted = config["format_fn"](rollup_value)
            if formatted is None:
                continue
            value, unit = formatted

            civil = point.get("civilStartTime", {}).get("date")
            if civil is None:
                continue
            day = date_(civil["year"], civil["month"], civil["day"])

            records.append(
                NeatRecord(
                    date=day,
                    metric_name=config["metric_name"],
                    value=value,
                    unit=unit,
                    source="google_health",
                )
            )

        return records