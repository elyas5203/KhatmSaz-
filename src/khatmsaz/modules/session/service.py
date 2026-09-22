"""Secure, opaque sessions for the admin web dashboard."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.security import generate_token, hash_token
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.identity.models import User, UserStatus
from khatmsaz.modules.session import repository


SESSION_TTL = timedelta(hours=8)


async def issue_admin_session(session: AsyncSession, user: User) -> str:
    if not await authorization_service.is_admin(session, user):
        raise PermissionError("only an active administrator may open the dashboard")
    raw = generate_token(32)
    await repository.create(
        session,
        user_id=user.id,
        token_hash=hash_token(raw),
        expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        purpose="ADMIN",
    )
    return raw


async def authenticate_admin(session: AsyncSession, raw_token: str) -> User | None:
    if not raw_token:
        return None
    item = await repository.get_active_by_hash(
        session, hash_token(raw_token), purpose="ADMIN"
    )
    if item is None:
        return None
    user = await session.get(User, item.user_id)
    if not await authorization_service.is_admin(session, user):
        return None
    await repository.touch(session, item)
    return user


async def revoke_admin_session(session: AsyncSession, raw_token: str) -> None:
    if not raw_token:
        return
    item = await repository.get_active_by_hash(session, hash_token(raw_token))
    if item is not None:
        await repository.revoke(session, item)


async def issue_creator_session(session: AsyncSession, user: User) -> str:
    if user is None or user.deleted_at is not None or user.status != UserStatus.ACTIVE:
        raise PermissionError("only an active user may open the creator dashboard")
    raw = generate_token(32)
    await repository.create(
        session,
        user_id=user.id,
        token_hash=hash_token(raw),
        expires_at=datetime.now(timezone.utc) + SESSION_TTL,
        purpose="CREATOR",
    )
    return raw


async def authenticate_creator(session: AsyncSession, raw_token: str) -> User | None:
    if not raw_token:
        return None
    item = await repository.get_active_by_hash(
        session, hash_token(raw_token), purpose="CREATOR"
    )
    if item is None:
        return None
    user = await session.get(User, item.user_id)
    if user is None or user.deleted_at is not None or user.status != UserStatus.ACTIVE:
        return None
    await repository.touch(session, item)
    return user


async def revoke_web_session(session: AsyncSession, raw_token: str, *, purpose: str) -> None:
    if not raw_token:
        return
    item = await repository.get_active_by_hash(
        session, hash_token(raw_token), purpose=purpose
    )
    if item is not None:
        await repository.revoke(session, item)
