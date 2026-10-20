"""Unit and integration tests for MASTER-60:
Creator Broadcast Engagement, Delivery Receipts & Live Seen/Activity Tracking System.

Tests cover:
1. Creation of per-recipient KhatmBroadcastReceipt records upon broadcast delivery.
2. Verification that audience message content is pristine without extra buttons or text.
3. Marking user receipts as SEEN when user becomes active in bot (record_user_seen).
4. Generating real-time analytics summary (get_analytics) with counts and percentages.
5. Formatting warm plain Persian stats cards for text, audio, and media.
6. Creator notification on delivery with interactive button (notify_creator_broadcast_sent).
7. Bot callback handler cbroadcast:stats:{broadcast_id} displaying live stats.
8. Bot callback handler cbroadcast:refresh:{broadcast_id} refreshing stats in place.
9. Bot callback handler cbroadcast:recipients:{broadcast_id}:{page} rendering paginated recipient list.
10. ModerationMiddleware invoking record_user_seen on user activity.
11. Web Admin history tab rendering seen count and engagement badge.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse

from khatmsaz.bot.middlewares import ModerationMiddleware
from khatmsaz.bot.handlers.creator_broadcast import (
    _format_broadcast_stats_card,
    _build_stats_keyboard,
    view_broadcast_stats,
    refresh_broadcast_stats,
    view_broadcast_recipients,
)
from khatmsaz.modules.broadcast.models import (
    BroadcastReceiptStatus,
    BroadcastStatus,
    KhatmBroadcast,
    KhatmBroadcastReceipt,
)
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.broadcast import repository as broadcast_repo
from khatmsaz.modules.broadcast.delivery import deliver_broadcast
from khatmsaz.web.app import broadcasts_page


@pytest.fixture
def sample_broadcast():
    b_id = uuid.uuid4()
    c_id = uuid.uuid4()
    k_id = uuid.uuid4()
    return KhatmBroadcast(
        id=b_id,
        khatm_id=k_id,
        creator_user_id=c_id,
        body="سلام و درود بر اعضای محترم ختم قرآن کریم",
        target_scope="KHATM",
        channel="TELEGRAM",
        audience_count=50,
        cost_toman=0,
        status=BroadcastStatus.APPROVED,
        media_type=None,
        media_file_id_telegram=None,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_broadcast_delivery_creates_receipts_and_keeps_message_clean(sample_broadcast, monkeypatch):
    """MASTER-60: Verify receipts are created and audience message remains pristine without extra buttons."""
    session = AsyncMock()
    user_1 = uuid.uuid4()
    user_2 = uuid.uuid4()

    destinations = [
        broadcast_service.DigitalDestination(subject="111", bot_instance_id=None, user_id=user_1),
        broadcast_service.DigitalDestination(subject="222", bot_instance_id=None, user_id=user_2),
    ]
    monkeypatch.setattr(broadcast_service, "audience_destinations", AsyncMock(return_value=destinations))
    monkeypatch.setattr(broadcast_service, "sender_display_name", AsyncMock(return_value="سازنده ختم"))
    monkeypatch.setattr(broadcast_service, "mark_sent", AsyncMock())

    created_receipts_holder = []

    async def fake_create_receipts(sess, receipts):
        created_receipts_holder.extend(receipts)
        return len(receipts)

    monkeypatch.setattr(broadcast_repo, "create_receipts", fake_create_receipts)

    delivered_calls = []

    async def fake_notify(channel, subject, text, *, bot_instance_id=None):
        delivered_calls.append({"channel": channel, "subject": subject, "text": text})

    monkeypatch.setattr("khatmsaz.modules.broadcast.delivery.get_notify_fn", lambda: fake_notify)

    mock_notify_creator = AsyncMock(return_value=True)
    monkeypatch.setattr(broadcast_service, "notify_creator_broadcast_sent", mock_notify_creator)

    count = await deliver_broadcast(session, sample_broadcast)

    assert count == 2
    # Verify delivered message content is clean (no buttons or extra appended text)
    assert len(delivered_calls) == 2
    for call in delivered_calls:
        assert "سلام و درود بر اعضای محترم" in call["text"]
        # Must not contain any button prompt or intrusive ack text
        assert "دکمه" not in call["text"]
        assert "تأیید خواندن" not in call["text"]

    # Verify receipts created
    assert len(created_receipts_holder) == 2
    assert created_receipts_holder[0]["recipient_user_id"] == user_1
    assert created_receipts_holder[0]["status"] == BroadcastReceiptStatus.DELIVERED.value
    assert created_receipts_holder[1]["recipient_user_id"] == user_2

    # Verify creator notification was fired
    assert mock_notify_creator.called
    assert mock_notify_creator.call_args[0][1] == sample_broadcast
    assert mock_notify_creator.call_args[0][2] == 2


@pytest.mark.asyncio
async def test_record_user_seen_updates_receipts(monkeypatch):
    """MASTER-60: Verify user activity updates unread receipts to SEEN status."""
    session = AsyncMock()
    mock_execute = AsyncMock()
    mock_res = MagicMock()
    mock_res.rowcount = 3
    mock_execute.return_value = mock_res
    session.execute = mock_execute
    session.flush = AsyncMock()

    user_id = uuid.uuid4()
    count = await broadcast_service.record_user_seen(session, user_id, source="BOT_ACTIVITY")

    assert count == 3
    assert session.execute.called
    assert session.flush.called


@pytest.mark.asyncio
async def test_get_analytics_summary(sample_broadcast, monkeypatch):
    """MASTER-60: Test aggregating seen/unseen percentages and media formatting."""
    session = AsyncMock()
    monkeypatch.setattr(broadcast_repo, "get_by_id", AsyncMock(return_value=sample_broadcast))
    monkeypatch.setattr(
        broadcast_repo,
        "get_broadcast_stats",
        AsyncMock(return_value={
            "total": 100,
            "seen": 65,
            "unseen": 35,
            "seen_percentage": 65.0,
        }),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.khatm.service.get_khatm",
        AsyncMock(return_value=SimpleNamespace(title="ختم سوره واقعه")),
    )

    analytics = await broadcast_service.get_analytics(session, sample_broadcast.id)

    assert analytics is not None
    assert analytics["khatm_title"] == "ختم سوره واقعه"
    assert analytics["total"] == 100
    assert analytics["seen"] == 65
    assert analytics["unseen"] == 35
    assert analytics["seen_percentage"] == 65.0

    # Test format stats card text
    card = _format_broadcast_stats_card(analytics)
    assert "📊 گزارش لحظه‌ای بازخورد و سین پیام" in card
    assert "ختم سوره واقعه" in card
    assert "کل مخاطبان: 100 نفر" in card
    assert "مشاهده شده (سین خورده): 65 نفر (65.0٪)" in card
    assert "در انتظار مشاهده: 35 نفر (35.0٪)" in card


def test_format_broadcast_stats_card_audio_and_media_copy():
    """MASTER-60: Verify media-specific note in Persian copy for voice and image broadcasts."""
    audio_stats = {
        "khatm_title": "ختم یاسین",
        "media_type": "voice",
        "total": 50,
        "delivered": 50,
        "seen": 30,
        "unseen": 20,
        "seen_percentage": 60.0,
        "sent_at": datetime.now(timezone.utc),
    }
    card_audio = _format_broadcast_stats_card(audio_stats)
    assert "پیام صوتی (ویس)" in card_audio
    assert "🎧 وضعیت شنیدن صوت: 30 نفر فایل صوتی را دریافت و گوش داده‌اند." in card_audio

    photo_stats = {
        "khatm_title": "ختم صلوات",
        "media_type": "photo",
        "total": 80,
        "delivered": 80,
        "seen": 50,
        "unseen": 30,
        "seen_percentage": 62.5,
        "sent_at": datetime.now(timezone.utc),
    }
    card_photo = _format_broadcast_stats_card(photo_stats)
    assert "تصویر / عکس" in card_photo
    assert "🖼 وضعیت رسانه: 50 نفر رسانه را دریافت و مشاهده نموده‌اند." in card_photo


@pytest.mark.asyncio
async def test_notify_creator_broadcast_sent(sample_broadcast, monkeypatch):
    """MASTER-60: Test sending notification with interactive stats button to creator."""
    session = AsyncMock()
    mock_identity = SimpleNamespace(platform=SimpleNamespace(value="TELEGRAM"), subject="123456")
    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.list_identities_for_user",
        AsyncMock(return_value=[mock_identity]),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.khatm.service.get_khatm",
        AsyncMock(return_value=SimpleNamespace(title="ختم سوره نصر")),
    )
    mock_send_kb = AsyncMock(return_value=True)
    monkeypatch.setattr("khatmsaz.bot.notify_adapter.send_with_keyboard", mock_send_kb)

    sent = await broadcast_service.notify_creator_broadcast_sent(session, sample_broadcast, dest_count=50)

    assert sent is True
    assert mock_send_kb.called
    args = mock_send_kb.call_args[0]
    kwargs = mock_send_kb.call_args[1]
    platform = args[0]
    subject = args[1]
    text = args[2]
    markup = kwargs.get("reply_markup") or (args[3] if len(args) > 3 else None)
    assert platform == "TELEGRAM"
    assert subject == "123456"
    assert "پیام گروهی شما با موفقیت برای اعضا ارسال شد" in text
    assert "ختم سوره نصر" in text
    assert "50 نفر" in text
    # Verify button
    buttons = markup.inline_keyboard[0]
    assert buttons[0].text == "📊 مشاهده آمار بازخورد و سین"
    assert buttons[0].callback_data == f"cbroadcast:stats:{sample_broadcast.id}"


@pytest.mark.asyncio
async def test_view_broadcast_stats_callback_handler(sample_broadcast, monkeypatch):
    """MASTER-60: Test cbroadcast:stats callback handler renders report card."""
    callback = AsyncMock()
    callback.data = f"cbroadcast:stats:{sample_broadcast.id}"
    callback.message = AsyncMock()
    callback.message.edit_text = AsyncMock()

    stats_dict = {
        "khatm_title": "ختم صلوات",
        "media_type": "text",
        "total": 40,
        "delivered": 40,
        "seen": 25,
        "unseen": 15,
        "seen_percentage": 62.5,
        "sent_at": datetime.now(timezone.utc),
        "khatm_id": sample_broadcast.khatm_id,
    }
    monkeypatch.setattr(broadcast_service, "get_analytics", AsyncMock(return_value=stats_dict))

    await view_broadcast_stats(callback)

    assert callback.message.edit_text.called
    rendered_text = callback.message.edit_text.call_args[0][0]
    assert "📊 گزارش لحظه‌ای بازخورد و سین پیام" in rendered_text
    assert "ختم صلوات" in rendered_text
    assert "40 نفر" in rendered_text


@pytest.mark.asyncio
async def test_refresh_broadcast_stats_callback_handler(sample_broadcast, monkeypatch):
    """MASTER-60: Test cbroadcast:refresh callback handler updates text in place and toasts alert."""
    callback = AsyncMock()
    callback.data = f"cbroadcast:refresh:{sample_broadcast.id}"
    callback.message = AsyncMock()
    callback.message.edit_text = AsyncMock()

    stats_dict = {
        "khatm_title": "ختم حدیث کساء",
        "media_type": "text",
        "total": 70,
        "delivered": 70,
        "seen": 50,
        "unseen": 20,
        "seen_percentage": 71.4,
        "sent_at": datetime.now(timezone.utc),
        "khatm_id": sample_broadcast.khatm_id,
    }
    monkeypatch.setattr(broadcast_service, "get_analytics", AsyncMock(return_value=stats_dict))

    mock_answer = AsyncMock()
    monkeypatch.setattr("khatmsaz.bot.handlers.creator_broadcast.safe_answer_callback", mock_answer)

    await refresh_broadcast_stats(callback)

    assert callback.message.edit_text.called
    assert mock_answer.called
    assert "آمار با موفقیت بروز شد 🔄" in mock_answer.call_args[0][1]


@pytest.mark.asyncio
async def test_view_broadcast_recipients_pagination(sample_broadcast, monkeypatch):
    """MASTER-60: Test cbroadcast:recipients callback handler renders paginated list with seen indicators."""
    callback = AsyncMock()
    callback.data = f"cbroadcast:recipients:{sample_broadcast.id}:0"
    callback.message = AsyncMock()
    callback.message.edit_text = AsyncMock()

    recipients_data = [
        {"name": "علی رضایی", "seen": True, "seen_at": datetime(2026, 10, 20, 14, 5), "delivered_at": datetime(2026, 10, 20, 14, 0), "source": "BOT_ACTIVITY"},
        {"name": "زهرا حسینی", "seen": False, "seen_at": None, "delivered_at": datetime(2026, 10, 20, 14, 0), "source": None},
    ]
    monkeypatch.setattr(
        broadcast_service,
        "list_recipients_page",
        AsyncMock(return_value=(recipients_data, 2)),
    )

    await view_broadcast_recipients(callback)

    assert callback.message.edit_text.called
    rendered_text = callback.message.edit_text.call_args[0][0]
    assert "👥 وضعیت مشاهده پیام توسط مخاطبان" in rendered_text
    assert "✅ علی رضایی — دیده شد (14:05)" in rendered_text
    assert "⏳ زهرا حسینی — در انتظار مشاهده" in rendered_text


@pytest.mark.asyncio
async def test_moderation_middleware_records_seen(monkeypatch):
    """MASTER-60: Verify ModerationMiddleware triggers record_user_seen on user message/callback."""
    middleware = ModerationMiddleware()
    event = MagicMock()
    event.message = None
    event.chat = MagicMock()
    event.chat.id = 998877

    data = {"bot": MagicMock()}
    handler = AsyncMock(return_value="handled")

    mock_user = SimpleNamespace(id=uuid.uuid4(), is_blocked=False, last_activity_at=None)
    monkeypatch.setattr("khatmsaz.modules.identity.service.find_by_platform", AsyncMock(return_value=mock_user))
    monkeypatch.setattr("khatmsaz.modules.identity.service.is_blocked", AsyncMock(return_value=False))

    mock_record_seen = AsyncMock(return_value=1)
    monkeypatch.setattr(broadcast_service, "record_user_seen", mock_record_seen)

    res = await middleware(handler, event, data)

    assert res == "handled"
    assert mock_record_seen.called
    assert mock_record_seen.call_args[0][1] == mock_user.id


@pytest.mark.asyncio
async def test_web_broadcasts_history_renders_seen_badge(sample_broadcast, monkeypatch):
    """MASTER-60: Verify /broadcasts?tab=history renders seen metrics and eye badge."""
    mock_admin = SimpleNamespace(
        id=uuid.uuid4(),
        display_name="مدیر ناظر",
        is_super_admin=True,
        _admin_permissions={"MODERATION_MANAGE"},
    )
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))

    mock_session = AsyncMock()
    # Mock KPIs
    mock_session.scalar = AsyncMock(side_effect=[0, 1, 50])

    # Sent broadcast in history
    sample_broadcast.status = BroadcastStatus.SENT
    sample_broadcast.sent_at = datetime.now(timezone.utc)

    mock_exec = MagicMock()
    mock_exec.scalars.return_value = [sample_broadcast]
    mock_session.execute = AsyncMock(return_value=mock_exec)

    monkeypatch.setattr(
        broadcast_service.repository,
        "get_broadcast_stats",
        AsyncMock(return_value={"total": 50, "seen": 35, "unseen": 15, "seen_percentage": 70.0}),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.khatm.service.get_khatm",
        AsyncMock(return_value=SimpleNamespace(title="ختم سوره واقعه")),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.find_by_id",
        AsyncMock(return_value=SimpleNamespace(display_name="سازنده واقعه")),
    )

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = Request({
        "type": "http",
        "method": "GET",
        "path": "/broadcasts",
        "query_string": b"tab=history",
        "headers": [],
    })

    resp = await broadcasts_page(req, tab="history")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "تاریخچه و آرشیو ارسالی‌ها" in html
    assert "👁 35 (70.0٪)" in html
