"""Add the admin-curated dua/ziyarat asset library."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "v2a3b4c5d6e7"
down_revision = "u1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devotional_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_type", sa.String(length=16), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("text_body", sa.String(), nullable=True),
        sa.Column("audio_ref", sa.String(length=500), nullable=True),
        sa.Column("audio_platform", sa.String(length=16), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.CheckConstraint("content_type IN ('DUA', 'ZIYARAT')", name="ck_devotional_assets_type"),
        sa.CheckConstraint("audio_platform IS NULL OR audio_platform IN ('TELEGRAM', 'BALE')", name="ck_devotional_assets_audio_platform"),
    )
    op.create_index("ix_devotional_assets_type_enabled", "devotional_assets", ["content_type", "enabled"])


def downgrade() -> None:
    op.drop_index("ix_devotional_assets_type_enabled", table_name="devotional_assets")
    op.drop_table("devotional_assets")
