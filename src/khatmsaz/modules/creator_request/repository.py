"""Repository layer for creator requests — thin DB-access functions."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.creator_request.models import CreatorRequest, CreatorRequestStatus


async def create(session: AsyncSession, user_id: uuid.UUID) -> CreatorRequest:
    """Insert a new PENDING creator request."""
    req = CreatorRequest(id=uuid.uuid4(), user_id=user_id)
    session.add(req)
    await session.flush()
    return req


async def get_pending_by_user(
    session: AsyncSession, user_id: uuid.UUID,
) -> CreatorRequest | None:
    """Return the latest PENDING request for this user, if any."""
    result = await session.execute(
        select(CreatorRequest)
        .where(
            CreatorRequest.user_id == user_id,
            CreatorRequest.status == CreatorRequestStatus.PENDING,
        )
        .order_by(CreatorRequest.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_by_id(
    session: AsyncSession, request_id: uuid.UUID,
) -> CreatorRequest | None:
    return await session.get(CreatorRequest, request_id)


async def list_pending(
    session: AsyncSession, *, limit: int = 50,
) -> list[CreatorRequest]:
    result = await session.execute(
        select(CreatorRequest)
        .where(CreatorRequest.status == CreatorRequestStatus.PENDING)
        .order_by(CreatorRequest.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def approve(
    session: AsyncSession,
    request_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    *,
    note: str | None = None,
) -> CreatorRequest | None:
    req = await get_by_id(session, request_id)
    if req is None or req.status != CreatorRequestStatus.PENDING:
        return None
    req.status = CreatorRequestStatus.APPROVED
    req.reviewed_at = datetime.now(timezone.utc)
    req.reviewed_by = reviewer_id
    req.admin_note = note
    await session.flush()
    return req


async def reject(
    session: AsyncSession,
    request_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    *,
    note: str | None = None,
) -> CreatorRequest | None:
    req = await get_by_id(session, request_id)
    if req is None or req.status != CreatorRequestStatus.PENDING:
        return None
    req.status = CreatorRequestStatus.REJECTED
    req.reviewed_at = datetime.now(timezone.utc)
    req.reviewed_by = reviewer_id
    req.admin_note = note
    await session.flush()
    return req
