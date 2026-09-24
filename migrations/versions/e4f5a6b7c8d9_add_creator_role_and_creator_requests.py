"""add creator role and creator_requests table

Revision ID: e4f5a6b7c8d9
Revises: 175a9ceb2d73
Create Date: 2026-09-24

Owner request (2026-09-24, Antigravity): separate participant and creator
menus. Users start as USER; to gain access to khatm creation they must
request the CREATOR role and be approved by an admin.

Two changes in this migration:
1. Add 'CREATOR' to the PostgreSQL userrole enum.
2. Create the creator_requests table.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e4f5a6b7c8d9"
down_revision = "175a9ceb2d73"
branch_labels = None
depends_on = None

# Disable transaction to allow adding enum value and using it in the same run (PostgreSQL limitation)
disable_ddl_transaction = True

def upgrade() -> None:
    # 1. Add CREATOR to the userrole enum.
    # PostgreSQL enums must be altered with raw SQL; Alembic can't express
    # ADD VALUE natively.
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'CREATOR'")

    # 2. Create the creator_requests table.
    op.create_table(
        "creator_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("admin_note", sa.String, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "reviewed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_creator_requests_user_id", "creator_requests", ["user_id"],
    )
    op.create_index(
        "ix_creator_requests_status", "creator_requests", ["status"],
    )

    # 3. Auto-upgrade existing khatm creators to CREATOR role.
    # Any user who already has at least one khatm as creator_user_id
    # should be upgraded to CREATOR (unless they're already SUPER_ADMIN).
    op.execute("""
        UPDATE users
        SET role = 'CREATOR'
        WHERE id IN (
            SELECT DISTINCT creator_user_id FROM khatms
        )
        AND role = 'USER'
    """)


def downgrade() -> None:
    # Revert existing CREATOR users back to USER.
    op.execute("UPDATE users SET role = 'USER' WHERE role = 'CREATOR'")

    op.drop_index("ix_creator_requests_status", table_name="creator_requests")
    op.drop_index("ix_creator_requests_user_id", table_name="creator_requests")
    op.drop_table("creator_requests")

    # PostgreSQL doesn't support DROP VALUE from an enum directly.
    # Leaving the enum value in place is harmless; a full removal would
    # require recreating the enum type which is fragile in a downgrade.
