"""add partial progress to quantity portions

Revision ID: d4e5f6a7b8c9
Revises: cf308fcab881
Create Date: 2026-09-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "cf308fcab881"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Hand-written migration; do not touch the hand-maintained partial indexes.
    op.add_column(
        "khatm_portions",
        sa.Column("completed_quantity", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("khatm_portions", "completed_quantity")
