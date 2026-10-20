"""Unit and functional tests for MASTER-59: Unified Collective Quran Progression Relay,
Round Wrap-Around & Unread Portions Reminder Engine.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from khatmsaz.modules.allocation.models import KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind
from khatmsaz.modules.allocation.repository import allocate_page_amount
from khatmsaz.modules.share_occurrence.delivery import get_next_open_quran_page, prepare, record_progress
from khatmsaz.modules.share_occurrence.service import list_uncompleted_previous_occurrences
from khatmsaz.modules.share_occurrence.models import ShareOccurrence
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.bot import occurrence_adapter as adapter


@pytest.fixture
def canonical_plan():
    kid = uuid.uuid4()
    boundaries = [[1, 3]] + [[i, i + 1] for i in range(4, 602, 2)] + [[602, 604]]
    plan = KhatmAllocationPlan(
        id=uuid.uuid4(),
        khatm_id=kid,
        unit_kind=PortionUnitKind.POSITIONAL,
        total_portions=len(boundaries),
        allocation_strategy="ROTATING",
        positional_boundaries=boundaries,
    )
    return plan, kid


@pytest.fixture
def dummy_quran_khatm(canonical_plan):
    plan, kid = canonical_plan
    k = Khatm(
        id=kid,
        creator_user_id=uuid.uuid4(),
        title="ختم دسته‌جمعی نور",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
        status=KhatmStatus.ACTIVE,
        repetition_target=604,
        commitment_policy="MEMBER_CHOICE",
        daily_deadline_hour=24,
        quran_edition_id="madani_604",
    )
    return k, plan


@pytest.mark.asyncio
async def test_allocate_page_amount_collective_relay(canonical_plan):
    """Test collective relay portion allocation across multiple participants:
    - First allocation starting at page 1 for amount=2 spans pages 1 to 3 (audio boundary).
    - Second allocation for next participant spans pages 4 to 5.
    - Third allocation for next turn spans pages 6 to 7.
    """
    plan, kid = canonical_plan
    pid1, pid2 = uuid.uuid4(), uuid.uuid4()

    session = AsyncMock()
    part1 = Participation(id=pid1, khatm_id=kid, user_id=uuid.uuid4(), status=ParticipationStatus.ACTIVE)
    part2 = Participation(id=pid2, khatm_id=kid, user_id=uuid.uuid4(), status=ParticipationStatus.ACTIVE)

    # 1. First allocation: latest is None -> calls create_next_rotating_portion (start 1, end 3)
    with patch("khatmsaz.modules.allocation.repository.get_plan_by_khatm_for_update", return_value=plan):
        session.get = AsyncMock(return_value=part1)

        # Mock query returning no previous portions
        mock_res1 = MagicMock()
        mock_res1.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_res1)

        portions1 = await allocate_page_amount(session, kid, pid1, 2)
        assert len(portions1) == 1
        p1 = portions1[0]
        assert p1.unit_start == 1
        assert p1.unit_end == 3  # Correctly preserved audio boundary 1-3

        # 2. Second allocation for Participant 2: latest is portion 1 (ending at 3)
        session.get = AsyncMock(return_value=part2)
        mock_res2 = MagicMock()
        mock_res2.scalar_one_or_none.return_value = p1
        session.execute = AsyncMock(return_value=mock_res2)

        portions2 = await allocate_page_amount(session, kid, pid2, 2)
        assert len(portions2) == 1
        p2 = portions2[0]
        assert p2.unit_start == 4
        assert p2.unit_end == 5  # Collective relay continuous progression: 4 to 5

        # 3. Third allocation for Participant 1 next turn: latest is portion 2 (ending at 5)
        session.get = AsyncMock(return_value=part1)
        mock_res3 = MagicMock()
        mock_res3.scalar_one_or_none.return_value = p2
        session.execute = AsyncMock(return_value=mock_res3)

        portions3 = await allocate_page_amount(session, kid, pid1, 2)
        assert len(portions3) == 1
        p3 = portions3[0]
        assert p3.unit_start == 6
        assert p3.unit_end == 7  # Continues immediately from 6 to 7


@pytest.mark.asyncio
async def test_allocate_page_amount_wrap_around_to_page_1(canonical_plan):
    """When the collective cursor reaches 604, it wraps around back to page 1 for the next round."""
    plan, kid = canonical_plan
    pid = uuid.uuid4()
    part = Participation(id=pid, khatm_id=kid, user_id=uuid.uuid4(), status=ParticipationStatus.ACTIVE)

    session = AsyncMock()
    session.get = AsyncMock(return_value=part)

    with patch("khatmsaz.modules.allocation.repository.get_plan_by_khatm_for_update", return_value=plan):
        # 1. Portion ending at page 601 -> next portion covers 602 to 604
        p_pre_end = KhatmPortion(
            id=uuid.uuid4(), plan_id=plan.id, khatm_id=kid, sequence=300,
            unit_kind=PortionUnitKind.POSITIONAL, unit_start=600, unit_end=601,
            status=PortionStatus.COMPLETED, participation_id=pid,
        )
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = p_pre_end
        session.execute = AsyncMock(return_value=mock_res)

        end_portions = await allocate_page_amount(session, kid, pid, 2)
        assert len(end_portions) == 1
        p_last = end_portions[0]
        assert p_last.unit_start == 602
        assert p_last.unit_end == 604

        # 2. Latest portion is at 604 -> next portion wraps around to page 1!
        mock_res_wrap = MagicMock()
        mock_res_wrap.scalar_one_or_none.return_value = p_last
        session.execute = AsyncMock(return_value=mock_res_wrap)

        round2_portions = await allocate_page_amount(session, kid, pid, 2)
        assert len(round2_portions) == 1
        p_round2 = round2_portions[0]
        assert p_round2.unit_start == 1
        assert p_round2.unit_end == 3  # Round 2 begins from page 1 (1-3)


@pytest.mark.asyncio
async def test_get_next_open_quran_page_relay_and_wrap():
    """Verify get_next_open_quran_page correctly reads prior ShareOccurrence and wraps around 604."""
    session = AsyncMock()
    kid = uuid.uuid4()

    # When last occurrence ended on page 3 -> next is 4
    occ1 = SimpleNamespace(id=uuid.uuid4(), unit="PAGE", content_spec={"ranges": [[1, 3]]})
    mock_res1 = MagicMock()
    mock_res1.scalars.return_value.first.return_value = occ1
    session.execute = AsyncMock(return_value=mock_res1)

    next_p = await get_next_open_quran_page(session, kid, 604)
    assert next_p == 4

    # When last occurrence ended on page 604 -> wraps around to 1
    occ_end = SimpleNamespace(id=uuid.uuid4(), unit="PAGE", content_spec={"ranges": [[602, 604]]})
    mock_res2 = MagicMock()
    mock_res2.scalars.return_value.first.return_value = occ_end
    session.execute = AsyncMock(return_value=mock_res2)

    wrap_p = await get_next_open_quran_page(session, kid, 604)
    assert wrap_p == 1


@pytest.mark.asyncio
async def test_list_uncompleted_previous_occurrences():
    """Verify list_uncompleted_previous_occurrences returns only delivered uncompleted previous shares."""
    session = AsyncMock()
    pid = uuid.uuid4()
    cur_id = uuid.uuid4()
    prev1_id = uuid.uuid4()
    prev2_id = uuid.uuid4()
    prev3_id = uuid.uuid4()

    now = datetime.now(timezone.utc)
    # prev1: delivered, not completed -> should be included
    occ_prev1 = ShareOccurrence(id=prev1_id, participation_id=pid, delivered_at=now, completed_at=None, amount=2)
    # prev2: delivered, completed -> should NOT be included
    occ_prev2 = ShareOccurrence(id=prev2_id, participation_id=pid, delivered_at=now, completed_at=now, amount=2)
    # prev3: not delivered -> should NOT be included
    occ_prev3 = ShareOccurrence(id=prev3_id, participation_id=pid, delivered_at=None, completed_at=None, amount=2)
    # cur: current occurrence being prepared/delivered -> should NOT be included
    occ_cur = ShareOccurrence(id=cur_id, participation_id=pid, delivered_at=None, completed_at=None, amount=2)

    with patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", return_value=[occ_prev1, occ_prev2, occ_prev3, occ_cur]):
        unread = await list_uncompleted_previous_occurrences(session, pid, current_occurrence_id=cur_id)
        assert len(unread) == 1
        assert unread[0].id == prev1_id


def test_format_unread_reminder_persian_copy():
    """Test format_unread_reminder outputs the exact confirmed Persian reminder format."""
    # Quran page range
    occ1 = SimpleNamespace(unit="PAGE", content_spec={"ranges": [[1, 3]]}, amount=3)
    text1 = adapter.format_unread_reminder([occ1])
    assert text1 == "⚠️ یادآوری سهم گذشته: شما هنوز صفحات 1 تا 3 از نوبت قبل را تأیید نکرده‌اید؛ لطفاً آن را هم قرائت فرمایید. 🌱"

    # Multiple unread page ranges
    occ2 = SimpleNamespace(unit="PAGE", content_spec={"ranges": [[4, 5]]}, amount=2)
    text2 = adapter.format_unread_reminder([occ1, occ2])
    assert "صفحات 1 تا 3 و 4 تا 5" in text2

    # Salawat / Count
    occ_salawat = SimpleNamespace(unit="COUNT", content_spec={}, amount=500)
    text_s = adapter.format_unread_reminder([occ_salawat])
    assert "500" in text_s
    assert "صفحات" not in text_s


@pytest.mark.asyncio
async def test_unread_reminder_attached_in_send_control(dummy_quran_khatm):
    """Test send_control appends the unread reminder when ACTION is sent and user has uncompleted shares."""
    khatm, plan = dummy_quran_khatm
    session = AsyncMock()

    pid = uuid.uuid4()
    part = Participation(id=pid, khatm_id=khatm.id, user_id=uuid.uuid4(), status=ParticipationStatus.ACTIVE)
    now = datetime.now(timezone.utc)

    # Current occurrence for today (pages 4 to 5)
    cur_occ = ShareOccurrence(
        id=uuid.uuid4(), participation_id=pid, bot_instance_id=uuid.uuid4(),
        amount=2, unit="PAGE", content_spec={"ranges": [[4, 5]], "language": "fa"},
    )
    # Previous unread occurrence (pages 1 to 3)
    prev_occ = ShareOccurrence(
        id=uuid.uuid4(), participation_id=pid, delivered_at=now - timedelta(days=1),
        completed_at=None, amount=3, unit="PAGE", content_spec={"ranges": [[1, 3]], "language": "fa"},
    )

    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock(return_value=SimpleNamespace(message_id=999))

    with (
        patch("khatmsaz.modules.share_occurrence.repository.list_messages", return_value=[]),
        patch("khatmsaz.bot.occurrence_adapter.route", return_value=(mock_bot, 12345)),
        patch("khatmsaz.modules.share_occurrence.service.list_uncompleted_previous_occurrences", return_value=[prev_occ]),
        patch("khatmsaz.modules.share_occurrence.service.record_message", new_callable=AsyncMock),
    ):
        sent = await adapter.send_control(session, part, khatm, cur_occ, "ACTION", now=now)
        assert sent is True

        mock_bot.send_message.assert_awaited_once()
        sent_text = mock_bot.send_message.await_args.kwargs["text"]
        assert "⚠️ یادآوری سهم گذشته: شما هنوز صفحات 1 تا 3 از نوبت قبل را تأیید نکرده‌اید؛ لطفاً آن را هم قرائت فرمایید. 🌱" in sent_text


@pytest.mark.asyncio
async def test_multi_round_target_completion_in_record_progress(dummy_quran_khatm):
    """Test record_progress triggers complete_khatm once total pages match repetition_target."""
    khatm, plan = dummy_quran_khatm
    khatm.repetition_target = 1208  # 2 rounds
    session = AsyncMock()

    part = Participation(id=uuid.uuid4(), khatm_id=khatm.id, user_id=uuid.uuid4(), status=ParticipationStatus.ACTIVE)
    occ = ShareOccurrence(
        id=uuid.uuid4(), participation_id=part.id, amount=2, unit="PAGE",
        content_spec={"ranges": [[602, 604]], "portion_ids": []},
    )

    with (
        patch("khatmsaz.modules.khatm.service.get_khatm", return_value=khatm),
        patch("khatmsaz.modules.open_contribution.service.log_contribution", return_value=(None, None, 1208)),
        patch("khatmsaz.modules.khatm.service.complete_khatm", new_callable=AsyncMock) as mock_complete,
        patch("khatmsaz.modules.advertising.service.accrue_first_completed_action", new_callable=AsyncMock),
    ):
        await record_progress(session, part, occ)
        mock_complete.assert_awaited_once_with(session, khatm.id)
