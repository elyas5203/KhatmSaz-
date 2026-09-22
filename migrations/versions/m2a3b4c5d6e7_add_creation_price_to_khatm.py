"""Persist the price charged when a khatm is created."""

from alembic import op
import sqlalchemy as sa

revision = "m2a3b4c5d6e7"
down_revision = "l1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatms",
        sa.Column("creation_price_toman", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("khatms", "creation_price_toman", server_default=None)


def downgrade() -> None:
    op.drop_column("khatms", "creation_price_toman")
