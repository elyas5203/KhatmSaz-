from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.ids import new_id
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scheduled_start_is_persisted_and_blocks_delivery_until_time():
    user_id = new_id()
    khatm_id = new_id()
    future = datetime.now(timezone.utc) + timedelta(days=1)
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(
            Khatm(
                id=khatm_id,
                creator_user_id=user_id,
                title="ختم آینده",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE,
                start_at=future,
            )
        )
        await session.flush()
        khatm = await khatm_service.get_khatm(session, khatm_id)
        assert khatm is not None
        assert not khatm_service.has_started(khatm)
        assert khatm_service.has_started(khatm, now=future + timedelta(seconds=1))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
