"""add open reservations

Revision ID: res20261003120539
Revises: policy2026100302
Create Date: 2026-10-03T12:05:39.932456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'res20261003120539'
down_revision = 'policy2026100302'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('open_reservations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('khatm_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('participation_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('reminded_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['khatm_id'], ['khatms.id'], ),
    sa.ForeignKeyConstraint(['participation_id'], ['khatm_participations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_open_reservations_khatm_id', 'open_reservations', ['khatm_id'], unique=False)
    op.create_index('ix_open_reservations_participation_id', 'open_reservations', ['participation_id'], unique=False)
    op.create_index('ix_open_reservations_status', 'open_reservations', ['status'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_open_reservations_status', table_name='open_reservations')
    op.drop_index('ix_open_reservations_participation_id', table_name='open_reservations')
    op.drop_index('ix_open_reservations_khatm_id', table_name='open_reservations')
    op.drop_table('open_reservations')
