"""Add devotional_media table: multiple audio reciters, multiple image
pages, and a PDF slot per devotional asset (owner request, 2026-09-22).

The legacy single audio_ref/image_ref columns on devotional_assets stay
untouched as a fallback for content registered before this table existed.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f4a5b6c7d8e9"
down_revision = "e3f4a5b6c7d8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "devotional_media",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("devotional_asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("reciter_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("reciter_label", sa.String(length=100), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("asset_ref", sa.String(length=500), nullable=False),
        sa.Column("asset_platform", sa.String(length=16), nullable=False, server_default="TELEGRAM"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["devotional_asset_id"], ["devotional_assets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "devotional_asset_id", "kind", "reciter_id", "page_number", "asset_platform",
            name="uq_devotional_media_identity",
        ),
    )
    op.create_index("ix_devotional_media_lookup", "devotional_media", ["devotional_asset_id", "kind"])


def downgrade() -> None:
    op.drop_index("ix_devotional_media_lookup", table_name="devotional_media")
    op.drop_table("devotional_media")
