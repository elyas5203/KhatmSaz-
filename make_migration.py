import os
from datetime import datetime, timezone

ts = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
filename = f'migrations/versions/res{ts}_add_commitment_deliveries.py'
content = f'''"""add commitment deliveries for 2-hour reminder

Revision ID: res{ts}
Revises: 175a9ceb2d73
Create Date: {datetime.now(timezone.utc).isoformat()}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'res{ts}'
down_revision: Union[str, None] = '175a9ceb2d73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'commitment_deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('participation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('chat_id', sa.String(length=64), nullable=True),
        sa.Column('message_id', sa.String(length=64), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reminder_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['participation_id'], ['khatm_participations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_commitment_deliveries_participation', 'commitment_deliveries', ['participation_id'], unique=False)
    op.create_index('ix_commitment_deliveries_pending', 'commitment_deliveries', ['is_completed', 'delivered_at'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_commitment_deliveries_pending', table_name='commitment_deliveries')
    op.drop_index('ix_commitment_deliveries_participation', table_name='commitment_deliveries')
    op.drop_table('commitment_deliveries')
'''
with open(filename, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Created {filename}")
