"""Add soft-deletion marker for user accounts."""

from alembic import op
import sqlalchemy as sa


revision = "i9j0k1l2"
down_revision = "h8i9j0k1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "deleted_at")
