import pytest
from sqlalchemy import delete

import khatmsaz.core.model_registry  # noqa: F401
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import (
    Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum, KhatmVisibility,
)
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.participation.models import Participation


@pytest.mark.integration
@pytest.mark.asyncio
async def test_only_creator_can_approve_private_join_request():
    creator_id, attacker_id, requester_id, khatm_id = [new_id() for _ in range(4)]
    async with session_scope() as session:
        session.add_all([
            User(id=creator_id), User(id=attacker_id), User(id=requester_id),
            Khatm(
                id=khatm_id, creator_user_id=creator_id, title="خصوصی",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE,
                visibility=KhatmVisibility.PRIVATE,
            ),
        ])
        await session.flush()

        with pytest.raises(PermissionError):
            await workflow_service.approve_join_request(
                session, khatm_id, requester_id, creator_user_id=attacker_id
            )

        khatm, participation, _portion, _waitlisted = await workflow_service.approve_join_request(
            session, khatm_id, requester_id, creator_user_id=creator_id
        )
        assert khatm.id == khatm_id
        assert participation.user_id == requester_id

        await session.execute(delete(Participation).where(Participation.khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, attacker_id, requester_id])))
