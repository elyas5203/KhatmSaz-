"""Persistence access for settings — the only place that runs SQL for this module."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.settings.models import UserSettings


async def get_by_user(session: AsyncSession, user_id) -> UserSettings | None:
    return await session.get(UserSettings, user_id)


async def create_for_user(session: AsyncSession, user_id) -> UserSettings:
    settings = UserSettings(user_id=user_id)
    session.add(settings)
    await session.flush()
    return settings


async def find_by_contact_phones(
    session: AsyncSession, phones: set[str]
) -> list[UserSettings]:
    if not phones:
        return []
    result = await session.execute(
        select(UserSettings).where(UserSettings.contact_phone.in_(sorted(phones)))
    )
    return list(result.scalars())


async def list_all(session: AsyncSession, *, user_ids: set | None = None) -> list[UserSettings]:
    stmt = select(UserSettings).order_by(UserSettings.user_id)
    if user_ids is not None:
        if not user_ids:
            return []
        stmt = stmt.where(UserSettings.user_id.in_(user_ids))
    result = await session.execute(stmt)
    return list(result.scalars())
