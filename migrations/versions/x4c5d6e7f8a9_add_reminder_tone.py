"""Add creator-selected reminder tone presets."""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "x4c5d6e7f8a9"
down_revision = "w3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatms",
        sa.Column("reminder_tone", sa.String(length=16), nullable=False, server_default="FRIENDLY"),
    )
    op.create_check_constraint(
        "ck_khatms_reminder_tone", "khatms",
        "reminder_tone IN ('FRIENDLY', 'FORMAL', 'DEVOTIONAL', 'SHORT')",
    )
    templates = sa.table(
        "message_templates",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String()), sa.column("locale", sa.String()),
        sa.column("version", sa.Integer()), sa.column("body", sa.Text()),
        sa.column("enabled", sa.Boolean()),
    )
    bodies = {
        "FORMAL": {
            "reminder.first": "یادآوری رسمی\nسهم امروز شما در «{{title}}»: صفحات {{start}} تا {{end}}",
            "reminder.second": "یادآوری دوم\nسهم شما در «{{title}}»: صفحات {{start}} تا {{end}}\nمهلت: {{deadline}}:00",
            "reminder.final": "هشدار نهایی\nسهم شما در «{{title}}»: صفحات {{start}} تا {{end}}\nمهلت: {{deadline}}:00",
        },
        "DEVOTIONAL": {
            "reminder.first": "یادآوری عبادت 🌱\nسهم نورانی شما در «{{title}}»: صفحات {{start}} تا {{end}}",
            "reminder.second": "یادآوری همراهی 🌱\nدر «{{title}}» صفحات {{start}} تا {{end}} را تا {{deadline}}:00 بخوانید.",
            "reminder.final": "یادآوری پایانی 🤍\nصفحات {{start}} تا {{end}} از «{{title}}» تا {{deadline}}:00 باقی است.",
        },
        "SHORT": {
            "reminder.first": "سهم امروز: «{{title}}» صفحات {{start}} تا {{end}}",
            "reminder.second": "یادآوری دوم: صفحات {{start}} تا {{end}} تا {{deadline}}:00",
            "reminder.final": "هشدار نهایی: صفحات {{start}} تا {{end}} تا {{deadline}}:00",
        },
    }
    op.bulk_insert(
        templates,
        [
            {"id": uuid.uuid4(), "key": f"{key}.{tone.lower()}", "locale": "fa",
             "version": 1, "body": body, "enabled": True}
            for tone, values in bodies.items() for key, body in values.items()
        ],
    )


def downgrade() -> None:
    op.execute(sa.text(
        "DELETE FROM message_templates WHERE locale = 'fa' AND "
        "(key LIKE '%.formal' OR key LIKE '%.devotional' OR key LIKE '%.short')"
    ))
    op.drop_constraint("ck_khatms_reminder_tone", "khatms", type_="check")
    op.drop_column("khatms", "reminder_tone")
