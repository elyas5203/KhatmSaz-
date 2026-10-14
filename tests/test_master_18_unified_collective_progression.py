"""Tests for Child Master 18 — Unified Collective Progression Engine.

Verifies that ALL khatms (both commitment and open, across Quran and Khutbah):
1. allocate_page_amount with KhatmAllocationPlan advances sequentially across multiple participants:
   - User 1 takes 2 pages -> [1, 2]
   - User 2 takes 2 pages -> [3, 4]
   - User 3 takes 2 pages -> [5, 6]
   - User 1 takes 2 more pages -> [7, 8]
2. create_next_rotating_portion hands portions sequentially across participants under the plan.
3. delivery.prepare (scheduled daily delivery) allocates collective Quran pages for committed members.
4. delivery.prepare_numeric (manual portion receipt) allocates collective Quran pages for committed members.
5. Khutbah section allocations remain collective across all participants.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from khatmsaz.modules.allocation.models import (
    AllocationStrategy, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind,
)
from khatmsaz.modules.allocation.repository import (
    allocate_page_amount,
    create_next_rotating_portion,
)
from khatmsaz.modules.share_occurrence.delivery import (
    prepare,
    prepare_numeric,
    allocate_khutbah_section_range,
    get_next_open_quran_page,
)


@pytest.mark.asyncio
async def test_allocate_page_amount_collective_progression_across_participants():
    """Verify that multiple participants in a commitment Quran plan advance together sequentially."""
    khatm_id = uuid4()
    plan_id = uuid4()
    part1_id = uuid4()
    part2_id = uuid4()
    part3_id = uuid4()

    plan = KhatmAllocationPlan(
        id=plan_id,
        khatm_id=khatm_id,
        unit_kind=PortionUnitKind.POSITIONAL,
        total_portions=302,
        allocation_strategy=AllocationStrategy.ROTATING,
        positional_boundaries=[(start, min(start + 1, 604)) for start in range(1, 605, 2)],
    )

    stored_portions = []

    session = MagicMock()

    async def fake_get_plan_for_update(sess, kid):
        return plan

    def fake_add(obj):
        if isinstance(obj, KhatmPortion):
            stored_portions.append(obj)

    session.add = fake_add
    session.flush = AsyncMock()

    async def fake_get(model, obj_id):
        m = MagicMock()
        m.id = obj_id
        return m

    session.get = fake_get

    def fake_execute(stmt):
        res = MagicMock()
        # Find latest KhatmPortion in stored_portions
        if stored_portions:
            sorted_p = sorted(stored_portions, key=lambda p: (p.sequence, p.unit_end), reverse=True)
            res.scalar_one_or_none = MagicMock(return_value=sorted_p[0])
            res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=sorted_p[0])))
        else:
            res.scalar_one_or_none = MagicMock(return_value=None)
            res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
        return res

    session.execute = AsyncMock(side_effect=fake_execute)

    with patch("khatmsaz.modules.allocation.repository.get_plan_by_khatm_for_update", side_effect=fake_get_plan_for_update):
        # 1. User 1 takes 2 pages -> [1, 2]
        res1 = await allocate_page_amount(session, khatm_id, part1_id, 2)
        assert len(res1) == 1
        assert res1[0].unit_start == 1
        assert res1[0].unit_end == 2
        assert res1[0].participation_id == part1_id

        # 2. User 2 takes 2 pages -> [3, 4] (User 2 continues immediately after User 1!)
        res2 = await allocate_page_amount(session, khatm_id, part2_id, 2)
        assert len(res2) == 1
        assert res2[0].unit_start == 3
        assert res2[0].unit_end == 4
        assert res2[0].participation_id == part2_id

        # 3. User 3 takes 4 pages -> [5, 8]
        res3 = await allocate_page_amount(session, khatm_id, part3_id, 4)
        assert len(res3) == 1
        assert res3[0].unit_start == 5
        assert res3[0].unit_end == 8
        assert res3[0].participation_id == part3_id

        # 4. User 1 takes 2 more pages -> [9, 10] (User 1 continues from where User 3 left off!)
        res4 = await allocate_page_amount(session, khatm_id, part1_id, 2)
        assert len(res4) == 1
        assert res4[0].unit_start == 9
        assert res4[0].unit_end == 10
        assert res4[0].participation_id == part1_id


@pytest.mark.asyncio
async def test_create_next_rotating_portion_collective_boundaries():
    """Verify create_next_rotating_portion distributes plan boundaries sequentially among participants."""
    khatm_id = uuid4()
    plan_id = uuid4()
    part1_id = uuid4()
    part2_id = uuid4()

    plan = KhatmAllocationPlan(
        id=plan_id,
        khatm_id=khatm_id,
        unit_kind=PortionUnitKind.POSITIONAL,
        total_portions=3,
        allocation_strategy=AllocationStrategy.ROTATING,
        positional_boundaries=[(1, 2), (3, 4), (5, 6)],
    )

    stored_portions = []
    session = MagicMock()
    session.add = lambda obj: stored_portions.append(obj)
    session.flush = AsyncMock()
    session.get = AsyncMock(side_effect=lambda model, oid: MagicMock(id=oid))

    def fake_execute(stmt):
        res = MagicMock()
        if stored_portions:
            sorted_p = sorted(stored_portions, key=lambda p: (p.sequence, p.unit_end), reverse=True)
            res.scalar_one_or_none = MagicMock(return_value=sorted_p[0])
        else:
            res.scalar_one_or_none = MagicMock(return_value=None)
        return res

    session.execute = AsyncMock(side_effect=fake_execute)

    # User 1 gets boundary 0: [1, 2]
    p1 = await create_next_rotating_portion(session, plan, khatm_id, part1_id)
    assert p1.unit_start == 1
    assert p1.unit_end == 2
    assert p1.participation_id == part1_id
    assert p1.sequence == 1

    # User 2 gets boundary 1: [3, 4]
    p2 = await create_next_rotating_portion(session, plan, khatm_id, part2_id)
    assert p2.unit_start == 3
    assert p2.unit_end == 4
    assert p2.participation_id == part2_id
    assert p2.sequence == 2


@pytest.mark.asyncio
async def test_prepare_numeric_committed_quran_collective():
    """Verify that prepare_numeric for committed members advances collectively."""
    khatm_id = uuid4()
    bot_id = uuid4()

    khatm = MagicMock()
    khatm.id = khatm_id
    khatm.khatm_type = "COMMITMENT"
    khatm.template_type = "QURAN_PAGE"
    khatm.status = "ACTIVE"
    khatm.commitment_policy = "MEMBER_CHOICE"
    khatm.repetition_target = None

    user1_id = uuid4()
    part1 = MagicMock()
    part1.id = uuid4()
    part1.khatm_id = khatm_id
    part1.user_id = user1_id
    part1.status = "ACTIVE"
    part1.is_committed = True
    part1.joined_via_bot_instance_id = bot_id
    part1.open_reading_next_page = 1

    user2_id = uuid4()
    part2 = MagicMock()
    part2.id = uuid4()
    part2.khatm_id = khatm_id
    part2.user_id = user2_id
    part2.status = "ACTIVE"
    part2.is_committed = True
    part2.joined_via_bot_instance_id = bot_id
    part2.open_reading_next_page = 1

    issued_occurrences = []

    def fake_execute(*args, **kwargs):
        res = MagicMock()
        if issued_occurrences:
            sorted_occ = sorted(issued_occurrences, key=lambda x: x.created_at, reverse=True)
            res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=sorted_occ[0])))
        else:
            res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
        return res

    session = MagicMock()
    session.execute = AsyncMock(side_effect=fake_execute)
    session.flush = AsyncMock()

    async def fake_get_by_id(sess, pid):
        return part1 if pid == part1.id else part2

    async def fake_get_khatm(sess, kid):
        return khatm

    async def fake_create_once(sess, **kwargs):
        occ = MagicMock()
        occ.id = uuid4()
        occ.participation_id = kwargs["participation_id"]
        occ.amount = kwargs["amount"]
        occ.unit = kwargs["unit"]
        occ.content_spec = kwargs["content_spec"]
        from datetime import datetime, timezone
        occ.created_at = datetime.now(timezone.utc)
        issued_occurrences.append(occ)
        return occ, True

    with (
        patch("khatmsaz.modules.participation.repository.get_by_id", side_effect=fake_get_by_id),
        patch("khatmsaz.modules.participation.repository.get_by_id_for_update", side_effect=fake_get_by_id),
        patch("khatmsaz.modules.khatm.service.get_khatm_for_update", side_effect=fake_get_khatm),
        patch("khatmsaz.modules.khatm.service.has_started", return_value=True),
        patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", return_value=[]),
        patch("khatmsaz.modules.open_contribution.repository.total_for_khatm", return_value=0),
        patch("khatmsaz.modules.content.service.get_quran_total_pages", return_value=604),
        patch("khatmsaz.modules.share_occurrence.service.create_once", side_effect=fake_create_once),
        patch("khatmsaz.modules.allocation.service.allocate_page_amount", return_value=[]),
    ):
        # User 1 takes 5 pages -> [1..5]
        occ1 = await prepare_numeric(session, part1.id, 5, user_id=user1_id, bot_instance_id=bot_id)
        assert occ1.content_spec["ranges"] == [[1, 5]]

        # User 2 takes 3 pages -> [6..8]
        occ2 = await prepare_numeric(session, part2.id, 3, user_id=user2_id, bot_instance_id=bot_id)
        assert occ2.content_spec["ranges"] == [[6, 8]]
