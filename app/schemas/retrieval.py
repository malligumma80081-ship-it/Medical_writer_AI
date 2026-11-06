from pydantic import BaseModel, Field
from uuid import UUID


class SearchRequest(BaseModel):
    project_id: UUID
    query: str = Field(min_length=3, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)