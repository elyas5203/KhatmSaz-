"""Wallet regressions using real APIs and meaningful assertions."""
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4
import pytest
from khatmsaz.modules.wallet import service
from khatmsaz.modules.wallet.models import InvoiceKind

@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["REFUNDED", "CANCELLED"])
async def test_nonpaid_invoice_never_reaches_legacy_refund(monkeypatch, status):
    refund = AsyncMock()
    monkeypatch.setattr(service, "refund_cash", refund)
    monkeypatch.setattr(service.repository, "get_invoice_by_resource", AsyncMock(return_value=SimpleNamespace(status=status)))
    with pytest.raises(service.InvalidPaymentError):
        await service.refund_purchase_invoice(AsyncMock(), user_id=uuid4(), kind=InvoiceKind.KHATM_CREATION, resource_ref="test", description="test")
    refund.assert_not_awaited()

@pytest.mark.asyncio
async def test_lost_invoice_compare_and_set_cannot_credit_wallet(monkeypatch):
    refund = AsyncMock()
    monkeypatch.setattr(service, "refund_cash", refund)
    monkeypatch.setattr(service.repository, "get_invoice_by_resource", AsyncMock(return_value=SimpleNamespace(id=uuid4(), status="PAID")))
    monkeypatch.setattr(service.repository, "mark_invoice_refunded", AsyncMock(return_value=None))
    with pytest.raises(service.InvalidPaymentError):
        await service.refund_purchase_invoice(AsyncMock(), user_id=uuid4(), kind=InvoiceKind.KHATM_CREATION, resource_ref="test", description="test")
    refund.assert_not_awaited()

@pytest.mark.asyncio
async def test_refund_credits_balance_and_ledger(monkeypatch):
    wallet = SimpleNamespace(id=uuid4())
    monkeypatch.setattr(service, "get_or_create_wallet", AsyncMock(return_value=wallet))
    balance, ledger = AsyncMock(), AsyncMock()
    monkeypatch.setattr(service.repository, "add_balance", balance)
    monkeypatch.setattr(service.repository, "record_transaction", ledger)
    session = AsyncMock()
    await service.refund_cash(session, uuid4(), 1000, description="refund")
    balance.assert_awaited_once_with(session, wallet.id, 1000)
    assert ledger.await_args.args[2] == 1000
