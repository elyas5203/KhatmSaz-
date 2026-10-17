from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from khatmsaz.modules.broadcast import repository, service
from khatmsaz.modules.plan.models import PlanTier


@pytest.mark.asyncio
async def test_submit_allows_free_plan_with_wallet_spend(monkeypatch):
    """MASTER-31: Broadcast entitlement does not require PRO plan; any funded creator can send."""
    creator_id = uuid4()
    monkeypatch.setattr(service, "audience_user_ids", AsyncMock(return_value=[uuid4(), uuid4()]))
    monkeypatch.setattr(service, "channel_policy", AsyncMock(return_value=(0, 50_000)))
    mock_spend = AsyncMock()
    monkeypatch.setattr(service.wallet_service, "spend", mock_spend)
    created = SimpleNamespace()
    create = AsyncMock(return_value=created)
    monkeypatch.setattr(repository, "create", create)

    result = await service.submit(
        object(), khatm_id=None, creator_user_id=creator_id,
        body="سلام اعضای عزیز", channel="BALE",
    )
    assert result is created
    assert mock_spend.await_count == 1
    assert mock_spend.await_args.kwargs["amount"] == 50_000


@pytest.mark.asyncio
async def test_pro_plan_charged_per_1000_recipients_from_wallet(monkeypatch):
    creator_id = uuid4()
    # 2 recipients = 1 package of 1000
    monkeypatch.setattr(service, "audience_user_ids", AsyncMock(return_value=[uuid4(), uuid4()]))
    monkeypatch.setattr(service, "channel_policy", AsyncMock(return_value=(0, 50_000)))
    monkeypatch.setattr(service.plan_service, "get_plan", AsyncMock(return_value=PlanTier.PRO))
    mock_spend = AsyncMock()
    monkeypatch.setattr(service.wallet_service, "spend", mock_spend)
    created = SimpleNamespace()
    create = AsyncMock(return_value=created)
    monkeypatch.setattr(repository, "create", create)

    result = await service.submit(
        object(), khatm_id=None, creator_user_id=creator_id,
        body="پیام گروهی", channel="BALE",
    )
    assert result is created
    assert mock_spend.await_count == 1
    assert mock_spend.await_args.kwargs["amount"] == 50_000
    assert create.await_args.kwargs["cost_toman"] == 50_000


@pytest.mark.asyncio
async def test_sms_is_paid_per_tier(monkeypatch):
    creator_id = uuid4()
    monkeypatch.setattr(service, "audience_user_ids", AsyncMock(return_value=[uuid4()]))
    monkeypatch.setattr(service, "channel_policy", AsyncMock(return_value=(0, 100_000)))
    monkeypatch.setattr(service.plan_service, "get_plan", AsyncMock(return_value=PlanTier.PRO))
    mock_spend = AsyncMock()
    monkeypatch.setattr(service.wallet_service, "spend", mock_spend)
    create = AsyncMock(return_value=SimpleNamespace())
    monkeypatch.setattr(repository, "create", create)

    await service.submit(object(), khatm_id=None, creator_user_id=creator_id, body="پیامک", channel="SMS")
    assert mock_spend.await_args.kwargs["amount"] == 100_000
    assert create.await_args.kwargs["cost_toman"] == 100_000


@pytest.mark.asyncio
async def test_submit_requires_supported_channel_and_nonempty_audience(monkeypatch):
    with pytest.raises(ValueError):
        await service.submit(object(), khatm_id=None, creator_user_id=uuid4(), body="سلام", channel="EMAIL")

    monkeypatch.setattr(service, "audience_user_ids", AsyncMock(return_value=[]))
    with pytest.raises(ValueError):
        await service.submit(object(), khatm_id=None, creator_user_id=uuid4(), body="سلام", channel="SMS")


@pytest.mark.asyncio
async def test_all_three_channel_policies_are_admin_backed(monkeypatch):
    get_int = AsyncMock(side_effect=[3, 0, 2, 5_000, 0, 15_000])
    monkeypatch.setattr(service.system_settings_service, "get_int", get_int)

    assert await service.channel_policy(object(), "TELEGRAM") == (3, 0)
    assert await service.channel_policy(object(), "BALE") == (2, 5_000)
    assert await service.channel_policy(object(), "SMS") == (0, 15_000)
