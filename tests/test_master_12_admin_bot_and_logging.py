import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from aiogram.types import InlineKeyboardMarkup, Message, User as TgUser

from khatmsaz.bot.handlers.admin_bot import handlers as admin_bot_handlers
from khatmsaz.bot.handlers.admin_bot.handlers import (
    admin_broadcasts_handler,
    admin_laan_handler,
    admin_receipts_handler,
    admin_start_handler,
    admin_status_handler,
)
from khatmsaz.core.logging_system import (
    TelegramErrorAlertHandler,
    get_log_file_paths,
    get_recent_errors,
    get_recent_logs,
)
from khatmsaz.modules.bot_registry.models import BotCategory, BotRole
from khatmsaz.modules.identity.models import Platform, UserRole


@pytest.mark.asyncio
async def test_telegram_error_alert_handler_emits_alert_and_debounces():
    mock_notify = AsyncMock()
    with patch("khatmsaz.bot.admin_notifications.notify_super_admins", new=mock_notify):
        handler = TelegramErrorAlertHandler(level=logging.ERROR)

        record = logging.LogRecord(
            name="khatmsaz.test",
            level=logging.ERROR,
            pathname="src/test.py",
            lineno=42,
            msg="Test critical exception occurred",
            args=(),
            exc_info=None,
        )

        # First emission should send
        handler.emit(record)
        await asyncio.sleep(0.02)
        assert mock_notify.await_count == 1
        call_text = mock_notify.await_args.args[0]
        assert "🚨 <b>هشدار خطای سیستمی در ختم‌ساز</b>" in call_text
        assert "Test critical exception occurred" in call_text

        # Immediate second emission with same key should be debounced
        mock_notify.reset_mock()
        handler.emit(record)
        await asyncio.sleep(0.02)
        assert mock_notify.await_count == 0


def test_logging_helper_functions(tmp_path, monkeypatch):
    khatmsaz_log = tmp_path / "khatmsaz.log"
    errors_log = tmp_path / "errors.log"

    khatmsaz_log.write_text("line 1\nline 2\nline 3\n", encoding="utf-8")
    errors_log.write_text("error line\n", encoding="utf-8")

    monkeypatch.setattr("khatmsaz.core.logging_system._MAIN_LOG_FILE", khatmsaz_log)
    monkeypatch.setattr("khatmsaz.core.logging_system._ERROR_LOG_FILE", errors_log)

    assert "line 3" in get_recent_logs(lines=2)
    assert "error line" in get_recent_errors(lines=1)


@pytest.mark.asyncio
async def test_admin_bot_authorization_guard(monkeypatch):
    # Non-super admin
    monkeypatch.setattr(
        admin_bot_handlers,
        "_is_super_admin",
        AsyncMock(return_value=False),
    )

    message = MagicMock()
    message.from_user = SimpleNamespace(id=111111)
    message.answer = AsyncMock()

    await admin_start_handler(message)
    message.answer.assert_awaited_once()
    assert "دسترسی غیرمجاز" in message.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_admin_bot_start_dashboard_for_super_admin(monkeypatch):
    monkeypatch.setattr(
        admin_bot_handlers,
        "_is_super_admin",
        AsyncMock(return_value=True),
    )

    # Mock count queries
    mock_session = AsyncMock()
    mock_session.scalar = AsyncMock(return_value=3)

    mock_scope = MagicMock()
    mock_scope.__aenter__.return_value = mock_session

    monkeypatch.setattr(admin_bot_handlers, "session_scope", lambda: mock_scope)

    message = MagicMock()
    message.from_user = SimpleNamespace(id=5490508090)
    message.answer = AsyncMock()

    await admin_start_handler(message)
    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "سامانه مدیریت مرکزی ختم‌ساز" in sent_text
    assert "مدیر گرامی" in sent_text
    assert "فیش" in sent_text
    reply_markup = message.answer.await_args.kwargs.get("reply_markup")
    assert isinstance(reply_markup, InlineKeyboardMarkup)


@pytest.mark.asyncio
async def test_admin_bot_status_telemetry(monkeypatch):
    monkeypatch.setattr(
        admin_bot_handlers,
        "_is_super_admin",
        AsyncMock(return_value=True),
    )

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_scope = MagicMock()
    mock_scope.__aenter__.return_value = mock_session
    monkeypatch.setattr(admin_bot_handlers, "session_scope", lambda: mock_scope)

    mock_reg = MagicMock()
    mock_reg.creator_bots = lambda: [MagicMock()]
    mock_reg.admin_bots = lambda: [MagicMock()]
    mock_reg.member_bots = lambda: [MagicMock()]
    monkeypatch.setattr(admin_bot_handlers, "get_registry", lambda: mock_reg)

    message = MagicMock()
    message.from_user = SimpleNamespace(id=5490508090)
    message.answer = AsyncMock()

    await admin_status_handler(message)
    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args.args[0]
    assert "وضعیت" in sent_text
    assert "Postgres" in sent_text


@pytest.mark.asyncio
async def test_custom_laan_wizard_handlers():
    from khatmsaz.bot.handlers.create_khatm import (
        enter_laan_title,
        enter_laan_text,
        CreateKhatm,
    )

    # 1. Enter title
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"lang": "fa"})
    message = MagicMock()
    message.text = "لعن بنی‌امیه و دشمنان اهل‌بیت"
    message.answer = AsyncMock()

    with patch("khatmsaz.bot.handlers.create_khatm._wiz", new=AsyncMock()) as mock_wiz:
        await enter_laan_title(message, state)
        state.update_data.assert_awaited_once_with(title="لعن بنی‌امیه و دشمنان اهل‌بیت")
        state.set_state.assert_awaited_once_with(CreateKhatm.entering_laan_text)
        mock_wiz.assert_awaited_once()

    # 2. Enter text
    state_mock = AsyncMock()
    state_mock.get_data = AsyncMock(return_value={"title": "لعن بنی‌امیه", "lang": "fa"})
    message2 = MagicMock()
    message2.text = "اللهم العن اول ظالم ظلم حق محمد و آل محمد..."
    message2.answer = AsyncMock()

    with patch("khatmsaz.bot.handlers.create_khatm._ask_mode", new=AsyncMock()) as mock_ask_mode:
        await enter_laan_text(message2, state_mock)
        state_mock.update_data.assert_awaited_once_with(
            recitation_text="اللهم العن اول ظالم ظلم حق محمد و آل محمد..."
        )
        mock_ask_mode.assert_awaited_once()
