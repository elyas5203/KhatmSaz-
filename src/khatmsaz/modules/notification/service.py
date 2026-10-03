"""Notification business logic: dedup a reminder/miss send against "already
sent today", and count how many times something has been logged (used for
the miss-threshold check in `reminder_engine`).

"Today" is deliberately simple for this MVP pass: `sent_at >= start of the
current UTC day`. This is not perfectly correct for a user far from UTC near
midnight, but reminder/deadline hours are themselves compared in the app's
configured timezone (see `reminder_engine/service.py`) — tightening this to
per-user timezone boundaries is a documented follow-up, not silently wrong
in a way that double-sends within the same real day for the timezones this
product targets (Iran).
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.notification import repository
from khatmsaz.modules.notification.models import NotificationKind


def _start_of_today_utc() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


async def already_sent_today(session: AsyncSession, participation_id, kind: NotificationKind) -> bool:
    log = await repository.find_log_since(session, participation_id, kind, _start_of_today_utc())
    return log is not None


async def record_sent(session: AsyncSession, participation_id, kind: NotificationKind) -> None:
    await repository.create_log(session, participation_id, kind)


async def total_miss_count(session: AsyncSession, participation_id, *, window_days: int | None = None) -> int:
    since = None if window_days is None else datetime.now(timezone.utc) - timedelta(days=window_days)
    return await repository.count_logs(session, participation_id, NotificationKind.FOLLOW_UP, since)


async def get_preference(session: AsyncSession, participation_id):
    return await repository.get_preference(session, participation_id)


async def get_reminder_time(session: AsyncSession, participation) -> tuple[int, int]:
    """Return the clock actually used for this membership, including old plans."""
    if (
        getattr(participation, "commitment_mode", None) == "REGULAR"
        and getattr(participation, "schedule_hour", None) is not None
    ):
        return participation.schedule_hour, participation.schedule_anchor or 0
    preference = await repository.get_preference(session, participation.id)
    if preference is not None and preference.enabled:
        return preference.reminder_hour, preference.reminder_minute or 0
    from khatmsaz.modules.system_settings import service as system_settings_service

    return await system_settings_service.get_int(session, "default_reminder_hour"), 0


async def set_reminder_preference(
    session: AsyncSession, participation_id, *, reminder_hour: int, reminder_minute: int = 0, enabled: bool = True
):
    if not 0 <= reminder_hour <= 23:
        raise ValueError("reminder_hour must be between 0 and 23")
    if not 0 <= reminder_minute <= 59:
        raise ValueError("reminder_minute must be between 0 and 59")
    preference = await repository.upsert_preference(
        session, participation_id,
        reminder_hour=reminder_hour, reminder_minute=reminder_minute, enabled=enabled
    )
    from khatmsaz.modules.participation import service as participation_service

    await participation_service.update_regular_reminder_time(
        session, participation_id, hour=reminder_hour, minute=reminder_minute,
    )
    return preference


async def snooze(session: AsyncSession, participation_id, minutes: int):
    if minutes not in (30, 60, 180):
        raise ValueError("snooze must be 30, 60, or 180 minutes")
    return await repository.set_snoozed_until(
        session, participation_id, datetime.now(timezone.utc) + timedelta(minutes=minutes)
    )


async def snooze_until(session: AsyncSession, participation_id, until: datetime):
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)
    if until <= datetime.now(timezone.utc):
        raise ValueError("snooze end must be in the future")
    return await repository.set_snoozed_until(session, participation_id, until)
