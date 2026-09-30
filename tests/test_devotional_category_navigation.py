from types import SimpleNamespace
from uuid import uuid4

from khatmsaz.bot.keyboards import category_choice_keyboard, template_choice_keyboard
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup


def _button_pairs(markup):
    return [(button.text, button.callback_data) for row in markup.inline_keyboard for button in row]


def test_creation_menu_exposes_devotional_families_as_independent_parents():
    buttons = _button_pairs(template_choice_keyboard())

    assert ("📿 ختم صلوات", "ck:group:SALAWAT") in buttons
    assert ("🤲 ختم دعا و زیارت", "ck:group:DUA") in buttons
    assert ("🗡 ختم لعن", "ck:group:LAAN") in buttons
    assert ("📖 ختم قرآن", "ck:tpl:QURAN_PAGE") in buttons
    assert all(callback != "ck:tpl:SALAWAT" for _, callback in buttons)


def test_each_parent_keyboard_contains_only_supplied_children():
    dua = SimpleNamespace(id=uuid4(), title="دعای عهد", group=KhatmCategoryGroup.DUA)
    laan = SimpleNamespace(id=uuid4(), title="لعن عمر", group=KhatmCategoryGroup.LAAN)

    dua_buttons = _button_pairs(
        category_choice_keyboard([dua], group="DUA", allow_custom_request=True)
    )
    laan_buttons = _button_pairs(
        category_choice_keyboard([laan], group="LAAN", allow_custom_request=False)
    )

    assert any(text == "🤲 دعای عهد" for text, _ in dua_buttons)
    assert all("لعن عمر" not in text for text, _ in dua_buttons)
    assert ("➕ دعا یا زیارت دیگر", "ck:cat:custom") in dua_buttons
    assert any(text == "🗡 لعن عمر" for text, _ in laan_buttons)
    assert all(callback != "ck:cat:custom" for _, callback in laan_buttons)
