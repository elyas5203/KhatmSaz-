"""Persistence access for identity — the only place that runs SQL for this module."""

from sqlalchemy import String, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole, UserStatus
from khatmsaz.modules.settings.models import UserSettings


async def find_by_platform_identity(
    session: AsyncSession, platform: Platform, subject: str
) -> User | None:
    stmt = (
        select(User)
        .join(PlatformIdentity, PlatformIdentity.user_id == User.id)
        .where(PlatformIdentity.platform == platform, PlatformIdentity.subject == subject)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_platform_identity(
    session: AsyncSession, platform: Platform, subject: str
) -> PlatformIdentity | None:
    return await session.scalar(
        select(PlatformIdentity).where(
            PlatformIdentity.platform == platform,
            PlatformIdentity.subject == str(subject),
        )
    )


async def find_by_id(session: AsyncSession, user_id: str) -> User | None:
    return await session.get(User, user_id)


async def search_users(
    session: AsyncSession, query: str, *, limit: int = 10, offset: int = 0
) -> list[User]:
    """Find canonical users by a bounded name, phone, identity, or UUID query."""
    needle = query.strip()
    
    stmt = select(User)
    
    if needle:
        pattern = f"%{needle}%"
        stmt = (
            stmt
            .outerjoin(PlatformIdentity, PlatformIdentity.user_id == User.id)
            .outerjoin(UserSettings, UserSettings.user_id == User.id)
            .where(
                or_(
                    User.display_name.ilike(pattern),
                    UserSettings.contact_phone.ilike(pattern),
                    PlatformIdentity.subject == needle,
                    User.id.cast(String).ilike(pattern),
                )
            )
            .distinct()
        )
        
    from sqlalchemy.orm import selectinload
    stmt = (
        stmt
        .options(selectinload(User.platform_identities))
        .order_by(User.created_at.desc())
        .offset(max(0, offset))
        .limit(max(1, min(limit, 50)))
    )
    result = await session.execute(stmt)
    return list(result.scalars())


async def create_user_with_platform_identity(
    session: AsyncSession, platform: Platform, subject: str
) -> User:
    """Raises `sqlalchemy.exc.IntegrityError` if a concurrent request won the
    race for this (platform, subject) first — see `identity/service.py` for
    the retry. Runs inside a SAVEPOINT so a lost race leaves no orphan `User`
    row behind (without it, the `User` insert above would still commit even
    though the `PlatformIdentity` insert failed)."""
    async with session.begin_nested():
        user = User(id=new_id())
        session.add(user)
        await session.flush()

        identity = PlatformIdentity(id=new_id(), user_id=user.id, platform=platform, subject=subject)
        session.add(identity)
        await session.flush()

    return user


async def attach_platform_identity(
    session: AsyncSession, user_id: str, platform: Platform, subject: str
) -> None:
    identity = PlatformIdentity(id=new_id(), user_id=user_id, platform=platform, subject=subject)
    session.add(identity)
    await session.flush()


async def list_platform_identities(session: AsyncSession, user_id: str) -> list[PlatformIdentity]:
    stmt = select(PlatformIdentity).where(PlatformIdentity.user_id == user_id)
    result = await session.execute(stmt)
    return list(result.scalars())


async def set_status(session: AsyncSession, user_id, status: UserStatus) -> None:
    user = await session.get(User, user_id)
    if user is None:
        return
    user.status = status
    await session.flush()


async def set_role(session: AsyncSession, user_id, role: UserRole) -> None:
    user = await session.get(User, user_id)
    if user is None:
        return
    user.role = role
    await session.flush()


async def set_display_name(session: AsyncSession, user_id, display_name: str) -> None:
    user = await session.get(User, user_id)
    if user is None:
        return
    user.display_name = display_name
    await session.flush()
