from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.connectors.models.workout_records import WorkoutSessionRecord
from ingestion.src.models.fitness.workout import WorkoutSession, WorkoutSet, WorkoutPr
from src.loaders.references import get_or_create_exercise


async def load_workout_sessions(db: AsyncSession, records: list[WorkoutSessionRecord]) -> int:
    count = 0

    for record in records:
        session_id = await _upsert_session(db, record)
        if session_id is None:
            continue

        for set_record in record.sets:
            exercise = await get_or_create_exercise(db, set_record.exercise_name)
            stmt = pg_insert(WorkoutSet).values(
                session_id=session_id,
                exercise_id=exercise.id,
                set_number=set_record.set_number,
                is_warmup=set_record.is_warmup,
                weight=set_record.weight,
                reps=set_record.reps,
                rpe=set_record.rpe,
                rir=set_record.rir,
                performed_at=set_record.performed_at,
            ).on_conflict_do_nothing(index_elements=["session_id", "exercise_id", "set_number"])
            await db.execute(stmt)

        for pr_record in record.prs:
            exercise = await get_or_create_exercise(db, pr_record.exercise_name)
            stmt = pg_insert(WorkoutPr).values(
                session_id=session_id,
                exercise_id=exercise.id,
                metric=pr_record.metric,
                value=pr_record.value,
                achieved_at=pr_record.achieved_at,
            ).on_conflict_do_nothing(index_elements=["session_id", "exercise_id", "metric"])
            await db.execute(stmt)

        count += 1

    return count


async def _upsert_session(db: AsyncSession, record: WorkoutSessionRecord) -> int | None:
    stmt = pg_insert(WorkoutSession).values(
        date=record.date,
        started_at=record.started_at,
        ended_at=record.ended_at,
        duration=record.duration,
        sources=record.sources,
        notes=record.notes,
    ).on_conflict_do_nothing(index_elements=["started_at"]).returning(WorkoutSession.id)

    result = await db.execute(stmt)
    session_id = result.scalar_one_or_none()

    if session_id is not None:
        return session_id

    existing = await db.execute(
        select(WorkoutSession.id).where(WorkoutSession.started_at == record.started_at)
    )
    return existing.scalar_one_or_none()