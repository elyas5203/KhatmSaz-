"""Add image_ref/image_platform to devotional_assets.

Owner request (2026-09-22): support attaching an image (e.g. a photo of
the Ziyarat Ashura text) to a devotional asset, mirroring the existing
audio_ref/audio_platform columns.
"""

from alembic import op
import sqlalchemy as sa

revision = "e3f4a5b6c7d8"
down_revision = "78e35fca4f39"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("devotional_assets", sa.Column("image_ref", sa.String(length=500), nullable=True))
    op.add_column("devotional_assets", sa.Column("image_platform", sa.String(length=16), nullable=True))


def downgrade() -> None:
    op.drop_column("devotional_assets", "image_platform")
    op.drop_column("devotional_assets", "image_ref")
