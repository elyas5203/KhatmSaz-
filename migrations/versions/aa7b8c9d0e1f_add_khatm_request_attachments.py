"""Store optional platform file metadata on custom khatm requests."""

from alembic import op
import sqlalchemy as sa

revision = "aa7b8c9d0e1f"
down_revision = "a7f8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatm_requests", sa.Column("attachment_file_id", sa.String(length=255), nullable=True))
    op.add_column("khatm_requests", sa.Column("attachment_file_name", sa.String(length=255), nullable=True))
    op.add_column("khatm_requests", sa.Column("attachment_mime_type", sa.String(length=120), nullable=True))
    op.add_column("khatm_requests", sa.Column("attachment_platform", sa.String(length=16), nullable=True))


def downgrade() -> None:
    op.drop_column("khatm_requests", "attachment_platform")
    op.drop_column("khatm_requests", "attachment_mime_type")
    op.drop_column("khatm_requests", "attachment_file_name")
    op.drop_column("khatm_requests", "attachment_file_id")
