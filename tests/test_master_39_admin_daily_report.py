"""Tests for MASTER-39: Admin Daily Analytics & Trend Comparison Report."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from khatmsaz.bot.handlers.admin_bot.handlers import admin_daily_report_handler, _build_dashboard_keyboard
from khatmsaz.modules.reporting.admin_daily_report import (
    AdminDailyReportData,
    build_admin_daily_report_keyboard,
    build_admin_daily_report_text,
    calc_trend,
    format_persian_date,
    get_admin_daily_report_data,
    send_daily_admin_report,
    to_persian_digits,
)


def _fake_session_scope():
    mock_session = AsyncMock()
    mock_scope = MagicMock()
    mock_scope.__aenter__ = AsyncMock(return_value=mock_session)
    mock_scope.__aexit__ = AsyncMock(return_value=None)
    return mock_scope, mock_session


# --- 1. Trend Calculation & Helpers ---

def test_calc_trend_scenarios():
    # 0 vs 0
    icon, text = calc_trend(0, 0)
    assert icon == "➡️"
    assert "بدون تغییر" in text

    # New records from 0
    icon, text = calc_trend(5, 0)
    assert icon == "↗️"
    assert "رکورد جدید" in text

    # Positive growth
    icon, text = calc_trend(15, 10)
    assert icon == "↗️"
    assert "صعودی" in text
    assert "۵۰" in text  # 50%

    # Negative decline
    icon, text = calc_trend(5, 10)
    assert icon == "↘️"
    assert "کاهشی" in text
    assert "۵۰" in text  # -50%

    # Flat
    icon, text = calc_trend(10, 10)
    assert icon == "➡️"
    assert "ثابت" in text


def test_persian_formatting():
    assert to_persian_digits(12345) == "۱۲۳۴۵"
    dt = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)
    formatted = format_persian_date(dt)
    assert "مهر" in formatted or "۱۴۰۵" in formatted


# --- 2. Report Text Formatting ---

def test_build_admin_daily_report_text():
    data = AdminDailyReportData(
        generated_at_local=datetime(2026, 10, 17, 15, 30),
        persian_date_str="شنبه ۲۵ مهر ۱۴۰۵",
        time_str="۱۵:۳۰",
        khatms_today=3,
        khatms_yesterday=1,
        total_khatms=25,
        active_khatms=20,
        parts_today=5,
        parts_yesterday=2,
        active_parts=45,
        readings_today=15,
        readings_yesterday=10,
        users_today=8,
        users_yesterday=4,
        total_users=100,
        active_users_today=14,
        active_users_yesterday=9,
        top_khatm_today=("ختم خطبه فدکیه", 4),
        top_khatms_overall=[("ختم صلوات", 15), ("ختم زیارت عاشورا", 10)],
    )

    text = build_admin_daily_report_text(data)

    # Header
    assert "گزارش تحلیلی روزانه مدیریت ختم‌ساز" in text
    assert "شنبه ۲۵ مهر ۱۴۰۵" in text

    # Khatms section
    assert "وضعیت ختم‌ها" in text
    assert "۳ ختم" in text
    assert "۱ ختم" in text
    assert "صعودی" in text

    # Participations & Readings
    assert "وضعیت شراکت‌ها و قرائت‌ها" in text
    assert "۴۵ شراکت" in text

    # Users & DAU
    assert "کاربران فعال امروز (DAU)" in text
    assert "۱۴ نفر" in text
    assert "۹ نفر" in text

    # Top Khatm Today
    assert "ختم خطبه فدکیه" in text
    assert "۴" in text

    # Top Overall Khatms
    assert "ختم صلوات" in text
    assert "ختم زیارت عاشورا" in text


# --- 3. Dashboard Keyboard Button ---

def test_dashboard_keyboard_has_daily_report_button():
    counts = {
        "pending_receipts": 0,
        "pending_laan": 0,
        "pending_broadcasts": 0,
        "pending_transfers": 0,
        "active_khatms": 5,
        "total_users": 50,
    }
    kb = _build_dashboard_keyboard(counts)
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    texts = [btn.text for row in kb.inline_keyboard for btn in row]

    assert "admin:daily_report" in callbacks
    idx = callbacks.index("admin:daily_report")
    assert "گزارش تحلیلی روزانه" in texts[idx]


# --- 4. Handler Invocations & Permissions ---

@pytest.mark.asyncio
async def test_admin_daily_report_handler_unauthorized():
    mock_msg = AsyncMock()
    mock_msg.from_user.id = 999999
    
    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=False)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers._reject_unauthorized", new=AsyncMock()) as mock_reject:
        await admin_daily_report_handler(mock_msg)
        mock_reject.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_daily_report_handler_authorized():
    mock_msg = AsyncMock()
    mock_msg.data = None
    mock_msg.from_user.id = 123456

    scope, mock_sess = _fake_session_scope()
    fake_data = AdminDailyReportData(
        generated_at_local=datetime(2026, 10, 17, 15, 30),
        persian_date_str="شنبه ۲۵ مهر ۱۴۰۵",
        time_str="۱۵:۳۰",
        khatms_today=2,
        khatms_yesterday=1,
        total_khatms=20,
        active_khatms=18,
        parts_today=3,
        parts_yesterday=2,
        active_parts=40,
        readings_today=10,
        readings_yesterday=8,
        users_today=5,
        users_yesterday=3,
        total_users=90,
        active_users_today=12,
        active_users_yesterday=8,
        top_khatm_today=("ختم تست", 2),
        top_khatms_overall=[("ختم برتر", 10)],
    )

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope", return_value=scope), \
         patch("khatmsaz.modules.reporting.admin_daily_report.get_admin_daily_report_data", new=AsyncMock(return_value=fake_data)):

        await admin_daily_report_handler(mock_msg)

        mock_msg.answer.assert_awaited_once()
        text_sent = mock_msg.answer.call_args[0][0]
        markup = mock_msg.answer.call_args.kwargs.get("reply_markup")

        assert "گزارش تحلیلی روزانه مدیریت ختم‌ساز" in text_sent
        assert "ختم برتر" in text_sent
        assert markup is not None
        callbacks = [btn.callback_data for row in markup.inline_keyboard for btn in row]
        assert "admin:daily_report_refresh" in callbacks
        assert "admin:refresh" in callbacks


@pytest.mark.asyncio
async def test_admin_daily_report_callback_refresh():
    mock_cb = AsyncMock()
    mock_cb.data = "admin:daily_report_refresh"
    mock_cb.from_user.id = 123456
    mock_msg = AsyncMock()
    mock_cb.message = mock_msg

    scope, mock_sess = _fake_session_scope()
    fake_data = AdminDailyReportData(
        generated_at_local=datetime(2026, 10, 17, 15, 30),
        persian_date_str="شنبه ۲۵ مهر ۱۴۰۵",
        time_str="۱۵:۳۰",
        khatms_today=2,
        khatms_yesterday=1,
        total_khatms=20,
        active_khatms=18,
        parts_today=3,
        parts_yesterday=2,
        active_parts=40,
        readings_today=10,
        readings_yesterday=8,
        users_today=5,
        users_yesterday=3,
        total_users=90,
        active_users_today=12,
        active_users_yesterday=8,
        top_khatm_today=None,
        top_khatms_overall=[],
    )

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope", return_value=scope), \
         patch("khatmsaz.modules.reporting.admin_daily_report.get_admin_daily_report_data", new=AsyncMock(return_value=fake_data)):

        await admin_daily_report_handler(mock_cb)

        mock_msg.edit_text.assert_awaited_once()
        mock_cb.answer.assert_awaited_once_with("گزارش روزانه بروزرسانی شد ✅")


# --- 5. Scheduled Daily Dispatch ---

@pytest.mark.asyncio
async def test_send_daily_admin_report_dispatches():
    fake_data = AdminDailyReportData(
        generated_at_local=datetime(2026, 10, 17, 23, 45),
        persian_date_str="شنبه ۲۵ مهر ۱۴۰۵",
        time_str="۲۳:۴۵",
        khatms_today=4,
        khatms_yesterday=2,
        total_khatms=20,
        active_khatms=18,
        parts_today=5,
        parts_yesterday=3,
        active_parts=50,
        readings_today=20,
        readings_yesterday=15,
        users_today=10,
        users_yesterday=5,
        total_users=100,
        active_users_today=15,
        active_users_yesterday=10,
        top_khatm_today=("ختم عاشورا", 5),
        top_khatms_overall=[],
    )

    scope, mock_sess = _fake_session_scope()
    with patch("khatmsaz.modules.reporting.admin_daily_report.session_scope", return_value=scope), \
         patch("khatmsaz.modules.reporting.admin_daily_report.get_admin_daily_report_data", new=AsyncMock(return_value=fake_data)), \
         patch("khatmsaz.modules.reporting.admin_daily_report.notify_super_admins", new=AsyncMock()) as mock_notify:

        await send_daily_admin_report()

        mock_notify.assert_awaited_once()
        call_args = mock_notify.call_args
        text_arg = call_args[0][0]
        assert "گزارش تحلیلی روزانه مدیریت ختم‌ساز" in text_arg
        assert "ختم عاشورا" in text_arg


# --- 6. Direct Service Query Assembly ---

@pytest.mark.asyncio
async def test_get_admin_daily_report_data_assembly():
    mock_session = AsyncMock()
    # Mock execute results
    mock_result_scalar = MagicMock()
    mock_result_scalar.scalar.return_value = 5
    mock_result_first = MagicMock()
    mock_result_first.first.return_value = ("ختم الغدیر", 12)
    mock_result_all = MagicMock()
    mock_result_all.all.return_value = [("ختم قرآن", 50), ("ختم صلوات", 30)]

    mock_session.execute.side_effect = [
        mock_result_scalar,  # total_khatms
        mock_result_scalar,  # active_khatms
        mock_result_scalar,  # khatms_today
        mock_result_scalar,  # khatms_yesterday
        mock_result_scalar,  # total_users
        mock_result_scalar,  # users_today
        mock_result_scalar,  # users_yesterday
        mock_result_scalar,  # parts_today
        mock_result_scalar,  # parts_yesterday
        mock_result_scalar,  # active_parts
        mock_result_scalar,  # occ_today
        mock_result_scalar,  # occ_yesterday
        mock_result_scalar,  # open_contrib_today
        mock_result_scalar,  # open_contrib_yesterday
        mock_result_scalar,  # portion_today
        mock_result_scalar,  # portion_yesterday
        mock_result_scalar,  # active_users_today
        mock_result_scalar,  # active_users_yesterday
        mock_result_first,   # top_today_stmt
        mock_result_all,     # top_khatms_stmt
    ]

    now_test = datetime(2026, 10, 17, 14, 0, tzinfo=timezone.utc)
    data = await get_admin_daily_report_data(mock_session, now_dt=now_test)

    assert data.total_khatms == 5
    assert data.top_khatm_today == ("ختم الغدیر", 12)
    assert len(data.top_khatms_overall) == 2
    assert data.top_khatms_overall[0] == ("ختم قرآن", 50)
