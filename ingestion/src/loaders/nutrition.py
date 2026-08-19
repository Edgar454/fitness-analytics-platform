from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.connectors.models.nutrition_record import NutritionRecord
from src.models.daily_telemetry import DailyNutrition


async def load_nutrition(db: AsyncSession, records: list[NutritionRecord]) -> int:
    count = 0

    for record in records:
        stmt = pg_insert(DailyNutrition).values(
            date=record.date,
            calories=record.calories,
            protein=record.protein,
            fat=record.fat,
            carbs=record.carbs,
            fiber=record.fiber,
            water=record.water,
            source=record.source,
        ).on_conflict_do_nothing(index_elements=["date"])

        result = await db.execute(stmt)
        if result.rowcount > 0:
            count += 1

    return count