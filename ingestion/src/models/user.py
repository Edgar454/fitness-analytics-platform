import enum
from .base import FitnessBase
from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, LargeBinary, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped


class Provider(str, enum.Enum):
    GOOGLE_HEALTH = "google_health"
    FATSECRET = "fatsecret"
    LYFTA = "lyfta"


class User(FitnessBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime]
    last_active: Mapped[Optional[datetime]]

    def __repr__(self) -> str:
        return f"User<id={self.id!r}, email={self.email!r}>"


class UserCredential(FitnessBase):
    __tablename__ = "user_credentials"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_credentials_user_provider"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[Provider] = mapped_column(Enum(Provider))
    encrypted_payload: Mapped[bytes] = mapped_column(LargeBinary)  # JSON chiffré (KMS), contenu variable par provider
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime]
    updated_at: Mapped[Optional[datetime]]

    def __repr__(self) -> str:
        return f"UserCredential<user_id={self.user_id!r}, provider={self.provider!r}>"