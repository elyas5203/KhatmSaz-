"""Per-user reading text-size preference."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from khatmsaz.bot.keyboards import main_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import FontSize

router = Router(name="font_settings")


@router.message(Command("font"))
async def set_font(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
    value = (command.args or "").strip().lower()
    if value not in {"normal", "large"}:
        await message.answer(t("font_settings.usage", lang))
        return
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        await settings_service.set_font_size(session, user.id, FontSize(value.upper()))
    label = t("font_settings.label_normal", lang) if value == "normal" else t("font_settings.label_large", lang)
    await message.answer(t("font_settings.saved", lang, label=label), reply_markup=main_menu_keyboard(lang))
