"""partial unique indexes

Revision ID: 3b206b888ca5
Revises: 585f0d556cb8
Create Date: 2026-09-15 11:44:03.952923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b206b888ca5'
down_revision: Union[str, None] = '585f0d556cb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # At most one ACTIVE participation per (khatm, user) — a user who LEFT may
    # rejoin as a new row, but never two ACTIVE rows at once.
    op.execute(
        "CREATE UNIQUE INDEX uq_participation_active_khatm_user "
        "ON khatm_participations (khatm_id, user_id) WHERE status = 'ACTIVE'"
    )

    # At most one ACTIVE capability grant per (user, type) — a revoke+re-grant
    # is a new row, never an update of the old one.
    op.execute(
        "CREATE UNIQUE INDEX uq_capability_active_user_type "
        "ON user_capabilities (user_id, type) WHERE revoked_at IS NULL"
    )

    # Non-overlap of positional allocation portions within a plan — engine
    # portions are atomic single units (unit_start = unit_end).
    op.execute(
        "CREATE UNIQUE INDEX uq_portion_positional_plan_unit_start "
        "ON khatm_portions (plan_id, unit_start) WHERE unit_kind = 'POSITIONAL'"
    )

    # Phone claim invariants (three, all partial — plain uniques can't express them):
    #  1. at most one VERIFIED claim per canonical number, globally;
    #  2. at most one active (non-revoked) claim per (user, number);
    #  3. at most one VERIFIED claim per user, across all numbers.
    op.execute(
        "CREATE UNIQUE INDEX uq_phone_claim_verified_e164 "
        "ON phone_claims (e164) WHERE status = 'VERIFIED'"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_phone_claim_active_user_e164 "
        "ON phone_claims (user_id, e164) WHERE status != 'REVOKED'"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_phone_claim_verified_user "
        "ON phone_claims (user_id) WHERE status = 'VERIFIED'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_phone_claim_verified_user")
    op.execute("DROP INDEX IF EXISTS uq_phone_claim_active_user_e164")
    op.execute("DROP INDEX IF EXISTS uq_phone_claim_verified_e164")
    op.execute("DROP INDEX IF EXISTS uq_portion_positional_plan_unit_start")
    op.execute("DROP INDEX IF EXISTS uq_capability_active_user_type")
    op.execute("DROP INDEX IF EXISTS uq_participation_active_khatm_user")
