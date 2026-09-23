"""Add reminder_minute to notification_preferences

Revision ID: d39691343c63
Revises: 175a9ceb2d73
Create Date: 2026-09-23 12:27:40.300268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd39691343c63'
down_revision: Union[str, None] = '175a9ceb2d73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('notification_preferences', sa.Column('reminder_minute', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('notification_preferences', 'reminder_minute')
