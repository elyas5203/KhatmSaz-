"""Small participant-facing reminder preference command."""

from aiogram import F, Router
from aiogram.types import Message

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings import service as settings_service

router = Router(name="reminder_settings")


@router.message(F.text.startswith("/reminder"))
async def set_reminder(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    value = parts[1].strip().lower() if len(parts) == 2 else ""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        participations = await participation_service.list_my_active(session, user.id)
        committed = [p for p in participations if p.is_committed]
        if value == "off":
            for participation in committed:
                await notification_service.set_reminder_preference(
                    session, participation.id, reminder_hour=9, enabled=False
                )
            await message.answer(t("reminder_settings.turned_off", lang))
            return
        if not value.isdigit() or not 0 <= int(value) <= 23:
            await message.answer(t("reminder_settings.usage", lang))
            return
        hour = int(value)
        for participation in committed:
            await notification_service.set_reminder_preference(
                session, participation.id, reminder_hour=hour, enabled=True
            )
    await message.answer(t("reminder_settings.saved", lang, hour=hour))
