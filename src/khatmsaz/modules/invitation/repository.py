"""Persistence access for invitation — the only place that runs SQL for this module."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.invitation.models import KhatmInvitation


async def create(session: AsyncSession, khatm_id, created_by_user_id, token_hash: str, expires_at) -> KhatmInvitation:
    invitation = KhatmInvitation(
        id=new_id(),
        khatm_id=khatm_id,
        created_by_user_id=created_by_user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    session.add(invitation)
    await session.flush()
    return invitation


async def get_by_token_hash(session: AsyncSession, token_hash: str) -> KhatmInvitation | None:
    stmt = select(KhatmInvitation).where(KhatmInvitation.token_hash == token_hash)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def mark_accepted(session: AsyncSession, token_hash: str, user_id) -> None:
    invitation = await get_by_token_hash(session, token_hash)
    if invitation is None or invitation.accepted_at is not None:
        return
    invitation.accepted_at = datetime.now(timezone.utc)
    invitation.accepted_by_user_id = user_id
    await session.flush()


async def list_for_khatm(session: AsyncSession, khatm_id) -> list[KhatmInvitation]:
    stmt = (
        select(KhatmInvitation)
        .where(
            KhatmInvitation.khatm_id == khatm_id,
            KhatmInvitation.cancelled_at.is_(None),
        )
        .order_by(KhatmInvitation.created_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def cancel_all_for_khatm(session: AsyncSession, khatm_id) -> int:
    """Mark all active invitations for a khatm as cancelled/revoked."""
    stmt = (
        select(KhatmInvitation)
        .where(
            KhatmInvitation.khatm_id == khatm_id,
            KhatmInvitation.cancelled_at.is_(None),
        )
    )
    result = await session.execute(stmt)
    invitations = list(result.scalars().all())
    now = datetime.now(timezone.utc)
    for inv in invitations:
        inv.cancelled_at = now
    await session.flush()
    return len(invitations)

