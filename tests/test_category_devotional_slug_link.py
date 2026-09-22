"""BACKLOG.md §14 fix (2026-09-21): replace the fragile name-matching hack
("عاشورا" appearing in the category title) with an explicit
`KhatmCategory.devotional_slug` link, admin-editable via the categories
web panel. This confirms a category with an explicit slug delivers the
right devotional text regardless of its title — the old hack would have
required a specific Persian substring in the title to work at all."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_category.models import KhatmCategory


@pytest.mark.integration
@pytest.mark.asyncio
async def test_devotional_slug_link_does_not_depend_on_title_wording():
    slug = f"test-devotional-{new_id()}"[:40]
    async with session_scope() as session:
        await content_service.register_devotional_text(
            session, content_type="DUA", slug=slug, title="یک دعای تستی",
            text_body="متن آزمایشی برای تست اتصال مستقیم",
        )
        category = await category_service.create(
            session, group="DUA", title="یک اسم کاملاً بی‌ربط، بدون کلمهٔ خاص",
            body_text=None, source_note=None, devotional_slug=slug,
        )
        assert category.devotional_slug == slug

        asset = await content_service.get_devotional_asset(session, category.devotional_slug)
        assert asset is not None
        assert asset.text_body == "متن آزمایشی برای تست اتصال مستقیم"

        # Update should also persist the link (and allow clearing it).
        updated = await category_service.update(
            session, category.id, title=category.title, body_text=None, source_note=None,
            devotional_slug=None,
        )
        assert updated.devotional_slug is None

        from khatmsaz.modules.content.models import DevotionalAsset
        await session.execute(delete(KhatmCategory).where(KhatmCategory.id == category.id))
        await session.execute(delete(DevotionalAsset).where(DevotionalAsset.slug == slug))
