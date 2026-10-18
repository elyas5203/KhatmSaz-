"""Comprehensive test suite for MASTER-42: Support Tickets & Direct Messaging Hub."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from starlette.testclient import TestClient

from khatmsaz.modules.identity.models import Platform, User, UserRole, PlatformIdentity
from khatmsaz.modules.support_ticket.models import SupportTicket, SupportTicketStatus
from khatmsaz.modules.support_ticket import repository as ticket_repo
from khatmsaz.modules.support_ticket import service as ticket_service
from khatmsaz.web.app import app


def test_support_ticket_model_structure():
    user_id = uuid.uuid4()
    ticket = SupportTicket(
        sender_user_id=user_id,
        body="پیشنهاد اضافه کردن دعای جوشن کبیر به سامانه",
        target_role="SUPER_ADMIN",
    )
    assert ticket.sender_user_id == user_id
    assert ticket.body == "پیشنهاد اضافه کردن دعای جوشن کبیر به سامانه"
    assert ticket.status == SupportTicketStatus.PENDING
    assert ticket.target_role == "SUPER_ADMIN"
    assert ticket.target_creator_id is None
    assert ticket.reply_text is None


@pytest.mark.asyncio
async def test_repository_ticket_lifecycle():
    user_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    added_items = []

    class DummySession:
        def add(self, item):
            added_items.append(item)

        async def flush(self):
            pass

        async def get(self, model, ident):
            for item in added_items:
                if item.id == ident:
                    return item
            return None

    session = DummySession()

    # 1. Create ticket
    ticket = await ticket_repo.create(
        session,
        sender_user_id=user_id,
        body="سلام، آیا امکان برگزاری ختم قرآن گروهی برای ۱۰۰۰ نفر هست؟",
        target_role="SUPER_ADMIN",
    )
    assert ticket.id is not None
    assert ticket.status == SupportTicketStatus.PENDING
    assert ticket.sender_user_id == user_id

    # 2. Answer ticket
    answered = await ticket_repo.answer_ticket(
        session,
        ticket_id=ticket.id,
        reply_text="سلام و درود، بله از طریق منوی ارتقا به پلن حرفه‌ای امکان‌پذیر است.",
        replied_by_user_id=admin_id,
    )
    assert answered.status == SupportTicketStatus.ANSWERED
    assert answered.reply_text.startswith("سلام و درود")
    assert answered.replied_by_user_id == admin_id
    assert answered.replied_at is not None

    # 3. Close ticket
    closed = await ticket_repo.close_ticket(session, ticket.id)
    assert closed.status == SupportTicketStatus.CLOSED


@pytest.mark.asyncio
async def test_service_submit_and_answer_with_notification():
    user_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    ticket_id = uuid.uuid4()

    mock_ticket = SupportTicket(
        id=ticket_id,
        sender_user_id=user_id,
        body="درخواست راهنمایی در خصوص پرداخت پی‌پینگ",
        status=SupportTicketStatus.PENDING,
    )

    mock_ident = PlatformIdentity(
        user_id=user_id,
        platform=Platform.TELEGRAM,
        subject="12345678",
    )

    sent_notifications = []

    async def dummy_notify(platform, subject, text, **kwargs):
        sent_notifications.append({"platform": platform, "subject": subject, "text": text})

    with patch("khatmsaz.modules.support_ticket.repository.answer_ticket", AsyncMock(return_value=mock_ticket)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit, \
         patch("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[mock_ident])), \
         patch("khatmsaz.modules.support_ticket.service.get_notify_fn", return_value=dummy_notify):

        res = await ticket_service.answer_ticket_by_admin(
            AsyncMock(),
            ticket_id=ticket_id,
            reply_text="مشکل درگاه با موفقیت بررسی و رفع گردید.",
            admin_user_id=admin_id,
        )

        assert res.id == ticket_id
        mock_audit.assert_awaited_once()
        assert len(sent_notifications) == 1
        assert sent_notifications[0]["subject"] == "12345678"
        assert "مشکل درگاه با موفقیت بررسی و رفع گردید" in sent_notifications[0]["text"]


def test_web_moderation_tab_tickets_renders():
    client = TestClient(app, raise_server_exceptions=True)

    admin_user = User(
        id=uuid.uuid4(),
        role=UserRole.SUPER_ADMIN,
        display_name="مدیر کل سیستم",
    )

    mock_ticket = SupportTicket(
        id=uuid.uuid4(),
        sender_user_id=uuid.uuid4(),
        body="متن پیام تستی برای بررسی نمایش در تب تیکت‌ها",
        status=SupportTicketStatus.PENDING,
    )

    sender_user = User(id=mock_ticket.sender_user_id, display_name="کاربر تست")

    from contextlib import asynccontextmanager
    from unittest.mock import MagicMock

    mock_session = AsyncMock()
    mock_exec = MagicMock()
    mock_exec.scalars.return_value = [sender_user]
    mock_session.execute.return_value = mock_exec

    @asynccontextmanager
    async def dummy_scope():
        yield mock_session

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "valid_raw"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", dummy_scope), \
         patch("khatmsaz.modules.support_ticket.service.list_admin_tickets", AsyncMock(return_value=[mock_ticket])), \
         patch("khatmsaz.modules.khatm.service.list_pending_laan_khatms", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.khatm.service.list_pending_covers", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.khatm_request.service.list_pending", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.broadcast.service.list_pending", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.creator_request.service.list_pending", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.manual_phone_verification.repository.list_pending", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.khatm_category.service.list_pending_requests", AsyncMock(return_value=[])):

        client.cookies.set("khatmsaz_session", "valid_raw")
        resp = client.get("/moderation?tab=tickets")
        assert resp.status_code == 200
        assert "تیکت‌های پشتیبانی" in resp.text
        assert "متن پیام تستی برای بررسی نمایش در تب تیکت‌ها" in resp.text
        assert "ارسال پاسخ مستقیم به کاربر" in resp.text


def test_web_moderation_ticket_reply_action():
    client = TestClient(app, raise_server_exceptions=False)
    admin_user = User(id=uuid.uuid4(), role=UserRole.SUPER_ADMIN)
    ticket_id = uuid.uuid4()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "valid_raw"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.modules.support_ticket.service.answer_ticket_by_admin", AsyncMock()) as mock_answer:

        resp = client.post(
            f"/moderation/tickets/{ticket_id}/reply",
            data={"reply_text": "پاسخ ادمین از طریق پنل وب", "csrf": "csrf_token"},
            cookies={"khatmsaz_session": "valid_raw"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/moderation?tab=tickets&saved=ticket_answered" in resp.headers["location"]
        mock_answer.assert_awaited_once()


def test_web_moderation_ticket_close_action():
    client = TestClient(app, raise_server_exceptions=False)
    admin_user = User(id=uuid.uuid4(), role=UserRole.SUPER_ADMIN)
    ticket_id = uuid.uuid4()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "valid_raw"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.modules.support_ticket.service.close_ticket_by_admin", AsyncMock()) as mock_close:

        resp = client.post(
            f"/moderation/tickets/{ticket_id}/close",
            data={"csrf": "csrf_token"},
            cookies={"khatmsaz_session": "valid_raw"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/moderation?tab=tickets&saved=ticket_closed" in resp.headers["location"]
        mock_close.assert_awaited_once()
