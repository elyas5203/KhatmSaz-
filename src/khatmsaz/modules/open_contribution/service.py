"""Open-contribution business logic: log a free-form amount toward an OPEN
khatm's target, splitting any overflow into "counted toward the goal" vs
"surplus" — DOMAIN_MODEL.md §2/§3's "mazad" rule. A contribution is never
rejected for being too large; the split is purely a display-time courtesy.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.open_contribution import repository


async def has_for_participation_since(session: AsyncSession, participation_id, since: datetime) -> bool:
    return await repository.has_for_participation_since(session, participation_id, since)


async def log_contribution(
    session: AsyncSession, khatm_id, participation_id, amount: float, target: float | None
) -> tuple[float, float, float]:
    """Returns (counted, surplus, new_total_for_khatm)."""
    already = await repository.total_for_khatm(session, khatm_id)

    if target is None:
        counted, surplus = amount, 0.0
    else:
        remaining = max(target - already, 0.0)
        counted = min(amount, remaining)
        surplus = amount - counted

    await repository.create(
        session, khatm_id, participation_id, amount,
        counted_amount=counted, surplus_amount=surplus,
    )
    return counted, surplus, already + amount


async def today_vs_yesterday(session: AsyncSession, khatm_id, timezone_name: str) -> tuple[float, float]:
    """Owner request (2026-09-20): show a countable khatm's whole-group
    total so far *today* next to *yesterday's* full-day total, so a member
    logging their share at, say, noon can see the number is still growing
    (many members log later the same day, up to the local end of day).
    Returns (today_so_far, yesterday_total), both Tehran-local calendar
    days (or whichever timezone the khatm/app is configured for)."""
    tz = ZoneInfo(timezone_name)
    now_local = datetime.now(tz)
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    today_total = await repository.total_for_khatm_between(session, khatm_id, today_start, now_local)
    yesterday_total = await repository.total_for_khatm_between(session, khatm_id, yesterday_start, today_start)
    return today_total, yesterday_total
