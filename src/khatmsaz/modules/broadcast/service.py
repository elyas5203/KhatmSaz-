"""Business rules for creator messages requiring moderation."""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.broadcast import repository
from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmStatus


async def submit(session: AsyncSession, *, khatm_id, creator_user_id, body: str) -> KhatmBroadcast:
    body = body.strip()
    if not body or len(body) > 1000:
        raise ValueError("broadcast body must be between 1 and 1000 characters")
    khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id or khatm.status != KhatmStatus.ACTIVE:
        raise ValueError("only the creator of an active khatm may submit a broadcast")
    return await repository.create(session, khatm_id=khatm_id, creator_user_id=creator_user_id, body=body)


async def get(session: AsyncSession, broadcast_id) -> KhatmBroadcast | None:
    return await repository.get_by_id(session, broadcast_id)


async def list_pending(session: AsyncSession) -> list[KhatmBroadcast]:
    return await repository.list_pending(session)


async def approve(session: AsyncSession, broadcast_id, note: str | None = None) -> KhatmBroadcast:
    item = await repository.get_by_id(session, broadcast_id)
    if item is None or item.status != BroadcastStatus.PENDING:
        raise ValueError("broadcast is not pending")
    await repository.mark_reviewed(session, item, BroadcastStatus.APPROVED, note)
    return item


async def reject(session: AsyncSession, broadcast_id, note: str | None = None) -> KhatmBroadcast:
    item = await repository.get_by_id(session, broadcast_id)
    if item is None or item.status != BroadcastStatus.PENDING:
        raise ValueError("broadcast is not pending")
    await repository.mark_reviewed(session, item, BroadcastStatus.REJECTED, note)
    return item


async def mark_sent(session: AsyncSession, item: KhatmBroadcast) -> None:
    await repository.mark_sent(session, item)
