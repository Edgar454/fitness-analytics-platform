from typing import Any
from datetime import datetime

from pydantic import BaseModel


class CredentialCreate(BaseModel):
    provider: str
    credentials: dict[str, Any]

class CredentialResponse(BaseModel):
    id: int
    provider: str
    active: bool
    created_at: datetime
    updated_at: datetime | None