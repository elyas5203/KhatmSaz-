"""Plan tier model — OWNER_SPEC_MASTER §A (2026-09-30).

Superseded the earlier wallet-threshold derivation: the tier is now STORED
(FREE default; FREE auto-upgrades to BASIC past the audience cap; PRO by
purchase). These tests pin the stored-tier reads and the audience-cap
auto-upgrade.
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from khatmsaz.modules.plan import service
from khatmsaz.modules.plan.models import ACTIVE_PLAN_TIERS, PlanTier


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("stored", "expected"),
    [(None, PlanTier.FREE), (PlanTier.FREE, PlanTier.FREE),
     (PlanTier.BASIC, PlanTier.BASIC), (PlanTier.PRO, PlanTier.PRO)],
)
async def test_get_plan_reads_stored_tier(monkeypatch, stored, expected):
    row = None if stored is None else SimpleNamespace(plan=stored)
    monkeypatch.setattr(service.repository, "get_by_user", AsyncMock(return_value=row))
    assert await service.get_plan(object(), uuid4()) == expected


def test_all_three_tiers_are_active():
    assert ACTIVE_PLAN_TIERS == (PlanTier.FREE, PlanTier.BASIC, PlanTier.PRO)


@pytest.mark.asyncio
async def test_free_autoupgrades_to_basic_past_cap(monkeypatch):
    monkeypatch.setattr(service, "get_plan", AsyncMock(return_value=PlanTier.FREE))
    monkeypatch.setattr(service, "get_free_total_member_cap", AsyncMock(return_value=1000))
    monkeypatch.setattr(service, "count_total_active_members", AsyncMock(return_value=1001))
    set_plan = AsyncMock()
    monkeypatch.setattr(service, "set_plan", set_plan)

    assert await service.maybe_autoupgrade_free_to_basic(object(), uuid4()) is True
    set_plan.assert_awaited_once()
    assert set_plan.await_args.args[2] == PlanTier.BASIC


@pytest.mark.asyncio
async def test_no_autoupgrade_under_cap_or_not_free(monkeypatch):
    monkeypatch.setattr(service, "get_free_total_member_cap", AsyncMock(return_value=1000))
    monkeypatch.setattr(service, "set_plan", AsyncMock())
    # under cap
    monkeypatch.setattr(service, "get_plan", AsyncMock(return_value=PlanTier.FREE))
    monkeypatch.setattr(service, "count_total_active_members", AsyncMock(return_value=1000))
    assert await service.maybe_autoupgrade_free_to_basic(object(), uuid4()) is False
    # already BASIC → never re-upgrades
    monkeypatch.setattr(service, "get_plan", AsyncMock(return_value=PlanTier.BASIC))
    monkeypatch.setattr(service, "count_total_active_members", AsyncMock(return_value=5000))
    assert await service.maybe_autoupgrade_free_to_basic(object(), uuid4()) is False


@pytest.mark.asyncio
async def test_ads_enabled_only_on_basic(monkeypatch):
    basic_def = SimpleNamespace(entitlements={"ads_enabled": True})
    monkeypatch.setattr(service, "get_definition", AsyncMock(return_value=basic_def))
    for tier, expected in ((PlanTier.BASIC, True), (PlanTier.FREE, False), (PlanTier.PRO, False)):
        monkeypatch.setattr(service, "get_plan", AsyncMock(return_value=tier))
        assert await service.ads_enabled_for_creator(object(), uuid4()) is expected
