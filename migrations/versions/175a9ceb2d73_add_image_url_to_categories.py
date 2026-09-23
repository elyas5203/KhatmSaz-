"""add_image_url_to_categories

Revision ID: 175a9ceb2d73
Revises: 3075f15510b8
Create Date: 2026-09-23 10:39:19.863857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '175a9ceb2d73'
down_revision: Union[str, None] = '3075f15510b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("khatm_categories", sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("khatm_categories", "image_url")
