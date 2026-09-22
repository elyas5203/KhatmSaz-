"""Persistence helpers for foreign-number manual verification."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.manual_phone_verification.models import ManualPhoneVerification


async def pending_for_user(session: AsyncSession, user_id) -> ManualPhoneVerification | None:
    return await session.scalar(
        select(ManualPhoneVerification).where(
            ManualPhoneVerification.user_id == user_id,
            ManualPhoneVerification.status == "PENDING",
        )
    )


async def create(
    session: AsyncSession, *, user_id, e164: str, purpose: str
) -> ManualPhoneVerification:
    request = ManualPhoneVerification(
        id=new_id(), user_id=user_id, e164=e164, purpose=purpose, status="PENDING"
    )
    session.add(request)
    await session.flush()
    return request


async def get_for_update(session: AsyncSession, request_id) -> ManualPhoneVerification | None:
    return await session.scalar(
        select(ManualPhoneVerification)
        .where(ManualPhoneVerification.id == request_id)
        .with_for_update()
    )


async def list_pending(session: AsyncSession) -> list[ManualPhoneVerification]:
    result = await session.execute(
        select(ManualPhoneVerification)
        .where(ManualPhoneVerification.status == "PENDING")
        .order_by(ManualPhoneVerification.created_at.asc())
    )
    return list(result.scalars())


async def decide(
    session: AsyncSession,
    request: ManualPhoneVerification,
    *,
    status: str,
    reviewed_by_user_id,
    admin_note: str | None = None,
) -> None:
    request.status = status
    request.reviewed_by_user_id = reviewed_by_user_id
    request.admin_note = admin_note
    request.reviewed_at = datetime.now(timezone.utc)
    await session.flush()
