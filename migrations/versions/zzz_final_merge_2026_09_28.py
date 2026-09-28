"""final merge: unify the two remaining alembic heads (2026-09-28)

The migration history had more parallel branches than one merge covered:
  - 506f73c6ae72  (an earlier merge of b7c8d9e0f1a2 + b8c9d0e1f2b4)
  - bii2026092803 (this session's chain: mrg2026092801 -> mcm2026092802 ->
    bii2026092803, itself merging a1b2c3d4e5f6 + f4a5b6c7d8e9 + zz9999)

Two tips still tripped `alembic upgrade head` ("Multiple head revisions"). This
pure no-op merge unifies them so a single head exists and `upgrade head` works.

Revision ID: fin2026092804
Revises: 506f73c6ae72, bii2026092803
Create Date: 2026-09-28
"""
from __future__ import annotations

revision = "fin2026092804"
down_revision = ("506f73c6ae72", "bii2026092803")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
