"""Persistence operations for message templates."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.message_template.models import MessageTemplate


async def get_latest(session: AsyncSession, key: str, locale: str = "fa") -> MessageTemplate | None:
    result = await session.execute(
        select(MessageTemplate)
        .where(
            MessageTemplate.key == key,
            MessageTemplate.locale == locale,
            MessageTemplate.enabled.is_(True),
        )
        .order_by(MessageTemplate.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession,
    *,
    key: str,
    locale: str,
    body: str,
    version: int,
    enabled: bool = True,
) -> MessageTemplate:
    template = MessageTemplate(
        id=uuid.uuid4(), key=key, locale=locale, body=body,
        version=version, enabled=enabled,
    )
    session.add(template)
    await session.flush()
    return template


async def next_version(session: AsyncSession, key: str, locale: str) -> int:
    result = await session.execute(
        select(func.coalesce(func.max(MessageTemplate.version), 0)).where(
            MessageTemplate.key == key, MessageTemplate.locale == locale
        )
    )
    return int(result.scalar_one()) + 1


async def list_latest(session: AsyncSession, locale: str = "fa") -> list[MessageTemplate]:
    """Return the enabled latest version for each key in one locale."""
    latest = (
        select(
            MessageTemplate.key,
            func.max(MessageTemplate.version).label("version"),
        )
        .where(MessageTemplate.locale == locale, MessageTemplate.enabled.is_(True))
        .group_by(MessageTemplate.key)
        .subquery()
    )
    result = await session.execute(
        select(MessageTemplate)
        .join(
            latest,
            (MessageTemplate.key == latest.c.key)
            & (MessageTemplate.version == latest.c.version)
            & (MessageTemplate.locale == locale),
        )
        .order_by(MessageTemplate.key)
    )
    return list(result.scalars())


async def list_versions(
    session: AsyncSession, key: str, locale: str = "fa"
) -> list[MessageTemplate]:
    result = await session.execute(
        select(MessageTemplate)
        .where(MessageTemplate.key == key, MessageTemplate.locale == locale)
        .order_by(MessageTemplate.version.desc())
    )
    return list(result.scalars())


async def set_enabled(
    session: AsyncSession, key: str, locale: str, version: int, enabled: bool
) -> MessageTemplate | None:
    result = await session.execute(
        select(MessageTemplate).where(
            MessageTemplate.key == key,
            MessageTemplate.locale == locale,
            MessageTemplate.version == version,
        )
    )
    template = result.scalar_one_or_none()
    if template is None:
        return None
    template.enabled = enabled
    await session.flush()
    return template
