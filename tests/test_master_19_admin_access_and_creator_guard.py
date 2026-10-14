import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import AsyncClient, ASGITransport

from khatmsaz.bot.handlers import panel
from khatmsaz.bot.handlers.settings_menu import _can_open_creator_panel
from khatmsaz.bot.keyboards import (
    bail_if_menu_button,
    help_manage_actions_keyboard,
    settings_home_keyboard,
)
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.session import service as session_service
from khatmsaz.web.app import app
from khatmsaz.web.telegram_mini_app import validate_telegram_init_data, InvalidTelegramInitData


@pytest.mark.asyncio
async def test_bail_if_menu_button_handles_none_role(monkeypatch):
    """Regression test for AttributeError: 'NoneType' object has no attribute 'value'"""
    # Mock message with reserved menu button text
    msg = MagicMock()
    msg.text = "➕ ساخت ختم جدید"
    msg.answer = AsyncMock()
    state = MagicMock()
    state.clear = AsyncMock()

    # resolve_home_navigation returns role=None on member bots
    async def mock_resolve(message):
        return "fa", None, None

    monkeypatch.setattr("khatmsaz.bot.navigation.resolve_home_navigation", mock_resolve)

    handled = await bail_if_menu_button(msg, state)
    assert handled is True
    assert state.clear.called
    assert msg.answer.called
    reply_text = msg.answer.call_args[0][0]
    assert "لغو شد" in reply_text


def test_creator_panel_button_hidden_in_all_keyboards():
    """MASTER-19: Creator panel web app button is hidden from all in-bot menus."""
    # 1. settings_home_keyboard
    assert not _can_open_creator_panel(MagicMock(), MagicMock(role=UserRole.SUPER_ADMIN))
    kb_settings = settings_home_keyboard(audio_enabled=False, lang="fa", show_creator_panel=False)
    settings_cb = [b.callback_data for row in kb_settings.inline_keyboard for b in row if b.callback_data]
    assert "creator:web_login" not in settings_cb

    # 2. help_manage_actions_keyboard
    kb_help = help_manage_actions_keyboard(lang="fa", is_creator=True, is_admin=True)
    help_cb = [b.callback_data for row in kb_help.inline_keyboard for b in row if b.callback_data]
    assert "creator:web_login" not in help_cb

    # 3. creator_panel_keyboard
    kb_panel = panel.creator_panel_keyboard(lang="fa", is_admin=True)
    panel_cb = [b.callback_data for row in kb_panel.inline_keyboard for b in row if b.callback_data]
    assert "creator:web_login" not in panel_cb


@pytest.mark.asyncio
async def test_admin_redirect_route():
    """MASTER-19: /admin and /admin/ redirect to / instead of 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/admin", follow_redirects=False)
        assert res.status_code == 303
        assert res.headers["location"] == "/"

        res2 = await client.get("/admin/", follow_redirects=False)
        assert res2.status_code == 303
        assert res2.headers["location"] == "/"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_direct_browser_token_login():
    """MASTER-19: /login?token=<raw_token> authenticates admin directly and sets session cookie."""
    async with session_scope() as session:
        # Create or find admin user
        admin = await identity_service.resolve_or_provision_user(
            session, Platform.TELEGRAM, 999901
        )
        await identity_service.repository.set_role(session, admin.id, UserRole.SUPER_ADMIN)
        token = await session_service.issue_admin_session(session, admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Valid token logs in and redirects to / with cookie
        res = await client.get(f"/login?token={token}", follow_redirects=False)
        assert res.status_code == 303
        assert res.headers["location"] == "/"
        assert "khatmsaz_admin_session=" in res.headers.get("set-cookie", "")

        # 2. Invalid token returns 401 with login page
        res_bad = await client.get("/login?token=invalid_token_12345", follow_redirects=False)
        assert res_bad.status_code == 401
        assert "لینک ورود نامعتبر است" in res_bad.text
