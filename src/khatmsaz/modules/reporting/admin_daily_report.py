"""Daily Administrator Report generator and automated dispatcher.

Calculates key daily operational metrics (new users, khatms, Quran pages,
salawat counts, support tickets, manual verification queues, and financial top-ups)
in Asia/Tehran timezone and formats a plain, warm Persian summary sent to all
administrators every night at 23:50 (or on-demand via /admin_daily_report).
"""

from datetime import datetime, timezone
import logging
from zoneinfo import ZoneInfo

from aiogram import Bot
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.admin_sync import get_all_admin_telegram_chat_ids
from khatmsaz.core.bot_registry import get_registry
from khatmsaz.modules.allocation.models import KhatmPortion, PortionStatus
from khatmsaz.modules.audit_log.models import AuditLog
from khatmsaz.modules.authorization.models import AdminAlertMessage
from khatmsaz.modules.identity.models import Platform, User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType
from khatmsaz.modules.manual_phone_verification.models import ManualPhoneVerification
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.wallet.models import TxType, WalletTransaction

logger = logging.getLogger("khatmsaz.admin_daily_report")

PERSIAN_WEEKDAYS = {
    0: "دوشنبه",
    1: "سه‌شنبه",
    2: "چهارشنبه",
    3: "پنج‌شنبه",
    4: "جمعه",
    5: "شنبه",
    6: "یک‌شنبه",
}

PERSIAN_MONTHS = [
    "",
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند",
]


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    """Convert Gregorian date (year, month, day) to Jalali (jy, jm, jd)."""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy if gm > 2 else gy - 1
    days = 365 * gy + (gy2 + 4) // 4 - (gy2 + 100) // 100 + (gy2 + 400) // 400 - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + (days % 31)
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


async def get_daily_admin_stats(
    session: AsyncSession,
    *,
    now: datetime | None = None,
    tz_name: str = "Asia/Tehran",
) -> dict:
    """Query database metrics for the specified day in tz_name timezone."""
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("Asia/Tehran")

    current_local = (now or datetime.now(timezone.utc)).astimezone(tz)
    start_local = current_local.replace(hour=0, minute=0, second=0, microsecond=0)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = current_local.astimezone(timezone.utc)

    # 1. Users
    new_users = await session.scalar(
        select(func.count(User.id)).where(User.created_at >= start_utc, User.created_at <= end_utc)
    ) or 0
    total_users = await session.scalar(select(func.count(User.id))) or 0

    # 2. Khatms
    new_khatms = await session.scalar(
        select(func.count(Khatm.id)).where(Khatm.created_at >= start_utc, Khatm.created_at <= end_utc)
    ) or 0
    active_khatms = await session.scalar(
        select(func.count(Khatm.id)).where(Khatm.status == KhatmStatus.ACTIVE)
    ) or 0
    total_khatms = await session.scalar(select(func.count(Khatm.id))) or 0

    # 3. Recitations & portions
    quran_portions_sum = await session.scalar(
        select(func.coalesce(func.sum(KhatmPortion.unit_end - KhatmPortion.unit_start + 1), 0))
        .select_from(KhatmPortion)
        .join(Khatm, Khatm.id == KhatmPortion.khatm_id)
        .where(
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= start_utc,
            KhatmPortion.completed_at <= end_utc,
            Khatm.template_type == KhatmTemplateType.QURAN_PAGE,
        )
    ) or 0
    quran_open_sum = await session.scalar(
        select(func.coalesce(func.sum(OpenContribution.amount), 0))
        .select_from(OpenContribution)
        .join(Khatm, Khatm.id == OpenContribution.khatm_id)
        .where(
            OpenContribution.recorded_at >= start_utc,
            OpenContribution.recorded_at <= end_utc,
            Khatm.template_type == KhatmTemplateType.QURAN_PAGE,
        )
    ) or 0
    quran_pages_today = int(quran_portions_sum + quran_open_sum)

    salawat_portions_sum = await session.scalar(
        select(func.coalesce(func.sum(KhatmPortion.completed_quantity), 0))
        .select_from(KhatmPortion)
        .join(Khatm, Khatm.id == KhatmPortion.khatm_id)
        .where(
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= start_utc,
            KhatmPortion.completed_at <= end_utc,
            Khatm.template_type != KhatmTemplateType.QURAN_PAGE,
        )
    ) or 0
    salawat_open_sum = await session.scalar(
        select(func.coalesce(func.sum(OpenContribution.amount), 0))
        .select_from(OpenContribution)
        .join(Khatm, Khatm.id == OpenContribution.khatm_id)
        .where(
            OpenContribution.recorded_at >= start_utc,
            OpenContribution.recorded_at <= end_utc,
            Khatm.template_type != KhatmTemplateType.QURAN_PAGE,
        )
    ) or 0
    salawat_today = int(salawat_portions_sum + salawat_open_sum)

    completed_portions_today = await session.scalar(
        select(func.count(KhatmPortion.id)).where(
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= start_utc,
            KhatmPortion.completed_at <= end_utc,
        )
    ) or 0

    # 4. Support and queues
    tickets_received_today = await session.scalar(
        select(func.count(AuditLog.id)).where(
            AuditLog.action == "USER_SUGGESTION",
            AuditLog.created_at >= start_utc,
            AuditLog.created_at <= end_utc,
        )
    ) or 0
    alerts_handled_today = await session.scalar(
        select(func.count(func.distinct(AdminAlertMessage.reference_id))).where(
            AdminAlertMessage.handled.is_(True),
            AdminAlertMessage.handled_at >= start_utc,
            AdminAlertMessage.handled_at <= end_utc,
        )
    ) or 0

    pending_phone_requests = await session.scalar(
        select(func.count(ManualPhoneVerification.id)).where(
            ManualPhoneVerification.status == "PENDING"
        )
    ) or 0
    approved_phone_today = await session.scalar(
        select(func.count(ManualPhoneVerification.id)).where(
            ManualPhoneVerification.status == "APPROVED",
            ManualPhoneVerification.reviewed_at >= start_utc,
            ManualPhoneVerification.reviewed_at <= end_utc,
        )
    ) or 0

    # 5. Financial / Wallet Topups
    wallet_charge_today = await session.scalar(
        select(func.coalesce(func.sum(WalletTransaction.amount), 0)).where(
            WalletTransaction.type == TxType.CHARGE,
            WalletTransaction.created_at >= start_utc,
            WalletTransaction.created_at <= end_utc,
        )
    ) or 0

    jy, jm, jd = gregorian_to_jalali(current_local.year, current_local.month, current_local.day)
    weekday_name = PERSIAN_WEEKDAYS.get(current_local.weekday(), "")
    month_name = PERSIAN_MONTHS[jm] if 1 <= jm <= 12 else ""

    return {
        "local_datetime": current_local,
        "jalali_str": f"{weekday_name}، {jd} {month_name} {jy}",
        "gregorian_str": current_local.strftime("%Y-%m-%d"),
        "time_str": current_local.strftime("%H:%M"),
        "new_users": int(new_users),
        "total_users": int(total_users),
        "new_khatms": int(new_khatms),
        "active_khatms": int(active_khatms),
        "total_khatms": int(total_khatms),
        "quran_pages_today": quran_pages_today,
        "salawat_today": salawat_today,
        "completed_portions_today": int(completed_portions_today),
        "tickets_received_today": int(tickets_received_today),
        "alerts_handled_today": int(alerts_handled_today),
        "pending_phone_requests": int(pending_phone_requests),
        "approved_phone_today": int(approved_phone_today),
        "wallet_charge_today": int(wallet_charge_today),
    }


async def generate_daily_admin_report_text(
    session: AsyncSession,
    *,
    now: datetime | None = None,
    tz_name: str = "Asia/Tehran",
) -> str:
    """Generate a clean, structured Persian daily report message for admins."""
    stats = await get_daily_admin_stats(session, now=now, tz_name=tz_name)

    lines = [
        "📊 <b>گزارش روزانهٔ ختم‌ساز</b>",
        f"📅 تاریخ: {stats['jalali_str']} ({stats['gregorian_str']})",
        f"⏰ ساعت گزارش: {stats['time_str']}",
        "",
        "👥 <b>کاربران:</b>",
        f"• کاربران جدید امروز: +{stats['new_users']:,} نفر",
        f"• کل کاربران ثبت‌شده: {stats['total_users']:,} نفر",
        "",
        "🌱 <b>ختم‌ها:</b>",
        f"• ختم‌های ایجادشده امروز: +{stats['new_khatms']:,} ختم",
        f"• ختم‌های در حال اجرا: {stats['active_khatms']:,} ختم",
        f"• کل ختم‌های ثبت‌شده: {stats['total_khatms']:,} ختم",
        "",
        "📖 <b>تلاوت و مشارکت‌های امروز:</b>",
        f"• صفحات قرآن تلاوت‌شده: {stats['quran_pages_today']:,} صفحه",
        f"• ذکر و صلوات ثبت‌شده: {stats['salawat_today']:,} مرتبه",
        f"• بخش‌های تکمیل‌شده: {stats['completed_portions_today']:,} جزء/بخش",
        "",
        "📨 <b>پشتیبانی و بررسی‌ها:</b>",
        f"• پیام‌های پشتیبانی دریافتی امروز: {stats['tickets_received_today']:,} مورد",
        f"• موارد اقدام‌شده توسط ادمین‌ها: {stats['alerts_handled_today']:,} مورد",
        f"• تأیید شماره‌های دستی: {stats['approved_phone_today']:,} تأییدشده ({stats['pending_phone_requests']:,} در انتظار)",
    ]

    if stats["wallet_charge_today"] > 0:
        lines.extend([
            "",
            "💳 <b>امور مالی و کیف پول:</b>",
            f"• شارژ کیف پول امروز: {stats['wallet_charge_today']:,} تومان",
        ])

    lines.extend([
        "",
        "🌟 خداقوت به همهٔ خادمان و مدیران ارجمند ختم‌ساز.",
    ])

    return "\n".join(lines)


async def send_daily_admin_report(
    session: AsyncSession,
    bot: Bot | None = None,
    *,
    tz_name: str = "Asia/Tehran",
) -> int:
    """Deliver daily report to all configured and delegated admins."""
    report_text = await generate_daily_admin_report_text(session, tz_name=tz_name)
    admin_ids = await get_all_admin_telegram_chat_ids(session)

    if not admin_ids:
        logger.warning("No admin Telegram chat IDs found for daily report.")
        return 0

    if bot is None:
        try:
            bot = get_registry().get_creator_bot(Platform.TELEGRAM)
        except Exception:
            bot = None

    sent_count = 0
    for chat_id in admin_ids:
        try:
            if bot is not None:
                await bot.send_message(chat_id=int(chat_id), text=report_text, parse_mode="HTML")
            else:
                from khatmsaz.bot.notify_adapter import get_notify_fn
                notify = get_notify_fn()
                await notify(Platform.TELEGRAM.value, chat_id, report_text)
            sent_count += 1
        except Exception as exc:
            logger.warning("Failed to send daily report to admin %s: %s", chat_id, exc)

    logger.info("Daily admin report sent to %d/%d admins.", sent_count, len(admin_ids))
    return sent_count
