from typing import Optional, List
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column, relationship, Mapped

from .base import FitnessBase


class Equipment(FitnessBase):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)  # id Lyfta exact, pas généré
    name: Mapped[str]


class BodyPart(FitnessBase):
    __tablename__ = "body_part"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]


class Muscle(FitnessBase):
    __tablename__ = "muscle"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]