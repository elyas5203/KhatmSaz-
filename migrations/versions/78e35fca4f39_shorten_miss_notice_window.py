"""Shorten default miss_notice_window_days from 7 to 3 (consecutive-day detection).

Owner decision (2026-09-22): notify creator after 2 *consecutive* missed days,
not 2 misses spread over a week. A 3-day window with threshold=2 is equivalent
to "missed 2 of the last 3 days" which captures consecutive misses without
false-positives. All existing khatms are updated to the new default.
"""

from alembic import op

revision = "78e35fca4f39"
down_revision = "c8e057163033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE khatms ALTER COLUMN miss_notice_window_days SET DEFAULT 3"
    )
    op.execute(
        "UPDATE khatms SET miss_notice_window_days = 3 WHERE miss_notice_window_days = 7"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE khatms ALTER COLUMN miss_notice_window_days SET DEFAULT 7"
    )
    op.execute(
        "UPDATE khatms SET miss_notice_window_days = 3 WHERE miss_notice_window_days = 3"
    )
