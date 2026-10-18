"""Tests for multi-admin delegation, cross-admin alert sync, and daily operational report."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pytest

from khatmsaz.bot.admin_sync import (
    get_all_admin_telegram_chat_ids,
    is_admin_alert_handled,
    mark_admin_alert_handled,
    record_admin_alert_message,
)
from khatmsaz.bot.handlers import admin as admin_handler
from khatmsaz.bot.handlers import manual_phone_verification as mpv_handler
from khatmsaz.bot.handlers import suggestions as suggestions_handler
from khatmsaz.config import Settings
from khatmsaz.modules.authorization.models import AdminAlertMessage, AdminPermission, AdminRole, AdminRoleGrant
from khatmsaz.modules.authorization.service import ROLE_PERMISSIONS, has_permission
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole
from khatmsaz.modules.identity.service import _bootstrap_super_admin_if_configured
from khatmsaz.modules.reporting.admin_daily_report import (
    generate_daily_admin_report_text,
    get_daily_admin_stats,
    gregorian_to_jalali,
)


def test_admin_role_permissions_include_all_except_role_management():
    """AdminRole.ADMIN must have full admin operations without permission to manage roles."""
    admin_perms = ROLE_PERMISSIONS[AdminRole.ADMIN]

    # Required operational permissions
    assert AdminPermission.DASHBOARD_ACCESS in admin_perms
    assert AdminPermission.SUPPORT_USERS in admin_perms
    assert AdminPermission.CONTENT_MANAGE in admin_perms
    assert AdminPermission.MODERATION_MANAGE in admin_perms
    assert AdminPermission.FINANCE_MANAGE in admin_perms
    assert AdminPermission.MARKETING_MANAGE in admin_perms
    assert AdminPermission.OPERATIONS_VIEW in admin_perms

    # Excluded strictly: cannot add, revoke, or alter other admins
    assert AdminPermission.ADMIN_ROLES_MANAGE not in admin_perms


@pytest.mark.asyncio
async def test_bootstrap_admin_from_env_config(monkeypatch):
    """Users in admin_telegram_chat_ids are bootstrapped as AdminRole.ADMIN without SUPER_ADMIN user role."""
    fake_settings = Settings(
        admin_telegram_chat_ids="999888,777666",
        super_admin_telegram_chat_ids="111222",
    )
    monkeypatch.setattr("khatmsaz.modules.identity.service.get_settings", lambda: fake_settings)

    granted_roles = []

    async def fake_grant(session, user_id, role):
        granted_roles.append((user_id, role))

    monkeypatch.setattr("khatmsaz.modules.authorization.service.grant_role_by_system", fake_grant)
    monkeypatch.setattr("khatmsaz.modules.authorization.service.list_roles", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.identity.repository.set_role", AsyncMock())

    # 1. Non-super admin chat ID
    admin_user = User(id=uuid.uuid4(), role=UserRole.USER)
    session = AsyncMock()
    await _bootstrap_super_admin_if_configured(session, Platform.TELEGRAM, "999888", admin_user)

    assert admin_user.role == UserRole.USER  # Remains USER (or CREATOR), not SUPER_ADMIN
    assert (admin_user.id, AdminRole.ADMIN) in granted_roles

    # 2. Super admin chat ID
    super_user = User(id=uuid.uuid4(), role=UserRole.USER)
    await _bootstrap_super_admin_if_configured(session, Platform.TELEGRAM, "111222", super_user)

    assert super_user.role == UserRole.SUPER_ADMIN


@pytest.mark.asyncio
async def test_get_all_admin_telegram_chat_ids(monkeypatch):
    """Chat IDs from both super_admin_telegram_chat_ids and admin_telegram_chat_ids are unified."""
    fake_settings = Settings(
        super_admin_telegram_chat_ids="100, 200",
        admin_telegram_chat_ids="200, 300, 400",
    )
    monkeypatch.setattr("khatmsaz.bot.admin_sync.get_settings", lambda: fake_settings)

    ids = await get_all_admin_telegram_chat_ids(session=None)
    assert ids == ["100", "200", "300", "400"]


@pytest.mark.asyncio
async def test_admin_alert_recording_and_sync():
    """Alert messages sent to multiple admins are tracked and updated synchronously upon first action."""
    mock_alerts = []

    class FakeSession:
        def add(self, obj):
            mock_alerts.append(obj)

        async def flush(self):
            pass

        async def execute(self, stmt):
            result = MagicMock()
            res_list = [a for a in mock_alerts if a.alert_type == "SUPPORT_TICKET" and a.reference_id == "ref-123"]
            result.scalars.return_value.all.return_value = res_list
            handled_items = [a for a in res_list if a.handled]
            result.scalar_one_or_none.return_value = handled_items[0] if handled_items else None
            return result

    session = FakeSession()

    # Record alerts sent to Admin A and Admin B
    await record_admin_alert_message(
        session,
        alert_type="SUPPORT_TICKET",
        reference_id="ref-123",
        chat_id="1001",
        message_id=55,
        original_text="پیام تست کاربر",
    )
    await record_admin_alert_message(
        session,
        alert_type="SUPPORT_TICKET",
        reference_id="ref-123",
        chat_id="1002",
        message_id=56,
        original_text="پیام تست کاربر",
    )

    # Initial check: not handled
    handled, by_name, action = await is_admin_alert_handled(session, "SUPPORT_TICKET", "ref-123")
    assert not handled
    assert by_name is None

    # First admin takes action
    bot = AsyncMock()
    count = await mark_admin_alert_handled(
        session,
        bot,
        alert_type="SUPPORT_TICKET",
        reference_id="ref-123",
        actor_name="علی",
        action_label="پاسخ داده",
        tz_name="Asia/Tehran",
    )

    assert count == 2
    for a in mock_alerts:
        assert a.handled is True
        assert a.handled_by_name == "علی"
        assert a.action_taken == "پاسخ داده"

    # Both admins' Telegram messages were edited
    assert bot.edit_message_text.call_count == 2
    called_chats = {call.kwargs["chat_id"] for call in bot.edit_message_text.call_args_list}
    assert called_chats == {1001, 1002}
    for call in bot.edit_message_text.call_args_list:
        assert "✅ توسط «علی»" in call.kwargs["text"]
        assert "پاسخ داده شد." in call.kwargs["text"]
        assert call.kwargs["reply_markup"] is None

    # Subsequent check: handled
    handled2, by_name2, action2 = await is_admin_alert_handled(session, "SUPPORT_TICKET", "ref-123")
    assert handled2 is True
    assert by_name2 == "علی"
    assert action2 == "پاسخ داده"


@pytest.mark.asyncio
async def test_duplicate_manual_phone_decision_prevented(monkeypatch):
    """When an admin clicks a decision on an already-handled request, an alert is shown and no action is taken."""
    callback = AsyncMock()
    callback.data = "mpv:a:550e8400-e29b-41d4-a716-446655440000"
    callback.from_user.id = 1001
    callback.message.bot.khatmsaz_platform = Platform.TELEGRAM

    admin_user = SimpleNamespace(id=uuid.uuid4(), display_name="ادمین ۱")

    @asynccontextmanager
    async def fake_session_scope():
        session = AsyncMock()
        yield session

    monkeypatch.setattr("khatmsaz.bot.handlers.manual_phone_verification.session_scope", fake_session_scope)
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.manual_phone_verification._authorized_admin",
        AsyncMock(return_value=admin_user),
    )
    # Simulate already handled by another admin
    monkeypatch.setattr(
        "khatmsaz.bot.admin_sync.is_admin_alert_handled",
        AsyncMock(return_value=(True, "ادمین ۲", "تأیید")),
    )

    approve_mock = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.manual_phone_verification.service.approve", approve_mock)

    await mpv_handler.decide_manual_phone_request(callback)

    # Approve was NOT called
    assert not approve_mock.called
    # Alert popup was displayed to the admin
    callback.answer.assert_called_once()
    alert_text = callback.answer.call_args.args[0] if callback.answer.call_args.args else callback.answer.call_args.kwargs.get("text")
    assert "قبلاً توسط «ادمین ۲» تأیید شده است" in alert_text


@pytest.mark.asyncio
async def test_duplicate_ticket_reply_prevented(monkeypatch):
    """When an admin clicks reply on an already-handled ticket, an alert is shown and state is not set."""
    callback = AsyncMock()
    callback.data = f"reply_user:{uuid.uuid4()}:ticket_ref_99"
    state = AsyncMock()

    @asynccontextmanager
    async def fake_session_scope():
        yield AsyncMock()

    monkeypatch.setattr("khatmsaz.bot.handlers.suggestions.session_scope", fake_session_scope)
    monkeypatch.setattr(
        "khatmsaz.bot.admin_sync.is_admin_alert_handled",
        AsyncMock(return_value=(True, "مهدی", "پاسخ داده")),
    )

    await suggestions_handler.start_reply_to_user(callback, state)

    # State was not set to replying_to_user
    assert not state.set_state.called
    # Alert notice shown
    callback.answer.assert_called_once()
    alert_text = callback.answer.call_args.args[0] if callback.answer.call_args.args else callback.answer.call_args.kwargs.get("text")
    assert "قبلاً توسط «مهدی» پاسخ داده شده است" in alert_text


def test_gregorian_to_jalali_conversion():
    """Verify precision of pure-Python Gregorian to Jalali converter."""
    # 2026-10-18 -> 1405-07-26 (26 Mehr 1405)
    jy, jm, jd = gregorian_to_jalali(2026, 10, 18)
    assert (jy, jm, jd) == (1405, 7, 26)

    # Nowruz 2026-03-21 -> 1405-01-01 (1 Farvardin 1405)
    jy2, jm2, jd2 = gregorian_to_jalali(2026, 3, 21)
    assert (jy2, jm2, jd2) == (1405, 1, 1)


@pytest.mark.asyncio
async def test_generate_daily_admin_report_formatting(monkeypatch):
    """Daily report generates structured Persian text with date, user, khatm, and activity metrics."""
    fake_stats = {
        "local_datetime": datetime(2026, 10, 18, 23, 50, tzinfo=timezone.utc),
        "jalali_str": "یکشنبه، ۲۶ مهر ۱۴۰۵",
        "gregorian_str": "2026-10-18",
        "time_str": "23:50",
        "new_users": 15,
        "total_users": 1250,
        "new_khatms": 4,
        "active_khatms": 82,
        "total_khatms": 530,
        "quran_pages_today": 240,
        "salawat_today": 35000,
        "completed_portions_today": 195,
        "tickets_received_today": 3,
        "alerts_handled_today": 3,
        "pending_phone_requests": 0,
        "approved_phone_today": 2,
        "wallet_charge_today": 150000,
    }

    monkeypatch.setattr(
        "khatmsaz.modules.reporting.admin_daily_report.get_daily_admin_stats",
        AsyncMock(return_value=fake_stats),
    )

    text = await generate_daily_admin_report_text(AsyncMock())

    assert "گزارش روزانهٔ ختم‌ساز" in text
    assert "۲۶ مهر ۱۴۰۵" in text
    assert "کاربران جدید امروز: +15" in text
    assert "صفحات قرآن تلاوت‌شده: 240" in text
    assert "ذکر و صلوات ثبت‌شده: 35,000" in text
    assert "150,000 تومان" in text
    assert "خداقوت" in text


@pytest.mark.asyncio
async def test_admin_daily_report_command_authorization(monkeypatch):
    """Only admins with OPERATIONS_VIEW permission can run /admin_daily_report."""
    message = AsyncMock()
    message.bot.khatmsaz_platform = Platform.TELEGRAM

    # 1. Non-admin user -> denied silently
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.admin._require_admin",
        AsyncMock(return_value=False),
    )
    await admin_handler.admin_daily_report_cmd(message)
    assert not message.answer.called

    # 2. Authorized admin -> answers with report
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.admin._require_admin",
        AsyncMock(return_value=True),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.reporting.admin_daily_report.generate_daily_admin_report_text",
        AsyncMock(return_value="متن گزارش تستی"),
    )

    @asynccontextmanager
    async def fake_session_scope():
        yield AsyncMock()

    monkeypatch.setattr("khatmsaz.bot.handlers.admin.session_scope", fake_session_scope)

    await admin_handler.admin_daily_report_cmd(message)
    message.answer.assert_called_once_with("متن گزارش تستی", parse_mode="HTML")


@pytest.mark.asyncio
async def test_notify_new_admin_appointed(monkeypatch):
    """notify_new_admin_appointed delivers warm Persian welcome message to user's Telegram identity."""
    from khatmsaz.bot.admin_sync import notify_new_admin_appointed
    from khatmsaz.modules.identity.models import Platform, PlatformIdentity

    fake_user_id = uuid.uuid4()
    fake_identities = [
        PlatformIdentity(user_id=fake_user_id, platform=Platform.TELEGRAM, subject="555444333")
    ]

    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.list_identities_for_user",
        AsyncMock(return_value=fake_identities),
    )

    bot = AsyncMock()
    session = AsyncMock()

    sent = await notify_new_admin_appointed(session, fake_user_id, bot=bot)

    assert sent is True
    bot.send_message.assert_called_once()
    call_args = bot.send_message.call_args
    assert call_args.kwargs["chat_id"] == 555444333
    assert "مدیر (ادمین)" in call_args.kwargs["text"]
    assert "گزارش‌های روزانه" in call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_bot_panel_admin_role_toggle_authorization(monkeypatch):
    """Only SUPER_ADMIN can grant/revoke roles in bot panel; normal admin receives warning alert."""
    from khatmsaz.bot.handlers.panel import handle_admin_role_toggle
    from khatmsaz.modules.identity.models import User, UserRole

    target_id = uuid.uuid4()
    callback = AsyncMock()
    callback.data = f"admin_role:toggle:{target_id}:grant"
    callback.from_user.id = 999888
    callback.bot.khatmsaz_platform = Platform.TELEGRAM

    # 1. Non-super admin actor (normal ADMIN or USER) -> denied
    regular_admin = User(id=uuid.uuid4(), display_name="مدیر عادی", role=UserRole.USER)
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.panel._get_context",
        AsyncMock(return_value=(regular_admin, "fa")),
    )
    await handle_admin_role_toggle(callback)
    callback.answer.assert_called_once()
    assert "فقط مدیر کل (سوپرادمین)" in callback.answer.call_args.args[0]
    assert callback.answer.call_args.kwargs["show_alert"] is True

    # 2. Super admin actor -> granted, audit logged, and notified
    super_admin = User(id=uuid.uuid4(), display_name="مدیر ارشد", role=UserRole.SUPER_ADMIN)
    target_user = User(id=target_id, display_name="کاربر هدف", role=UserRole.USER)

    monkeypatch.setattr(
        "khatmsaz.bot.handlers.panel._get_context",
        AsyncMock(return_value=(super_admin, "fa")),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.find_by_id",
        AsyncMock(side_effect=lambda s, uid: super_admin if uid == super_admin.id else target_user),
    )
    grant_mock = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.authorization.service.grant_role", grant_mock)
    audit_mock = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", audit_mock)
    notify_mock = AsyncMock(return_value=True)
    monkeypatch.setattr("khatmsaz.bot.handlers.panel.notify_new_admin_appointed", notify_mock)

    @asynccontextmanager
    async def fake_session_scope():
        yield AsyncMock()

    monkeypatch.setattr("khatmsaz.bot.handlers.panel.session_scope", fake_session_scope)

    callback.message.reply_markup.inline_keyboard = [
        [
            InlineKeyboardButton(
                text="⭐️ مدیر کردن: کاربر هدف",
                callback_data=f"admin_role:toggle:{target_id}:grant",
            )
        ]
    ]

    await handle_admin_role_toggle(callback)

    grant_mock.assert_called_once()
    audit_mock.assert_called_once()
    notify_mock.assert_called_once()
    # Check that reply markup was edited to flip button to revoke
    callback.message.edit_reply_markup.assert_called_once()
    new_kb = callback.message.edit_reply_markup.call_args.kwargs["reply_markup"]
    assert new_kb.inline_keyboard[0][0].callback_data == f"admin_role:toggle:{target_id}:revoke"
    assert "لغو مدیر" in new_kb.inline_keyboard[0][0].text


@pytest.mark.asyncio
async def test_bot_panel_search_user_and_render_cards(monkeypatch):
    """Admin user search query finds users and renders interactive cards with role toggle buttons."""
    from khatmsaz.bot.handlers.panel import handle_admin_user_search_query
    from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole

    target_user = User(
        id=uuid.uuid4(),
        display_name="حسین علوی",
        role=UserRole.USER,
        platform_identities=[
            PlatformIdentity(platform=Platform.TELEGRAM, subject="777888999")
        ],
    )
    actor_user = User(id=uuid.uuid4(), display_name="مدیر کل", role=UserRole.SUPER_ADMIN)

    message = AsyncMock()
    message.text = "777888999"
    message.chat.id = 111222
    message.bot.khatmsaz_platform = Platform.TELEGRAM
    state = AsyncMock()

    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.find_by_platform",
        AsyncMock(return_value=actor_user),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.search_users",
        AsyncMock(return_value=[target_user]),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.authorization.service.list_roles",
        AsyncMock(return_value=[]),
    )

    @asynccontextmanager
    async def fake_session_scope():
        session = AsyncMock()
        session.execute = AsyncMock(return_value=MagicMock(scalars=lambda: MagicMock(all=lambda: [])))
        yield session

    monkeypatch.setattr("khatmsaz.bot.handlers.panel.session_scope", fake_session_scope)

    await handle_admin_user_search_query(message, state)

    state.clear.assert_called_once()
    message.answer.assert_called_once()
    ans_text, ans_kwargs = message.answer.call_args.args[0], message.answer.call_args.kwargs
    assert "حسین علوی" in ans_text
    assert "777888999" in ans_text
    kb = ans_kwargs["reply_markup"]
    assert any(btn.callback_data == f"admin_role:toggle:{target_user.id}:grant" for row in kb.inline_keyboard for btn in row)


@pytest.mark.asyncio
async def test_search_users_query_construction():
    """search_users constructs query matching subject with/without @, phone, name, or returns recent."""
    from khatmsaz.modules.identity.repository import search_users

    session = AsyncMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=lambda: []))

    # 1. Empty query (returns recent users)
    await search_users(session, "")
    stmt1 = session.execute.call_args.args[0]
    compiled1 = str(stmt1)
    assert "users.created_at DESC" in compiled1

    # 2. Query with @ (e.g. @12345678)
    await search_users(session, "@12345678")
    stmt2 = session.execute.call_args.args[0]
    compiled2 = str(stmt2)
    assert "platform_identities" in compiled2
    assert "user_settings" in compiled2


