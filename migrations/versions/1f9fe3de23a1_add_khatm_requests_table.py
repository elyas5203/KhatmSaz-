"""add khatm_requests table

Revision ID: 1f9fe3de23a1
Revises: fc2337bfe5d5
Create Date: 2026-09-15 15:28:07.967063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f9fe3de23a1'
down_revision: Union[str, None] = 'fc2337bfe5d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: autogenerate also proposed dropping the 6 hand-written partial
    # unique indexes — a known false positive, see DATABASE.md. Stripped.
    op.create_table(
        'khatm_requests',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('requester_user_id', sa.UUID(), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='khatmrequeststatus'), nullable=False),
        sa.Column('admin_note', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['requester_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_khatm_requests_requester', 'khatm_requests', ['requester_user_id'], unique=False)
    op.create_index('ix_khatm_requests_status', 'khatm_requests', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_khatm_requests_status', table_name='khatm_requests')
    op.drop_index('ix_khatm_requests_requester', table_name='khatm_requests')
    op.drop_table('khatm_requests')
    op.execute('DROP TYPE IF EXISTS khatmrequeststatus')
