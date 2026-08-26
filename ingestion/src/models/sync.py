import enum

from .base import FitnessBase
from typing import Optional
from datetime import datetime

from sqlalchemy import Enum , DateTime , ForeignKey, UniqueConstraint, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped


class SyncStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"


class TriggerType(enum.Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class SyncHistory(FitnessBase):
    __tablename__ = "sync_history"
    __table_args__ = (UniqueConstraint("user_id", "started_at", name="uq_sync_history_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    connector: Mapped[str]
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus))
    records_processed: Mapped[Optional[int]]
    error: Mapped[Optional[str]]
    trigger_type: Mapped[TriggerType] = mapped_column(Enum(TriggerType))

    def __repr__(self) -> str:
        return f"SyncHistory<id={self.id!r}, connector={self.connector!r}, status={self.status!r}>"