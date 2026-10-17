"""Allow KHUTBAH in ck_devotional_assets_type.

Revision ID: khutbah2026100801
Revises: share2026100501
"""

from alembic import op

revision = "khutbah2026100801"
down_revision = "share2026100501"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_devotional_assets_type", "devotional_assets", type_="check")
    op.create_check_constraint(
        "ck_devotional_assets_type",
        "devotional_assets",
        "content_type IN ('DUA', 'ZIYARAT', 'SALAWAT', 'KHUTBAH')",
    )
    op.execute("ALTER TYPE khatmcategorygroup ADD VALUE IF NOT EXISTS 'KHUTBAH'")


def downgrade() -> None:
    op.execute("DELETE FROM devotional_assets WHERE content_type = 'KHUTBAH'")
    op.drop_constraint("ck_devotional_assets_type", "devotional_assets", type_="check")
    op.create_check_constraint(
        "ck_devotional_assets_type",
        "devotional_assets",
        "content_type IN ('DUA', 'ZIYARAT', 'SALAWAT')",
    )
