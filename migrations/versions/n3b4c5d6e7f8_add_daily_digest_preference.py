"""Add per-user daily digest preference."""

from alembic import op
import sqlalchemy as sa

revision = "n3b4c5d6e7f8"
down_revision = "m2a3b4c5d6e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_settings",
        sa.Column("daily_digest_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("user_settings", "daily_digest_enabled", server_default=None)


def downgrade() -> None:
    op.drop_column("user_settings", "daily_digest_enabled")
