import uuid
from xml.dom.minidom import Document

from sqlalchemy import (
    Integer,
    Text,
    String,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column



class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    section: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    document: Mapped["Document"] = relationship(
        back_populates="chunks",
    )
