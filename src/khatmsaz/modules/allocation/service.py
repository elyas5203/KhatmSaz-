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
from khatmsaz.modules.allocation.models import KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind

DEFAULT_PAGES_PER_PORTION = 2
EMERGENCY_CLAIM_LOCK = timedelta(hours=2)


async def generate_quran_page_plan(
    session: AsyncSession, khatm_id, total_pages: int, pages_per_portion: int = DEFAULT_PAGES_PER_PORTION
) -> KhatmAllocationPlan:
    existing = await repository.get_plan_by_khatm(session, khatm_id)
    if existing is not None:
        return existing

    total_portions = -(-total_pages // pages_per_portion)  # ceil division
    plan = await repository.create_plan(session, khatm_id, PortionUnitKind.POSITIONAL, total_portions)
    await repository.bulk_create_positional_portions(session, plan.id, khatm_id, total_pages, pages_per_portion)
    return plan


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

    plan = await repository.create_plan(session, khatm_id, PortionUnitKind.POSITIONAL, len(boundaries))
    await repository.bulk_create_positional_portions_from_boundaries(session, plan.id, khatm_id, boundaries)
    return plan


async def allocate_next_portion_to(session: AsyncSession, khatm_id, participation_id) -> KhatmPortion | None:
    plan = await repository.get_plan_by_khatm(session, khatm_id)
    if plan is None:
        return None
    portion = await repository.next_open_portion(session, plan.id)
    if portion is None:
        return None
    await repository.assign_portion(session, portion.id, participation_id)
    return portion


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


async def list_awaiting_next_portion(session: AsyncSession) -> list[KhatmPortion]:
    """See `repository.list_latest_completed_without_current_assignment`."""
    return await repository.list_latest_completed_without_current_assignment(session)


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
    completed = await repository.count_status(session, plan.id, PortionStatus.COMPLETED)
    return completed, plan.total_portions


async def list_for_khatm(session: AsyncSession, khatm_id) -> list[KhatmPortion]:
    return await repository.list_for_khatm(session, khatm_id)


async def list_assigned_positional_portions(session: AsyncSession) -> list[KhatmPortion]:
    return await repository.list_assigned_positional_portions(session)


async def release_portion(session: AsyncSession, portion_id) -> None:
    """A missed-deadline portion goes back to the shared OPEN pool — the
    "emergency pool" (DOMAIN_MODEL.md §3) anyone in the khatm can then claim
    via `claim_next_open_portion`. See DECISIONS.md DEC-PY-0009: the original
    holder is NOT auto-reassigned a replacement; they keep their ACTIVE
    participation and can claim a new portion themselves like anyone else."""
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
