"""Add persistent manual verification requests for foreign phone numbers."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "q7r8s9t0"
down_revision = "p6q7r8s9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "manual_phone_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("e164", sa.String(length=16), nullable=False),
        sa.Column("purpose", sa.String(length=24), nullable=False, server_default="CREATOR_VERIFY"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="PENDING"),
        sa.Column("reviewed_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("admin_note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_manual_phone_verifications_user",
        "manual_phone_verifications",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_manual_phone_verifications_status",
        "manual_phone_verifications",
        ["status", "created_at"],
    )
    op.create_index(
        "ix_manual_phone_verifications_e164",
        "manual_phone_verifications",
        ["e164"],
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_manual_phone_verification_pending_user "
        "ON manual_phone_verifications (user_id) WHERE status = 'PENDING'"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_manual_phone_verification_pending_e164 "
        "ON manual_phone_verifications (e164) WHERE status = 'PENDING'"
    )


def downgrade() -> None:
    op.drop_index("uq_manual_phone_verification_pending_e164")
    op.drop_index("uq_manual_phone_verification_pending_user")
    op.drop_index("ix_manual_phone_verifications_e164", table_name="manual_phone_verifications")
    op.drop_index("ix_manual_phone_verifications_status", table_name="manual_phone_verifications")
    op.drop_index("ix_manual_phone_verifications_user", table_name="manual_phone_verifications")
    op.drop_table("manual_phone_verifications")
