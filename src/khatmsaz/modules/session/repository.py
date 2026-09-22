"""Persistence operations for opaque web dashboard sessions."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.session.models import Session


async def create(
    session: AsyncSession, *, user_id, token_hash: str, expires_at, purpose: str = "ADMIN"
) -> Session:
    item = Session(
        id=new_id(), user_id=user_id, token_hash=token_hash, expires_at=expires_at,
        purpose=purpose,
    )
    session.add(item)
    await session.flush()
    return item


async def get_active_by_hash(
    session: AsyncSession, token_hash: str, *, purpose: str | None = None,
    now: datetime | None = None,
) -> Session | None:
    current = now or datetime.now(timezone.utc)
    stmt = select(Session).where(
            Session.token_hash == token_hash,
            Session.revoked_at.is_(None),
            Session.expires_at > current,
        )
    if purpose is not None:
        stmt = stmt.where(Session.purpose == purpose)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def touch(session: AsyncSession, item: Session) -> None:
    item.last_used_at = datetime.now(timezone.utc)
    await session.flush()


async def revoke(session: AsyncSession, item: Session) -> None:
    item.revoked_at = datetime.now(timezone.utc)
    await session.flush()
