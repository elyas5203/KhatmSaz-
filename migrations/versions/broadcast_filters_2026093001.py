"""Add composable province/gender filters to moderated broadcasts.

Revision ID: broadcastfilters2026093001
Revises: broadcast2026092901
Create Date: 2026-09-30
"""

from alembic import op
import sqlalchemy as sa

revision = "broadcastfilters2026093001"
down_revision = "broadcast2026092901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatm_broadcasts", sa.Column("target_province", sa.String(100), nullable=True))
    op.add_column("khatm_broadcasts", sa.Column("target_gender", sa.String(16), nullable=True))


def downgrade() -> None:
    op.drop_column("khatm_broadcasts", "target_gender")
    op.drop_column("khatm_broadcasts", "target_province")
