"""Persistence access for moderated creator messages."""

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.broadcast.models import (
    BroadcastReceiptStatus,
    BroadcastStatus,
    KhatmBroadcast,
    KhatmBroadcastReceipt,
)


async def create(
    session: AsyncSession, *, khatm_id, creator_user_id, body: str,
    target_scope: str, channel: str, audience_count: int, cost_toman: int,
    target_province: str | None = None, target_gender: str | None = None,
    media_type: str | None = None, media_file_id_telegram: str | None = None,
    media_file_id_bale: str | None = None,
) -> KhatmBroadcast:
    item = KhatmBroadcast(
        id=new_id(), khatm_id=khatm_id, creator_user_id=creator_user_id,
        body=body, status=BroadcastStatus.PENDING, target_scope=target_scope,
        target_province=target_province, target_gender=target_gender,
        channel=channel, audience_count=audience_count, cost_toman=cost_toman,
        media_type=media_type, media_file_id_telegram=media_file_id_telegram,
        media_file_id_bale=media_file_id_bale,
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


async def count_lifetime_digital_for_creator(session, creator_user_id) -> int:
    """Count reserved/used Telegram+Bale messages; rejected requests do not consume quota."""
    from sqlalchemy import func
    result = await session.execute(select(func.count(KhatmBroadcast.id)).where(
        KhatmBroadcast.creator_user_id == creator_user_id,
        KhatmBroadcast.channel.in_(["TELEGRAM", "BALE"]),
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


async def create_receipts(session: AsyncSession, receipts: list[dict]) -> int:
    """Bulk create per-recipient broadcast receipts."""
    if not receipts:
        return 0
    instances = [
        KhatmBroadcastReceipt(
            id=r.get("id") or new_id(),
            broadcast_id=r["broadcast_id"],
            recipient_user_id=r["recipient_user_id"],
            channel=r.get("channel", "TELEGRAM"),
            status=r.get("status", BroadcastReceiptStatus.DELIVERED.value),
            delivered_at=r.get("delivered_at") or datetime.now(timezone.utc),
            seen_at=r.get("seen_at"),
            seen_source=r.get("seen_source"),
        )
        for r in receipts
    ]
    session.add_all(instances)
    await session.flush()
    return len(instances)


async def mark_user_receipts_seen(
    session: AsyncSession, user_id, source: str = "BOT_ACTIVITY",
) -> int:
    """Mark all unread receipts for a given user as seen upon any bot interaction."""
    stmt = (
        update(KhatmBroadcastReceipt)
        .where(
            KhatmBroadcastReceipt.recipient_user_id == user_id,
            KhatmBroadcastReceipt.seen_at.is_(None),
        )
        .values(
            status=BroadcastReceiptStatus.SEEN.value,
            seen_at=datetime.now(timezone.utc),
            seen_source=source,
        )
    )
    res = await session.execute(stmt)
    await session.flush()
    return getattr(res, "rowcount", 0) or 0


async def get_broadcast_stats(session: AsyncSession, broadcast_id) -> dict:
    """Return aggregated delivered and seen statistics for a broadcast."""
    stmt = (
        select(
            func.count(KhatmBroadcastReceipt.id).label("total_receipts"),
            func.count(KhatmBroadcastReceipt.seen_at).label("seen_receipts"),
        )
        .where(KhatmBroadcastReceipt.broadcast_id == broadcast_id)
    )
    row = (await session.execute(stmt)).one_or_none()
    total = row[0] if row else 0
    seen = row[1] if row else 0
    unseen = max(0, total - seen)
    pct = round((seen / total * 100), 1) if total > 0 else 0.0
    return {
        "total": total,
        "seen": seen,
        "unseen": unseen,
        "seen_percentage": pct,
    }


async def list_broadcast_receipts(
    session: AsyncSession, broadcast_id, limit: int = 50, offset: int = 0,
) -> list:
    """Return paginated recipients with their seen status for a broadcast."""
    from khatmsaz.modules.identity.models import User
    stmt = (
        select(KhatmBroadcastReceipt, User)
        .join(User, User.id == KhatmBroadcastReceipt.recipient_user_id)
        .where(KhatmBroadcastReceipt.broadcast_id == broadcast_id)
        .order_by(
            KhatmBroadcastReceipt.seen_at.desc().nullslast(),
            KhatmBroadcastReceipt.delivered_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )
    return list((await session.execute(stmt)).all())


async def list_recent_broadcasts_for_creator(
    session: AsyncSession, creator_user_id, limit: int = 10,
) -> list[KhatmBroadcast]:
    """Return recent sent broadcasts for creator."""
    stmt = (
        select(KhatmBroadcast)
        .where(
            KhatmBroadcast.creator_user_id == creator_user_id,
            KhatmBroadcast.status == BroadcastStatus.SENT,
        )
        .order_by(KhatmBroadcast.sent_at.desc().nullslast(), KhatmBroadcast.created_at.desc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars())
