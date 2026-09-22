"""Real PostgreSQL coverage for template history and activation control."""

import uuid

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.modules.message_template import repository
from khatmsaz.modules.message_template.models import MessageTemplate


@pytest.mark.integration
@pytest.mark.asyncio
async def test_template_version_toggle_falls_back_to_previous_enabled_version():
    key = "pytest.template." + uuid.uuid4().hex
    async with session_scope() as session:
        first = await repository.create(
            session, key=key, locale="fa", body="نسخه اول", version=1
        )
        second = await repository.create(
            session, key=key, locale="fa", body="نسخه دوم", version=2
        )

        assert (await repository.get_latest(session, key, "fa")).id == second.id
        await repository.set_enabled(session, key, "fa", 2, False)
        assert (await repository.get_latest(session, key, "fa")).id == first.id

        history = await repository.list_versions(session, key, "fa")
        assert [item.version for item in history] == [2, 1]
        assert [item.enabled for item in history] == [False, True]

        await session.execute(delete(MessageTemplate).where(MessageTemplate.key == key))
