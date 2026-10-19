"""Unit and integration tests for MASTER-49: Finance, Subscription Plans, Member Caps & Tariffs Hub."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import Request
from starlette.testclient import TestClient

from khatmsaz.modules.plan.models import PlanTier, PricingMode, PlanDefinition
from khatmsaz.modules.wallet.models import WalletInvoice, InvoiceStatus, Wallet
from khatmsaz.modules.identity.models import User
from khatmsaz.web.app import app, finance, finance_wallet_adjust, finance_refund_invoice, update_plan_definition, update_broadcast_policy


def test_finance_template_structure():
    """Verify that finance.html template contains all MASTER-49 required UI elements and structures."""
    with open("src/khatmsaz/web/templates/finance.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Header and Help button
    assert "مرکز مالی، پلن‌ها و کیف پول" in content
    assert "help_button" in content

    # 4 KPI Cards
    assert "کل مبالغ پرداخت‌شده" in content
    assert "مسترد شده به کیف پول" in content
    assert "کل فاکتورهای ثبت‌شده" in content
    assert "درگاه پرداخت پی‌پینگ (PayPing)" in content

    # Direct Shaparak Gateway Card
    assert "درگاه مستقیم شاپرک پی‌پینگ" in content
    assert "gateway_status.direct_url" in content
    assert "کپی لینک" in content

    # 5 Tabs
    assert 'id="tabBtn_plans"' in content
    assert 'id="tabBtn_invoices"' in content
    assert 'id="tabBtn_wallet"' in content
    assert 'id="tabBtn_coupons"' in content
    assert 'id="tabBtn_policies"' in content

    # Educational & Progressive Disclosure Plan Cards
    assert "سطح رایگان (FREE)" in content
    assert "۱۰۰ نفر" in content
    assert "۳۰۲ نفر" in content
    assert "سطح پایه (BASIC)" in content
    assert "سطح حرفه‌ای (PRO)" in content

    # Invoices Filtering Toolbar
    assert 'name="time_range"' in content
    assert 'value="today"' in content
    assert 'value="7d"' in content
    assert 'value="30d"' in content
    assert 'name="status_filter"' in content
    assert 'value="PAID"' in content
    assert 'value="REFUNDED"' in content

    # Direct link to dedicated coupons hub (MASTER-45)
    assert 'href="/coupons"' in content
    assert "مرکز پیشرفته مدیریت کدهای تخفیف و کمپین‌ها (MASTER-45)" in content

    # Broadcast package pricing (MASTER-38)
    assert "📢 تعرفه و اندازه بسته‌های ارسال پیام گروهی" in content


def test_finance_page_unauthenticated():
    """Unauthenticated access to /finance must redirect to /login."""
    client = TestClient(app, follow_redirects=False)
    response = client.get("/finance")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


@pytest.mark.asyncio
async def test_finance_page_authenticated():
    """Authenticated admin can load /finance and receive full KPI, plan, and gateway contexts."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.display_name = "Finance Admin"

    dummy_session = AsyncMock()
    dummy_session.execute.return_value = MagicMock(
        all=MagicMock(return_value=[]),
        scalars=MagicMock(return_value=[]),
    )
    dummy_session.scalar.return_value = 1500000

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()
    req.query_params = {}

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.list_coupons", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.broadcast.service.channel_policy", AsyncMock(return_value=(0, 150000))), \
         patch("khatmsaz.modules.broadcast.service.channel_package_size", AsyncMock(return_value=1000)):

        resp = await finance(request=req)
        assert resp.status_code == 200
        html = resp.body.decode("utf-8")
        assert "مرکز مالی، پلن‌ها و کیف پول" in html
        assert "درگاه مستقیم شاپرک پی‌پینگ" in html
        assert "https://ppng.ir/d/VFBD" in html


@pytest.mark.asyncio
async def test_finance_page_with_filters():
    """Testing /finance with time_range, status_filter, and search query parameters."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    dummy_session = AsyncMock()
    dummy_session.execute.return_value = MagicMock(
        all=MagicMock(return_value=[]),
        scalars=MagicMock(return_value=[]),
    )
    dummy_session.scalar.return_value = 0

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()
    req.query_params = {"time_range": "today", "status_filter": "PAID", "q": "Mohammad"}

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.list_coupons", AsyncMock(return_value=[])), \
         patch("khatmsaz.modules.broadcast.service.channel_policy", AsyncMock(return_value=(0, 150000))), \
         patch("khatmsaz.modules.broadcast.service.channel_package_size", AsyncMock(return_value=1000)):

        resp = await finance(request=req, time_range="today", status_filter="PAID", q="Mohammad")
        assert resp.status_code == 200
        # Check that session.execute was called to fetch filtered invoices
        assert dummy_session.execute.called


@pytest.mark.asyncio
async def test_finance_wallet_adjust():
    """Testing manual adjustment of user wallet balance and gift credit."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    target_user_id = uuid4()

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.admin_adjust_wallet", AsyncMock()) as mock_adjust, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await finance_wallet_adjust(
            request=req,
            user_id=target_user_id,
            cash_delta=100000,
            credit_delta=25000,
            reason="شارژ هدیه مناسبتی",
            csrf="mock_cookie",
            uq="testuser",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == "/finance?uq=testuser&saved=wallet_adjusted"

        mock_adjust.assert_awaited_once_with(
            dummy_session,
            target_user_id,
            cash_delta=100000,
            credit_delta=25000,
            description="شارژ هدیه مناسبتی",
        )
        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "CREDIT_GRANT"
        assert mock_audit.await_args[1]["target_user_id"] == target_user_id


@pytest.mark.asyncio
async def test_finance_refund_invoice():
    """Testing invoice refund to user wallet with audit log."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    invoice_id = uuid4()
    target_user_id = uuid4()

    mock_invoice = MagicMock(spec=WalletInvoice)
    mock_invoice.id = invoice_id
    mock_invoice.user_id = target_user_id
    mock_invoice.net_amount_toman = 50000
    mock_invoice.status = InvoiceStatus.REFUNDED.value

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.admin_refund_invoice", AsyncMock(return_value=mock_invoice)) as mock_refund, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await finance_refund_invoice(
            request=req,
            invoice_id=invoice_id,
            reason="استرداد درخواست کاربر",
            csrf="mock_cookie",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == "/finance?saved=refunded"

        mock_refund.assert_awaited_once_with(
            dummy_session,
            invoice_id,
            description="استرداد درخواست کاربر",
        )
        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "INVOICE_REFUND"
        assert mock_audit.await_args[1]["details"]["amount"] == 50000


@pytest.mark.asyncio
async def test_update_plan_definition():
    """Testing update of plan definition entitlements and member caps."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    mock_current_def = MagicMock(spec=PlanDefinition)
    mock_current_def.entitlements = {"khatm.create": True}

    mock_updated_def = MagicMock(spec=PlanDefinition)
    mock_updated_def.enabled = True

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.plan.service.get_definition", AsyncMock(return_value=mock_current_def)), \
         patch("khatmsaz.modules.plan.service.set_definition", AsyncMock(return_value=mock_updated_def)) as mock_set_def, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await update_plan_definition(
            request=req,
            plan_name="FREE",
            csrf="mock_cookie",
            title="رایگان شروع",
            pricing_mode="FIXED",
            price_toman=0,
            max_devotional_members="100",
            max_quran_members="302",
            free_total_member_cap="1000",
            ads_enabled="",
            khatm_create="on",
            enabled="on",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == "/finance?saved=plan"

        mock_set_def.assert_awaited_once()
        passed_entitlements = mock_set_def.await_args[1]["entitlements"]
        assert passed_entitlements["max_devotional_members"] == 100
        assert passed_entitlements["max_quran_members"] == 302
        assert passed_entitlements["free_total_member_cap"] == 1000
        assert passed_entitlements["ads_enabled"] is False
        assert passed_entitlements["khatm.create"] is True

        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "PLAN_DEFINITION_UPDATE"


@pytest.mark.asyncio
async def test_update_broadcast_policy():
    """Testing update of broadcast policy tariffs (150,000 Toman / 1,000 members)."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.system_settings.service.set_int", AsyncMock()) as mock_set_int, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await update_broadcast_policy(
            request=req,
            csrf="mock_cookie",
            channel="TELEGRAM",
            price_toman=150000,
            package_size=1000,
            free_count=0,
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == "/finance?saved=broadcast_policy"

        assert mock_set_int.await_count == 3
        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "BROADCAST_POLICY_UPDATE"
        assert mock_audit.await_args[1]["details"]["price_toman"] == 150000
        assert mock_audit.await_args[1]["details"]["package_size"] == 1000
