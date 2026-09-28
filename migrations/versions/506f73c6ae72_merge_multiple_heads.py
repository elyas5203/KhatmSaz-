"""Merge multiple heads

Revision ID: 506f73c6ae72
Revises: b8c9d0e1f2b4
Create Date: 2026-09-26 14:41:17.052755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '506f73c6ae72'
# The original file merged b7 and b8 as sibling revisions.  That graph was
# invalid for a fresh install because b8 creates a foreign key to the table
# introduced by b7.  The history is now ordered b7 -> b8, while this no-op
# revision remains in place so already-upgraded databases keep the same
# revision identity.
down_revision: Union[str, None] = 'b8c9d0e1f2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
