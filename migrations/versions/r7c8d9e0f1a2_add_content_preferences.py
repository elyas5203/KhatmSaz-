"""Add per-user translation and tafsir preferences."""

from alembic import op
import sqlalchemy as sa

revision = "r7c8d9e0f1a2"
down_revision = "q6b7c8d9e0f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_settings", sa.Column("translation_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("user_settings", sa.Column("tafsir_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("user_settings", "translation_enabled", server_default=None)
    op.alter_column("user_settings", "tafsir_enabled", server_default=None)


def downgrade() -> None:
    op.drop_column("user_settings", "tafsir_enabled")
    op.drop_column("user_settings", "translation_enabled")
