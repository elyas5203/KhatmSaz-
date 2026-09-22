"""Real PostgreSQL coverage for the admin user-search query."""

import pytest
import uuid
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_search_finds_user_by_phone_and_platform_subject():
    user_id = new_id()
    identity_id = new_id()
    phone = "09" + uuid.uuid4().hex[:10]
    subject = "pytest-subject-" + uuid.uuid4().hex
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="جست‌وجوی آزمایشی"))
        session.add(
            PlatformIdentity(
                id=identity_id, user_id=user_id, platform=Platform.TELEGRAM, subject=subject
            )
        )
        session.add(UserSettings(user_id=user_id, contact_phone=phone))
        await session.flush()

        by_phone = await identity_service.search_users(session, phone)
        by_subject = await identity_service.search_users(session, subject)
        assert [item.id for item in by_phone] == [user_id]
        assert [item.id for item in by_subject] == [user_id]

        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.id == identity_id))
        await session.execute(delete(User).where(User.id == user_id))
