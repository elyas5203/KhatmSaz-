import sqlalchemy as sa
from alembic import op

revision = 'zz9999'
down_revision = 'e4f5a6b7c8d9'

def upgrade() -> None:
    op.add_column('khatm_broadcasts', sa.Column('media_type', sa.String(32), nullable=True))
    op.add_column('khatm_broadcasts', sa.Column('media_file_id_telegram', sa.String(255), nullable=True))
    op.add_column('khatm_broadcasts', sa.Column('media_file_id_bale', sa.String(255), nullable=True))
    op.add_column('khatm_broadcasts', sa.Column('cost_toman', sa.Integer(), server_default='0', nullable=False))
    op.add_column('khatm_broadcasts', sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('khatm_broadcasts', sa.Column('invoice_id', sa.UUID(), nullable=True))

def downgrade() -> None:
    op.drop_column('khatm_broadcasts', 'invoice_id')
    op.drop_column('khatm_broadcasts', 'paid_at')
    op.drop_column('khatm_broadcasts', 'cost_toman')
    op.drop_column('khatm_broadcasts', 'media_file_id_bale')
    op.drop_column('khatm_broadcasts', 'media_file_id_telegram')
    op.drop_column('khatm_broadcasts', 'media_type')

