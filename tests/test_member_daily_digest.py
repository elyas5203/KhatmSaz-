"""Tests for member daily 14:00 progress digest and motivational progress banner."""

from datetime import datetime, timezone
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.member_copy import (
    build_motivational_progress_snippet,
    completion_text,
)
from khatmsaz.modules.identity.models import Platform, User, UserStatus
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.reporting.member_daily_digest import (
    build_member_daily_digest_message,
    deliver_member_daily_digests,
    get_member_today_status,
)
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.asyncio
async def test_member_today_status_detection():
    """Verify detection of DONE, PENDING, and READY status for member today."""
    session = AsyncMock(spec=AsyncSession)
    part = MagicMock(spec=Participation)
    part.id = uuid.uuid4()
    today_start = datetime(2026, 10, 11, 0, 0, 0, tzinfo=timezone.utc)

    # 1. When a completed occurrence exists today -> DONE
    session.scalar.side_effect = [1, 0, 0, 0, 0, 0]
    status = await get_member_today_status(session, part, today_start)
    assert status == "DONE"

    # 2. When no completed occurrence but pending occurrence exists -> PENDING
    session.scalar.side_effect = [0, 0, 0, 0, 1, 0]
    status = await get_member_today_status(session, part, today_start)
    assert status == "PENDING"

    # 3. When neither exists -> READY
    session.scalar.side_effect = [0, 0, 0, 0, 0, 0]
    status = await get_member_today_status(session, part, today_start)
    assert status == "READY"


@pytest.mark.asyncio
async def test_build_member_daily_digest_message():
    """Verify message formatting and action keyboard generation for members."""
    session = AsyncMock(spec=AsyncSession)
    now_utc = datetime(2026, 10, 11, 10, 30, tzinfo=timezone.utc) # 14:00 Tehran
    local_now = datetime(2026, 10, 11, 14, 0)
    today_start_utc = datetime(2026, 10, 10, 20, 30, tzinfo=timezone.utc)

    khatm = MagicMock(spec=Khatm)
    khatm.id = uuid.uuid4()
    khatm.title = "خطبه غدیر پیامبر اکرم (ص)"
    khatm.template_type = KhatmTemplateType.SALAWAT
    khatm.khatm_type = KhatmTypeEnum.OPEN
    khatm.repetition_target = 80 # 10 rounds of 8 sections
    khatm.content_category_id = None

    part = MagicMock(spec=Participation)
    part.id = uuid.uuid4()

    with (
        patch("khatmsaz.modules.reporting.member_daily_digest.get_khatm_daily_counts",
              new=AsyncMock(return_value=(24.0, 8.0, 32.0, 12))),
        patch("khatmsaz.modules.reporting.member_daily_digest.format_khatm_amount",
              new=AsyncMock(side_effect=["۳ دور", "۱ دور", "۴ دور", "۱۰ دور"])),
        patch("khatmsaz.modules.reporting.member_daily_digest.get_member_today_status",
              new=AsyncMock(return_value="PENDING")),
    ):
        body, keyboard = await build_member_daily_digest_message(
            session, [(khatm, part)], local_now, today_start_utc, now_utc
        )

        assert "خلاصه پیشرفت روزانه ختم‌های شما (ساعت ۱۴:۰۰)" in body
        assert "خطبه غدیر پیامبر اکرم (ص)" in body
        assert "پیشرفت کل ختم تا دیروز: ۳ دور" in body
        assert "قرائت‌های امروز ختم (تا ساعت ۱۴): ۱ دور" in body
        assert "مجموع قرائت‌شده: <b>۴ دور</b>" in body
        assert "وضعیت سهم شما: ⏳ سهم امروز شما منتظر قرائت است." in body
        assert len(keyboard.inline_keyboard) == 1
        btn = keyboard.inline_keyboard[0][0]
        assert "انجام سهم" in btn.text
        assert btn.callback_data == f"today_pick:{part.id}"


@pytest.mark.asyncio
async def test_motivational_progress_snippet_and_completion_text():
    """Verify motivational progress snippet rendering and integration in completion_text."""
    session = AsyncMock(spec=AsyncSession)
    khatm = MagicMock(spec=Khatm)
    khatm.title = "صلوات برای فرج"
    khatm.niyyat = "تعجیل در فرج"
    khatm.template_type = KhatmTemplateType.SALAWAT
    khatm.repetition_target = 14000
    khatm.content_category_id = None

    with (
        patch("khatmsaz.modules.reporting.creator_daily_report.get_khatm_daily_counts",
              new=AsyncMock(return_value=(5000.0, 2000.0, 7000.0, 25))),
        patch("khatmsaz.modules.reporting.creator_daily_report.format_khatm_amount",
              new=AsyncMock(side_effect=["۵،۰۰۰ صلوات", "۲،۰۰۰ صلوات", "۷،۰۰۰ صلوات", "۱۴،۰۰۰ صلوات"])),
    ):
        snippet = await build_motivational_progress_snippet(session, khatm)
        assert "روند پیشرفت کلی این ختم" in snippet
        assert "قرائت تا دیروز: ۵،۰۰۰ صلوات" in snippet
        assert "قرائت‌های امروز: ۲،۰۰۰ صلوات" in snippet
        assert "مجموع قرائت‌شده: <b>۷،۰۰۰ صلوات</b> از <b>۱۴،۰۰۰ صلوات</b>" in snippet
        assert "۵۰.۰٪" in snippet

        invite_line = "\n\nبا ارسال این لینک برای دوستانتون، اون‌ها رو هم به مشارکت در همین ثواب دعوت کنید:\nhttps://t.me/salawat_Khatm_fa_bot?start=join_abc"
        msg1 = completion_text(
            khatm, "salawat", "۱۰۰ صلوات", invite_line=invite_line, lang="fa"
        )
        assert "✅ ۱۰۰ صلوات انجام شد." in msg1
        assert "خداوند از شما قبول فرماید. با تشکر." in msg1
        assert "https://t.me/salawat_Khatm_fa_bot?start=join_abc" in msg1
        assert "روند پیشرفت کلی این ختم" not in msg1


@pytest.mark.asyncio
async def test_complete_share_sends_two_separate_messages_without_extra_button():
    """Verify complete_share sends Message 1 (Confirmation + Invite Link) and Message 2 (Progress Report) separately without 'read another portion' button."""
    from khatmsaz.bot.handlers.member_commitment import complete_share

    oid = uuid.uuid4()
    uid = uuid.uuid4()
    pid = uuid.uuid4()
    kid = uuid.uuid4()
    bid = uuid.uuid4()

    callback = MagicMock()
    callback.data = f"share_done:{oid}"
    callback.from_user.id = 123456
    callback.message.bot.khatmsaz_platform = Platform.TELEGRAM
    callback.message.bot.khatmsaz_role = "MEMBER"
    callback.message.bot.khatmsaz_instance_id = bid
    callback.message.answer = AsyncMock()

    user = MagicMock(id=uid)
    part = MagicMock(id=pid, user_id=uid, khatm_id=kid)
    khatm = MagicMock(spec=Khatm)
    khatm.id = kid
    khatm.creator_user_id = uid
    khatm.title = "آزمایشی"
    khatm.niyyat = "سلامتی و فرج امام عصر علیه السلام"
    khatm.template_type = KhatmTemplateType.SALAWAT
    khatm.repetition_target = 14
    khatm.content_category_id = None

    occurrence = MagicMock()
    occurrence.id = oid
    occurrence.participation_id = pid
    occurrence.bot_instance_id = bid
    occurrence.amount = 1
    occurrence.unit = "COUNT"
    occurrence.content_spec = {"family": "salawat", "language": "fa"}

    mock_session = AsyncMock(spec=AsyncSession)
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_session
    mock_cm.__aexit__.return_value = False

    with (
        patch("khatmsaz.bot.handlers.member_commitment.session_scope", return_value=mock_cm),
        patch("khatmsaz.bot.handlers.member_commitment.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=user)),
        patch("khatmsaz.modules.share_occurrence.repository.get", new=AsyncMock(return_value=occurrence)),
        patch("khatmsaz.bot.handlers.member_commitment.participation_service.get_by_id", new=AsyncMock(return_value=part)),
        patch("khatmsaz.bot.handlers.member_commitment.khatm_service.get_khatm_for_update", new=AsyncMock(return_value=khatm)),
        patch("khatmsaz.modules.share_occurrence.service.complete", new=AsyncMock(return_value=(occurrence, True))),
        patch("khatmsaz.bot.occurrence_adapter.cleanup", new=AsyncMock()),
        patch("khatmsaz.bot.handlers.member_commitment.safe_answer_callback", new=AsyncMock()),
        patch("khatmsaz.bot.handlers.portions._invite_friends_line", new=AsyncMock(return_value="\n\nبا ارسال این لینک برای دوستانتون، اون‌ها رو هم به مشارکت در همین ثواب دعوت کنید:\nhttps://t.me/test_bot?start=join_tok")),
        patch("khatmsaz.bot.member_copy.build_motivational_progress_snippet", new=AsyncMock(return_value="📊 <b>روند پیشرفت کلی این ختم:</b>\n▫️ قرائت تا دیروز: ۰ صلوات\n▫️ قرائت‌های امروز: ۱ صلوات\n▫️ مجموع قرائت‌شده: <b>۱ صلوات</b> از <b>۱۴ صلوات</b> (پیشرفت: <b>۷.۱٪</b>)")),
    ):
        await complete_share(callback)

    assert callback.message.answer.call_count == 2
    first_call_args, first_call_kwargs = callback.message.answer.call_args_list[0]
    second_call_args, second_call_kwargs = callback.message.answer.call_args_list[1]

    msg1_text = first_call_args[0]
    msg2_text = second_call_args[0]

    # Message 1: Confirmation + Invite link, NO progress snippet, NO button
    assert "با سلام 🌱" in msg1_text
    assert "اعلام شما در سیستم ثبت شد" in msg1_text
    assert "https://t.me/test_bot?start=join_tok" in msg1_text
    assert "روند پیشرفت کلی این ختم" not in msg1_text
    assert first_call_kwargs.get("reply_markup") is None

    # Message 2: Progress report snippet, NO button
    assert "📊 <b>روند پیشرفت کلی این ختم:</b>" in msg2_text
    assert "مجموع قرائت‌شده" in msg2_text
    assert second_call_kwargs.get("reply_markup") is None


@pytest.mark.asyncio
async def test_deliver_member_daily_digests_before_14_returns_zero():
    """Delivery before 14:00 local Tehran time must do nothing."""
    session = AsyncMock(spec=AsyncSession)
    notify = AsyncMock()
    # 09:30 UTC is 13:00 Tehran -> before 14:00
    now_utc = datetime(2026, 10, 11, 9, 30, tzinfo=timezone.utc)

    delivered = await deliver_member_daily_digests(
        session, notify, now=now_utc, tz_name="Asia/Tehran"
    )
    assert delivered == 0
    notify.assert_not_called()


@pytest.mark.asyncio
async def test_deliver_member_daily_digests_at_14_and_idempotency():
    """Delivery at 14:00 local delivers to members and is idempotent for that day."""
    session = AsyncMock(spec=AsyncSession)
    notify = AsyncMock()

    uid = uuid.uuid4()
    bot_inst_id = uuid.uuid4()

    # Mock user query result
    users_result = MagicMock()
    users_result.scalars.return_value = [uid]

    # Mock user entity
    user = MagicMock(spec=User)
    user.id = uid
    user.status = UserStatus.ACTIVE
    user.deleted_at = None

    # Mock settings
    settings = MagicMock(spec=UserSettings)
    settings.member_daily_digest_enabled = True
    settings.last_member_daily_digest_date = None

    # Mock active participations
    khatm = MagicMock(spec=Khatm)
    khatm.id = uuid.uuid4()
    khatm.title = "ختم قرآن کریم"
    khatm.status = KhatmStatus.ACTIVE

    part = MagicMock(spec=Participation)
    part.id = uuid.uuid4()
    part.user_id = uid
    part.khatm_id = khatm.id
    part.status = ParticipationStatus.ACTIVE
    part.joined_via_bot_instance_id = bot_inst_id

    parts_result = MagicMock()
    parts_result.all.return_value = [(part, khatm)]

    session.execute.side_effect = [users_result, parts_result]

    identity = MagicMock()
    identity.platform = Platform.TELEGRAM
    identity.subject = "12345678"

    # 10:35 UTC is 14:05 Tehran
    now_utc = datetime(2026, 10, 11, 10, 35, tzinfo=timezone.utc)

    with (
        patch("khatmsaz.modules.settings.service.get_or_create",
              new=AsyncMock(return_value=settings)),
        patch("khatmsaz.modules.identity.service.find_by_id",
              new=AsyncMock(return_value=user)),
        patch("khatmsaz.modules.identity.service.list_identities_for_user",
              new=AsyncMock(return_value=[identity])),
        patch("khatmsaz.modules.reporting.member_daily_digest.build_member_daily_digest_message",
              new=AsyncMock(return_value=("خلاصه پیشرفت روزانه", MagicMock()))),
        patch("khatmsaz.modules.reporting.member_daily_digest.send_with_keyboard",
              new=AsyncMock(return_value=True)) as mock_send,
    ):
        delivered = await deliver_member_daily_digests(
            session, notify, now=now_utc, tz_name="Asia/Tehran"
        )
        assert delivered == 1
        assert settings.last_member_daily_digest_date == "2026-10-11"
        assert mock_send.call_count == 1
        args, kwargs = mock_send.call_args
        assert kwargs.get("bot_instance_id") == bot_inst_id

        # Second run on the same day must skip (idempotent)
        session.execute.side_effect = [users_result, parts_result]
        delivered_again = await deliver_member_daily_digests(
            session, notify, now=now_utc, tz_name="Asia/Tehran"
        )
        assert delivered_again == 0
