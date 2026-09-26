"""Merge multiple heads

Revision ID: 506f73c6ae72
Revises: b7c8d9e0f1a2, b8c9d0e1f2b4
Create Date: 2026-09-26 14:41:17.052755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '506f73c6ae72'
down_revision: Union[str, None] = ('b7c8d9e0f1a2', 'b8c9d0e1f2b4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
