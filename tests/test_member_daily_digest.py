"""Tests for member daily 14:00 progress digest, motivational progress banner, and Bale Markdown formatting."""

from datetime import datetime, timezone
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.bale.client import BaleAiohttpSession
from khatmsaz.bot.bale.formatting import html_to_bale_markdown
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
async def test_build_member_daily_digest_message_is_simple_without_buttons():
    """Verify message formatting without action buttons (owner requirement)."""
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
        # Owner requirement: simple message without buttons
        assert keyboard is None


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

        full_msg = completion_text(
            khatm, "salawat", "۱۰۰ صلوات", progress_snippet=snippet, lang="fa"
        )
        assert "✅ ۱۰۰ صلوات انجام شد." in full_msg
        assert "روند پیشرفت کلی این ختم" in full_msg
        assert "خداوند از شما قبول فرماید. با تشکر." in full_msg


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
    """Delivery at 14:00 local delivers to members without buttons and is idempotent."""
    session = AsyncMock(spec=AsyncSession)
    notify = AsyncMock()

    uid = uuid.uuid4()
    bot_inst_id = uuid.uuid4()

    users_result = MagicMock()
    users_result.scalars.return_value = [uid]

    user = MagicMock(spec=User)
    user.id = uid
    user.status = UserStatus.ACTIVE
    user.deleted_at = None

    settings = MagicMock(spec=UserSettings)
    settings.member_daily_digest_enabled = True
    settings.last_member_daily_digest_date = None

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

    now_utc = datetime(2026, 10, 11, 10, 35, tzinfo=timezone.utc)

    with (
        patch("khatmsaz.modules.settings.service.get_or_create",
              new=AsyncMock(return_value=settings)),
        patch("khatmsaz.modules.identity.service.find_by_id",
              new=AsyncMock(return_value=user)),
        patch("khatmsaz.modules.identity.service.list_identities_for_user",
              new=AsyncMock(return_value=[identity])),
        patch("khatmsaz.modules.reporting.member_daily_digest.build_member_daily_digest_message",
              new=AsyncMock(return_value=("خلاصه پیشرفت روزانه", None))),
    ):
        delivered = await deliver_member_daily_digests(
            session, notify, now=now_utc, tz_name="Asia/Tehran"
        )
        assert delivered == 1
        assert settings.last_member_daily_digest_date == "2026-10-11"
        assert notify.call_count == 1
        args, kwargs = notify.call_args
        assert kwargs.get("bot_instance_id") == bot_inst_id

        # Second run on the same day must skip (idempotent)
        session.execute.side_effect = [users_result, parts_result]
        delivered_again = await deliver_member_daily_digests(
            session, notify, now=now_utc, tz_name="Asia/Tehran"
        )
        assert delivered_again == 0


def test_html_to_bale_markdown_conversion():
    """Verify HTML tags (<b>, <i>, <code>, <a>) are converted to clean Bale Markdown."""
    sample_html = (
        "<b>گزارش روزانه ختم‌های شما (ساعت ۱۲:۰۰ ظهر)</b>\n"
        "📅 یکشنبه ۱۹ مهر ۱۴۰۵\n\n"
        "🌟 <b>ختم «ختم زیارت آل یاسین»</b>\n"
        "▫️ مجموع قرائت‌شده: <b>۰ مرتبه</b>\n"
        "🌱 <i>طاعت و خدمت خالصانه‌تان قبول درگاه حق و التماس دعا 🤍</i>\n"
        "کد رهگیری: <code>12345</code>\n"
        '<a href="https://example.com">مشاهده جزئیات</a>'
    )
    converted = html_to_bale_markdown(sample_html)

    # Must NOT have raw HTML tags
    assert "<b>" not in converted
    assert "</b>" not in converted
    assert "<i>" not in converted
    assert "</i>" not in converted
    assert "<code>" not in converted
    assert "</code>" not in converted
    assert "<a href=" not in converted

    # Must contain Markdown syntax
    assert "*گزارش روزانه ختم‌های شما (ساعت ۱۲:۰۰ ظهر)*" in converted
    assert "*ختم «ختم زیارت آل یاسین»*" in converted
    assert "*۰ مرتبه*" in converted
    assert "_طاعت و خدمت خالصانه‌تان قبول درگاه حق و التماس دعا 🤍_" in converted
    assert "`12345`" in converted
    assert "[مشاهده جزئیات](https://example.com)" in converted


@pytest.mark.asyncio
async def test_bale_aiohttp_session_transforms_payload():
    """Verify BaleAiohttpSession transforms method.text and method.caption before sending."""
    from aiogram.methods import SendMessage, SendPhoto
    from aiogram import Bot

    from aiogram.client.default import DefaultBotProperties

    session = BaleAiohttpSession()
    bot = MagicMock(spec=Bot)
    bot.token = "123:abc"
    bot.default = DefaultBotProperties(parse_mode=None)

    send_msg = SendMessage(
        chat_id=123,
        text="<b>سلام</b> و <i>احترام</i>",
        parse_mode="HTML",
    )

    with patch.object(BaleAiohttpSession, "create_session", new=AsyncMock()) as mock_create:
        mock_http = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(
            return_value='{"ok": true, "result": {"message_id": 1, "date": 1600000000, "chat": {"id": 123, "type": "private"}}}'
        )
        mock_http.post.return_value.__aenter__.return_value = mock_resp
        mock_create.return_value = mock_http

        await session.make_request(bot, send_msg)

        # send_msg.text must be transformed to Bale Markdown
        assert send_msg.text == "*سلام* و _احترام_"
        # parse_mode must be cleared so Bale does not choke on HTML
        assert send_msg.parse_mode is None
