import asyncio
from collections import defaultdict
from datetime import date, datetime , timedelta
from decimal import Decimal

from src.connectors.base_connector import BaseConnector
from src.connectors.models.nutrition_record import NutritionRecord
from src.connectors.fatsecret.auth import FatSecretAuthConnector
from src.rate_limiter.redis_admission import RedisAdmissionController



class FatSecretNutritionConnector(BaseConnector[NutritionRecord]):
    """
    Version async — la lib `fatsecret` (client OAuth1) est sync-only, sans
    variante async connue. Plutôt que de réécrire tout le client HTTP à la
    main pour ce seul connector, on délègue l'appel bloquant à un thread via
    asyncio.to_thread — ça libère bien la boucle d'événements pendant l'appel
    réseau, même si ce n'est pas de la "vraie" I/O async comme httpx.
    """

    connector_name = "fatsecret"

    def __init__(self, auth: FatSecretAuthConnector, admission_controller: RedisAdmissionController):
        self._auth = auth
        self._admission = admission_controller

    async def fetch(
        self,
        since: datetime,
        until: datetime,
    ) -> list[dict]:

        current_date = since.date()
        end_date = until.date()

        dates = []

        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        raw_entries: list[dict] = []

        for day in dates:
            entries = await self._fetch_day(day)

            for entry in entries:
                raw_entries.append({
                    "date": day,
                    "entry": entry,
                })

        return raw_entries

    async def _fetch_day(self, day: date):
        async with self._admission.acquire() :
            return await asyncio.to_thread(
                self._auth.client.diary.entries_get_v2,
                date=day,
            )

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

            daily[day]["calories"] += entry.calories if entry.calories is not None else Decimal("0")
            daily[day]["protein"] += entry.protein if entry.protein is not None else Decimal("0")
            daily[day]["fat"] += entry.fat if entry.fat is not None else Decimal("0")
            daily[day]["carbs"] += entry.carbohydrate if entry.carbohydrate is not None else Decimal("0")
            daily[day]["fiber"] += entry.fiber if entry.fiber is not None else Decimal("0")

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