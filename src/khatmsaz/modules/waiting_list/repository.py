"""Persistence access for waiting_list — the only place that runs SQL for this module."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.waiting_list.models import WaitingList


async def add(session: AsyncSession, khatm_id, user_id) -> WaitingList:
    stmt = select(func.coalesce(func.max(WaitingList.position), 0)).where(WaitingList.khatm_id == khatm_id)
    result = await session.execute(stmt)
    next_position = int(result.scalar_one()) + 1

    entry = WaitingList(id=new_id(), khatm_id=khatm_id, user_id=user_id, position=next_position)
    session.add(entry)
    await session.flush()
    return entry


async def pop_first(session: AsyncSession, khatm_id) -> WaitingList | None:
    stmt = (
        select(WaitingList)
        .where(WaitingList.khatm_id == khatm_id)
        .order_by(WaitingList.position.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    result = await session.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry is None:
        return None
    await session.delete(entry)
    await session.flush()
    return entry
