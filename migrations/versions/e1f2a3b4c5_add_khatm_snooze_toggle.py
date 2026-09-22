"""Add creator-controlled snooze toggle."""

from alembic import op
import sqlalchemy as sa

revision = "e1f2a3b4c5"
down_revision = "d0e1f2a3b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("allow_snooze", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column("khatms", "allow_snooze", server_default=None)


def downgrade() -> None:
    op.drop_column("khatms", "allow_snooze")
