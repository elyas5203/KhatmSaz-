"""Cancellation fallback checks; these do not claim to prove concurrency."""
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from khatmsaz.modules.khatm_workflow import service as workflow
from khatmsaz.modules.wallet.service import InvalidPaymentError


@pytest.mark.asyncio
async def test_refunded_invoice_cannot_enter_legacy_cancellation_fallback(monkeypatch):
    user_id, khatm_id = uuid4(), uuid4()
    khatm = SimpleNamespace(id=khatm_id, creator_user_id=user_id, status="ACTIVE",
                            creation_price_toman=1000, title="test")
    monkeypatch.setattr(workflow.khatm_service, "get_khatm_for_update", AsyncMock(return_value=khatm))
    monkeypatch.setattr(workflow.participation_service, "count_for_khatm", AsyncMock(return_value=0))
    monkeypatch.setattr(workflow.khatm_service, "cancel_khatm", AsyncMock())
    monkeypatch.setattr(workflow.wallet_service, "refund_purchase_invoice",
                        AsyncMock(side_effect=InvalidPaymentError("already refunded")))
    refund = AsyncMock()
    monkeypatch.setattr(workflow.wallet_service, "refund_cash", refund)
    with pytest.raises(InvalidPaymentError):
        await workflow.cancel_khatm(AsyncMock(), khatm_id=khatm_id, creator_user_id=user_id)
    refund.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancelled_khatm_rejected_before_refund(monkeypatch):
    user_id, khatm_id = uuid4(), uuid4()
    monkeypatch.setattr(workflow.khatm_service, "get_khatm_for_update", AsyncMock(
        return_value=SimpleNamespace(id=khatm_id, creator_user_id=user_id, status="CANCELLED")))
    refund = AsyncMock()
    monkeypatch.setattr(workflow.wallet_service, "refund_purchase_invoice", refund)
    with pytest.raises(workflow.KhatmCancellationError):
        await workflow.cancel_khatm(AsyncMock(), khatm_id=khatm_id, creator_user_id=user_id)
    refund.assert_not_awaited()
