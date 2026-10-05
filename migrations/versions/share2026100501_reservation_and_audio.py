"""Link numeric shares to reservations and add per-membership audio overrides.

Additive: historical shares/reservations and account preferences are untouched.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "share2026100501"
down_revision = "a6289f6b73c2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("share_occurrences", sa.Column("reservation_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_share_reservation", "share_occurrences", "open_reservations", ["reservation_id"], ["id"])
    op.create_unique_constraint("uq_share_reservation", "share_occurrences", ["reservation_id"])
    op.add_column("khatm_participations", sa.Column("quran_audio_enabled", sa.Boolean(), nullable=True))


def downgrade():
    op.execute("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM share_occurrences WHERE reservation_id IS NOT NULL)
           OR EXISTS (SELECT 1 FROM khatm_participations WHERE quran_audio_enabled IS NOT NULL) THEN
            RAISE EXCEPTION 'Preserve numeric share links and audio settings before downgrade';
        END IF;
    END $$;""")
    op.drop_column("khatm_participations", "quran_audio_enabled")
    op.drop_constraint("uq_share_reservation", "share_occurrences", type_="unique")
    op.drop_constraint("fk_share_reservation", "share_occurrences", type_="foreignkey")
    op.drop_column("share_occurrences", "reservation_id")
