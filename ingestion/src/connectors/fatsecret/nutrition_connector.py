from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from src.connectors.base_connector import BaseConnector
from src.connectors.models.nutrition_record import NutritionRecord
from src.connectors.fatsecret.auth import FatSecretAuthConnector


class FatSecretNutritionConnector(BaseConnector[NutritionRecord]):
    connector_name = "fatsecret"

    def __init__(self, auth: FatSecretAuthConnector):
        self._auth = auth

    def fetch(self, since: datetime, until: datetime) -> list[dict]:
        raw_entries: list[dict] = []

        current_date = since.date()
        end_date = until.date()

        while current_date <= end_date:
            entries = self._auth.client.diary.entries_get_v2(
                date=current_date
            )

            for entry in entries:
                raw_entries.append({
                    "date": current_date,
                    "entry": entry,
                })

            current_date = current_date.fromordinal(
                current_date.toordinal() + 1
            )

        return raw_entries
    
    def transform(self, raw_data: list[dict]) -> list[NutritionRecord]:
        daily: dict[date, dict[str, Decimal]] = defaultdict(
            lambda: {
                "calories": Decimal("0"),
                "protein": Decimal("0"),
                "fat": Decimal("0"),
                "carbs": Decimal("0"),
                "fiber": Decimal("0"),
            }
        )

        for item in raw_data:
            day = item["date"]
            entry = item["entry"]

            daily[day]["calories"] += (
                entry.calories if entry.calories is not None else Decimal("0")
            )
            daily[day]["protein"] += (
                entry.protein if entry.protein is not None else Decimal("0")
            )
            daily[day]["fat"] += (
                entry.fat if entry.fat is not None else Decimal("0")
            )
            daily[day]["carbs"] += (
                entry.carbohydrate if entry.carbohydrate is not None else Decimal("0")
            )
            daily[day]["fiber"] += (
                entry.fiber if entry.fiber is not None else Decimal("0")
            )

        return [
            NutritionRecord(
                date=day,
                calories=values["calories"],
                protein=values["protein"],
                fat=values["fat"],
                carbs=values["carbs"],
                fiber=values["fiber"],
                water=None,
                source="fatsecret",
            )
            for day, values in sorted(daily.items())
        ]