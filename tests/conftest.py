"""Shared pytest configuration for unit and opt-in integration tests."""

import asyncio
import os

import pytest


if os.name == "nt":
    # asyncpg is reliable under SelectorEventLoop on Windows.  This also
    # matches the event-loop policy used by the bot bootstrap.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_INTEGRATION_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_INTEGRATION_TESTS=1 to run PostgreSQL tests")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(autouse=True)
async def dispose_sqlalchemy_pool_after_test():
    """Prevent asyncpg connections from crossing pytest event loops on Windows."""
    yield
    if os.getenv("RUN_INTEGRATION_TESTS") == "1":
        from khatmsaz.core.db import get_engine

        await get_engine().dispose()
