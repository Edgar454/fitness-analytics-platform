# schemas/measurements.py
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel
from .common import ListResponse
from ingestion.src.models.body import MeasureCategory

class MeasurementQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    measure_type: str | None = None
    category: MeasureCategory | None = None
    source: str | None = None

class MeasureTypeResponse(BaseModel):
    id: int
    name: str
    category: MeasureCategory
    unit_default: str | None = None

class BodyMeasurementResponse(BaseModel):
    measured_at: datetime
    measure_type: MeasureTypeResponse
    value: Decimal
    unit: str | None = None
    source: str | None = None

class BodyMeasurementListResponse(
    ListResponse[BodyMeasurementResponse]
):
    pass


class MeasureTypeListResponse(
    ListResponse[MeasureTypeResponse]
):
    pass