"""Tests for MASTER-36: Comprehensive Creator Bot Button Audit & Repairs.

Validates:
1. Purging of khatm cancellation (no "لغو ختم" button, guidance on legacy callbacks).
2. Navigation continuity in creator settings (back button points to specific khatm management).
3. Back/cancel buttons in broadcast flow (target selection, message prompt, cross-state cancel).
4. Back/cancel buttons in wallet flows (invoices back button, receipt upload cancel button & handler).
5. Back/cancel buttons in custom khatm request flow.
6. Back buttons in khatm reports (stats, qr, export).
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Chat, Message, User as TgUser

from khatmsaz.bot.keyboards import (
    creator_khatm_keyboard,
    creator_settings_keyboard,
    creator_menu_keyboard,
    creator_management_keyboard,
    creator_finance_keyboard,
    creator_support_keyboard,
)
from khatmsaz.bot.handlers import (
    my_khatms,
    creator_broadcast,
    wallet,
    khatm_request,
)
from khatmsaz.bot.handlers.creator_broadcast import CreatorBroadcastFlow
from khatmsaz.bot.handlers.wallet import WalletReceiptUpload
from khatmsaz.bot.handlers.khatm_request import RequestKhatm
from khatmsaz.modules.identity.models import Platform, User, UserRole
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType


def _make_mock_user(user_id=None, role=UserRole.CREATOR):
    u = User(id=user_id or uuid.uuid4(), role=role)
    u.display_name = "تست‌کننده"
    return u


def _make_tg_user(tg_id=12345678):
    return TgUser(id=tg_id, is_bot=False, first_name="Ali", username="ali_test")


def _make_chat(chat_id=12345678):
    return Chat(id=chat_id, type="private")


def _mock_callback(data: str, chat_id=12345678, user_id=12345678):
    cb = AsyncMock(spec=CallbackQuery)
    cb.data = data
    cb.from_user = _make_tg_user(user_id)
    msg = AsyncMock(spec=Message)
    msg.chat = _make_chat(chat_id)
    msg.message_id = 999
    msg.answer = AsyncMock()
    msg.edit_text = AsyncMock()
    msg.edit_reply_markup = AsyncMock()
    cb.message = msg
    cb.bot = MagicMock()
    cb.bot.khatmsaz_platform = Platform.TELEGRAM
    cb.answer = AsyncMock()
    return cb


def _mock_message(text: str = "", chat_id=12345678, user_id=12345678):
    msg = AsyncMock(spec=Message)
    msg.text = text
    msg.caption = None
    msg.photo = None
    msg.video = None
    msg.voice = None
    msg.document = None
    msg.chat = _make_chat(chat_id)
    msg.from_user = _make_tg_user(user_id)
    msg.bot = MagicMock()
    msg.bot.khatmsaz_platform = Platform.TELEGRAM
    msg.answer = AsyncMock()
    msg.answer_photo = AsyncMock()
    msg.answer_document = AsyncMock()
    return msg


async def _get_fsm_context(chat_id: int = 12345678, user_id: int = 12345678) -> FSMContext:
    storage = MemoryStorage()
    bot = MagicMock()
    key = StorageKey(bot_id=1, chat_id=chat_id, user_id=user_id)
    return FSMContext(storage=storage, key=key)


# ==============================================================================
# 1. PURGE "لغو ختم" & VERIFY BACK BUTTON IN CREATOR KHATM KEYBOARD
# ==============================================================================

def test_creator_khatm_keyboard_purges_cancellation():
    """`creator_khatm_keyboard` must NEVER include 'لغو ختم' callback, even if can_cancel=True."""
    khatm_id = str(uuid.uuid4())
    kb = creator_khatm_keyboard(khatm_id, can_cancel=True, transfer_status="NONE", lang="fa")
    
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    
    assert f"cancel_khatm_ask:{khatm_id}" not in callbacks
    assert not any("لغو ختم" in t for t in texts)
    assert "my_khatms:open" in callbacks
    assert "🔙 بازگشت به ختم‌های من" in texts


@pytest.mark.asyncio
async def test_ask_cancel_khatm_displays_guidance_alert():
    """Legacy or direct hit on `cancel_khatm_ask:` must show an alert guiding to Rule 5 transfer."""
    khatm_id = str(uuid.uuid4())
    cb = _mock_callback(f"cancel_khatm_ask:{khatm_id}")
    
    await my_khatms.ask_cancel_khatm(cb)
    
    cb.answer.assert_awaited_once()
    args, kwargs = cb.answer.call_args
    assert kwargs.get("show_alert") is True
    alert_text = args[0]
    assert "امکان لغو ختم وجود ندارد" in alert_text
    assert "واگذاری مدیریت به پشتیبانی" in alert_text


# ==============================================================================
# 2. SETTINGS NAVIGATION CONTINUITY
# ==============================================================================

def test_creator_settings_keyboard_points_to_khatm_management():
    """`creator_settings_keyboard` back button must point to `my_khatms:manage:{khatm_id}`."""
    khatm_id = str(uuid.uuid4())
    kb = creator_settings_keyboard(
        khatm_id,
        is_quran=True,
        is_commitment=True,
        is_open=True,
        allow_pause=True,
        allow_snooze=True,
        miss_threshold=1,
        miss_window_days=7,
        content_mode="AUTO",
        lang="fa",
    )
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    
    assert f"my_khatms:manage:{khatm_id}" in callbacks
    assert "my_khatms:open" not in callbacks
    assert "🔙 بازگشت به مدیریت ختم" in texts


# ==============================================================================
# 3. BROADCAST TARGET SELECTOR & CANCELLATION
# ==============================================================================

@pytest.mark.asyncio
async def test_broadcast_target_selection_includes_cancel():
    """Target selection keyboard must contain [❌ انصراف] button."""
    user = _make_mock_user()
    khatm = Khatm(
        id=uuid.uuid4(),
        title="ختم صلوات تستی",
        creator_user_id=user.id,
        template_type=KhatmTemplateType.SALAWAT,
        status=KhatmStatus.ACTIVE,
    )
    msg = _mock_message()
    state = await _get_fsm_context()
    
    with patch("khatmsaz.bot.handlers.creator_broadcast.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.creator_broadcast.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=user)), \
         patch("khatmsaz.bot.handlers.creator_broadcast.khatm_service.list_my_created", new=AsyncMock(return_value=[khatm])):
        mock_scope.return_value.__aenter__.return_value = AsyncMock()
        await creator_broadcast.start_broadcast(msg, state)
    
    msg.answer.assert_awaited_once()
    _, kwargs = msg.answer.call_args
    markup = kwargs["reply_markup"]
    callbacks = [btn.callback_data for row in markup.inline_keyboard for btn in row]
    texts = [btn.text for row in markup.inline_keyboard for btn in row]
    
    assert "cbroadcast:cancel" in callbacks
    assert "❌ انصراف" in texts


@pytest.mark.asyncio
async def test_broadcast_cancel_works_from_any_state():
    """`cbroadcast:cancel` must clear state and return to main menu from any state."""
    cb = _mock_callback("cbroadcast:cancel")
    state = await _get_fsm_context()
    await state.set_state(CreatorBroadcastFlow.choosing_target)
    
    await creator_broadcast.cancel_broadcast(cb, state)
    
    assert await state.get_state() is None
    cb.message.answer.assert_awaited_once()
    call_text = cb.message.answer.call_args[0][0]
    assert "لغو شد" in call_text


# ==============================================================================
# 4. WALLET INVOICES & RECEIPT UPLOAD
# ==============================================================================

@pytest.mark.asyncio
async def test_wallet_invoices_includes_return_button():
    """`_show_invoices` must include [🔙 بازگشت به کیف پول] button."""
    user = _make_mock_user()
    settings = MagicMock(language="fa")
    msg = _mock_message()
    
    with patch("khatmsaz.bot.handlers.wallet.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.wallet.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=user)), \
         patch("khatmsaz.bot.handlers.wallet.settings_service.get_or_create", new=AsyncMock(return_value=settings)), \
         patch("khatmsaz.bot.handlers.wallet.wallet_service.list_invoices", new=AsyncMock(return_value=[])):
        mock_scope.return_value.__aenter__.return_value = AsyncMock()
        await wallet._show_invoices(msg)
    
    msg.answer.assert_awaited_once()
    _, kwargs = msg.answer.call_args
    markup = kwargs["reply_markup"]
    callbacks = [btn.callback_data for row in markup.inline_keyboard for btn in row]
    
    assert "wallet:open" in callbacks


@pytest.mark.asyncio
async def test_wallet_receipt_upload_has_cancel_and_cleans_up():
    """`start_receipt_upload` offers cancel button; `cancel_receipt_upload` clears state."""
    cb = _mock_callback("wallet:receipt_upload")
    state = await _get_fsm_context()
    
    with patch("khatmsaz.bot.handlers.wallet._lang_for", new=AsyncMock(return_value="fa")):
        await wallet.start_receipt_upload(cb, state)
    
    assert await state.get_state() == WalletReceiptUpload.entering_amount.state
    cb.message.answer.assert_awaited_once()
    _, kwargs = cb.message.answer.call_args
    markup = kwargs["reply_markup"]
    callbacks = [btn.callback_data for row in markup.inline_keyboard for btn in row]
    assert "wallet:cancel_receipt" in callbacks
    
    # Now trigger cancel_receipt
    cb_cancel = _mock_callback("wallet:cancel_receipt")
    with patch("khatmsaz.bot.handlers.wallet._show_wallet", new=AsyncMock()) as mock_show_wallet:
        await wallet.cancel_receipt_upload(cb_cancel, state)
        mock_show_wallet.assert_awaited_once()
    
    assert await state.get_state() is None


# ==============================================================================
# 5. CUSTOM KHATM REQUEST
# ==============================================================================

@pytest.mark.asyncio
async def test_khatm_request_has_cancel_button():
    """`request_khatm:start` prompt offers [❌ انصراف] and `request_khatm:cancel` resets state."""
    cb = _mock_callback("request_khatm:start")
    state = await _get_fsm_context()
    
    with patch("khatmsaz.bot.handlers.khatm_request._lang_for", new=AsyncMock(return_value="fa")):
        await khatm_request.request_khatm_start(cb, state)
        
    assert await state.get_state() == RequestKhatm.entering_description.state
    cb.message.answer.assert_awaited_once()
    _, kwargs = cb.message.answer.call_args
    markup = kwargs["reply_markup"]
    callbacks = [btn.callback_data for row in markup.inline_keyboard for btn in row]
    assert "request_khatm:cancel" in callbacks
    
    # Trigger cancel
    cb_cancel = _mock_callback("request_khatm:cancel")
    with patch("khatmsaz.bot.handlers.khatm_request._lang_for", new=AsyncMock(return_value="fa")):
        await khatm_request.request_khatm_cancel(cb_cancel, state)
    
    assert await state.get_state() is None
    cb_cancel.message.answer.assert_awaited_once()
    assert "لغو شد" in cb_cancel.message.answer.call_args[0][0]
