import pytest

from khatmsaz.bot.handlers.member_start import _matches_member_bot
from khatmsaz.modules.bot_registry.models import BotCategory
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType


@pytest.mark.asyncio
async def test_category_free_salawat_is_accepted_by_salawat_member_bot():
    khatm = Khatm(
        template_type=KhatmTemplateType.SALAWAT,
        content_category_id=None,
    )

    assert await _matches_member_bot(None, khatm, BotCategory.SALAWAT.value)
    assert not await _matches_member_bot(None, khatm, BotCategory.QURAN.value)
