"""Admin review UI for foreign phone numbers that cannot receive Iranian OTP."""

from uuid import UUID

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from khatmsaz.bot.keyboards import safe_answer_callback
from khatmsaz.bot.notify_adapter import get_notify_fn, send_with_keyboard
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.authorization.models import AdminPermission
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.manual_phone_verification import repository
from khatmsaz.modules.manual_phone_verification import service as manual_service
from khatmsaz.modules.settings import repository as settings_repository
from khatmsaz.modules.settings import service as settings_service

router = Router(name="manual_phone_verification")


def _decision_keyboard(request_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ تأیید هویت", callback_data=f"mpv:a:{request_id}"
                ),
                InlineKeyboardButton(
                    text="❌ رد درخواست", callback_data=f"mpv:r:{request_id}"
                ),
            ]
        ]
    )


async def notify_admins_of_manual_request(
    *, request_id, display_name: str | None, e164: str, purpose: str,
    sms_otp_expired: bool = False,
) -> None:
    admin_ids = [
        item.strip()
        for item in get_settings().super_admin_telegram_chat_ids.split(",")
        if item.strip()
    ]
    purpose_label = "تغییر شماره" if purpose == "PHONE_CHANGE" else "فعال‌سازی سازنده"
    request_title = (
        "⏱ درخواست تأیید دستی پس از نرسیدن/انقضای پیامک"
        if sms_otp_expired else "🌍 درخواست تأیید دستی شمارهٔ خارج از کشور"
    )
    text = (
        f"{request_title}\n\n"
        f"نام: {display_name or 'ثبت نشده'}\n"
        f"شماره: {e164}\n"
        f"هدف: {purpose_label}\n\n"
        "فقط بعد از بررسی واقعی مالکیت شماره، یکی از دکمه‌ها را بزنید."
    )
    keyboard = _decision_keyboard(request_id)
    for chat_id in admin_ids:
        await send_with_keyboard(Platform.TELEGRAM.value, chat_id, text, keyboard)


async def _authorized_admin(session, platform: Platform, subject: str):
    admin = await identity_service.find_by_platform(session, platform, subject)
    if not await authorization_service.has_permission(
        session, admin, AdminPermission.SUPPORT_USERS
    ):
        return None
    return admin


@router.message(Command("admin_phone_requests"))
async def list_manual_phone_requests(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        admin = await _authorized_admin(session, platform, str(message.chat.id))
        if admin is None:
            return
        requests = await repository.list_pending(session)
        rows = []
        for request in requests:
            user = await identity_service.find_by_id(session, request.user_id)
            profile = await settings_repository.get_by_user(session, request.user_id)
            rows.append((request, user, profile))
    if not rows:
        await message.answer("درخواست تأیید دستی شماره‌ای در انتظار نیست.")
        return
    await message.answer(f"{len(rows)} درخواست تأیید شماره در انتظار است:")
    for request, user, profile in rows:
        await message.answer(
            "🌍 درخواست تأیید دستی\n\n"
            f"نام: {user.display_name or 'ثبت نشده'}\n"
            f"شماره: {request.e164}\n"
            f"کشور/محل ثبت‌شده: {(profile.province if profile else None) or 'نامشخص'} / "
            f"{(profile.city if profile else None) or 'نامشخص'}\n"
            f"شناسه درخواست: {request.id}",
            reply_markup=_decision_keyboard(request.id),
        )


@router.callback_query(F.data.startswith("mpv:"))
async def decide_manual_phone_request(callback: CallbackQuery) -> None:
    try:
        _, decision, raw_id = callback.data.split(":", 2)
        request_id = UUID(raw_id)
    except (AttributeError, ValueError):
        await safe_answer_callback(callback, "درخواست نامعتبر است.", show_alert=True)
        return
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        async with session_scope() as session:
            admin = await _authorized_admin(session, platform, str(callback.from_user.id))
            if admin is None:
                await safe_answer_callback(callback, "اجازهٔ بررسی این درخواست را ندارید.", show_alert=True)
                return
            if decision == "a":
                request, _ = await manual_service.approve(
                    session, request_id=request_id, admin_user_id=admin.id
                )
            elif decision == "r":
                request = await manual_service.reject(
                    session,
                    request_id=request_id,
                    admin_user_id=admin.id,
                    note="رد توسط ادمین",
                )
            else:
                raise manual_service.ManualVerificationError("unknown decision")
            identities = await identity_service.list_identities_for_user(
                session, request.user_id
            )
            requester_settings = await settings_service.get_or_create(session, request.user_id)
            requester_lang = requester_settings.language
    except manual_service.ManualVerificationError as exc:
        await safe_answer_callback(
            callback, f"این درخواست قابل انجام نیست: {exc}", show_alert=True
        )
        return

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    approved = decision == "a"
    await safe_answer_callback(callback, "تأیید شد ✅" if approved else "رد شد.")
    text = (
        t("manual_phone_verification.approved_notice", requester_lang)
        if approved
        else t("manual_phone_verification.rejected_notice", requester_lang)
    )
    notify = get_notify_fn()
    for identity in identities:
        if approved and request.purpose == "CREATOR_VERIFY":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=t("manual_phone_verification.continue_button", requester_lang),
                    callback_data="phone_verify_continue",
                )
            ]])
            await send_with_keyboard(
                identity.platform.value, identity.subject, text, keyboard,
            )
        else:
            await notify(identity.platform.value, identity.subject, text)
