"""Reminder + deadline-miss detection for QURAN_PAGE + COMMITMENT portions."""

import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Compatibility/status constant; the live scheduler scans every minute.
SCAN_INTERVAL_MINUTES = 1


def _is_reminder_due(now_local: datetime, reminder_hour: int, reminder_minute: int = 0) -> bool:
    """Return True once the local clock has reached the reminder time today.

    Owner report (2026-09-29): pages/reminders stopped arriving on the member
    bots. Root cause — the old check only fired inside a tight 15-minute window
    [target, target+15). Because DEC-PY-0095 removed the immediate send at setup,
    that window became the ONLY delivery path; a single scan that missed it (a
    restart, a scheduler tick landing outside the window, an odd HH:MM, or a
    user timezone whose minutes don't align to :00/:15/:30/:45) dropped the whole
    day's delivery. Every caller here already dedupes to once-per-local-day
    (`already_sent_today`, `open_reading_last_sent_at`, the portion's `updated_at`),
    so "due = the clock is at or past the chosen time" is safe: the message goes
    out on the first scan at/after the chosen time and never repeats that day."""
    target_total = reminder_hour * 60 + reminder_minute
    now_total = now_local.hour * 60 + now_local.minute
    return now_total >= target_total

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.completion import service as completion_service
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.message_template import service as template_service
from khatmsaz.modules.monthly_report import service as monthly_report_service
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.notification.models import NotificationKind
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings import service as settings_service


from khatmsaz.modules.system_settings import service as system_settings_service

NotifyFn = Callable[[str, str, str], Awaitable[None]]
# (session, platform_value, chat_id, *, khatm, user_id, page_start, page_end) -> None
SendQuranPagesFn = Callable[..., Awaitable[None]]


async def process_open_reservations(session: AsyncSession, notify: NotifyFn, *, reservation_id=None, now=None) -> None:
    from sqlalchemy import select
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    from khatmsaz.modules.open_contribution.models import OpenReservation, OpenReservationStatus
    
    now = now or datetime.now(ZoneInfo("UTC"))
    stmt = select(OpenReservation).where(OpenReservation.status == OpenReservationStatus.ACTIVE)
    if reservation_id is not None:
        stmt = stmt.where(OpenReservation.id == reservation_id)
    reservations = (await session.execute(stmt)).scalars().all()
    
    for r in reservations:
        # Match completion's lock order; never hold a reservation then wait for a share.
        await khatm_service.get_khatm_for_update(session, r.khatm_id)
        from khatmsaz.modules.open_contribution import repository as reservation_repo
        r = await reservation_repo.get_reservation(session, r.id, for_update=True)
        if r.status != OpenReservationStatus.ACTIVE:
            continue
        if now >= r.expires_at:
            r.status = OpenReservationStatus.EXPIRED
        elif r.reminded_at is None:
            participation = await participation_repository.get_by_id(session, r.participation_id)
            if participation:
                khatm = await khatm_service.get_khatm(session, str(r.khatm_id))
                if khatm:
                    settings = await settings_service.get_or_create(session, participation.user_id)
                    from khatmsaz.modules.share_occurrence.delivery import timezone_for
                    local_created = r.created_at.astimezone(timezone_for(settings.timezone))
                    due = (local_created + timedelta(days=6)).replace(hour=12, minute=0, second=0, microsecond=0)
                    if now < due or not participation.joined_via_bot_instance_id:
                        continue
                    lang = settings.language
                    from khatmsaz.i18n import t
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    from khatmsaz.modules.share_occurrence import repository as shares
                    share = await shares.get_by_source(session, participation.id, f"reservation:{r.id}")
                    if share is not None and share.delivered_at is None:
                        continue
                    if share is not None:
                        from khatmsaz.bot.occurrence_adapter import send_control
                        if await send_control(session, participation, khatm, share, "RESERVATION_WARNING", now=now):
                            r.reminded_at = now
                        continue
                    action = f"share_done:{share.id}" if share else f"complete_reservation:{r.id}"
                    sent = await _notify_user_with_keyboard(
                        session, participation.user_id,
                        t("portions.open_reservation_warning", lang, count=int(r.amount)),
                        InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ انجام این سهم", callback_data=action)]]),
                        bot_instance_id=participation.joined_via_bot_instance_id,
                    )
                    if sent:
                        r.reminded_at = now


SECOND_REMINDER_HOURS_BEFORE_DEADLINE = 4
FINAL_REMINDER_HOURS_BEFORE_DEADLINE = 1


async def _default_reminder_hour(session) -> int:
    """Admin-editable system default (owner request, 2026-09-21: "همه چیز
    داینامیک باشه") — see `system_settings.service.KNOWN_SETTINGS`. Used
    whenever a participant hasn't set their own `/reminder` hour yet."""
    return await system_settings_service.get_int(session, "default_reminder_hour")


async def _inactivity_days(session) -> int:
    return await system_settings_service.get_int(session, "inactivity_days")


def _tone_key(khatm, key: str) -> str:
    tone = getattr(khatm, "reminder_tone", "FRIENDLY")
    return key if tone == "FRIENDLY" else f"{key}.{str(tone).lower()}"


async def run_once(
    session: AsyncSession, notify: NotifyFn, *, tz_name: str = "Asia/Tehran",
    monthly_report_day: int = 1, monthly_report_hour: int = 10,
    send_quran_pages: SendQuranPagesFn | None = None,
) -> None:
    """The only live share scan; legacy workers below are not scheduled."""
    from khatmsaz.core.db import session_scope
    # Commit lifecycle changes before delivery sessions take khatm locks.
    async with session_scope() as lifecycle:
        await khatm_service.close_due_khatms(lifecycle)
    await deliver_share_occurrences()
    await cleanup_completed_shares()
    await process_reservation_warnings()
    # Reporting errors cannot roll back successfully delivered member shares.
    await completion_service.deliver_pending(session, notify)
    await monthly_report_service.deliver_due(
        session, notify, report_day=monthly_report_day, report_hour=monthly_report_hour
    )


async def process_reservation_warnings():
    from khatmsaz.core.db import session_scope
    from khatmsaz.modules.open_contribution.models import OpenReservation
    async with session_scope() as session:
        ids = list((await session.execute(select(OpenReservation.id).where(OpenReservation.status == "ACTIVE"))).scalars())
    for rid in ids:
        try:
            async with session_scope() as session:
                await process_open_reservations(session, None, reservation_id=rid)
        except Exception:
            logger.exception("Reservation warning will retry for %s", rid)

async def cleanup_completed_shares():
    """Retry control cleanup independently of membership/goal completion."""
    from khatmsaz.core.db import session_scope
    from khatmsaz.modules.share_occurrence import repository as shares
    from khatmsaz.bot.occurrence_adapter import cleanup
    async with session_scope() as session:
        ids = await shares.pending_cleanup_ids(session)
    for oid in ids:
        try:
            async with session_scope() as session:
                occurrence = await shares.get(session, oid)
                part = await participation_repository.get_by_id(session, occurrence.participation_id)
                if part is not None:
                    await cleanup(session, part, occurrence)
        except Exception:
            logger.warning("Share control cleanup will retry for occurrence %s", oid)


async def deliver_share_occurrences():
    """Each member commits independently; one failed delivery cannot stop others."""
    from khatmsaz.core.db import session_scope
    from khatmsaz.modules.share_occurrence import delivery
    async with session_scope() as session:
        ids = await delivery.candidate_ids(session)
    for pid in ids:
        try:
            async with session_scope() as session:
                occurrence = await delivery.prepare(session, pid)
                # Preserve successful component receipts even if the next API
                # call fails. Database errors must still roll back this member.
                try:
                    if occurrence is not None:
                        await delivery.deliver(session, occurrence)
                    from khatmsaz.modules.share_occurrence import repository as shares
                    for pending in await shares.list_outstanding(session, pid):
                        if pending.source_key.startswith(("count:", "reservation:")) and pending.delivered_at is None:
                            await delivery.deliver(session, pending)
                    await delivery.remind(session, pid)
                except Exception:
                    if not session.is_active:
                        raise
                    logger.warning("Share delivery will retry for membership %s", pid)
        except Exception:
            logger.exception("Share scan failed for membership %s", pid)


async def _push_portion_content(session, send_quran_pages, participation, khatm, portion) -> None:
    """Auto-push the real Quran page content (image/audio/text) alongside a
    reminder, instead of requiring a manual "📖 نمایش محتوای سهم" tap. Owner
    request (2026-09-21): "سهم امروز باید اتومات باشه، دکمه نداشته باشه" —
    mirrors `deliver_due_open_quran_reading`'s push for open readers, now
    also applied to committed ones. Best-effort only — a delivery failure
    here must never block the reminder text itself, which is why callers
    still show the manual "show content" button as a fallback."""
    if send_quran_pages is None or portion.unit_start is None or portion.unit_end is None:
        return
    try:
        for identity in await identity_service.list_identities_for_user(session, participation.user_id):
            await send_quran_pages(
                session, identity.platform.value, identity.subject,
                khatm=khatm, user_id=participation.user_id,
                page_start=portion.unit_start, page_end=portion.unit_end,
                bot_instance_id=participation.joined_via_bot_instance_id,
            )
    except Exception:
        pass


async def deliver_due_next_portions(
    session: AsyncSession, notify: NotifyFn, tz_name: str = "Asia/Tehran",
    send_quran_pages: SendQuranPagesFn | None = None,
) -> int:
    """Owner decision (2026-09-21): one Quran portion per calendar day —
    a participant's next portion is not handed out the moment they finish
    the current one (see `allocation_service.complete_current_portion_and_advance`).
    Instead, once a day has passed since their last completion (in their
    own timezone) and the local clock reaches their own reminder hour
    (the same `/reminder` setting used for daily reminders), this hands
    out the next portion and lets them know. No emergency/backup-reader
    fallback exists anymore — a missed portion is simply read the next
    day the member is ready; nobody else is notified."""
    from khatmsaz.modules.notification.models import NotificationKind
    delivered = 0
    for latest_portion in await allocation_service.list_latest_portion_per_participation(session):
        participation = await participation_repository.get_by_id(session, latest_portion.participation_id)
        if participation is None:
            continue
        khatm = await khatm_service.get_khatm(session, latest_portion.khatm_id)
        if khatm is None or not khatm_service.has_started(khatm):
            continue

        preference = await notification_service.get_preference(session, participation.id)
        user_settings = await settings_service.get_or_create(session, participation.user_id)
        try:
            user_tz = ZoneInfo(user_settings.timezone)
        except (KeyError, ValueError):
            user_tz = ZoneInfo(tz_name)

        now_local = datetime.now(user_tz)
        reminder_hour = (
            preference.reminder_hour if preference is not None and preference.enabled else await _default_reminder_hour(session)
        )
        reminder_minute = getattr(preference, "reminder_minute", 0) if (preference is not None and preference.enabled) else 0
        if not _is_reminder_due(now_local, reminder_hour, reminder_minute):
            continue
        
        # updated_at records the last status change (e.g. to ASSIGNED or COMPLETED)
        # If it happened today, they already got a portion today, don't send another one.
        if latest_portion.updated_at is not None:
            updated_local_date = latest_portion.updated_at.astimezone(user_tz).date()
            if now_local.date() <= updated_local_date:
                # P7: 2-hour followup for undone portions
                from khatmsaz.modules.allocation.models import PortionStatus
                from datetime import timedelta
                
                if latest_portion.status == PortionStatus.ASSIGNED:
                    time_since = now_local - latest_portion.updated_at.astimezone(user_tz)
                    if time_since >= timedelta(hours=2):
                        if not await notification_service.already_sent_today(session, participation.id, NotificationKind.SECOND_REMINDER):
                            from khatmsaz.bot.member_copy import reminder_text, share_label
                            text = "یادآوری انجام سهم ⏳\n\n" + reminder_text(
                                khatm, "quran",
                                share_label("quran", start=latest_portion.unit_start, end=latest_portion.unit_end, lang=user_settings.language),
                                deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=getattr(user_settings, "quran_audio_enabled", True),
                            )
                            from khatmsaz.bot.keyboards import portion_done_keyboard
                            delivered_now = await _notify_user_with_keyboard(
                                session, participation.user_id, text,
                                portion_done_keyboard(str(khatm.id), allow_snooze=bool(khatm.allow_snooze), lang=user_settings.language),
                                bot_instance_id=participation.joined_via_bot_instance_id,
                            )
                            if delivered_now:
                                await notification_service.record_sent(session, participation.id, NotificationKind.SECOND_REMINDER)
                continue

        next_portion = await allocation_service.allocate_next_portion_to(session, khatm.id, participation.id)
        if next_portion is None:
            continue
        delivered += 1
        await _push_portion_content(session, send_quran_pages, participation, khatm, next_portion)
        from khatmsaz.bot.member_copy import reminder_text, share_label
        text = reminder_text(
            khatm, "quran",
            share_label("quran", start=next_portion.unit_start, end=next_portion.unit_end, lang=user_settings.language),
            deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=getattr(user_settings, "quran_audio_enabled", True)
        )
        # Committed Quran is completed as one whole assigned portion. Keep the
        # single-tap «done» action on its scheduled delivery; numeric logging is
        # reserved for open/self-reported Quran reading.
        from khatmsaz.bot.keyboards import portion_done_keyboard
        delivered_now = await _notify_user_with_keyboard(
            session, participation.user_id, text,
            portion_done_keyboard(
                str(khatm.id), allow_snooze=bool(khatm.allow_snooze), lang=user_settings.language,
            ),
            bot_instance_id=participation.joined_via_bot_instance_id,
        )
        if not delivered_now:
            await _notify_user(
                session, notify, participation.user_id, text,
                bot_instance_id=participation.joined_via_bot_instance_id,
            )
        # Record the daily reminder so the digest path (which also sends the
        # current ASSIGNED portion at the reminder hour) does not re-send this
        # freshly-allocated portion on the next 1-minute scan — that produced a
        # duplicate message on the day after a completion (E1 audit 2026-09-30).
        await notification_service.record_sent(
            session, participation.id, NotificationKind.DAILY_REMINDER
        )
    return delivered


async def deliver_due_open_quran_reading(
    session: AsyncSession, notify: NotifyFn, send_quran_pages: SendQuranPagesFn, tz_name: str = "Asia/Tehran"
) -> int:
    """Owner request (2026-09-21): an open/waitlisted (non-committed) Quran
    reader can set "N pages/day" once (see `bot/handlers/portions.py`'s
    setup flow); this delivers that day's real page content (image/audio/
    text, not just a bare number) once per local calendar day, at the
    reader's own chosen hour (stored the same way as `/reminder`, via
    `notification_service`). Stops once the reader has reached the
    edition's total page count (`khatm.repetition_target`, already used
    as the OPEN-Quran completion target) — no further auto-sends after
    that; a manual "ثبت مشارکت" can still log extra, but there is nothing
    left to send."""
    delivered = 0
    for participation in await participation_service.list_active_with_open_reading_plan(session):
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        if (
            khatm is None or khatm.template_type != KhatmTemplateType.QURAN_PAGE
            or not khatm_service.has_started(khatm)
        ):
            continue
        total_pages = content_service.get_quran_total_pages(khatm)
        if participation.open_reading_next_page > total_pages:
            continue

        preference = await notification_service.get_preference(session, participation.id)
        user_settings = await settings_service.get_or_create(session, participation.user_id)
        try:
            user_tz = ZoneInfo(user_settings.timezone)
        except (KeyError, ValueError):
            user_tz = ZoneInfo(tz_name)

        now_local = datetime.now(user_tz)
        reminder_hour = (
            preference.reminder_hour if preference is not None and preference.enabled else await _default_reminder_hour(session)
        )
        reminder_minute = getattr(preference, "reminder_minute", 0) if (preference is not None and preference.enabled) else 0
        if not _is_reminder_due(now_local, reminder_hour, reminder_minute):
            continue
        if participation.open_reading_last_sent_at is not None:
            last_sent_local_date = participation.open_reading_last_sent_at.astimezone(user_tz).date()
            if now_local.date() <= last_sent_local_date:
                continue

        pages_today = min(participation.open_reading_pages_per_day or 0, total_pages - participation.open_reading_next_page + 1)
        if pages_today <= 0:
            continue
        reserved = await participation_service.advance_open_reading(session, participation.id, pages_today)
        if reserved is None:
            continue
        start, end = reserved
        await participation_service.mark_open_reading_sent_now(session, participation.id)

        for identity in await identity_service.list_identities_for_user(session, participation.user_id):
            await send_quran_pages(
                session, identity.platform.value, identity.subject,
                khatm=khatm, user_id=participation.user_id, page_start=start, page_end=end,
                bot_instance_id=participation.joined_via_bot_instance_id,
            )
        text = await _render_or_default(
            session, "reminder.open_quran_daily", locale=user_settings.language,
            title=khatm.title, start=start, end=end,
            default=f"🌱 سهم امروزتان از «{khatm.title}» فرستاده شد: صفحات {start} تا {end}.",
        )
        # Owner (2026-09-29): the «ثبت مشارکت» log button now rides on the daily
        # page delivery — i.e. it appears exactly when there IS something to log,
        # not on the pre-delivery join/setup cards. Best-effort: fall back to a
        # plain notice if the keyboard sender is unavailable.
        from khatmsaz.bot.keyboards import contribute_keyboard
        delivered_now = await _notify_user_with_keyboard(
            session, participation.user_id, text,
            contribute_keyboard(str(khatm.id), user_settings.language),
            bot_instance_id=participation.joined_via_bot_instance_id,
        )
        if not delivered_now:
            await _notify_user(session, notify, participation.user_id, text, bot_instance_id=participation.joined_via_bot_instance_id)
        delivered += 1
    return delivered


async def deliver_due_regular_commitments(
    session: AsyncSession, notify: NotifyFn, tz_name: str = "Asia/Tehran"
) -> int:
    """R11 (owner 2026-09-28): a member on a REGULAR commitment schedule
    (Salawat/Dua/Ziyarat/La'an — not Quran) gets a nudge at their chosen local
    time each occurrence (daily / weekly on a weekday / monthly on a day),
    reminding them to read their per-occurrence amount. Deduped per calendar day
    via `schedule_last_sent_at`, mirroring `deliver_due_open_quran_reading`."""
    from khatmsaz.modules.participation.commitment import is_regular_due

    delivered = 0
    for participation in await participation_service.list_active_with_regular_schedule(session):
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        if khatm is None or not khatm_service.has_started(khatm):
            continue
        if getattr(khatm, "template_type", None) in (KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.QURAN_SURAH):
            # Older broken setup flows could persist REGULAR on Quran readers.
            # Quran delivery belongs to the page/portion workers, never devotional text.
            continue
        if participation.schedule_freq is None or participation.schedule_hour is None:
            continue

        user_settings = await settings_service.get_or_create(session, participation.user_id)
        try:
            user_tz = ZoneInfo(user_settings.timezone)
        except (KeyError, ValueError):
            user_tz = ZoneInfo(tz_name)
        now_local = datetime.now(user_tz)

        last_sent_local_date = (
            participation.schedule_last_sent_at.astimezone(user_tz).date()
            if participation.schedule_last_sent_at is not None
            else None
        )
        reminder_hour, reminder_minute = await notification_service.get_reminder_time(session, participation)
        count = participation.commitment_per_occurrence or 1
        
        is_due = is_regular_due(
            now_local,
            participation.schedule_freq,
            reminder_hour,
            reminder_minute,
            last_sent_local_date,
            weekdays=getattr(participation, "schedule_weekdays", None),
        )
        
        if not is_due:
            # P7: 2-hour followup for undone regular commitments
            if last_sent_local_date == now_local.date():
                from datetime import timedelta
                from khatmsaz.modules.notification.models import NotificationKind
                from khatmsaz.modules.open_contribution import service as open_contribution_service
                
                time_since_sent = now_local - participation.schedule_last_sent_at.astimezone(user_tz)
                if time_since_sent >= timedelta(hours=2):
                    if not await notification_service.already_sent_today(session, participation.id, NotificationKind.SECOND_REMINDER):
                        # Check if it was done since sent
                        if not await open_contribution_service.has_for_participation_since(session, participation.id, participation.schedule_last_sent_at):
                            from khatmsaz.bot.member_copy import content_family, reminder_text, share_label
                            family = await content_family(session, khatm)
                            text = "یادآوری انجام سهم ⏳\n\n" + reminder_text(
                                khatm, family, share_label(family, count=count, lang=user_settings.language),
                                deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=getattr(user_settings, "quran_audio_enabled", True),
                            )
                            from khatmsaz.bot.keyboards import regular_commitment_done_keyboard
                            delivered_now = await _notify_user_with_keyboard(
                                session, participation.user_id, text,
                                regular_commitment_done_keyboard(str(participation.id), user_settings.language),
                                bot_instance_id=participation.joined_via_bot_instance_id,
                            )
                            if delivered_now:
                                await notification_service.record_sent(session, participation.id, NotificationKind.SECOND_REMINDER)
            continue


        from khatmsaz.bot.member_copy import content_family, reminder_text, share_label
        family = await content_family(session, khatm)
        text = reminder_text(
            khatm, family, share_label(family, count=count, lang=user_settings.language),
            deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=getattr(user_settings, "quran_audio_enabled", True),
        )
        # The reading content belongs immediately ABOVE the action reminder.
        # Send registered images/PDF first; use text only when no readable media
        # exists. This is the scheduled equivalent of «انجام قرائت امروز».
        from khatmsaz.bot.notify_adapter import send_devotional_content
        content_delivered = False
        for identity in await identity_service.list_identities_for_user(session, participation.user_id):
            content_delivered = await send_devotional_content(
                session, identity.platform.value, identity.subject,
                khatm=khatm, lang=user_settings.language,
                bot_instance_id=participation.joined_via_bot_instance_id,
            ) or content_delivered
        if not content_delivered:
            logger.warning("Skipping reminder action because khatm content was unavailable: %s", khatm.id)
            continue
        from khatmsaz.bot.keyboards import regular_commitment_done_keyboard
        delivered_now = await _notify_user_with_keyboard(
            session, participation.user_id, text,
            regular_commitment_done_keyboard(str(participation.id), user_settings.language),
            bot_instance_id=participation.joined_via_bot_instance_id,
        )
        if delivered_now:
            await participation_service.mark_schedule_sent_now(session, participation.id)
            delivered += 1
    return delivered


async def delegate_inactive_portions(session: AsyncSession, notify: NotifyFn) -> int:
    """Delegate legacy shared-pool portions from inactive members.

    DEC-PY-0092 rotating portions remain personal and are deliberately skipped.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=await _inactivity_days(session))
    moved = 0
    for portion in await allocation_service.list_assigned_positional_portions(session):
        participation = await participation_repository.get_by_id(session, portion.participation_id)
        if participation is None:
            continue
        member = await identity_service.find_by_id(session, participation.user_id)
        if member is None or member.last_activity_at >= cutoff:
            continue
        khatm = await khatm_service.get_khatm(session, portion.khatm_id)
        if khatm is None or khatm.khatm_type != KhatmTypeEnum.COMMITMENT:
            continue
        # DEC-PY-0092 personal journeys have no shared/backup pool. An
        # inactive reader keeps their current personal range until returning.
        if await allocation_service.uses_rotating_allocation(session, khatm.id):
            continue
        await allocation_service.release_portion(session, portion.id)
        for backup in await participation_repository.list_active_for_khatm(session, khatm.id):
            if backup.id == participation.id or not backup.backup_reader_opt_in:
                continue
            if backup.paused_until is not None and backup.paused_until > datetime.now(timezone.utc):
                continue
            if await allocation_service.get_current_portion(session, khatm.id, backup.id) is not None:
                continue
            claimed = await allocation_service.claim_next_open_portion(session, khatm.id, backup.id)
            if claimed is None:
                continue
            moved += 1
            await _notify_user(
                session, notify, backup.user_id,
                f"📖 یک سهم از ختم «{khatm.title}» به‌دلیل عدم فعالیت عضو اصلی، برای همراهی شما واگذار شد: "
                f"صفحات {claimed.unit_start} تا {claimed.unit_end}",
                bot_instance_id=backup.joined_via_bot_instance_id,
            )
            await _notify_user(
                session, notify, participation.user_id,
                f"اطلاع‌رسانی: سهم شما در ختم «{khatm.title}» به‌دلیل ۳۰ روز عدم فعالیت، به پشتیبان واگذار شد؛ "
                "برای بازگشت کافی است دوباره با ربات تعامل کنید.",
                bot_instance_id=participation.joined_via_bot_instance_id,
            )
            break
    return moved


async def _send_open_schedule_reminders(session, notify, tz_name: str) -> None:
    """Send a scheduled prompt for open khatms at each member's reminder hour."""
    result = await session.execute(
        select(Khatm).where(
            Khatm.status == KhatmStatus.ACTIVE,
            Khatm.khatm_type == KhatmTypeEnum.OPEN,
        )
    )
    today = datetime.now(ZoneInfo(tz_name)).date()
    for khatm in result.scalars():
        if not khatm_service.schedule_is_due(khatm, today):
            continue
        for participation in await participation_repository.list_active_for_khatm(session, khatm.id):
            from khatmsaz.modules.share_occurrence.delivery import is_managed
            if is_managed(participation, khatm) or participation.commitment_mode == "COUNT":
                continue
            preference = await notification_service.get_preference(session, participation.id)
            if preference is not None and not preference.enabled:
                continue
            user_settings = await settings_service.get_or_create(session, participation.user_id)
            try:
                user_tz = ZoneInfo(user_settings.timezone)
            except (KeyError, ValueError):
                user_tz = ZoneInfo(tz_name)
            _pref_hour = preference.reminder_hour if preference else await _default_reminder_hour(session)
            _pref_minute = getattr(preference, "reminder_minute", 0) if preference else 0
            if not _is_reminder_due(datetime.now(user_tz), _pref_hour, _pref_minute):
                continue
            if await notification_service.already_sent_today(session, participation.id, NotificationKind.DAILY_REMINDER):
                continue
            text = await _render_or_default(
                session, _tone_key(khatm, "reminder.open"), locale=user_settings.language,
                title=khatm.title,
                default=f"یادآوری همراهی 🌱\nامروز می‌توانید در «{khatm.title}» مشارکت کنید.",
            )
            if khatm.template_type == KhatmTemplateType.SALAWAT:
                from khatmsaz.bot.notify_adapter import send_devotional_content
                content_delivered = False
                for identity in await identity_service.list_identities_for_user(session, participation.user_id):
                    content_delivered = await send_devotional_content(
                        session, identity.platform.value, identity.subject,
                        khatm=khatm, lang=user_settings.language,
                        bot_instance_id=participation.joined_via_bot_instance_id,
                    ) or content_delivered
                if not content_delivered:
                    logger.warning("Skipping open reminder action because khatm content was unavailable: %s", khatm.id)
                    continue
            from khatmsaz.bot.keyboards import contribute_keyboard
            delivered = await _notify_user_with_keyboard(
                session, participation.user_id, text,
                contribute_keyboard(str(khatm.id), user_settings.language),
                bot_instance_id=participation.joined_via_bot_instance_id,
            )
            if delivered:
                await notification_service.record_sent(session, participation.id, NotificationKind.DAILY_REMINDER)


async def _send_daily_digest(session, notify: NotifyFn, candidates, send_quran_pages: SendQuranPagesFn | None = None) -> None:
    """Send each committed Quran share with its own khatm-bound done button."""
    from khatmsaz.bot.keyboards import portion_done_keyboard
    for participation, khatm, portion, locale, _digest_enabled in candidates:
        await _push_portion_content(session, send_quran_pages, participation, khatm, portion)
        from khatmsaz.bot.member_copy import reminder_text, share_label
        text = reminder_text(
            khatm, "quran",
            share_label("quran", start=portion.unit_start, end=portion.unit_end, lang=locale),
            deadline=getattr(khatm, "daily_deadline_hour", None), lang=locale,
        )
        delivered = await _notify_user_with_keyboard(
            session, participation.user_id, text,
            portion_done_keyboard(str(khatm.id), allow_snooze=bool(khatm.allow_snooze), lang=locale),
            bot_instance_id=participation.joined_via_bot_instance_id,
        )
        if delivered:
            await notification_service.record_sent(
                session, participation.id, NotificationKind.DAILY_REMINDER
            )


async def _maybe_send_reminder(session, notify: NotifyFn, participation, khatm, portion, locale: str) -> None:
    if await notification_service.already_sent_today(session, participation.id, NotificationKind.DAILY_REMINDER):
        return
    text = await _render_or_default(
        session, _tone_key(khatm, "reminder.first"), locale=locale, title=khatm.title,
        start=portion.unit_start, end=portion.unit_end,
        default=f"یادآوری 🌱\nسهم امروزتان در «{khatm.title}»: صفحات {portion.unit_start} تا {portion.unit_end}",
    )
    await _notify_user(session, notify, participation.user_id, text, bot_instance_id=participation.joined_via_bot_instance_id)
    await notification_service.record_sent(session, participation.id, NotificationKind.DAILY_REMINDER)


async def _maybe_send_staged_reminder(
    session, notify, participation, khatm, portion, kind: NotificationKind, heading: str, locale: str, audio_enabled: bool = False
) -> None:
    if await notification_service.already_sent_today(session, participation.id, kind):
        return
    from khatmsaz.bot.member_copy import reminder_text, share_label
    text = heading + "\n\n" + reminder_text(
        khatm, "quran",
        share_label("quran", start=portion.unit_start, end=portion.unit_end, lang=locale),
        deadline=getattr(khatm, "daily_deadline_hour", None), lang=locale, audio_enabled=audio_enabled
    )
    from khatmsaz.bot.keyboards import portion_done_keyboard
    delivered = await _notify_user_with_keyboard(
        session, participation.user_id, text,
        portion_done_keyboard(str(khatm.id), allow_snooze=bool(khatm.allow_snooze), lang=locale),
        bot_instance_id=participation.joined_via_bot_instance_id,
    )
    if delivered:
        await notification_service.record_sent(session, participation.id, kind)


async def _maybe_record_miss_and_notify_creator(session, notify, participation, khatm) -> None:
    """Owner decision (2026-09-22): a missed portion does NOT notify the
    participant and does NOT release their portion. After 2 consecutive
    missed days (threshold=2, window=3 days), the creator is notified with
    the member's name AND phone number and asked whether to remove them.
    Nothing is done automatically — the creator decides."""
    if await notification_service.already_sent_today(session, participation.id, NotificationKind.FOLLOW_UP):
        return
    await notification_service.record_sent(session, participation.id, NotificationKind.FOLLOW_UP)

    threshold = getattr(khatm, "miss_notice_threshold", 2)
    window_days = getattr(khatm, "miss_notice_window_days", 3)
    misses = await notification_service.total_miss_count(session, participation.id, window_days=window_days)
    if misses < threshold:
        return

    member = await identity_service.find_by_id(session, participation.user_id)
    member_name = member.display_name if member and member.display_name else "یکی از اعضا"
    member_settings = await settings_service.get_or_create(session, participation.user_id)
    phone = member_settings.contact_phone or "ثبت‌نشده"
    creator_settings = await settings_service.get_or_create(session, khatm.creator_user_id)
    creator_text = await _render_or_default(
        session, _tone_key(khatm, "reminder.creator_miss"), locale=creator_settings.language,
        title=khatm.title, name=member_name, misses=misses,
        default=(
            f"⚠️ در ختم «{khatm.title}»، «{member_name}» {misses} روز پشت‌سرهم سهمش رو نخونده."
        ),
    )
    # Phone and action prompt are always appended — they're operational details,
    # not part of the customisable template text.
    creator_text += (
        f"\n\n📞 شماره تماس: {phone}\n\n"
        "چیکارش کنیم؟ می‌تونی باهاش تماس بگیری یا پیام بدی — بعد اگه خواستی از "
        "«👥 اعضا» در مدیریت ختم حذفش کنی."
    )
    await _notify_user(session, notify, khatm.creator_user_id, creator_text)


async def _notify_user(session, notify, user_id, text: str, *, bot_instance_id=None) -> None:
    for identity in await identity_service.list_identities_for_user(session, user_id):
        await notify(identity.platform.value, identity.subject, text, bot_instance_id=bot_instance_id)


async def _notify_user_with_keyboard(
    session, user_id, text: str, reply_markup, *, bot_instance_id=None,
) -> int:
    """Deliver on the participant's own bot/platform and count real successes."""
    from khatmsaz.bot.notify_adapter import send_with_keyboard

    successes = 0
    for identity in await identity_service.list_identities_for_user(session, user_id):
        if await send_with_keyboard(
            identity.platform.value, identity.subject, text, reply_markup,
            bot_instance_id=bot_instance_id,
        ):
            successes += 1
    return successes


async def _render_or_default(
    session, key: str, *, default: str, locale: str = "fa", **values: object
) -> str:
    rendered = await template_service.render(session, key, locale=locale, **values)
    return rendered if rendered is not None else default
