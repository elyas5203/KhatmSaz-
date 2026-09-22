"""Add admin-managed plan pricing and feature entitlements."""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "o4c5d6e7f8a9"
down_revision = "n3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plan_definitions",
        sa.Column("plan", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=80), nullable=False),
        sa.Column("pricing_mode", sa.String(length=20), nullable=False),
        sa.Column("price_toman", sa.Integer(), nullable=False),
        sa.Column("unit_price_toman", sa.Integer(), nullable=False),
        sa.Column("entitlements", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("plan"),
    )
    table = sa.table(
        "plan_definitions", sa.column("plan", sa.String()), sa.column("title", sa.String()),
        sa.column("pricing_mode", sa.String()), sa.column("price_toman", sa.Integer()),
        sa.column("unit_price_toman", sa.Integer()), sa.column("entitlements", postgresql.JSON()),
        sa.column("enabled", sa.Boolean()),
    )
    op.bulk_insert(table, [
        {"plan": "FREE", "title": "رایگان", "pricing_mode": "FIXED", "price_toman": 0,
         "unit_price_toman": 0, "entitlements": {"khatm.create": True, "report.view": True}, "enabled": True},
        {"plan": "BASIC", "title": "پایه", "pricing_mode": "FIXED", "price_toman": 0,
         "unit_price_toman": 0, "entitlements": {"khatm.create": True, "report.view": True}, "enabled": True},
        {"plan": "PRO", "title": "حرفه‌ای", "pricing_mode": "FIXED", "price_toman": 0,
         "unit_price_toman": 0, "entitlements": {"khatm.create": True, "report.view": True}, "enabled": True},
    ])


def downgrade() -> None:
    op.drop_table("plan_definitions")
