import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.allocation.models import AllocationStrategy, KhatmAllocationPlan, KhatmPortion
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401 - registers FK target
import khatmsaz.modules.bot_registry.models  # noqa: F401 - registers FK target
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.participation.models import Participation


@pytest.mark.integration
@pytest.mark.asyncio
async def test_committed_quran_readers_advance_personally_and_wrap() -> None:
    creator_id, first_user_id, second_user_id, khatm_id = [new_id() for _ in range(4)]
    async with session_scope() as session:
        session.add_all([User(id=creator_id), User(id=first_user_id), User(id=second_user_id)])
        session.add(Khatm(
            id=khatm_id, creator_user_id=creator_id, title="چرخش قرآن تست",
            template_type=KhatmTemplateType.QURAN_PAGE,
            khatm_type=KhatmTypeEnum.COMMITMENT, status=KhatmStatus.ACTIVE,
        ))
        await session.flush()
        first = await participation_repository.create(session, khatm_id, first_user_id)
        second = await participation_repository.create(session, khatm_id, second_user_id)
        plan = await allocation_service.generate_quran_page_plan(session, khatm_id, 6, 2)

        assert plan.allocation_strategy == AllocationStrategy.ROTATING.value
        first_day_first = await allocation_service.allocate_next_portion_to(session, khatm_id, first.id)
        first_day_second = await allocation_service.allocate_next_portion_to(session, khatm_id, second.id)
        assert (first_day_first.unit_start, first_day_first.unit_end) == (1, 2)
        assert (first_day_second.unit_start, first_day_second.unit_end) == (3, 4)

        await allocation_service.complete_current_portion_and_advance(session, khatm_id, first.id)
        await allocation_service.complete_current_portion_and_advance(session, khatm_id, second.id)
        second_day_first = await allocation_service.allocate_next_portion_to(session, khatm_id, first.id)
        second_day_second = await allocation_service.allocate_next_portion_to(session, khatm_id, second.id)
        assert (second_day_first.unit_start, second_day_first.unit_end) == (3, 4)
        assert (second_day_second.unit_start, second_day_second.unit_end) == (5, 6)

        await allocation_service.complete_current_portion_and_advance(session, khatm_id, first.id)
        third_day_first = await allocation_service.allocate_next_portion_to(session, khatm_id, first.id)
        assert (third_day_first.unit_start, third_day_first.unit_end) == (5, 6)
        await allocation_service.complete_current_portion_and_advance(session, khatm_id, first.id)
        wrapped = await allocation_service.allocate_next_portion_to(session, khatm_id, first.id)
        assert (wrapped.unit_start, wrapped.unit_end) == (1, 2)
        await allocation_service.release_portion(session, wrapped.id)
        await session.refresh(wrapped)
        assert wrapped.participation_id == first.id
        assert await allocation_service.count_open(session, khatm_id) == 0
        assert await allocation_service.claim_next_open_portion(session, khatm_id, second.id) is None

        await session.execute(delete(KhatmPortion).where(KhatmPortion.khatm_id == khatm_id))
        await session.execute(delete(Participation).where(Participation.khatm_id == khatm_id))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, first_user_id, second_user_id])))
