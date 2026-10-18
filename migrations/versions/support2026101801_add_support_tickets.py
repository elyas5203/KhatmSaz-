"""Add support_tickets table.

Revision ID: support2026101801
Revises: khatm2026101501
"""

from alembic import op
import sqlalchemy as sa

revision = "support2026101801"
down_revision = "khatm2026101501"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS support_tickets (
            id UUID PRIMARY KEY,
            sender_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            target_role VARCHAR(32) NOT NULL DEFAULT 'SUPER_ADMIN',
            target_creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
            subject VARCHAR(200),
            body TEXT NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
            reply_text TEXT,
            replied_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            replied_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_support_tickets_status ON support_tickets(status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_support_tickets_sender ON support_tickets(sender_user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_support_tickets_target_creator ON support_tickets(target_creator_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_support_tickets_created_at ON support_tickets(created_at)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS support_tickets;")
