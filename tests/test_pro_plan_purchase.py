from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from khatmsaz.modules.plan import repository, service
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import InvoiceKind


@pytest.mark.asyncio
async def test_purchase_pro_uses_database_price_spends_once_and_sets_plan(monkeypatch):
    user_id = uuid4()
    session = object()
    lock = AsyncMock()
    purchase = AsyncMock(return_value=SimpleNamespace(net_amount_toman=275_000))
    set_plan = AsyncMock()
    monkeypatch.setattr(repository, "lock_plan_change", lock)
    monkeypatch.setattr(service, "get_plan", AsyncMock(return_value=PlanTier.FREE))
    monkeypatch.setattr(service, "get_definition", AsyncMock(return_value=SimpleNamespace(
        enabled=True, price_toman=275_000,
    )))
    monkeypatch.setattr(wallet_service, "purchase", purchase)
    monkeypatch.setattr(service, "set_plan", set_plan)

    invoice = await service.purchase_pro(session, user_id)

    assert invoice.net_amount_toman == 275_000
    lock.assert_awaited_once()
    purchase.assert_awaited_once_with(
        session, user_id=user_id, gross_amount_toman=275_000,
        description="خرید دائمی پلن پرو", invoice_kind=InvoiceKind.PURCHASE,
    )
    set_plan.assert_awaited_once_with(session, user_id, PlanTier.PRO)


@pytest.mark.asyncio
async def test_purchase_pro_never_recharges_existing_paid_plan(monkeypatch):
    purchase = AsyncMock()
    monkeypatch.setattr(repository, "lock_plan_change", AsyncMock())
    monkeypatch.setattr(service, "get_plan", AsyncMock(return_value=PlanTier.PRO))
    monkeypatch.setattr(wallet_service, "purchase", purchase)

    assert await service.purchase_pro(object(), uuid4()) is None
    purchase.assert_not_awaited()


@pytest.mark.asyncio
async def test_purchase_pro_requires_enabled_positive_admin_price(monkeypatch):
    monkeypatch.setattr(repository, "lock_plan_change", AsyncMock())
    monkeypatch.setattr(service, "get_plan", AsyncMock(return_value=PlanTier.FREE))
    monkeypatch.setattr(service, "get_definition", AsyncMock(return_value=SimpleNamespace(
        enabled=True, price_toman=0,
    )))

    with pytest.raises(service.ProPlanUnavailableError):
        await service.purchase_pro(object(), uuid4())
