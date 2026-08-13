from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.workout import Exercise
from src.models.body import MeasureType, MeasureCategory


def get_or_create_exercise(db: Session, name: str) -> Exercise:
    """
    Résout un nom d'exercice (venant d'un connector) vers l'Exercise existant,
    ou en crée un nouveau si jamais vu. Utilise SQLAlchemy Core (select()) plutôt
    que l'ancien style session.query(), cohérent avec l'API 2.0.
    """
    stmt = select(Exercise).where(Exercise.name == name)
    exercise = db.execute(stmt).scalar_one_or_none()

    if exercise is None:
        exercise = Exercise(name=name)
        db.add(exercise)
        db.flush()  # attribue l'id sans attendre le commit final, pour pouvoir l'utiliser tout de suite

    return exercise


def get_or_create_measure_type(db: Session, name: str, category: MeasureCategory) -> MeasureType:
    stmt = select(MeasureType).where(MeasureType.name == name)
    measure_type = db.execute(stmt).scalar_one_or_none()

    if measure_type is None:
        measure_type = MeasureType(name=name, category=category)
        db.add(measure_type)
        db.flush()

    return measure_type