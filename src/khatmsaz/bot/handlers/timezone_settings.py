"""Per-user IANA timezone preference for scheduled reminders."""

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="timezone_settings")


@router.message(Command("timezone"))
async def timezone_command(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    value = (command.args or "").strip()
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        if not value:
            await message.answer(t("timezone_settings.current", lang, timezone=settings.timezone))
            return
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            await message.answer(t("timezone_settings.invalid", lang))
            return
        await settings_service.set_timezone(session, user.id, value)
    await message.answer(t("timezone_settings.saved", lang, timezone=value))
