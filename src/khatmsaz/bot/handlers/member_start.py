"""Member bot /start handler — for category-specific member bots.

Mirrors the creator bot's start.py but uses member_menu_keyboard and
the bot-level language instead of per-user settings.
"""
from html import escape

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from khatmsaz.bot.keyboards import member_menu_keyboard, join_preview_keyboard, safe_clear_inline_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.invitation.service import InvitationExpiredError, InvitationNotFoundError
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.bot.handlers.start import build_join_preview_message, JoinWorkflow, _creator_display_name

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

            khatm = await khatm_service.get_khatm(session, khatm_id)
            if khatm is None or khatm.status == KhatmStatus.CANCELLED:
                await message.answer(t("join.error.khatm_gone", lang), reply_markup=member_menu_keyboard(lang))
                return

            if khatm.status == KhatmStatus.COMPLETED:
                await message.answer(t("join.error.khatm_ended", lang), reply_markup=member_menu_keyboard(lang))
                return

            from khatmsaz.modules.bot_registry.models import BotCategory

            # Determine Khatm's bot category
            khatm_bot_cat = None
            if khatm.template_type in [KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.QURAN_SURAH]:
                khatm_bot_cat = BotCategory.QURAN.value
            else:
                cat_obj = await category_service.get(session, khatm.content_category_id) if khatm.content_category_id else None
                if cat_obj:
                    if cat_obj.group.name == "SALAWAT":
                        khatm_bot_cat = BotCategory.SALAWAT.value
                    elif cat_obj.group.name == "LAAN":
                        khatm_bot_cat = BotCategory.LAAN.value
                    elif cat_obj.group.name == "DUA":
                        khatm_bot_cat = BotCategory.DUA_ZIYARAT.value

            if bot_category and khatm_bot_cat != bot_category:
                await message.answer(t("join.error.wrong_bot", lang), reply_markup=member_menu_keyboard(lang))
                return

            cat = None
            if khatm.content_category_id:
                cat = await category_service.get(session, khatm.content_category_id)

            allowed_p = getattr(khatm, "allowed_platforms", "BOTH")
            if allowed_p != "BOTH" and allowed_p != platform.value:
                await message.answer(
                    t("join.error.platform_restricted", lang, platform=allowed_p),
                    reply_markup=member_menu_keyboard(lang),
                )
                return

            creator = await identity_service.find_by_id(session, khatm.creator_user_id)
            creator_name = _creator_display_name(khatm, creator)

            member_count = await participation_service.count_for_khatm(session, khatm.id)

            text = build_join_preview_message(
                khatm, creator_name, member_count, lang,
                category_title=cat.title if cat else None, category_group=cat.group.name if cat else None
            )

            await state.update_data(
                pending_join_khatm_id=str(khatm_id),
                joined_via_bot_instance_id=getattr(bot, "khatmsaz_instance_id", None)
            )
            await state.set_state(JoinWorkflow.previewing)

            kb = join_preview_keyboard(token, lang)
            await message.answer(text, reply_markup=kb)


@router.message(Command("cancel"))
async def handle_member_cancel(message: Message, state: FSMContext) -> None:
    """`/cancel` on a member bot: escape any active flow (registration, join,
    reminder-hour…) and return to the member menu. Previously only the creator
    bot had a /cancel handler, so a member could get stuck mid-registration
    (owner/Codex live QA)."""
    await state.clear()
    lang = getattr(message.bot, "khatmsaz_language", "fa")
    await message.answer(t("navigation.cancelled", lang), reply_markup=member_menu_keyboard(lang))


@router.message(CommandStart())
async def handle_member_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    bot = message.bot
    lang = getattr(bot, "khatmsaz_language", "fa")

    await message.answer(t("member.welcome", lang), reply_markup=member_menu_keyboard(lang))


@router.callback_query(F.data.startswith("join_preview:"))
async def handle_member_join_callback(callback: CallbackQuery, state: FSMContext) -> None:
    # NOTE: intentionally NOT filtered on `JoinWorkflow.previewing`. The token
    # is carried in the callback data, so this must work even after the FSM
    # state is gone — e.g. the service was restarted between showing the
    # preview and the user tapping "شرکت" (MemoryStorage is wiped on restart).
    # The creator-side handler (`start.accept_join_preview`) is likewise
    # state-independent; the member one used to require the state, so on a
    # member bot the join button silently died after any restart.
    from khatmsaz.modules.settings import service as settings_service
    from khatmsaz.bot.handlers.member_registration import start_member_registration
    from khatmsaz.bot.handlers.start import resume_join_after_registration

    token = callback.data.split(":", 1)[1]
    if token == "cancel":
        lang = getattr(callback.message.bot, "khatmsaz_language", "fa")
        await safe_clear_inline_keyboard(callback.message)
        await state.clear()
        await callback.message.answer(t("join.cancelled", lang), reply_markup=member_menu_keyboard(lang))
        await callback.answer()
        return

    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        await safe_clear_inline_keyboard(callback.message)

        if not await settings_service.is_registered(session, user.id) or not user.display_name:
            await start_member_registration(callback.message, state, pending_join_token=token)
        else:
            await resume_join_after_registration(callback.message, session, user.id, token, state=state)
    await callback.answer()
