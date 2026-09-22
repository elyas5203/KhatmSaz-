"""Add moderated creator-to-member messages."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "z6e7f8a9b0c1"
down_revision = "y5d6e7f8a9b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    status_enum = postgresql.ENUM(
        "PENDING", "APPROVED", "REJECTED", "SENT", name="broadcaststatus", create_type=False
    )
    status_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "khatm_broadcasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("khatm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("admin_note", sa.String(length=500), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["khatm_id"], ["khatms.id"]),
        sa.ForeignKeyConstraint(["creator_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_khatm_broadcasts_status_created", "khatm_broadcasts", ["status", "created_at"])
    op.create_index("ix_khatm_broadcasts_khatm_created", "khatm_broadcasts", ["khatm_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_khatm_broadcasts_khatm_created", table_name="khatm_broadcasts")
    op.drop_index("ix_khatm_broadcasts_status_created", table_name="khatm_broadcasts")
    op.drop_table("khatm_broadcasts")
    op.execute("DROP TYPE IF EXISTS broadcaststatus")
