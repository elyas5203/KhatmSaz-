"""Tests for MASTER-57 / DEC-PY-0149:
Direct Shaparak Gateway Link (ppng.ir/d/VFBD) & Receipt Upload Flow for Wallet Recharge.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, PhotoSize

from khatmsaz.bot.handlers.wallet import (
    WalletReceiptUpload,
    WalletTopup,
    _topup_keyboard,
    _send_direct_shaparak_topup,
    create_topup,
    receive_custom_topup,
    start_receipt_upload,
    show_topup_info,
)
from khatmsaz.bot.keyboards import wallet_recharge_packages_keyboard


# --- 1. Keyboard Structure Tests ---

def test_topup_keyboard_has_direct_shaparak_url_button():
    """`_topup_keyboard` MUST contain a direct URL button to Shaparak and a receipt upload button."""
    kb = _topup_keyboard("fa")
    assert isinstance(kb, InlineKeyboardMarkup)
    
    url_buttons = [btn for row in kb.inline_keyboard for btn in row if btn.url]
    callback_buttons = [btn for row in kb.inline_keyboard for btn in row if btn.callback_data]

    # Must contain direct Shaparak link
    shaparak_urls = [btn.url for btn in url_buttons if "ppng.ir/d/VFBD" in btn.url]
    assert len(shaparak_urls) == 1
    
    # Must contain receipt upload callback
    receipt_cbs = [btn.callback_data for btn in callback_buttons if btn.callback_data == "wallet:receipt_upload"]
    assert len(receipt_cbs) == 1


def test_wallet_recharge_packages_keyboard_has_direct_shaparak_url_button():
    """`wallet_recharge_packages_keyboard` MUST contain a direct URL button to Shaparak."""
    kb = wallet_recharge_packages_keyboard("fa", back_callback="back", recheck_callback="recheck")
    assert isinstance(kb, InlineKeyboardMarkup)
    
    url_buttons = [btn for row in kb.inline_keyboard for btn in row if btn.url]
    shaparak_urls = [btn.url for btn in url_buttons if "ppng.ir/d/VFBD" in btn.url]
    assert len(shaparak_urls) == 1


# --- 2. Direct Shaparak Recharge Flow Tests ---

@pytest.mark.asyncio
async def test_send_direct_shaparak_topup_generates_correct_buttons():
    """`_send_direct_shaparak_topup` generates direct URL button and receipt upload with specific amount."""
    mock_msg = MagicMock(spec=Message)
    mock_msg.answer = AsyncMock()

    await _send_direct_shaparak_topup(mock_msg, 1_346_955, "fa")

    mock_msg.answer.assert_awaited_once()
    _, kwargs = mock_msg.answer.await_args
    markup = kwargs["reply_markup"]
    assert isinstance(markup, InlineKeyboardMarkup)

    # First button: Direct Shaparak URL
    btn_url = markup.inline_keyboard[0][0]
    assert btn_url.url == "https://ppng.ir/d/VFBD"
    assert "شاپرک" in btn_url.text

    # Second button: Receipt upload prefilled with 1346955
    btn_receipt = markup.inline_keyboard[1][0]
    assert btn_receipt.callback_data == "wallet:receipt_upload:1346955"
    assert "فیش" in btn_receipt.text

    # Third button: Back
    btn_back = markup.inline_keyboard[2][0]
    assert btn_back.callback_data == "wallet:open"


@pytest.mark.asyncio
async def test_create_topup_predefined_amount():
    """Selecting predefined amount (e.g. 50,000) delegates to `_send_direct_shaparak_topup`."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "wallet_topup:50000"
    callback.message = MagicMock(spec=Message)
    callback.message.chat = MagicMock(id=12345)
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()
    callback.bot = MagicMock()

    with patch("khatmsaz.bot.handlers.wallet._lang_for", new=AsyncMock(return_value="fa")):
        await create_topup(callback)

    callback.message.answer.assert_awaited_once()
    _, kwargs = callback.message.answer.await_args
    markup = kwargs["reply_markup"]

    assert markup.inline_keyboard[0][0].url == "https://ppng.ir/d/VFBD"
    assert markup.inline_keyboard[1][0].callback_data == "wallet:receipt_upload:50000"


@pytest.mark.asyncio
async def test_receive_custom_topup_delegates_to_direct_shaparak():
    """Entering custom amount (e.g. 1346955) clears state and presents direct Shaparak link."""
    message = MagicMock(spec=Message)
    message.text = "1346955"
    message.answer = AsyncMock()
    message.bot = MagicMock()

    state = MagicMock(spec=FSMContext)
    state.get_data = AsyncMock(return_value={"lang": "fa"})
    state.clear = AsyncMock()

    with patch("khatmsaz.bot.keyboards.bail_if_menu_button", new=AsyncMock(return_value=False)):
        await receive_custom_topup(message, state)

    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once()
    _, kwargs = message.answer.await_args
    markup = kwargs["reply_markup"]

    assert markup.inline_keyboard[0][0].url == "https://ppng.ir/d/VFBD"
    assert markup.inline_keyboard[1][0].callback_data == "wallet:receipt_upload:1346955"


# --- 3. Receipt Upload Handlers Tests ---

@pytest.mark.asyncio
async def test_start_receipt_upload_with_amount_moves_directly_to_photo():
    """When amount is provided in callback (wallet:receipt_upload:1346955), skips asking amount and requests photo."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "wallet:receipt_upload:1346955"
    callback.message = MagicMock(spec=Message)
    callback.message.chat = MagicMock(id=12345)
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()
    callback.bot = MagicMock()

    state = MagicMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()

    with patch("khatmsaz.bot.handlers.wallet._lang_for", new=AsyncMock(return_value="fa")):
        await start_receipt_upload(callback, state)

    # Moves directly to uploading_photo
    state.set_state.assert_awaited_once_with(WalletReceiptUpload.uploading_photo)
    state.update_data.assert_awaited_once_with(lang="fa", amount_toman=1346955)
    
    callback.message.answer.assert_awaited_once()
    args, _ = callback.message.answer.await_args
    assert "۱٬۳۴۶٬۹۵۵" in args[0] or "1,346,955" in args[0] or "فیش" in args[0]


@pytest.mark.asyncio
async def test_start_receipt_upload_without_amount_asks_for_amount():
    """When amount is NOT provided (wallet:receipt_upload), asks for amount first."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "wallet:receipt_upload"
    callback.message = MagicMock(spec=Message)
    callback.message.chat = MagicMock(id=12345)
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()
    callback.bot = MagicMock()

    state = MagicMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()

    with patch("khatmsaz.bot.handlers.wallet._lang_for", new=AsyncMock(return_value="fa")):
        await start_receipt_upload(callback, state)

    # Moves to entering_amount
    state.set_state.assert_awaited_once_with(WalletReceiptUpload.entering_amount)
    callback.message.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_show_topup_info_includes_direct_button():
    """`show_topup_info` includes direct Shaparak URL button."""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "wallet:topup_info"
    callback.message = MagicMock(spec=Message)
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()

    await show_topup_info(callback)

    callback.message.answer.assert_awaited_once()
    _, kwargs = callback.message.answer.await_args
    markup = kwargs["reply_markup"]
    assert markup.inline_keyboard[0][0].url == "https://ppng.ir/d/VFBD"
