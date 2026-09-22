"""Waiting-list business logic: a simple FIFO queue keyed by khatm."""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.waiting_list import repository
from khatmsaz.modules.waiting_list.models import WaitingList


async def join(session: AsyncSession, khatm_id, user_id) -> WaitingList:
    return await repository.add(session, khatm_id, user_id)


async def promote_next(session: AsyncSession, khatm_id) -> WaitingList | None:
    """Pop and return the first-in-line waiting entry, or None if the queue
    is empty. The caller (khatm_workflow) is responsible for actually
    turning this into a committed participation + portion assignment."""
    return await repository.pop_first(session, khatm_id)
