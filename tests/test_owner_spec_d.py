"""Regression coverage for OWNER_SPEC_MASTER section D."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from khatmsaz.bot.keyboards import member_menu_keyboard, participant_menu_keyboard
from khatmsaz.i18n import t
from khatmsaz.bot.handlers import member_registration
from khatmsaz.bot.handlers import join_flow


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


class _RegistrationState:
    def __init__(self):
        self.data = {"_member_reg_mid": 41}

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **kwargs):
        self.data.update(kwargs)


class _RegistrationBot:
    def __init__(self):
        self.deleted = []

    async def delete_message(self, chat_id, message_id):
        self.deleted.append((chat_id, message_id))


class _RegistrationMessage:
    def __init__(self):
        self.bot = _RegistrationBot()
        self.chat = SimpleNamespace(id=7)
        self.from_user = SimpleNamespace(is_bot=False)
        self.message_id = 42
        self.deleted = False
        self.answers = []

    async def delete(self):
        self.deleted = True

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))
        return SimpleNamespace(message_id=43)


@pytest.mark.asyncio
async def test_d5_member_registration_replaces_only_its_owned_prompt_and_typed_reply():
    state = _RegistrationState()
    message = _RegistrationMessage()

    await member_registration._member_reg_prompt(message, state, "مرحله بعد")

    assert message.deleted is True
    assert message.bot.deleted == [(7, 41)]
    assert state.data["_member_reg_mid"] == 43
    assert message.answers[0][0] == "مرحله بعد"


def test_d5_member_registration_has_previous_step_actions_after_name():
    province_callbacks = [
        button.callback_data
        for row in member_registration._member_province_keyboard("fa").inline_keyboard
        for button in row
    ]
    gender_callbacks = [
        button.callback_data
        for row in member_registration._member_gender_keyboard("fa").inline_keyboard
        for button in row
    ]
    assert "mreg:back:phone" in province_callbacks
    assert "mreg:back:city" in gender_callbacks


@pytest.mark.asyncio
async def test_d5_delivery_hour_completion_keeps_the_join_welcome_summary():
    edits = []

    class Bot:
        async def edit_message_text(self, **kwargs):
            edits.append(kwargs)

    message = SimpleNamespace(bot=Bot(), chat=SimpleNamespace(id=9), answer=None)
    await join_flow._finish_join_prompt(
        message, {"_join_wizard_mid": 12, "_join_summary": "خوش آمدید به ختم نمونه"},
        "ساعت ۰۹:۰۰ ذخیره شد",
    )
    assert edits[0]["message_id"] == 12
    assert edits[0]["text"] == "خوش آمدید به ختم نمونه\n\nساعت ۰۹:۰۰ ذخیره شد"
