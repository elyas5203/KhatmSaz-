from types import SimpleNamespace
from uuid import uuid4

import pytest

from khatmsaz.bot.member_scope import khatm_matches_bot, participation_matches_bot
from khatmsaz.modules.bot_registry.models import BotCategory, BotRole
from khatmsaz.modules.khatm.models import KhatmTemplateType
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup


def _bot(category, instance_id=None):
    return SimpleNamespace(
        khatmsaz_role=BotRole.MEMBER,
        khatmsaz_category=category,
        khatmsaz_instance_id=instance_id or uuid4(),
    )


def test_member_participation_is_strictly_limited_to_current_bot_instance():
    bot = _bot(BotCategory.DUA_ZIYARAT)
    assert participation_matches_bot(
        SimpleNamespace(joined_via_bot_instance_id=bot.khatmsaz_instance_id), bot
    )
    assert not participation_matches_bot(
        SimpleNamespace(joined_via_bot_instance_id=uuid4()), bot
    )
    assert not participation_matches_bot(
        SimpleNamespace(joined_via_bot_instance_id=None), bot
    )


@pytest.mark.asyncio
async def test_quran_khatm_never_appears_in_dua_bot():
    khatm = SimpleNamespace(
        template_type=KhatmTemplateType.QURAN_PAGE, content_category_id=None
    )
    assert not await khatm_matches_bot(None, khatm, _bot(BotCategory.DUA_ZIYARAT))
    assert await khatm_matches_bot(None, khatm, _bot(BotCategory.QURAN))


@pytest.mark.asyncio
async def test_devotional_families_do_not_cross_member_bots(monkeypatch):
    category_id = uuid4()
    khatm = SimpleNamespace(
        template_type=KhatmTemplateType.SALAWAT, content_category_id=category_id
    )

    async def fake_get(_session, _category_id):
        assert _category_id == category_id
        return SimpleNamespace(group=KhatmCategoryGroup.DUA)

    monkeypatch.setattr("khatmsaz.bot.member_scope.category_service.get", fake_get)
    assert await khatm_matches_bot(None, khatm, _bot(BotCategory.DUA_ZIYARAT))
    assert not await khatm_matches_bot(None, khatm, _bot(BotCategory.SALAWAT))
    assert not await khatm_matches_bot(None, khatm, _bot(BotCategory.LAAN))
