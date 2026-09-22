"""Add per-user monthly-report deduplication period."""

from alembic import op
import sqlalchemy as sa

revision = "p6q7r8s9"
down_revision = "o5p6q7r8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_settings",
        sa.Column("last_monthly_report_period", sa.String(length=7), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_settings", "last_monthly_report_period")
