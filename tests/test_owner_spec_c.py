"""Regression locks for OWNER_SPEC_MASTER section C."""

from pathlib import Path

from khatmsaz.bot.handlers import creator_broadcast


ROOT = Path(__file__).resolve().parents[1]


def test_c3_positive_content_approval_copy_is_used():
    bot_source = Path(creator_broadcast.__file__).read_text(encoding="utf-8")
    web = (ROOT / "src/khatmsaz/web/templates/creator_broadcasts.html").read_text(encoding="utf-8")
    assert "برای تأیید محتوا" in bot_source
    assert "برای تأیید محتوا" in web
    assert "ثبت برای تأیید مدیر" not in web


def test_c5_web_exposes_composable_scope_province_and_gender_filters():
    web = (ROOT / "src/khatmsaz/web/templates/creator_broadcasts.html").read_text(encoding="utf-8")
    assert 'name="target"' in web
    assert 'name="province"' in web
    assert 'name="gender"' in web


def test_c6_bot_accepts_text_photo_video_and_voice():
    source = Path(creator_broadcast.__file__).read_text(encoding="utf-8")
    for media in ("message.text", "message.photo", "message.video", "message.voice"):
        assert media in source


def test_create_wizard_renders_cancel_only_on_the_first_screen():
    from khatmsaz.bot import keyboards

    first_callbacks = [
        button.callback_data for row in keyboards.template_choice_keyboard("fa").inline_keyboard for button in row
    ]
    later_callbacks = [
        button.callback_data for row in keyboards.commitment_mode_keyboard("fa").inline_keyboard for button in row
    ]
    assert first_callbacks.count("ck:cancel") == 1
    assert "ck:back" not in first_callbacks
    assert "ck:cancel" not in later_callbacks
    assert "ck:back" in later_callbacks
