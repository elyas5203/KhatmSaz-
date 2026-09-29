from khatmsaz.bot.handlers.create_khatm import _default_khatm_title
from khatmsaz.modules.khatm.models import KhatmTemplateType


def test_quran_title_is_automatic():
    assert _default_khatm_title(
        {"template_type": KhatmTemplateType.QURAN_PAGE.value}, "fa"
    ) == "ختم قرآن"


def test_devotional_title_uses_selected_category():
    assert _default_khatm_title(
        {
            "template_type": KhatmTemplateType.SALAWAT.value,
            "content_category_title": "دعای عهد",
        },
        "fa",
    ) == "ختم دعای عهد"
