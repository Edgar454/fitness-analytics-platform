from datetime import date
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class DateRangeQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    count: int