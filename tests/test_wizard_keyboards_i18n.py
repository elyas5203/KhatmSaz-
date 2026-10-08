"""Regression: the create-khatm wizard keyboards were hardcoded Persian, so a
creator on the Arabic/English bot saw Persian buttons; and several steps had
no previous-step action. The owner later removed the explicit cancel button;
every wizard keyboard remains language-aware and ends with a back row."""
import pytest

from khatmsaz.bot import keyboards as k
from khatmsaz.i18n import t

_NO_ARG = [
    k.commitment_mode_keyboard,
    k.skip_niyyat_keyboard,
    k.content_delivery_mode_keyboard,
    k.reminder_tone_keyboard,
    k.creator_display_keyboard,
    k.start_schedule_keyboard,
    k.capacity_choice_keyboard,
    k.visibility_choice_keyboard,
    k.advertising_choice_keyboard,
    k.coupon_entry_keyboard,
]


@pytest.mark.parametrize("lang", ["fa", "ar", "en"])
def test_every_wizard_keyboard_is_localized_without_cancel(lang):
    for fn in _NO_ARG:
        kb = fn(lang)
        callbacks = [button.callback_data for row in kb.inline_keyboard for button in row]
        assert "ck:cancel" not in callbacks
        previous = kb.inline_keyboard[-1][0]
        assert previous.callback_data == "ck:back", f"{fn.__name__} missing previous-step row"
        assert previous.text == t("ck.back", lang)
    # keyboards that take extra args
    conf = k.confirm_keyboard(allow_coupon=True, lang=lang)
    assert conf.inline_keyboard[0][0].text == t("ck.confirm", lang)
    assert conf.inline_keyboard[-1][0].callback_data == "ck:edit_menu"
    cat = k.category_choice_keyboard([], group="DUA", allow_custom_request=True, lang=lang)
    assert cat.inline_keyboard[-1][0].callback_data == "ck:back"
    assert cat.inline_keyboard[0][0].text == t("ck.cat.custom", lang)

    first = k.template_choice_keyboard(lang)
    assert first.inline_keyboard[-1][0].callback_data == "ck:cancel"
    assert first.inline_keyboard[-1][0].text == t("ck.cancel", lang)
    assert "ck:back" not in [button.callback_data for row in first.inline_keyboard for button in row]


def test_wizard_labels_actually_differ_by_language():
    # Guards against a copy-paste that leaves every language identical.
    fa = k.template_choice_keyboard("fa").inline_keyboard[0][0].text
    en = k.template_choice_keyboard("en").inline_keyboard[0][0].text
    assert fa != en
