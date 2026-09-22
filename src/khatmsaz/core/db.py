"""Async SQLAlchemy engine/session setup. One engine for the whole process."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from khatmsaz.config import get_settings


class Base(DeclarativeBase):
    """Shared declarative base for every module's models."""


_engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
_session_factory = async_sessionmaker(bind=_engine, expire_on_commit=False)


def get_engine():
    return _engine


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Yield a session, committing on success and rolling back on error."""
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
