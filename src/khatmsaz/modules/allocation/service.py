"""Allocation engine business logic.

Phase 1 scope (see ROADMAP.md): POSITIONAL (page-range) plans only, generated
once, portions handed out sequentially per participant ("Personal Journey" —
DOMAIN_MODEL.md §2) so a participant's own pages always advance in order and
never overlap with another participant's (enforced at the DB level too, by
the `uq_portion_positional_plan_unit_start` partial index).

QUANTITY (salawat/dhikr counts) does NOT go through this engine for OPEN
khatms — those are tracked as `open_contribution` rows instead (simpler, and
matches the original project's OPEN-khatm design). QUANTITY *commitment*
portions support both one-tap completion and partial progress recording (see
ROADMAP.md and DOMAIN_MODEL.md §3).
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.allocation import repository
from khatmsaz.modules.allocation.models import (
    AllocationStrategy, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind,
)

DEFAULT_PAGES_PER_PORTION = 2
EMERGENCY_CLAIM_LOCK = timedelta(hours=2)


def positional_range_for_step(
    *, offset: int, step: int, total_units: int, units_per_portion: int = DEFAULT_PAGES_PER_PORTION
) -> tuple[int, int]:
    """Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28).

    Root cause of the reported bug: committed Quran readers were handed the
    next OPEN portion from one shared pool, so with N members each reader's own
    pages jumped by N (e.g. 4,5 → 8,9 → 12,13). The owner confirmed the
    DOMAIN_MODEL §2 rotating model: each reader advances their OWN pages
    sequentially (4,5 → 6,7 → 8,9 …) from a distinct starting offset, wrapping
    around the book, so the group still covers everything with no same-day
    duplicates (as long as members ≤ total portions).

    - `offset`: this reader's distinct 0-based starting portion (staggered by
      join order).
    - `step`: how many portions this reader has already completed (0-based
      index of the portion they are about to read).
    Returns a 1-based inclusive (start_page, end_page).
    """
    total_portions = -(-total_units // units_per_portion)  # ceil
    if total_portions <= 0:
        raise ValueError("total_units and units_per_portion must be positive")
    seq = (offset + step) % total_portions  # 0-based portion index, wraps
    start = seq * units_per_portion + 1
    end = min(start + units_per_portion - 1, total_units)
    return start, end


async def generate_quran_page_plan(
    session: AsyncSession, khatm_id, total_pages: int, pages_per_portion: int = DEFAULT_PAGES_PER_PORTION
) -> KhatmAllocationPlan:
    existing = await repository.get_plan_by_khatm(session, khatm_id)
    if existing is not None:
        return existing

    boundaries = [
        (start, min(start + pages_per_portion - 1, total_pages))
        for start in range(1, total_pages + 1, pages_per_portion)
    ]
    return await repository.create_plan(
        session, khatm_id, PortionUnitKind.POSITIONAL, len(boundaries),
        allocation_strategy=AllocationStrategy.ROTATING,
        positional_boundaries=boundaries,
    )


async def generate_quran_page_plan_from_boundaries(
    session: AsyncSession, khatm_id, boundaries: list[tuple[int, int]]
) -> KhatmAllocationPlan:
    """Explicit-boundary variant of `generate_quran_page_plan` — see
    `repository.bulk_create_positional_portions_from_boundaries` for why
    this exists (audio-segment alignment for the canonical 604-page
    edition)."""
    existing = await repository.get_plan_by_khatm(session, khatm_id)
    if existing is not None:
        return existing

    return await repository.create_plan(
        session, khatm_id, PortionUnitKind.POSITIONAL, len(boundaries),
        allocation_strategy=AllocationStrategy.ROTATING,
        positional_boundaries=boundaries,
    )


async def allocate_next_portion_to(session: AsyncSession, khatm_id, participation_id) -> KhatmPortion | None:
    plan = await repository.get_plan_by_khatm_for_update(session, khatm_id)
    if plan is None:
        return None
    if plan.allocation_strategy == AllocationStrategy.ROTATING.value:
        return await repository.create_next_rotating_portion(session, plan, khatm_id, participation_id)
    portion = await repository.next_open_portion(session, plan.id)
    if portion is None:
        return None
    await repository.assign_portion(session, portion.id, participation_id)
    return portion


async def allocate_page_amount(session, khatm_id, participation_id, amount):
    """Preserve personal rotation order while honoring an exact page quantity."""
    return await repository.allocate_page_amount(session, khatm_id, participation_id, amount)


async def get_current_portion(session: AsyncSession, khatm_id, participation_id) -> KhatmPortion | None:
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        return None
    return await repository.get_current_assigned_portion(session, plan.id, participation_id)


async def complete_current_portion_and_advance(
    session: AsyncSession, khatm_id, participation_id
) -> tuple[KhatmPortion | None, KhatmPortion | None]:
    """Mark the participant's currently-assigned portion complete.

    Owner decision (2026-09-21): only one portion per calendar day — the
    next portion is **not** auto-assigned here anymore (it used to be,
    immediately). It's handed out later by
    `reminder_engine.service.deliver_due_next_portions`, once per day, at
    the participant's own configured reminder hour in their own timezone.
    The second return value always being `None` is kept (not just removed)
    so `bot/handlers/portions.py::mark_portion_done` — which used to
    branch on "is there a next portion" — doesn't need restructuring; it
    now always takes the "no next portion yet" branch unless the whole
    plan just finished."""
    current = await get_current_portion(session, khatm_id, participation_id)
    if current is None:
        return None, None
    completed = await repository.complete_portion(session, current.id)
    return completed, None


async def list_latest_portion_per_participation(session: AsyncSession) -> list[KhatmPortion]:
    """See `repository.list_latest_portion_per_participation`."""
    return await repository.list_latest_portion_per_participation(session)


async def peek_next_open_portion(session: AsyncSession, khatm_id) -> KhatmPortion | None:
    """Read-only preview of whether the shared pool still has an open
    portion for this khatm — does **not** assign it. Used right after a
    completion to phrase the confirmation message correctly ("your next
    portion arrives tomorrow" vs. "that was your last one") without
    actually handing out tomorrow's portion today (see
    `complete_current_portion_and_advance`'s one-portion-per-day note)."""
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        return None
    if plan.allocation_strategy == AllocationStrategy.ROTATING.value:
        # A rotating plan has no shared OPEN rows; an existing personal row is
        # enough to signal that the reader can continue on the next day.
        result = await repository.list_for_khatm(session, khatm_id)
        return result[-1] if result else None
    return await repository.next_open_portion(session, plan.id)


async def undo_completion(
    session: AsyncSession, completed_portion_id, participation_id, next_portion_id=None
) -> bool:
    return await repository.undo_completion(
        session, completed_portion_id, participation_id, next_portion_id
    )


async def progress(session: AsyncSession, khatm_id) -> tuple[int, int]:
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        return 0, 0
    if plan.allocation_strategy == AllocationStrategy.ROTATING.value:
        # Amount changes can split or span old plan boundaries. Count a plan
        # segment only when all its pages are covered, never just its start.
        merged = []
        for start, end in await repository.completed_positional_ranges(session, plan.id):
            if start is None or end is None:
                continue
            if merged and start <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        completed = sum(
            any(start <= a and end >= b for start, end in merged)
            for a, b in (plan.positional_boundaries or [])
        )
    else:
        completed = await repository.count_status(session, plan.id, PortionStatus.COMPLETED)
    return completed, plan.total_portions


async def list_for_khatm(session: AsyncSession, khatm_id) -> list[KhatmPortion]:
    return await repository.list_for_khatm(session, khatm_id)


async def list_assigned_positional_portions(session: AsyncSession) -> list[KhatmPortion]:
    return await repository.list_assigned_positional_portions(session)


async def uses_rotating_allocation(session: AsyncSession, khatm_id) -> bool:
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    return plan is not None and plan.allocation_strategy == AllocationStrategy.ROTATING.value


async def release_portion(session: AsyncSession, portion_id) -> None:
    """Release a legacy shared-pool portion, or retire a rotating personal one.

    A rotating row retains its participation identity and is never exposed to
    the shared claim path; the next reader/day is generated independently.
    """
    portion = await session.get(KhatmPortion, portion_id)
    plan = await session.get(KhatmAllocationPlan, portion.plan_id) if portion is not None else None
    if plan is not None and plan.allocation_strategy == AllocationStrategy.ROTATING.value:
        await repository.retire_rotating_portion(session, portion_id)
    else:
        await repository.release_portion(session, portion_id)


async def claim_next_open_portion(
    session: AsyncSession, khatm_id, participation_id, max_attempts: int = 5
) -> KhatmPortion | None:
    """Claim the lowest-sequence OPEN portion in this khatm's plan,
    race-safe against other participants claiming concurrently (retries on
    a lost race up to `max_attempts` — see `repository.try_claim_portion`).
    Returns None if the pool is empty (no OPEN portions right now)."""
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        return None
    if plan.allocation_strategy == AllocationStrategy.ROTATING.value:
        return None

    await repository.release_expired_claims(session, datetime.now(timezone.utc))

    for _ in range(max_attempts):
        candidate = await repository.next_open_portion(session, plan.id)
        if candidate is None:
            return None
        expires_at = datetime.now(timezone.utc) + EMERGENCY_CLAIM_LOCK
        if await repository.try_claim_portion(session, candidate.id, participation_id, expires_at):
            return await session.get(KhatmPortion, candidate.id)
    return None


async def count_open(session: AsyncSession, khatm_id) -> int:
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        return 0
    if plan.allocation_strategy == AllocationStrategy.ROTATING.value:
        return 0
    return await repository.count_status(session, plan.id, PortionStatus.OPEN)


async def assign_quantity_commitment(session: AsyncSession, khatm_id, participation_id, quantity: int) -> KhatmPortion:
    """A fixed per-participant quantity commitment (e.g. SALAWAT COMMITMENT
    mode: "every participant commits to N"). Unlike the Quran-page plan,
    this plan grows lazily — one portion is added the moment each
    participant joins, there is no upfront total to generate."""
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        plan = await repository.create_plan(session, khatm_id, PortionUnitKind.QUANTITY, 0)

    sequence = await repository.count_all(session, plan.id) + 1
    portion = await repository.add_quantity_commitment_portion(
        session, plan.id, khatm_id, participation_id, quantity, sequence
    )
    await repository.increment_plan_total(session, plan.id)
    return portion


async def record_quantity_commitment_progress(
    session: AsyncSession, khatm_id, participation_id, amount: int
) -> tuple[KhatmPortion | None, int, int]:
    """Record a partial or complete quantity commitment for one participant."""
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        return None, 0, amount
    portion = await repository.get_current_assigned_portion(session, plan.id, participation_id)
    if portion is None:
        return None, 0, amount
    result = await repository.record_quantity_progress(session, portion.id, amount)
    portion_result, counted, surplus = result
    if portion_result is not None and counted > 0:
        await repository.log_committed_quantity(session, khatm_id, participation_id, counted)
    return result


async def today_vs_yesterday_committed(
    session: AsyncSession, khatm_id, timezone_name: str
) -> tuple[int, int]:
    """Owner request (2026-09-22): whole-group today-vs-yesterday for QUANTITY
    commitment khatms (salawat/dua/laan). Mirrors open_contribution.today_vs_yesterday
    but queries committed_quantity_logs instead of open_contribution rows."""
    tz = ZoneInfo(timezone_name)
    now_local = datetime.now(tz)
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    today_total = await repository.committed_quantity_total_between(session, khatm_id, today_start, now_local)
    yesterday_total = await repository.committed_quantity_total_between(session, khatm_id, yesterday_start, today_start)
    return today_total, yesterday_total
