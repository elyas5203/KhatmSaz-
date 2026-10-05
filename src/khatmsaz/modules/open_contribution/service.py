"""Open-contribution business logic: log a free-form amount toward an OPEN
khatm's target, splitting any overflow into "counted toward the goal" vs
"surplus" — DOMAIN_MODEL.md §2/§3's "mazad" rule. A contribution is never
rejected for being too large; the split is purely a display-time courtesy.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.open_contribution import repository
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.participation import service as participation_service


async def has_for_participation_since(session: AsyncSession, participation_id, since: datetime) -> bool:
    return await repository.has_for_participation_since(session, participation_id, since)


async def log_contribution(
    session: AsyncSession, khatm_id, participation_id, amount: float, target: float | None
) -> tuple[float, float, float]:
    """Returns (counted, surplus, new_total_for_khatm)."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    await khatm_service.get_khatm_for_update(session, khatm_id)
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


from khatmsaz.modules.open_contribution.models import OpenReservationStatus
from khatmsaz.modules.open_contribution import repository

async def create_reservation(
    session: AsyncSession, khatm_id, participation_id, amount: float, target: float | None
):
    """Create a reservation that expires in 7 days."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    khatm = await khatm_service.get_khatm_for_update(session, khatm_id)
    participation = await participation_service.get_by_id(session, participation_id)
    if (khatm is None or khatm.khatm_type != "OPEN" or khatm.status != "ACTIVE"
            or participation is None or str(participation.khatm_id) != str(khatm_id)
            or participation.status != "ACTIVE"):
        raise ValueError("Only active open memberships can reserve")
    target = khatm.repetition_target
    # check if user already has an active reservation
    existing = await repository.get_active_reservation_for_participation(session, participation_id)
    if existing:
        return existing, False # return existing and False meaning not created
        
    already_done = await repository.total_for_khatm(session, khatm_id)
    already_reserved = await repository.get_active_reserved_amount_for_khatm(session, khatm_id)
    
    if target is not None:
        available = max(target - already_done - already_reserved, 0.0)
        # If no capacity left, they cannot reserve. We can return None to indicate this.
        if available <= 0:
            return None, False
        amount = min(amount, available)
        
    expires_at = datetime.now(ZoneInfo("UTC")) + timedelta(days=7)
    reservation = await repository.create_reservation(session, khatm_id, participation_id, amount, expires_at)
    return reservation, True

async def complete_reservation(
    session: AsyncSession, reservation_id, target: float | None, *, user_id, bot_instance_id
) -> tuple[float, float, float]:
    """Mark an active reservation as completed, and log the contribution."""
    reservation = await repository.get_reservation(session, reservation_id)
    if reservation is None:
        raise ValueError("Unknown reservation")
    khatm = await khatm_service.get_khatm_for_update(session, reservation.khatm_id)
    reservation = await repository.get_reservation(session, reservation_id, for_update=True)
    participation = await participation_service.get_by_id(session, reservation.participation_id)
    if (participation is None or participation.user_id != user_id
            or bot_instance_id is None or participation.joined_via_bot_instance_id != bot_instance_id):
        raise ValueError("Reservation belongs to another member or bot")
    if not reservation or reservation.status != OpenReservationStatus.ACTIVE:
        raise ValueError("Reservation is not active or does not exist")
    if reservation.expires_at <= datetime.now(timezone.utc):
        raise ValueError("Reservation expired")
    from khatmsaz.modules.share_occurrence import repository as shares
    if await shares.get_by_source(session, participation.id, f"reservation:{reservation.id}") is not None:
        raise ValueError("Use the delivered share action for this reservation")
    
    reservation.status = OpenReservationStatus.COMPLETED
    
    # Log it as an actual contribution
    return await log_contribution(session, reservation.khatm_id, reservation.participation_id, reservation.amount, khatm.repetition_target)

async def cancel_reservation(session: AsyncSession, reservation_id):
    reservation = await repository.get_reservation(session, reservation_id)
    if reservation and reservation.status == OpenReservationStatus.ACTIVE:
        reservation.status = OpenReservationStatus.EXPIRED

async def get_active_reserved_amount_for_khatm(session: AsyncSession, khatm_id) -> float:
    return await repository.get_active_reserved_amount_for_khatm(session, khatm_id)

async def get_active_reservation_for_participation(session: AsyncSession, participation_id):
    return await repository.get_active_reservation_for_participation(session, participation_id)
