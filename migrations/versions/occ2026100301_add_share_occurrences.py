"""Add persistent share identities and message receipts (redesign P3a).

Additive only: no backfill, no changes to existing memberships or schedules.
Runtime cutover is a later phase. Downgrade refuses to erase recorded shares.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision = "occ2026100301"
down_revision = "devsalawat2026100102"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "share_occurrences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("participation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("khatm_participations.id"), nullable=False),
        sa.Column("bot_instance_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bot_instances.id"), nullable=False),
        sa.Column("source_key", sa.String(80), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("unit", sa.String(16), nullable=False),
        sa.Column("content_spec", postgresql.JSONB(), nullable=False),
        sa.Column("committed", sa.Boolean(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("participation_id", "source_key", name="uq_share_occurrence_source"),
        sa.CheckConstraint("amount > 0", name="ck_share_occurrence_amount"),
        sa.CheckConstraint("unit IN ('PAGE', 'COUNT', 'REPETITION')", name="ck_share_occurrence_unit"),
        sa.CheckConstraint("completed_at IS NULL OR delivered_at IS NOT NULL", name="ck_share_occurrence_completed_delivery"),
    )
    op.create_index("ix_share_occurrence_due", "share_occurrences", ["scheduled_for"], postgresql_where=sa.text("delivered_at IS NULL"))
    op.create_index("ix_share_occurrence_outstanding", "share_occurrences", ["participation_id", "scheduled_for"], postgresql_where=sa.text("completed_at IS NULL"))
    op.create_table(
        "share_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("occurrence_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("share_occurrences.id"), nullable=False),
        sa.Column("component_key", sa.String(80), nullable=False),
        sa.Column("purpose", sa.String(16), nullable=False),
        sa.Column("chat_id", sa.String(32), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("occurrence_id", "component_key", name="uq_share_message_component"),
        sa.CheckConstraint("purpose IN ('CONTENT', 'ACTION', 'FOLLOWUP', 'DEADLINE')", name="ck_share_message_purpose"),
        sa.CheckConstraint("message_id > 0", name="ck_share_message_id"),
        sa.CheckConstraint("purpose <> 'CONTENT' OR deleted_at IS NULL", name="ck_share_message_preserve_content"),
    )


def downgrade():
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM share_occurrences) OR EXISTS (SELECT 1 FROM share_messages) THEN
                RAISE EXCEPTION 'Cannot downgrade while recorded shares exist; preserve their history first';
            END IF;
        END $$;
    """)
    op.drop_table("share_messages")
    op.drop_index("ix_share_occurrence_outstanding", table_name="share_occurrences")
    op.drop_index("ix_share_occurrence_due", table_name="share_occurrences")
    op.drop_table("share_occurrences")
