"""Add creator-controlled, delayed completion announcements."""

from alembic import op
import sqlalchemy as sa

revision = "n4o5p6q7"
down_revision = "m3n4o5p6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatms",
        sa.Column(
            "completion_announcement_enabled",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
    )
    op.add_column("khatms", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "khatms", sa.Column("completion_announced_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index(
        "ix_khatms_completion_announcement",
        "khatms",
        ["status", "completion_announcement_enabled", "completion_announced_at", "completed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_khatms_completion_announcement", table_name="khatms")
    op.drop_column("khatms", "completion_announced_at")
    op.drop_column("khatms", "completed_at")
    op.drop_column("khatms", "completion_announcement_enabled")
