"""Unit and integration tests for MASTER-54: Broadcasts, Creator Messages & Outbound Campaigns Hub.

Tests cover:
- Unauthenticated access redirect to /login
- Authenticated view of /broadcasts across all 4 tabs (pending, history, servant_ad, tariffs)
- Verification of 4 messaging KPI cards (pending, sent, total audience reached, basic audience)
- Legacy /servant-ad seamless 303 redirect to /broadcasts?tab=servant_ad
- Approve broadcast decision action
- Reject broadcast decision action with custom admin note
- Servant ad save action with direct multipart file upload
- Broadcast tariffs update action (POST /broadcasts/tariffs)
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi import UploadFile

from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.web.app import (
    broadcasts_page,
    decide_broadcast,
    servant_ad_page,
    servant_ad_save,
    update_broadcast_tariffs,
)


@pytest.fixture
def mock_admin():
    return SimpleNamespace(
        id=uuid.uuid4(),
        display_name="مدیر نظارت و ممیزی",
        is_super_admin=True,
        _admin_permissions={"MODERATION_MANAGE", "FINANCE_MANAGE"},
    )


@pytest.fixture
def sample_broadcast():
    b_id = uuid.uuid4()
    c_id = uuid.uuid4()
    k_id = uuid.uuid4()
    return SimpleNamespace(
        id=b_id,
        khatm_id=k_id,
        creator_user_id=c_id,
        body="پیام اطلاع‌رسانی آزمایشی به اعضای محترم ختم قرآن",
        target_scope="KHATM",
        target_province=None,
        target_gender=None,
        channel="TELEGRAM",
        audience_count=250,
        cost_toman=37500,
        media_type="photo",
        media_file_id_telegram="AgAC_test_file_id",
        media_file_id_bale=None,
        paid_at=datetime.now(timezone.utc),
        invoice_id=uuid.uuid4(),
        status=BroadcastStatus.PENDING,
        admin_note=None,
        reviewed_at=None,
        sent_at=None,
        created_at=datetime.now(timezone.utc),
    )


def _make_request(path: str = "/broadcasts", query_string: bytes = b"", query_params: dict | None = None) -> Request:
    req = Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": query_string,
        }
    )
    if query_params:
        req._query_params = query_params
    return req


# -----------------------------------------------------------------------------
# 1. Access Control Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_broadcasts_page_unauthenticated_redirect(monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(None, None)))
    req = _make_request("/broadcasts")
    resp = await broadcasts_page(req)
    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


# -----------------------------------------------------------------------------
# 2. Authenticated Hub Tabs & 4 KPIs Rendering
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_broadcasts_page_authenticated_pending_tab(mock_admin, sample_broadcast, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.audience_size", AsyncMock(return_value=1250))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.get_ad", AsyncMock(return_value={
        "text": "تست تبلیغ", "media_type": "", "media_telegram": "", "media_bale": "", "media_local": "", "enabled": True,
    }))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_int", AsyncMock(return_value=150000))
    monkeypatch.setattr("khatmsaz.modules.identity.service.find_by_id", AsyncMock(return_value=SimpleNamespace(id=sample_broadcast.creator_user_id, display_name="سازنده نمونه")))

    mock_session = AsyncMock()
    mock_session.scalar = AsyncMock(side_effect=[1, 5, 2500])  # pending_count, sent_count, total_audience
    mock_execute = MagicMock()
    mock_execute.scalars.return_value = [sample_broadcast]
    mock_session.execute = AsyncMock(return_value=mock_execute)
    mock_session.get = AsyncMock(return_value=SimpleNamespace(id=sample_broadcast.khatm_id, title="ختم صلوات فرج"))

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/broadcasts", query_string=b"tab=pending")

    resp = await broadcasts_page(req, tab="pending")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    # Header and KPIs
    assert "پیام‌های گروهی و کمپین‌های سراسری" in html
    assert "در انتظار بررسی" in html
    assert "پیام‌های ارسال‌شده" in html
    assert "مخاطبان پوشش‌یافته" in html
    assert "مخاطبان پلن پایه" in html
    assert "1,250" in html

    # Pending tab content
    assert "ختم صلوات فرج" in html
    assert "سازنده نمونه" in html
    assert "پیام اطلاع‌رسانی آزمایشی" in html
    assert "تأیید و ارسال" in html
    assert "رد پیام" in html


@pytest.mark.asyncio
async def test_broadcasts_page_history_tab(mock_admin, sample_broadcast, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.audience_size", AsyncMock(return_value=500))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.get_ad", AsyncMock(return_value={
        "text": "", "media_type": "", "media_telegram": "", "media_bale": "", "media_local": "", "enabled": False,
    }))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_int", AsyncMock(return_value=0))
    monkeypatch.setattr("khatmsaz.modules.identity.service.find_by_id", AsyncMock(return_value=SimpleNamespace(id=sample_broadcast.creator_user_id, display_name="سازنده یک")))

    sent_broadcast = SimpleNamespace(
        id=uuid.uuid4(),
        khatm_id=sample_broadcast.khatm_id,
        creator_user_id=sample_broadcast.creator_user_id,
        body="پیام ارسال‌شده در تاریخچه",
        target_scope="KHATM",
        target_province=None,
        target_gender=None,
        channel="BALE",
        audience_count=100,
        cost_toman=15000,
        media_type=None,
        media_file_id_telegram=None,
        media_file_id_bale=None,
        paid_at=datetime.now(timezone.utc),
        invoice_id=uuid.uuid4(),
        status=BroadcastStatus.SENT,
        admin_note=None,
        reviewed_at=datetime.now(timezone.utc),
        sent_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    mock_session = AsyncMock()
    mock_session.scalar = AsyncMock(side_effect=[0, 10, 5000])
    mock_pending_exec = MagicMock()
    mock_pending_exec.scalars.return_value = []
    mock_history_exec = MagicMock()
    mock_history_exec.scalars.return_value = [sent_broadcast]
    mock_session.execute = AsyncMock(side_effect=[mock_pending_exec, mock_history_exec])
    mock_session.get = AsyncMock(return_value=SimpleNamespace(id=sent_broadcast.khatm_id, title="ختم سوره یاسین"))

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/broadcasts", query_string=b"tab=history")

    resp = await broadcasts_page(req, tab="history")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "تاریخچه و آرشیو ارسالی‌ها" in html
    assert "ختم سوره یاسین" in html
    assert "پیام ارسال‌شده در تاریخچه" in html
    assert "ارسال‌شده" in html


@pytest.mark.asyncio
async def test_broadcasts_page_servant_ad_tab(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.audience_size", AsyncMock(return_value=840))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.get_ad", AsyncMock(return_value={
        "text": "پیام تبلیغاتی خدمتگزاران اهل بیت",
        "media_type": "photo",
        "media_telegram": "AgAC_tg",
        "media_bale": "bale_id",
        "media_local": "/static/uploads/campaigns/test.jpg",
        "enabled": True,
    }))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_int", AsyncMock(return_value=150000))

    mock_session = AsyncMock()
    mock_session.scalar = AsyncMock(side_effect=[0, 0, 0])
    mock_exec = MagicMock()
    mock_exec.scalars.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_exec)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/broadcasts", query_string=b"tab=servant_ad")

    resp = await broadcasts_page(req, tab="servant_ad")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "کمپین تبلیغ خدمتگزاران" in html
    assert "پیام تبلیغاتی خدمتگزاران اهل بیت" in html
    assert "840" in html
    assert "اجرای فوری کمپین" in html


@pytest.mark.asyncio
async def test_broadcasts_page_tariffs_tab(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.audience_size", AsyncMock(return_value=100))
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.get_ad", AsyncMock(return_value={
        "text": "", "media_type": "", "media_telegram": "", "media_bale": "", "media_local": "", "enabled": False,
    }))
    # Values for telegram, bale, sms free_count, price, package_size (9 calls)
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_int", AsyncMock(side_effect=[
        0, 150000, 1000,  # telegram
        0, 120000, 1000,  # bale
        0, 80, 1,         # sms
    ]))

    mock_session = AsyncMock()
    mock_session.scalar = AsyncMock(side_effect=[0, 0, 0])
    mock_exec = MagicMock()
    mock_exec.scalars.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_exec)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/broadcasts", query_string=b"tab=tariffs")

    resp = await broadcasts_page(req, tab="tariffs")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "تعرفه‌ها و بسته‌های ارسال" in html
    assert "تعرفه تلگرام (Telegram)" in html
    assert "تعرفه بله (Bale)" in html
    assert "تعرفه پیامک (SMS)" in html


# -----------------------------------------------------------------------------
# 3. Legacy /servant-ad Seamless Redirect
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_servant_ad_page_redirect():
    req = _make_request("/servant-ad")
    resp = await servant_ad_page(req)
    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/broadcasts?tab=servant_ad"


# -----------------------------------------------------------------------------
# 4. Actions: Decide Broadcast (Approve & Reject with Note)
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_decide_broadcast_approve(mock_admin, sample_broadcast, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    approved_item = SimpleNamespace(
        id=sample_broadcast.id,
        khatm_id=sample_broadcast.khatm_id,
        creator_user_id=sample_broadcast.creator_user_id,
        cost_toman=0,
        paid_at=None,
        channel="TELEGRAM",
        body="متن تأییدشده",
        media_type=None,
        media_file_id_telegram=None,
        media_file_id_bale=None,
        status=BroadcastStatus.APPROVED,
    )
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.approve", AsyncMock(return_value=approved_item))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.audience_destinations", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.sender_display_name", AsyncMock(return_value="سازنده"))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.mark_sent", AsyncMock())
    monkeypatch.setattr("khatmsaz.modules.identity.service.find_by_id", AsyncMock(return_value=mock_admin))
    monkeypatch.setattr("khatmsaz.web.app._dispatch_broadcast_delivery", AsyncMock())
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request("/broadcasts/decide")
    resp = await decide_broadcast(
        request=req,
        broadcast_id=sample_broadcast.id,
        decision="approve",
        csrf="valid-csrf",
        admin_note="تأیید شد",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "saved=approved" in resp.headers["location"]
    assert mock_audit.called
    assert mock_audit.call_args[1]["action"] == "KHATM_BROADCAST_APPROVE"


@pytest.mark.asyncio
async def test_decide_broadcast_reject_with_admin_note(mock_admin, sample_broadcast, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    rejected_item = SimpleNamespace(
        id=sample_broadcast.id,
        khatm_id=sample_broadcast.khatm_id,
        creator_user_id=sample_broadcast.creator_user_id,
        cost_toman=10000,
        status=BroadcastStatus.REJECTED,
    )
    mock_reject = AsyncMock(return_value=rejected_item)
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.reject", mock_reject)
    monkeypatch.setattr("khatmsaz.modules.identity.service.find_by_id", AsyncMock(return_value=mock_admin))
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request("/broadcasts/decide")
    resp = await decide_broadcast(
        request=req,
        broadcast_id=sample_broadcast.id,
        decision="reject",
        csrf="valid-csrf",
        admin_note="متن حاوی لینک تبلیغاتی غیرمجاز بود",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "saved=rejected" in resp.headers["location"]
    assert mock_reject.call_args[0][2] == "متن حاوی لینک تبلیغاتی غیرمجاز بود"
    assert mock_audit.call_args[1]["action"] == "KHATM_BROADCAST_REJECT"
    assert mock_audit.call_args[1]["details"]["note"] == "متن حاوی لینک تبلیغاتی غیرمجاز بود"


# -----------------------------------------------------------------------------
# 5. Servant Ad Save with Multipart Upload & Tariffs
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_servant_ad_save_with_file_upload(mock_admin, monkeypatch, tmp_path):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    mock_set_ad = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.servant_ad.service.set_ad", mock_set_ad)
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    # Fake file upload
    file_bytes = b"fake-campaign-image"
    upload = UploadFile(filename="campaign_poster.jpg", file=BytesIO(file_bytes))

    req = _make_request("/servant-ad/save")
    resp = await servant_ad_save(
        request=req,
        csrf="valid-csrf",
        text="متن تستی کمپین",
        media_type="photo",
        media_telegram="",
        media_bale="",
        media_local="",
        enabled="on",
        file_media=upload,
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/broadcasts?tab=servant_ad&saved=1"
    assert mock_set_ad.called
    assert mock_set_ad.call_args[1]["enabled"] is True
    assert "campaign_poster.jpg" in mock_set_ad.call_args[1]["media_local"]
    assert mock_audit.call_args[1]["action"] == "SERVANT_AD_SAVE"


@pytest.mark.asyncio
async def test_update_broadcast_tariffs(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    mock_set_int = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.set_int", mock_set_int)
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request("/broadcasts/tariffs")
    resp = await update_broadcast_tariffs(
        request=req,
        csrf="valid-csrf",
        channel="TELEGRAM",
        price_toman=180000,
        package_size=1000,
        free_count=2,
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/broadcasts?tab=tariffs&saved=tariffs_saved"
    assert mock_set_int.called
    assert mock_audit.call_args[1]["action"] == "BROADCAST_TARIFFS_UPDATE"
    assert mock_audit.call_args[1]["details"]["price_toman"] == 180000
