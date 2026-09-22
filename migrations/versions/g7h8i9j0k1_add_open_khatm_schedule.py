"""Add configurable schedule for open-khatm prompts."""

from alembic import op
import sqlalchemy as sa

revision = "g7h8i9j0k1"
down_revision = "f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("schedule_kind", sa.String(length=16), nullable=False, server_default="NONE"))
    op.add_column("khatms", sa.Column("schedule_value", sa.String(length=120), nullable=True))
    op.create_index("ix_khatms_schedule_kind", "khatms", ["schedule_kind"])
    op.alter_column("khatms", "schedule_kind", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_khatms_schedule_kind", table_name="khatms")
    op.drop_column("khatms", "schedule_value")
    op.drop_column("khatms", "schedule_kind")
