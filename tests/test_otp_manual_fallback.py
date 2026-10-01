from pathlib import Path

from khatmsaz.bot.handlers.change_phone import ChangePhone, _otp_fallback_keyboard, _reveal_otp_fallback
from khatmsaz.i18n import t


def test_fsm_uses_persistent_redis_with_bot_scoped_keys():
    source = Path("src/khatmsaz/bootstrap.py").read_text(encoding="utf-8")
    assert "RedisStorage.from_url" in source
    assert "with_bot_id=True" in source
    assert "Dispatcher(storage=MemoryStorage())" not in source


def test_expired_otp_offers_admin_review_action():
    markup = _otp_fallback_keyboard("challenge-id", "fa")
    button = markup.inline_keyboard[0][0]
    assert "پیامک نرسید" in button.text
    assert button.callback_data == "otp_manual:challenge-id"
    assert hasattr(ChangePhone, "waiting_manual_review")


def test_creator_otp_copy_matches_real_five_minute_ttl():
    assert "۵ دقیقه" in t("change_phone.otp_sms_text", "fa", code="123456")
    assert "درخواست بررسی شماره" in t("change_phone.request_admin_after_expiry", "fa")
    assert "دکمهٔ ادامه" in t("change_phone.manual_review_creator", "fa")


def test_admin_review_button_is_revealed_by_delayed_task_not_initial_copy():
    import inspect

    source = inspect.getsource(_reveal_otp_fallback)
    assert "asyncio.sleep(300)" in source
    assert "edit_message_reply_markup" in source


def test_admin_approval_notice_has_continue_label():
    assert t("manual_phone_verification.continue_button", "fa") == "✅ ادامهٔ فرایند"
