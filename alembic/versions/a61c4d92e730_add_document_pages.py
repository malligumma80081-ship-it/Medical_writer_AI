"""add document pages

Revision ID: a61c4d92e730
Revises: 005fe7ca038d
Create Date: 2026-11-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a61c4d92e730"
down_revision: Union[str, Sequence[str], None] = "005fe7ca038d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "pages",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("documents", "pages")
