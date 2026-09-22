"""Seed the owner-defined children of the top-level La'an family."""

from alembic import op


revision = "ab8c9d0e1f2a"
down_revision = "aa7b8c9d0e1f"
branch_labels = None
depends_on = None


_ROWS = (
    ("e1010000-0000-4000-8000-000000000001", "لعن عمر", 10),
    ("e1010000-0000-4000-8000-000000000002", "لعن ابوبکر", 20),
    ("e1010000-0000-4000-8000-000000000003", "لعن عایشه", 30),
    ("e1010000-0000-4000-8000-000000000004", "لعن هشت‌گانه امام رضا علیه‌السلام", 40),
)


def upgrade() -> None:
    for category_id, title, sort_order in _ROWS:
        op.execute(
            f"""
            INSERT INTO khatm_categories
                (id, \"group\", title, body_text, source_note, is_active, sort_order)
            SELECT
                '{category_id}'::uuid, 'LAAN'::khatmcategorygroup,
                '{title}', NULL, 'seed:owner-2026-09-20', true, {sort_order}
            WHERE NOT EXISTS (
                SELECT 1 FROM khatm_categories
                WHERE \"group\" = 'LAAN'::khatmcategorygroup AND title = '{title}'
            )
            """
        )


def downgrade() -> None:
    ids = ",".join(f"'{category_id}'::uuid" for category_id, _, _ in _ROWS)
    op.execute(
        f"""
        DELETE FROM khatm_categories AS category
        WHERE category.id IN ({ids})
          AND NOT EXISTS (
              SELECT 1 FROM khatms WHERE khatms.content_category_id = category.id
          )
        """
    )
