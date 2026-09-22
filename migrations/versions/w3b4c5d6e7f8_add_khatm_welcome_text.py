"""Add optional creator-authored welcome text."""

from alembic import op
import sqlalchemy as sa

revision = "w3b4c5d6e7f8"
down_revision = "v2a3b4c5d6e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatms", sa.Column("welcome_text", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("khatms", "welcome_text")
