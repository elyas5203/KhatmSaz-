"""Unit and integration tests for MASTER-55: Content and User Moderation Hub (/moderation).

Tests cover:
- Unauthenticated access redirect to /login
- Authenticated view of /moderation across all 5 active queues:
  1) laan (custom laan review with edit capability)
  2) covers (khatm cover image review)
  3) requests (khatm type proposal requests)
  4) tickets (support tickets with direct response)
  5) banners (advertising and devotional banners)
- Verification of 4 Moderation KPIs (total_pending, pending_content, open_tickets, pending_banners_requests)
- Actions:
  - decide_laan_moderation (approve with updated description / reject)
  - decide_cover_moderation (approve / reject with note)
  - decide_khatm_request_moderation (approve / reject with note)
  - reply_support_ticket (answer ticket by admin)
  - close_support_ticket (close ticket by admin)
  - moderation_decide_banner (approve / reject banner)
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from khatmsaz.modules.support_ticket.models import SupportTicketStatus
from khatmsaz.modules.advertising.models import AdvertisingBanner, BannerStatus
from khatmsaz.web.app import (
    moderation_center,
    decide_laan_moderation,
    decide_cover_moderation,
    decide_khatm_request_moderation,
    reply_support_ticket,
    close_support_ticket,
    moderation_decide_banner,
)


@pytest.fixture
def mock_admin():
    return SimpleNamespace(
        id=uuid.uuid4(),
        display_name="مدیر ناظر",
        is_super_admin=True,
        _admin_permissions={"MODERATION_MANAGE", "SUPPORT_USERS", "CONTENT_MANAGE"},
    )


def _make_request(path: str = "/moderation", query_string: bytes = b"", query_params: dict | None = None) -> Request:
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
async def test_moderation_unauthenticated_redirect(monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(None, None)))
    req = _make_request("/moderation")
    resp = await moderation_center(req)
    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


# -----------------------------------------------------------------------------
# 2. Authenticated Hub Tabs & 4 KPIs Rendering
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_moderation_page_laan_tab(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    creator_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=creator_id, display_name="کاربر سازنده")
    sample_laan_khatm = SimpleNamespace(
        id=uuid.uuid4(),
        title="ختم زیارت عاشورا با لعن اختصاصی",
        creator_user_id=creator_id,
        description="اللهم العن اول ظالم ظلم حق محمد و آل محمد",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_laan_khatms", AsyncMock(return_value=[sample_laan_khatm]))
    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_covers", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.support_ticket.service.list_admin_tickets", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.advertising.service.list_banners", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.manual_phone_verification.repository.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.creator_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_category.service.list_pending_requests", AsyncMock(return_value=[]))

    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.scalars.return_value = [mock_user]
    mock_session.execute = AsyncMock(return_value=mock_scalars)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/moderation", query_string=b"tab=laan")

    resp = await moderation_center(req, tab="laan")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "صف‌های جامع نظارت و تایید صلاحیت" in html
    assert "کل موارد در انتظار" in html
    assert "لعن‌ها و کاورها" in html
    assert "تیکت‌های باز" in html
    assert "بنرها و پیشنهادات" in html
    assert "ختم زیارت عاشورا با لعن اختصاصی" in html
    assert "اللهم العن اول ظالم" in html
    assert "کاربر سازنده" in html


@pytest.mark.asyncio
async def test_moderation_page_covers_tab(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    creator_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=creator_id, display_name="سازنده پوستر")
    sample_cover_khatm = SimpleNamespace(
        id=uuid.uuid4(),
        title="ختم صلوات با کاور اختصاصی",
        creator_user_id=creator_id,
        cover_ref="https://cdn.example.com/cover1.jpg",
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_laan_khatms", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_covers", AsyncMock(return_value=[sample_cover_khatm]))
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.support_ticket.service.list_admin_tickets", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.advertising.service.list_banners", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.manual_phone_verification.repository.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.creator_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_category.service.list_pending_requests", AsyncMock(return_value=[]))

    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.scalars.return_value = [mock_user]
    mock_session.execute = AsyncMock(return_value=mock_scalars)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/moderation", query_string=b"tab=covers")

    resp = await moderation_center(req, tab="covers")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "ختم صلوات با کاور اختصاصی" in html
    assert "https://cdn.example.com/cover1.jpg" in html
    assert "سازنده پوستر" in html


@pytest.mark.asyncio
async def test_moderation_page_requests_tab(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    requester_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=requester_id, display_name="پیشنهاد دهنده دعا")
    sample_request = SimpleNamespace(
        id=uuid.uuid4(),
        title="دعای جوشن صغیر",
        description="لطفاً این دعای شریف را به انواع ختم اضافه بفرمایید",
        requester_user_id=requester_id,
        created_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_laan_khatms", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_covers", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.list_pending", AsyncMock(return_value=[sample_request]))
    monkeypatch.setattr("khatmsaz.modules.support_ticket.service.list_admin_tickets", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.advertising.service.list_banners", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.manual_phone_verification.repository.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.creator_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_category.service.list_pending_requests", AsyncMock(return_value=[]))

    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.scalars.return_value = [mock_user]
    mock_session.execute = AsyncMock(return_value=mock_scalars)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/moderation", query_string=b"tab=requests")

    resp = await moderation_center(req, tab="requests")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "لطفاً این دعای شریف را به انواع ختم اضافه بفرمایید" in html
    assert "پیشنهاد دهنده دعا" in html


@pytest.mark.asyncio
async def test_moderation_page_tickets_tab(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    sender_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=sender_id, display_name="کاربر پشتیبانی")
    sample_ticket = SimpleNamespace(
        id=uuid.uuid4(),
        subject="مشکل در پرداخت آنلاین",
        body="مبلغ از حساب کسر شده ولی ختم فعال نشده است",
        sender_user_id=sender_id,
        status=SupportTicketStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        replied_at=None,
        reply_text=None,
    )

    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_laan_khatms", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_covers", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.support_ticket.service.list_admin_tickets", AsyncMock(return_value=[sample_ticket]))
    monkeypatch.setattr("khatmsaz.modules.advertising.service.list_banners", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.manual_phone_verification.repository.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.creator_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_category.service.list_pending_requests", AsyncMock(return_value=[]))

    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.scalars.return_value = [mock_user]
    mock_session.execute = AsyncMock(return_value=mock_scalars)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/moderation", query_string=b"tab=tickets")

    resp = await moderation_center(req, tab="tickets")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "مبلغ از حساب کسر شده" in html
    assert "کاربر پشتیبانی" in html


@pytest.mark.asyncio
async def test_moderation_page_banners_tab(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    creator_id = uuid.uuid4()
    mock_user = SimpleNamespace(id=creator_id, display_name="سفارش دهنده تبلیغ")
    sample_banner = SimpleNamespace(
        id=uuid.uuid4(),
        title="بنر معرفی ختم هفتگی آل یاسین",
        content_text="همه روزهای جمعه ساعت ۱۷ در جمع خادمان منتظر",
        creator_user_id=creator_id,
        khatm_id=None,
        status=BannerStatus.PENDING,
        cost_toman=15000,
        banner_type=SimpleNamespace(value="SYSTEM_CULTURAL"),
        placement=SimpleNamespace(value="ALL"),
        image_url=None,
        button_text=None,
        button_url=None,
        created_at=datetime.now(timezone.utc),
    )


    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_laan_khatms", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm.service.list_pending_covers", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.support_ticket.service.list_admin_tickets", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.advertising.service.list_banners", AsyncMock(return_value=[sample_banner]))
    monkeypatch.setattr("khatmsaz.modules.broadcast.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.manual_phone_verification.repository.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.creator_request.service.list_pending", AsyncMock(return_value=[]))
    monkeypatch.setattr("khatmsaz.modules.khatm_category.service.list_pending_requests", AsyncMock(return_value=[]))

    mock_session = AsyncMock()
    mock_scalars = MagicMock()
    mock_scalars.scalars.return_value = [mock_user]
    mock_session.execute = AsyncMock(return_value=mock_scalars)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/moderation", query_string=b"tab=banners")

    resp = await moderation_center(req, tab="banners")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "بنر معرفی ختم هفتگی آل یاسین" in html
    assert "سفارش دهنده تبلیغ" in html


# -----------------------------------------------------------------------------
# 3. Actions: La'n Review Decisions
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_decide_laan_approve(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    khatm_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    reviewed_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم عاشورا",
        creator_user_id=creator_id,
    )
    monkeypatch.setattr("khatmsaz.modules.khatm.service.review_laan_khatm", AsyncMock(return_value=reviewed_khatm))
    monkeypatch.setattr("khatmsaz.modules.invitation.service.get_or_create_for_khatm", AsyncMock(return_value="inv-tok-123"))
    monkeypatch.setattr("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[]))
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/laan/{khatm_id}/decide")
    resp = await decide_laan_moderation(
        request=req,
        khatm_id=khatm_id,
        decision="approve",
        updated_description="متن اصلاح شده لعن",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=laan&saved=laan_approved"
    assert mock_audit.called


@pytest.mark.asyncio
async def test_decide_laan_reject(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    khatm_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    reviewed_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم نامعتبر",
        creator_user_id=creator_id,
    )
    monkeypatch.setattr("khatmsaz.modules.khatm.service.review_laan_khatm", AsyncMock(return_value=reviewed_khatm))
    monkeypatch.setattr("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[]))
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/laan/{khatm_id}/decide")
    resp = await decide_laan_moderation(
        request=req,
        khatm_id=khatm_id,
        decision="reject",
        updated_description="",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=laan&saved=laan_rejected"
    assert mock_audit.called


# -----------------------------------------------------------------------------
# 4. Actions: Cover Review Decisions
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_decide_cover_approve(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    khatm_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    reviewed_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات",
        creator_user_id=creator_id,
    )
    monkeypatch.setattr("khatmsaz.modules.khatm.service.review_cover", AsyncMock(return_value=reviewed_khatm))
    monkeypatch.setattr("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[]))
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/covers/{khatm_id}/decide")
    resp = await decide_cover_moderation(
        request=req,
        khatm_id=khatm_id,
        decision="approve",
        note="",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=covers&saved=cover_approved"
    assert mock_audit.called


@pytest.mark.asyncio
async def test_decide_cover_reject(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    khatm_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    reviewed_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات",
        creator_user_id=creator_id,
    )
    monkeypatch.setattr("khatmsaz.modules.khatm.service.review_cover", AsyncMock(return_value=reviewed_khatm))
    monkeypatch.setattr("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[]))
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/covers/{khatm_id}/decide")
    resp = await decide_cover_moderation(
        request=req,
        khatm_id=khatm_id,
        decision="reject",
        note="تصویر بی‌کیفیت است",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=covers&saved=cover_rejected"
    assert mock_audit.called


# -----------------------------------------------------------------------------
# 5. Actions: Khatm Type Proposals Decisions
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_decide_khatm_request_approve(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    request_id = uuid.uuid4()
    requester_id = uuid.uuid4()

    req_obj = SimpleNamespace(id=request_id, requester_user_id=requester_id)
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.get", AsyncMock(return_value=req_obj))
    mock_approve = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.approve", mock_approve)
    monkeypatch.setattr("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[]))
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/khatm-requests/{request_id}/decide")
    resp = await decide_khatm_request_moderation(
        request=req,
        request_id=request_id,
        decision="approve",
        note="به لیست ختم‌ها افزوده خواهد شد",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=requests&saved=req_approved"
    assert mock_approve.called
    assert mock_audit.called


@pytest.mark.asyncio
async def test_decide_khatm_request_reject(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    request_id = uuid.uuid4()
    requester_id = uuid.uuid4()

    req_obj = SimpleNamespace(id=request_id, requester_user_id=requester_id)
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.get", AsyncMock(return_value=req_obj))
    mock_reject = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.khatm_request.service.reject", mock_reject)
    monkeypatch.setattr("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[]))
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/khatm-requests/{request_id}/decide")
    resp = await decide_khatm_request_moderation(
        request=req,
        request_id=request_id,
        decision="reject",
        note="امکان افزودن وجود ندارد",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=requests&saved=req_rejected"
    assert mock_reject.called
    assert mock_audit.called


# -----------------------------------------------------------------------------
# 6. Actions: Support Tickets
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reply_support_ticket(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    ticket_id = uuid.uuid4()

    mock_answer = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.support_ticket.service.answer_ticket_by_admin", mock_answer)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/tickets/{ticket_id}/reply")
    resp = await reply_support_ticket(
        request=req,
        ticket_id=ticket_id,
        reply_text="سلام، تراکنش شما بررسی و فعال شد.",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=tickets&saved=ticket_answered"
    assert mock_answer.called


@pytest.mark.asyncio
async def test_close_support_ticket(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    ticket_id = uuid.uuid4()

    mock_close = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.support_ticket.service.close_ticket_by_admin", mock_close)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/tickets/{ticket_id}/close")
    resp = await close_support_ticket(
        request=req,
        ticket_id=ticket_id,
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=tickets&saved=ticket_closed"
    assert mock_close.called


# -----------------------------------------------------------------------------
# 7. Actions: Advertising Banners Moderation
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_moderation_decide_banner_approve(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    banner_id = uuid.uuid4()

    mock_banner = SimpleNamespace(id=banner_id, title="بنر تأیید شده")
    mock_review = AsyncMock(return_value=mock_banner)
    monkeypatch.setattr("khatmsaz.modules.advertising.service.review_banner", mock_review)
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/banners/{banner_id}/decide")
    resp = await moderation_decide_banner(
        request=req,
        banner_id=str(banner_id),
        decision="approve",
        admin_note="تأیید شد",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=banners&saved=banner_approved"
    assert mock_review.called
    assert mock_audit.called


@pytest.mark.asyncio
async def test_moderation_decide_banner_reject(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    banner_id = uuid.uuid4()

    mock_banner = SimpleNamespace(id=banner_id, title="بنر رد شده")
    mock_review = AsyncMock(return_value=mock_banner)
    monkeypatch.setattr("khatmsaz.modules.advertising.service.review_banner", mock_review)
    mock_audit = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", mock_audit)

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    req = _make_request(f"/moderation/banners/{banner_id}/decide")
    resp = await moderation_decide_banner(
        request=req,
        banner_id=str(banner_id),
        decision="reject",
        admin_note="محتوا خلاف قوانین است",
        csrf="valid-csrf",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/moderation?tab=banners&saved=banner_rejected"
    assert mock_review.called
    assert mock_audit.called
