import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_can_toggle_skip_today_only_for_committed_quran():
    user_id, khatm_id, other_id = new_id(), new_id(), new_id()
    async with session_scope() as session:
        session.add_all([
            User(id=user_id), User(id=other_id),
            Khatm(
                id=khatm_id, creator_user_id=user_id, title="قرآن",
                template_type=KhatmTemplateType.QURAN_PAGE,
                khatm_type=KhatmTypeEnum.COMMITMENT, status=KhatmStatus.ACTIVE,
                allow_skip_today=True,
            ),
        ])
        await session.flush()
        updated = await khatm_service.set_allow_skip_today(
            session, khatm_id=khatm_id, creator_user_id=user_id, enabled=False
        )
        assert updated.allow_skip_today is False
        with pytest.raises(ValueError):
            await khatm_service.set_allow_skip_today(
                session, khatm_id=khatm_id, creator_user_id=other_id, enabled=True
            )
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([user_id, other_id])))
