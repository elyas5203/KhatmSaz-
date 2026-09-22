"""Request-a-khatm-type flow (DOMAIN_MODEL.md §2). A user submits a
free-text description; an admin lists pending requests and approves/rejects
with a note, which notifies the requester on whichever platform they're on.

`/request_khatm` is a typed command, not a menu button — matches
DOMAIN_MODEL.md's framing as a fallback path ("if what you want isn't in
the list"), not a primary flow, so it doesn't earn Home-menu space.

The submitter-facing part is fully localized. The admin-only commands
(`/admin_requests`, `/admin_approve_request`, `/admin_reject_request`)
keep their Persian text — same treatment as `admin.py` — but the
notification sent back to the requester after a decision is always in
*their* own language, since that's the actual end user.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import bail_if_menu_button, main_menu_keyboard, safe_answer_callback, safe_clear_inline_keyboard
from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.authorization.models import AdminPermission
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.khatm_request import service as khatm_request_service
from khatmsaz.modules.settings import service as settings_service

router = Router(name="khatm_request")

_SKIP_WORDS = {"ندارم", "خیر", "نه", "skip", "none", "no", "ليس لدي", "لا"}


class RequestKhatm(StatesGroup):
    entering_description = State()
    entering_attachment = State()


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


async def _submit_request(message: Message, description: str, lang: str, **attachment) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        await khatm_request_service.submit(session, user.id, description, **attachment)
    text = t("khatm_request.submitted", lang)
    if attachment.get("attachment_file_id"):
        text += t("khatm_request.attachment_saved", lang)
    await message.answer(text, reply_markup=main_menu_keyboard(lang))


@router.callback_query(F.data == "request_khatm:start")
async def request_khatm_start(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await state.set_state(RequestKhatm.entering_description)
    await state.update_data(lang=lang)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("khatm_request.ask_description", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(RequestKhatm.entering_description))
async def request_khatm_description(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    description = (message.text or "").strip()
    if not description:
        await message.answer(t("khatm_request.description_required", lang))
        return
    await state.update_data(request_description=description)
    await state.set_state(RequestKhatm.entering_attachment)
    await message.answer(t("khatm_request.ask_attachment", lang))


@router.message(StateFilter(RequestKhatm.entering_attachment), F.document)
async def request_khatm_document(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "fa")
    document = message.document
    await _submit_request(
        message, data["request_description"], lang,
        attachment_file_id=document.file_id,
        attachment_file_name=document.file_name,
        attachment_mime_type=document.mime_type,
        attachment_platform=getattr(getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM), "value", "TELEGRAM"),
    )
    await state.clear()


@router.message(StateFilter(RequestKhatm.entering_attachment), F.photo)
async def request_khatm_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "fa")
    photo = message.photo[-1]
    await _submit_request(
        message, data["request_description"], lang,
        attachment_file_id=photo.file_id,
        attachment_file_name=None,
        attachment_mime_type="image/jpeg",
        attachment_platform=getattr(getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM), "value", "TELEGRAM"),
    )
    await state.clear()


@router.message(StateFilter(RequestKhatm.entering_attachment))
async def request_khatm_without_attachment(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    if (message.text or "").strip().lower() not in _SKIP_WORDS:
        await message.answer(t("khatm_request.attachment_or_skip", lang))
        return
    await _submit_request(message, data["request_description"], lang)
    await state.clear()


@router.message(Command("request_khatm"))
async def request_khatm(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    description = (command.args or "").strip()
    if not description:
        await message.answer(t("khatm_request.usage_hint", lang))
        return
    await _submit_request(message, description, lang)


@router.message(Command("admin_requests"))
async def admin_list_requests(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if not await authorization_service.has_permission(
            session, admin, AdminPermission.CONTENT_MANAGE
        ):
            return

        pending = await khatm_request_service.list_pending(session)

    if not pending:
        await message.answer("درخواستی وجود نداره.")
        return

    lines = ["درخواست‌های در انتظار بررسی:\n"]
    for request in pending:
        attachment = " 📎 فایل پیوست دارد" if request.attachment_file_id else ""
        lines.append(f"#{request.id}{attachment}\n{request.description}\n")
    lines.append(
        "برای تایید: /admin_approve_request <id> <یادداشت اختیاری>\n"
        "برای رد: /admin_reject_request <id> <یادداشت اختیاری>"
    )
    await message.answer("\n".join(lines))
    # The file ID is platform-scoped and can be replayed by Telegram without
    # downloading user content to our server. This happens only after the
    # permission check above, directly to the reviewing admin.
    for request in pending:
        if not request.attachment_file_id:
            continue
        caption = f"پیوست درخواست #{request.id}\n{request.description[:700]}"
        try:
            if request.attachment_mime_type == "image/jpeg":
                await message.bot.send_photo(
                    chat_id=message.chat.id, photo=request.attachment_file_id, caption=caption
                )
            else:
                await message.bot.send_document(
                    chat_id=message.chat.id, document=request.attachment_file_id, caption=caption
                )
        except Exception:
            # A file can expire or be inaccessible after a platform migration;
            # the textual queue entry remains available for the admin.
            await message.answer(f"پیوست درخواست #{request.id} قابل ارسال نبود؛ شناسه در دیتابیس محفوظ است.")


async def _resolve_decision(message: Message, command: CommandObject) -> tuple[str, str] | None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if not await authorization_service.has_permission(
            session, admin, AdminPermission.CONTENT_MANAGE
        ):
            return None

    args = (command.args or "").strip()
    if not args:
        return None
    parts = args.split(maxsplit=1)
    request_id = parts[0]
    note = parts[1] if len(parts) > 1 else ""
    return request_id, note


@router.message(Command("admin_approve_request"))
async def admin_approve_request(message: Message, command: CommandObject) -> None:
    parsed = await _resolve_decision(message, command)
    if parsed is None:
        return
    request_id, note = parsed
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        request = await khatm_request_service.get(session, request_id)
        if request is None:
            await message.answer("این درخواست پیدا نشد.")
            return
        await khatm_request_service.approve(session, request_id, note or None)
        await audit_service.record(session, actor_user_id=admin.id, action="KHATM_REQUEST_APPROVE", target_user_id=request.requester_user_id, details={"request_id": request_id, "note": note})
        identities = await identity_service.list_identities_for_user(session, request.requester_user_id)
        requester_settings = await settings_service.get_or_create(session, request.requester_user_id)
        requester_lang = requester_settings.language

    await message.answer("درخواست تایید شد ✅ به کاربر خبر داده شد.")
    notify = get_notify_fn()
    text = t("khatm_request.approved_notice", requester_lang, description=request.description)
    if note:
        text += t("khatm_request.admin_note_line", requester_lang, note=note)
    for identity in identities:
        await notify(identity.platform.value, identity.subject, text)


@router.message(Command("admin_reject_request"))
async def admin_reject_request(message: Message, command: CommandObject) -> None:
    parsed = await _resolve_decision(message, command)
    if parsed is None:
        return
    request_id, note = parsed
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        request = await khatm_request_service.get(session, request_id)
        if request is None:
            await message.answer("این درخواست پیدا نشد.")
            return
        await khatm_request_service.reject(session, request_id, note or None)
        await audit_service.record(session, actor_user_id=admin.id, action="KHATM_REQUEST_REJECT", target_user_id=request.requester_user_id, details={"request_id": request_id, "note": note})
        identities = await identity_service.list_identities_for_user(session, request.requester_user_id)
        requester_settings = await settings_service.get_or_create(session, request.requester_user_id)
        requester_lang = requester_settings.language

    await message.answer("درخواست رد شد؛ به کاربر خبر داده شد.")
    notify = get_notify_fn()
    text = t("khatm_request.rejected_notice", requester_lang, description=request.description)
    if note:
        text += t("khatm_request.reason_line", requester_lang, note=note)
    for identity in identities:
        await notify(identity.platform.value, identity.subject, text)
