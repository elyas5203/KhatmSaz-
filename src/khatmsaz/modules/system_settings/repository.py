from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.system_settings.models import SystemSetting


async def get(session: AsyncSession, key: str) -> str | None:
    row = await session.get(SystemSetting, key)
    return row.value if row is not None else None


async def set(session: AsyncSession, key: str, value: str) -> SystemSetting:
    stmt = (
        insert(SystemSetting)
        .values(key=key, value=value)
        .on_conflict_do_update(index_elements=[SystemSetting.key], set_={"value": value})
        .returning(SystemSetting)
    )
    result = await session.execute(stmt)
    await session.flush()
    return result.scalar_one()


async def list_all(session: AsyncSession) -> list[SystemSetting]:
    result = await session.execute(select(SystemSetting).order_by(SystemSetting.key))
    return list(result.scalars())
