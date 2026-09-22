"""Keep Quran media references separate per bot platform."""

from alembic import op
import sqlalchemy as sa

revision = "u1f2a3b4c5d6"
down_revision = "t0f1a2b3c4d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "quran_page_assets",
        sa.Column("asset_platform", sa.String(length=16), nullable=False, server_default="TELEGRAM"),
    )
    op.drop_constraint("uq_quran_page_assets_identity", "quran_page_assets", type_="unique")
    op.create_unique_constraint(
        "uq_quran_page_assets_identity",
        "quran_page_assets",
        ["edition_id", "page_number", "kind", "reciter_id", "asset_platform"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_quran_page_assets_identity", "quran_page_assets", type_="unique")
    op.create_unique_constraint(
        "uq_quran_page_assets_identity",
        "quran_page_assets",
        ["edition_id", "page_number", "kind", "reciter_id"],
    )
    op.drop_column("quran_page_assets", "asset_platform")
