"""Add per-khatm creator display choice."""

from alembic import op
import sqlalchemy as sa

revision = "y5d6e7f8a9b0"
down_revision = "x4c5d6e7f8a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("creator_display_mode", sa.String(length=16), nullable=False, server_default="FULL_NAME"))
    op.add_column("khatms", sa.Column("creator_pseudonym", sa.String(length=64), nullable=True))
    op.create_check_constraint(
        "ck_khatms_creator_display_mode", "khatms",
        "creator_display_mode IN ('FULL_NAME', 'FIRST_NAME', 'PSEUDONYM', 'ANONYMOUS')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_khatms_creator_display_mode", "khatms", type_="check")
    op.drop_column("khatms", "creator_pseudonym")
    op.drop_column("khatms", "creator_display_mode")
