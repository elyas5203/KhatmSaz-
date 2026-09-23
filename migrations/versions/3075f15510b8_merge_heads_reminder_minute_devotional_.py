"""merge heads: reminder_minute + devotional_media

Revision ID: 3075f15510b8
Revises: a1b2c3d4e5f6, f4a5b6c7d8e9
Create Date: 2026-09-23 09:49:30.569896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3075f15510b8'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'f4a5b6c7d8e9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
