from typing import Optional, List
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column, relationship, Mapped

from ingestion.src.models.base import Base


class Equipment(Base):
    __tablename__ = "equipment"
    __table_args__ = {"schema": "fitness"}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)  # id Lyfta exact, pas généré
    name: Mapped[str]


class BodyPart(Base):
    __tablename__ = "body_part"
    __table_args__ = {"schema": "fitness"}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]


class Muscle(Base):
    __tablename__ = "muscle"
    __table_args__ = {"schema": "fitness"}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]