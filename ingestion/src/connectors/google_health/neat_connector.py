from collections import defaultdict
from datetime import datetime, date as date_
from decimal import Decimal
from typing import Optional
import requests

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.neat_record import NeatRecord

API_BASE = "https://health.googleapis.com/v4/users/me/dataTypes"


def _format_steps(body: dict) -> Optional[Decimal]:
    count = body.get("count")
    if count is None:
        return None
    return Decimal(count)


# Mapping dataType Google Health (kebab-case, tel qu'utilisé dans l'URL)
# -> configuration nécessaire pour fetch/transform.
#   json_key   : clé du champ dans la réponse JSON (casse propre à chaque type,
#                à vérifier au cas par cas — ne pas supposer une transformation
#                automatique de casse, cf. body-fat -> bodyFat).
#   is_interval: True si le type utilise interval.civil_start_time (comme steps,
#                confirmé), False si type "sample" avec sample_time.physical_time
#                (comme weight/body-fat/height en body_measurement).
#   format_fn  : extrait la valeur numérique brute depuis le corps du point.
#   neat_field : nom du champ correspondant sur NeatRecord.
# Seul "steps" a été vérifié manuellement sur une vraie réponse à ce stade.
DATA_TYPE_CONFIG = {
    "steps": {
        "json_key": "steps",
        "is_interval": True,
        "format_fn": _format_steps,
        "neat_field": "steps",
    },
}


class GoogleHealthNeatConnector(BaseConnector[NeatRecord]):
    """
    Connector NEAT s'appuyant sur la Google Health API.
    Agrège les micro-datapoints (ex: steps par tranche de 10-60s) en un total journalier.
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

        config = DATA_TYPE_CONFIG[data_type]
        filter_field = data_type.replace("-", "_")
        time_path = "interval.start_time" if config["is_interval"] else "sample_time.physical_time"
        filter_expr = (
            f'{filter_field}.{time_path} >= "{since.strftime("%Y-%m-%dT%H:%M:%SZ")}" AND '
            f'{filter_field}.{time_path} < "{until.strftime("%Y-%m-%dT%H:%M:%SZ")}"'
        )
        params = {"filter": filter_expr}

        while True:
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(
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

    def transform(self, raw_data: list[dict]) -> list[NeatRecord]:
        # Agrégation par jour civil, tous data types confondus dans un même dict.
        daily: dict[date_, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))

        for point in raw_data:
            data_type = point["_data_type"]
            config = DATA_TYPE_CONFIG[data_type]
            body = point[config["json_key"]]

            value = config["format_fn"](body)
            if value is None:
                continue

            civil = self._extract_civil_date(body, config["is_interval"])
            if civil is None:
                continue

            daily[civil][config["neat_field"]] += value

        records = []
        for day, metrics in daily.items():
            records.append(
                NeatRecord(
                    date=day,
                    steps=int(metrics["steps"]) if "steps" in metrics else None,
                    active_minutes=int(metrics["active_minutes"]) if "active_minutes" in metrics else None,
                    calories_burned=metrics.get("calories_burned"),
                    sleep_minutes=int(metrics["sleep_minutes"]) if "sleep_minutes" in metrics else None,
                    resting_hr=int(metrics["resting_hr"]) if "resting_hr" in metrics else None,
                    source="google_health",
                )
            )
        return records

    @staticmethod
    def _extract_civil_date(body: dict, is_interval: bool) -> Optional[date_]:
        if is_interval:
            civil = body.get("interval", {}).get("civilStartTime", {}).get("date")
        else:
            civil = body.get("sampleTime", {}).get("civilTime", {}).get("date")
        if civil is None:
            return None
        return date_(civil["year"], civil["month"], civil["day"])