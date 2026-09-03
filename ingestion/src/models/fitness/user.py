import enum
from src.models.base import Base
from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, LargeBinary, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped


class Provider(str, enum.Enum):
    GOOGLE_HEALTH = "google_health"
    FATSECRET = "fatsecret"
    LYFTA = "lyfta"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "fitness"}

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime]
    last_active: Mapped[Optional[datetime]]

    def __repr__(self) -> str:
        return f"User<id={self.id!r}, email={self.email!r}>"


class UserCredential(Base):
    __tablename__ = "user_credentials"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_credentials_user_provider"),
        {"schema": "fitness"}
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("fitness.users.id"))
    provider: Mapped[Provider] = mapped_column(Enum(Provider))
    encrypted_payload: Mapped[bytes] = mapped_column(LargeBinary)  # JSON chiffré (KMS), contenu variable par provider
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime]
    updated_at: Mapped[Optional[datetime]]

    def __repr__(self) -> str:
        return f"UserCredential<user_id={self.user_id!r}, provider={self.provider!r}>"