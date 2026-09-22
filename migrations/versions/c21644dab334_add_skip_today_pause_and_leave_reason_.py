"""add skip-today, pause, and leave-reason fields

Revision ID: c21644dab334
Revises: 687e213ff34b
Create Date: 2026-09-15 16:17:54.600741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c21644dab334'
down_revision: Union[str, None] = '687e213ff34b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: autogenerate also proposed dropping the 6 hand-written partial
    # unique indexes — a known false positive, see DATABASE.md. Stripped.
    op.add_column('khatm_participations', sa.Column('paused_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('khatm_participations', sa.Column('leave_reason', sa.String(length=50), nullable=True))
    # server_default so existing rows (from earlier testing) get a value —
    # autogenerate omitted this, which would fail NOT NULL on a non-empty table.
    op.add_column(
        'khatms',
        sa.Column('allow_skip_today', sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column('khatms', 'allow_skip_today')
    op.drop_column('khatm_participations', 'leave_reason')
    op.drop_column('khatm_participations', 'paused_until')
