"""Tests for MASTER-38: Creator Broadcast & Wallet Recharge Overhaul."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, User as TgUser

from khatmsaz.bot.handlers.creator_broadcast import (
    CreatorBroadcastFlow,
    start_broadcast_for_khatm,
    choose_broadcast_target,
    recheck_broadcast_wallet,
    confirm_broadcast,
)
from khatmsaz.bot.keyboards import (
    creator_khatm_keyboard,
    wallet_recharge_packages_keyboard,
)
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.khatm.models import KhatmStatus
from khatmsaz.modules.system_settings import service as system_settings_service


# --- 1. Keyboard Structure & Buttons ---

def test_creator_khatm_keyboard_has_broadcast_button():
    """`creator_khatm_keyboard` MUST include [ 📢 ارسال پیام گروهی ] with cbroadcast_khatm:{khatm_id}."""
    khatm_id = str(uuid.uuid4())
    kb = creator_khatm_keyboard(khatm_id, can_cancel=False, transfer_status="NONE", lang="fa")
    
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    
    expected_cb = f"cbroadcast_khatm:{khatm_id}"
    assert expected_cb in callbacks
    idx = callbacks.index(expected_cb)
    assert "ارسال پیام گروهی" in texts[idx]


def test_wallet_recharge_packages_keyboard_options():
    """Wallet recharge packages keyboard MUST strictly contain 50k, 100k, 500k, and custom amount."""
    kb = wallet_recharge_packages_keyboard(lang="fa", back_callback="test_back", recheck_callback="test_recheck")
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    texts = [btn.text for row in kb.inline_keyboard for btn in row]

    assert "wallet_topup:50000" in callbacks
    assert "wallet_topup:100000" in callbacks
    assert "wallet_topup:500000" in callbacks
    assert "wallet_topup_custom" in callbacks
    assert "wallet:receipt_upload" in callbacks
    assert "test_recheck" in callbacks
    assert "test_back" in callbacks

    # Check Persian labels
    assert any("۵۰,۰۰۰" in t for t in texts)
    assert any("۱۰۰,۰۰۰" in t for t in texts)
    assert any("۵۰۰,۰۰۰" in t for t in texts)
    assert any("مبلغ دلخواه" in t for t in texts)


# --- 2. Per-Message Pricing & System Settings ---

@pytest.mark.asyncio
async def test_per_message_price_defaults_to_150():
    """Per-message price default is 150 Tomans per recipient."""
    mock_session = AsyncMock()
    with patch("khatmsaz.modules.system_settings.service.get_int", new=AsyncMock(return_value=150)):
        price_tg = await broadcast_service.per_message_price(mock_session, "TELEGRAM")
        price_bale = await broadcast_service.per_message_price(mock_session, "BALE")
        assert price_tg == 150
        assert price_bale == 150


@pytest.mark.asyncio
async def test_broadcast_submit_with_cost_override():
    """`broadcast_service.submit` accepts cost_override and spends exact amount."""
    mock_session = AsyncMock()
    creator_id = uuid.uuid4()
    audience = [uuid.uuid4() for _ in range(14)]

    with patch("khatmsaz.modules.broadcast.service.audience_user_ids", new=AsyncMock(return_value=audience)), \
         patch("khatmsaz.modules.wallet.service.spend", new=AsyncMock(return_value=MagicMock(id=uuid.uuid4()))) as mock_spend, \
         patch("khatmsaz.modules.broadcast.repository.create", new=AsyncMock(return_value=MagicMock(id=uuid.uuid4(), cost_toman=2100, audience_count=14))):

        # 14 recipients * 150 tomans = 2,100 tomans
        item = await broadcast_service.submit(
            mock_session,
            khatm_id=None,
            creator_user_id=creator_id,
            body="پیام تستی ۱۴ نفره",
            channel="TELEGRAM",
            cost_override=2100,
        )

        mock_spend.assert_awaited_once()
        assert mock_spend.call_args.kwargs["amount"] == 2100
        assert "14 مخاطب فعال" in mock_spend.call_args.kwargs["description"]


# --- 3. Khatm Direct Broadcast Flow (`cbroadcast_khatm`) ---

@pytest.mark.asyncio
async def test_start_broadcast_for_khatm_insufficient_funds():
    """When wallet balance is insufficient, displays 150 Tomans rate and top-up packages."""
    khatm_id = uuid.uuid4()
    creator_id = uuid.uuid4()
    mock_user = MagicMock(id=creator_id)
    mock_khatm = MagicMock(id=khatm_id, title="ختم صلوات حاجت", creator_user_id=creator_id, status=KhatmStatus.ACTIVE)

    mock_bot = AsyncMock()
    mock_bot.khatmsaz_platform = Platform.TELEGRAM

    mock_msg = AsyncMock()
    mock_msg.chat.id = 123456

    mock_cb = AsyncMock()
    mock_cb.data = f"cbroadcast_khatm:{khatm_id}"
    mock_cb.bot = mock_bot
    mock_cb.message = mock_msg

    storage = MemoryStorage()
    state = FSMContext(storage=storage, key=MagicMock())

    with patch("khatmsaz.bot.handlers.creator_broadcast.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=mock_user)), \
         patch("khatmsaz.bot.handlers.creator_broadcast.khatm_service.get_khatm", new=AsyncMock(return_value=mock_khatm)), \
         patch("khatmsaz.bot.handlers.creator_broadcast.broadcast_service.audience_user_ids", new=AsyncMock(return_value=[uuid.uuid4() for _ in range(14)])), \
         patch("khatmsaz.bot.handlers.creator_broadcast.broadcast_service.per_message_price", new=AsyncMock(return_value=150)), \
         patch("khatmsaz.bot.handlers.creator_broadcast.wallet_service.get_balances", new=AsyncMock(return_value=(0, 0))):

        await start_broadcast_for_khatm(mock_cb, state)

        # 14 audience * 150 = 2,100 toman. Balance = 0 -> shows insufficient funds and recharge packages
        mock_msg.answer.assert_awaited_once()
        text_sent = mock_msg.answer.call_args[0][0]
        reply_markup = mock_msg.answer.call_args.kwargs.get("reply_markup")

        assert "۱۴ نفر" in text_sent or "14 نفر" in text_sent
        assert "۱۵۰ تومان" in text_sent or "150 تومان" in text_sent
        assert "۲,۱۰۰ تومان" in text_sent or "2,100 تومان" in text_sent
        assert "موجودی کیف پول شما برای ارسال این پیام گروهی کافی نیست" in text_sent

        # Check recharge buttons in markup
        callbacks = [btn.callback_data for row in reply_markup.inline_keyboard for btn in row]
        assert "wallet_topup:50000" in callbacks
        assert "wallet_topup:100000" in callbacks
        assert "wallet_topup:500000" in callbacks
        assert "wallet_topup_custom" in callbacks


@pytest.mark.asyncio
async def test_start_broadcast_for_khatm_sufficient_funds():
    """When wallet balance is sufficient, transitions to entering message."""
    khatm_id = uuid.uuid4()
    creator_id = uuid.uuid4()
    mock_user = MagicMock(id=creator_id)
    mock_khatm = MagicMock(id=khatm_id, title="ختم عاشورا", creator_user_id=creator_id, status=KhatmStatus.ACTIVE)

    mock_bot = AsyncMock()
    mock_bot.khatmsaz_platform = Platform.TELEGRAM
    mock_msg = AsyncMock()
    mock_msg.chat.id = 123456
    mock_cb = AsyncMock()
    mock_cb.data = f"cbroadcast_khatm:{khatm_id}"
    mock_cb.bot = mock_bot
    mock_cb.message = mock_msg

    storage = MemoryStorage()
    state = FSMContext(storage=storage, key=MagicMock())

    with patch("khatmsaz.bot.handlers.creator_broadcast.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=mock_user)), \
         patch("khatmsaz.bot.handlers.creator_broadcast.khatm_service.get_khatm", new=AsyncMock(return_value=mock_khatm)), \
         patch("khatmsaz.bot.handlers.creator_broadcast.broadcast_service.audience_user_ids", new=AsyncMock(return_value=[uuid.uuid4() for _ in range(14)])), \
         patch("khatmsaz.bot.handlers.creator_broadcast.broadcast_service.per_message_price", new=AsyncMock(return_value=150)), \
         patch("khatmsaz.bot.handlers.creator_broadcast.wallet_service.get_balances", new=AsyncMock(return_value=(50_000, 0))):

        await start_broadcast_for_khatm(mock_cb, state)

        mock_msg.answer.assert_awaited_once()
        text_sent = mock_msg.answer.call_args[0][0]
        assert "لطفاً متن، عکس، فیلم یا فایل خود را ارسال کنید" in text_sent

        current_state = await state.get_state()
        assert current_state == CreatorBroadcastFlow.entering_message.state


# --- 4. Wallet Recheck Callback ---

@pytest.mark.asyncio
async def test_recheck_broadcast_wallet_transition_when_funded():
    """`cbroadcast_recheck` transitions user to entering_message once wallet is funded."""
    creator_id = uuid.uuid4()
    storage = MemoryStorage()
    state = FSMContext(storage=storage, key=MagicMock())
    await state.update_data(
        creator_id=str(creator_id),
        total_cost=2100,
        target_title="ختم صلوات",
    )

    mock_msg = AsyncMock()
    mock_cb = AsyncMock()
    mock_cb.message = mock_msg

    # Now balance is 10,000 (> 2,100)
    with patch("khatmsaz.bot.handlers.creator_broadcast.wallet_service.get_balances", new=AsyncMock(return_value=(10_000, 0))):
        await recheck_broadcast_wallet(mock_cb, state)

        mock_msg.answer.assert_awaited_once()
        text_sent = mock_msg.answer.call_args[0][0]
        assert "موجودی کیف پول شما با موفقیت تأیید شد" in text_sent

        current_state = await state.get_state()
        assert current_state == CreatorBroadcastFlow.entering_message.state
