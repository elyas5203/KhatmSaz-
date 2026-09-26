from html import escape
from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from khatmsaz.bot.keyboards import member_menu_keyboard, join_preview_keyboard, pack_join_callback_data
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.invitation.service import InvitationExpiredError, InvitationNotFoundError
from khatmsaz.modules.khatm.models import Khatm, KhatmTypeEnum, KhatmVisibility
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.bot.handlers.start import build_join_preview_message, JoinWorkflow

router = Router(name="member_start")

@router.message(CommandStart(deep_link=True))
async def handle_member_start_with_payload(message: Message, command: CommandObject, state: FSMContext) -> None:
    await state.clear()
    bot = message.bot
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = getattr(bot, "khatmsaz_language", "fa")
    bot_category = getattr(bot, "khatmsaz_category", None)
    
    payload = command.args or ""
    
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        
        if payload.startswith("join_"):
            token = payload.removeprefix("join_")
            try:
                khatm_id = await invitation_service.resolve_khatm_id(session, token)
            except InvitationNotFoundError:
                await message.answer(t("join.error.invalid_link", lang), reply_markup=member_menu_keyboard(lang))
                return
            except InvitationExpiredError:
                await message.answer(t("join.error.expired_link", lang), reply_markup=member_menu_keyboard(lang))
                return
            
            khatm = await khatm_service.get_khatm_by_id(session, khatm_id)
            if not khatm or not khatm.is_active:
                await message.answer(t("join.error.khatm_inactive", lang), reply_markup=member_menu_keyboard(lang))
                return
                
            if khatm.is_ended:
                await message.answer(t("join.error.khatm_finished", lang), reply_markup=member_menu_keyboard(lang))
                return
                
            from khatmsaz.modules.bot_registry.models import BotCategory
            
            # Determine Khatm's bot category
            khatm_bot_cat = None
            if khatm.template_type in [KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.QURAN_SURAH]:
                khatm_bot_cat = BotCategory.QURAN.value
            else:
                cat = await category_service.get_category(session, khatm.content_category_id)
                if cat:
                    if cat.group.name == "SALAWAT":
                        khatm_bot_cat = BotCategory.SALAWAT.value
                    elif cat.group.name == "LAAN":
                        khatm_bot_cat = BotCategory.LAAN.value
                    elif cat.group.name == "DUA":
                        khatm_bot_cat = BotCategory.DUA_ZIYARAT.value
            
            if bot_category and khatm_bot_cat != bot_category.value:
                await message.answer("این ختم مربوط به بات دیگری است.", reply_markup=member_menu_keyboard(lang))
                return
                
            cat = None
            if khatm.content_category_id:
                cat = await category_service.get_category(session, khatm.content_category_id)
                
            if khatm.allowed_platforms and platform.name not in khatm.allowed_platforms:
                pl_name = "بله" if platform == Platform.TELEGRAM else "تلگرام"
                await message.answer(t("join.error.wrong_platform", lang, platform=pl_name), reply_markup=member_menu_keyboard(lang))
                return
                
            creator = await identity_service.get_user(session, khatm.creator_id)
            from khatmsaz.bot.handlers.start import _creator_display_name
            creator_name = _creator_display_name(khatm, creator)
            
            from khatmsaz.modules.participation import service as participation_service
            stats = await participation_service.get_khatm_participation_stats(session, khatm.id)
            
            text = build_join_preview_message(
                khatm, creator_name, stats.total_members, lang,
                category_title=cat.title if cat else None, category_group=cat.group.name if cat else None
            )
            
            await state.update_data(
                pending_join_khatm_id=khatm_id,
                joined_via_bot_instance_id=getattr(bot, "khatmsaz_instance_id", None)
            )
            await state.set_state(JoinWorkflow.previewing)
            
            kb = join_preview_keyboard(khatm_id, lang)
            # pack data for base64 limits if needed, handled in keyboards
            await message.answer(text, reply_markup=kb)

@router.message(CommandStart())
async def handle_member_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    bot = message.bot
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = getattr(bot, "khatmsaz_language", "fa")
    bot_category = getattr(bot, "khatmsaz_category", None)
    
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
    
    welcome_text = "سلام!\nبا لینک دعوت می‌توانید در ختم شرکت کنید."
    
    async with session_scope() as session:
        # List public khatms of this category
        from khatmsaz.modules.khatm.repository import get_recent_khatms
        khatms = await get_recent_khatms(session, limit=5, visibility=KhatmVisibility.PUBLIC)
        public_buttons = []
        for k in khatms:
            cat = await category_service.get_category(session, k.content_category_id)
            if bot_category and cat.group.name == bot_category.name:
                public_buttons.append([InlineKeyboardButton(text=k.title, callback_data=pack_join_callback_data(k.id))])
    
    kb = InlineKeyboardMarkup(inline_keyboard=public_buttons) if public_buttons else None
    
    await message.answer(welcome_text, reply_markup=member_menu_keyboard(lang))
    if kb:
        await message.answer("ختم‌های عمومی:", reply_markup=kb)

@router.callback_query(F.data.startswith("join:"), JoinWorkflow.previewing)
@router.callback_query(F.data.startswith("join_b64:"), JoinWorkflow.previewing)
async def handle_member_join_callback(callback: CallbackQuery, state: FSMContext) -> None:
    from khatmsaz.bot.keyboards import unpack_join_callback_data, safe_clear_inline_keyboard
    from khatmsaz.modules.settings import service as settings_service
    from khatmsaz.bot.handlers.member_registration import start_member_registration
    from khatmsaz.bot.handlers.start import resume_join_after_registration

    token = unpack_join_callback_data(callback.data)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        await safe_clear_inline_keyboard(callback.message)
        
        if not await settings_service.is_registered(session, user.id) or not user.display_name:
            await start_member_registration(callback.message, state, pending_join_token=token)
        else:
            await resume_join_after_registration(callback.message, session, user.id, token, state=state)
    await callback.answer()

@router.callback_query(F.data == "join_cancel", JoinWorkflow.previewing)
async def handle_member_join_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    from khatmsaz.bot.keyboards import safe_clear_inline_keyboard
    lang = getattr(callback.message.bot, "khatmsaz_language", "fa")
    await safe_clear_inline_keyboard(callback.message)
    await state.clear()
    await callback.message.answer(t("join.canceled", lang), reply_markup=member_menu_keyboard(lang))
    await callback.answer()
