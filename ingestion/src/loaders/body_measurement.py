from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.connectors.models.body_measurement_record import BodyMeasurementRecord
from ingestion.src.models.fitness.body import BodyMeasurement, MeasureCategory
from src.loaders.references import get_or_create_measure_type


async def load_body_measurements(db: AsyncSession, records: list[BodyMeasurementRecord]) -> int:
    count = 0

    for record in records:
        measure_type = await get_or_create_measure_type(
            db,
            name=record.measure_type_name,
            category=MeasureCategory.COMPOSITION,
        )

        stmt = pg_insert(BodyMeasurement).values(
            measured_at=record.measured_at,
            measure_type_id=measure_type.id,
            value=record.value,
            unit=record.unit,
            source=record.source,
        ).on_conflict_do_nothing(index_elements=["measured_at", "measure_type_id"])

        result = await db.execute(stmt)
        if result.rowcount > 0:
            count += 1

    return count