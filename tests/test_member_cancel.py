"""Regression: /cancel had no handler on member bots, so a member could get
stuck mid-registration/join (owner+Codex live QA). /cancel must clear the FSM
state and return the member menu."""
from datetime import datetime, timezone

import pytest
from aiogram import Bot, Dispatcher
from aiogram.enums import MessageEntityType
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, MessageEntity, Update, User

from khatmsaz.bot.handlers import member_start
from khatmsaz.bot.handlers.member_registration import MemberRegistration


def _cancel_update(update_id: int, chat_id: int = 9505) -> Update:
    return Update(
        update_id=update_id,
        message=Message(
            message_id=update_id,
            date=datetime.now(timezone.utc),
            chat=Chat(id=chat_id, type="private"),
            from_user=User(id=chat_id, is_bot=False, first_name="Member"),
            text="/cancel",
            entities=[MessageEntity(type=MessageEntityType.BOT_COMMAND, offset=0, length=7)],
        ),
    )


@pytest.mark.asyncio
async def test_member_cancel_clears_state(monkeypatch):
    answers = []

    async def capture(self, text, **kwargs):
        answers.append(text)
        return self
    monkeypatch.setattr(Message, "answer", capture)

    bot = Bot("123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
    bot._me = User(id=123456, is_bot=True, first_name="KhatmSaz", username="khatmsaz_test_bot")
    bot.khatmsaz_language = "fa"  # type: ignore[attr-defined]
    dp = Dispatcher(storage=MemoryStorage())
    member_start.router._parent_router = None
    dp.include_router(member_start.router)

    ctx = dp.fsm.get_context(bot=bot, chat_id=9505, user_id=9505)
    try:
        await ctx.set_state(MemberRegistration.entering_name)  # stuck mid-registration
        await dp.feed_update(bot, _cancel_update(1))
        assert await ctx.get_state() is None, "/cancel did not clear the member FSM state"
        assert answers, "/cancel produced no reply on the member bot"
    finally:
        await bot.session.close()
