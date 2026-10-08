"""Plain-language, button-driven help for inexperienced bot users."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import (
    ABOUT_US_BUTTON_TEXTS,
    HELP_BUTTON_TEXTS,
    help_keyboard,
    help_create_actions_keyboard,
    help_manage_actions_keyboard,
    help_settings_actions_keyboard,
    help_wallet_actions_keyboard,
    safe_answer_callback,
)
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="help")

# fa fallback text for callers that don't (yet) have a resolved user
# language — see docs/ai/I18N_MIGRATION.md for the conversion pattern.
HELP_HOME = t("help.home", "fa")

_TOPIC_KEYS = {
    "join": "help.join",
    "portion": "help.portion",
    "create": "help.create",
    "wallet": "help.wallet",
    "settings": "help.settings",
    "manage": "help.manage",
}

# fa-only view of the topic texts, kept for tests/tools that inspect the
# Persian baseline content directly (see tests/test_help.py).
HELP_TOPICS = {topic: t(key, "fa") for topic, key in _TOPIC_KEYS.items()}


from khatmsaz.modules.identity.models import Platform, UserRole

async def _resolve_user_info(message: Message) -> tuple[str, bool, bool]:
    # Member bots: language is fixed per bot, and members are never creators/admins.
    bot_lang = getattr(message.bot, "khatmsaz_language", None)
    if bot_lang:
        return bot_lang, False, False

    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        is_creator = user.role in (UserRole.CREATOR, UserRole.SUPER_ADMIN)
        is_admin = user.role == UserRole.SUPER_ADMIN
        return settings.language, is_creator, is_admin


@router.message(Command("help"))
@router.message(F.text.in_(HELP_BUTTON_TEXTS))
async def help_command(message: Message) -> None:
    lang, is_creator, is_admin = await _resolve_user_info(message)
    await message.answer(t("help.home", lang), reply_markup=help_keyboard(lang, is_creator, is_admin))


@router.callback_query(F.data.startswith("help:"))
async def help_topic(callback: CallbackQuery) -> None:
    topic = callback.data.split(":", 1)[1]
    lang, is_creator, is_admin = await _resolve_user_info(callback.message)
    text = t("help.home", lang) if topic == "home" else t(_TOPIC_KEYS.get(topic, "help.home"), lang)
    keyboard = (
        help_wallet_actions_keyboard(lang) if topic == "wallet"
        else help_settings_actions_keyboard(lang) if topic == "settings"
        else help_create_actions_keyboard(lang) if topic == "create"
        else help_manage_actions_keyboard(lang, is_creator, is_admin) if topic == "manage"
        else help_keyboard(lang, is_creator, is_admin)
    )
    await callback.message.answer(text, reply_markup=keyboard)
    await safe_answer_callback(callback)


@router.callback_query(F.data == "create:start_from_help")
async def help_start_creation(callback: CallbackQuery, state: FSMContext) -> None:
    if getattr(callback.bot, "khatmsaz_language", None):
        # Member bot — creation is not available here
        await safe_answer_callback(callback, "ساخت ختم از این ربات امکان‌پذیر نیست.")
        return
    # Route through the same verified-phone creation entry point as the Home
    # button, without asking an inexperienced user to hunt for that button.
    from khatmsaz.bot.handlers.create_khatm import start_wizard

    await start_wizard(callback.message, state)
    await safe_answer_callback(callback)


@router.callback_query(F.data == "my_khatms:open")
async def help_open_my_khatms(callback: CallbackQuery) -> None:
    from khatmsaz.bot.handlers.my_khatms import list_my_khatms

    await list_my_khatms(callback.message)
    await safe_answer_callback(callback)


@router.message(F.text.in_(ABOUT_US_BUTTON_TEXTS))
async def about_us_command(message: Message) -> None:
    lang, _, _ = await _resolve_user_info(message)
    await message.answer(t("about_us.text", lang))
