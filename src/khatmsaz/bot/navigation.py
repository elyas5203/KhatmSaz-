"""Shared navigation recovery helpers, independent from handler routers."""

from aiogram.types import Message, ReplyKeyboardRemove

from khatmsaz.bot.keyboards import main_menu_keyboard, member_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.settings import service as settings_service


def home_markup_for_role(lang: str, role: UserRole):
    """Return the approved home markup for each formal role experience.

    The repository has no approved Super Admin reply-menu composition. Admins
    enter through the existing `/admin_web_login` flow, so recovery removes a
    stale wizard keyboard instead of incorrectly showing creator controls.
    """
    return main_menu_keyboard(lang, is_creator=role == UserRole.CREATOR, is_admin=role == UserRole.SUPER_ADMIN)


async def resolve_home_navigation(message: Message, lang: str | None = None):
    bot = message.bot
    bot_role = getattr(bot, "khatmsaz_role", None)

    if bot_role is not None and str(bot_role) == "MEMBER":
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
