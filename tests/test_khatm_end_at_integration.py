from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_due_end_time_closes_active_khatm_and_is_idempotent():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(Khatm(
            id=khatm_id, creator_user_id=user_id, title="پایان تاریخی",
            template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
            status=KhatmStatus.ACTIVE, end_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        ))
        await session.flush()
        assert await service.close_due_khatms(session) == 1
        assert await service.close_due_khatms(session) == 0
        khatm = await service.get_khatm(session, khatm_id)
        assert khatm.status == KhatmStatus.COMPLETED
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
