"""Fail-closed behavior before a public HTTPS Mini App origin exists."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from khatmsaz.bot.handlers import admin, my_khatms, panel
from khatmsaz.bot.keyboards import admin_menu_keyboard
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


def test_panel_buttons_request_chat_entry_before_opening_mini_app():
    admin_reply = admin_menu_keyboard("fa")
    assert admin_reply.keyboard[0][0].web_app is None

    admin_inline = panel.admin_panel_keyboard("fa")
    assert admin_inline.inline_keyboard[0][0].callback_data == "admin:web_login"
    assert admin_inline.inline_keyboard[0][0].web_app is None

    creator_inline = panel.creator_panel_keyboard("fa")
    assert creator_inline.inline_keyboard[0][0].callback_data == "creator:web_login"
    assert creator_inline.inline_keyboard[0][0].web_app is None
