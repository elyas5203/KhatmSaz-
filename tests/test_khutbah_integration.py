import pytest
from types import SimpleNamespace
from uuid import uuid4

from khatmsaz.bot.handlers.start import build_join_preview_message
from khatmsaz.bot.member_copy import completion_text
from khatmsaz.i18n import t
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.bot_registry.models import BotCategory


def test_khutbah_join_preview_message():
    khatm = Khatm(
        id=uuid4(),
        title="ختم خطبه فدکیه",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        niyyat="فرج امام زمان عجل الله تعالی فرجه الشریف",
        welcome_text="خوش آمدید",
    )
    preview = build_join_preview_message(
        khatm,
        creator_name="خادم",
        member_count=5,
        lang="fa",
        category_title="خطبه فدکیه حضرت فاطمه زهرا (س)",
        category_group="KHUTBAH",
    )
    assert "📜" in preview
    assert "خطبه" in preview
    assert "خطبه فدکیه حضرت فاطمه زهرا (س)" in preview


def test_khutbah_completion_verb():
    khatm = SimpleNamespace(
        title="ختم خطبه فدکیه",
        niyyat="سلامتی و فرج امام عصر علیه السلام",
    )
    msg = completion_text(khatm, "khutbah", "بخش ۱ از خطبه فدکیه", lang="fa")
    assert "✅ بخش ۱ از خطبه فدکیه قرائت شد." in msg
    assert "انجام شد" not in msg


def test_bot_category_enum_includes_khutbah():
    assert hasattr(BotCategory, "KHUTBAH")
    assert BotCategory.KHUTBAH.value == "KHUTBAH"


def test_khutbah_routing_to_dua_ziyarat_bot():
    from khatmsaz.bot.handlers.create_khatm import _bot_category_for
    from khatmsaz.modules.bot_registry import service as bot_reg_service
    from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup

    # 1. Wizard category resolution
    wizard_cat = _bot_category_for(KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.KHUTBAH.value)
    assert wizard_cat == BotCategory.DUA_ZIYARAT.value

    # 2. Service resolution for Khatm
    khatm = Khatm(
        id=uuid4(),
        title="ختم خطبه فدکیه",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
    )
    cat = KhatmCategory(
        id=uuid4(),
        group=KhatmCategoryGroup.KHUTBAH,
        title="خطبه فدکیه",
    )
    resolved = bot_reg_service.resolve_bot_category(khatm, cat)
    assert resolved == BotCategory.DUA_ZIYARAT

