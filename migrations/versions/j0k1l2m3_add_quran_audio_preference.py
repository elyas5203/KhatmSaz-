"""Add opt-in Quran audio preference."""

from alembic import op
import sqlalchemy as sa

revision = "j0k1l2m3"
down_revision = "i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_settings",
        sa.Column("quran_audio_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("user_settings", "quran_audio_enabled")
