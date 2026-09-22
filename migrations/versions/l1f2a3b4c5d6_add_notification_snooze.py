"""Add per-participation reminder snooze state."""

from alembic import op
import sqlalchemy as sa

revision = "l1f2a3b4c5d6"
down_revision = "k0e1f2a3b4c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notification_preferences",
        sa.Column("snoozed_until", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("notification_preferences", "snoozed_until")
