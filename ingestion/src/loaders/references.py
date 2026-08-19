from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.workout import Exercise
from src.models.body import MeasureType, MeasureCategory


async def get_or_create_exercise(db: AsyncSession, name: str) -> Exercise:
    stmt = select(Exercise).where(Exercise.name == name)
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()

    if exercise is None:
        exercise = Exercise(name=name)
        db.add(exercise)
        await db.flush()

    return exercise


async def get_or_create_measure_type(db: AsyncSession, name: str, category: MeasureCategory) -> MeasureType:
    stmt = select(MeasureType).where(MeasureType.name == name)
    result = await db.execute(stmt)
    measure_type = result.scalar_one_or_none()

    if measure_type is None:
        measure_type = MeasureType(name=name, category=category)
        db.add(measure_type)
        await db.flush()

    return measure_type