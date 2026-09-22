"""Add time-limited SMS reminder subscriptions and admin-editable plan options."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b8c9d0e1f2a3"
down_revision = "ab8c9d0e1f2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sms_plan_options",
        sa.Column("months", sa.Integer(), nullable=False),
        sa.Column("price_toman", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("months"),
    )
    op.create_table(
        "sms_subscriptions",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expiry_notified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_sms_subscriptions_expires_at", "sms_subscriptions", ["expires_at"])
    # Seed the owner's two example plans (admin-editable afterwards, not fixed).
    op.execute(
        "INSERT INTO sms_plan_options (months, price_toman, enabled) VALUES "
        "(3, 50000, true), (6, 87000, true)"
    )


def downgrade() -> None:
    op.drop_index("ix_sms_subscriptions_expires_at", table_name="sms_subscriptions")
    op.drop_table("sms_subscriptions")
    op.drop_table("sms_plan_options")
