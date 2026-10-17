"""Add transfer and deactivation fields to khatms (Rule 5).

Revision ID: khatm2026101501
Revises: proplan2026101302
"""

from alembic import op
import sqlalchemy as sa

revision = "khatm2026101501"
down_revision = "proplan2026101302"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE khatms ADD COLUMN IF NOT EXISTS join_link_closed BOOLEAN DEFAULT FALSE;")
    op.execute("ALTER TABLE khatms ADD COLUMN IF NOT EXISTS transfer_request_status VARCHAR(20) DEFAULT 'NONE';")
    op.execute("ALTER TABLE khatms ADD COLUMN IF NOT EXISTS transfer_request_reason VARCHAR(500);")
    op.execute("ALTER TABLE khatms ADD COLUMN IF NOT EXISTS transfer_requested_at TIMESTAMP WITH TIME ZONE;")
    op.execute("ALTER TABLE khatms ADD COLUMN IF NOT EXISTS transferred_to_admin_at TIMESTAMP WITH TIME ZONE;")
    op.execute("ALTER TABLE khatms ADD COLUMN IF NOT EXISTS transferred_from_user_id UUID REFERENCES users(id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_khatms_transfer_status ON khatms(transfer_request_status);")


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_khatms_transfer_status;
        ALTER TABLE khatms DROP COLUMN IF EXISTS transferred_from_user_id;
        ALTER TABLE khatms DROP COLUMN IF EXISTS transferred_to_admin_at;
        ALTER TABLE khatms DROP COLUMN IF EXISTS transfer_requested_at;
        ALTER TABLE khatms DROP COLUMN IF EXISTS transfer_request_reason;
        ALTER TABLE khatms DROP COLUMN IF EXISTS transfer_request_status;
        ALTER TABLE khatms DROP COLUMN IF EXISTS join_link_closed;
        """
    )
