# schemas/health.py

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from .common import ListResponse


class HealthQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    source: str | None = None


class HealthResponse(BaseModel):
    date: date
    steps: int | None = None
    active_minutes: int | None = None
    distance: Decimal | None = None
    calories_burned: Decimal | None = None
    sleep_minutes: int | None = None
    resting_hr: int | None = None
    source: str | None = None


class HealthListResponse(ListResponse[HealthResponse]):
    pass