"""Seed Arabic and English reminder templates."""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "k0e1f2a3b4c5"
down_revision = "j0e1f2a3b4c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    templates = sa.table(
        "message_templates",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String()),
        sa.column("locale", sa.String()),
        sa.column("version", sa.Integer()),
        sa.column("body", sa.Text()),
        sa.column("enabled", sa.Boolean()),
    )
    translations = {
        "ar": {
            "reminder.first": "تذكير 🌱\nحصتكم اليوم في «{{title}}»: الصفحات {{start}} إلى {{end}}",
            "reminder.second": "التذكير الثاني 🌱\nحصتكم اليوم في «{{title}}»: الصفحات {{start}} إلى {{end}}\nالموعد النهائي الساعة {{deadline}}:00.",
            "reminder.final": "تنبيه نهائي قبل الموعد ⏰\nحصتكم اليوم في «{{title}}»: الصفحات {{start}} إلى {{end}}\nالموعد النهائي الساعة {{deadline}}:00.",
            "reminder.missed": "انتهى موعد اليوم لـ«{{title}}» — لا تقلقوا 🤍\nأعيدت الحصة إلى المجموعة المشتركة حتى لا يتأخر الختم.",
            "reminder.creator_miss": "أحد أعضاء «{{title}}» لم ينجز حصته للمرة {{misses}}. هذا إشعار فقط ولا يوجد إجراء تلقائي.",
        },
        "en": {
            "reminder.first": "Reminder 🌱\nYour share in “{{title}}” today: pages {{start}} to {{end}}",
            "reminder.second": "Second reminder 🌱\nYour share in “{{title}}” today: pages {{start}} to {{end}}\nDeadline: {{deadline}}:00.",
            "reminder.final": "Final reminder before the deadline ⏰\nYour share in “{{title}}” today: pages {{start}} to {{end}}\nDeadline: {{deadline}}:00.",
            "reminder.missed": "Today’s deadline for “{{title}}” has passed — no worries 🤍\nYour share was returned to the shared pool so the khatm can stay on track.",
            "reminder.creator_miss": "A member of “{{title}}” missed their share for the {{misses}} time. This is informational; no automatic action was taken.",
        },
    }
    op.bulk_insert(
        templates,
        [
            {"id": uuid.uuid4(), "key": key, "locale": locale, "version": 1, "body": body, "enabled": True}
            for locale, values in translations.items()
            for key, body in values.items()
        ],
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM message_templates WHERE locale IN ('ar', 'en')"))
