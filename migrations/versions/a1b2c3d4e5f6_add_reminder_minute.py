"""Add reminder_minute to notification_preferences.

Owner request (2026-09-23): support per-minute delivery times (e.g. 7:45,
19:30) instead of only whole-hour values. Existing rows default to 0 (i.e.
the top of the hour they already had). The scheduler now fires every 15
minutes and uses a window check instead of an exact-hour match.
"""

import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "78e35fca4f39"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notification_preferences",
        sa.Column("reminder_minute", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("notification_preferences", "reminder_minute")
