import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import KhatmReciter
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reciter_favorite_uses_khatm_whitelist_then_falls_back():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(UserSettings(user_id=user_id, preferred_reciter="abdulbasit"))
        session.add(Khatm(
            id=khatm_id, creator_user_id=user_id, title="قاری تستی",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE,
        ))
        await session.flush()
        await content_service.set_allowed_reciters(session, khatm_id, ["husary", "minshawi"])
        assert await content_service.get_effective_reciter(session, khatm_id, user_id) == "husary"
        await content_service.set_user_favorite(session, user_id, "minshawi")
        assert await content_service.get_effective_reciter(session, khatm_id, user_id) == "minshawi"
        await content_service.set_allowed_reciters(session, khatm_id, [])
        assert await content_service.get_effective_reciter(session, khatm_id, user_id) == "parhizgar"

        await session.execute(delete(KhatmReciter).where(KhatmReciter.khatm_id == khatm_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
