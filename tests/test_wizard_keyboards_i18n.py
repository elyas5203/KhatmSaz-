"""Regression: the create-khatm wizard keyboards were hardcoded Persian, so a
creator on the Arabic/English bot saw Persian buttons; and several steps had
no cancel. Now every wizard keyboard is language-aware and ends with a cancel
row (goal: «انصراف» available at every step)."""
import pytest

from khatmsaz.bot import keyboards as k
from khatmsaz.i18n import t

_NO_ARG = [
    k.commitment_mode_keyboard,
    k.template_choice_keyboard,
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
def test_every_wizard_keyboard_is_localized_and_cancellable(lang):
    for fn in _NO_ARG:
        kb = fn(lang)
        last = kb.inline_keyboard[-1][0]
        assert last.callback_data == "ck:cancel", f"{fn.__name__} missing cancel row"
        assert last.text == t("ck.cancel", lang), f"{fn.__name__} cancel not localized for {lang}"
    # keyboards that take extra args
    conf = k.confirm_keyboard(allow_coupon=True, lang=lang)
    assert conf.inline_keyboard[0][0].text == t("ck.confirm", lang)
    assert conf.inline_keyboard[-1][0].callback_data == "ck:cancel"
    cat = k.category_choice_keyboard([], group="DUA", allow_custom_request=True, lang=lang)
    assert cat.inline_keyboard[-1][0].callback_data == "ck:cancel"
    assert cat.inline_keyboard[0][0].text == t("ck.cat.custom", lang)


def test_wizard_labels_actually_differ_by_language():
    # Guards against a copy-paste that leaves every language identical.
    fa = k.template_choice_keyboard("fa").inline_keyboard[0][0].text
    en = k.template_choice_keyboard("en").inline_keyboard[0][0].text
    assert fa != en
