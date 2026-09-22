"""Add per-khatm content delivery mode."""

from alembic import op
import sqlalchemy as sa

revision = "t0f1a2b3c4d5"
down_revision = "s8d9e0f1a2b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatms",
        sa.Column("content_delivery_mode", sa.String(length=16), nullable=False, server_default="AUTO"),
    )
    op.create_check_constraint(
        "ck_khatms_content_delivery_mode",
        "khatms",
        "content_delivery_mode IN ('AUTO', 'PHOTO', 'TEXT')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_khatms_content_delivery_mode", "khatms", type_="check")
    op.drop_column("khatms", "content_delivery_mode")
