from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from khatmsaz.bot.keyboards import (
    creator_management_keyboard,
    creator_finance_keyboard,
    creator_support_keyboard,
    main_menu_keyboard,
)
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t, variants
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.settings import service as settings_service

router = Router(name="creator_menu")


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language

@router.message(F.text.in_(variants("menu.creator.management")))
async def handle_creator_management(message: Message) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await message.answer(
        t("text.creator.management", lang),
        reply_markup=creator_management_keyboard(lang)
    )

@router.message(F.text.in_(variants("menu.creator.finance")))
async def handle_creator_finance(message: Message) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await message.answer(
        t("text.creator.finance", lang),
        reply_markup=creator_finance_keyboard(lang)
    )

@router.message(F.text.in_(variants("menu.creator.support")))
async def handle_creator_support(message: Message) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await message.answer(
        t("text.creator.support", lang),
        reply_markup=creator_support_keyboard(lang)
    )

@router.message(F.text.in_(variants("menu.back_to_main")))
async def handle_back_to_main(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await state.clear()
    
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        is_creator = user.role == UserRole.CREATOR
        is_admin = user.role == UserRole.SUPER_ADMIN

    await message.answer(
        t("welcome.text", lang),
        reply_markup=main_menu_keyboard(lang, is_creator=is_creator, is_admin=is_admin)
    )
