import uuid

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from app.models.document_chunk import DocumentChunk
from app.models.project import Project
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column


class Document(Base):

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    page_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="UPLOADED",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="documents",
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    source_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extraction_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    pages: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
