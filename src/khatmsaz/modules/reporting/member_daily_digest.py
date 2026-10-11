"""Member daily 14:00 progress digest.

Delivers an automated progress summary and motivational check-in at 14:00 (Tehran time)
to members who are active participants in active khatms via their corresponding member bots.
Shows progress up to yesterday, today's contributions so far, overall goal progress,
and the member's current portion status with direct action buttons.
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
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.reporting.creator_daily_report import (
    format_khatm_amount,
    format_persian_date,
    get_khatm_daily_counts,
    to_persian_digits,
)
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.share_occurrence.models import ShareOccurrence

logger = logging.getLogger(__name__)

NotifyFn = Callable[[str, str, str], Awaitable[None]]


async def get_member_today_status(
    session: AsyncSession,
    participation: Participation,
    today_start_utc: datetime,
) -> str:
    """Determine member's participation status for today in this khatm.

    Returns:
        "DONE": Has completed today's share.
        "PENDING": Has an assigned/undone portion or share.
        "READY": Open/general participation ready for contribution.
    """
    # 1. Check if user completed any share/portion today
    # ShareOccurrence
    has_done_occurrence = await session.scalar(
        select(func.count(ShareOccurrence.id)).where(
            ShareOccurrence.participation_id == participation.id,
            ShareOccurrence.completed_at >= today_start_utc,
        )
    )
    if has_done_occurrence and has_done_occurrence > 0:
        return "DONE"

    # KhatmPortion
    has_done_portion = await session.scalar(
        select(func.count(KhatmPortion.id)).where(
            KhatmPortion.participation_id == participation.id,
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= today_start_utc,
        )
    )
    if has_done_portion and has_done_portion > 0:
        return "DONE"

    # OpenContribution
    has_done_open = await session.scalar(
        select(func.count(OpenContribution.id)).where(
            OpenContribution.participation_id == participation.id,
            OpenContribution.recorded_at >= today_start_utc,
        )
    )
    if has_done_open and has_done_open > 0:
        return "DONE"

    # CommittedQuantityLog
    has_done_qty = await session.scalar(
        select(func.count(CommittedQuantityLog.id)).where(
            CommittedQuantityLog.participation_id == participation.id,
            CommittedQuantityLog.logged_at >= today_start_utc,
        )
    )
    if has_done_qty and has_done_qty > 0:
        return "DONE"

    # 2. Check if user has an assigned/undone share or portion
    has_pending_occurrence = await session.scalar(
        select(func.count(ShareOccurrence.id)).where(
            ShareOccurrence.participation_id == participation.id,
            ShareOccurrence.completed_at.is_(None),
        )
    )
    if has_pending_occurrence and has_pending_occurrence > 0:
        return "PENDING"

    has_pending_portion = await session.scalar(
        select(func.count(KhatmPortion.id)).where(
            KhatmPortion.participation_id == participation.id,
            KhatmPortion.status == PortionStatus.ASSIGNED,
        )
    )
    if has_pending_portion and has_pending_portion > 0:
        return "PENDING"

    return "READY"


async def build_member_daily_digest_message(
    session: AsyncSession,
    items: list[tuple[Khatm, Participation]],
    local_now: datetime,
    today_start_utc: datetime,
    now_utc: datetime,
) -> tuple[str, InlineKeyboardMarkup]:
    """Renders Persian text and interactive buttons for member daily digest."""
    date_str = format_persian_date(local_now)
    sections = [
        f"🌤 <b>با سلام و احترام، ظهرتون بخیر 🌱</b>\n"
        f"📊 <b>خلاصه پیشرفت روزانه ختم‌های شما (ساعت ۱۴:۰۰)</b>\n"
        f"📅 {date_str}"
    ]

    keyboard_rows: list[list[InlineKeyboardButton]] = []

    for khatm, participation in items:
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

        status_code = await get_member_today_status(session, participation, today_start_utc)
        if status_code == "DONE":
            status_text = "✅ سهم امروز شما ثبت شده است؛ خداقوت 💐"
            btn_text = f"🤲 مشارکت بیشتر: {khatm.title[:18]}" if len(items) > 1 else "🤲 ثبت مشارکت بیشتر"
        elif status_code == "PENDING":
            status_text = "⏳ سهم امروز شما منتظر قرائت است."
            btn_text = f"📖 انجام سهم: {khatm.title[:18]}" if len(items) > 1 else "📖 دریافت و انجام سهم امروز"
        else:
            status_text = "✨ آماده ثبت سهم یا مشارکت امروز"
            btn_text = f"📖 دریافت سهم: {khatm.title[:18]}" if len(items) > 1 else "📖 دریافت سهم امروز"

        block = (
            f"🌟 <b>ختم «{khatm.title}»</b>\n"
            f"▫️ پیشرفت کل ختم تا دیروز: {before_str}\n"
            f"▫️ قرائت‌های امروز ختم (تا ساعت ۱۴): {today_str}\n"
            f"{target_line}\n"
            f"▫️ وضعیت سهم شما: {status_text}"
        )
        sections.append(block)

        keyboard_rows.append([
            InlineKeyboardButton(text=btn_text, callback_data=f"today_pick:{participation.id}")
        ])

    sections.append("🌱 <i>از همراهی و دعای خیرتان در این ختم‌های نورانی سپاسگزاریم 🤍</i>")

    body = "\n\n".join(sections[:2])
    if len(sections) > 3:
        body += "\n\n" + "\n\n────────────────────\n\n".join(sections[2:-1])
    if len(sections) >= 3:
        body += "\n\n" + sections[-1]

    return body, InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


async def deliver_member_daily_digests(
    session: AsyncSession,
    notify: NotifyFn,
    *,
    tz_name: str = "Asia/Tehran",
    now: datetime | None = None,
    user_ids: set | None = None,
) -> int:
    """Deliver daily 14:00 Tehran progress digests to active members.

    Idempotent per local calendar day via UserSettings.last_member_daily_digest_date.
    Routes notifications through the member bot each participant joined through.
    """
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        tz = ZoneInfo("Asia/Tehran")

    now_utc = now or datetime.now(timezone.utc)
    local_now = now_utc.astimezone(tz)

    # Digest is scheduled for 14:00 local time. If earlier than 14:00, do not trigger.
    if local_now.hour < 14:
        return 0

    today_str = local_now.strftime("%Y-%m-%d")
    today_start_utc = local_now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)

    # Discover members with active participations in active khatms
    stmt = (
        select(distinct(Participation.user_id))
        .join(Khatm, Participation.khatm_id == Khatm.id)
        .where(
            Participation.status == ParticipationStatus.ACTIVE,
            Khatm.status == KhatmStatus.ACTIVE,
        )
    )
    if user_ids:
        stmt = stmt.where(Participation.user_id.in_(user_ids))

    users_res = await session.execute(stmt)
    target_user_ids = list(users_res.scalars())

    delivered_count = 0

    for uid in target_user_ids:
        settings = await settings_service.get_or_create(session, uid)
        if not getattr(settings, "member_daily_digest_enabled", True):
            continue
        if getattr(settings, "last_member_daily_digest_date", None) == today_str:
            continue

        user = await identity_service.find_by_id(session, uid)
        user_status_val = getattr(getattr(user, "status", None), "value", getattr(user, "status", None))
        if user is None or user_status_val != "ACTIVE" or user.deleted_at is not None:
            settings.last_member_daily_digest_date = today_str
            continue

        parts_stmt = (
            select(Participation, Khatm)
            .join(Khatm, Participation.khatm_id == Khatm.id)
            .where(
                Participation.user_id == uid,
                Participation.status == ParticipationStatus.ACTIVE,
                Khatm.status == KhatmStatus.ACTIVE,
            )
            .order_by(Participation.created_at.asc())
        )
        active_items = list((await session.execute(parts_stmt)).all())
        if not active_items:
            settings.last_member_daily_digest_date = today_str
            continue

        # Group by member bot (joined_via_bot_instance_id) so each member bot delivers
        # only the khatms joined through that bot without mixing platforms or bot roles.
        bot_groups: dict[object, list[tuple[Khatm, Participation]]] = {}
        for part, khatm in active_items:
            bot_groups.setdefault(part.joined_via_bot_instance_id, []).append((khatm, part))

        user_delivered = False
        identities = await identity_service.list_identities_for_user(session, uid)

        for bot_instance_id, items in bot_groups.items():
            msg_text, keyboard = await build_member_daily_digest_message(
                session, items, local_now, today_start_utc, now_utc
            )

            for identity in identities:
                try:
                    sent = await send_with_keyboard(
                        identity.platform.value,
                        identity.subject,
                        msg_text,
                        keyboard,
                        bot_instance_id=bot_instance_id,
                    )
                    if sent:
                        user_delivered = True
                except Exception:
                    try:
                        await notify(
                            identity.platform.value,
                            identity.subject,
                            msg_text,
                        )
                        user_delivered = True
                    except Exception:
                        logger.warning("Failed to notify member %s via %s", uid, identity.platform.value)

        if user_delivered:
            settings.last_member_daily_digest_date = today_str
            delivered_count += 1

    await session.flush()
    return delivered_count
