"""Regression: the «🕋 ختم‌های عمومی» reply button (menu.public_khatms) was
only wired as a /public_khatms Command, so tapping the reply button in the
participant/member menu did nothing. This feeds the button text through a
real Dispatcher and asserts the list handler fires."""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, Update, User

from khatmsaz.bot.handlers import public_khatms
from khatmsaz.i18n import t


def _text_update(update_id: int, text: str, chat_id: int = 9202) -> Update:
    return Update(
        update_id=update_id,
        message=Message(
            message_id=update_id,
            date=datetime.now(timezone.utc),
            chat=Chat(id=chat_id, type="private"),
            from_user=User(id=chat_id, is_bot=False, first_name="Member"),
            text=text,
        ),
    )


@pytest.mark.asyncio
async def test_public_khatms_reply_button_is_wired(monkeypatch):
    answers = []

    async def fake_lang(_chat_id, _bot):
        return "fa"

    async def fake_list_public_active(*_a, **_k):
        return []  # exercise the "none active" branch — still a real response

    async def capture_answer(self, text, **kwargs):
        answers.append(text)
        return self

    monkeypatch.setattr(public_khatms, "_lang_for", fake_lang)
    monkeypatch.setattr(public_khatms.khatm_service, "list_public_active", fake_list_public_active)
    monkeypatch.setattr(Message, "answer", capture_answer)

    bot = Bot("123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
    bot._me = User(id=123456, is_bot=True, first_name="KhatmSaz", username="khatmsaz_test_bot")
    dp = Dispatcher(storage=MemoryStorage())
    # Detach the singleton router from any Dispatcher a prior test attached it
    # to (e.g. test_navigation_dispatcher) so include_router doesn't raise.
    public_khatms.router._parent_router = None
    dp.include_router(public_khatms.router)
    try:
        for lang in ("fa", "ar", "en"):
            await dp.feed_update(bot, _text_update(hash(lang) % 10000, t("menu.public_khatms", lang)))
    finally:
        await bot.session.close()

    assert len(answers) == 3, "«ختم‌های عمومی» reply button did not reach the handler in every language"
    assert all(a == t("public_khatms.none_active", "fa") for a in answers)
