"""Add khatm_broadcast_receipts table for read/engagement analytics.

Revision ID: bcreceipt2026102001
Revises: banners2026101801
"""

from alembic import op
import sqlalchemy as sa

revision = "bcreceipt2026102001"
down_revision = "banners2026101801"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS khatm_broadcast_receipts (
            id UUID PRIMARY KEY,
            broadcast_id UUID NOT NULL REFERENCES khatm_broadcasts(id) ON DELETE CASCADE,
            recipient_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            channel VARCHAR(16) NOT NULL DEFAULT 'TELEGRAM',
            status VARCHAR(20) NOT NULL DEFAULT 'DELIVERED',
            delivered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            seen_at TIMESTAMP WITH TIME ZONE,
            seen_source VARCHAR(32)
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_khatm_broadcast_receipts_user_seen ON khatm_broadcast_receipts(recipient_user_id, seen_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_khatm_broadcast_receipts_bc_status ON khatm_broadcast_receipts(broadcast_id, status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_khatm_broadcast_receipts_broadcast_id ON khatm_broadcast_receipts(broadcast_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_khatm_broadcast_receipts_recipient_id ON khatm_broadcast_receipts(recipient_user_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS khatm_broadcast_receipts")
