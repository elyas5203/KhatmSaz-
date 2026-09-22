"""add contact_phone to user_settings

Revision ID: 687e213ff34b
Revises: 1f9fe3de23a1
Create Date: 2026-09-15 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '687e213ff34b'
down_revision: Union[str, None] = '1f9fe3de23a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: autogenerate also proposed dropping the 6 hand-written partial
    # unique indexes — a known false positive, see DATABASE.md. Stripped.
    op.add_column('user_settings', sa.Column('contact_phone', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('user_settings', 'contact_phone')
