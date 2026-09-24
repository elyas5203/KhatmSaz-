"""add creator_broadcasts

Revision ID: 33382c085479
Revises: 2441f6d73dea
Create Date: 2026-09-24 13:55:02.211934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '33382c085479'
down_revision: Union[str, None] = '2441f6d73dea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "creator_broadcasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("message_text", sa.String, nullable=True),
        sa.Column("media_file_id", sa.String, nullable=True),
        sa.Column("media_type", sa.String(length=16), nullable=True),
        sa.Column("cost_toman", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_paid", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("audience_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("creator_broadcasts")
