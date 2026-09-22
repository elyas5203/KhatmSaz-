from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_workflow import service as workflow_service


@pytest.mark.integration
@pytest.mark.asyncio
async def test_active_khatm_transitions_to_completed_once():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(
            Khatm(
                id=khatm_id, creator_user_id=user_id, title="هدف‌محور",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN, status=KhatmStatus.ACTIVE,
            )
        )
        await session.flush()
        completed = await khatm_service.complete_khatm(session, khatm_id)
        assert completed is not None
        assert completed.status == KhatmStatus.COMPLETED
        again = await khatm_service.complete_khatm(session, khatm_id)
        assert again is not None
        assert again.status == KhatmStatus.COMPLETED
        with pytest.raises(workflow_service.KhatmUnavailableError):
            await workflow_service._complete_join(session, again, user_id)
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
