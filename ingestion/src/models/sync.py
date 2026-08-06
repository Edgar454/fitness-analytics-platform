import enum

from .base import FitnessBase
from typing import Optional
from datetime import datetime

from sqlalchemy import Enum
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

    id: Mapped[int] = mapped_column(primary_key=True)
    connector: Mapped[str]
    started_at: Mapped[datetime]
    ended_at: Mapped[Optional[datetime]]
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus))
    records_processed: Mapped[Optional[int]]
    error: Mapped[Optional[str]]
    trigger_type: Mapped[TriggerType] = mapped_column(Enum(TriggerType))

    def __repr__(self) -> str:
        return f"SyncHistory<id={self.id!r}, connector={self.connector!r}, status={self.status!r}>"