"""Add distinct staged reminder kinds to the PostgreSQL enum.

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
"""

from alembic import op

revision = "g7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE notificationkind ADD VALUE IF NOT EXISTS 'SECOND_REMINDER'")
    op.execute("ALTER TYPE notificationkind ADD VALUE IF NOT EXISTS 'FINAL_REMINDER'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum labels safely in-place.
    pass
