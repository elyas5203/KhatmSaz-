"""Add joined_via_bot_instance_id to participations

Revision ID: b8c9d0e1f2b4
Revises: zz9999
Create Date: 2026-09-26 13:52:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2b4'
down_revision: Union[str, None] = 'zz9999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('khatm_participations', sa.Column('joined_via_bot_instance_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'khatm_participations', 'bot_instances', ['joined_via_bot_instance_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(None, 'khatm_participations', type_='foreignkey')
    op.drop_column('khatm_participations', 'joined_via_bot_instance_id')
