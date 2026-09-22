"""Real PostgreSQL filtering proof for independent devotional families."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.modules.khatm_category import service
from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup


@pytest.mark.integration
@pytest.mark.asyncio
async def test_active_categories_are_filtered_by_the_selected_parent_family():
    marker = "integration-family-filter"
    async with session_scope() as session:
        dua = await service.create(
            session, group="DUA", title="دعای تست تفکیک", body_text=None, source_note=marker
        )
        laan = await service.create(
            session, group="LAAN", title="لعن تست تفکیک", body_text=None, source_note=marker
        )
        salawat = await service.create(
            session, group="SALAWAT", title="صلوات تست تفکیک", body_text=None, source_note=marker
        )
        await service.set_active(session, salawat.id, False)

        duas = await service.list_active(session, KhatmCategoryGroup.DUA)
        laans = await service.list_active(session, KhatmCategoryGroup.LAAN)
        salawats = await service.list_active(session, KhatmCategoryGroup.SALAWAT)
        assert dua.id in {item.id for item in duas}
        assert laan.id not in {item.id for item in duas}
        assert laan.id in {item.id for item in laans}
        assert dua.id not in {item.id for item in laans}
        assert salawat.id not in {item.id for item in salawats}

    async with session_scope() as session:
        await session.execute(delete(KhatmCategory).where(KhatmCategory.source_note == marker))
