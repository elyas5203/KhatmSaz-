"""Final migration-history marker (2026-09-28).

The earlier merge graph listed ``zz9999`` separately from a descendant branch
that creates ``bot_instances``.  On a fresh database Alembic could therefore
mark the common ancestor complete and skip the descendant before R2 tried to
alter ``bot_instances``.  The graph is now ordered through 506f73c6ae72 before
the R11/R2 chain; this no-op revision remains as the stable final revision ID.

Revision ID: fin2026092804
Revises: bii2026092803
Create Date: 2026-09-28
"""
from __future__ import annotations

revision = "fin2026092804"
down_revision = "bii2026092803"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
