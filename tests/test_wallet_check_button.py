"""Unit tests for the in-bot manual payment verification flow."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup

from khatmsaz.bot.handlers.wallet import (
    WalletTopup,
    _create_topup_payment,
    handle_wallet_check,
    receive_ref_id_for_verification,
)
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.gateway import PaymentRequest, PaymentVerification


@pytest.mark.asyncio
async def test_create_topup_payment_includes_check_button(monkeypatch):
    payment_id = uuid4()
    mock_pending = SimpleNamespace(id=payment_id)
    mock_request = PaymentRequest(authority="test-auth", payment_url="https://payping.ir/test")

    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.resolve_or_provision_user",
        AsyncMock(return_value=SimpleNamespace(id=uuid4())),
    )
    monkeypatch.setattr(
        wallet_service,
        "create_payment_intent",
        AsyncMock(return_value=(mock_pending, mock_request)),
    )
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.wallet.get_settings",
        lambda: SimpleNamespace(
            payping_api_token="token",
            payping_callback_url="https://api.khedmatgozaran.com/payments/payping/callback",
        ),
    )

    message = MagicMock()
    message.chat = SimpleNamespace(id=12345)
    message.answer = AsyncMock()

    bot = MagicMock()
    bot.khatmsaz_platform = "telegram"

    await _create_topup_payment(message, bot, 50_000, "fa")

    message.answer.assert_awaited_once()
    _, kwargs = message.answer.await_args
    reply_markup = kwargs.get("reply_markup")
    assert isinstance(reply_markup, InlineKeyboardMarkup)
    assert len(reply_markup.inline_keyboard) == 2
    # First button is payment URL
    assert reply_markup.inline_keyboard[0][0].url == "https://payping.ir/test"
    # Second button is check callback
    assert reply_markup.inline_keyboard[1][0].callback_data == f"wallet_check:{payment_id}"


@pytest.mark.asyncio
async def test_handle_wallet_check_sets_fsm_state(monkeypatch):
    payment_id = uuid4()
    future_exp = datetime.now(timezone.utc) + timedelta(minutes=20)
    mock_pending = SimpleNamespace(id=payment_id, used=False, expires_at=future_exp)

    monkeypatch.setattr(
        "khatmsaz.modules.wallet.repository.get_pending_payment_by_id",
        AsyncMock(return_value=mock_pending),
    )
    monkeypatch.setattr("khatmsaz.bot.handlers.wallet._lang_for", AsyncMock(return_value="fa"))

    callback = MagicMock()
    callback.data = f"wallet_check:{payment_id}"
    callback.message = MagicMock()
    callback.message.chat = SimpleNamespace(id=12345)
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()

    state = MagicMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()

    await handle_wallet_check(callback, state)

    state.set_state.assert_awaited_once_with(WalletTopup.entering_ref_id)
    state.update_data.assert_awaited_once_with(payment_id=str(payment_id), lang="fa")
    callback.message.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_receive_ref_id_successful_verification(monkeypatch):
    payment_id = uuid4()
    future_exp = datetime.now(timezone.utc) + timedelta(minutes=20)
    mock_pending = SimpleNamespace(
        id=payment_id,
        authority="auth123",
        amount_toman=50_000,
        used=False,
        expires_at=future_exp,
    )

    monkeypatch.setattr(
        "khatmsaz.modules.wallet.repository.get_pending_payment_by_id",
        AsyncMock(return_value=mock_pending),
    )
    mock_verify = AsyncMock(
        return_value=PaymentVerification(
            authority="auth123",
            amount_toman=50_000,
            transaction_ref="123456",
        )
    )
    monkeypatch.setattr(wallet_service, "verify_payping_callback_and_credit", mock_verify)
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.wallet.get_settings",
        lambda: SimpleNamespace(payping_api_token="token"),
    )
    monkeypatch.setattr("khatmsaz.bot.handlers.wallet._show_wallet", AsyncMock())

    message = MagicMock()
    # User sends Persian digits
    message.text = "۱۲۳۴۵۶"
    message.answer = AsyncMock()

    state = MagicMock(spec=FSMContext)
    state.get_data = AsyncMock(return_value={"payment_id": str(payment_id), "lang": "fa"})
    state.clear = AsyncMock()

    await receive_ref_id_for_verification(message, state)

    mock_verify.assert_awaited_once()
    assert mock_verify.await_args.kwargs["transaction_ref"] == "123456"
    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once()
    assert "تأیید شد" in message.answer.await_args.args[0]
