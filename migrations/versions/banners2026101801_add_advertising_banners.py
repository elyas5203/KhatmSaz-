"""Add advertising_banners table.

Revision ID: banners2026101801
Revises: support2026101801
"""

from alembic import op
import sqlalchemy as sa

revision = "banners2026101801"
down_revision = "support2026101801"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS advertising_banners (
            id UUID PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            banner_type VARCHAR(32) NOT NULL DEFAULT 'SYSTEM_CULTURAL',
            placement VARCHAR(32) NOT NULL DEFAULT 'ALL',
            content_text TEXT NOT NULL,
            image_url VARCHAR(500),
            button_text VARCHAR(100),
            button_url VARCHAR(500),
            creator_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            khatm_id UUID REFERENCES khatms(id) ON DELETE SET NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            status VARCHAR(32) NOT NULL DEFAULT 'APPROVED',
            audience_count INTEGER NOT NULL DEFAULT 0,
            cost_toman INTEGER NOT NULL DEFAULT 0,
            impressions_count INTEGER NOT NULL DEFAULT 0,
            clicks_count INTEGER NOT NULL DEFAULT 0,
            starts_at TIMESTAMP WITH TIME ZONE,
            ends_at TIMESTAMP WITH TIME ZONE,
            admin_note VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_advertising_banners_status_active ON advertising_banners(status, is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_advertising_banners_placement ON advertising_banners(placement)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_advertising_banners_banner_type ON advertising_banners(banner_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_advertising_banners_created_at ON advertising_banners(created_at)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS advertising_banners;")
