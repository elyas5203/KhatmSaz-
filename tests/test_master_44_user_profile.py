"""Tests for MASTER-44: User 360 Profile & Financial Wallet Management Hub in Web Admin."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import Request
from khatmsaz.modules.identity.models import User, UserStatus, UserRole, PlatformIdentity, Platform
from khatmsaz.modules.wallet.models import Wallet, WalletInvoice, WalletTransaction, TxType
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.modules.phone.models import PhoneClaim
from khatmsaz.modules.plan.models import UserPlan, PlanTier
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTypeEnum, KhatmVisibility
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.support_ticket.models import SupportTicket, SupportTicketStatus


def test_user_detail_template_structure():
    with open("src/khatmsaz/web/templates/user_detail.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Verify 360 headers & identity
    assert "پروفایل ۳۶۰ درجه" in content
    assert "target_user.display_name" in content
    assert "target_user.id" in content

    # Verify Financial & Wallet Hub
    assert "مدیریت مالی، کیف پول و اعتبارات کاربر" in content
    assert "wallet.balance_toman" in content
    assert "wallet.credit_toman" in content

    # Verify Adjustment Form & Decision Inputs
    assert 'action="/users/{{ target_user.id }}/wallet"' in content
    assert 'name="balance_type"' in content
    assert 'value="cash"' in content
    assert 'value="credit"' in content
    assert 'name="amount"' in content
    assert 'name="reason"' in content
    assert "اعلان رسمی تغییر موجودی با ذکر مبلغ و علت به چت بات کاربر ارسال می‌شود" in content

    # Verify All 4 Tabs
    assert "tab=khatms" in content
    assert "tab=participations" in content
    assert "tab=finances" in content
    assert "tab=tickets" in content

    # Verify Tab Tables
    assert "ختم‌های ایجادشده توسط این کاربر" in content
    assert "سوابق عضویت و تلاوت در ختم‌ها" in content
    assert "فاکتورها و اسناد مالی (Invoices)" in content
    assert "تیکت‌های پشتیبانی ارسالی کاربر" in content


def test_users_template_has_360_links():
    with open("src/khatmsaz/web/templates/users.html", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'href="/users/{{ user.id }}"' in content
    assert "۳۶۰° ←" in content


@pytest.mark.asyncio
async def test_admin_adjust_user_wallet_cash():
    from khatmsaz.web.app import admin_adjust_user_wallet

    user_id = uuid4()
    admin_id = uuid4()
    wallet_mock = MagicMock()
    wallet_mock.balance_toman = 75000
    wallet_mock.credit_toman = 10000

    admin_user = MagicMock()
    admin_user.id = admin_id

    mock_notify = AsyncMock()
    user_ident = PlatformIdentity(user_id=user_id, platform=Platform.TELEGRAM, subject="998877")

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_token"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.admin_adjust_wallet", AsyncMock(return_value=wallet_mock)) as mock_wallet_adjust, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit, \
         patch("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[user_ident])), \
         patch("khatmsaz.web.app.get_notify_fn", return_value=mock_notify):

        resp = await admin_adjust_user_wallet(
            request=req,
            user_id=user_id,
            cash_delta=0,
            credit_delta=0,
            balance_type="cash",
            amount=50000,
            reason="شارژ نقدی تشویقی",
            csrf="mock_token",
            redirect_to=f"/users/{user_id}",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == f"/users/{user_id}?saved=wallet_adjusted"

        mock_wallet_adjust.assert_awaited_once_with(
            dummy_session,
            user_id,
            cash_delta=50000,
            credit_delta=0,
            description="شارژ نقدی تشویقی",
        )

        mock_audit.assert_awaited_once()
        audit_call = mock_audit.await_args[1]
        assert audit_call["action"] == "ADMIN_WALLET_ADJUST"
        assert audit_call["details"]["cash_delta"] == 50000
        assert audit_call["details"]["balance_type"] == "cash"

        mock_notify.assert_awaited_once()
        notify_call = mock_notify.await_args[0]
        assert notify_call[0] == "TELEGRAM"
        assert notify_call[1] == "998877"
        assert "50,000 تومان" in notify_call[2]
        assert "شارژ نقدی تشویقی" in notify_call[2]
        assert "75,000 تومان" in notify_call[2]


@pytest.mark.asyncio
async def test_admin_adjust_user_wallet_credit():
    from khatmsaz.web.app import admin_adjust_user_wallet

    user_id = uuid4()
    admin_id = uuid4()
    wallet_mock = MagicMock()
    wallet_mock.balance_toman = 10000
    wallet_mock.credit_toman = 35000

    admin_user = MagicMock()
    admin_user.id = admin_id

    mock_notify = AsyncMock()
    user_ident = PlatformIdentity(user_id=user_id, platform=Platform.BALE, subject="554433")

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_token"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.admin_adjust_wallet", AsyncMock(return_value=wallet_mock)) as mock_wallet_adjust, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit, \
         patch("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[user_ident])), \
         patch("khatmsaz.web.app.get_notify_fn", return_value=mock_notify):

        resp = await admin_adjust_user_wallet(
            request=req,
            user_id=user_id,
            cash_delta=0,
            credit_delta=0,
            balance_type="credit",
            amount=25000,
            reason="اعتبار هدیه عید",
            csrf="mock_token",
            redirect_to=f"/users/{user_id}",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == f"/users/{user_id}?saved=wallet_adjusted"

        mock_wallet_adjust.assert_awaited_once_with(
            dummy_session,
            user_id,
            cash_delta=0,
            credit_delta=25000,
            description="اعتبار هدیه عید",
        )

        mock_notify.assert_awaited_once()
        notify_call = mock_notify.await_args[0]
        assert notify_call[0] == "BALE"
        assert notify_call[1] == "554433"
        assert "25,000 تومان" in notify_call[2]
        assert "اعتبار هدیه عید" in notify_call[2]


@pytest.mark.asyncio
async def test_user_detail_route_loads_successfully():
    from khatmsaz.web.app import user_detail

    user_id = uuid4()
    admin_id = uuid4()

    admin_user = MagicMock()
    admin_user.id = admin_id

    target_user = User(
        id=user_id,
        display_name="کاربر نمونه",
        status=UserStatus.ACTIVE,
        role=UserRole.CREATOR,
        created_at=datetime.now(timezone.utc),
    )

    wallet_mock = MagicMock()
    wallet_mock.id = uuid4()
    wallet_mock.balance_toman = 50000
    wallet_mock.credit_toman = 15000

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()
    req.query_params = {}

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_token"))), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.identity.service.find_by_id", AsyncMock(return_value=target_user)), \
         patch("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.wallet.service.get_or_create_wallet", AsyncMock(return_value=wallet_mock)):

        # Mock scalar results for execute
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_scalars.all.return_value = []

        mock_exec_result = MagicMock()
        mock_exec_result.scalars.return_value = mock_scalars
        mock_exec_result.all.return_value = []
        dummy_session.execute.return_value = mock_exec_result
        dummy_session.get.return_value = None

        resp = await user_detail(request=req, user_id=user_id)
        assert resp.status_code == 200
        # Verify rendered template contains user name
        assert "کاربر نمونه" in resp.body.decode("utf-8")
