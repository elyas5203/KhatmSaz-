"""Add moderated per-platform khatm covers."""

from alembic import op
import sqlalchemy as sa

revision = "f2a3b4c5d6"
down_revision = "e1f2a3b4c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("cover_ref", sa.String(length=255), nullable=True))
    op.add_column("khatms", sa.Column("cover_platform", sa.String(length=16), nullable=True))
    op.add_column("khatms", sa.Column("cover_status", sa.String(length=16), nullable=False, server_default="NONE"))
    op.add_column("khatms", sa.Column("cover_admin_note", sa.String(length=500), nullable=True))
    op.create_index("ix_khatms_cover_status", "khatms", ["cover_status"])
    op.alter_column("khatms", "cover_status", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_khatms_cover_status", table_name="khatms")
    op.drop_column("khatms", "cover_admin_note")
    op.drop_column("khatms", "cover_status")
    op.drop_column("khatms", "cover_platform")
    op.drop_column("khatms", "cover_ref")
