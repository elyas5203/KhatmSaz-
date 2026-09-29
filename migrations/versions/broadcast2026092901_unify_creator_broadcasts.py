"""Unify creator broadcasts behind the moderated multi-channel queue.

Revision ID: broadcast2026092901
Revises: rot2026092805
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa

revision = "broadcast2026092901"
down_revision = "rot2026092805"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("khatm_broadcasts", "khatm_id", existing_type=sa.UUID(), nullable=True)
    op.add_column("khatm_broadcasts", sa.Column("target_scope", sa.String(16), nullable=False, server_default="KHATM"))
    op.add_column("khatm_broadcasts", sa.Column("channel", sa.String(16), nullable=False, server_default="TELEGRAM"))
    op.add_column("khatm_broadcasts", sa.Column("audience_count", sa.Integer(), nullable=False, server_default="0"))
    op.create_check_constraint("ck_broadcast_target_scope", "khatm_broadcasts", "target_scope IN ('KHATM','ALL')")
    op.create_check_constraint(
        "ck_broadcast_target_khatm",
        "khatm_broadcasts",
        "(target_scope = 'ALL' AND khatm_id IS NULL) OR (target_scope = 'KHATM' AND khatm_id IS NOT NULL)",
    )
    op.create_check_constraint("ck_broadcast_channel", "khatm_broadcasts", "channel IN ('TELEGRAM','BALE','SMS')")
    op.create_index("ix_khatm_broadcasts_creator_channel_created", "khatm_broadcasts", ["creator_user_id", "channel", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_khatm_broadcasts_creator_channel_created", table_name="khatm_broadcasts")
    op.drop_constraint("ck_broadcast_channel", "khatm_broadcasts", type_="check")
    op.drop_constraint("ck_broadcast_target_scope", "khatm_broadcasts", type_="check")
    op.drop_constraint("ck_broadcast_target_khatm", "khatm_broadcasts", type_="check")
    op.drop_column("khatm_broadcasts", "audience_count")
    op.drop_column("khatm_broadcasts", "channel")
    op.drop_column("khatm_broadcasts", "target_scope")
    op.execute("DELETE FROM khatm_broadcasts WHERE khatm_id IS NULL")
    op.alter_column("khatm_broadcasts", "khatm_id", existing_type=sa.UUID(), nullable=False)
