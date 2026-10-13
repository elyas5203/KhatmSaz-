"""Dedicated Admin Bot (@khatmsaz_admin_bot) router and command dashboard.

Hosted exclusively on @khatmsaz_admin_bot (DEC-PY-0125, MASTER-12).
Restricted strictly to Super Admins.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from html import escape
import os
import sys
from uuid import UUID

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from sqlalchemy import func, select

from khatmsaz.config import get_settings
from khatmsaz.core.bot_registry import get_registry
from khatmsaz.core.db import session_scope
from khatmsaz.core.logging_system import (
    get_log_file_paths,
    get_recent_errors,
    get_recent_logs,
)
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import WalletReceiptClaim, ReceiptClaimStatus
from khatmsaz.bot import invite_links

router = Router(name="admin_bot")


async def _is_super_admin(message_or_callback: Message | CallbackQuery) -> bool:
    """Check if the sender is authorized as a Super Admin."""
    chat_id = str(message_or_callback.from_user.id)
    settings = get_settings()
    env_admins = {v.strip() for v in settings.super_admin_telegram_chat_ids.split(",") if v.strip()}
    if chat_id in env_admins:
        return True

    try:
        async with session_scope() as session:
            stmt = (
                select(User.role)
                .join(PlatformIdentity, PlatformIdentity.user_id == User.id)
                .where(
                    PlatformIdentity.platform == Platform.TELEGRAM,
                    PlatformIdentity.subject == chat_id,
                )
            )
            role = (await session.execute(stmt)).scalar_one_or_none()
            if role == UserRole.SUPER_ADMIN:
                return True
    except Exception:
        pass

    return False


async def _reject_unauthorized(message_or_callback: Message | CallbackQuery) -> None:
    text = "⛔️ <b>دسترسی غیرمجاز</b>\n\nاین ربات اختصاصی مدیریت سیستم ختم‌ساز است و شما دسترسی لازم برای استفاده از آن را ندارید."
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.answer("دسترسی غیرمجاز.", show_alert=True)
    else:
        await message_or_callback.answer(text)


async def _fetch_dashboard_counts() -> dict[str, int]:
    """Fetch live counts for the admin dashboard."""
    counts = {
        "pending_receipts": 0,
        "pending_laan": 0,
        "pending_broadcasts": 0,
        "active_khatms": 0,
        "total_users": 0,
    }
    try:
        async with session_scope() as session:
            # 1. Pending receipts
            r_stmt = select(func.count(WalletReceiptClaim.id)).where(
                WalletReceiptClaim.status == ReceiptClaimStatus.PENDING.value
            )
            counts["pending_receipts"] = (await session.execute(r_stmt)).scalar() or 0

            # 2. Pending La'n khatms
            l_stmt = select(func.count(Khatm.id)).where(
                Khatm.pending_lan_approval.is_(True)
            )
            counts["pending_laan"] = (await session.execute(l_stmt)).scalar() or 0

            # 3. Pending broadcasts
            counts["pending_broadcasts"] = len(await broadcast_service.list_pending_review(session))

            # 4. Active khatms
            k_stmt = select(func.count(Khatm.id)).where(Khatm.status == KhatmStatus.ACTIVE)
            counts["active_khatms"] = (await session.execute(k_stmt)).scalar() or 0

            # 5. Total users
            u_stmt = select(func.count(User.id))
            counts["total_users"] = (await session.execute(u_stmt)).scalar() or 0
    except Exception:
        pass
    return counts


def _build_dashboard_keyboard(counts: dict[str, int]) -> InlineKeyboardMarkup:
    receipts_btn = f"🧾 فیش‌های واریزی ({counts['pending_receipts']})"
    laan_btn = f"⚔️ ختم‌های لعن ({counts['pending_laan']})"
    broadcast_btn = f"📢 پیام‌های همگانی ({counts['pending_broadcasts']})"

    rows = [
        [
            InlineKeyboardButton(text=receipts_btn, callback_data="admin:receipts"),
            InlineKeyboardButton(text=laan_btn, callback_data="admin:laan"),
        ],
        [
            InlineKeyboardButton(text=broadcast_btn, callback_data="admin:broadcasts"),
            InlineKeyboardButton(text="📊 وضعیت زنده سرور", callback_data="admin:status"),
        ],
        [
            InlineKeyboardButton(text="📑 مشاهده لاگ‌ها", callback_data="admin:logs"),
            InlineKeyboardButton(text="🚨 آخرین خطاها", callback_data="admin:errors"),
        ],
        [
            InlineKeyboardButton(text="🔄 بروزرسانی آمار", callback_data="admin:refresh"),
        ],
    ]

    base_url = get_settings().admin_web_base_url.rstrip("/")
    if base_url.lower().startswith("https://"):
        login_url = f"{base_url}/mini/admin"
        rows.append([
            InlineKeyboardButton(text="🌐 ورود به پنل تحت وب", web_app=WebAppInfo(url=login_url))
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("start", "admin", "menu"))
async def admin_start_handler(message: Message) -> None:
    if not await _is_super_admin(message):
        await _reject_unauthorized(message)
        return

    counts = await _fetch_dashboard_counts()
    name = (getattr(message.from_user, "full_name", None) if message.from_user else None) or "مدیر گرامی"

    text = (
        f"👑 <b>سامانه مدیریت مرکزی ختم‌ساز</b>\n\n"
        f"سلام <b>{escape(name)}</b> عزیز، خوش آمدید.\n"
        f"این ربات مرکز کنترل و پایش اختصاصی تمامی بخش‌های ختم‌ساز است.\n\n"
        f"📊 <b>خلاصه وضعیت کارتابل:</b>\n"
        f"• 🧾 فیش‌های واریزی در انتظار: <b>{counts['pending_receipts']}</b>\n"
        f"• ⚔️ ختم‌های لعن در انتظار تأیید: <b>{counts['pending_laan']}</b>\n"
        f"• 📢 پیام‌های همگانی در انتظار: <b>{counts['pending_broadcasts']}</b>\n"
        f"• 📖 ختم‌های فعال: <b>{counts['active_khatms']}</b>\n"
        f"• 👥 کل کاربران سامانه: <b>{counts['total_users']:,}</b>\n\n"
        f"👇 لطفاً بخش مورد نظر خود را انتخاب فرمایید:"
    )

    await message.answer(text, reply_markup=_build_dashboard_keyboard(counts))


@router.callback_query(F.data == "admin:refresh")
async def admin_refresh_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    counts = await _fetch_dashboard_counts()
    name = callback.from_user.full_name or "مدیر گرامی"
    text = (
        f"👑 <b>سامانه مدیریت مرکزی ختم‌ساز</b>\n\n"
        f"سلام <b>{escape(name)}</b> عزیز، خوش آمدید.\n"
        f"این ربات مرکز کنترل و پایش اختصاصی تمامی بخش‌های ختم‌ساز است.\n\n"
        f"📊 <b>خلاصه وضعیت کارتابل (بروزرسانی شد):</b>\n"
        f"• 🧾 فیش‌های واریزی در انتظار: <b>{counts['pending_receipts']}</b>\n"
        f"• ⚔️ ختم‌های لعن در انتظار تأیید: <b>{counts['pending_laan']}</b>\n"
        f"• 📢 پیام‌های همگانی در انتظار: <b>{counts['pending_broadcasts']}</b>\n"
        f"• 📖 ختم‌های فعال: <b>{counts['active_khatms']}</b>\n"
        f"• 👥 کل کاربران سامانه: <b>{counts['total_users']:,}</b>\n\n"
        f"👇 لطفاً بخش مورد نظر خود را انتخاب فرمایید:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=_build_dashboard_keyboard(counts))
    except Exception:
        pass
    await callback.answer("آمار بروزرسانی شد ✅")


# --- Receipts Handlers ---

@router.message(Command("receipts"))
@router.callback_query(F.data == "admin:receipts")
async def admin_receipts_handler(event: Message | CallbackQuery) -> None:
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    message = event if not isinstance(event, CallbackQuery) else event.message

    async with session_scope() as session:
        stmt = (
            select(WalletReceiptClaim, User)
            .join(User, User.id == WalletReceiptClaim.user_id)
            .where(WalletReceiptClaim.status == ReceiptClaimStatus.PENDING.value)
            .order_by(WalletReceiptClaim.created_at.asc())
            .limit(10)
        )
        claims = (await session.execute(stmt)).all()

    if not claims:
        text = "✅ <b>هیچ فیش واریزی در انتظار بررسی وجود ندارد.</b>\nکارتابل مالی خالی است."
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="admin:refresh")]])
        if isinstance(event, CallbackQuery):
            await message.edit_text(text, reply_markup=kb)
            await event.answer()
        else:
            await message.answer(text, reply_markup=kb)
        return

    for claim, user in claims:
        tracking_code = str((claim.id.int % 90000000) + 10000000)
        time_str = claim.created_at.strftime("%Y-%m-%d %H:%M")
        caption = (
            "🧾 <b>فیش در انتظار بررسی</b>\n\n"
            f"👤 کاربر: <b>{escape(user.display_name or 'نامشخص')}</b> (شناسه: <code>{user.id}</code>)\n"
            f"💰 مبلغ اعلام‌شده: <b>{claim.amount_toman:,} تومان</b>\n"
            f"🆔 کد رهگیری: <code>{tracking_code}</code>\n"
            f"📅 زمان ثبت: <code>{time_str}</code>\n\n"
            "وضعیت را مشخص کنید:"
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ تأیید و شارژ کیف پول", callback_data=f"receipt:approve:{claim.id}"),
                    InlineKeyboardButton(text="❌ رد فیش", callback_data=f"receipt:reject:{claim.id}"),
                ]
            ]
        )
        await message.answer(caption, reply_markup=markup)

    if isinstance(event, CallbackQuery):
        await event.answer()


# --- La'n Khatms Handlers ---

@router.message(Command("laan"))
@router.callback_query(F.data == "admin:laan")
async def admin_laan_handler(event: Message | CallbackQuery) -> None:
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    message = event if not isinstance(event, CallbackQuery) else event.message

    async with session_scope() as session:
        stmt = (
            select(Khatm, User)
            .join(User, User.id == Khatm.creator_user_id)
            .where(Khatm.pending_lan_approval.is_(True))
            .order_by(Khatm.created_at.asc())
            .limit(10)
        )
        khatms = (await session.execute(stmt)).all()

    if not khatms:
        text = "✅ <b>هیچ ختم لعن در انتظار تأییدی وجود ندارد.</b>\nکارتابل نظارت پاک است."
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="admin:refresh")]])
        if isinstance(event, CallbackQuery):
            await message.edit_text(text, reply_markup=kb)
            await event.answer()
        else:
            await message.answer(text, reply_markup=kb)
        return

    for khatm, user in khatms:
        text = (
            "⚔️ <b>درخواست تأیید ختم لعن سفارشی</b>\n\n"
            f"📌 <b>عنوان:</b> {escape(khatm.title)}\n"
            f"👤 <b>سازنده:</b> {escape(user.display_name or 'نامشخص')}\n"
            f"📜 <b>متن ذکر لعن:</b>\n<blockquote>{escape(khatm.recitation_text or '—')}</blockquote>\n"
            f"🎯 <b>نیت:</b> {escape(khatm.niyyat or '—')}\n"
            f"📅 <b>نوع:</b> {'تعهدی' if khatm.khatm_type.value == 'COMMITMENT' else 'آزاد'}\n\n"
            "آیا این ختم و ذکر لعن مورد تأیید است؟"
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ تأیید و فعال‌سازی", callback_data=f"laan:approve:{khatm.id}"),
                    InlineKeyboardButton(text="❌ رد کردن", callback_data=f"laan:reject:{khatm.id}"),
                ]
            ]
        )
        await message.answer(text, reply_markup=markup)

    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(F.data.startswith("laan:approve:"))
async def approve_laan_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    raw_id = callback.data.split(":", 2)[2]
    try:
        khatm_id = UUID(raw_id)
    except ValueError:
        await callback.answer("شناسه معتبر نیست.", show_alert=True)
        return

    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(
            session, Platform.TELEGRAM, str(callback.from_user.id)
        )
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if not khatm:
            await callback.answer("ختم یافت نشد.", show_alert=True)
            return

        khatm.pending_lan_approval = False
        khatm.status = KhatmStatus.ACTIVE
        await session.flush()

        # Audit log
        if admin_user:
            await audit_service.record(
                session, actor_user_id=admin_user.id, target_khatm_id=khatm.id,
                action="LAAN_KHATM_APPROVE", details={"khatm_id": str(khatm.id)},
            )

        # Generate invite token & links
        token = await invitation_service.create_invitation(session, khatm.id, khatm.creator_user_id)
        cat_val = await invite_links.resolve_khatm_category_value(session, khatm)
        by_lang = invite_links.build_member_invite_links(cat_val, token)
        invite_lines_str = invite_links.format_invite_lines(by_lang)
        creator_user_id = khatm.creator_user_id
        khatm_title = khatm.title
        khatm_niyyat = khatm.niyyat

    await callback.message.edit_text(
        f"✅ ختم «<b>{escape(khatm_title)}</b>» تأیید و فعال شد.\n"
        f"لینک دعوت به صورت خودکار برای سازنده ارسال گردید."
    )
    await callback.answer("ختم تأیید و فعال شد ✅")

    # Send Message to Creator via Creator Bot
    try:
        registry = get_registry()
        creator_bot = registry.get_creator_bot(Platform.TELEGRAM)
        if creator_bot:
            async with session_scope() as session:
                idents = await identity_service.list_identities_for_user(session, creator_user_id)
            tg_subjects = [i.subject for i in idents if i.platform == Platform.TELEGRAM]

            msg1 = (
                f"🎉 <b>ختم شما تأیید و فعال شد!</b>\n\n"
                f"ختم «<b>{escape(khatm_title)}</b>» توسط مدیریت تأیید شد و هم‌اکنون آماده جذب عضو و شروع است 🌱"
            )
            msg2 = (
                f"✨ <b>شما به ختم «{escape(khatm_title)}» دعوت شده‌اید.</b>\n"
                f"نیت: {escape(khatm_niyyat or 'قربة الی الله')}\n\n"
                f"🔗 <b>لینک‌های ورود اعضا:</b>\n{invite_lines_str}\n\n"
                f"🌱 <i>این پیام را برای دوستان و گروه‌های خود فوروارد کنید تا در ثواب این ختم شریک شوند.</i>"
            )
            for sid in tg_subjects:
                try:
                    await creator_bot.send_message(chat_id=int(sid), text=msg1)
                    await creator_bot.send_message(chat_id=int(sid), text=msg2)
                except Exception:
                    pass
    except Exception:
        pass


@router.callback_query(F.data.startswith("laan:reject:"))
async def reject_laan_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    raw_id = callback.data.split(":", 2)[2]
    try:
        khatm_id = UUID(raw_id)
    except ValueError:
        await callback.answer("شناسه معتبر نیست.", show_alert=True)
        return

    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(
            session, Platform.TELEGRAM, str(callback.from_user.id)
        )
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if not khatm:
            await callback.answer("ختم یافت نشد.", show_alert=True)
            return

        khatm.pending_lan_approval = False
        khatm.status = KhatmStatus.CANCELLED
        await session.flush()

        creator_user_id = khatm.creator_user_id
        khatm_title = khatm.title

        if admin_user:
            await audit_service.record(
                session, actor_user_id=admin_user.id, target_khatm_id=khatm.id,
                action="LAAN_KHATM_REJECT", details={"khatm_id": str(khatm.id)},
            )

    await callback.message.edit_text(f"❌ ختم «<b>{escape(khatm_title)}</b>» رد شد.")
    await callback.answer("ختم رد شد ❌")

    # Notify creator
    try:
        registry = get_registry()
        creator_bot = registry.get_creator_bot(Platform.TELEGRAM)
        if creator_bot:
            async with session_scope() as session:
                idents = await identity_service.list_identities_for_user(session, creator_user_id)
            tg_subjects = [i.subject for i in idents if i.platform == Platform.TELEGRAM]
            msg = (
                f"⚠️ <b>عدم تأیید ختم لعن</b>\n\n"
                f"متأسفانه ذکر یا عنوان ختم «<b>{escape(khatm_title)}</b>» مورد تأیید قوانین سامانه قرار نگرفت و فعال نشد."
            )
            for sid in tg_subjects:
                try:
                    await creator_bot.send_message(chat_id=int(sid), text=msg)
                except Exception:
                    pass
    except Exception:
        pass


# --- Broadcasts Handlers ---

@router.message(Command("broadcasts"))
@router.callback_query(F.data == "admin:broadcasts")
async def admin_broadcasts_handler(event: Message | CallbackQuery) -> None:
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    message = event if not isinstance(event, CallbackQuery) else event.message

    async with session_scope() as session:
        pending = await broadcast_service.list_pending_review(session)

    if not pending:
        text = "✅ <b>هیچ پیام همگانی در انتظار بررسی وجود ندارد.</b>"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="admin:refresh")]])
        if isinstance(event, CallbackQuery):
            await message.edit_text(text, reply_markup=kb)
            await event.answer()
        else:
            await message.answer(text, reply_markup=kb)
        return

    for b in pending:
        text = (
            "📢 <b>درخواست ارسال پیام همگانی</b>\n\n"
            f"🆔 شناسه: <code>{b.id}</code>\n"
            f"👥 مخاطبان: <b>{b.audience_count} نفر</b>\n"
            f"💰 هزینه پرداخت‌شده: <b>{b.cost_toman:,} تومان</b>\n\n"
            f"📝 متن پیام:\n<blockquote>{escape(b.message_text[:800])}</blockquote>\n\n"
            "وضعیت را مشخص کنید:"
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ تأیید و ارسال", callback_data=f"admin_broadcast:approve:{b.id}"),
                    InlineKeyboardButton(text="❌ رد و عودت وجه", callback_data=f"admin_broadcast:reject:{b.id}"),
                ]
            ]
        )
        await message.answer(text, reply_markup=markup)

    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(F.data.startswith("admin_broadcast:approve:"))
async def approve_broadcast_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    raw_id = callback.data.split(":", 2)[2]
    try:
        broadcast_id = UUID(raw_id)
    except ValueError:
        await callback.answer("شناسه نامعتبر است.", show_alert=True)
        return

    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(session, Platform.TELEGRAM, str(callback.from_user.id))
        admin_id = admin_user.id if admin_user else None
        b = await broadcast_service.review(session, broadcast_id=broadcast_id, approved=True, reviewer_user_id=admin_id)

    await callback.message.edit_text(f"✅ پیام همگانی (شناسه: <code>{b.id}</code>) تأیید شد و در صف ارسال قرار گرفت.")
    await callback.answer("پیام همگانی تأیید شد ✅")


@router.callback_query(F.data.startswith("admin_broadcast:reject:"))
async def reject_broadcast_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    raw_id = callback.data.split(":", 2)[2]
    try:
        broadcast_id = UUID(raw_id)
    except ValueError:
        await callback.answer("شناسه نامعتبر است.", show_alert=True)
        return

    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(session, Platform.TELEGRAM, str(callback.from_user.id))
        admin_id = admin_user.id if admin_user else None
        b = await broadcast_service.review(
            session, broadcast_id=broadcast_id, approved=False, reviewer_user_id=admin_id, reason="رد توسط مدیریت"
        )

    await callback.message.edit_text(f"❌ پیام همگانی (شناسه: <code>{b.id}</code>) رد شد و مبلغ پرداختی به کیف پول عودت داده شد.")
    await callback.answer("پیام رد و وجه عودت داده شد ❌")


# --- Logs and Status Handlers ---

@router.message(Command("logs"))
@router.callback_query(F.data == "admin:logs")
async def admin_logs_handler(event: Message | CallbackQuery) -> None:
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    message = event if not isinstance(event, CallbackQuery) else event.message
    logs_tail = get_recent_logs(lines=25)

    text = (
        "📑 <b>آخرین لاگ‌های عمومی سامانه:</b>\n\n"
        f"<pre>{escape(logs_tail[:3500])}</pre>"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📥 دانلود کامل فایل لاگ", callback_data="admin:download_logs"),
                InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="admin:refresh"),
            ]
        ]
    )
    if isinstance(event, CallbackQuery):
        await message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb)


@router.message(Command("errors"))
@router.callback_query(F.data == "admin:errors")
async def admin_errors_handler(event: Message | CallbackQuery) -> None:
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    message = event if not isinstance(event, CallbackQuery) else event.message
    errors_tail = get_recent_errors(lines=25)

    text = (
        "🚨 <b>آخرین خطاهای بحرانی ثبت‌شده:</b>\n\n"
        f"<pre>{escape(errors_tail[:3500])}</pre>"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="admin:errors"),
                InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="admin:refresh"),
            ]
        ]
    )
    if isinstance(event, CallbackQuery):
        await message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "admin:download_logs")
async def admin_download_logs_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    main_log, _ = get_log_file_paths()
    if not main_log.exists():
        await callback.answer("فایل لاگ یافت نشد.", show_alert=True)
        return

    await callback.answer("در حال ارسال فایل...")
    doc = FSInputFile(str(main_log), filename=f"khatmsaz_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    await callback.message.answer_document(doc, caption="📁 فایل کامل لاگ سیستم ختم‌ساز")


@router.message(Command("status"))
@router.callback_query(F.data == "admin:status")
async def admin_status_handler(event: Message | CallbackQuery) -> None:
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    message = event if not isinstance(event, CallbackQuery) else event.message

    registry = get_registry()
    creator_count = len(registry.creator_bots())
    admin_count = len(registry.admin_bots())
    member_count = len(registry.member_bots())

    db_ok = "متصل ✅"
    try:
        async with session_scope() as session:
            await session.execute(select(1))
    except Exception as exc:
        db_ok = f"خطا ❌ ({exc})"

    text = (
        "📊 <b>وضعیت لحظه‌ای سرور و خدمات ختم‌ساز</b>\n\n"
        f"🖥 <b>سیستم‌عامل:</b> {sys.platform}\n"
        f"🐍 <b>نسخه پایتون:</b> {sys.version.split()[0]}\n"
        f"🗄 <b>پایگاه‌داده Postgres:</b> {db_ok}\n"
        f"🤖 <b>ربات‌های فعال:</b>\n"
        f"• ربات‌های سازنده: <b>{creator_count}</b>\n"
        f"• ربات ادمین مرکزی: <b>{admin_count}</b> (@khatmsaz_admin_bot)\n"
        f"• ربات‌های مخاطبان (عضویت): <b>{member_count}</b>\n"
        f"⏰ <b>زمان سرور:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="admin:refresh")]])
    if isinstance(event, CallbackQuery):
        await message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb)
