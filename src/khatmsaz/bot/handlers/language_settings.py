"""Participant-facing language preference."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="language_settings")
_LABEL_KEYS = {"fa": "language_settings.label.fa", "ar": "language_settings.label.ar", "en": "language_settings.label.en"}


@router.message(Command("language"))
async def language_command(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    value = (command.args or "").strip().lower()
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        if not value:
            label = t(_LABEL_KEYS.get(settings.language, _LABEL_KEYS["fa"]), lang)
            await message.answer(t("language_settings.current", lang, label=label, code=settings.language))
            return
        if value not in settings_service.SUPPORTED_LANGUAGES:
            await message.answer(t("language_settings.invalid", lang))
            return
        await settings_service.set_language(session, user.id, value)
    await message.answer(t("language_settings.saved", value, label=t(_LABEL_KEYS[value], value)))
