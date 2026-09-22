"""Track creator resolution of repeated missed commitments.

Revision ID: j0e1f2a3b4c5
Revises: i9d0e1f2a3b4
"""

from alembic import op
import sqlalchemy as sa

revision = "j0e1f2a3b4c5"
down_revision = "i9d0e1f2a3b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatm_participations",
        sa.Column("creator_resolution", sa.String(length=32), nullable=False, server_default="PENDING"),
    )
    op.alter_column("khatm_participations", "creator_resolution", server_default=None)


def downgrade() -> None:
    op.drop_column("khatm_participations", "creator_resolution")
