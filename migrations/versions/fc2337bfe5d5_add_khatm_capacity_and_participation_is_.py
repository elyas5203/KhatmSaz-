"""add khatm capacity and participation is_committed

Revision ID: fc2337bfe5d5
Revises: 435027907255
Create Date: 2026-09-15 14:30:26.702332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc2337bfe5d5'
down_revision: Union[str, None] = '435027907255'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default so existing rows (all committed under the pre-hybrid
    # model) get a valid value; the ORM default is Python-side only and
    # doesn't backfill existing rows.
    op.add_column(
        'khatm_participations',
        sa.Column('is_committed', sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column('khatms', sa.Column('capacity', sa.Integer(), nullable=True))
    # NOTE: autogenerate also proposed dropping the 6 hand-written partial
    # unique indexes — a known false positive, see DATABASE.md. Stripped.


def downgrade() -> None:
    op.drop_column('khatms', 'capacity')
    op.drop_column('khatm_participations', 'is_committed')
