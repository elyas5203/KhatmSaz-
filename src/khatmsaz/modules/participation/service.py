"""Participation business logic.

`join()` decides committed-vs-waiting when a capacity limit is set
(DEC-PY-0010); the caller (`khatm_workflow`) is responsible for what
"committed" then triggers (portion assignment) — this module only owns the
`Participation` row itself.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.participation import repository
from khatmsaz.modules.participation.models import Participation, ParticipationStatus


class AlreadyParticipatingError(Exception):
    """Raised when a user tries to join a khatm they already have an ACTIVE
    participation in. The DB partial unique index is the real backstop —
    this check just gives a friendlier error before hitting it."""


async def join(
    session: AsyncSession, khatm_id, user_id, *, capacity: int | None = None,
    joined_via_bot_instance_id=None, force_open: bool = False,
) -> tuple[Participation, bool]:
    """Returns (participation, was_waitlisted). If `capacity` is given and
    the number of currently-committed participants has reached it, the new
    participation is created with `is_committed=False` and `was_waitlisted`
    is True — the caller adds them to the waiting_list queue.

    Known limitation: the capacity check-then-insert is not fully race-safe
    (two joins landing at the exact capacity boundary at the same instant
    could both read "under capacity" before either commits) — see
    DEBUGGING.md. Accepted for now: worst case is a soft product limit
    being off by one or two, not a security/data-integrity issue."""
    existing = await repository.get_active(session, khatm_id, user_id)
    if existing is not None:
        raise AlreadyParticipatingError()

    is_committed = not force_open
    if capacity is not None and not force_open:
        current = await repository.count_committed_active(session, khatm_id)
        is_committed = current < capacity

    try:
        participation = await repository.create(
            session, khatm_id, user_id, is_committed=is_committed,
            joined_via_bot_instance_id=joined_via_bot_instance_id,
        )
    except IntegrityError:
        # Lost a race: a concurrent join for the same (khatm, user) committed
        # first (e.g. a double-tapped invite link). Treat it the same as
        # "already participating" rather than crashing the handler.
        raise AlreadyParticipatingError() from None

    # ``force_open`` is a reading mode, not a waiting-list condition.
    return participation, capacity is not None and not is_committed


async def promote_to_committed(session: AsyncSession, participation_id) -> None:
    await repository.set_committed(session, participation_id, True)


async def leave(session: AsyncSession, participation_id, *, reason: str | None = None) -> None:
    await repository.set_status(session, participation_id, ParticipationStatus.LEFT, leave_reason=reason)


async def set_paused_until(session: AsyncSession, participation_id, until) -> None:
    await repository.set_paused_until(session, participation_id, until)


async def set_backup_reader_opt_in(session: AsyncSession, participation_id, enabled: bool) -> None:
    await repository.set_backup_reader_opt_in(session, participation_id, enabled)


async def set_open_reading_pages_per_day(session: AsyncSession, participation_id, pages_per_day: int) -> None:
    await repository.set_open_reading_pages_per_day(session, participation_id, pages_per_day)


async def advance_open_reading(session: AsyncSession, participation_id, pages: int) -> tuple[int, int] | None:
    return await repository.advance_open_reading(session, participation_id, pages)


async def mark_open_reading_sent_now(session: AsyncSession, participation_id) -> None:
    from datetime import datetime, timezone

    await repository.mark_open_reading_sent_now(session, participation_id, datetime.now(timezone.utc))


async def list_active_with_open_reading_plan(session: AsyncSession) -> list[Participation]:
    return await repository.list_active_with_open_reading_plan(session)


# ---- R11: member-chosen commitment mode --------------------------------------

async def set_commitment_count(session: AsyncSession, participation_id, target: int) -> None:
    await repository.set_commitment_count(session, participation_id, target)


async def log_commitment_count(session: AsyncSession, participation_id, amount: int) -> tuple[int, int, bool] | None:
    return await repository.log_commitment_count(session, participation_id, amount)


async def set_commitment_schedule(
    session: AsyncSession, participation_id, *, freq: str, hour: int, minute: int,
    times_per_period: int, weekdays: str | None = None,
) -> None:
    await repository.set_commitment_schedule(
        session, participation_id, freq=freq, hour=hour, minute=minute,
        times_per_period=times_per_period, weekdays=weekdays,
    )


async def mark_schedule_sent_now(session: AsyncSession, participation_id) -> None:
    from datetime import datetime, timezone

    await repository.mark_schedule_sent_now(session, participation_id, datetime.now(timezone.utc))


async def list_active_with_regular_schedule(session: AsyncSession) -> list[Participation]:
    return await repository.list_active_with_regular_schedule(session)


async def set_creator_resolution(session: AsyncSession, participation_id, resolution: str) -> None:
    await repository.set_creator_resolution(session, participation_id, resolution)


async def is_paused(participation) -> bool:
    from datetime import datetime, timezone

    return participation.paused_until is not None and participation.paused_until > datetime.now(timezone.utc)


async def list_my_active(
    session: AsyncSession, user_id, *, joined_via_bot_instance_id=None
) -> list[Participation]:
    return await repository.list_active_for_user(
        session, user_id, joined_via_bot_instance_id=joined_via_bot_instance_id
    )


async def get_by_id(session: AsyncSession, participation_id) -> Participation | None:
    return await repository.get_by_id(session, participation_id)


async def count_for_khatm(session: AsyncSession, khatm_id) -> int:
    return await repository.count_for_khatm(session, khatm_id)


async def list_active_for_khatm(session: AsyncSession, khatm_id) -> list[Participation]:
    return await repository.list_active_for_khatm(session, khatm_id)


async def list_active_with_users(session: AsyncSession, khatm_id):
    return await repository.list_active_with_users(session, khatm_id)


async def get_active(session: AsyncSession, khatm_id, user_id) -> Participation | None:
    return await repository.get_active(session, khatm_id, user_id)
