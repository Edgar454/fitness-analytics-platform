from .base import FitnessBase
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey , DateTime
from sqlalchemy.orm import mapped_column, relationship, Mapped


class Habit(FitnessBase):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category: Mapped[Optional[str]]
    goal_type: Mapped[Optional[str]]

    logs: Mapped[List["HabitLog"]] = relationship(back_populates="habit", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Habit<id={self.id!r}, name={self.name!r}>"


class HabitLog(FitnessBase):
    __tablename__ = "habit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    value: Mapped[Optional[Decimal]]
    completed: Mapped[Optional[bool]]

    habit: Mapped["Habit"] = relationship(back_populates="logs")

    def __repr__(self) -> str:
        return f"HabitLog<id={self.id!r}, habit_id={self.habit_id!r}, completed={self.completed!r}>"