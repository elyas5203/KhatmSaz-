"""Regression: the creator reply-menu buttons «📊 گزارش و مالی» and
«❓ راهنما و پشتیبانی» had NO handler at all, so tapping them did nothing
(QA report, 2026-09-27). These tests feed each button's text through a real
Dispatcher and assert the wired handler fires."""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, Update, User

from khatmsaz.bot.handlers import panel, help as help_handler
from khatmsaz.i18n import t
from khatmsaz.modules.identity.models import UserRole


def _text_update(update_id: int, text: str, chat_id: int = 9101) -> Update:
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


@pytest.mark.asyncio
async def test_creator_finance_and_support_buttons_are_wired(monkeypatch):
    creator = SimpleNamespace(id="creator-id", role=UserRole.CREATOR)
    calls = {"finance": 0, "support": 0}

    async def fake_context(_event):
        return creator, "fa"

    async def fake_answer(_message, text, **kwargs):
        assert "گزارش و مالی" in text
        assert kwargs.get("reply_markup") is not None
        calls["finance"] += 1

    async def fake_help(_message):
        calls["support"] += 1

    monkeypatch.setattr(panel, "_get_context", fake_context)
    # «گزارش و مالی» opens its own report/wallet submenu (owner 2026-10-01).
    monkeypatch.setattr(Message, "answer", fake_answer)
    monkeypatch.setattr(help_handler, "help_command", fake_help)

    bot = Bot("123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
    bot._me = User(id=123456, is_bot=True, first_name="KhatmSaz", username="khatmsaz_test_bot")
    dp = Dispatcher(storage=MemoryStorage())
    panel.router._parent_router = None
    dp.include_router(panel.router)
    uid = 0
    try:
        # Every localized label of each button must reach its handler.
        for lang in ("fa", "ar", "en"):
            uid += 1
            await dp.feed_update(bot, _text_update(uid, t("menu.creator.finance", lang)))
            uid += 1
            await dp.feed_update(bot, _text_update(uid, t("menu.creator.support", lang)))
    finally:
        await bot.session.close()

    assert calls["finance"] == 3, "«گزارش و مالی» button did not reach a handler in every language"
    assert calls["support"] == 3, "«راهنما و پشتیبانی» button did not reach a handler in every language"
