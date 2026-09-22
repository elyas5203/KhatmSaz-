"""Per-user daily reminder digest preference."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="digest_settings")


@router.message(Command("digest"))
async def digest_command(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    value = (command.args or "").strip().lower()
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        if not value:
            state = t("digest_settings.status_on", lang) if settings.daily_digest_enabled else t("digest_settings.status_off", lang)
            await message.answer(t("digest_settings.current_status", lang, state=state))
            return
        if value not in {"on", "off"}:
            await message.answer(t("digest_settings.usage", lang))
            return
        settings.daily_digest_enabled = value == "on"
        await session.flush()
    await message.answer(t("digest_settings.turned_on", lang) if value == "on" else t("digest_settings.turned_off", lang))
