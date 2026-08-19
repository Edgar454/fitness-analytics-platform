from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.connectors.models.neat_record import NeatRecord
from src.models.daily_telemetry import DailyHealth


async def load_neat(db: AsyncSession, records: list[NeatRecord]) -> int:
    count = 0

    for record in records:
        stmt = pg_insert(DailyHealth).values(
            date=record.date,
            steps=record.steps,
            active_minutes=record.active_minutes,
            distance=record.distance,
            calories_burned=record.calories_burned,
            sleep_minutes=record.sleep_minutes,
            resting_hr=record.resting_hr,
            source=record.source,
        ).on_conflict_do_nothing(index_elements=["date"])

        result = await db.execute(stmt)
        if result.rowcount > 0:
            count += 1

    return count