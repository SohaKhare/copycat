from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Environment(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime