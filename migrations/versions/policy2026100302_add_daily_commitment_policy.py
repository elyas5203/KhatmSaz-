"""Add the creator's fixed daily quantity policy without changing old commitments.

Existing rows retain MEMBER_CHOICE; no amounts, deadlines or progress are reset.
"""

import sqlalchemy as sa
from alembic import op

revision = "policy2026100302"
down_revision = "occ2026100301"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("khatms", sa.Column("commitment_policy", sa.String(16), nullable=False, server_default="MEMBER_CHOICE"))
    op.add_column("khatms", sa.Column("daily_commitment_amount", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_khatm_daily_commitment_policy", "khatms",
        "(commitment_policy = 'MEMBER_CHOICE' AND daily_commitment_amount IS NULL) OR "
        "(commitment_policy = 'FIXED_DAILY' AND khatm_type = 'COMMITMENT' "
        "AND daily_commitment_amount IS NOT NULL AND daily_commitment_amount > 0)",
    )


def downgrade():
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM khatms WHERE commitment_policy <> 'MEMBER_CHOICE') THEN
                RAISE EXCEPTION 'Cannot downgrade while fixed daily commitments exist';
            END IF;
        END $$;
    """)
    op.drop_constraint("ck_khatm_daily_commitment_policy", "khatms", type_="check")
    op.drop_column("khatms", "daily_commitment_amount")
    op.drop_column("khatms", "commitment_policy")
