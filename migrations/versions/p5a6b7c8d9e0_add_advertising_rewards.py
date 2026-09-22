"""Add per-khatm advertising opt-in and reward-rate history."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "p5a6b7c8d9e0"
down_revision = "o4c5d6e7f8a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("advertising_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column("khatms", "advertising_enabled", server_default=None)
    op.create_table(
        "advertising_reward_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_toman", sa.Integer(), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("advertising_reward_rates")
    op.drop_column("khatms", "advertising_enabled")
