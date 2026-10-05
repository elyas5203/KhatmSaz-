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


@pytest.fixture
def scope_legacy_delivery_scan(monkeypatch):
    """Run real legacy queries but limit a scenario to its own khatm's rows.

    Integration tests share PostgreSQL, so global scans must not consume other
    tests' memberships. Transport is mocked separately by each scenario.
    """
    from khatmsaz.modules.allocation import service as allocation
    from khatmsaz.modules.participation import service as participation

    def scope(khatm_id):
        for module, name in (
            (allocation, "list_latest_portion_per_participation"),
            (participation, "list_active_with_open_reading_plan"),
        ):
            original = getattr(module, name)

            async def filtered(session, _original=original):
                return [row for row in await _original(session) if row.khatm_id == khatm_id]

            monkeypatch.setattr(module, name, filtered)
    return scope
