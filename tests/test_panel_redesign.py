"""Regression for the 2026-09-29 panel redesign:

1. The creator «💳 شارژ کیف پول» reply button reaches the wallet handler in
   every language (owner request — creators had no tap-only wallet entry).
2. The redesigned creator web panel and the new admin creator-requests page
   expose their routes.
"""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, Update, User

from khatmsaz.bot import keyboards
from khatmsaz.bot.handlers import panel, wallet as wallet_handler
from khatmsaz.i18n import t
from khatmsaz.modules.identity.models import UserRole


def _text_update(update_id: int, text: str, chat_id: int = 9202) -> Update:
    return Update(
        update_id=update_id,
        message=Message(
            message_id=update_id,
            date=datetime.now(timezone.utc),
            chat=Chat(id=chat_id, type="private"),
            from_user=User(id=chat_id, is_bot=False, first_name="Creator"),
            text=text,
        ),
    )


def test_wallet_button_present_in_finance_keyboard():
    labels = {btn.text for row in keyboards.creator_finance_keyboard("fa").keyboard for btn in row}
    assert t("menu.creator.wallet", "fa") in labels


@pytest.mark.asyncio
async def test_creator_wallet_button_is_wired(monkeypatch):
    creator = SimpleNamespace(id="creator-id", role=UserRole.CREATOR)
    calls = {"wallet": 0}

    async def fake_context(_event):
        return creator, "fa"

    async def fake_show_wallet(_message):
        calls["wallet"] += 1

    monkeypatch.setattr(panel, "_get_context", fake_context)
    monkeypatch.setattr(wallet_handler, "_show_wallet", fake_show_wallet)

    bot = Bot("123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
    bot._me = User(id=123456, is_bot=True, first_name="KhatmSaz", username="khatmsaz_test_bot")
    dp = Dispatcher(storage=MemoryStorage())
    panel.router._parent_router = None
    dp.include_router(panel.router)
    uid = 0
    try:
        for lang in ("fa", "ar", "en"):
            uid += 1
            await dp.feed_update(bot, _text_update(uid, t("menu.creator.wallet", lang)))
    finally:
        await bot.session.close()

    assert calls["wallet"] == 3, "«شارژ کیف پول» did not reach the wallet handler in every language"


def test_new_panel_routes_exist():
    from khatmsaz.web.app import app

    paths = {getattr(r, "path", "") for r in app.routes}
    for path in (
        "/creator/khatms", "/creator/khatms/new", "/creator/khatms/create",
        "/creator/wallet", "/creator/wallet/topup", "/creator/plan/upgrade",
        "/creator-requests", "/finance/user-plan",
    ):
        assert path in paths, f"missing route {path}"
