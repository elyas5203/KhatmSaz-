"""Persistence access for notification — the only place that runs SQL for this module."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.notification.models import NotificationKind, NotificationLog, NotificationPreference


async def find_log_since(
    session: AsyncSession, participation_id, kind: NotificationKind, since: datetime
) -> NotificationLog | None:
    stmt = select(NotificationLog).where(
        NotificationLog.participation_id == participation_id,
        NotificationLog.kind == kind,
        NotificationLog.sent_at >= since,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_log(session: AsyncSession, participation_id, kind: NotificationKind) -> NotificationLog:
    log = NotificationLog(id=new_id(), participation_id=participation_id, kind=kind)
    session.add(log)
    await session.flush()
    return log


async def count_logs(session: AsyncSession, participation_id, kind: NotificationKind, since=None) -> int:
    stmt = select(NotificationLog).where(
        NotificationLog.participation_id == participation_id, NotificationLog.kind == kind
    )
    if since is not None:
        stmt = stmt.where(NotificationLog.sent_at >= since)
    result = await session.execute(stmt)
    return len(list(result.scalars()))


async def get_preference(session: AsyncSession, participation_id) -> NotificationPreference | None:
    stmt = select(NotificationPreference).where(NotificationPreference.participation_id == participation_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def upsert_preference(session: AsyncSession, participation_id, *, reminder_hour: int, enabled: bool) -> NotificationPreference:
    preference = await get_preference(session, participation_id)
    if preference is None:
        preference = NotificationPreference(
            id=new_id(), participation_id=participation_id, reminder_hour=reminder_hour, enabled=enabled
        )
        session.add(preference)
    else:
        preference.reminder_hour = reminder_hour
        preference.enabled = enabled
    await session.flush()
    return preference


async def set_snoozed_until(session: AsyncSession, participation_id, until: datetime) -> NotificationPreference:
    preference = await get_preference(session, participation_id)
    if preference is None:
        preference = NotificationPreference(
            id=new_id(), participation_id=participation_id, reminder_hour=9, enabled=True,
        )
        session.add(preference)
    preference.snoozed_until = until
    await session.flush()
    return preference
