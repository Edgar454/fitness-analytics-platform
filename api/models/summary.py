# schemas/summaries.py

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel
from .common import ListResponse
from ingestion.src.models.fitness.summary import SummaryStatus

class DailySummaryQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class DailySummaryResponse(BaseModel):
    date: date
    health_score: Decimal | None = None
    training_load: Decimal | None = None
    calorie_balance: Decimal | None = None
    weekly_volume: Decimal | None = None

class WeeklySummaryQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    status: SummaryStatus | None = None


class WeeklySummaryResponse(BaseModel):
    week_start: date
    week_end: date
    content: str | None = None
    model_used: str | None = None
    generated_at: datetime
    status: SummaryStatus

class DailySummaryListResponse(
    ListResponse[DailySummaryResponse]
):
    pass


class WeeklySummaryListResponse(
    ListResponse[WeeklySummaryResponse]
):
    pass