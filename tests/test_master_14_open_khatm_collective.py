"""Tests for Child Master 14 — Open Khatm Collective Progression Engine.

Verifies:
1. get_next_open_quran_page falls back to default_start when no prior occurrences exist.
2. get_next_open_quran_page extracts next page from previous occurrence range.
3. get_next_open_quran_page wraps around after total_pages (e.g. 604) to page 1.
4. prepare_numeric allocates sequential collective Quran ranges across multiple users:
   - User 1 takes 5 pages -> [1, 5]
   - User 2 takes 3 pages -> [6, 8]
   - User 3 takes 10 pages -> [9, 18]
   - User 1 takes 2 more pages -> [19, 20]
5. prepare_numeric handles wrap-around at page 604 across multiple segments:
   - User at page 602 requests 5 pages -> [[602, 604], [1, 2]]
   - Next user requests 4 pages -> [[3, 6]]
6. allocate_khutbah_section_range advances sections collectively across all participants:
   - User 1 takes 2 sections -> (1, 2)
   - User 2 takes 1 section -> (3, 3)
   - User 3 takes 2 sections -> (4, 5)
   - User 4 takes 1 section -> (1, 1) [Round 2]
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from khatmsaz.modules.khatm.models import KhatmTypeEnum, KhatmTemplateType
from khatmsaz.modules.share_occurrence.delivery import (
    get_next_open_quran_page,
    allocate_khutbah_section_range,
    prepare_numeric,
)


@pytest.mark.asyncio
async def test_get_next_open_quran_page_initial_fallback():
    session = MagicMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))))
    next_page = await get_next_open_quran_page(session, uuid4(), 604, default_start=1)
    assert next_page == 1


@pytest.mark.asyncio
async def test_get_next_open_quran_page_advances_from_last_occurrence():
    session = MagicMock()
    last_occ = MagicMock()
    last_occ.content_spec = {"ranges": [[1, 5]]}
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=last_occ)))))

    next_page = await get_next_open_quran_page(session, uuid4(), 604, default_start=1)
    assert next_page == 6


@pytest.mark.asyncio
async def test_get_next_open_quran_page_wraps_around_at_604():
    session = MagicMock()
    last_occ = MagicMock()
    last_occ.content_spec = {"ranges": [[600, 604]]}
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=last_occ)))))

    next_page = await get_next_open_quran_page(session, uuid4(), 604, default_start=1)
    assert next_page == 1


@pytest.mark.asyncio
async def test_prepare_numeric_collective_quran_progression_across_users():
    khatm_id = uuid4()
    bot_id = uuid4()

    khatm = MagicMock()
    khatm.id = khatm_id
    khatm.khatm_type = "OPEN"
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
    part1.is_committed = False
    part1.joined_via_bot_instance_id = bot_id
    part1.open_reading_next_page = 1

    user2_id = uuid4()
    part2 = MagicMock()
    part2.id = uuid4()
    part2.khatm_id = khatm_id
    part2.user_id = user2_id
    part2.status = "ACTIVE"
    part2.is_committed = False
    part2.joined_via_bot_instance_id = bot_id
    part2.open_reading_next_page = 1

    issued_occurrences = []

    def fake_execute(*args, **kwargs):
        # Return the latest issued occurrence for get_next_open_quran_page
        res = MagicMock()
        last = issued_occurrences[-1] if issued_occurrences else None
        res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=last)))
        return res

    session = MagicMock()
    session.execute = AsyncMock(side_effect=fake_execute)

    async def fake_create_once(sess, **kwargs):
        occ = MagicMock()
        occ.id = uuid4()
        occ.amount = kwargs.get("amount")
        occ.content_spec = kwargs.get("content_spec")
        occ.committed = kwargs.get("committed")
        occ.source_key = kwargs.get("source_key")
        occ.reservation_id = None
        issued_occurrences.append(occ)
        return occ, True

    with (
        patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(side_effect=lambda s, pid: part1 if pid == part1.id else part2)),
        patch("khatmsaz.modules.participation.repository.get_by_id_for_update", AsyncMock(side_effect=lambda s, pid: part1 if pid == part1.id else part2)),
        patch("khatmsaz.modules.khatm.service.get_khatm_for_update", AsyncMock(return_value=khatm)),
        patch("khatmsaz.modules.khatm.service.has_started", return_value=True),
        patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", AsyncMock(return_value=[])),
        patch("khatmsaz.modules.open_contribution.repository.total_for_khatm", AsyncMock(return_value=0)),
        patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="quran")),
        patch("khatmsaz.modules.content.service.get_quran_total_pages", return_value=604),
        patch("khatmsaz.modules.share_occurrence.service.create_once", AsyncMock(side_effect=fake_create_once)),
    ):
        # 1. User 1 takes 5 pages -> [1, 5]
        occ1 = await prepare_numeric(session, part1.id, 5, user_id=user1_id, bot_instance_id=bot_id)
        assert occ1 is not None
        assert occ1.content_spec["ranges"] == [[1, 5]]

        # 2. User 2 takes 3 pages -> [6, 8]
        occ2 = await prepare_numeric(session, part2.id, 3, user_id=user2_id, bot_instance_id=bot_id)
        assert occ2 is not None
        assert occ2.content_spec["ranges"] == [[6, 8]]

        # 3. User 1 takes 10 more pages -> [9, 18]
        occ3 = await prepare_numeric(session, part1.id, 10, user_id=user1_id, bot_instance_id=bot_id)
        assert occ3 is not None
        assert occ3.content_spec["ranges"] == [[9, 18]]


@pytest.mark.asyncio
async def test_prepare_numeric_quran_wraparound_at_604():
    khatm_id = uuid4()
    bot_id = uuid4()

    khatm = MagicMock()
    khatm.id = khatm_id
    khatm.khatm_type = "OPEN"
    khatm.template_type = "QURAN_PAGE"
    khatm.status = "ACTIVE"
    khatm.commitment_policy = "MEMBER_CHOICE"
    khatm.repetition_target = None

    user_id = uuid4()
    part = MagicMock()
    part.id = uuid4()
    part.khatm_id = khatm_id
    part.user_id = user_id
    part.status = "ACTIVE"
    part.is_committed = False
    part.joined_via_bot_instance_id = bot_id
    part.open_reading_next_page = 1

    # Simulate prior occurrence that reached page 601
    prior_occ = MagicMock()
    prior_occ.content_spec = {"ranges": [[590, 601]]}
    issued = [prior_occ]

    def fake_execute(*args, **kwargs):
        res = MagicMock()
        last = issued[-1] if issued else None
        res.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=last)))
        return res

    session = MagicMock()
    session.execute = AsyncMock(side_effect=fake_execute)

    async def fake_create_once(sess, **kwargs):
        occ = MagicMock()
        occ.id = uuid4()
        occ.amount = kwargs.get("amount")
        occ.content_spec = kwargs.get("content_spec")
        occ.committed = kwargs.get("committed")
        occ.source_key = kwargs.get("source_key")
        occ.reservation_id = None
        issued.append(occ)
        return occ, True

    with (
        patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.participation.repository.get_by_id_for_update", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.khatm.service.get_khatm_for_update", AsyncMock(return_value=khatm)),
        patch("khatmsaz.modules.khatm.service.has_started", return_value=True),
        patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", AsyncMock(return_value=[])),
        patch("khatmsaz.modules.open_contribution.repository.total_for_khatm", AsyncMock(return_value=0)),
        patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="quran")),
        patch("khatmsaz.modules.content.service.get_quran_total_pages", return_value=604),
        patch("khatmsaz.modules.share_occurrence.service.create_once", AsyncMock(side_effect=fake_create_once)),
    ):
        # Starts at (601 % 604) + 1 = 602. Requests 5 pages.
        # Should cover 602..604 (3 pages) and 1..2 (2 pages) -> [[602, 604], [1, 2]]
        occ1 = await prepare_numeric(session, part.id, 5, user_id=user_id, bot_instance_id=bot_id)
        assert occ1 is not None
        assert occ1.content_spec["ranges"] == [[602, 604], [1, 2]]

        # Next request takes 4 pages -> starts at (2 % 604) + 1 = 3 -> [[3, 6]]
        occ2 = await prepare_numeric(session, part.id, 4, user_id=user_id, bot_instance_id=bot_id)
        assert occ2 is not None
        assert occ2.content_spec["ranges"] == [[3, 6]]


@pytest.mark.asyncio
async def test_allocate_khutbah_section_range_collective_across_participants():
    khatm = MagicMock()
    khatm.id = uuid4()
    khatm.title = "ختم خطبه فدکیه"

    part1_id = uuid4()
    part2_id = uuid4()
    part3_id = uuid4()

    occurrences = []

    class FakeResult:
        def __init__(self, items):
            self._items = items
        def scalars(self):
            return self._items

    session = MagicMock()
    session.execute = AsyncMock(side_effect=lambda *a, **kw: FakeResult(list(occurrences)))
    session.flush = AsyncMock()

    with (
        patch("khatmsaz.modules.content.service.resolve_khatm_devotional_source", AsyncMock(return_value=(None, "khutbah-fadakiah"))),
        patch("khatmsaz.modules.content.service.list_devotional_video_pages", AsyncMock(return_value=[
            MagicMock(page_number=i) for i in range(1, 6)
        ])),
    ):
        # User 1 takes 2 sections -> (1, 2)
        s1, e1 = await allocate_khutbah_section_range(session, part1_id, khatm, 2)
        assert (s1, e1) == (1, 2)
        occurrences.append(MagicMock(id=uuid4(), amount=2, content_spec={"ranges": [[1, 2]], "family": "khutbah"}, completed_at=None))

        # User 2 takes 1 section -> (3, 3)
        s2, e2 = await allocate_khutbah_section_range(session, part2_id, khatm, 1)
        assert (s2, e2) == (3, 3)
        occurrences.append(MagicMock(id=uuid4(), amount=1, content_spec={"ranges": [[3, 3]], "family": "khutbah"}, completed_at=None))

        # User 3 takes 2 sections -> (4, 5)
        s3, e3 = await allocate_khutbah_section_range(session, part3_id, khatm, 2)
        assert (s3, e3) == (4, 5)
        occurrences.append(MagicMock(id=uuid4(), amount=2, content_spec={"ranges": [[4, 5]], "family": "khutbah"}, completed_at=None))

        # User 1 takes 1 section -> wraps to (1, 1) (Round 2)
        s4, e4 = await allocate_khutbah_section_range(session, part1_id, khatm, 1)
        assert (s4, e4) == (1, 1)
