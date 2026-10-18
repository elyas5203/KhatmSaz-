"""Coverage for Admin Promotion and Management in Web Panel and Dedicated Admin Bot."""

import pytest
import uuid
from unittest.mock import AsyncMock, patch

from aiogram.types import InlineKeyboardMarkup, Message, User as TgUser

from khatmsaz.bot.handlers.admin_bot.handlers import (
    _build_dashboard_keyboard,
    _execute_add_admin,
    _execute_remove_admin,
    _get_all_super_admins_data,
    _normalize_phone_input,
)
from khatmsaz.core.db import get_engine, session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole
from khatmsaz.modules.phone.models import PhoneClaim
from khatmsaz.modules.settings.models import UserSettings


@pytest.fixture(autouse=True)
async def dispose_engine_after_test():
    """Ensure asyncpg connection pool is disposed so connections don't cross event loops."""
    await get_engine().dispose()
    yield
    await get_engine().dispose()


def test_dashboard_keyboard_contains_manage_admins():
    counts = {
        "pending_receipts": 0,
        "pending_laan": 0,
        "pending_broadcasts": 0,
        "pending_transfers": 0,
    }
    kb = _build_dashboard_keyboard(counts)
    assert isinstance(kb, InlineKeyboardMarkup)
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row if btn.callback_data]
    assert "admin:manage_admins" in callbacks


def test_normalize_phone_input():
    assert _normalize_phone_input("09123456789") == "+989123456789"
    assert _normalize_phone_input("+989123456789") == "+989123456789"
    assert _normalize_phone_input(" 0933-680-7599 ") == "+989336807599"


@pytest.mark.asyncio
async def test_get_all_super_admins_data_returns_admins():
    u_id = new_id()
    rand_subj = f"test_{uuid.uuid4().hex[:8]}"
    async with session_scope() as session:
        admin_user = User(id=u_id, role=UserRole.SUPER_ADMIN, display_name="تست سوپرادمین")
        ident = PlatformIdentity(id=new_id(), user_id=u_id, platform=Platform.TELEGRAM, subject=rand_subj)
        session.add_all([admin_user, ident])
        await session.commit()

    try:
        async with session_scope() as session:
            data = await _get_all_super_admins_data(session)
            matching = [d for d in data if d["id"] == u_id]
            assert len(matching) == 1
            assert rand_subj in matching[0]["telegram_ids"]
            assert matching[0]["display_name"] == "تست سوپرادمین"
    finally:
        async with session_scope() as session:
            ident_row = await session.get(PlatformIdentity, ident.id)
            if ident_row:
                await session.delete(ident_row)
                await session.flush()
            admin_row = await session.get(User, u_id)
            if admin_row:
                await session.delete(admin_row)
            await session.commit()


@pytest.mark.asyncio
async def test_execute_add_admin_by_telegram_chat_id():
    mock_msg = AsyncMock(spec=Message)
    mock_msg.from_user = TgUser(id=5490508090, is_bot=False, first_name="Admin")
    mock_msg.answer = AsyncMock()

    rand_int = uuid.uuid4().int % 90000000 + 10000000
    target_chat_id = str(rand_int)

    with patch("khatmsaz.bot.handlers.admin_bot.handlers.audit_service.record", new_callable=AsyncMock), \
         patch("khatmsaz.bot.notify_adapter.send_with_keyboard", new_callable=AsyncMock):
        await _execute_add_admin(mock_msg, target_chat_id)

    assert mock_msg.answer.called
    reply_text = mock_msg.answer.call_args[0][0]
    assert "با موفقیت به عنوان مدیر کل (Super Admin) ثبت شد" in reply_text

    async with session_scope() as session:
        from sqlalchemy import select
        user = await session.execute(
            PlatformIdentity.__table__.select().where(PlatformIdentity.subject == target_chat_id)
        )
        row = user.first()
        assert row is not None
        user_row = await session.get(User, row.user_id)
        assert user_row.role == UserRole.SUPER_ADMIN

        # Cleanup
        settings_rows = (await session.execute(
            select(UserSettings).where(UserSettings.user_id == row.user_id)
        )).scalars().all()
        for s in settings_rows:
            await session.delete(s)
        pi = await session.get(PlatformIdentity, row.id)
        if pi:
            await session.delete(pi)
        await session.flush()
        await session.delete(user_row)
        await session.commit()


@pytest.mark.asyncio
async def test_execute_add_and_remove_admin_by_phone():
    rand_phone_tail = f"{uuid.uuid4().int % 9000000 + 1000000:07d}"
    target_phone = f"+9891{rand_phone_tail}"
    input_phone = f"091{rand_phone_tail}"
    u_id = new_id()
    phone_claim_id = new_id()

    async with session_scope() as session:
        normal_user = User(id=u_id, role=UserRole.USER, display_name="کاربر تستی")
        phone_claim = PhoneClaim(id=phone_claim_id, user_id=u_id, e164=target_phone)
        session.add_all([normal_user, phone_claim])
        await session.commit()

    try:
        mock_msg = AsyncMock(spec=Message)
        mock_msg.from_user = TgUser(id=5490508090, is_bot=False, first_name="Admin")
        mock_msg.answer = AsyncMock()

        with patch("khatmsaz.bot.handlers.admin_bot.handlers.audit_service.record", new_callable=AsyncMock):
            # Promote by phone
            await _execute_add_admin(mock_msg, input_phone)
            assert "با موفقیت به عنوان مدیر کل (Super Admin) ثبت شد" in mock_msg.answer.call_args[0][0]

            async with session_scope() as session:
                refreshed = await session.get(User, u_id)
                assert refreshed.role == UserRole.SUPER_ADMIN

            # Demote by phone
            await _execute_remove_admin(mock_msg, input_phone)
            assert "دسترسی مدیریت کل کاربر لغو شد" in mock_msg.answer.call_args[0][0]

            async with session_scope() as session:
                refreshed = await session.get(User, u_id)
                assert refreshed.role == UserRole.CREATOR
    finally:
        async with session_scope() as session:
            pc = await session.get(PhoneClaim, phone_claim_id)
            if pc:
                await session.delete(pc)
                await session.flush()
            refreshed = await session.get(User, u_id)
            if refreshed:
                await session.delete(refreshed)
            await session.commit()
