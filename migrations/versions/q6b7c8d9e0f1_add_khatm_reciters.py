"""Add per-khatm reciter whitelists."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "q6b7c8d9e0f1"
down_revision = "p5a6b7c8d9e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "khatm_reciters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("khatm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reciter_id", sa.String(length=64), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["khatm_id"], ["khatms.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("khatm_id", "reciter_id", name="uq_khatm_reciters_khatm_reciter"),
    )
    op.create_index("ix_khatm_reciters_khatm_priority", "khatm_reciters", ["khatm_id", "priority"])


def downgrade() -> None:
    op.drop_index("ix_khatm_reciters_khatm_priority", table_name="khatm_reciters")
    op.drop_table("khatm_reciters")
