"""Add locale-keyed, versioned message templates with Persian defaults.

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
"""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "i9d0e1f2a3b4"
down_revision = "h8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "message_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "locale", "version", name="uq_message_templates_key_locale_version"),
    )
    op.create_index(
        "ix_message_templates_key_locale_enabled",
        "message_templates",
        ["key", "locale", "enabled"],
    )

    templates = sa.table(
        "message_templates",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String()),
        sa.column("locale", sa.String()),
        sa.column("version", sa.Integer()),
        sa.column("body", sa.Text()),
        sa.column("enabled", sa.Boolean()),
    )
    defaults = [
        ("reminder.first", "یادآوری 🌱\nسهم امروزتان در «{{title}}»: صفحات {{start}} تا {{end}}"),
        ("reminder.second", "یادآوری دوم 🌱\nسهم امروزتان در «{{title}}»: صفحات {{start}} تا {{end}}\nمهلت انجام تا ساعت {{deadline}}:00 است."),
        ("reminder.final", "هشدار نهایی قبل از مهلت ⏰\nسهم امروزتان در «{{title}}»: صفحات {{start}} تا {{end}}\nمهلت انجام تا ساعت {{deadline}}:00 است."),
        ("reminder.missed", "مهلت امروز برای «{{title}}» گذشت — جای نگرانی نیست 🤍\nسهمتون به استخر مشترک این ختم برگشت تا کل ختم عقب نیفته. هر وقت خواستید از «🕋 ختم‌های من» یک سهم جدید بردارید."),
        ("reminder.creator_miss", "یکی از اعضای «{{title}}» برای {{misses}}اُمین بار سهمش رو سر وقت انجام نداده.\nاین پیام فقط اطلاع‌رسانیه — فعلاً هیچ اقدام خودکاری انجام نمی‌شه."),
    ]
    op.bulk_insert(
        templates,
        [
            {"id": uuid.uuid4(), "key": key, "locale": "fa", "version": 1, "body": body, "enabled": True}
            for key, body in defaults
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_message_templates_key_locale_enabled", table_name="message_templates")
    op.drop_table("message_templates")
