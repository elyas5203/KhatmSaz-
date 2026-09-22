import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_content_preferences_are_independent_and_persisted():
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        await session.flush()
        await settings_service.set_content_option(session, user_id, "translation", True)
        await settings_service.set_content_option(session, user_id, "tafsir", False)
        settings = await settings_service.get_or_create(session, user_id)
        assert settings.translation_enabled is True
        assert settings.tafsir_enabled is False
        assert settings.quran_audio_enabled is False
        settings = await settings_service.set_quran_audio_enabled(session, user_id, True)
        assert settings.quran_audio_enabled is True
        with pytest.raises(ValueError, match="unsupported content option"):
            await settings_service.set_content_option(session, user_id, "audio", True)
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
