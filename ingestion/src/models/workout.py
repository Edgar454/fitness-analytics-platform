from .base import FitnessBase
from typing import Optional , List
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey,String
from sqlalchemy.orm import mapped_column,relationship,Mapped


class Exercise(FitnessBase):
    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category: Mapped[Optional[str]]
    muscle_group: Mapped[Optional[str]]
    equipment: Mapped[Optional[str]]
    is_compound: Mapped[Optional[bool]]

    sets: Mapped[List["WorkoutSet"]] = relationship(back_populates="exercise")

    def __repr__(self) -> str:
        return f"Exercise<id={self.id!r} , name={self.name!r},muscle_group={self.muscle_group!r}>"


class WorkoutSession(FitnessBase):
    __tablename__ = "workout_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    started_at: Mapped[datetime]
    ended_at: Mapped[Optional[datetime]]
    duration: Mapped[Optional[int]]
    sources: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]

    sets: Mapped[List["WorkoutSet"]] = relationship(back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Session<id={self.id !r} , date={self.date !r}, duration={self.duration !r}>"

class WorkoutSet(FitnessBase):
    __tablename__ = "workout_set"

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

    id: Mapped[int] = mapped_column(primary_key= True)
    session_id: Mapped[int] = mapped_column(ForeignKey("workout_session.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"))
    metric: Mapped[str]
    value: Mapped[Decimal]
    achieved_at: Mapped[datetime]

    def __repr__(self):
        return f"WorkoutPr<session_id={self.session_id!r}, id={self.id!r}, exercise_id={self.exercise_id!r},value={self.value!r}>"


