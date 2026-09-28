"""merge the 3 divergent heads into one (2026-09-28)

Three migration branches accumulated in parallel (multiple AI assistants):
  - a1b2c3d4e5f6  add_reminder_minute
  - f4a5b6c7d8e9  add_devotional_media
  - zz9999        add_broadcast_media_and_payment

With more than one head ``alembic upgrade head`` fails ("Multiple head
revisions are present"). This is a pure merge revision: it introduces no schema
change, it only re-unifies the history so a single ``head`` exists again and new
migrations can chain onto it.

Revision ID: mrg2026092801
Revises: a1b2c3d4e5f6, f4a5b6c7d8e9, zz9999
Create Date: 2026-09-28
"""
from __future__ import annotations

# revision identifiers, used by Alembic.
revision = "mrg2026092801"
down_revision = ("a1b2c3d4e5f6", "f4a5b6c7d8e9", "zz9999")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op: merge revision only unifies history."""
    pass


def downgrade() -> None:
    """No-op: splitting back into three heads is not supported."""
    pass
