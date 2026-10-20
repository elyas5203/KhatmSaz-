"""Unit and integration tests for MASTER-58: Motivational Reminders,
Creator Inactivity Alerts & Daily Digest Engine.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.notification.models import NotificationKind
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.reminder_engine.service import (
    _maybe_record_miss_and_notify_creator,
    check_share_occurrence_misses,
)
from khatmsaz.modules.reporting.creator_daily_report import (
    build_creator_daily_report_message,
    deliver_creator_daily_reports,
    format_khatm_amount,
)
from khatmsaz.bot.member_copy import build_motivational_progress_snippet


@pytest.fixture
def dummy_khatm():
    k = Khatm(
        id=uuid.uuid4(),
        creator_user_id=uuid.uuid4(),
        title="ختم صلوات فرج",
        khatm_type=KhatmTypeEnum.COMMITMENT,
        template_type=KhatmTemplateType.SALAWAT,
        status=KhatmStatus.ACTIVE,
        repetition_target=14000,
        miss_notice_threshold=2,
        miss_notice_window_days=3,
    )
    return k


@pytest.fixture
def dummy_participation(dummy_khatm):
    p = Participation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        khatm_id=dummy_khatm.id,
        status=ParticipationStatus.ACTIVE,
        is_committed=True,
    )
    return p


@pytest.mark.asyncio
async def test_miss_below_threshold_does_not_alert_creator(dummy_khatm, dummy_participation):
    """When member misses 1 day (< threshold 2), miss is recorded but creator is not alerted."""
    session = AsyncMock()
    notify = AsyncMock()

    with (
        patch("khatmsaz.modules.notification.service.already_sent_today", return_value=False),
        patch("khatmsaz.modules.notification.service.record_sent", new_callable=AsyncMock) as mock_record,
        patch("khatmsaz.modules.notification.service.total_miss_count", return_value=1),
        patch("khatmsaz.modules.reminder_engine.service._notify_user_with_keyboard", new_callable=AsyncMock) as mock_notify_kb,
        patch("khatmsaz.modules.reminder_engine.service._notify_user", new_callable=AsyncMock) as mock_notify_plain,
    ):
        await _maybe_record_miss_and_notify_creator(session, notify, dummy_participation, dummy_khatm)

        mock_record.assert_awaited_once_with(session, dummy_participation.id, NotificationKind.FOLLOW_UP)
        mock_notify_kb.assert_not_called()
        mock_notify_plain.assert_not_called()


@pytest.mark.asyncio
async def test_miss_at_or_above_threshold_alerts_creator_with_action_buttons(dummy_khatm, dummy_participation):
    """When member reaches threshold (2 misses), creator receives alert with phone and action buttons."""
    session = AsyncMock()
    notify = AsyncMock()

    dummy_member = MagicMock()
    dummy_member.display_name = "علی رضایی"

    dummy_member_settings = MagicMock()
    dummy_member_settings.contact_phone = "09123456789"

    dummy_creator_settings = MagicMock()
    dummy_creator_settings.language = "fa"

    with (
        patch("khatmsaz.modules.notification.service.already_sent_today", return_value=False),
        patch("khatmsaz.modules.notification.service.record_sent", new_callable=AsyncMock) as mock_record,
        patch("khatmsaz.modules.notification.service.total_miss_count", return_value=2),
        patch("khatmsaz.modules.identity.service.find_by_id", return_value=dummy_member),
        patch("khatmsaz.modules.settings.service.get_or_create", side_effect=[dummy_member_settings, dummy_creator_settings]),
        patch("khatmsaz.modules.message_template.service.render", return_value=None),
        patch("khatmsaz.modules.reminder_engine.service._notify_user_with_keyboard", new_callable=AsyncMock) as mock_notify_kb,
        patch("khatmsaz.modules.reminder_engine.service._notify_user", new_callable=AsyncMock) as mock_notify_plain,
    ):
        mock_notify_kb.return_value = 1  # 1 delivery success

        await _maybe_record_miss_and_notify_creator(session, notify, dummy_participation, dummy_khatm)

        mock_record.assert_awaited_once_with(session, dummy_participation.id, NotificationKind.FOLLOW_UP)
        mock_notify_kb.assert_awaited_once()

        # Check call arguments
        call_args = mock_notify_kb.call_args
        creator_user_id = call_args[0][1]
        msg_text = call_args[0][2]
        keyboard = call_args[0][3]

        assert creator_user_id == dummy_khatm.creator_user_id
        assert "09123456789" in msg_text
        assert "علی رضایی" in msg_text
        assert "۲ روز متوالی" in msg_text or "2 روز متوالی" in msg_text

        # Verify inline action buttons
        assert len(keyboard.inline_keyboard) == 2
        btn_member = keyboard.inline_keyboard[0][0]
        btn_khatm = keyboard.inline_keyboard[1][0]

        assert "بررسی و مدیریت این عضو" in btn_member.text
        assert btn_member.callback_data == f"km:v:{dummy_participation.id.hex}"

        assert "مدیریت ختم" in btn_khatm.text
        assert btn_khatm.callback_data == f"my_khatms:manage:{dummy_khatm.id}"


@pytest.mark.asyncio
async def test_miss_alert_deduplication_same_day(dummy_khatm, dummy_participation):
    """When already sent today, creator is NOT alerted again."""
    session = AsyncMock()
    notify = AsyncMock()

    with (
        patch("khatmsaz.modules.notification.service.already_sent_today", return_value=True),
        patch("khatmsaz.modules.notification.service.record_sent", new_callable=AsyncMock) as mock_record,
        patch("khatmsaz.modules.reminder_engine.service._notify_user_with_keyboard", new_callable=AsyncMock) as mock_notify_kb,
    ):
        await _maybe_record_miss_and_notify_creator(session, notify, dummy_participation, dummy_khatm)

        mock_record.assert_not_called()
        mock_notify_kb.assert_not_called()


@pytest.mark.asyncio
async def test_check_share_occurrence_misses_scans_and_deduplicates():
    """check_share_occurrence_misses queries overdue uncompleted shares and deduplicates participations."""
    session = AsyncMock()
    notify = AsyncMock()

    part_id = uuid.uuid4()
    occ1 = MagicMock()
    occ1.id = uuid.uuid4()
    occ1.participation_id = part_id

    occ2 = MagicMock()
    occ2.id = uuid.uuid4()
    occ2.participation_id = part_id  # Duplicate participation in same scan

    mock_res = MagicMock()
    mock_res.scalars.return_value = [occ1, occ2]
    session.execute.return_value = mock_res

    part = MagicMock()
    part.id = part_id
    part.status = ParticipationStatus.ACTIVE
    part.khatm_id = uuid.uuid4()

    khatm = MagicMock()
    khatm.id = part.khatm_id
    khatm.status = KhatmStatus.ACTIVE

    with (
        patch("khatmsaz.modules.participation.repository.get_by_id", return_value=part),
        patch("khatmsaz.modules.khatm.service.get_khatm", return_value=khatm),
        patch("khatmsaz.modules.reminder_engine.service._maybe_record_miss_and_notify_creator", new_callable=AsyncMock) as mock_miss,
    ):
        await check_share_occurrence_misses(session, notify)

        # Should only be called once because occ1 and occ2 have the same participation_id
        mock_miss.assert_awaited_once_with(session, notify, part, khatm)


@pytest.mark.asyncio
async def test_creator_daily_report_generation(dummy_khatm):
    """build_creator_daily_report_message renders Persian report and interactive buttons."""
    session = AsyncMock()
    local_now = datetime(2026, 10, 20, 12, 0, 0, tzinfo=timezone.utc)
    today_start = datetime(2026, 10, 20, 0, 0, 0, tzinfo=timezone.utc)
    now_utc = local_now

    with (
        patch("khatmsaz.modules.reporting.creator_daily_report.get_khatm_daily_counts", return_value=(500.0, 200.0, 700.0, 15)),
        patch("khatmsaz.modules.reporting.creator_daily_report.format_khatm_amount", side_effect=lambda s, k, amt: f"{int(amt)} صلوات"),
    ):
        msg_text, keyboard = await build_creator_daily_report_message(
            session, [dummy_khatm], local_now, today_start, now_utc
        )

        assert "گزارش روزانه ختم‌های شما (ساعت ۱۲:۰۰ ظهر)" in msg_text
        assert "پیشرفت تا دیروز: ۵۰۰ صلوات" in msg_text or "500 صلوات" in msg_text
        assert "قرائت‌های امروز (تا ساعت ۱۲): ۲۰۰ صلوات" in msg_text or "200 صلوات" in msg_text
        assert "همراهان فعال: ۱۵ نفر" in msg_text or "15 نفر" in msg_text

        # Verify buttons
        all_buttons = [b for row in keyboard.inline_keyboard for b in row]
        button_texts = [b.text for b in all_buttons]
        callback_datas = [b.callback_data for b in all_buttons]

        assert any("مدیریت این ختم" in t for t in button_texts)
        assert any(f"my_khatms:manage:{dummy_khatm.id}" in c for c in callback_datas)
        assert any("فهرست همه ختم‌ها" in t for t in button_texts)


@pytest.mark.asyncio
async def test_motivational_progress_snippet_formatting(dummy_khatm):
    """build_motivational_progress_snippet returns clean summary of progress."""
    session = AsyncMock()

    with (
        patch("khatmsaz.modules.reporting.creator_daily_report.get_khatm_daily_counts", return_value=(1000.0, 300.0, 1300.0, 20)),
        patch("khatmsaz.modules.reporting.creator_daily_report.format_khatm_amount", side_effect=lambda s, k, amt: f"{int(amt)} صلوات"),
        patch("khatmsaz.bot.member_copy.content_family", return_value="salawat"),
    ):
        snippet = await build_motivational_progress_snippet(session, dummy_khatm)

        assert "روند پیشرفت کلی این ختم" in snippet
        assert "قرائت تا دیروز: ۱۰۰۰ صلوات" in snippet or "1000 صلوات" in snippet
        assert "قرائت‌های امروز: ۳۰۰ صلوات" in snippet or "300 صلوات" in snippet
        assert "مجموع قرائت‌شده: <b>۱۳۰۰ صلوات</b>" in snippet or "1300 صلوات" in snippet
        assert "پیشرفت:" in snippet
