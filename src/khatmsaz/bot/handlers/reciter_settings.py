"""Per-user Quran reciter favorite."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from khatmsaz.bot.keyboards import main_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="reciter_settings")


@router.message(Command("reciter"))
async def set_reciter(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
    value = (command.args or "").strip().lower()
    if not value:
        options = "، ".join(f"{key} ({name})" for key, name in content_service.list_reciters())
        await message.answer(t("reciter_settings.usage", lang, options=options))
        return
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        try:
            await content_service.set_user_favorite(session, user.id, value)
        except ValueError:
            await message.answer(t("reciter_settings.invalid", lang))
            return
        # See settings_menu.py::set_reciter for why — picking a reciter
        # means "I want audio", so turn the separate audio-enabled flag
        # on too instead of leaving it silently off.
        await settings_service.set_quran_audio_enabled(session, user.id, True)
    await message.answer(
        t("reciter_settings.saved", lang, name=content_service.SYSTEM_RECITERS[value]),
        reply_markup=main_menu_keyboard(lang),
    )
