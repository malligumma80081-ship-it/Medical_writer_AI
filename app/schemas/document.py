import uuid

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):

    id: uuid.UUID

    project_id: uuid.UUID

    title: str

    file_name: str

    file_type: str

    page_count: int

    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class DocumentDetail(DocumentResponse):

    source_metadata: dict

    extracted_text: str | None