"""Add revocable delegated admin role assignments."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "m3n4o5p6"
down_revision = "l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_role_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("granted_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["granted_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role", name="uq_admin_role_grants_user_role"),
    )
    op.create_index("ix_admin_role_grants_user_id", "admin_role_grants", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_admin_role_grants_user_id", table_name="admin_role_grants")
    op.drop_table("admin_role_grants")
