"""Add configurable creator miss-notice threshold and window."""

from alembic import op
import sqlalchemy as sa

revision = "d0e1f2a3b4"
down_revision = "c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("miss_notice_threshold", sa.SmallInteger(), nullable=False, server_default="2"))
    op.add_column("khatms", sa.Column("miss_notice_window_days", sa.SmallInteger(), nullable=False, server_default="7"))
    op.alter_column("khatms", "miss_notice_threshold", server_default=None)
    op.alter_column("khatms", "miss_notice_window_days", server_default=None)


def downgrade() -> None:
    op.drop_column("khatms", "miss_notice_window_days")
    op.drop_column("khatms", "miss_notice_threshold")
