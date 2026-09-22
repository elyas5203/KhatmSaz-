"""Add per-participant open-Quran-reading plan columns.

Owner request (2026-09-21): an OPEN (or waitlisted) Quran reader can set a
daily page count once, instead of only self-reporting a bare number with no
actual page content ever sent. See `docs/ai/DECISIONS.md` and
`bot/handlers/portions.py`.
"""

from alembic import op
import sqlalchemy as sa

revision = "r9s0t1u2v3w4"
down_revision = "d0e1f2a3b4c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatm_participations",
        sa.Column("open_reading_pages_per_day", sa.Integer(), nullable=True),
    )
    op.add_column(
        "khatm_participations",
        sa.Column("open_reading_next_page", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "khatm_participations",
        sa.Column("open_reading_last_sent_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("khatm_participations", "open_reading_last_sent_at")
    op.drop_column("khatm_participations", "open_reading_next_page")
    op.drop_column("khatm_participations", "open_reading_pages_per_day")
