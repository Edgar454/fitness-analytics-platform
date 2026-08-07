from src.connectors.base_connector import BaseConnector

from datetime import datetime
from decimal import Decimal
import requests

from src.connectors.google_health.auth import GoogleAuthConnector
from src.connectors.models.body_measurement_record import BodyMeasurementRecord

API_BASE = "https://health.googleapis.com/v4/users/me/dataTypes"

# Mapping dataType Google Health -> measure_type_name interne à notre schéma.
# ATTENTION : seul "weight" a été vérifié manuellement sur un vrai compte.
# Les autres noms de dataType sont des suppositions à confirmer dans la doc
# officielle (developers.google.com/health/reference) avant de faire confiance
# à ce connector en production.
DATA_TYPE_TO_MEASURE_NAME = {
    "weight": "weight",
    "bodyFat": "bodyfat",
    "bmi": "bmi",
    "muscleMass": "muscle_mass",
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
        for data_type in DATA_TYPE_TO_MEASURE_NAME:
            raw_points.extend(self._fetch_data_type(data_type, since, until))
        return raw_points

    def _fetch_data_type(self, data_type: str, since: datetime, until: datetime) -> list[dict]:
        points: list[dict] = []
        page_token: str | None = None
        headers = {"Authorization": f"Bearer {self._auth.get_access_token()}"}
        params = {
            "startTime": since.isoformat(),
            "endTime": until.isoformat(),
        }

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
        records: list[BodyMeasurementRecord] = []

        for point in raw_data:
            data_type = point["_data_type"]
            measure_name = DATA_TYPE_TO_MEASURE_NAME[data_type]

            # Hypothèse de structure, à confirmer sur une vraie réponse :
            # point[data_type] contient un champ "value" (ou équivalent) et un instant.
            # Pour "weight" (le seul confirmé), on suppose une structure proche de "steps"
            # mais avec un instant unique plutôt qu'un interval (à vérifier).
            body = point[data_type]
            value = body.get("value")
            if value is None:
                continue  # point mal formé ou champ inattendu, on l'ignore plutôt que de planter

            timestamp_str = point.get("instantTime") or body.get("instantTime")
            measured_at = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")) if timestamp_str else None
            if measured_at is None:
                continue

            records.append(
                BodyMeasurementRecord(
                    measured_at=measured_at,
                    measure_type_name=measure_name,
                    value=Decimal(str(value)),
                    source="google_health",
                )
            )

        return records