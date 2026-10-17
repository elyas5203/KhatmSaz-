"""Member bot /start handler — for category-specific member bots.

Mirrors the creator bot's start.py but uses member_menu_keyboard and
the bot-level language instead of per-user settings.
"""
from html import escape

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from khatmsaz.bot.keyboards import CUSTOM_KHATM_BUTTON_TEXTS, commitment_consent_keyboard, member_menu_keyboard, safe_clear_inline_keyboard
from khatmsaz.bot import invite_links
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.invitation.service import InvitationExpiredError, InvitationNotFoundError
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.bot.handlers.start import build_join_consent_message, JoinWorkflow, _creator_display_name, _is_commitment
from khatmsaz.modules.system_settings import service as system_settings_service

router = Router(name="member_start")


@router.message(F.text.in_(CUSTOM_KHATM_BUTTON_TEXTS))
async def custom_khatm_contact(message: Message) -> None:
    """Give members the admin-managed contact for a bespoke khatm request."""
    lang = getattr(message.bot, "khatmsaz_language", "fa")
    async with session_scope() as session:
        phone = await system_settings_service.get_str(session, "custom_khatm_admin_phone")
    key = "custom_khatm.contact" if phone else "custom_khatm.unavailable"
    await message.answer(
        t(key, lang, phone=phone) if phone else t(key, lang),
        reply_markup=member_menu_keyboard(lang),
    )


async def _matches_member_bot(session, khatm: Khatm, bot_category: str | None) -> bool:
    """Keep invite generation and member-bot admission on one category rule."""
    if not bot_category:
        return True
    return await invite_links.resolve_khatm_category_value(session, khatm) == bot_category


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
            except invitation_service.InvitationTransferredError as err:
                khatm = await khatm_service.get_khatm(session, err.khatm_id)
                if khatm is None or khatm.status != KhatmStatus.ACTIVE:
                    await message.answer(t("join.error.invalid_link", lang), reply_markup=member_menu_keyboard(lang))
                    return

                existing_p = await participation_service.get_active(session, khatm.id, user.id)
                if existing_p is not None:
                    await message.answer(
                        "🌱 <b>شما از قبل عضو فعال این ختم هستید</b>\n\n"
                        f"مدیریت ختم «{escape(khatm.title)}» به مجموعه خدمتگزاران تک واگذار گردیده و به عنوان ختم عمومی ادامه دارد.\n"
                        "سهم‌های تلاوت شما کاملاً محفوظ است و بدون وقفه می‌توانید به قرائت روزانه خود ادامه دهید.",
                        reply_markup=member_menu_keyboard(lang),
                    )
                    return

                new_token = await invitation_service.get_or_create_for_khatm(session, khatm.id, khatm.creator_user_id)
                khatm_bot_cat = await invite_links.resolve_khatm_category_value(session, khatm)
                by_lang = invite_links.build_member_invite_links(khatm_bot_cat, new_token)
                new_links_formatted = invite_links.format_invite_lines(by_lang)

                from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🌱 پیوستن به این ختم عمومی", callback_data=f"public_join:{khatm.id}")],
                    ]
                )
                await message.answer(
                    "📢 <b>مدیریت این ختم به مجموعه «خدمتگزاران تک» واگذار شده است</b>\n\n"
                    f"ختم «{escape(khatm.title)}» با تصمیم سازنده و تأیید پشتیبانی، به یک <b>ختم عمومی</b> تبدیل شده و لینک ورود قبلی منقضی گردیده است.\n\n"
                    "شما می‌توانید با لینک عمومی جدید و یا دکمه زیر، وارد این ختم عمومی شوید:\n\n"
                    f"{new_links_formatted}",
                    reply_markup=kb,
                )
                return
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

            if getattr(khatm, "join_link_closed", False):
                existing_p = await participation_service.get_active(session, khatm.id, user.id)
                if existing_p is None:
                    await message.answer(
                        "⚠️ <b>امکان عضویت جدید در این ختم وجود ندارد</b>\n\n"
                        "لینک عضویت این ختم توسط مدیریت بسته شده است و اعضای قبلی در حال تکمیل قرائت روزانه خود هستند.\n\n"
                        "جهت شرکت در سایر ختم‌ها می‌توانید از منوی اصلی ربات اقدام فرمایید.",
                        reply_markup=member_menu_keyboard(lang),
                    )
                    return

            if not await _matches_member_bot(session, khatm, bot_category):
                await message.answer(t("join.error.wrong_bot", lang), reply_markup=member_menu_keyboard(lang))
                return

            allowed_p = getattr(khatm, "allowed_platforms", "BOTH")
            if allowed_p != "BOTH" and allowed_p != platform.value:
                await message.answer(
                    t("join.error.platform_restricted", lang, platform=allowed_p),
                    reply_markup=member_menu_keyboard(lang),
                )
                return

            # The first message is fixed context + an explicit rules gate. It
            # stays above the separate, updating question message.
            instance_id = getattr(bot, "khatmsaz_instance_id", None)
            await state.update_data(
                # RedisStorage serializes FSM data as JSON.  SQLAlchemy UUIDs
                # therefore must cross this boundary as strings.
                joined_via_bot_instance_id=str(instance_id) if instance_id else None
            )
            creator = await identity_service.find_by_id(session, khatm.creator_user_id)
            member_count = await participation_service.count_for_khatm(session, khatm.id)
            category_title = None
            category_group = None
            if khatm.template_type == KhatmTemplateType.SALAWAT:
                if khatm.content_category_id:
                    from khatmsaz.modules.khatm_category import service as category_service
                    category = await category_service.get(session, khatm.content_category_id)
                    if category is not None:
                        category_title = category.title
                        category_group = category.group.value
                else:
                    category_group = "SALAWAT"
            await state.update_data(pending_commitment_token=token)
            await message.answer(
                build_join_consent_message(
                    khatm, _creator_display_name(khatm, creator), member_count, lang,
                    category_title=category_title, category_group=category_group,
                ),
                reply_markup=commitment_consent_keyboard(
                    token, lang, committed=_is_commitment(khatm),
                ),
            )


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
