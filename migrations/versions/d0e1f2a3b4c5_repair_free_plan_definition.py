"""Repair the required FREE definition and add the owner-approved default cap.

This migration is intentionally idempotent and never overwrites an existing
admin-selected max_devotional_members value.
"""

from alembic import op


revision = "d0e1f2a3b4c5"
down_revision = "c9d0e1f2a3b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO plan_definitions
            (plan, title, pricing_mode, price_toman, unit_price_toman, entitlements, enabled)
        VALUES
            ('FREE', 'رایگان', 'FIXED', 0, 0,
             '{"khatm.create": true, "report.view": true, "max_devotional_members": 100}',
             true)
        ON CONFLICT (plan) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE plan_definitions
        SET entitlements = (
            entitlements::jsonb || '{"max_devotional_members": 100}'::jsonb
        )::json
        WHERE plan = 'FREE'
          AND NOT (entitlements::jsonb ? 'max_devotional_members')
        """
    )


def downgrade() -> None:
    # Data repair is deliberately retained: deleting or guessing whether this
    # row/value was later edited by an admin would be destructive.
    pass
