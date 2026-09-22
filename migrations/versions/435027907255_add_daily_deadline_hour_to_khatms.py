"""add daily_deadline_hour to khatms

Revision ID: 435027907255
Revises: 3b206b888ca5
Create Date: 2026-09-15 13:53:00.584367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '435027907255'
down_revision: Union[str, None] = '3b206b888ca5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: autogenerate also proposed dropping the 6 hand-written partial
    # unique indexes from the previous migration — that's a known false
    # positive (SQLAlchemy's model layer can't express partial indexes, so
    # autogenerate always "sees" them as extra and wants to remove them).
    # Stripped out here; see DATABASE.md "Invariants SQLAlchemy can't
    # express declaratively". Only the real change (the new column) stays.
    op.add_column('khatms', sa.Column('daily_deadline_hour', sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('khatms', 'daily_deadline_hour')
