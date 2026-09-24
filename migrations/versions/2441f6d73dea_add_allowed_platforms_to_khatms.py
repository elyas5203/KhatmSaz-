"""add allowed_platforms to khatms

Revision ID: 2441f6d73dea
Revises: zz9999
Create Date: 2026-09-24 13:48:28.658979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2441f6d73dea'
down_revision: Union[str, None] = 'zz9999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "khatms",
        sa.Column("allowed_platforms", sa.String(length=16), server_default="BOTH", nullable=False)
    )

def downgrade() -> None:
    op.drop_column("khatms", "allowed_platforms")
