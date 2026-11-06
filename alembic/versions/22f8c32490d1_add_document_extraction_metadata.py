"""add document extraction metadata

Revision ID: 22f8c32490d1
Revises: 4b97894caaf5
Create Date: 2026-11-05 11:03:21.596182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22f8c32490d1'
down_revision: Union[str, Sequence[str], None] = '4b97894caaf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("auth_sessions") as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sa.NUMERIC(),
            type_=sa.Uuid(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "user_id",
            existing_type=sa.NUMERIC(),
            type_=sa.Uuid(),
            existing_nullable=False,
        )

    op.add_column(
        "documents",
        sa.Column(
            "source_metadata",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("extraction_error", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("documents", "extraction_error")
    op.drop_column("documents", "extracted_text")
    op.drop_column("documents", "source_metadata")

    with op.batch_alter_table("auth_sessions") as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Uuid(),
            type_=sa.NUMERIC(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "id",
            existing_type=sa.Uuid(),
            type_=sa.NUMERIC(),
            existing_nullable=False,
        )
