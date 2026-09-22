"""Fail-closed behavior before a public HTTPS Mini App origin exists."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from khatmsaz.bot.handlers import admin, my_khatms
from khatmsaz.modules.identity.models import Platform


def _message():
    return SimpleNamespace(
        bot=SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM),
        chat=SimpleNamespace(id=123),
        answer=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_admin_mini_app_rejects_local_http_origin(monkeypatch):
    message = _message()
    monkeypatch.setattr(admin, "_require_admin", AsyncMock(return_value=True))
    monkeypatch.setattr(
        admin, "get_settings", lambda: SimpleNamespace(admin_web_base_url="http://127.0.0.1:8000")
    )
    await admin.admin_web_login(message)
    text = message.answer.await_args.args[0]
    assert "HTTPS" in text and "app.khatmsaz.com" in text
    assert message.answer.await_args.kwargs.get("reply_markup") is None


@pytest.mark.asyncio
async def test_creator_mini_app_rejects_local_http_origin_before_database_access(monkeypatch):
    message = _message()
    monkeypatch.setattr(
        my_khatms, "get_settings", lambda: SimpleNamespace(admin_web_base_url="http://10.0.0.2:8000")
    )
    await my_khatms.creator_web_login(message)
    text = message.answer.await_args.args[0]
    # Creator-facing copy (unlike admin.py) deliberately avoids the "HTTPS"
    # jargon term per the tone-guide checklist (docs/ai/TONE_GUIDE_80YO_PERSONA.md);
    # what matters here is the fail-closed behavior, not the exact wording.
    assert "آماده نشده" in text
    assert message.answer.await_args.kwargs.get("reply_markup") is None
