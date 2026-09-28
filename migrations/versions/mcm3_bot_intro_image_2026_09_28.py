"""R2 (owner 2026-09-28): per-bot intro image shown after mode selection.

Each member bot (Quran/Salawat/Dua/La'an × lang × platform) can have its own
intro image — uploaded in the admin panel — displayed with the caption
"همه ختم‌ها به نیت صاحب‌الزمان" so a creator (and member) sees how every khatm is
presented. Adds a nullable column to `bot_instances`; existing rows untouched.

Revision ID: bii2026092803
Revises: mcm2026092802
Create Date: 2026-09-28
"""
from alembic import op
import sqlalchemy as sa

revision = "bii2026092803"
down_revision = "mcm2026092802"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bot_instances", sa.Column("intro_image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("bot_instances", "intro_image_url")
