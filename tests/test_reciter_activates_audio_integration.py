"""Owner-reported bug (2026-09-21): "قاری رو فعال میکنم اما برام صوت
ارسال نمیشه" — picking a reciter (either via the ⚙️ تنظیمات inline menu
or the typed `/reciter` command) never turned on `UserSettings.quran_audio_enabled`,
a separate flag defaulting to False and buried in a different settings
screen — so audio was silently never sent no matter which reciter was
picked. See `bot/handlers/settings_menu.py::set_reciter` and
`bot/handlers/reciter_settings.py::set_reciter`."""

from types import SimpleNamespace

import pytest
from sqlalchemy import delete

from khatmsaz.bot.handlers.reciter_settings import set_reciter as set_reciter_command
from khatmsaz.bot.handlers.settings_menu import set_reciter as set_reciter_callback
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import UserSettings


class FakeMessage:
    def __init__(self, chat_id):
        self.chat = SimpleNamespace(id=chat_id)
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM)

    async def answer(self, *args, **kwargs):
        pass

    async def edit_text(self, *args, **kwargs):
        pass


class FakeCallback:
    def __init__(self, chat_id, data):
        self.data = data
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM)
        self.message = FakeMessage(chat_id)

    async def answer(self, *args, **kwargs):
        pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_picking_a_reciter_via_settings_menu_turns_on_audio():
    chat_id = 9_810_000_001
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
        settings = await settings_service.set_quran_audio_enabled(session, user.id, False)
        assert settings.quran_audio_enabled is False
        user_id = user.id

    await set_reciter_callback(FakeCallback(chat_id, "set_reciter:parhizgar"))

    async with session_scope() as session:
        settings = await settings_service.get_or_create(session, user_id)
        assert settings.quran_audio_enabled is True
        assert settings.preferred_reciter == "parhizgar"

        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_picking_a_reciter_via_typed_command_turns_on_audio():
    chat_id = 9_810_000_002
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
        settings = await settings_service.set_quran_audio_enabled(session, user.id, False)
        assert settings.quran_audio_enabled is False
        user_id = user.id

    command = SimpleNamespace(args="parhizgar")
    await set_reciter_command(FakeMessage(chat_id), command)

    async with session_scope() as session:
        settings = await settings_service.get_or_create(session, user_id)
        assert settings.quran_audio_enabled is True

        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
