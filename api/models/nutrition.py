# schemas/nutrition.py

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from .common import ListResponse


class NutritionQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    source: str | None = None


class NutritionResponse(BaseModel):
    date: date
    calories: Decimal | None = None
    protein: Decimal | None = None
    fat: Decimal | None = None
    carbs: Decimal | None = None
    fiber: Decimal | None = None
    water: Decimal | None = None
    source: str | None = None


class NutritionListResponse(ListResponse[NutritionResponse]):
    pass