from sqlalchemy import Enum, ForeignKey, UniqueConstraint , String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.ingestion.jobs import JobEventType, JobStatus


class JobStateTransition(Base):
    __tablename__ = "job_state_transitions"
    __table_args__ = (
        UniqueConstraint(
            "from_state",
            "event_type",
            name="uq_job_state_transition",
        ),
        {"schema": "ingestion"},
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    from_state: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    event_type: Mapped[JobEventType] = mapped_column(
        Enum(JobEventType),
        nullable=False,
    )

    to_state: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        nullable=False,
    )