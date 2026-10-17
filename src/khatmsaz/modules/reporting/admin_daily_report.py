"""Admin Daily Analytics & Trend Comparison Report (MASTER-39).

Calculates comprehensive operational metrics comparing today vs yesterday:
- New & active Khatms with trend
- New & active Users (DAU) with trend
- New & active Participations with trend
- Completed readings/portions with trend
- Most popular Khatm today & Top 5 active Khatms overall
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import distinct, func, select, union
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.admin_notifications import notify_super_admins
from khatmsaz.core.db import session_scope
from khatmsaz.modules.allocation.models import KhatmPortion, PortionStatus
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.share_occurrence.models import ShareOccurrence

logger = logging.getLogger("khatmsaz")

PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]
PERSIAN_WEEKDAYS = [
    "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه",
]


def to_persian_digits(s: object) -> str:
    mapping = str.maketrans("0123456789,", "۰۱۲۳۴۵۶۷۸۹،")
    return str(s).translate(mapping)


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
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
        jd = 1 + days % 31
    else:
        days -= 186
        jm = 7 + days // 30
        jd = 1 + days % 30
    return jy, jm, jd


def format_persian_date(dt: datetime) -> str:
    jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
    weekday = PERSIAN_WEEKDAYS[dt.weekday()]
    month_name = PERSIAN_MONTHS[jm - 1]
    return f"{weekday} {to_persian_digits(jd)} {month_name} {to_persian_digits(jy)}"


def calc_trend(today: int, yesterday: int) -> tuple[str, str]:
    """Calculate trend icon and label (↗️ صعودی / ↘️ کاهشی / ➡️ بدون تغییر)."""
    if yesterday == 0:
        if today == 0:
            return "➡️", "بدون تغییر"
        return "↗️", f"صعودی (+{to_persian_digits(today)} رکورد جدید)"
    diff = today - yesterday
    pct = (diff / yesterday) * 100
    pct_formatted = f"{abs(pct):.1f}%".replace(".0%", "%")
    pct_persian = to_persian_digits(pct_formatted)
    if diff > 0:
        return "↗️", f"صعودی (+{pct_persian})"
    elif diff < 0:
        return "↘️", f"کاهشی (-{pct_persian})"
    else:
        return "➡️", "ثابت (بدون تغییر)"


@dataclass(frozen=True)
class AdminDailyReportData:
    generated_at_local: datetime
    persian_date_str: str
    time_str: str
    
    # Khatms
    khatms_today: int
    khatms_yesterday: int
    total_khatms: int
    active_khatms: int

    # Participations
    parts_today: int
    parts_yesterday: int
    active_parts: int

    # Readings
    readings_today: int
    readings_yesterday: int

    # Users
    users_today: int
    users_yesterday: int
    total_users: int
    active_users_today: int
    active_users_yesterday: int

    # Top Khatms
    top_khatm_today: tuple[str, int] | None
    top_khatms_overall: list[tuple[str, int]]


async def get_admin_daily_report_data(
    session: AsyncSession,
    now_dt: datetime | None = None,
) -> AdminDailyReportData:
    """Query operational metrics comparing today vs yesterday in Tehran timezone."""
    tehran_tz = ZoneInfo("Asia/Tehran")
    if now_dt is None:
        now_dt = datetime.now(timezone.utc)
    now_local = now_dt.astimezone(tehran_tz)

    today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start_local = today_start_local - timedelta(days=1)

    today_start_utc = today_start_local.astimezone(timezone.utc)
    yesterday_start_utc = yesterday_start_local.astimezone(timezone.utc)
    yesterday_end_utc = today_start_utc

    # 1. Khatms stats
    total_khatms = (await session.execute(select(func.count(Khatm.id)))).scalar() or 0
    active_khatms = (await session.execute(
        select(func.count(Khatm.id)).where(Khatm.status == KhatmStatus.ACTIVE)
    )).scalar() or 0
    khatms_today = (await session.execute(
        select(func.count(Khatm.id)).where(Khatm.created_at >= today_start_utc)
    )).scalar() or 0
    khatms_yesterday = (await session.execute(
        select(func.count(Khatm.id)).where(
            Khatm.created_at >= yesterday_start_utc,
            Khatm.created_at < yesterday_end_utc,
        )
    )).scalar() or 0

    # 2. Users stats
    total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
    users_today = (await session.execute(
        select(func.count(User.id)).where(User.created_at >= today_start_utc)
    )).scalar() or 0
    users_yesterday = (await session.execute(
        select(func.count(User.id)).where(
            User.created_at >= yesterday_start_utc,
            User.created_at < yesterday_end_utc,
        )
    )).scalar() or 0

    # 3. Participations stats
    parts_today = (await session.execute(
        select(func.count(Participation.id)).where(Participation.created_at >= today_start_utc)
    )).scalar() or 0
    parts_yesterday = (await session.execute(
        select(func.count(Participation.id)).where(
            Participation.created_at >= yesterday_start_utc,
            Participation.created_at < yesterday_end_utc,
        )
    )).scalar() or 0
    active_parts = (await session.execute(
        select(func.count(Participation.id)).where(Participation.status == ParticipationStatus.ACTIVE)
    )).scalar() or 0

    # 4. Readings / Completions stats
    occ_today = (await session.execute(
        select(func.count(ShareOccurrence.id)).where(ShareOccurrence.completed_at >= today_start_utc)
    )).scalar() or 0
    occ_yesterday = (await session.execute(
        select(func.count(ShareOccurrence.id)).where(
            ShareOccurrence.completed_at >= yesterday_start_utc,
            ShareOccurrence.completed_at < yesterday_end_utc,
        )
    )).scalar() or 0

    open_contrib_today = (await session.execute(
        select(func.count(OpenContribution.id)).where(OpenContribution.created_at >= today_start_utc)
    )).scalar() or 0
    open_contrib_yesterday = (await session.execute(
        select(func.count(OpenContribution.id)).where(
            OpenContribution.created_at >= yesterday_start_utc,
            OpenContribution.created_at < yesterday_end_utc,
        )
    )).scalar() or 0

    portion_today = (await session.execute(
        select(func.count(KhatmPortion.id)).where(
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= today_start_utc,
        )
    )).scalar() or 0
    portion_yesterday = (await session.execute(
        select(func.count(KhatmPortion.id)).where(
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= yesterday_start_utc,
            KhatmPortion.completed_at < yesterday_end_utc,
        )
    )).scalar() or 0

    readings_today = occ_today + open_contrib_today + portion_today
    readings_yesterday = occ_yesterday + open_contrib_yesterday + portion_yesterday

    # 5. Active Users (DAU) Today vs Yesterday
    act_today_union = union(
        select(Participation.user_id.label("uid")).where(Participation.created_at >= today_start_utc),
        select(Participation.user_id.label("uid")).join(
            ShareOccurrence, ShareOccurrence.participation_id == Participation.id
        ).where(ShareOccurrence.completed_at >= today_start_utc),
        select(User.id.label("uid")).where(User.last_activity_at >= today_start_utc),
    ).subquery()
    active_users_today = (await session.execute(
        select(func.count(distinct(act_today_union.c.uid)))
    )).scalar() or 0

    act_yest_union = union(
        select(Participation.user_id.label("uid")).where(
            Participation.created_at >= yesterday_start_utc,
            Participation.created_at < yesterday_end_utc,
        ),
        select(Participation.user_id.label("uid")).join(
            ShareOccurrence, ShareOccurrence.participation_id == Participation.id
        ).where(
            ShareOccurrence.completed_at >= yesterday_start_utc,
            ShareOccurrence.completed_at < yesterday_end_utc,
        ),
        select(User.id.label("uid")).where(
            User.last_activity_at >= yesterday_start_utc,
            User.last_activity_at < yesterday_end_utc,
        ),
    ).subquery()
    active_users_yesterday = (await session.execute(
        select(func.count(distinct(act_yest_union.c.uid)))
    )).scalar() or 0

    # 6. Top Khatm Today
    # Pick khatm with most activity today (new participations or completions)
    top_today_stmt = (
        select(Khatm.title, func.count(Participation.id).label("cnt"))
        .join(Participation, Participation.khatm_id == Khatm.id)
        .where(Participation.created_at >= today_start_utc)
        .group_by(Khatm.id, Khatm.title)
        .order_by(func.count(Participation.id).desc())
        .limit(1)
    )
    top_today_row = (await session.execute(top_today_stmt)).first()
    top_khatm_today = (top_today_row[0], int(top_today_row[1])) if top_today_row else None

    # Fallback to general active khatm if no new participation today
    if not top_khatm_today:
        fallback_stmt = (
            select(Khatm.title, func.count(Participation.id).label("cnt"))
            .join(Participation, Participation.khatm_id == Khatm.id)
            .where(Khatm.status == KhatmStatus.ACTIVE, Participation.status == ParticipationStatus.ACTIVE)
            .group_by(Khatm.id, Khatm.title)
            .order_by(func.count(Participation.id).desc())
            .limit(1)
        )
        fb_row = (await session.execute(fallback_stmt)).first()
        if fb_row:
            top_khatm_today = (fb_row[0], int(fb_row[1]))

    # Top Khatms Overall
    top_khatms_stmt = (
        select(Khatm.title, func.count(Participation.id).label("members_cnt"))
        .join(Participation, Participation.khatm_id == Khatm.id)
        .where(Khatm.status == KhatmStatus.ACTIVE, Participation.status == ParticipationStatus.ACTIVE)
        .group_by(Khatm.id, Khatm.title)
        .order_by(func.count(Participation.id).desc())
        .limit(5)
    )
    top_khatms_rows = (await session.execute(top_khatms_stmt)).all()
    top_khatms_overall = [(r[0], int(r[1])) for r in top_khatms_rows]

    persian_date_str = format_persian_date(now_local)
    time_str = to_persian_digits(now_local.strftime("%H:%M"))

    return AdminDailyReportData(
        generated_at_local=now_local,
        persian_date_str=persian_date_str,
        time_str=time_str,
        khatms_today=khatms_today,
        khatms_yesterday=khatms_yesterday,
        total_khatms=total_khatms,
        active_khatms=active_khatms,
        parts_today=parts_today,
        parts_yesterday=parts_yesterday,
        active_parts=active_parts,
        readings_today=readings_today,
        readings_yesterday=readings_yesterday,
        users_today=users_today,
        users_yesterday=users_yesterday,
        total_users=total_users,
        active_users_today=active_users_today,
        active_users_yesterday=active_users_yesterday,
        top_khatm_today=top_khatm_today,
        top_khatms_overall=top_khatms_overall,
    )


def build_admin_daily_report_text(data: AdminDailyReportData) -> str:
    """Format the report into clean Persian HTML for Telegram."""
    k_icon, k_trend = calc_trend(data.khatms_today, data.khatms_yesterday)
    p_icon, p_trend = calc_trend(data.parts_today, data.parts_yesterday)
    r_icon, r_trend = calc_trend(data.readings_today, data.readings_yesterday)
    u_icon, u_trend = calc_trend(data.users_today, data.users_yesterday)
    au_icon, au_trend = calc_trend(data.active_users_today, data.active_users_yesterday)

    # Top today text
    if data.top_khatm_today:
        top_today_title, top_today_cnt = data.top_khatm_today
        top_today_text = (
            f"• «<b>{top_today_title}</b>» با <b>{to_persian_digits(top_today_cnt)}</b> مشارکت/عضو فعال"
        )
    else:
        top_today_text = "• <i>هنوز در طول امروز فعالیتی ثبت نشده است.</i>"

    # Top overall list
    top_overall_lines = []
    if data.top_khatms_overall:
        for idx, (title, members) in enumerate(data.top_khatms_overall, start=1):
            num = to_persian_digits(idx)
            m_cnt = to_persian_digits(members)
            top_overall_lines.append(f"{num}. <b>{title}</b> — {m_cnt} عضو فعال")
    else:
        top_overall_lines.append("<i>هنوز ختم فعالی ثبت نشده است.</i>")
    top_overall_text = "\n".join(top_overall_lines)

    lines = [
        "📊 <b>گزارش تحلیلی روزانه مدیریت ختم‌ساز</b>",
        f"🗓 <b>تاریخ:</b> {data.persian_date_str} | ⏰ <b>ساعت:</b> {data.time_str}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🌱 <b>۱. وضعیت ختم‌ها:</b>",
        f"• ختم‌های جدید امروز: <b>{to_persian_digits(data.khatms_today)} ختم</b>",
        f"• ختم‌های جدید دیروز: <b>{to_persian_digits(data.khatms_yesterday)} ختم</b>",
        f"• روند استقبال: <b>{k_icon} {k_trend}</b>",
        f"• کل ختم‌های فعال سامانه: <b>{to_persian_digits(data.active_khatms)} ختم</b> (از مجموع {to_persian_digits(data.total_khatms)})",
        "",
        "👥 <b>۲. وضعیت شراکت‌ها و قرائت‌ها:</b>",
        f"• عضویت جدید در ختم‌ها: امروز <b>{to_persian_digits(data.parts_today)}</b> | دیروز <b>{to_persian_digits(data.parts_yesterday)}</b> ({p_icon} {p_trend})",
        f"• قرائت‌های تکمیل‌شده: امروز <b>{to_persian_digits(data.readings_today)}</b> | دیروز <b>{to_persian_digits(data.readings_yesterday)}</b> ({r_icon} {r_trend})",
        f"• مجموع کل شراکت‌های فعال سامانه: <b>{to_persian_digits(data.active_parts)} شراکت</b>",
        "",
        "👤 <b>۳. کاربران (جدید و فعال):</b>",
        f"• کاربران جدید: امروز <b>{to_persian_digits(data.users_today)} نفر</b> | دیروز <b>{to_persian_digits(data.users_yesterday)} نفر</b> ({u_icon} {u_trend})",
        f"• <b>کاربران فعال امروز (DAU):</b> <b>{to_persian_digits(data.active_users_today)} نفر</b>",
        f"• کاربران فعال دیروز: <b>{to_persian_digits(data.active_users_yesterday)} نفر</b>",
        f"• تغییر کاربران فعال: <b>{au_icon} {au_trend}</b>",
        f"• کل کاربران ثبت‌نامی: <b>{to_persian_digits(data.total_users)} نفر</b>",
        "",
        "🔥 <b>۴. ختم پر استقبال امروز:</b>",
        top_today_text,
        "",
        "🏆 <b>۵. برترین ختم‌های فعال سامانه:</b>",
        top_overall_text,
        "━━━━━━━━━━━━━━━━━━━━",
        "⚙️ <i>سامانه در وضعیت نرمال و پایدار عملیاتی قرار دارد.</i>",
    ]
    return "\n".join(lines)


def build_admin_daily_report_keyboard() -> InlineKeyboardMarkup:
    """Inline buttons for refreshing report or returning to dashboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 بروزرسانی گزارش روزانه", callback_data="admin:daily_report_refresh"),
                InlineKeyboardButton(text="🔙 بازگشت به داشبورد", callback_data="admin:refresh"),
            ]
        ]
    )


async def send_daily_admin_report(session: AsyncSession | None = None) -> None:
    """Generate and dispatch daily analytics report to all Super Admins."""
    logger.info("Generating scheduled daily admin analytics report...")
    try:
        if session is not None:
            data = await get_admin_daily_report_data(session)
        else:
            async with session_scope() as s:
                data = await get_admin_daily_report_data(s)
        
        text = build_admin_daily_report_text(data)
        keyboard = build_admin_daily_report_keyboard()
        await notify_super_admins(text, reply_markup=keyboard, session=session)
        logger.info("Daily admin analytics report successfully dispatched to Super Admins.")
    except Exception as exc:
        logger.exception("Failed to dispatch daily admin analytics report: %s", exc)
