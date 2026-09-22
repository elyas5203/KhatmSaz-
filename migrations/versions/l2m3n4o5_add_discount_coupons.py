"""Add admin-managed coupons and immutable redemption records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "l2m3n4o5"
down_revision = "k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "discount_coupons",
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("discount_type", sa.String(length=16), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("min_purchase_toman", sa.Integer(), nullable=False),
        sa.Column("max_discount_toman", sa.Integer(), nullable=True),
        sa.Column("total_redemption_limit", sa.Integer(), nullable=True),
        sa.Column("per_user_limit", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_table(
        "coupon_redemptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("coupon_code", sa.String(length=40), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("discount_amount_toman", sa.Integer(), nullable=False),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["coupon_code"], ["discount_coupons.code"]),
        sa.ForeignKeyConstraint(["invoice_id"], ["wallet_invoices.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_id"),
    )
    op.create_index("ix_coupon_redemptions_coupon", "coupon_redemptions", ["coupon_code"])
    op.create_index(
        "ix_coupon_redemptions_user_coupon", "coupon_redemptions", ["user_id", "coupon_code"]
    )


def downgrade() -> None:
    op.drop_index("ix_coupon_redemptions_user_coupon", table_name="coupon_redemptions")
    op.drop_index("ix_coupon_redemptions_coupon", table_name="coupon_redemptions")
    op.drop_table("coupon_redemptions")
    op.drop_table("discount_coupons")
