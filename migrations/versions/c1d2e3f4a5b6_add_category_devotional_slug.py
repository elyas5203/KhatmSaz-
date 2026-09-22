"""Add explicit devotional_slug link to khatm_categories (BACKLOG.md §14).

Replaces the fragile name-matching hack in bot/handlers/portions.py that
guessed which devotional_assets row belonged to a category by checking if
"عاشورا" appeared in the category title — broke if a creator renamed the
category. This is a plain nullable string column, no data backfill needed
(existing categories simply have devotional_slug=NULL until an admin sets
one via the web panel).
"""

from alembic import op
import sqlalchemy as sa

revision = "c1d2e3f4a5b6"
down_revision = "r9s0t1u2v3w4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "khatm_categories",
        sa.Column("devotional_slug", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("khatm_categories", "devotional_slug")
