"""Owner §A4: خدمتگزاران system ad — dedup + BASIC-only delivery + guards."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from khatmsaz.modules.servant_ad import service as sa


@pytest.mark.asyncio
async def test_send_now_requires_enabled_and_nonempty(monkeypatch):
    monkeypatch.setattr(sa, "get_ad", AsyncMock(return_value={
        "enabled": False, "text": "x", "media_type": "", "media_telegram": "", "media_bale": "",
    }))
    with pytest.raises(ValueError):
        await sa.send_now(object(), AsyncMock())

    monkeypatch.setattr(sa, "get_ad", AsyncMock(return_value={
        "enabled": True, "text": "", "media_type": "", "media_telegram": "", "media_bale": "",
    }))
    with pytest.raises(ValueError):
        await sa.send_now(object(), AsyncMock())


@pytest.mark.asyncio
async def test_send_now_delivers_once_per_target(monkeypatch):
    monkeypatch.setattr(sa, "get_ad", AsyncMock(return_value={
        "enabled": True, "text": "سلام", "media_type": "", "media_telegram": "", "media_bale": "",
    }))
    monkeypatch.setattr(sa, "_targets", AsyncMock(return_value=[
        ("TELEGRAM", "111"), ("TELEGRAM", "222"), ("BALE", "333"),
    ]))
    sent = []

    async def _send(platform, subject, text, media_type, media_file_id):
        sent.append((platform, subject))
        return True

    delivered = await sa.send_now(object(), _send)
    assert delivered == 3
    assert sent == [("TELEGRAM", "111"), ("TELEGRAM", "222"), ("BALE", "333")]
