"""Creator daily 12:00 PM progress report.

Generates and delivers a daily status summary at 12:00 PM (Tehran time) to creators
with active khatms, showing progress up to yesterday, today's contributions so far,
overall progress against target, and active member count.
"""

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.notify_adapter import send_with_keyboard
from khatmsaz.modules.allocation.models import CommittedQuantityLog, KhatmPortion, PortionStatus
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import UserStatus
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.settings import service as settings_service

logger = logging.getLogger(__name__)

NotifyFn = Callable[[str, str, str], Awaitable[None]]

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
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


def format_persian_date(dt: datetime) -> str:
    jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
    weekday_str = PERSIAN_WEEKDAYS[dt.weekday()]
    month_str = PERSIAN_MONTHS[jm - 1]
    return f"{weekday_str} {to_persian_digits(jd)} {month_str} {to_persian_digits(jy)}"


async def get_khatm_daily_counts(
    session: AsyncSession, khatm: Khatm, today_start_utc: datetime, now_utc: datetime
) -> tuple[float, float, float, int]:
    """Calculate (before_today, today_so_far, total, active_members)."""
    # Active participants
    active_members = await session.scalar(
        select(func.count(Participation.id)).where(
            Participation.khatm_id == khatm.id,
            Participation.status == ParticipationStatus.ACTIVE,
        )
    ) or 0

    # Committed positional Quran portions use KhatmPortion
    if khatm.template_type == KhatmTemplateType.QURAN_PAGE and khatm.khatm_type == KhatmTypeEnum.COMMITMENT:
        before_today_quran = await session.scalar(
            select(func.coalesce(func.sum(KhatmPortion.unit_end - KhatmPortion.unit_start + 1), 0)).where(
                KhatmPortion.khatm_id == khatm.id,
                KhatmPortion.status == PortionStatus.COMPLETED,
                KhatmPortion.completed_at < today_start_utc,
            )
        ) or 0
        today_quran = await session.scalar(
            select(func.coalesce(func.sum(KhatmPortion.unit_end - KhatmPortion.unit_start + 1), 0)).where(
                KhatmPortion.khatm_id == khatm.id,
                KhatmPortion.status == PortionStatus.COMPLETED,
                KhatmPortion.completed_at >= today_start_utc,
                KhatmPortion.completed_at <= now_utc,
            )
        ) or 0
        total_quran = await session.scalar(
            select(func.coalesce(func.sum(KhatmPortion.unit_end - KhatmPortion.unit_start + 1), 0)).where(
                KhatmPortion.khatm_id == khatm.id,
                KhatmPortion.status == PortionStatus.COMPLETED,
            )
        ) or 0
        return float(before_today_quran), float(today_quran), float(total_quran), int(active_members)

    # Open contributions
    before_today_open = await session.scalar(
        select(func.coalesce(func.sum(OpenContribution.amount), 0.0)).where(
            OpenContribution.khatm_id == khatm.id,
            OpenContribution.recorded_at < today_start_utc,
        )
    ) or 0.0
    today_open = await session.scalar(
        select(func.coalesce(func.sum(OpenContribution.amount), 0.0)).where(
            OpenContribution.khatm_id == khatm.id,
            OpenContribution.recorded_at >= today_start_utc,
            OpenContribution.recorded_at <= now_utc,
        )
    ) or 0.0

    # Committed quantity logs (if any exist)
    before_today_qty = await session.scalar(
        select(func.coalesce(func.sum(CommittedQuantityLog.amount), 0)).where(
            CommittedQuantityLog.khatm_id == khatm.id,
            CommittedQuantityLog.logged_at < today_start_utc,
        )
    ) or 0
    today_qty = await session.scalar(
        select(func.coalesce(func.sum(CommittedQuantityLog.amount), 0)).where(
            CommittedQuantityLog.khatm_id == khatm.id,
            CommittedQuantityLog.logged_at >= today_start_utc,
            CommittedQuantityLog.logged_at <= now_utc,
        )
    ) or 0

    before_today = float(before_today_open) + float(before_today_qty)
    today = float(today_open) + float(today_qty)
    total = before_today + today

    return before_today, today, total, int(active_members)


async def format_khatm_amount(
    session: AsyncSession, khatm: Khatm, amount: float | int
) -> str:
    """Format numeric contribution according to khatm devotional family."""
    from khatmsaz.bot.member_copy import content_family
    from khatmsaz.modules.khatm_category import service as category_service

    fam = await content_family(session, khatm)
    amt_int = int(round(amount))

    if fam == "khutbah":
        sections_per_round = 5
        cat_slug = ""
        if khatm.content_category_id:
            cat = await category_service.get(session, khatm.content_category_id)
            if cat and cat.devotional_slug:
                cat_slug = cat.devotional_slug
        if "ghadir" in cat_slug or (khatm.title and "غدیر" in khatm.title):
            sections_per_round = 8

        rounds = amt_int // sections_per_round
        secs = amt_int % sections_per_round
        parts = []
        if rounds > 0:
            parts.append(f"{to_persian_digits(f'{rounds:,}')} دور")
        if secs > 0 or rounds == 0:
            parts.append(f"{to_persian_digits(secs)} بخش")
        return " و ".join(parts)

    if khatm.template_type == KhatmTemplateType.QURAN_PAGE:
        if amt_int >= 604:
            rounds = amt_int // 604
            pages = amt_int % 604
            parts = []
            if rounds > 0:
                parts.append(f"{to_persian_digits(f'{rounds:,}')} دور ختم کامل")
            if pages > 0:
                parts.append(f"{to_persian_digits(f'{pages:,}')} صفحه")
            return " و ".join(parts)
        return f"{to_persian_digits(f'{amt_int:,}')} صفحه"

    if fam == "salawat":
        return f"{to_persian_digits(f'{amt_int:,}')} صلوات"

    if fam == "laan":
        return f"{to_persian_digits(f'{amt_int:,}')} مرتبه لعن"

    if fam == "dua":
        return f"{to_persian_digits(f'{amt_int:,}')} مرتبه"

    return f"{to_persian_digits(f'{amt_int:,}')} مرتبه"


async def build_creator_daily_report_message(
    session: AsyncSession,
    khatms: list[Khatm],
    local_now: datetime,
    today_start_utc: datetime,
    now_utc: datetime,
) -> tuple[str, InlineKeyboardMarkup]:
    """Renders the Persian report text and interactive management keyboard."""
    date_str = format_persian_date(local_now)
    sections = [
        f"📊 <b>گزارش روزانه ختم‌های شما (ساعت ۱۲:۰۰ ظهر)</b>\n📅 {date_str}"
    ]

    keyboard_rows: list[list[InlineKeyboardButton]] = []

    for khatm in khatms:
        before_today, today, total, active_members = await get_khatm_daily_counts(
            session, khatm, today_start_utc, now_utc
        )

        before_str = await format_khatm_amount(session, khatm, before_today)
        today_str = await format_khatm_amount(session, khatm, today)
        total_str = await format_khatm_amount(session, khatm, total)

        target_line = f"▫️ مجموع قرائت‌شده: <b>{total_str}</b>"
        if khatm.repetition_target is not None and khatm.repetition_target > 0:
            effective_target = khatm.repetition_target
            from khatmsaz.bot.member_copy import content_family
            fam = await content_family(session, khatm)
            if fam == "khutbah":
                sections_per_round = 8 if (khatm.title and "غدیر" in khatm.title) else 5
                if effective_target < sections_per_round:
                    effective_target *= sections_per_round
            target_str = await format_khatm_amount(session, khatm, effective_target)
            percent = min(round((total / effective_target) * 100, 1), 100.0) if effective_target > 0 else 0.0
            target_line += f" از <b>{target_str}</b> (پیشرفت: <b>{to_persian_digits(percent)}٪</b>)"

        from khatmsaz.bot.member_copy import format_khatm_report_header, get_khatm_display_title
        header = await format_khatm_report_header(session, khatm, "fa")

        block = (
            f"{header}\n"
            f"▫️ پیشرفت تا دیروز: {before_str}\n"
            f"▫️ قرائت‌های امروز (تا ساعت ۱۲): {today_str}\n"
            f"{target_line}\n"
            f"▫️ همراهان فعال: {to_persian_digits(active_members)} نفر"
        )
        sections.append(block)

        if len(khatms) == 1:
            keyboard_rows.append([
                InlineKeyboardButton(text="⚙️ مدیریت این ختم", callback_data=f"my_khatms:manage:{khatm.id}"),
                InlineKeyboardButton(text="👥 مشاهده اعضا", callback_data=f"creator_report:members:{khatm.id}"),
            ])
        else:
            disp_title = get_khatm_display_title(khatm, "fa")
            btn_text = f"⚙️ مدیریت: {disp_title}"
            if len(btn_text) > 35:
                btn_text = btn_text[:32] + "..."
            keyboard_rows.append([
                InlineKeyboardButton(
                    text=btn_text, callback_data=f"my_khatms:manage:{khatm.id}"
                )
            ])

    sections.append("🌱 <i>طاعت و خدمت خالصانه‌تان قبول درگاه حق و التماس دعا 🤍</i>")
    keyboard_rows.append([
        InlineKeyboardButton(text="📋 فهرست همه ختم‌ها", callback_data="my_khatms:created")
    ])

    body = "\n\n".join(sections[:2])
    if len(sections) > 3:
        body += "\n\n" + "\n\n────────────────────\n\n".join(sections[2:-1])
    if len(sections) >= 3:
        body += "\n\n" + sections[-1]

    return body, InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


async def deliver_creator_daily_reports(
    session: AsyncSession,
    notify: NotifyFn,
    *,
    tz_name: str = "Asia/Tehran",
    now: datetime | None = None,
    creator_user_ids: set | None = None,
) -> int:
    """Deliver daily 12:00 PM Tehran progress reports to creators.

    Idempotent per local calendar day via UserSettings.last_creator_daily_report_date.
    """
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        tz = ZoneInfo("Asia/Tehran")

    now_utc = now or datetime.now(timezone.utc)
    local_now = now_utc.astimezone(tz)

    # Report is scheduled for 12:00 PM local time. If earlier than 12:00, do not trigger.
    if local_now.hour < 12:
        return 0

    today_str = local_now.strftime("%Y-%m-%d")
    today_start_utc = local_now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)

    # Discover creators with active khatms
    stmt = (
        select(distinct(Khatm.creator_user_id))
        .where(Khatm.status == KhatmStatus.ACTIVE)
    )
    if creator_user_ids:
        stmt = stmt.where(Khatm.creator_user_id.in_(creator_user_ids))

    creators_res = await session.execute(stmt)
    target_creator_ids = list(creators_res.scalars())

    delivered_count = 0

    for creator_id in target_creator_ids:
        settings = await settings_service.get_or_create(session, creator_id)
        if not getattr(settings, "creator_daily_report_enabled", True):
            continue
        if getattr(settings, "last_creator_daily_report_date", None) == today_str:
            continue

        user = await identity_service.find_by_id(session, creator_id)
        user_status_val = getattr(getattr(user, "status", None), "value", getattr(user, "status", None))
        if user is None or user_status_val != "ACTIVE" or user.deleted_at is not None:
            settings.last_creator_daily_report_date = today_str
            continue

        khatms_stmt = (
            select(Khatm)
            .where(
                Khatm.creator_user_id == creator_id,
                Khatm.status == KhatmStatus.ACTIVE,
            )
            .order_by(Khatm.created_at.asc())
        )
        active_khatms = list((await session.execute(khatms_stmt)).scalars())
        if not active_khatms:
            settings.last_creator_daily_report_date = today_str
            continue

        msg_text, keyboard = await build_creator_daily_report_message(
            session, active_khatms, local_now, today_start_utc, now_utc
        )

        sent_successfully = False
        identities = await identity_service.list_identities_for_user(session, creator_id)
        for identity in identities:
            try:
                sent = await send_with_keyboard(
                    identity.platform.value,
                    identity.subject,
                    msg_text,
                    keyboard,
                )
                if sent:
                    sent_successfully = True
            except Exception:
                try:
                    await notify(identity.platform.value, identity.subject, msg_text)
                    sent_successfully = True
                except Exception:
                    logger.warning("Failed to notify creator %s via %s", creator_id, identity.platform.value)

        if sent_successfully:
            settings.last_creator_daily_report_date = today_str
            delivered_count += 1

    await session.flush()
    return delivered_count
