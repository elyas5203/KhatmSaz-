"""add schedule_weekdays to khatm_participations (owner L4: weekly multi-day)

Revision ID: schedweekdays2026100101
Revises: broadcastfilters2026093001
Create Date: 2026-10-01

A nullable text column holding comma-separated Persian weekday indices
(0=Sat..6=Fri) for a REGULAR + WEEKLY commitment that recurs on several chosen
days. Nullable + no backfill, so existing rows are unaffected.
"""
from alembic import op
import sqlalchemy as sa

revision = "schedweekdays2026100101"
down_revision = "broadcastfilters2026093001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatm_participations",
        sa.Column("schedule_weekdays", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("khatm_participations", "schedule_weekdays")
