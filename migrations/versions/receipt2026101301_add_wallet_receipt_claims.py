"""Add wallet_receipt_claims table.

Revision ID: receipt2026101301
Revises: laan2026101101
"""

from alembic import op
import sqlalchemy as sa

revision = "receipt2026101301"
down_revision = "laan2026101101"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS wallet_receipt_claims (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount_toman INTEGER NOT NULL,
            photo_file_id VARCHAR(255) NOT NULL,
            photo_file_id_bale VARCHAR(255),
            status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
            admin_user_id UUID REFERENCES users(id),
            admin_note VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            reviewed_at TIMESTAMP WITH TIME ZONE
        );
        CREATE INDEX IF NOT EXISTS ix_wallet_receipt_claims_user ON wallet_receipt_claims(user_id);
        CREATE INDEX IF NOT EXISTS ix_wallet_receipt_claims_status ON wallet_receipt_claims(status);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS wallet_receipt_claims;")
