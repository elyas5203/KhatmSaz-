"""merge multiple heads

Revision ID: a6289f6b73c2
Revises: res20261003120539, res20261003123135
Create Date: 2026-10-04 15:15:16.987493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6289f6b73c2'
down_revision: Union[str, None] = ('res20261003120539', 'res20261003123135')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
