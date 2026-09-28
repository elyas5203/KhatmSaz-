"""R11 (owner 2026-09-28): member-chosen commitment mode + schedule.

The member decides how they commit to a commitment khatm:
  • REGULAR — a recurring schedule (daily/weekly/monthly) delivered at a chosen
    hour, reading `commitment_per_occurrence` each time.
  • COUNT   — a one-off pledge of `commitment_target` repetitions, logged with a
    button; on completion they can pledge a fresh count (target/done reset).

Adds nullable columns to `khatm_participations`; all default to NULL/0 so
existing rows are untouched.

Revision ID: mcm2026092802
Revises: mrg2026092801
Create Date: 2026-09-28
"""
from alembic import op
import sqlalchemy as sa

revision = "mcm2026092802"
down_revision = "mrg2026092801"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatm_participations", sa.Column("commitment_mode", sa.String(length=16), nullable=True))
    op.add_column("khatm_participations", sa.Column("commitment_target", sa.Integer(), nullable=True))
    op.add_column(
        "khatm_participations",
        sa.Column("commitment_done", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("khatm_participations", sa.Column("schedule_freq", sa.String(length=16), nullable=True))
    op.add_column("khatm_participations", sa.Column("schedule_anchor", sa.Integer(), nullable=True))
    op.add_column("khatm_participations", sa.Column("schedule_hour", sa.Integer(), nullable=True))
    op.add_column("khatm_participations", sa.Column("commitment_per_occurrence", sa.Integer(), nullable=True))
    op.add_column(
        "khatm_participations",
        sa.Column("schedule_last_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Drop the server_default now that the column exists — the ORM supplies 0.
    op.alter_column("khatm_participations", "commitment_done", server_default=None)


def downgrade() -> None:
    for col in (
        "schedule_last_sent_at",
        "commitment_per_occurrence",
        "schedule_hour",
        "schedule_anchor",
        "schedule_freq",
        "commitment_done",
        "commitment_target",
        "commitment_mode",
    ):
        op.drop_column("khatm_participations", col)
