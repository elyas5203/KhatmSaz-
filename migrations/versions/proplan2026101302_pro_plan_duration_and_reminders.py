"""Add duration, expiration and reminder fields to user_plans.

Revision ID: proplan2026101302
Revises: receipt2026101301
"""

from alembic import op
import sqlalchemy as sa

revision = "proplan2026101302"
down_revision = "receipt2026101301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE user_plans ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE NULL;
        ALTER TABLE user_plans ADD COLUMN IF NOT EXISTS reminded_7d BOOLEAN DEFAULT FALSE;
        ALTER TABLE user_plans ADD COLUMN IF NOT EXISTS reminded_24h BOOLEAN DEFAULT FALSE;
        ALTER TABLE user_plans ADD COLUMN IF NOT EXISTS expired_notified BOOLEAN DEFAULT FALSE;
        CREATE INDEX IF NOT EXISTS ix_user_plans_plan_expires ON user_plans(plan, expires_at);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_user_plans_plan_expires;
        ALTER TABLE user_plans DROP COLUMN IF EXISTS expired_notified;
        ALTER TABLE user_plans DROP COLUMN IF EXISTS reminded_24h;
        ALTER TABLE user_plans DROP COLUMN IF EXISTS reminded_7d;
        ALTER TABLE user_plans DROP COLUMN IF EXISTS expires_at;
        """
    )
