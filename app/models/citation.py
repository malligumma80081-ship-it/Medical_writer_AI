import uuid

from sqlalchemy import (
    Integer,
    Text,
    String,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.generation import Generation


class Citation(Base):

    __tablename__ = "citations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    generation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=False,
    )

    chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="RESTRICT"),
        nullable=True,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    cited_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False,
    )

    generation: Mapped["Generation"] = relationship(
        back_populates="citations",
    )