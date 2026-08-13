from sqlalchemy.orm import Session

from src.connectors.models.workout_records import WorkoutSessionRecord
from src.models.workout import WorkoutSession, WorkoutSet, WorkoutPr
from src.loaders.references import get_or_create_exercise


def load_workout_sessions(db: Session, records: list[WorkoutSessionRecord]) -> int:
    """
    Persiste une liste de WorkoutSessionRecord (avec leurs sets/prs imbriqués)
    en base. Résout exercise_name -> Exercise via get_or_create.
    Retourne le nombre de sessions écrites.
    """
    count = 0

    for record in records:
        session = WorkoutSession(
            date=record.date,
            started_at=record.started_at,
            ended_at=record.ended_at,
            duration=record.duration,
            sources=record.sources,
            notes=record.notes,
        )
        db.add(session)
        db.flush()  # pour obtenir session.id avant d'ajouter les sets

        for set_record in record.sets:
            exercise = get_or_create_exercise(db, set_record.exercise_name)
            db.add(
                WorkoutSet(
                    session_id=session.id,
                    exercise_id=exercise.id,
                    set_number=set_record.set_number,
                    is_warmup=set_record.is_warmup,
                    weight= set_record.weight or 0,
                    reps=set_record.reps,
                    rpe=set_record.rpe,
                    rir=set_record.rir,
                    performed_at=set_record.performed_at,
                )
            )

        for pr_record in record.prs:
            exercise = get_or_create_exercise(db, pr_record.exercise_name)
            db.add(
                WorkoutPr(
                    session_id=session.id,
                    exercise_id=exercise.id,
                    metric=pr_record.metric,
                    value=pr_record.value,
                    achieved_at=pr_record.achieved_at,
                )
            )

        count += 1

    return count