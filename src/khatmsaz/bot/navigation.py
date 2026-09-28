"""Shared navigation recovery helpers, independent from handler routers."""

from aiogram.types import Message, ReplyKeyboardRemove

from khatmsaz.bot.keyboards import is_member_bot, main_menu_keyboard, member_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.settings import service as settings_service


def home_markup_for_role(lang: str, role: UserRole):
    """Creator-bot home is fixed; the formal account role does not alter it.

    The admin panel is deliberately absent from the persistent chat menu and
    remains available only through the permission-gated ``/admin_app``.
    """
    return main_menu_keyboard(lang)


async def resolve_home_navigation(message: Message, lang: str | None = None):
    bot = message.bot

    if is_member_bot(bot):
        if lang is None:
            lang = getattr(bot, "khatmsaz_language", "fa")
        return lang, None, member_menu_keyboard(lang)

    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        if lang is None:
            settings = await settings_service.get_or_create(session, user.id)
            lang = settings.language
    return lang, user.role, home_markup_for_role(lang, user.role)
