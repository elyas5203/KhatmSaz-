"""add khatm visibility

Revision ID: cf308fcab881
Revises: c21644dab334
Create Date: 2026-09-16 12:01:16.233702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf308fcab881'
down_revision: Union[str, None] = 'c21644dab334'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: autogenerate also proposed dropping the 6 hand-written partial
    # unique indexes — a known false positive, see DATABASE.md. Stripped.
    # server_default so existing rows (from earlier testing) get a value.
    op.execute("CREATE TYPE khatmvisibility AS ENUM ('PUBLIC', 'UNLISTED', 'PRIVATE')")
    op.add_column(
        'khatms',
        sa.Column(
            'visibility',
            sa.Enum('PUBLIC', 'UNLISTED', 'PRIVATE', name='khatmvisibility', create_type=False),
            nullable=False,
            server_default='UNLISTED',
        ),
    )


def downgrade() -> None:
    op.drop_column('khatms', 'visibility')
    op.execute('DROP TYPE IF EXISTS khatmvisibility')
