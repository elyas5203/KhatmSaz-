"""add bot_instances

Revision ID: a1b2c3d4e5f6
Revises: 33382c085479
Create Date: 2026-09-26 10:00:00.000000

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '33382c085479'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEED_ROWS = [
    # --- CREATOR bots (no category, no language) ---
    ("TELEGRAM", "CREATOR", None, None, "ختم‌ساز تلگرام"),
    ("BALE",     "CREATOR", None, None, "ختم‌ساز بله"),
    # --- MEMBER bots: TELEGRAM ---
    ("TELEGRAM", "MEMBER", "QURAN",      "fa", "ختم قرآن فارسی (تلگرام)"),
    ("TELEGRAM", "MEMBER", "QURAN",      "ar", "ختم القرآن العربیة (تلگرام)"),
    ("TELEGRAM", "MEMBER", "QURAN",      "en", "Quran Khatm (Telegram)"),
    ("TELEGRAM", "MEMBER", "SALAWAT",    "fa", "ختم صلوات فارسی (تلگرام)"),
    ("TELEGRAM", "MEMBER", "SALAWAT",    "ar", "ختم الصلوات العربیة (تلگرام)"),
    ("TELEGRAM", "MEMBER", "SALAWAT",    "en", "Salawat Khatm (Telegram)"),
    ("TELEGRAM", "MEMBER", "DUA_ZIYARAT","fa", "ختم دعا و زیارت فارسی (تلگرام)"),
    ("TELEGRAM", "MEMBER", "DUA_ZIYARAT","ar", "ختم الدعاء و الزیارة العربیة (تلگرام)"),
    ("TELEGRAM", "MEMBER", "DUA_ZIYARAT","en", "Dua & Ziyarat Khatm (Telegram)"),
    ("TELEGRAM", "MEMBER", "LAAN",       "fa", "ختم لعن فارسی (تلگرام)"),
    ("TELEGRAM", "MEMBER", "LAAN",       "ar", "ختم اللعن العربیة (تلگرام)"),
    ("TELEGRAM", "MEMBER", "LAAN",       "en", "La'n Khatm (Telegram)"),
    # --- MEMBER bots: BALE ---
    ("BALE", "MEMBER", "QURAN",      "fa", "ختم قرآن فارسی (بله)"),
    ("BALE", "MEMBER", "QURAN",      "ar", "ختم القرآن العربیة (بله)"),
    ("BALE", "MEMBER", "QURAN",      "en", "Quran Khatm (Bale)"),
    ("BALE", "MEMBER", "SALAWAT",    "fa", "ختم صلوات فارسی (بله)"),
    ("BALE", "MEMBER", "SALAWAT",    "ar", "ختم الصلوات العربیة (بله)"),
    ("BALE", "MEMBER", "SALAWAT",    "en", "Salawat Khatm (Bale)"),
    ("BALE", "MEMBER", "DUA_ZIYARAT","fa", "ختم دعا و زیارت فارسی (بله)"),
    ("BALE", "MEMBER", "DUA_ZIYARAT","ar", "ختم الدعاء و الزیارة العربیة (بله)"),
    ("BALE", "MEMBER", "DUA_ZIYARAT","en", "Dua & Ziyarat Khatm (Bale)"),
    ("BALE", "MEMBER", "LAAN",       "fa", "ختم لعن فارسی (بله)"),
    ("BALE", "MEMBER", "LAAN",       "ar", "ختم اللعن العربیة (بله)"),
    ("BALE", "MEMBER", "LAAN",       "en", "La'n Khatm (Bale)"),
]


def upgrade() -> None:
    bot_instances = op.create_table(
        "bot_instances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("platform", sa.String(10), nullable=False),
        sa.Column("bot_role", sa.String(10), nullable=False),
        sa.Column("category", sa.String(20), nullable=True),
        sa.Column("language", sa.String(2), nullable=True),
        sa.Column("token_encrypted", sa.Text(), nullable=False, server_default=""),
        sa.Column("username", sa.String(100), nullable=False, server_default=""),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "platform", "bot_role", "category", "language",
            name="uq_bot_instance_slot",
        ),
    )

    op.bulk_insert(
        bot_instances,
        [
            {
                "id": str(uuid4()),
                "platform": platform,
                "bot_role": role,
                "category": category,
                "language": language,
                "display_name": display_name,
            }
            for platform, role, category, language, display_name in SEED_ROWS
        ],
    )


def downgrade() -> None:
    op.drop_table("bot_instances")
