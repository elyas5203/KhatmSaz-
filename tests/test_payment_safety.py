"""Fast safety checks for pending-payment expiry and replay behavior."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from khatmsaz.modules.wallet import repository, service
from khatmsaz.modules.wallet.gateway import PaymentVerification


@pytest.mark.asyncio
async def test_cleanup_delegates_with_current_time_and_reports_count(monkeypatch):
    cleanup = AsyncMock(return_value=4)
    monkeypatch.setattr(repository, "delete_expired_unused_payments", cleanup)
    before = datetime.now(timezone.utc)

    count = await service.cleanup_expired_pending_payments(object())

    after = datetime.now(timezone.utc)
    assert count == 4
    called_now = cleanup.await_args.kwargs["now"]
    assert before <= called_now <= after


@pytest.mark.asyncio
async def test_callback_cas_loss_never_credits_wallet(monkeypatch):
    payment_id = uuid4()
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    pending = SimpleNamespace(
        id=payment_id, user_id=user_id, authority="authority",
        amount_toman=25_000, description="test", used=False,
        expires_at=now + timedelta(minutes=5),
    )
    monkeypatch.setattr(repository, "get_pending_payment_by_id", AsyncMock(return_value=pending))
    monkeypatch.setattr(repository, "claim_pending_payment", AsyncMock(return_value=None))
    credit = AsyncMock()
    monkeypatch.setattr(service, "add_cash", credit)
    gateway = SimpleNamespace(
        verify_payment=AsyncMock(return_value=PaymentVerification(
            authority="authority", amount_toman=25_000, transaction_ref="ref-1"
        ))
    )

    with pytest.raises(service.PaymentAlreadyProcessedError):
        await service.verify_payping_callback_and_credit(
            object(), gateway, client_ref_id=str(payment_id), authority="authority",
            amount_toman=25_000, transaction_ref="ref-1", now=now,
        )

    credit.assert_not_awaited()


@pytest.mark.asyncio
async def test_expired_callback_stops_before_gateway_or_credit(monkeypatch):
    payment_id = uuid4()
    now = datetime.now(timezone.utc)
    pending = SimpleNamespace(
        id=payment_id, user_id=uuid4(), authority="authority",
        amount_toman=25_000, description="test", used=False,
        expires_at=now - timedelta(seconds=1),
    )
    monkeypatch.setattr(repository, "get_pending_payment_by_id", AsyncMock(return_value=pending))
    credit = AsyncMock()
    monkeypatch.setattr(service, "add_cash", credit)
    gateway = SimpleNamespace(verify_payment=AsyncMock())

    with pytest.raises(service.InvalidPaymentError):
        await service.verify_payping_callback_and_credit(
            object(), gateway, client_ref_id=str(payment_id), authority="authority",
            amount_toman=25_000, transaction_ref="ref-1", now=now,
        )

    gateway.verify_payment.assert_not_awaited()
    credit.assert_not_awaited()
