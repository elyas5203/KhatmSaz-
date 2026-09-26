"""Persistence access for allocation — the only place that runs SQL for this module."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation.models import (
    CommittedQuantityLog,
    KhatmAllocationPlan,
    KhatmPortion,
    PortionStatus,
    PortionUnitKind,
)


async def create_plan(
    session: AsyncSession, khatm_id, unit_kind: PortionUnitKind, total_portions: int
) -> KhatmAllocationPlan:
    plan = KhatmAllocationPlan(id=new_id(), khatm_id=khatm_id, unit_kind=unit_kind, total_portions=total_portions)
    session.add(plan)
    await session.flush()
    return plan


async def get_plan_by_khatm(session: AsyncSession, khatm_id) -> KhatmAllocationPlan | None:
    stmt = select(KhatmAllocationPlan).where(KhatmAllocationPlan.khatm_id == khatm_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def bulk_create_positional_portions(
    session: AsyncSession, plan_id, khatm_id, total_units: int, units_per_portion: int
) -> list[KhatmPortion]:
    portions: list[KhatmPortion] = []
    sequence = 1
    start = 1
    while start <= total_units:
        end = min(start + units_per_portion - 1, total_units)
        portions.append(
            KhatmPortion(
                id=new_id(),
                plan_id=plan_id,
                khatm_id=khatm_id,
                sequence=sequence,
                unit_kind=PortionUnitKind.POSITIONAL,
                unit_start=start,
                unit_end=end,
                status=PortionStatus.OPEN,
            )
        )
        sequence += 1
        start = end + 1
    session.add_all(portions)
    await session.flush()
    return portions


async def bulk_create_positional_portions_from_boundaries(
    session: AsyncSession, plan_id, khatm_id, boundaries: list[tuple[int, int]]
) -> list[KhatmPortion]:
    """Same as `bulk_create_positional_portions` but with explicit,
    non-uniform (start, end) pairs instead of a fixed page count per
    portion — used for the canonical 604-page Quran edition so portion
    boundaries line up exactly with the reciter's real audio-segment
    boundaries (see `content/quran_channel_seed.py::AUDIO_MESSAGE_RANGES`).
    Owner-reported bug (2026-09-21): the old uniform 2-pages-per-portion
    chunking starting at page 1 didn't match the audio segments (which
    combine pages 1-3 into the first recording, then pair from page 4
    onward), so most portions straddled two different audio files and
    got two separate audio messages sent for what should be one portion."""
    portions = [
        KhatmPortion(
            id=new_id(),
            plan_id=plan_id,
            khatm_id=khatm_id,
            sequence=sequence,
            unit_kind=PortionUnitKind.POSITIONAL,
            unit_start=start,
            unit_end=end,
            status=PortionStatus.OPEN,
        )
        for sequence, (start, end) in enumerate(boundaries, start=1)
    ]
    session.add_all(portions)
    await session.flush()
    return portions


async def list_latest_portion_per_participation(session: AsyncSession) -> list[KhatmPortion]:
    """Owner request (2026-09-26): "portions should advance daily regardless of completion" — 
    a committed Quran participant gets a new portion every calendar day. This returns each 
    participant's most recent portion (either ASSIGNED or COMPLETED), so the reminder engine 
    can check if they already received one today.
    """
    stmt = (
        select(KhatmPortion)
        .where(
            KhatmPortion.status.in_([PortionStatus.COMPLETED, PortionStatus.ASSIGNED]),
            KhatmPortion.participation_id.isnot(None),
        )
        .order_by(KhatmPortion.participation_id, KhatmPortion.sequence.desc())
    )
    rows = list((await session.execute(stmt)).scalars())
    seen: set = set()
    latest: list[KhatmPortion] = []
    for row in rows:
        if row.participation_id in seen:
            continue
        seen.add(row.participation_id)
        latest.append(row)
    return latest


async def next_open_portion(session: AsyncSession, plan_id) -> KhatmPortion | None:
    stmt = (
        select(KhatmPortion)
        .where(KhatmPortion.plan_id == plan_id, KhatmPortion.status == PortionStatus.OPEN)
        .order_by(KhatmPortion.sequence.asc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def assign_portion(session: AsyncSession, portion_id, participation_id) -> None:
    portion = await session.get(KhatmPortion, portion_id)
    if portion is None:
        return
    portion.status = PortionStatus.ASSIGNED
    portion.participation_id = participation_id
    await session.flush()


async def complete_portion(session: AsyncSession, portion_id) -> KhatmPortion | None:
    portion = await session.get(KhatmPortion, portion_id)
    if portion is None:
        return None
    portion.status = PortionStatus.COMPLETED
    portion.completed_at = datetime.now(timezone.utc)
    portion.claim_expires_at = None
    await session.flush()
    return portion


async def undo_completion(
    session: AsyncSession, completed_portion_id, participation_id, next_portion_id=None, *, max_age_minutes: int = 5
) -> bool:
    """Undo a recent completion and retract only the untouched auto-next slot."""
    portion = await session.get(KhatmPortion, completed_portion_id)
    if portion is None or portion.status != PortionStatus.COMPLETED or portion.participation_id != participation_id:
        return False
    if portion.completed_at is None or portion.completed_at < datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes):
        return False
    if next_portion_id is not None:
        next_portion = await session.get(KhatmPortion, next_portion_id)
        if next_portion is not None:
            if next_portion.status != PortionStatus.ASSIGNED or next_portion.participation_id != participation_id:
                return False
            next_portion.status = PortionStatus.OPEN
            next_portion.participation_id = None
            next_portion.claim_expires_at = None
    portion.status = PortionStatus.ASSIGNED
    portion.completed_at = None
    await session.flush()
    return True


async def record_quantity_progress(session: AsyncSession, portion_id, amount: int) -> tuple[KhatmPortion | None, int, int]:
    """Add progress to a quantity commitment.

    Returns (portion, counted, surplus). The personal target is never
    exceeded in ``completed_quantity``; any extra is explicitly returned as
    surplus for user-facing reporting.
    """
    portion = await session.get(KhatmPortion, portion_id)
    if portion is None or portion.unit_kind != PortionUnitKind.QUANTITY or portion.status != PortionStatus.ASSIGNED:
        return None, 0, amount
    target = portion.quantity or 0
    remaining = max(target - portion.completed_quantity, 0)
    counted = min(amount, remaining)
    portion.completed_quantity += counted
    if portion.completed_quantity >= target:
        portion.status = PortionStatus.COMPLETED
        portion.completed_at = datetime.now(timezone.utc)
    await session.flush()
    return portion, counted, amount - counted


async def get_current_assigned_portion(session: AsyncSession, plan_id, participation_id) -> KhatmPortion | None:
    stmt = (
        select(KhatmPortion)
        .where(
            KhatmPortion.plan_id == plan_id,
            KhatmPortion.participation_id == participation_id,
            KhatmPortion.status == PortionStatus.ASSIGNED,
        )
        .order_by(KhatmPortion.sequence.asc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def count_status(session: AsyncSession, plan_id, status: PortionStatus) -> int:
    stmt = select(func.count()).select_from(KhatmPortion).where(
        KhatmPortion.plan_id == plan_id, KhatmPortion.status == status
    )
    result = await session.execute(stmt)
    return int(result.scalar_one())


async def count_all(session: AsyncSession, plan_id) -> int:
    stmt = select(func.count()).select_from(KhatmPortion).where(KhatmPortion.plan_id == plan_id)
    result = await session.execute(stmt)
    return int(result.scalar_one())


async def add_quantity_commitment_portion(
    session: AsyncSession, plan_id, khatm_id, participation_id, quantity: int, sequence: int
) -> KhatmPortion:
    """A fixed per-participant quantity commitment (e.g. "you commit to
    1000 salawat"), assigned directly — unlike POSITIONAL portions there is
    no shared OPEN pool to draw from; each committed participant gets their
    own portion the moment they join."""
    portion = KhatmPortion(
        id=new_id(),
        plan_id=plan_id,
        khatm_id=khatm_id,
        sequence=sequence,
        unit_kind=PortionUnitKind.QUANTITY,
        quantity=quantity,
        status=PortionStatus.ASSIGNED,
        participation_id=participation_id,
    )
    session.add(portion)
    await session.flush()
    return portion


async def increment_plan_total(session: AsyncSession, plan_id) -> None:
    plan = await session.get(KhatmAllocationPlan, plan_id)
    if plan is None:
        return
    plan.total_portions += 1
    await session.flush()


async def release_portion(session: AsyncSession, portion_id) -> None:
    """Return an ASSIGNED portion to the OPEN pool (e.g. a missed deadline).
    History is not lost — `Assignment`/`NotificationLog` rows referencing
    the original holder are untouched; only this portion's current holder
    is cleared."""
    portion = await session.get(KhatmPortion, portion_id)
    if portion is None:
        return
    portion.status = PortionStatus.OPEN
    portion.participation_id = None
    portion.claim_expires_at = None
    await session.flush()


async def try_claim_portion(session: AsyncSession, portion_id, participation_id, claim_expires_at: datetime) -> bool:
    """Atomically claim a portion only if it's still OPEN — a plain
    SELECT-then-UPDATE would race if two participants tap "claim" for the
    same emergency-pool portion at once. Returns False if someone else won."""
    stmt = (
        update(KhatmPortion)
        .where(KhatmPortion.id == portion_id, KhatmPortion.status == PortionStatus.OPEN)
        .values(
            status=PortionStatus.ASSIGNED,
            participation_id=participation_id,
            claim_expires_at=claim_expires_at,
        )
    )
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount > 0


async def release_expired_claims(session: AsyncSession, now: datetime) -> int:
    """Return expired emergency reservations to the pool atomically."""
    stmt = (
        update(KhatmPortion)
        .where(
            KhatmPortion.status == PortionStatus.ASSIGNED,
            KhatmPortion.claim_expires_at.is_not(None),
            KhatmPortion.claim_expires_at <= now,
        )
        .values(status=PortionStatus.OPEN, participation_id=None, claim_expires_at=None)
    )
    result = await session.execute(stmt)
    await session.flush()
    return int(result.rowcount or 0)


async def list_assigned_positional_portions(session: AsyncSession) -> list[KhatmPortion]:
    """All currently-ASSIGNED POSITIONAL portions, across every khatm. Used
    by the reminder engine to scan for Quran-page commitments that are due
    or overdue — see `modules/reminder_engine/service.py`."""
    stmt = select(KhatmPortion).where(
        KhatmPortion.unit_kind == PortionUnitKind.POSITIONAL,
        KhatmPortion.status == PortionStatus.ASSIGNED,
    )
    result = await session.execute(stmt)
    return list(result.scalars())


async def list_for_khatm(session: AsyncSession, khatm_id) -> list[KhatmPortion]:
    result = await session.execute(
        select(KhatmPortion)
        .where(KhatmPortion.khatm_id == khatm_id)
        .order_by(KhatmPortion.sequence.asc())
    )
    return list(result.scalars())


async def log_committed_quantity(session: AsyncSession, khatm_id, participation_id, amount: int) -> None:
    entry = CommittedQuantityLog(
        id=new_id(), khatm_id=khatm_id, participation_id=participation_id, amount=amount
    )
    session.add(entry)
    await session.flush()


async def committed_quantity_total_between(
    session: AsyncSession, khatm_id, start: datetime, end: datetime
) -> int:
    stmt = select(func.coalesce(func.sum(CommittedQuantityLog.amount), 0)).where(
        CommittedQuantityLog.khatm_id == khatm_id,
        CommittedQuantityLog.logged_at >= start,
        CommittedQuantityLog.logged_at < end,
    )
    result = await session.execute(stmt)
    return int(result.scalar() or 0)
