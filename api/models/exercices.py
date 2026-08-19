# schemas/exercises.py

from pydantic import BaseModel
from .common import ListResponse

class ExerciseReference(BaseModel):
    id: int
    name: str

class EquipmentResponse(BaseModel):
    id: int
    name: str


class BodyPartResponse(BaseModel):
    id: int
    name: str


class MuscleResponse(BaseModel):
    id: int
    name: str

class ExerciseResponse(BaseModel):
    id: int
    name: str
    category: str | None = None
    image_url: str | None = None

    equipment: list[EquipmentResponse]
    body_parts: list[BodyPartResponse]
    target_muscles: list[MuscleResponse]
    synergist_muscles: list[MuscleResponse]

class ExerciseQuery(BaseModel):
    search: str | None = None
    category: str | None = None
    equipment_id: int | None = None
    body_part_id: int | None = None
    muscle_id: int | None = None

class ExerciseListResponse(ListResponse[ExerciseResponse]):
    pass