"""Add generic admin-editable system_settings key/value table.

Owner request (2026-09-21): make small system-wide numeric defaults
(reminder hour, inactivity days, miss-notice threshold/window) editable
from the admin panel instead of hardcoded Python constants, without a new
migration for every future one of these.
"""

from alembic import op
import sqlalchemy as sa

revision = "d2e3f4a5b6c7"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=500), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("system_settings")
