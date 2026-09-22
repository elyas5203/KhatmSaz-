import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_can_configure_miss_notice_policy():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(Khatm(
            id=khatm_id, creator_user_id=user_id, title="آستانه میس",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE,
        ))
        await session.flush()
        khatm = await service.set_miss_notice_policy(
            session, khatm_id=khatm_id, creator_user_id=user_id, threshold=3, window_days=14
        )
        assert (khatm.miss_notice_threshold, khatm.miss_notice_window_days) == (3, 14)
        with pytest.raises(ValueError):
            await service.set_miss_notice_policy(
                session, khatm_id=khatm_id, creator_user_id=user_id, threshold=0, window_days=14
            )
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
