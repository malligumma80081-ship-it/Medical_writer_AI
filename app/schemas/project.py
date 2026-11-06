import uuid

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):

    name: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str | None = None


class ProjectResponse(BaseModel):

    id: uuid.UUID
    name: str
    description: str | None
    status: str
    owner_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )