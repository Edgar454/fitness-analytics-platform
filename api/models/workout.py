# schemas/workouts.py

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel
from .common import ListResponse
from api.models.exercices import ExerciseReference

class WorkoutSetResponse(BaseModel):
    set_number: int
    weight: Decimal
    reps: int | None = None
    is_warmup: bool | None = None
    rpe: Decimal | None = None
    rir: Decimal | None = None
    performed_at: datetime | None = None
    exercise: ExerciseReference

class WorkoutPRResponse(BaseModel):
    exercise: ExerciseReference
    metric: str
    value: Decimal
    achieved_at: datetime

class WorkoutQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    source: str | None = None

class WorkoutResponse(BaseModel):
    id: int
    date: datetime
    started_at: datetime
    ended_at: datetime | None = None
    duration: int | None = None
    sources: str | None = None
    notes: str | None = None

class WorkoutDetailResponse(WorkoutResponse):
    sets: list[WorkoutSetResponse]
    prs: list[WorkoutPRResponse]

class WorkoutListResponse(ListResponse[WorkoutResponse]):
    pass

class ExercisePRListResponse(
    ListResponse[WorkoutPRResponse]
):
    pass

class PRQuery(BaseModel):
    metric: str | None = None