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
from aiogram.filters import Command, CommandObject, StateFilter
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
from khatmsaz.modules.broadcast.delivery import deliver_broadcast
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup
from khatmsaz.modules.reporting import service as reporting_service
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import WalletReceiptClaim, ReceiptClaimStatus
from khatmsaz.bot import invite_links
from khatmsaz.bot.keyboards import safe_answer_callback

router = Router(name="admin_bot")


async def _is_super_admin(message_or_callback: Message | CallbackQuery) -> bool:
    """Check if the sender is authorized as a Super Admin, auto-promoting configured IDs."""
    if not message_or_callback.from_user:
        return False
    chat_id = str(message_or_callback.from_user.id)
    settings = get_settings()
    env_admins = {v.strip() for v in settings.super_admin_telegram_chat_ids.split(",") if v.strip()}

    try:
        async with session_scope() as session:
            user = await identity_service.find_by_platform(session, Platform.TELEGRAM, chat_id)
            if chat_id in env_admins:
                if user is None:
                    user = await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
                elif user.role != UserRole.SUPER_ADMIN:
                    await identity_service.repository.set_role(session, user.id, UserRole.SUPER_ADMIN)
                    user.role = UserRole.SUPER_ADMIN
                return True
            if user and user.role == UserRole.SUPER_ADMIN:
                return True
    except Exception:
        # Fallback to env check even if database check failed
        if chat_id in env_admins:
            return True

    return False


async def _reject_unauthorized(message_or_callback: Message | CallbackQuery) -> None:
    chat_id = str(message_or_callback.from_user.id) if message_or_callback.from_user else "نامشخص"
    text = (
        f"⛔️ <b>دسترسی غیرمجاز</b>\n\n"
        f"این ربات مرکز مدیریت اختصاصی سیستم ختم‌ساز است و حساب شما مجوز مدیریت ندارد.\n\n"
        f"🆔 <b>شناسه تلگرام شما:</b> <code>{chat_id}</code>\n\n"
        f"جهت فعال‌سازی دسترسی، این شناسه باید توسط مدیر ارشد در پیکربندی سامانه (<code>SUPER_ADMIN_TELEGRAM_CHAT_IDS</code>) ثبت شود."
    )
    if isinstance(message_or_callback, CallbackQuery):
        await safe_answer_callback(message_or_callback, f"دسترسی غیرمجاز (شناسه: {chat_id})", show_alert=True)
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
            InlineKeyboardButton(text="👥 تفکیک کاربران و دسته‌ها", callback_data="admin:user_analytics"),
        ],
        [
            InlineKeyboardButton(text="📊 وضعیت زنده سرور", callback_data="admin:status"),
            InlineKeyboardButton(text="📑 مشاهده لاگ‌ها", callback_data="admin:logs"),
        ],
        [
            InlineKeyboardButton(text="🚨 آخرین خطاها", callback_data="admin:errors"),
            InlineKeyboardButton(text="🌐 دریافت لینک ورود به پنل (مرورگر / وب)", callback_data="admin:web_link"),
        ],
    ]

    base_url = get_settings().admin_web_base_url.rstrip("/")
    if base_url.lower().startswith("https://"):
        login_url = f"{base_url}/mini/admin"
        rows.append([
            InlineKeyboardButton(text="📱 ورود سریع با مینی‌اپ تلگرام", web_app=WebAppInfo(url=login_url))
        ])

    rows.append([
        InlineKeyboardButton(text="📊 مشاهده گزارش روزانه (تست)", callback_data="admin:test_report"),
        InlineKeyboardButton(text="🔄 بروزرسانی آمار", callback_data="admin:refresh"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _send_web_login_instructions(message: Message, user_id: int | None = None) -> None:
    chat_id = str(user_id or (message.from_user.id if message.from_user else message.chat.id))
    settings = get_settings()
    base_url = settings.admin_web_base_url.rstrip("/")
    if not base_url:
        base_url = f"http://{settings.admin_web_host}:{settings.admin_web_port}"

    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, Platform.TELEGRAM, chat_id)
        if user is None:
            user = await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
        raw_token = await session_service.issue_admin_session(session, user)

    magic_url = f"{base_url}/login?token={raw_token}"
    mini_app_url = f"{base_url}/mini/admin"

    text = (
        f"🔐 <b>ورود به پنل مدیریت ختم‌ساز</b>\n\n"
        f"مدیر گرامی، شما می‌توانید از دو روش زیر وارد پنل مدیریت سامانه شوید:\n\n"
        f"۱️⃣ <b>ورود در مرورگر (کامپیوتر یا موبایل):</b>\n"
        f"روی لینک اختصاصی زیر بزنید یا آن را در نوار آدرس مرورگر خود باز کنید:\n"
        f"🔗 <code>{magic_url}</code>\n\n"
        f"۲️⃣ <b>ورود با مینی‌اپ داخل تلگرام:</b>\n"
        f"دکمهٔ «📱 بازکردن در مینی‌اپ» را در زیر لمس فرمایید.\n\n"
        f"⏱ <i>لینک ورود مستقیم تا ۸ ساعت معتبر بوده و بدون نیاز به رمز عبور شما را مستقیماً وارد پنل می‌کند.</i>"
    )

    keyboard_rows = [
        [InlineKeyboardButton(text="🚀 ورود مستقیم به پنل در مرورگر", url=magic_url)],
    ]
    if base_url.lower().startswith("https://"):
        keyboard_rows.append([
            InlineKeyboardButton(text="📱 بازکردن در مینی‌اپ تلگرام", web_app=WebAppInfo(url=mini_app_url))
        ])
    keyboard_rows.append([
        InlineKeyboardButton(text="🔙 بازگشت به داشبورد", callback_data="admin:refresh")
    ])

    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))


@router.message(Command("web_login", "panel", "web", "login"))
async def admin_web_login_command(message: Message) -> None:
    if not await _is_super_admin(message):
        await _reject_unauthorized(message)
        return
    await _send_web_login_instructions(message)


@router.callback_query(F.data == "admin:web_link")
async def admin_web_login_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return
    await _send_web_login_instructions(callback.message, user_id=callback.from_user.id)
    await callback.answer()


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


@router.callback_query(F.data.startswith("receipt:approve:"))
async def approve_receipt_admin_bot(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    claim_id_str = callback.data.split(":", 2)[2]
    try:
        claim_id = UUID(claim_id_str)
    except ValueError:
        await callback.answer("شناسه فیش نامعتبر است.", show_alert=True)
        return

    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        admin_user = await identity_service.resolve_or_provision_user(
            session, platform, callback.from_user.id
        )
        if admin_user.role != UserRole.SUPER_ADMIN:
            admin_user.role = UserRole.SUPER_ADMIN
            await session.flush()

        claim = await wallet_service.get_receipt_claim(session, claim_id)
        if claim is None or claim.status != ReceiptClaimStatus.PENDING.value:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return

        try:
            updated_claim, invoice = await wallet_service.approve_receipt_claim(
                session,
                claim_id=claim.id,
                admin_user_id=admin_user.id,
            )
        except ValueError:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return
        target_identities = await identity_service.list_identities_for_user(session, claim.user_id)
        new_balance, new_credit = await wallet_service.get_balances(session, claim.user_id)

    admin_name = callback.from_user.full_name or "مدیر"
    new_caption = (callback.message.caption or callback.message.text or "")
    new_caption += f"\n\n✅ <b>تأیید شد:</b> مبلغ {claim.amount_toman:,} تومان توسط {escape(admin_name)} تأیید و به کیف پول کاربر اضافه گردید."
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            await callback.message.edit_text(text=new_caption, reply_markup=None)
    except Exception:
        pass

    await safe_answer_callback(callback, f"✅ فیش با موفقیت تأیید شد و {claim.amount_toman:,} تومان شارژ گردید.", show_alert=True)

    user_notify_text = (
        "🎉 <b>واریز شما تأیید شد!</b>\n\n"
        f"مبلغ <b>{claim.amount_toman:,} تومان</b> با موفقیت به موجودی کیف پول شما افزوده شد 🌱\n\n"
        f"💰 موجودی فعلی کیف پول: <b>{new_balance:,} تومان</b>"
    )
    from khatmsaz.bot.notify_adapter import get_notify_fn
    try:
        notify = get_notify_fn()
        for ident in target_identities:
            await notify(ident.platform.value, ident.subject, user_notify_text)
    except Exception:
        pass
    try:
        registry = get_registry()
        creator_bot = registry.get_creator_bot(Platform.TELEGRAM)
        if creator_bot:
            for ident in target_identities:
                if ident.platform == Platform.TELEGRAM:
                    await creator_bot.send_message(chat_id=int(ident.subject), text=user_notify_text)
    except Exception:
        pass


@router.callback_query(F.data.startswith("receipt:reject:"))
async def reject_receipt_admin_bot(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    claim_id_str = callback.data.split(":", 2)[2]
    try:
        claim_id = UUID(claim_id_str)
    except ValueError:
        await safe_answer_callback(callback, "شناسه فیش نامعتبر است.", show_alert=True)
        return

    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        admin_user = await identity_service.resolve_or_provision_user(
            session, platform, callback.from_user.id
        )
        if admin_user.role != UserRole.SUPER_ADMIN:
            admin_user.role = UserRole.SUPER_ADMIN
            await session.flush()

        claim = await wallet_service.get_receipt_claim(session, claim_id)
        if claim is None or claim.status != ReceiptClaimStatus.PENDING.value:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return

        try:
            updated_claim = await wallet_service.reject_receipt_claim(
                session,
                claim_id=claim.id,
                admin_user_id=admin_user.id,
            )
        except ValueError:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return
        target_identities = await identity_service.list_identities_for_user(session, claim.user_id)

    admin_name = callback.from_user.full_name or "مدیر"
    new_caption = (callback.message.caption or callback.message.text or "")
    new_caption += f"\n\n❌ <b>رد شد:</b> فیش توسط {escape(admin_name)} رد شد."
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            await callback.message.edit_text(text=new_caption, reply_markup=None)
    except Exception:
        pass

    await safe_answer_callback(callback, "❌ فیش واریزی رد شد.", show_alert=True)

    user_notify_text = (
        "❌ <b>عدم تأیید فیش واریزی</b>\n\n"
        f"متأسفانه فیش واریزی ارسالی شما برای مبلغ <b>{claim.amount_toman:,} تومان</b> مورد تأیید قرار نگرفت.\n"
        "در صورت کسر وجه از حسابتان، لطفاً با پشتیبانی در ارتباط باشید."
    )
    from khatmsaz.bot.notify_adapter import get_notify_fn
    try:
        notify = get_notify_fn()
        for ident in target_identities:
            await notify(ident.platform.value, ident.subject, user_notify_text)
    except Exception:
        pass
    try:
        registry = get_registry()
        creator_bot = registry.get_creator_bot(Platform.TELEGRAM)
        if creator_bot:
            for ident in target_identities:
                if ident.platform == Platform.TELEGRAM:
                    await creator_bot.send_message(chat_id=int(ident.subject), text=user_notify_text)
    except Exception:
        pass


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
        await safe_answer_callback(callback, "شناسه معتبر نیست.", show_alert=True)
        return

    from khatmsaz.modules.khatm_workflow import service as workflow_service
    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(
            session, Platform.TELEGRAM, str(callback.from_user.id)
        )
        try:
            khatm, token, refunded = await workflow_service.review_laan_khatm_workflow(
                session,
                khatm_id=khatm_id,
                approved=False,
            )
        except ValueError:
            await safe_answer_callback(callback, "این ختم قبلاً بررسی یا لغو شده است.", show_alert=True)
            return

        creator_user_id = khatm.creator_user_id
        khatm_title = khatm.title

        if admin_user:
            await audit_service.record(
                session, actor_user_id=admin_user.id, target_khatm_id=khatm.id,
                action="LAAN_KHATM_REJECT", details={"khatm_id": str(khatm.id), "refunded": refunded},
            )

    refund_note = f"\nمبلغ {refunded:,} تومان به کیف پول سازنده بازگردانده شد." if refunded else ""
    await callback.message.edit_text(f"❌ ختم «<b>{escape(khatm_title)}</b>» رد شد.{refund_note}")
    await safe_answer_callback(callback, "ختم رد شد ❌")

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


async def _safe_edit_admin_message(message: Message, text: str) -> None:
    """Edit message text or caption safely regardless of whether it's a photo or text message."""
    try:
        if getattr(message, "photo", None):
            await message.edit_caption(caption=text, reply_markup=None)
        else:
            await message.edit_text(text=text, reply_markup=None)
    except Exception:
        try:
            await message.edit_caption(caption=text, reply_markup=None)
        except Exception:
            try:
                await message.edit_text(text=text, reply_markup=None)
            except Exception:
                await message.answer(text)


@router.callback_query(F.data.startswith("admin_broadcast:approve:"))
async def approve_broadcast_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    raw_id = callback.data.split(":", 2)[2]
    try:
        broadcast_id = UUID(raw_id)
    except ValueError:
        await safe_answer_callback(callback, "شناسه نامعتبر است.", show_alert=True)
        return

    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(session, Platform.TELEGRAM, str(callback.from_user.id))
        admin_id = admin_user.id if admin_user else None
        try:
            b = await broadcast_service.approve(session, broadcast_id=broadcast_id, note=f"Approved by admin {admin_id}")
        except ValueError:
            await safe_answer_callback(callback, "این پیام قبلاً بررسی شده یا در انتظار نیست.", show_alert=True)
            return

        dest_count = await deliver_broadcast(session, b)

    status_text = f"✅ پیام همگانی (شناسه: <code>{b.id}</code>) تأیید شد و برای {dest_count} مخاطب ارسال گردید."
    if callback.message:
        await _safe_edit_admin_message(callback.message, status_text)
    await safe_answer_callback(callback, "پیام همگانی تأیید و ارسال شد ✅")


@router.callback_query(F.data.startswith("admin_broadcast:reject:"))
async def reject_broadcast_callback(callback: CallbackQuery) -> None:
    if not await _is_super_admin(callback):
        await _reject_unauthorized(callback)
        return

    raw_id = callback.data.split(":", 2)[2]
    try:
        broadcast_id = UUID(raw_id)
    except ValueError:
        await safe_answer_callback(callback, "شناسه نامعتبر است.", show_alert=True)
        return

    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(session, Platform.TELEGRAM, str(callback.from_user.id))
        admin_id = admin_user.id if admin_user else None
        try:
            b = await broadcast_service.reject(
                session, broadcast_id=broadcast_id, note="رد توسط مدیریت"
            )
        except ValueError:
            await safe_answer_callback(callback, "این پیام قبلاً بررسی شده یا در انتظار نیست.", show_alert=True)
            return

    cost = getattr(b, "cost_toman", 0) or 0
    cost_text = f" و مبلغ {cost:,} تومان به کیف پول عودت داده شد" if cost > 0 else ""
    status_text = f"❌ پیام همگانی (شناسه: <code>{b.id}</code>) رد شد{cost_text}."
    if callback.message:
        await _safe_edit_admin_message(callback.message, status_text)
    await safe_answer_callback(callback, "پیام رد و وجه عودت داده شد ❌")


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
    user_summary = ""
    try:
        async with session_scope() as session:
            await session.execute(select(1))
            analytics = await reporting_service.get_system_user_analytics(session)
            p = analytics["platform"]
            top = analytics["top_category"]
            top_str = f" | 🏆 بیشترین استقبال: {top['title']}" if top else ""
            user_summary = f"\n👥 <b>مجموع کل کاربران:</b> {p['total_users']} (📱 {p['telegram_users']} تلگرام · 🟢 {p['bale_users']} بله){top_str}\n"
    except Exception as exc:
        db_ok = f"خطا ❌ ({exc})"

    text = (
        "📊 <b>وضعیت لحظه‌ای سرور و خدمات ختم‌ساز</b>\n\n"
        f"🖥 <b>سیستم‌عامل:</b> {sys.platform}\n"
        f"🐍 <b>نسخه پایتون:</b> {sys.version.split()[0]}\n"
        f"🗄 <b>پایگاه‌داده Postgres:</b> {db_ok}\n"
        f"{user_summary}"
        f"🤖 <b>ربات‌های فعال:</b>\n"
        f"• ربات‌های سازنده: <b>{creator_count}</b>\n"
        f"• ربات ادمین مرکزی: <b>{admin_count}</b> (@khatmsaz_admin_bot)\n"
        f"• ربات‌های مخاطبان (عضویت): <b>{member_count}</b>\n"
        f"⏰ <b>زمان سرور:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 مشاهده تفکیک کامل کاربران", callback_data="admin:user_analytics")],
        [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="admin:refresh")],
    ])
    if isinstance(event, CallbackQuery):
        await message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb)


@router.message(Command("users_stat", "analytics", "users"))
@router.callback_query(F.data == "admin:user_analytics")
async def admin_user_analytics_handler(event: Message | CallbackQuery) -> None:
    """MASTER-20: Breakdown of total users across all bots, platforms, and 5 devotional categories."""
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    message = event if not isinstance(event, CallbackQuery) else event.message
    async with session_scope() as session:
        analytics = await reporting_service.get_system_user_analytics(session)

    plat = analytics["platform"]
    cats = analytics["categories"]
    top_cat = analytics["top_category"]

    cat_lines = []
    for c in cats:
        star = " 🏆 (بیشترین استقبال)" if c["is_top"] else f" (رتبه {c['rank']})"
        cat_lines.append(
            f"• {c['icon']} <b>{c['title']}:</b> <code>{c['engaged_users']}</code> کاربر "
            f"({c['popularity_percent']}٪) · <i>{c['total_khatms']} ختم</i>{star}"
        )
    cat_text = "\n".join(cat_lines)

    top_text = f"\n🏆 <b>بیشترین استقبال:</b> {top_cat['title']} ({top_cat['popularity_percent']}٪ سهم بازار)\n" if top_cat else ""

    text = (
        "📊 <b>تحلیل جامع کاربران و تفکیک دسته‌ها</b>\n\n"
        f"👥 <b>مجموع کل کاربران سامانه:</b> <code>{plat['total_users']}</code> نفر\n"
        f"📱 <b>کاربران تلگرام:</b> <code>{plat['telegram_users']}</code> نفر\n"
        f"🟢 <b>کاربران بله:</b> <code>{plat['bale_users']}</code> نفر\n"
        f"🔄 <b>کاربران متصل به هر دو پلتفرم:</b> <code>{plat['dual_platform_users']}</code> نفر\n"
        f"👑 <b>سازندگان:</b> <code>{plat['creators_count']}</code> | 🛡 <b>مدیران:</b> <code>{plat['super_admins_count']}</code>\n"
        f"{top_text}\n"
        "📈 <b>میزان استقبال از ۵ دستهٔ عبادی:</b>\n"
        f"{cat_text}\n\n"
        "💡 <i>جهت مشاهده گزارش و نمودارهای کامل، به پنل مدیریت وب مراجعه فرمایید.</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی آمار", callback_data="admin:user_analytics")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="admin:refresh")],
    ])
    if isinstance(event, CallbackQuery):
        await message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await message.answer(text, reply_markup=kb)


@router.message(Command("test_report", "report", "test"))
@router.callback_query(F.data == "admin:test_report")
async def admin_test_report_handler(event: Message | CallbackQuery) -> None:
    """Send an immediate test daily report with Niabat titles."""
    if not await _is_super_admin(event):
        await _reject_unauthorized(event)
        return

    from zoneinfo import ZoneInfo
    from khatmsaz.modules.reporting.creator_daily_report import build_creator_daily_report_message

    message = event if not isinstance(event, CallbackQuery) else event.message
    chat_id = str(event.from_user.id) if event.from_user else str(message.chat.id)
    now_utc = datetime.now(timezone.utc)
    tz = ZoneInfo("Asia/Tehran")
    local_now = now_utc.astimezone(tz)
    today_start_utc = local_now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)

    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, Platform.TELEGRAM, chat_id)
        khatms = []
        if user:
            res = await session.execute(
                select(Khatm).where(Khatm.creator_user_id == user.id, Khatm.status == KhatmStatus.ACTIVE).order_by(Khatm.created_at.desc())
            )
            khatms = list(res.scalars().all())

        if not khatms:
            res = await session.execute(
                select(Khatm).where(Khatm.status == KhatmStatus.ACTIVE).order_by(Khatm.created_at.desc()).limit(5)
            )
            khatms = list(res.scalars().all())

        if not khatms:
            await message.answer("⚠️ هیچ ختم فعالی در سامانه برای گزارش یافت نشد.")
            if isinstance(event, CallbackQuery):
                await event.answer()
            return

        body, markup = await build_creator_daily_report_message(
            session, khatms, local_now, today_start_utc, now_utc
        )
        await message.answer(body, reply_markup=markup)
        if isinstance(event, CallbackQuery):
            await event.answer("گزارش آزمایشی ارسال شد ✅")


@router.message(StateFilter(None), ~F.text.startswith("/"))
async def admin_fallback_message_handler(message: Message) -> None:
    """Fallback handler so any non-command message with no active state sent to the admin bot brings up the dashboard or explains authorization."""
    if not await _is_super_admin(message):
        await _reject_unauthorized(message)
        return
    await admin_start_handler(message)

