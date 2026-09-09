# src/database/models/ingestion_job.py

import enum

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ingestion.src.models.base import Base


class JobStatus(enum.Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobEventType(enum.Enum):
    CREATED = "CREATED"
    PROCESSING_STARTED = "PROCESSING_STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRY = "RETRY"


class IngestionJob(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "ingestion"}

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("fitness.users.id"),
        nullable=False,
    )

    connector: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        nullable=False,
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    records_processed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    events: Mapped[list["IngestionJobEvent"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class IngestionJobEvent(Base):
    __tablename__ = "job_events"
    __table_args__ = {"schema": "ingestion"}

    id: Mapped[int] = mapped_column(primary_key=True)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("ingestion.jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    event_type: Mapped[JobEventType] = mapped_column(
        Enum(JobEventType),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    job: Mapped["IngestionJob"] = relationship(
        back_populates="events",
    )