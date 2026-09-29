"""Persistence access for moderated creator messages."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast


async def create(
    session: AsyncSession, *, khatm_id, creator_user_id, body: str,
    target_scope: str, channel: str, audience_count: int, cost_toman: int,
) -> KhatmBroadcast:
    item = KhatmBroadcast(
        id=new_id(), khatm_id=khatm_id, creator_user_id=creator_user_id,
        body=body, status=BroadcastStatus.PENDING, target_scope=target_scope,
        channel=channel, audience_count=audience_count, cost_toman=cost_toman,
    )
    session.add(item)
    await session.flush()
    return item


async def get_by_id(session: AsyncSession, broadcast_id) -> KhatmBroadcast | None:
    return await session.get(KhatmBroadcast, broadcast_id)


async def list_pending(session: AsyncSession) -> list[KhatmBroadcast]:
    result = await session.execute(
        select(KhatmBroadcast)
        .where(KhatmBroadcast.status == BroadcastStatus.PENDING)
        .order_by(KhatmBroadcast.created_at.asc())
    )
    return list(result.scalars())


async def count_recent_for_creator_channel(session, creator_user_id, channel: str, since: datetime) -> int:
    from sqlalchemy import func
    result = await session.execute(select(func.count(KhatmBroadcast.id)).where(
        KhatmBroadcast.creator_user_id == creator_user_id,
        KhatmBroadcast.channel == channel,
        KhatmBroadcast.created_at >= since,
        KhatmBroadcast.status.in_([
            BroadcastStatus.PENDING, BroadcastStatus.APPROVED, BroadcastStatus.SENT,
        ]),
    ))
    return int(result.scalar_one())


async def mark_reviewed(session: AsyncSession, item: KhatmBroadcast, status: BroadcastStatus, note: str | None) -> None:
    item.status = status
    item.admin_note = note
    item.reviewed_at = datetime.now(timezone.utc)
    await session.flush()


async def mark_sent(session: AsyncSession, item: KhatmBroadcast) -> None:
    item.status = BroadcastStatus.SENT
    item.sent_at = datetime.now(timezone.utc)
    await session.flush()
