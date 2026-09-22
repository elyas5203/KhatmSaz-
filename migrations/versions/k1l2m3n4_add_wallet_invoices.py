"""Add internal invoices for top-ups and purchases."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "k1l2m3n4"
down_revision = "j0k1l2m3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wallet_invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("gross_amount_toman", sa.Integer(), nullable=False),
        sa.Column("discount_amount_toman", sa.Integer(), nullable=False),
        sa.Column("net_amount_toman", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("external_ref", sa.String(length=255), nullable=True),
        sa.Column("resource_ref", sa.String(length=255), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_ref"),
    )
    op.create_index(
        "ix_wallet_invoices_user_issued", "wallet_invoices", ["user_id", "issued_at"]
    )
    op.create_index(
        "ix_wallet_invoices_kind_resource", "wallet_invoices", ["kind", "resource_ref"]
    )


def downgrade() -> None:
    op.drop_index("ix_wallet_invoices_kind_resource", table_name="wallet_invoices")
    op.drop_index("ix_wallet_invoices_user_issued", table_name="wallet_invoices")
    op.drop_table("wallet_invoices")
