"""Allow the fixed Salawat asset in the devotional asset table.

Revision ID: devsalawat2026100102
Revises: schedweekdays2026100101
"""

from alembic import op


revision = "devsalawat2026100102"
down_revision = "schedweekdays2026100101"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_devotional_assets_type", "devotional_assets", type_="check")
    op.create_check_constraint(
        "ck_devotional_assets_type",
        "devotional_assets",
        "content_type IN ('DUA', 'ZIYARAT', 'SALAWAT')",
    )


def downgrade() -> None:
    # The pre-feature schema has nowhere valid to retain the one fixed
    # Salawat row. Remove only that well-known synthetic asset before
    # restoring the narrower historical constraint.
    op.execute("DELETE FROM devotional_assets WHERE content_type = 'SALAWAT'")
    op.drop_constraint("ck_devotional_assets_type", "devotional_assets", type_="check")
    op.create_check_constraint(
        "ck_devotional_assets_type",
        "devotional_assets",
        "content_type IN ('DUA', 'ZIYARAT')",
    )
