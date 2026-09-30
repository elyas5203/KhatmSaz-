"""Persistence access for participation — the only place that runs SQL for this module."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.participation.models import Participation, ParticipationStatus


async def get_active(session: AsyncSession, khatm_id, user_id) -> Participation | None:
    stmt = select(Participation).where(
        Participation.khatm_id == khatm_id,
        Participation.user_id == user_id,
        Participation.status == ParticipationStatus.ACTIVE,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession, khatm_id, user_id, is_committed: bool = True,
    *, joined_via_bot_instance_id=None,
) -> Participation:
    """Raises `sqlalchemy.exc.IntegrityError` if a concurrent request already
    joined this (khatm, user) first — see `participation/service.py` for the
    retry. Runs inside a SAVEPOINT so a lost race doesn't poison the caller's
    outer transaction (same pattern as `identity/repository.py`).

    `joined_via_bot_instance_id` records which member bot the user joined
    through, so daily reminders/notifications route back via the exact same
    bot (multi-bot notification routing)."""
    async with session.begin_nested():
        participation = Participation(
            id=new_id(), khatm_id=khatm_id, user_id=user_id, is_committed=is_committed,
            joined_via_bot_instance_id=joined_via_bot_instance_id,
        )
        session.add(participation)
        await session.flush()
    return participation


async def count_committed_active(session: AsyncSession, khatm_id) -> int:
    stmt = select(func.count()).select_from(Participation).where(
        Participation.khatm_id == khatm_id,
        Participation.status == ParticipationStatus.ACTIVE,
        Participation.is_committed.is_(True),
    )
    result = await session.execute(stmt)
    return int(result.scalar_one())


async def count_for_khatm(session: AsyncSession, khatm_id) -> int:
    result = await session.execute(
        select(func.count()).select_from(Participation).where(Participation.khatm_id == khatm_id)
    )
    return int(result.scalar_one())


async def list_active_for_khatm(session: AsyncSession, khatm_id) -> list[Participation]:
    result = await session.execute(
        select(Participation).where(
            Participation.khatm_id == khatm_id,
            Participation.status == ParticipationStatus.ACTIVE,
        )
    )
    return list(result.scalars())


async def list_active_with_users(session: AsyncSession, khatm_id) -> list[tuple[Participation, User]]:
    result = await session.execute(
        select(Participation, User)
        .join(User, User.id == Participation.user_id)
        .where(
            Participation.khatm_id == khatm_id,
            Participation.status == ParticipationStatus.ACTIVE,
        )
        .order_by(Participation.joined_at.asc())
    )
    return list(result.all())


async def set_committed(session: AsyncSession, participation_id, is_committed: bool) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.is_committed = is_committed
    await session.flush()


async def set_creator_resolution(session: AsyncSession, participation_id, resolution: str) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.creator_resolution = resolution
    await session.flush()


async def set_status(
    session: AsyncSession, participation_id, status: ParticipationStatus, leave_reason: str | None = None
) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.status = status
    if leave_reason is not None:
        participation.leave_reason = leave_reason
    await session.flush()


async def set_paused_until(session: AsyncSession, participation_id, until) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.paused_until = until
    await session.flush()


async def set_backup_reader_opt_in(session: AsyncSession, participation_id, enabled: bool) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.backup_reader_opt_in = enabled
    await session.flush()


async def set_open_reading_pages_per_day(session: AsyncSession, participation_id, pages_per_day: int) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.open_reading_pages_per_day = pages_per_day
    await session.flush()


async def advance_open_reading(session: AsyncSession, participation_id, pages: int) -> tuple[int, int] | None:
    """Reserve the next `pages` pages for this open reader, advancing the
    cursor, and return the (start, end) 1-based range reserved. Returns
    None if the participation doesn't exist. Does not cap against the
    edition's total page count — the caller (which already knows the
    khatm's total) is responsible for passing a `pages` value that doesn't
    overrun it."""
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return None
    start = participation.open_reading_next_page
    end = start + pages - 1
    participation.open_reading_next_page = end + 1
    await session.flush()
    return start, end


async def mark_open_reading_sent_now(session: AsyncSession, participation_id, when) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.open_reading_last_sent_at = when
    await session.flush()


async def list_active_with_open_reading_plan(session: AsyncSession) -> list[Participation]:
    """All ACTIVE participations that have set up an open-Quran-reading
    daily plan — used by the reminder engine's daily auto-send scan."""
    stmt = select(Participation).where(
        Participation.status == ParticipationStatus.ACTIVE,
        Participation.open_reading_pages_per_day.isnot(None),
    )
    result = await session.execute(stmt)
    return list(result.scalars())


# ---- R11: member-chosen commitment mode (COUNT / REGULAR) ------------------

async def set_commitment_count(session: AsyncSession, participation_id, target: int) -> None:
    """COUNT mode: pledge to read `target` repetitions, resetting progress."""
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    from khatmsaz.modules.participation.commitment import CommitmentMode
    participation.commitment_mode = CommitmentMode.COUNT.value
    participation.commitment_target = target
    participation.commitment_done = 0
    # clear any REGULAR fields so the two modes never coexist
    participation.schedule_freq = None
    participation.schedule_anchor = None
    participation.schedule_hour = None
    participation.commitment_per_occurrence = None
    await session.flush()


async def log_commitment_count(session: AsyncSession, participation_id, amount: int) -> tuple[int, int, bool] | None:
    """Add `amount` to a COUNT-mode member's logged total. Returns
    (new_done, target, completed) or None if the participation is missing."""
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return None
    from khatmsaz.modules.participation.commitment import log_count
    new_done, completed = log_count(participation.commitment_done or 0, participation.commitment_target, amount)
    participation.commitment_done = new_done
    await session.flush()
    return new_done, participation.commitment_target, completed


async def set_commitment_schedule(
    session: AsyncSession, participation_id, *, freq: str, hour: int, minute: int,
    times_per_period: int, weekdays: str | None = None,
) -> None:
    """REGULAR mode: recurring schedule delivered by the reminder engine.

    Reused columns: schedule_anchor holds the reminder MINUTE (exact HH:MM),
    commitment_per_occurrence holds TIMES-PER-PERIOD. `weekdays` (Persian indices
    «0,1,4») applies only to WEEKLY (owner L4)."""
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    from khatmsaz.modules.participation.commitment import CommitmentMode
    participation.commitment_mode = CommitmentMode.REGULAR.value
    participation.schedule_freq = freq
    participation.schedule_hour = hour
    participation.schedule_anchor = minute
    participation.schedule_weekdays = weekdays if freq == "WEEKLY" else None
    participation.commitment_per_occurrence = times_per_period
    # clear COUNT fields
    participation.commitment_target = None
    participation.commitment_done = 0
    await session.flush()


async def mark_schedule_sent_now(session: AsyncSession, participation_id, when) -> None:
    participation = await session.get(Participation, participation_id)
    if participation is None:
        return
    participation.schedule_last_sent_at = when
    await session.flush()


async def list_active_with_regular_schedule(session: AsyncSession) -> list[Participation]:
    """All ACTIVE participations on a REGULAR commitment schedule — the
    reminder engine's scan source (mirrors list_active_with_open_reading_plan)."""
    from khatmsaz.modules.participation.commitment import CommitmentMode
    stmt = select(Participation).where(
        Participation.status == ParticipationStatus.ACTIVE,
        Participation.commitment_mode == CommitmentMode.REGULAR.value,
        Participation.schedule_freq.isnot(None),
    )
    result = await session.execute(stmt)
    return list(result.scalars())


async def list_active_for_user(
    session: AsyncSession, user_id, *, joined_via_bot_instance_id=None
) -> list[Participation]:
    stmt = select(Participation).where(
        Participation.user_id == user_id, Participation.status == ParticipationStatus.ACTIVE
    )
    if joined_via_bot_instance_id is not None:
        stmt = stmt.where(Participation.joined_via_bot_instance_id == joined_via_bot_instance_id)
    result = await session.execute(stmt)
    return list(result.scalars())


async def get_by_id(session: AsyncSession, participation_id) -> Participation | None:
    return await session.get(Participation, participation_id)
