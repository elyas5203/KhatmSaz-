"""Add committed_quantity_logs table for today-vs-yesterday on salawat/dua/laan."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c8e057163033"
down_revision = "d2e3f4a5b6c7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "committed_quantity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("khatm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("khatms.id"), nullable=False),
        sa.Column("participation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("khatm_participations.id"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "ix_committed_qty_log_khatm_logged",
        "committed_quantity_logs",
        ["khatm_id", "logged_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_committed_qty_log_khatm_logged", table_name="committed_quantity_logs")
    op.drop_table("committed_quantity_logs")
