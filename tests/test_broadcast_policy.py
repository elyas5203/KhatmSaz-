from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from khatmsaz.modules.broadcast import repository, service


@pytest.mark.asyncio
async def test_submit_all_targets_distinct_audience_and_uses_channel_policy(monkeypatch):
    creator_id = uuid4()
    created = SimpleNamespace()
    monkeypatch.setattr(service, "audience_user_ids", AsyncMock(return_value=[uuid4(), uuid4()]))
    monkeypatch.setattr(service, "channel_policy", AsyncMock(return_value=(3, 12_000)))
    monkeypatch.setattr(repository, "count_recent_for_creator_channel", AsyncMock(return_value=3))
    create = AsyncMock(return_value=created)
    monkeypatch.setattr(repository, "create", create)

    result = await service.submit(
        object(), khatm_id=None, creator_user_id=creator_id,
        body="سلام اعضای عزیز", channel="BALE",
    )

    assert result is created
    kwargs = create.await_args.kwargs
    assert kwargs["target_scope"] == "ALL"
    assert kwargs["channel"] == "BALE"
    assert kwargs["audience_count"] == 2
    assert kwargs["cost_toman"] == 12_000


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
