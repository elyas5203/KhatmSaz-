import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sms_opt_in_requires_phone_and_can_be_disabled():
    user_id, no_phone_id = new_id(), new_id()
    async with session_scope() as session:
        session.add_all([User(id=user_id), User(id=no_phone_id)])
        session.add(UserSettings(user_id=user_id, contact_phone="+989121234567"))
        await session.flush()

        settings = await settings_service.set_sms_enabled(session, user_id, True)
        assert settings.sms_enabled is True
        assert await settings_service.set_sms_enabled(session, user_id, False)
        with pytest.raises(ValueError, match="contact phone required"):
            await settings_service.set_sms_enabled(session, no_phone_id, True)

        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([user_id, no_phone_id])))
        await session.execute(delete(User).where(User.id.in_([user_id, no_phone_id])))
