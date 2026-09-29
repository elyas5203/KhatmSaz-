from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from khatmsaz.modules.plan import service
from khatmsaz.modules.plan.models import ACTIVE_PLAN_TIERS, PlanTier
from khatmsaz.modules.wallet import service as wallet_service


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("funds", "expected"),
    [(49_999, PlanTier.FREE), (50_000, PlanTier.PRO), (80_000, PlanTier.PRO)],
)
async def test_plan_is_derived_from_admin_threshold_and_wallet(monkeypatch, funds, expected):
    monkeypatch.setattr(service, "get_definition", AsyncMock(return_value=SimpleNamespace(
        enabled=True, price_toman=50_000,
    )))
    monkeypatch.setattr(wallet_service, "get_balances", AsyncMock(return_value=(funds - 10_000, 10_000)))

    assert await service.get_plan(object(), uuid4()) == expected


@pytest.mark.asyncio
async def test_disabled_threshold_keeps_free_without_reading_wallet(monkeypatch):
    balances = AsyncMock()
    monkeypatch.setattr(wallet_service, "get_balances", balances)
    monkeypatch.setattr(service, "get_definition", AsyncMock(return_value=SimpleNamespace(
        enabled=False, price_toman=50_000,
    )))

    assert await service.get_plan(object(), uuid4()) == PlanTier.FREE
    balances.assert_not_awaited()


def test_only_free_and_pro_are_active_tiers():
    assert ACTIVE_PLAN_TIERS == (PlanTier.FREE, PlanTier.PRO)
