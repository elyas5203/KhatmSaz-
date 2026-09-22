"""Add exact-page Quran asset registry."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "s8d9e0f1a2b3"
down_revision = "r7c8d9e0f1a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quran_page_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("edition_id", sa.String(length=64), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("reciter_id", sa.String(length=64), nullable=False),
        sa.Column("asset_ref", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("edition_id", "page_number", "kind", "reciter_id", name="uq_quran_page_assets_identity"),
        sa.CheckConstraint("kind IN ('IMAGE', 'AUDIO', 'TEXT')", name="ck_quran_page_assets_kind"),
    )
    op.create_index("ix_quran_page_assets_lookup", "quran_page_assets", ["edition_id", "page_number", "kind", "reciter_id"])


def downgrade() -> None:
    op.drop_index("ix_quran_page_assets_lookup", table_name="quran_page_assets")
    op.drop_table("quran_page_assets")
