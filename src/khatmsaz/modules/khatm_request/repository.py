"""Persistence access for khatm_request — the only place that runs SQL for this module."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.khatm_request.models import KhatmRequest, KhatmRequestStatus


async def create(session: AsyncSession, requester_user_id, description: str, **attachment) -> KhatmRequest:
    request = KhatmRequest(
        id=new_id(), requester_user_id=requester_user_id, description=description,
        **attachment,
    )
    session.add(request)
    await session.flush()
    return request


async def get_by_id(session: AsyncSession, request_id) -> KhatmRequest | None:
    return await session.get(KhatmRequest, request_id)


async def list_pending(session: AsyncSession) -> list[KhatmRequest]:
    stmt = (
        select(KhatmRequest)
        .where(KhatmRequest.status == KhatmRequestStatus.PENDING)
        .order_by(KhatmRequest.created_at.asc())
    )
    result = await session.execute(stmt)
    return list(result.scalars())


async def set_status(session: AsyncSession, request_id, status: KhatmRequestStatus, admin_note: str | None) -> None:
    request = await session.get(KhatmRequest, request_id)
    if request is None:
        return
    request.status = status
    request.admin_note = admin_note
    request.reviewed_at = datetime.now(timezone.utc)
    await session.flush()
