"""Persistent proof that the free cap aggregates every devotional subtype."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm_category.models import KhatmCategory  # noqa: F401
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanTier


@pytest.mark.integration
@pytest.mark.asyncio
async def test_free_devotional_cap_combines_salawat_dua_ziyarat_and_custom_rows():
    creator_id, member_a_id, member_b_id = new_id(), new_id(), new_id()
    salawat_id, dua_id = new_id(), new_id()
    participation_ids = [new_id(), new_id()]
    async with session_scope() as session:
        session.add_all([
            User(id=creator_id), User(id=member_a_id), User(id=member_b_id),
        ])
        await session.flush()
        session.add_all([
            Khatm(
                id=salawat_id, creator_user_id=creator_id, title="صلوات سقف",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE, repetition_target=100,
            ),
            Khatm(
                id=dua_id, creator_user_id=creator_id, title="دعای قدیمی سقف",
                template_type=KhatmTemplateType.DUA, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE, repetition_target=100,
            ),
        ])
        await session.flush()
        session.add_all([
            Participation(id=participation_ids[0], khatm_id=salawat_id, user_id=member_a_id),
            Participation(id=participation_ids[1], khatm_id=dua_id, user_id=member_b_id),
        ])
        definition = await plan_service.get_definition(session, PlanTier.FREE)
        original = dict(definition.entitlements)
        definition.entitlements = {**original, "max_devotional_members": 2}
        await session.flush()
        try:
            with pytest.raises(workflow_service.PlanCapExceededError):
                await workflow_service._enforce_creation_cap(
                    session, creator_id, KhatmTemplateType.ZIYARAT
                )
            # Quran has its independent optional cap; no key means unlimited.
            await workflow_service._enforce_creation_cap(
                session, creator_id, KhatmTemplateType.QURAN_PAGE
            )
        finally:
            definition.entitlements = original
            await session.execute(delete(Participation).where(Participation.id.in_(participation_ids)))
            await session.execute(delete(Khatm).where(Khatm.id.in_([salawat_id, dua_id])))
            await session.execute(delete(User).where(User.id.in_([creator_id, member_a_id, member_b_id])))
