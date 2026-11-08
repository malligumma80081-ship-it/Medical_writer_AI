import uuid

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    DateTime,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ClaimVerification(Base):

    __tablename__ = "claim_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    generation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("generations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    claim_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    citation_ids: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    evidence_details: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    verified_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )