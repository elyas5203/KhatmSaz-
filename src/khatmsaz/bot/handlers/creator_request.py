"""Creator role request flow.

Users who want to create khatms must request the CREATOR role.
An admin reviews the request and approves/rejects it.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import CREATOR_REQUEST_BUTTON_TEXTS, main_menu_keyboard, safe_answer_callback
from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.creator_request import service as request_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.settings import service as settings_service

router = Router(name="creator_request")


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


@router.callback_query(F.data == "creator_request:start")
async def handle_creator_request_button(callback: CallbackQuery) -> None:
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    chat_id = callback.message.chat.id
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        
        from khatmsaz.bot.keyboards import back_to_support_keyboard
        is_creator = user.role in (UserRole.CREATOR, UserRole.SUPER_ADMIN)
        if is_creator:
            await callback.message.edit_text(
                t("creator_request.approved", lang), 
                reply_markup=back_to_support_keyboard(lang)
            )
            await callback.answer()
            return

        if await request_service.has_pending_request(session, user.id):
            await callback.message.edit_text(
                t("creator_request.already_pending", lang),
                reply_markup=back_to_support_keyboard(lang)
            )
            await callback.answer()
            return
            
        try:
            req = await request_service.submit_request(session, user.id)
            request_id = req.id
        except request_service.AlreadyCreatorError:
            await callback.message.edit_text(
                t("creator_request.approved", lang), 
                reply_markup=back_to_support_keyboard(lang)
            )
            await callback.answer()
            return
        except request_service.PendingRequestExistsError:
            await callback.message.edit_text(
                t("creator_request.already_pending", lang),
                reply_markup=back_to_support_keyboard(lang)
            )
            await callback.answer()
            return

    # Notify admins
    admin_ids = [
        item.strip() for item in get_settings().super_admin_telegram_chat_ids.split(",") if item.strip()
    ]
    notify = get_notify_fn()
    display_name = user.display_name or "کاربر"
    admin_text = (
        f"درخواست سازنده‌شدن جدید از {display_name} (ID: {user.id})\n\n"
        f"برای تایید:\n/admin_approve_creator {request_id}\n\n"
        f"برای رد:\n/admin_reject_creator {request_id}"
    )
    # We could send inline keyboard to approve/reject, but for now just text to admins, 
    # they can use admin panel or command later.
    for admin_id in admin_ids:
        await notify(Platform.TELEGRAM.value, admin_id, admin_text)

    await callback.message.edit_text(t("creator_request.submitted", lang), reply_markup=back_to_support_keyboard(lang))
    await callback.answer()

from aiogram.filters import Command, CommandObject
from khatmsaz.bot.filters import AdminFilter

@router.message(Command("admin_approve_creator"), AdminFilter())
async def admin_approve_creator(message: Message, command: CommandObject) -> None:
    args = (command.args or "").split(maxsplit=1)
    if not args:
        await message.answer("Usage: /admin_approve_creator <request_id> [note]")
        return
    
    import uuid
    try:
        request_id = uuid.UUID(args[0])
    except ValueError:
        await message.answer("Invalid UUID")
        return
    note = args[1] if len(args) > 1 else None

    async with session_scope() as session:
        platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        reviewer = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        
        req = await request_service.approve_request(session, request_id, reviewer.id, note=note)
        if not req:
            await message.answer("Request not found or not pending.")
            return
        
        await message.answer(f"Approved creator request for user {req.user_id}")
        
        # Notify the user
        notify = get_notify_fn()
        user_settings = await settings_service.get_or_create(session, req.user_id)
        user = await identity_service.find_by_id(session, req.user_id)
        if user and user.platform_identities:
            pi = user.platform_identities[0]
            await notify(pi.platform.value, pi.subject, t("creator_request.approved", user_settings.language))


@router.message(Command("admin_reject_creator"), AdminFilter())
async def admin_reject_creator(message: Message, command: CommandObject) -> None:
    args = (command.args or "").split(maxsplit=1)
    if not args:
        await message.answer("Usage: /admin_reject_creator <request_id> [note]")
        return
    
    import uuid
    try:
        request_id = uuid.UUID(args[0])
    except ValueError:
        await message.answer("Invalid UUID")
        return
    note = args[1] if len(args) > 1 else None

    async with session_scope() as session:
        platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        reviewer = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        
        req = await request_service.reject_request(session, request_id, reviewer.id, note=note)
        if not req:
            await message.answer("Request not found or not pending.")
            return
            
        await message.answer(f"Rejected creator request for user {req.user_id}")
