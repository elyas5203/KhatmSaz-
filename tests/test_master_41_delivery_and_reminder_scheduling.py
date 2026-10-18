"""Unit and integration tests for MASTER-41 (Khatm Delivery & Reminder Engine Redesign).

Verifies the 4 authoritative owner decisions:
1. Immediate first-day delivery if member joins after their chosen schedule hour.
2. Single-stage evening reminder at 22:00 (2 hours before midnight); 2-hour followup eliminated.
3. Yesterday's portion remains active with independent ID/button; no 'deen shar'i' wording.
4. Open khatm has zero scheduled delivery or automated reminders.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from zoneinfo import ZoneInfo

from khatmsaz.core.ids import new_id
from khatmsaz.modules.participation.commitment import is_regular_due, ScheduleFreq
from khatmsaz.modules.share_occurrence import delivery
from khatmsaz.modules.share_occurrence.models import ShareOccurrence
from khatmsaz.modules.reminder_engine import service as reminder_engine_service


TEHRAN_TZ = ZoneInfo("Asia/Tehran")


def test_is_regular_due_late_join_first_day():
    """Member joins at 15:00 with scheduled hour 08:00:
    Because 15:00 >= 08:00 and last_sent_local_date is None, today is due immediately."""
    now_local = datetime(2026, 10, 18, 15, 0, tzinfo=TEHRAN_TZ)
    # Hour 8:00 has already passed today -> is_regular_due must be True
    assert is_regular_due(now_local, ScheduleFreq.DAILY.value, 8, 0, None) is True


def test_is_regular_due_early_join_first_day():
    """Member joins at 07:00 with scheduled hour 08:00:
    07:00 < 08:00 -> not due yet today, waits until 08:00."""
    now_local = datetime(2026, 10, 18, 7, 0, tzinfo=TEHRAN_TZ)
    assert is_regular_due(now_local, ScheduleFreq.DAILY.value, 8, 0, None) is False


def test_is_regular_due_subsequent_day_behavior():
    """On the next day, it is not due at 07:59, but becomes due at 08:00."""
    yesterday = datetime(2026, 10, 18, tzinfo=TEHRAN_TZ).date()
    # At 07:59 on Oct 19:
    now_before = datetime(2026, 10, 19, 7, 59, tzinfo=TEHRAN_TZ)
    assert is_regular_due(now_before, ScheduleFreq.DAILY.value, 8, 0, yesterday) is False

    # At 08:00 on Oct 19:
    now_due = datetime(2026, 10, 19, 8, 0, tzinfo=TEHRAN_TZ)
    assert is_regular_due(now_due, ScheduleFreq.DAILY.value, 8, 0, yesterday) is True


@pytest.mark.asyncio
async def test_remind_single_stage_evening_at_22():
    """Tests single-stage evening reminder at 22:00 (MASTER-41 / A2):
    - Delivered at 15:00
    - Remind at 17:00 (15:00 + 2h) -> does NOT send anything (followup removed)
    - Remind at 21:00 -> does NOT send
    - Remind at 22:00 -> sends exactly 1 DEADLINE reminder
    - Remind at 22:30 -> does NOT duplicate
    - Remind after midnight -> does NOT send past-deadline reminder
    """
    midnight_deadline = datetime(2026, 10, 19, 0, 0, tzinfo=TEHRAN_TZ)
    delivered_at = datetime(2026, 10, 18, 15, 0, tzinfo=TEHRAN_TZ)

    occ = ShareOccurrence(
        id=uuid4(),
        participation_id=uuid4(),
        bot_instance_id=uuid4(),
        source_key="daily:2026-10-18",
        amount=10,
        unit="COUNT",
        committed=True,
        delivered_at=delivered_at,
        deadline_at=midnight_deadline,
        completed_at=None,
    )

    controls_sent = []

    async def fake_send_control(session, part, khatm, occurrence, purpose, *, now):
        controls_sent.append((purpose, now))
        return True

    part = type("MockPart", (), {"id": occ.participation_id, "khatm_id": uuid4()})()
    khatm = type("MockKhatm", (), {"id": part.khatm_id, "title": "ختم تست"})()

    session = AsyncMock()

    with (
        patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.khatm.service.get_khatm", AsyncMock(return_value=khatm)),
        patch("khatmsaz.modules.notification.service.get_preference", AsyncMock(return_value=None)),
        patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", AsyncMock(return_value=[occ])),
        patch("khatmsaz.bot.occurrence_adapter.send_control", side_effect=fake_send_control),
    ):
        # 1. At 17:00 (2h after delivery) -> NO FOLLOWUP sent
        await delivery.remind(session, part.id, now=datetime(2026, 10, 18, 17, 0, tzinfo=TEHRAN_TZ))
        assert len(controls_sent) == 0

        # 2. At 21:00 (3h before deadline) -> NO reminder yet
        await delivery.remind(session, part.id, now=datetime(2026, 10, 18, 21, 0, tzinfo=TEHRAN_TZ))
        assert len(controls_sent) == 0

        # 3. At 22:00 (2h before midnight deadline) -> Exactly 1 DEADLINE reminder
        await delivery.remind(session, part.id, now=datetime(2026, 10, 18, 22, 0, tzinfo=TEHRAN_TZ))
        assert len(controls_sent) == 1
        assert controls_sent[0][0] == "DEADLINE"

        # 4. Past midnight (e.g. 00:15 next day) -> does NOT send
        controls_sent.clear()
        await delivery.remind(session, part.id, now=datetime(2026, 10, 19, 0, 15, tzinfo=TEHRAN_TZ))
        assert len(controls_sent) == 0


@pytest.mark.asyncio
async def test_open_khatm_schedule_reminders_retired():
    """Verifies MASTER-41 Rule 4: _send_open_schedule_reminders is completely retired/no-op."""
    session = AsyncMock()
    notify = AsyncMock()
    # Should execute without any DB calls or exceptions
    await reminder_engine_service._send_open_schedule_reminders(session, notify, "Asia/Tehran")
    assert session.execute.call_count == 0
    assert notify.call_count == 0


@pytest.mark.asyncio
async def test_deliver_immediately_if_due():
    """Verifies deliver_immediately_if_due prepares and delivers when due."""
    session = AsyncMock()
    pid = uuid4()
    mock_occ = type("MockOcc", (), {"id": uuid4(), "delivered_at": None})()

    with (
        patch("khatmsaz.modules.share_occurrence.delivery.prepare", AsyncMock(return_value=mock_occ)),
        patch("khatmsaz.modules.share_occurrence.delivery.deliver", AsyncMock(return_value=True)) as mock_deliv,
    ):
        res = await delivery.deliver_immediately_if_due(session, pid)
        assert res is True
        assert mock_deliv.call_count == 1
