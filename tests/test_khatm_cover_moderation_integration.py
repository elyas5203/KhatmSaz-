import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cover_requires_review_before_approval():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(Khatm(
            id=khatm_id, creator_user_id=user_id, title="کاور آزمایشی",
            template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
            status=KhatmStatus.ACTIVE,
        ))
        await session.flush()
        khatm = await service.submit_cover(
            session, khatm_id=khatm_id, creator_user_id=user_id,
            cover_ref="telegram-file-id", platform="TELEGRAM",
        )
        assert khatm.cover_status == "PENDING"
        khatm = await service.review_cover(session, khatm_id=khatm_id, approved=True)
        assert khatm.cover_status == "APPROVED"
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
