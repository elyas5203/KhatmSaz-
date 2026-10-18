"""Tests for MASTER-45: Discount Coupons & Campaign Management Hub in Web Admin."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import Request
from khatmsaz.modules.wallet.models import DiscountCoupon, CouponDiscountType, CouponRedemption, WalletInvoice
from khatmsaz.modules.identity.models import User, UserStatus, UserRole


def test_coupons_template_structure():
    with open("src/khatmsaz/web/templates/coupons.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Header and Help
    assert "مرکز مدیریت کدهای تخفیف و کمپین‌ها" in content
    assert "help_button" in content

    # Metrics
    assert "تعداد کل کدهای تخفیف" in content
    assert "کدهای تخفیف فعال" in content
    assert "کل دفعات استفاده (Redemptions)" in content
    assert "مجموع تخفیف‌های اعطاشده" in content

    # Create Form
    assert 'action="/coupons/create"' in content
    assert 'name="code"' in content
    assert 'name="discount_type"' in content
    assert 'value="PERCENT"' in content
    assert 'value="FIXED"' in content
    assert 'name="value"' in content
    assert 'name="min_purchase_toman"' in content
    assert 'name="total_redemption_limit"' in content
    assert 'name="per_user_limit"' in content
    assert 'name="is_active"' in content

    # Table and Toggle Form
    assert "فهرست کدهای تخفیف تعریف‌شده" in content
    assert 'action="/coupons/{{ c.code }}/toggle"' in content
    assert "غیرفعال‌سازی" in content
    assert "فعال‌سازی مجدد" in content

    # Redemption Ledger
    assert "دفتر کل ردگیری استفاده کاربران (Redemption Ledger)" in content
    assert "کاربر استفاده‌کننده" in content
    assert "مبلغ تخفیف" in content
    assert "شناسه فاکتور" in content


def test_base_sidebar_contains_coupons():
    with open("src/khatmsaz/web/templates/base.html", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'navlink("/coupons", "کدهای تخفیف و کمپین‌ها"' in content
    assert 'href="/coupons"' in content


@pytest.mark.asyncio
async def test_create_coupon_percent_success():
    from khatmsaz.web.app import create_coupon_hub

    admin_user = MagicMock()
    admin_user.id = uuid4()

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    mock_coupon = MagicMock()
    mock_coupon.code = "SPRING30"
    mock_coupon.discount_type = "PERCENT"
    mock_coupon.value = 30
    mock_coupon.enabled = True

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_token"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.set_coupon", AsyncMock(return_value=mock_coupon)) as mock_set, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await create_coupon_hub(
            request=req,
            csrf="mock_token",
            code="spring30",
            discount_type="PERCENT",
            value=30,
            min_purchase_toman=10000,
            total_redemption_limit="50",
            per_user_limit=1,
            max_discount_toman="15000",
            is_active="on",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == "/coupons?saved=coupon_created"

        mock_set.assert_awaited_once_with(
            dummy_session,
            code="spring30",
            discount_type=CouponDiscountType.PERCENT,
            value=30,
            min_purchase_toman=10000,
            max_discount_toman=15000,
            total_redemption_limit=50,
            per_user_limit=1,
            created_by_user_id=admin_user.id,
            enabled=True,
        )

        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "WEB_COUPON_CREATE"


@pytest.mark.asyncio
async def test_toggle_coupon_hub_success():
    from khatmsaz.web.app import toggle_coupon_hub

    admin_user = MagicMock()
    admin_user.id = uuid4()

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    existing_coupon = DiscountCoupon(
        code="EID1405",
        discount_type="PERCENT",
        value=50,
        enabled=True,
    )

    toggled_coupon = MagicMock()
    toggled_coupon.code = "EID1405"
    toggled_coupon.enabled = False

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_token"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.list_coupons", AsyncMock(return_value=[existing_coupon])), \
         patch("khatmsaz.modules.wallet.service.set_coupon_enabled", AsyncMock(return_value=toggled_coupon)) as mock_toggle, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await toggle_coupon_hub(request=req, code="EID1405", csrf="mock_token")

        assert resp.status_code == 303
        assert resp.headers["location"] == "/coupons?saved=coupon_toggled"

        # Toggle from True to False
        mock_toggle.assert_awaited_once_with(dummy_session, "EID1405", False)
        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "WEB_COUPON_TOGGLE"


@pytest.mark.asyncio
async def test_coupons_dashboard_renders_successfully():
    from khatmsaz.web.app import coupons_dashboard

    admin_user = MagicMock()
    admin_user.id = uuid4()

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()
    req.query_params = {}

    coupon = DiscountCoupon(
        code="GHADIR",
        discount_type="FIXED",
        value=20000,
        enabled=True,
        min_purchase_toman=0,
        per_user_limit=1,
    )

    user = User(
        id=uuid4(),
        display_name="کاربر شرکت‌کننده",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
        created_at=datetime.now(timezone.utc),
    )

    redemption = CouponRedemption(
        id=uuid4(),
        coupon_code="GHADIR",
        user_id=user.id,
        invoice_id=uuid4(),
        discount_amount_toman=20000,
        redeemed_at=datetime.now(timezone.utc),
    )

    stats = {
        "GHADIR": {"uses_count": 1, "total_saved_toman": 20000}
    }

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_token"))), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.wallet.service.list_coupons", AsyncMock(return_value=[coupon])), \
         patch("khatmsaz.modules.wallet.service.get_coupon_redemption_stats", AsyncMock(return_value=stats)), \
         patch("khatmsaz.modules.wallet.service.list_coupon_redemptions", AsyncMock(return_value=[(redemption, user, None)])):

        resp = await coupons_dashboard(request=req)
        assert resp.status_code == 200
        body = resp.body.decode("utf-8")
        assert "GHADIR" in body
        assert "کاربر شرکت‌کننده" in body
        assert "مرکز مدیریت کدهای تخفیف و کمپین‌ها" in body
