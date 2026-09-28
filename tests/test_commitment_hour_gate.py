"""Regression (owner live QA 2026-09-28): right after joining a commitment
khatm the bot asks the daily reminder hour. Tapping «ثبت بخشی از تعهد» before
answering used to switch the FSM to LogContribution.entering_amount, so the
number the user typed (the hour) was swallowed as the commitment quantity.
The contribute button must be blocked until the hour is set."""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from khatmsaz.bot.handlers import portions
from khatmsaz.bot.handlers.start import AskDeliveryHour
from khatmsaz.bot.handlers.portions import LogContribution


def _callback_update(update_id: int, data: str, chat_id: int = 9404) -> Update:
    msg = Message(
        message_id=update_id,
        date=datetime.now(timezone.utc),
        chat=Chat(id=chat_id, type="private"),
        from_user=User(id=chat_id, is_bot=False, first_name="Member"),
        text="_",
    )
    return Update(
        update_id=update_id,
        callback_query=CallbackQuery(
            id=str(update_id),
            from_user=User(id=chat_id, is_bot=False, first_name="Member"),
            chat_instance="ci",
            data=data,
            message=msg,
        ),
    )


@pytest.mark.asyncio
async def test_contribute_blocked_until_delivery_hour_set(monkeypatch):
    async def fake_lang(*_a, **_k):
        return "fa"
    monkeypatch.setattr(portions, "_lang_for", fake_lang)

    async def capture_answer(self, *a, **k):
        return self
    monkeypatch.setattr(Message, "answer", capture_answer)

    async def ok_ack(*a, **k):
        return None
    monkeypatch.setattr(portions, "safe_answer_callback", ok_ack)

    bot = Bot("123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
    bot._me = User(id=123456, is_bot=True, first_name="KhatmSaz", username="khatmsaz_test_bot")
    dp = Dispatcher(storage=MemoryStorage())
    portions.router._parent_router = None
    dp.include_router(portions.router)

    ctx = dp.fsm.get_context(bot=bot, chat_id=9404, user_id=9404)
    try:
        # Pending delivery-hour, exactly like right after a fresh join.
        await ctx.set_state(AskDeliveryHour.entering_hour)
        await dp.feed_update(bot, _callback_update(1, "commitment_contribute:some-khatm"))
        # The gate must NOT switch us into the quantity-entry state.
        assert await ctx.get_state() == AskDeliveryHour.entering_hour.state
        assert await ctx.get_state() != LogContribution.entering_amount.state
    finally:
        await bot.session.close()
