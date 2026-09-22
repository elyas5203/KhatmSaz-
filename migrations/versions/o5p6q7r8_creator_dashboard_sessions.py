"""Add scoped creator sessions and contribution split snapshots."""

from alembic import op
import sqlalchemy as sa

revision = "o5p6q7r8"
down_revision = "n4o5p6q7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("purpose", sa.String(length=16), server_default="ADMIN", nullable=False),
    )
    op.create_index("ix_sessions_purpose", "sessions", ["purpose"])
    op.add_column(
        "open_contributions",
        sa.Column("counted_amount", sa.Float(), server_default="0", nullable=False),
    )
    op.add_column(
        "open_contributions",
        sa.Column("surplus_amount", sa.Float(), server_default="0", nullable=False),
    )
    op.execute("UPDATE open_contributions SET counted_amount = amount")


def downgrade() -> None:
    op.drop_column("open_contributions", "surplus_amount")
    op.drop_column("open_contributions", "counted_amount")
    op.drop_index("ix_sessions_purpose", table_name="sessions")
    op.drop_column("sessions", "purpose")
