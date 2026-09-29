"""User feedback/bug-report inbox to admins (owner request, 2026-09-21).
Updated 2026-09-24: Participant tickets are routed to their Khatm creators.
Creator/Admin tickets go to Super Admins.
Creators can reply directly to participants via an inline button.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from khatmsaz.bot.keyboards import SUPPORT_BUTTON_TEXTS, CONTACT_CREATOR_BUTTON_TEXTS, bail_if_menu_button, home_keyboard_for_bot, main_menu_keyboard, safe_answer_callback, safe_clear_inline_keyboard
from khatmsaz.bot.notify_adapter import get_notify_fn, send_with_keyboard
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole, User, PlatformIdentity
from khatmsaz.modules.settings import service as settings_service
from sqlalchemy import func, select
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.khatm.models import Khatm
import logging
import uuid

logger = logging.getLogger("khatmsaz")
router = Router(name="suggestions")


class Suggestion(StatesGroup):
    entering_text = State()
    choosing_creator = State()
    replying_to_user = State()


async def _resolve_user_context(chat_id, bot) -> tuple[str, bool, bool, bool]:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        
        is_admin = user.role == UserRole.SUPER_ADMIN
        is_creator = user.role == UserRole.CREATOR
        
        is_participant = False
        if not is_admin and not is_creator:
            stmt = select(Participation).where(Participation.user_id == user.id, Participation.status == ParticipationStatus.ACTIVE)
            result = await session.execute(stmt)
            if result.first():
                is_participant = True
                
        return settings.language, is_participant, is_admin, is_creator


@router.message(F.text.in_(SUPPORT_BUTTON_TEXTS))
async def start_suggestion_message(message: Message, state: FSMContext) -> None:
    lang, is_participant, is_admin, is_creator = await _resolve_user_context(message.chat.id, message.bot)
    from khatmsaz.bot.keyboards import support_inline_keyboard
    await message.answer(t("support.menu_text", lang), reply_markup=support_inline_keyboard(lang, is_participant, is_admin, is_creator))


async def _member_creators(session, member_user_id):
    """Creators of the member's ACTIVE khatms, each with the member's own
    bot_instance_id for that khatm (so a reply can route back via the right
    member bot). Returns list of dicts {id, name, bot_instance_id}."""
    stmt = (
        select(
            User.id, User.display_name,
            func.max(Khatm.title), func.max(Participation.joined_via_bot_instance_id),
        )
        .select_from(Participation)
        .join(Khatm, Khatm.id == Participation.khatm_id)
        .join(User, User.id == Khatm.creator_user_id)
        .where(
            Participation.user_id == member_user_id,
            Participation.status == ParticipationStatus.ACTIVE,
        )
        .group_by(User.id, User.display_name)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {"id": r[0], "name": r[1] or r[2] or "سازنده", "bot_instance_id": r[3]}
        for r in rows
    ]


@router.message(F.text.in_(CONTACT_CREATOR_BUTTON_TEXTS))
async def start_creator_contact(message: Message, state: FSMContext) -> None:
    """Member → khatm creator (owner 2026-09-29). Members NEVER reach the
    super-admin here; they message the creator of a khatm they're in. If they
    are in khatms from several creators, they pick which one."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        creators = await _member_creators(session, user.id)

    from khatmsaz.bot.keyboards import home_keyboard_for_bot as _home
    if not creators:
        await message.answer(t("contact_creator.none", lang), reply_markup=_home(message.bot, lang))
        return
    if len(creators) == 1:
        c = creators[0]
        await state.set_state(Suggestion.entering_text)
        await state.update_data(
            lang=lang, target_creator_id=str(c["id"]),
            member_bot_instance_id=str(c["bot_instance_id"]) if c["bot_instance_id"] else None,
        )
        await message.answer(t("contact_creator.ask_text", lang, name=c["name"]))
        return
    await state.set_state(Suggestion.choosing_creator)
    await state.update_data(lang=lang, creator_instances={str(c["id"]): (str(c["bot_instance_id"]) if c["bot_instance_id"] else None) for c in creators})
    buttons = [[InlineKeyboardButton(text=c["name"], callback_data=f"suggest_to:{c['id']}")] for c in creators]
    await message.answer(t("contact_creator.pick", lang), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(F.data == "support:menu")
async def back_to_support_menu(callback: CallbackQuery, state: FSMContext) -> None:
    lang, is_participant, is_admin, is_creator = await _resolve_user_context(callback.message.chat.id, callback.bot)
    await state.clear()
    from khatmsaz.bot.keyboards import support_inline_keyboard
    await callback.message.edit_text(t("support.menu_text", lang), reply_markup=support_inline_keyboard(lang, is_participant, is_admin, is_creator))
    await safe_answer_callback(callback)


@router.callback_query(F.data == "suggest:start")
async def start_suggestion(callback: CallbackQuery, state: FSMContext) -> None:
    lang, _, _, _ = await _resolve_user_context(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        
        # If user is a Participant (not Creator/Admin), find their creators.
        if user.role == UserRole.USER:
            stmt = (
                select(User.id, User.display_name)
                .select_from(Participation)
                .join(Khatm, Khatm.id == Participation.khatm_id)
                .join(User, User.id == Khatm.creator_user_id)
                .where(Participation.user_id == user.id)
                .where(Participation.status == ParticipationStatus.ACTIVE)
                .group_by(User.id, User.display_name)
            )
            result = await session.execute(stmt)
            creators = result.all()
            
            if len(creators) == 1:
                # Only 1 creator, send to them
                await state.set_state(Suggestion.entering_text)
                await state.update_data(lang=lang, target_creator_id=str(creators[0].id))
                from khatmsaz.bot.keyboards import back_to_support_keyboard
                await callback.message.edit_text(
                    f"لطفاً پیام خود را برای سازنده «{creators[0].display_name or 'بدون نام'}» بنویسید:",
                    reply_markup=back_to_support_keyboard(lang)
                )
            elif len(creators) > 1:
                # Multiple creators -> select one
                await state.set_state(Suggestion.choosing_creator)
                await state.update_data(lang=lang)
                
                # Build inline keyboard
                buttons = []
                for cr in creators:
                    buttons.append([InlineKeyboardButton(text=cr.display_name or "سازنده بی‌نام", callback_data=f"suggest_to:{cr.id}")])
                buttons.append([InlineKeyboardButton(text=t("button.back", lang), callback_data="support:menu")])
                
                markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                await callback.message.edit_text(
                    "شما در ختم‌های مختلفی عضو هستید. لطفاً انتخاب کنید پیامتان به کدام سازنده ارسال شود:",
                    reply_markup=markup
                )
            else:
                # No active khatms (or fallback), route to Super Admin
                await state.set_state(Suggestion.entering_text)
                await state.update_data(lang=lang, target_creator_id="SUPER_ADMIN")
                from khatmsaz.bot.keyboards import back_to_support_keyboard
                await callback.message.edit_text(t("suggestions.ask_text", lang), reply_markup=back_to_support_keyboard(lang))
        else:
            # CREATOR or SUPER_ADMIN -> route to Super Admin
            await state.set_state(Suggestion.entering_text)
            await state.update_data(lang=lang, target_creator_id="SUPER_ADMIN")
            from khatmsaz.bot.keyboards import back_to_support_keyboard
            await callback.message.edit_text(t("suggestions.ask_text", lang), reply_markup=back_to_support_keyboard(lang))
            
    await safe_answer_callback(callback)


@router.callback_query(Suggestion.choosing_creator, F.data.startswith("suggest_to:"))
async def choose_creator(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "fa")
    
    target_creator_id = callback.data.split(":")[1]
    creator_instances = data.get("creator_instances", {})

    await state.set_state(Suggestion.entering_text)
    await state.update_data(
        target_creator_id=target_creator_id,
        member_bot_instance_id=creator_instances.get(target_creator_id),
    )

    from khatmsaz.bot.keyboards import back_to_support_keyboard
    await callback.message.edit_text(
        "حالا پیام خود را بنویسید:",
        reply_markup=back_to_support_keyboard(lang)
    )
    await safe_answer_callback(callback)


@router.message(Suggestion.entering_text)
async def receive_suggestion(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    target_creator_id = data.get("target_creator_id", "SUPER_ADMIN")
    text = (message.text or "").strip()
    
    if not text:
        await message.answer(t("suggestions.text_required", lang))
        return
    if len(text) > 1000:
        await message.answer(t("suggestions.text_too_long", lang))
        return

    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        display_name = user.display_name or t("suggestions.default_name", lang)
        
        await audit_service.record(
            session, actor_user_id=user.id, action="USER_SUGGESTION", details={"text": text, "target": target_creator_id},
        )
        
        if target_creator_id == "SUPER_ADMIN":
            admin_ids = [
                item.strip() for item in get_settings().super_admin_telegram_chat_ids.split(",") if item.strip()
            ]
            notify = get_notify_fn()
            admin_text = t("suggestions.admin_notice", "fa", name=display_name, text=text)
            for chat_id in admin_ids:
                await notify(Platform.TELEGRAM.value, chat_id, admin_text)
        else:
            # Send to creator using their primary platform identity
            creator = await session.get(User, uuid.UUID(target_creator_id))
            if creator:
                # Find creator's platform identity
                stmt = select(PlatformIdentity).where(PlatformIdentity.user_id == creator.id).order_by(PlatformIdentity.created_at.desc()).limit(1)
                result = await session.execute(stmt)
                creator_pid = result.scalar_one_or_none()
                
                if creator_pid:
                    admin_text = f"📩 پیام جدید از طرف عضو ختم‌های شما ({display_name}):\n\n{text}"
                    
                    # Inline button to reply
                    markup = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="پاسخ به این کاربر", callback_data=f"reply_user:{user.id}")]
                        ]
                    )
                    
                    await send_with_keyboard(creator_pid.platform.value, creator_pid.subject, admin_text, markup)

    await state.clear()
    await message.answer(t("suggestions.submitted", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))


@router.callback_query(F.data.startswith("reply_user:"))
async def start_reply_to_user(callback: CallbackQuery, state: FSMContext) -> None:
    target_user_id = callback.data.split(":")[1]
    
    # Store in state
    await state.set_state(Suggestion.replying_to_user)
    await state.update_data(reply_target_user_id=target_user_id)
    
    await callback.message.answer("متن پاسخ خود را بنویسید (برای لغو /cancel را بفرستید):")
    await safe_answer_callback(callback)


@router.message(Suggestion.replying_to_user)
async def receive_reply(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
        
    data = await state.get_data()
    target_user_id = data.get("reply_target_user_id")
    text = (message.text or "").strip()
    
    if not text:
        await message.answer("لطفاً متن بفرستید.")
        return
        
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        sender = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)

        target_user = await session.get(User, uuid.UUID(target_user_id))

        if target_user:
            # CRITICAL (owner 2026-09-29): the member uses a MEMBER bot; a reply
            # sent from the creator bot can't reach them (a bot can't message a
            # user who never started it). Route the reply through the exact member
            # bot the member joined via, per platform.
            member_bot_by_platform = {}
            inst_rows = (await session.execute(
                select(PlatformIdentity.platform, Participation.joined_via_bot_instance_id)
                .select_from(Participation)
                .join(Khatm, Khatm.id == Participation.khatm_id)
                .join(PlatformIdentity, PlatformIdentity.user_id == Participation.user_id)
                .where(
                    Participation.user_id == target_user.id,
                    Khatm.creator_user_id == sender.id,
                    Participation.status == ParticipationStatus.ACTIVE,
                    Participation.joined_via_bot_instance_id.isnot(None),
                )
            )).all()
            for plat, inst in inst_rows:
                member_bot_by_platform[plat.value if hasattr(plat, "value") else plat] = inst

            stmt = select(PlatformIdentity).where(PlatformIdentity.user_id == target_user.id).order_by(PlatformIdentity.created_at.desc())
            identities = list((await session.execute(stmt)).scalars())

            if identities:
                notify = get_notify_fn()
                reply_text = f"📨 پیام از طرف سازندهٔ ختم شما ({sender.display_name or 'سازنده'}):\n\n{text}"
                delivered = False
                for pid in identities:
                    inst = member_bot_by_platform.get(pid.platform.value)
                    try:
                        await notify(pid.platform.value, pid.subject, reply_text, bot_instance_id=inst)
                        delivered = True
                    except Exception as e:
                        logger.error(f"Failed to send reply to user {target_user_id} on {pid.platform.value}: {e}")
                if delivered:
                    await message.answer("پاسخ شما با موفقیت به کاربر ارسال شد.", reply_markup=home_keyboard_for_bot(message.bot, "fa"))
                else:
                    await message.answer("خطا در ارسال پیام به کاربر.")
            else:
                await message.answer("پلتفرم این کاربر یافت نشد.")
        else:
            await message.answer("کاربر یافت نشد یا اکانتش معتبر نیست.")
            
    await state.clear()
