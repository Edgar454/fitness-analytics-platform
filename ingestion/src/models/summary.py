import enum

from .base import FitnessBase
from typing import Optional
from datetime import date as date_, datetime
from decimal import Decimal

from sqlalchemy import Enum , DateTime , ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped


class SummaryStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class DailySummary(FitnessBase):
    __tablename__ = "daily_summary"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_daily_summary_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date_] = mapped_column(unique=True)
    health_score: Mapped[Optional[Decimal]]
    training_load: Mapped[Optional[Decimal]]
    calorie_balance: Mapped[Optional[Decimal]]
    weekly_volume: Mapped[Optional[Decimal]]

    def __repr__(self) -> str:
        return f"DailySummary<id={self.id!r}, date={self.date!r}, health_score={self.health_score!r}>"


class WeeklySummary(FitnessBase):
    __tablename__ = "weekly_summary"
    __table_args__ = (UniqueConstraint("user_id", "week_start", name="uq_weekly_summary_user_week_start"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    week_start: Mapped[date_] = mapped_column(unique=True)
    week_end: Mapped[date_]
    content: Mapped[Optional[str]]
    model_used: Mapped[Optional[str]]
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[SummaryStatus] = mapped_column(Enum(SummaryStatus))

    def __repr__(self) -> str:
        return f"WeeklySummary<id={self.id!r}, week_start={self.week_start!r}, status={self.status!r}>"