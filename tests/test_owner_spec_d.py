"""Regression coverage for OWNER_SPEC_MASTER section D."""

from pathlib import Path

from khatmsaz.bot.keyboards import member_menu_keyboard, participant_menu_keyboard
from khatmsaz.i18n import t


ROOT = Path(__file__).resolve().parents[1]


def test_d1_today_action_uses_the_full_reading_label_everywhere():
    assert t("menu.today", "fa") == "📖 انجام قرائت امروز"
    labels = [button.text for row in participant_menu_keyboard("fa").keyboard for button in row]
    assert "📖 انجام قرائت امروز" in labels

    user_facing_sources = [
        ROOT / "src/khatmsaz/i18n/__init__.py",
        ROOT / "src/khatmsaz/bot/handlers/content_settings.py",
        ROOT / "src/khatmsaz/bot/handlers/portions.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in user_facing_sources)
    for stale in ("📅 امروز", "📅 Today", "📅 اليوم", "دکمه «امروز»"):
        assert stale not in combined


def test_d2_help_matches_current_creation_settings_and_management_features():
    creation = t("help.create", "fa")
    settings = t("help.settings", "fa")
    manage = t("help.manage", "fa")

    assert "عنوان مناسب خودکار ساخته می‌شود" in creation
    assert "بات عنوان" not in creation
    assert all(term in settings for term in ("ساعت یادآوری", "منطقهٔ زمانی", "پیامک", "اتصال حساب قبلی"))
    assert "قاری قابل تغییرند" not in settings
    assert all(term in manage for term in ("افزایش امن هدف", "عکس", "فیلم", "ویس", "استان", "جنسیت"))
    assert "فقط عنوان و خوش‌آمد" not in manage


def test_d3_every_member_menu_contacts_the_khatm_creator_not_support():
    for factory in (member_menu_keyboard, participant_menu_keyboard):
        labels = [button.text for row in factory("fa").keyboard for button in row]
        assert t("menu.contact_creator", "fa") in labels
        assert t("menu.support", "fa") not in labels


def test_d4_member_menu_and_admin_panel_expose_custom_khatm_contact():
    labels = [button.text for row in member_menu_keyboard("fa").keyboard for button in row]
    assert t("menu.custom_khatm", "fa") in labels
    operations = (ROOT / "src/khatmsaz/web/templates/operations.html").read_text(encoding="utf-8")
    assert 'name="custom_khatm_admin_phone"' in operations
    assert "/operations/custom-khatm-phone" in operations
