"""Add optional date-based khatm ending."""

from alembic import op
import sqlalchemy as sa

revision = "c9d0e1f2a3"
down_revision = "b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("end_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_khatms_end_at", "khatms", ["end_at"])


def downgrade() -> None:
    op.drop_index("ix_khatms_end_at", table_name="khatms")
    op.drop_column("khatms", "end_at")
