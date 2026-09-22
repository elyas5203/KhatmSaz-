from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from khatmsaz.modules.notification import repository, service


@pytest.mark.asyncio
async def test_snooze_accepts_supported_durations(monkeypatch):
    captured = {}

    async def fake_set(session, participation_id, until):
        captured["participation_id"] = participation_id
        captured["until"] = until
        return SimpleNamespace(snoozed_until=until)

    monkeypatch.setattr(repository, "set_snoozed_until", fake_set)
    before = datetime.now(timezone.utc)
    result = await service.snooze(object(), "participation", 60)
    after = datetime.now(timezone.utc)

    assert result.snoozed_until >= before + timedelta(minutes=60)
    assert result.snoozed_until <= after + timedelta(minutes=60, seconds=1)
    assert captured["participation_id"] == "participation"


@pytest.mark.asyncio
async def test_snooze_rejects_arbitrary_duration(monkeypatch):
    with pytest.raises(ValueError):
        await service.snooze(object(), "participation", 45)


@pytest.mark.asyncio
async def test_custom_snooze_accepts_future_timezone_aware_time(monkeypatch):
    captured = {}

    async def fake_set(_session, _participation, until):
        captured["until"] = until
        return SimpleNamespace(snoozed_until=until)

    monkeypatch.setattr(repository, "set_snoozed_until", fake_set)
    until = datetime.now(timezone.utc) + timedelta(hours=2)
    result = await service.snooze_until(object(), "participation", until)
    assert result.snoozed_until == until


@pytest.mark.asyncio
async def test_custom_snooze_rejects_past_time(monkeypatch):
    with pytest.raises(ValueError):
        await service.snooze_until(object(), "participation", datetime.now(timezone.utc) - timedelta(minutes=1))
