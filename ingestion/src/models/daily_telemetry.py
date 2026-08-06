from .base import FitnessBase
from typing import Optional
from datetime import date as date_
from decimal import Decimal

from sqlalchemy.orm import mapped_column, Mapped


class DailyHealth(FitnessBase):
    __tablename__ = "daily_health"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_] = mapped_column(unique=True)
    steps: Mapped[Optional[int]]
    active_minutes: Mapped[Optional[int]]
    distance: Mapped[Optional[Decimal]]
    calories_burned: Mapped[Optional[Decimal]]
    sleep_minutes: Mapped[Optional[int]]
    resting_hr: Mapped[Optional[int]]
    source: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"DailyHealth<id={self.id!r}, date={self.date!r}, steps={self.steps!r}>"


class DailyNutrition(FitnessBase):
    __tablename__ = "daily_nutrition"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_] = mapped_column(unique=True)
    calories: Mapped[Optional[Decimal]]
    protein: Mapped[Optional[Decimal]]
    fat: Mapped[Optional[Decimal]]
    carbs: Mapped[Optional[Decimal]]
    fiber: Mapped[Optional[Decimal]]
    water: Mapped[Optional[Decimal]]
    source: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"DailyNutrition<id={self.id!r}, date={self.date!r}, calories={self.calories!r}>"