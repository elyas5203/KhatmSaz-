"""Track user activity for inactivity-safe commitment delegation."""

from alembic import op
import sqlalchemy as sa


revision = "h8i9j0k1"
down_revision = "g7h8i9j0k1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "last_activity_at")
