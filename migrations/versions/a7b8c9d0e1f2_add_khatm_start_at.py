"""Add optional scheduled start time to khatms."""

from alembic import op
import sqlalchemy as sa

revision = "a7b8c9d0e1f2"
down_revision = "z6e7f8a9b0c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("start_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_khatms_start_at", "khatms", ["start_at"])


def downgrade() -> None:
    op.drop_index("ix_khatms_start_at", table_name="khatms")
    op.drop_column("khatms", "start_at")
