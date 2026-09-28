from datetime import datetime, timedelta
from typing import Sequence
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.creator_broadcast.models import CreatorBroadcast
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.identity.models import PlatformIdentity

async def get_creator_audience_count(
    session: AsyncSession, creator_id: uuid.UUID, *, khatm_id: uuid.UUID | None = None
) -> int:
    """Distinct active members across all the creator's khatms, or scoped to
    a single khatm when `khatm_id` is given (per-khatm broadcast targeting)."""
    stmt = (
        select(func.count(Participation.user_id.distinct()))
        .select_from(Participation)
        .join(Khatm, Khatm.id == Participation.khatm_id)
        .where(Khatm.creator_user_id == creator_id)
        .where(Participation.status == ParticipationStatus.ACTIVE)
    )
    if khatm_id is not None:
        stmt = stmt.where(Participation.khatm_id == khatm_id)
    result = await session.execute(stmt)
    return result.scalar_one() or 0

async def get_broadcast_count_last_7_days(session: AsyncSession, creator_id: uuid.UUID) -> int:
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    stmt = (
        select(func.count(CreatorBroadcast.id))
        .where(CreatorBroadcast.creator_id == creator_id)
        .where(CreatorBroadcast.created_at >= seven_days_ago)
    )
    result = await session.execute(stmt)
    return result.scalar_one() or 0

async def calculate_broadcast_cost(audience_count: int, broadcasts_last_7_days: int) -> int:
    if broadcasts_last_7_days < 3:
        return 0
    if audience_count <= 1000:
        return 43000
    return 93000

async def create_broadcast(
    session: AsyncSession,
    creator_id: uuid.UUID,
    platform: str,
    message_text: str | None,
    media_file_id: str | None,
    media_type: str | None,
    cost_toman: int,
    audience_count: int,
    is_paid: bool = False
) -> CreatorBroadcast:
    broadcast = CreatorBroadcast(
        creator_id=creator_id,
        platform=platform,
        message_text=message_text,
        media_file_id=media_file_id,
        media_type=media_type,
        cost_toman=cost_toman,
        audience_count=audience_count,
        is_paid=is_paid
    )
    session.add(broadcast)
    await session.flush()
    return broadcast

async def get_broadcast_audience(
    session: AsyncSession, creator_id: uuid.UUID, platform: str, *, khatm_id: uuid.UUID | None = None
) -> list[str]:
    # Returns chat_ids for the given platform, optionally scoped to one khatm.
    stmt = (
        select(PlatformIdentity.subject)
        .select_from(Participation)
        .join(Khatm, Khatm.id == Participation.khatm_id)
        .join(PlatformIdentity, PlatformIdentity.user_id == Participation.user_id)
        .where(Khatm.creator_user_id == creator_id)
        .where(Participation.status == ParticipationStatus.ACTIVE)
        .where(PlatformIdentity.platform == platform)
    )
    if khatm_id is not None:
        stmt = stmt.where(Participation.khatm_id == khatm_id)
    result = await session.execute(stmt)
    # Use distinct to avoid sending twice to the same person if they are in multiple khatms
    return list(set(result.scalars().all()))
