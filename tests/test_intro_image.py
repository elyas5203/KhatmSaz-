"""R2 (owner 2026-09-28): per-bot intro image shown after the creator picks
commitment/free, with the fixed «همه ختم‌ها به نیت صاحب‌الزمان» caption. Tests the
pure wizard→bot-category mapping and that the caption exists in all languages."""
from khatmsaz.bot.handlers.create_khatm import _bot_category_for
from khatmsaz.modules.bot_registry.models import BotCategory
from khatmsaz.modules.khatm.models import KhatmTemplateType
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup
from khatmsaz.i18n import _STRINGS, SUPPORTED_LANGUAGES


def test_quran_maps_to_quran_bot():
    assert _bot_category_for(KhatmTemplateType.QURAN_PAGE.value, None) == BotCategory.QURAN.value
    assert _bot_category_for(KhatmTemplateType.QURAN_SURAH.value, None) == BotCategory.QURAN.value


def test_laan_group_maps_to_laan_bot():
    assert _bot_category_for(KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.LAAN.value) == BotCategory.LAAN.value


def test_dua_group_maps_to_dua_ziyarat_bot():
    assert _bot_category_for(KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.DUA.value) == BotCategory.DUA_ZIYARAT.value


def test_salawat_default():
    assert _bot_category_for(KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.SALAWAT.value) == BotCategory.SALAWAT.value
    assert _bot_category_for(KhatmTemplateType.SALAWAT.value, None) == BotCategory.SALAWAT.value


def test_intro_caption_present_all_langs():
    cap = _STRINGS["intro.image_caption"]
    for lang in SUPPORTED_LANGUAGES:
        assert cap[lang].strip()
