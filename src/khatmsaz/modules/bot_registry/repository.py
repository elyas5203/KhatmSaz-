from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import BotInstance, BotRole


async def list_active(session: AsyncSession) -> list[BotInstance]:
    result = await session.execute(
        select(BotInstance).where(BotInstance.is_active.is_(True)),
    )
    return list(result.scalars().all())


async def list_active_members(session: AsyncSession) -> list[BotInstance]:
    result = await session.execute(
        select(BotInstance).where(
            BotInstance.is_active.is_(True),
            BotInstance.bot_role == BotRole.MEMBER,
            BotInstance.token_encrypted != "",
        ),
    )
    return list(result.scalars().all())


async def list_all(session: AsyncSession) -> list[BotInstance]:
    result = await session.execute(
        select(BotInstance).order_by(
            BotInstance.platform,
            BotInstance.bot_role.desc(),
            BotInstance.category,
            BotInstance.language,
        ),
    )
    return list(result.scalars().all())


async def get_by_id(session: AsyncSession, instance_id: UUID) -> BotInstance | None:
    return await session.get(BotInstance, instance_id)


async def get_by_slot(
    session: AsyncSession,
    platform: str,
    bot_role: str,
    category: str | None,
    language: str | None,
) -> BotInstance | None:
    q = select(BotInstance).where(
        BotInstance.platform == platform,
        BotInstance.bot_role == bot_role,
    )
    if category is None:
        q = q.where(BotInstance.category.is_(None))
    else:
        q = q.where(BotInstance.category == category)
    if language is None:
        q = q.where(BotInstance.language.is_(None))
    else:
        q = q.where(BotInstance.language == language)
    result = await session.execute(q)
    return result.scalar_one_or_none()


async def set_token(
    session: AsyncSession,
    instance_id: UUID,
    token_encrypted: str,
    username: str,
) -> None:
    await session.execute(
        update(BotInstance)
        .where(BotInstance.id == instance_id)
        .values(token_encrypted=token_encrypted, username=username),
    )


async def toggle_active(
    session: AsyncSession,
    instance_id: UUID,
    is_active: bool,
) -> None:
    await session.execute(
        update(BotInstance)
        .where(BotInstance.id == instance_id)
        .values(is_active=is_active),
    )
