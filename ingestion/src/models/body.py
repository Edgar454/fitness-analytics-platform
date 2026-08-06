import enum

from .base import FitnessBase
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, UniqueConstraint, Enum
from sqlalchemy.orm import mapped_column, relationship, Mapped


class MeasureCategory(enum.Enum):
    COMPOSITION = "composition"
    TAPE_MEASUREMENT = "tape_measurement"


class PhotoView(enum.Enum):
    FRONT = "front"
    SIDE = "side"
    BACK = "back"


class MeasureType(FitnessBase):
    __tablename__ = "measure_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    category: Mapped[MeasureCategory] = mapped_column(Enum(MeasureCategory))
    unit_default: Mapped[Optional[str]]

    measurements: Mapped[List["BodyMeasurement"]] = relationship(back_populates="measure_type")

    def __repr__(self) -> str:
        return f"MeasureType<id={self.id!r}, name={self.name!r}, category={self.category!r}>"


class BodyMeasurement(FitnessBase):
    __tablename__ = "body_measurement"
    __table_args__ = (
        UniqueConstraint("measured_at", "measure_type_id", name="uq_body_measurement_time_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    measured_at: Mapped[datetime]
    measure_type_id: Mapped[int] = mapped_column(ForeignKey("measure_type.id"))
    value: Mapped[Decimal]
    unit: Mapped[Optional[str]]
    source: Mapped[Optional[str]]

    measure_type: Mapped["MeasureType"] = relationship(back_populates="measurements")

    def __repr__(self) -> str:
        return f"BodyMeasurement<id={self.id!r}, measure_type_id={self.measure_type_id!r}, value={self.value!r}>"


class ProgressPhoto(FitnessBase):
    __tablename__ = "progress_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    view: Mapped[Optional[PhotoView]] = mapped_column(Enum(PhotoView))
    s3_key: Mapped[str]
    mime_type: Mapped[Optional[str]]
    uploaded_at: Mapped[datetime]

    def __repr__(self) -> str:
        return f"ProgressPhoto<id={self.id!r}, view={self.view!r}, s3_key={self.s3_key!r}>"