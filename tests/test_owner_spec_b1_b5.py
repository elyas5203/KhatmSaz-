"""Owner specification B1-B5 regression coverage for the creation wizard."""

from khatmsaz.bot.handlers.create_khatm import _commitment_total_keyboard
from khatmsaz.bot.keyboards import create_wizard_back_keyboard, template_choice_keyboard
from khatmsaz.i18n import t


def _callbacks(markup):
    return [button.callback_data for row in markup.inline_keyboard for button in row]


def test_b2_quran_family_has_short_owner_label():
    first = template_choice_keyboard("fa").inline_keyboard[0][0]
    assert first.text == "📖 ختم قرآن"
    assert "صفحات" not in first.text
    assert "صفحات" not in t("create_khatm.confirm.quran_content", "fa")


def test_b3_typed_and_total_steps_offer_real_previous_action():
    assert "ck:back" in _callbacks(create_wizard_back_keyboard("fa"))
    assert "ck:back" in _callbacks(_commitment_total_keyboard("fa"))
    assert "ck:cancel" not in _callbacks(create_wizard_back_keyboard("fa"))
    assert "ck:cancel" not in _callbacks(_commitment_total_keyboard("fa"))


def test_b4_confirmation_promises_available_edits_instead_of_no_changes():
    copy = t("create_khatm.confirm.final_warning", "fa")
    assert "ختم‌های من" in copy
    assert "قابل تغییر نیست" not in copy


def test_b5_count_copy_mentions_future_increase_without_saying_paid():
    for key in (
        "create_khatm.ask_open_target",
        "create_khatm.ask_commitment_total",
        "create_khatm.ask_commitment_total_custom",
    ):
        copy = t(key, "fa", title="صلوات", unit="صلوات")
        assert "با تمام‌شدن ختم، مخاطبان نمی‌توانند ادامه دهند" in copy
        assert "در آینده امکان افزایش تعداد هست" in copy
        assert "پولی" not in copy
