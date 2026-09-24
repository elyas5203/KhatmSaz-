from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from aiogram import Bot, Dispatcher
from aiogram.enums import MessageEntityType
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, MessageEntity, Update, User

from khatmsaz.bot.handlers import profile, public_khatms, start
from khatmsaz.modules.identity.models import UserRole


def _command_update(update_id: int, text: str, *, chat_id: int = 7001) -> Update:
    return Update(
        update_id=update_id,
        message=Message(
            message_id=update_id,
            date=datetime.now(timezone.utc),
            chat=Chat(id=chat_id, type="private"),
            from_user=User(id=chat_id, is_bot=False, first_name="Test"),
            text=text,
            entities=[MessageEntity(type=MessageEntityType.BOT_COMMAND, offset=0, length=len(text.split()[0]))],
        ),
    )


@pytest.mark.asyncio
async def test_dispatcher_routes_commands_while_profile_phone_state_is_active(monkeypatch):
    """Regression for /profile → /start|/cancel|/public_khatms routing."""
    user = SimpleNamespace(id="user-id", role=UserRole.USER)
    settings = SimpleNamespace(language="fa", language_prompted=True)
    answers = []

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs):
        return user

    async def fake_settings(*args, **kwargs):
        return settings

    async def no_public_khatms(*args, **kwargs):
        return []

    async def capture_answer(self, text, **kwargs):
        answers.append((text, kwargs))
        return self

    for module in (start, profile, public_khatms):
        monkeypatch.setattr(module, "session_scope", fake_scope)
    monkeypatch.setattr(start.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(start.settings_service, "get_or_create", fake_settings)
    monkeypatch.setattr(profile.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(profile.settings_service, "get_or_create", fake_settings)
    monkeypatch.setattr(public_khatms.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(public_khatms.settings_service, "get_or_create", fake_settings)
    monkeypatch.setattr(public_khatms.khatm_service, "list_public_active", no_public_khatms)
    monkeypatch.setattr(Message, "answer", capture_answer)

    bot = Bot("123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
    bot._me = User(id=123456, is_bot=True, first_name="KhatmSaz", username="khatmsaz_test_bot")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(public_khatms.router)
    context = dp.fsm.get_context(bot=bot, chat_id=7001, user_id=7001)
    try:
        await context.set_state(profile.ProfileEdit.entering_phone)
        await dp.feed_update(bot, _command_update(1, "/start"))
        assert await context.get_state() is None
        assert answers[-1][0].startswith("سلام")

        await context.set_state(profile.ProfileEdit.entering_phone)
        await dp.feed_update(bot, _command_update(2, "/cancel"))
        assert await context.get_state() is None
        assert "لغو شد" in answers[-1][0]

        await context.set_state(profile.ProfileEdit.entering_phone)
        await dp.feed_update(bot, _command_update(3, "/public_khatms"))
        assert await context.get_state() == profile.ProfileEdit.entering_phone.state
        assert "ختم عمومی فعالی" in answers[-1][0]

        # A representative profile command must be routed as a command, not
        # normalized as a phone number by the active state's text handler.
        await context.set_state(profile.ProfileEdit.entering_phone)
        await dp.feed_update(bot, _command_update(4, "/profile"))
        assert await context.get_state() == profile.ProfileEdit.entering_name.state
    finally:
        await bot.session.close()
