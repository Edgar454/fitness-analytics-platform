from datetime import datetime
from decimal import Decimal
from typing import Optional
import requests

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.base_connector import BaseConnector
from src.connectors.models.body_measurement_record import BodyMeasurementRecord

API_BASE = "https://health.googleapis.com/v4/users/me/dataTypes"


def _format_weight(body: dict) -> Optional[tuple[Decimal, str]]:
    weight_grams = body.get("weightGrams")
    if weight_grams is None:
        return None
    return Decimal(weight_grams) / Decimal(1000), "kg"  # grammes -> kg


def _format_body_fat(body: dict) -> Optional[tuple[Decimal, str]]:
    percentage = body.get("percentage")
    if percentage is None:
        return None
    return Decimal(str(percentage)), "%"


def _format_height(body: dict) -> Optional[tuple[Decimal, str]]:
    height_mm = body.get("heightMillimeters")  # renvoyé en string par l'API
    if height_mm is None:
        return None
    return Decimal(height_mm) / Decimal(1000), "m"  # millimètres -> mètres


# Mapping dataType Google Health (kebab-case, tel qu'utilisé dans l'URL)
# -> measure_type_name interne + clé du champ JSON dans la réponse (camelCase,
# distincte de l'URL/kebab-case et du filtre/snake_case) + fonction qui sait
# extraire (value, unit) depuis le corps spécifique à ce type.
# weight, body-fat et height ont tous les trois été vérifiés manuellement.
DATA_TYPE_CONFIG = {
    "weight": {"measure_name": "weight", "json_key": "weight", "format_fn": _format_weight},
    "body-fat": {"measure_name": "bodyfat", "json_key": "bodyFat", "format_fn": _format_body_fat},
    "height": {"measure_name": "height", "json_key": "height", "format_fn": _format_height},
}


class GoogleHealthBodyMeasurementConnector(BaseConnector[BodyMeasurementRecord]):
    """
    Connector body_measurement s'appuyant sur la Google Health API.
    Une mesure ponctuelle (weight, bodyFat, etc.) = un BodyMeasurementRecord,
    pas d'agrégation journalière ici (contrairement à NEAT) puisqu'une pesée
    est déjà un événement discret, pas un flux de micro-datapoints.
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

        # snake_case dans le filtre, même si data_type est kebab-case dans l'URL.
        # weight/body-fat/height sont des types "sample" (sampleTime.physicalTime),
        # pas des types "interval" comme steps -> filtre sur sample_time.physical_time.
        filter_field = data_type.replace("-", "_")
        filter_expr = (
            f'{filter_field}.sample_time.physical_time >= "{since.strftime("%Y-%m-%dT%H:%M:%SZ")}" AND '
            f'{filter_field}.sample_time.physical_time < "{until.strftime("%Y-%m-%dT%H:%M:%SZ")}"'
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

    def transform(self, raw_data: list[dict]) -> list[BodyMeasurementRecord]:
        # Une même mesure peut être remontée par plusieurs sources en parallèle
        # (HEALTH_CONNECT, FITBIT_WEB_API, FITBIT manuel...) avec le même instant
        # et la même valeur. On déduplique sur (measure_name, measured_at, value).
        seen: set[tuple[str, str, str]] = set()
        records: list[BodyMeasurementRecord] = []

        for point in raw_data:
            data_type = point["_data_type"]
            config = DATA_TYPE_CONFIG[data_type]
            body = point[config["json_key"]]

            timestamp_str = body.get("sampleTime", {}).get("physicalTime")
            if timestamp_str is None:
                continue  # point mal formé, on l'ignore plutôt que de planter

            try:
                formatted = config["format_fn"](body)
            except NotImplementedError:
                continue  # type pas encore supporté, on l'ignore silencieusement
            if formatted is None:
                continue  # champ de valeur absent sur ce point précis

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