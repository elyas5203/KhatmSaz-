"""Participant-facing SMS opt-in, kept separate from the vendor boundary.

SMS reminders now require a paid, time-limited subscription (owner
decision, 2026-09-20) — this typed command is a compatibility fallback for
`/sms off` and pointing `/sms on` users to the button-driven purchase flow
in `settings_menu.py`; it never silently turns SMS on for free.
"""

from aiogram import Router
from aiogram.types import Message

from khatmsaz.bot.keyboards import home_keyboard_for_bot, main_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="sms_settings")


@router.message(lambda message: message.text and message.text.startswith("/sms"))
async def set_sms(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    value = parts[1].strip().lower() if len(parts) == 2 else ""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    bot_lang = getattr(message.bot, "khatmsaz_language", None)
    if bot_lang:
        lang = bot_lang
    else:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
            settings = await settings_service.get_or_create(session, user.id)
            lang = settings.language
    if value not in {"on", "off"}:
        await message.answer(t("sms_settings.usage", lang))
        return
    if value == "on":
        await message.answer(
            t("sms_settings.on_redirect", lang, settings_button=t("menu.settings", lang))
        )
        return
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        try:
            await settings_service.set_sms_enabled(session, user.id, False)
        except ValueError:
            pass
    await message.answer(t("sms_settings.turned_off", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
