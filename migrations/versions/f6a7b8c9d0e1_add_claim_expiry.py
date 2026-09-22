"""Add expiry for emergency-pool reservations.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
"""

from alembic import op
import sqlalchemy as sa

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("khatm_portions", sa.Column("claim_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(
        "ix_khatm_portions_claim_expires_at",
        "khatm_portions",
        ["claim_expires_at"],
        postgresql_where=sa.text("claim_expires_at IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_khatm_portions_claim_expires_at", table_name="khatm_portions")
    op.drop_column("khatm_portions", "claim_expires_at")
