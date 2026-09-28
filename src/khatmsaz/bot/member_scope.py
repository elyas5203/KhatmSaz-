"""Hard isolation boundary for category-specific member bots."""

from __future__ import annotations

from khatmsaz.modules.bot_registry.models import BotCategory, BotRole
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType
from khatmsaz.modules.khatm_category import service as category_service


def member_instance_id(bot):
    """Return the instance id only for member bots; creator bots are unscoped."""
    role = getattr(bot, "khatmsaz_role", None)
    if role not in {BotRole.MEMBER, BotRole.MEMBER.value}:
        return None
    return getattr(bot, "khatmsaz_instance_id", None)


def participation_matches_bot(participation, bot) -> bool:
    """A member bot may only access memberships created through itself."""
    instance_id = member_instance_id(bot)
    if instance_id is None:
        return getattr(bot, "khatmsaz_role", None) not in {BotRole.MEMBER, BotRole.MEMBER.value}
    return participation.joined_via_bot_instance_id == instance_id


async def khatm_matches_bot(session, khatm: Khatm, bot) -> bool:
    """Keep Quran/Salawat/Dua-Ziyarat/La'an families in their own member bot."""
    role = getattr(bot, "khatmsaz_role", None)
    if role not in {BotRole.MEMBER, BotRole.MEMBER.value}:
        return True

    actual = getattr(bot, "khatmsaz_category", None)
    actual = actual.value if isinstance(actual, BotCategory) else actual
    if khatm.template_type in {KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.QURAN_SURAH}:
        expected = BotCategory.QURAN.value
    else:
        category = (
            await category_service.get(session, khatm.content_category_id)
            if khatm.content_category_id
            else None
        )
        group = category.group.value if category is not None else None
        expected = {
            "SALAWAT": BotCategory.SALAWAT.value,
            "DUA": BotCategory.DUA_ZIYARAT.value,
            "LAAN": BotCategory.LAAN.value,
        }.get(group)
    return expected is not None and actual == expected
