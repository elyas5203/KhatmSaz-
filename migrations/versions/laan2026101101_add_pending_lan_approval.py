"""Add pending_lan_approval to khatms table.

Revision ID: laan2026101101
Revises: khutbah2026100801
"""

from alembic import op
import sqlalchemy as sa

revision = "laan2026101101"
down_revision = "khutbah2026100801"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE khatms ADD COLUMN IF NOT EXISTS pending_lan_approval BOOLEAN DEFAULT FALSE NOT NULL;"
    )


def downgrade() -> None:
    op.drop_column("khatms", "pending_lan_approval")
