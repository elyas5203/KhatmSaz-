"""Create admin_alert_messages table for cross-admin alert synchronization.

Tracks alert messages sent to admins so when one handles a ticket or verification,
the other admins' messages are edited and their action buttons removed.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "admin2026101801"
down_revision = "share2026100501"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_alert_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("alert_type", sa.String(32), nullable=False),
        sa.Column("reference_id", sa.String(64), nullable=False),
        sa.Column("chat_id", sa.String(32), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("original_text", sa.String(4000), nullable=True),
        sa.Column("handled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("handled_by_name", sa.String(64), nullable=True),
        sa.Column("action_taken", sa.String(64), nullable=True),
        sa.Column("handled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_admin_alert_messages_type_ref", "admin_alert_messages", ["alert_type", "reference_id"])
    op.create_index("ix_admin_alert_messages_chat_msg", "admin_alert_messages", ["chat_id", "message_id"])


def downgrade():
    op.drop_index("ix_admin_alert_messages_chat_msg", table_name="admin_alert_messages")
    op.drop_index("ix_admin_alert_messages_type_ref", table_name="admin_alert_messages")
    op.drop_table("admin_alert_messages")
