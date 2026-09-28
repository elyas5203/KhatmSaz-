"""DEC-PY-0092: personal-sequential rotating Quran allocation.

Existing plans retain SHARED_POOL. New Quran plans explicitly use ROTATING,
store their page/audio boundaries, and create portions per participation.

Revision ID: rot2026092805
Revises: fin2026092804
Create Date: 2026-09-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "rot2026092805"
down_revision = "fin2026092804"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatm_allocation_plans",
        sa.Column("allocation_strategy", sa.String(length=16), nullable=False, server_default="SHARED_POOL"),
    )
    op.add_column(
        "khatm_allocation_plans",
        sa.Column("positional_boundaries", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "khatm_participations",
        sa.Column("quran_rotation_offset", sa.Integer(), nullable=True),
    )

    op.drop_constraint("uq_khatm_portions_plan_sequence", "khatm_portions", type_="unique")
    op.execute("DROP INDEX IF EXISTS uq_portion_positional_plan_unit_start")
    op.execute(
        "CREATE UNIQUE INDEX uq_portion_shared_plan_sequence "
        "ON khatm_portions (plan_id, sequence) WHERE participation_id IS NULL"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_portion_participant_sequence "
        "ON khatm_portions (plan_id, participation_id, sequence) WHERE participation_id IS NOT NULL"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_portion_shared_positional_start "
        "ON khatm_portions (plan_id, unit_start) "
        "WHERE unit_kind = 'POSITIONAL' AND participation_id IS NULL"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_active_quran_rotation_offset "
        "ON khatm_participations (khatm_id, quran_rotation_offset) "
        "WHERE quran_rotation_offset IS NOT NULL AND status = 'ACTIVE'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_active_quran_rotation_offset")
    op.execute("DROP INDEX IF EXISTS uq_portion_shared_positional_start")
    op.execute("DROP INDEX IF EXISTS uq_portion_participant_sequence")
    op.execute("DROP INDEX IF EXISTS uq_portion_shared_plan_sequence")
    op.create_unique_constraint(
        "uq_khatm_portions_plan_sequence", "khatm_portions", ["plan_id", "sequence"]
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_portion_positional_plan_unit_start "
        "ON khatm_portions (plan_id, unit_start) WHERE unit_kind = 'POSITIONAL'"
    )
    op.drop_column("khatm_participations", "quran_rotation_offset")
    op.drop_column("khatm_allocation_plans", "positional_boundaries")
    op.drop_column("khatm_allocation_plans", "allocation_strategy")
