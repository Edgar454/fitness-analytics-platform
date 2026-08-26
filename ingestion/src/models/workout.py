from .base import FitnessBase
from typing import Optional , List
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey,String, UniqueConstraint , ARRAY, Integer , DateTime
from sqlalchemy.orm import mapped_column,relationship,Mapped 




class Exercise(FitnessBase):
    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category: Mapped[Optional[str]]
    image_url: Mapped[Optional[str]]

    # Arrays plutôt que many-to-many complet : un exercice composé (compound)
    # peut légitimement toucher plusieurs body parts/muscles à la fois — ce
    # n'est pas une anomalie de données Lyfta. Pas de vraie contrainte FK
    # possible élément par élément sur un array Postgres ; l'intégrité
    # référentielle vers equipment/body_part/muscle est assumée applicative,
    # pas enforced par la DB — compromis accepté pour rester simple.
    equipment_ids: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))
    body_part_ids: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))
    target_muscle_ids: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))
    synergist_muscle_ids: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer ))

    sets: Mapped[List["WorkoutSet"]] = relationship(back_populates="exercise")

    def __repr__(self) -> str:
        return f"Exercise<id={self.id!r}, name={self.name!r}>"


class WorkoutSession(FitnessBase):
    __tablename__ = "workout_session"
    __table_args__ = (UniqueConstraint("user_id", "started_at", name="uq_workout_session_user_started_at"),)


    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime]
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration: Mapped[Optional[int]]
    sources: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]

    sets: Mapped[List["WorkoutSet"]] = relationship(back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Session<id={self.id !r} , date={self.date !r}, duration={self.duration !r}>"

class WorkoutSet(FitnessBase):
    __tablename__ = "workout_set"
    __table_args__ = (
        UniqueConstraint("session_id", "exercise_id", "set_number", name="uq_workout_set_session_exercise_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("workout_session.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"))
    set_number: Mapped[int]
    reps: Mapped[Optional[int]]
    is_warmup: Mapped[Optional[bool]]
    weight: Mapped[Decimal]
    rpe: Mapped[Optional[Decimal]]
    rir: Mapped[Optional[Decimal]]
    performed_at: Mapped[datetime]

    session: Mapped["WorkoutSession"] = relationship(back_populates="sets")
    exercise: Mapped["Exercise"] = relationship(back_populates="sets")

    def __repr__(self):
        return f"WorkoutSet<session_id= {self.session_id!r} ,id={self.id!r}, set_number={self.set_number!r},weight={self.weight!r}>"

class WorkoutPr(FitnessBase):
    __tablename__ = "workout_pr"
    __table_args__ = (
        UniqueConstraint("session_id", "exercise_id", "metric", name="uq_workout_pr_session_exercise_metric"),
    )

    id: Mapped[int] = mapped_column(primary_key= True)
    session_id: Mapped[int] = mapped_column(ForeignKey("workout_session.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"))
    metric: Mapped[str]
    value: Mapped[Decimal]
    achieved_at: Mapped[datetime]

    def __repr__(self):
        return f"WorkoutPr<session_id={self.session_id!r}, id={self.id!r}, exercise_id={self.exercise_id!r},value={self.value!r}>"


