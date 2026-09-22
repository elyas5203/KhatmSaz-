"""Add creator-controlled pause toggle."""

from alembic import op
import sqlalchemy as sa

revision = "b8c9d0e1f2"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("allow_pause", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column("khatms", "allow_pause", server_default=None)


def downgrade() -> None:
    op.drop_column("khatms", "allow_pause")
