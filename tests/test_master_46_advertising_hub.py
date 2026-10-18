"""Unit and integration tests for MASTER-46: Advertising and Banner Hub."""

import uuid
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from khatmsaz.core.ids import new_id
from khatmsaz.modules.advertising import service as ad_service
from khatmsaz.modules.advertising.models import (
    AdvertisingBanner,
    BannerPlacement,
    BannerStatus,
    BannerType,
)
from khatmsaz.modules.authorization.models import AdminPermission
from khatmsaz.web.app import app


def test_banner_template_structure():
    """Verify banners.html template exists and has all required components."""
    template_path = Path(__file__).resolve().parent.parent / "src" / "khatmsaz" / "web" / "templates" / "banners.html"
    assert template_path.exists(), "banners.html must exist"
    content = template_path.read_text(encoding="utf-8")
    assert "مرکز مدیریت بنرها، تبلیغات و اطلاعیه‌ها" in content
    assert "کل بنرها" in content
    assert "بنرهای فعال" in content
    assert "در انتظار تأیید" in content
    assert "مجموع نمایش / کلیک" in content
    assert "SYSTEM_CULTURAL" in content
    assert "COMMERCIAL_AD" in content
    assert "PORTION_FOOTER" in content
    assert "INVITE_PAGE" in content
    assert "/banners/create" in content


def test_base_navigation_contains_banners():
    """Verify base.html contains the /banners route in navigation."""
    base_path = Path(__file__).resolve().parent.parent / "src" / "khatmsaz" / "web" / "templates" / "base.html"
    content = base_path.read_text(encoding="utf-8")
    assert 'navlink("/banners"' in content
    assert "بنرها و اطلاعیه‌ها" in content


@pytest.mark.asyncio
async def test_create_and_toggle_banner():
    """Verify creating a banner and toggling its active status."""
    mock_banner = AdvertisingBanner(
        id=new_id(),
        title="تست پویش صلوات",
        content_text="متن پیام پویش برای کاربران",
        banner_type=BannerType.SYSTEM_CULTURAL,
        placement=BannerPlacement.PORTION_FOOTER,
        image_url="https://example.com/banner.jpg",
        button_text="مشاهده پویش",
        button_url="https://t.me/khatmsaz",
        is_active=True,
        status=BannerStatus.APPROVED,
        impressions_count=10,
        clicks_count=2,
    )

    mock_session = AsyncMock()

    with patch.object(ad_service.ad_repository, "create_banner", return_value=mock_banner) as mock_create:
        banner = await ad_service.create_banner(
            mock_session,
            title="تست پویش صلوات",
            content_text="متن پیام پویش برای کاربران",
            banner_type=BannerType.SYSTEM_CULTURAL,
            placement=BannerPlacement.PORTION_FOOTER,
            button_text="مشاهده پویش",
            button_url="https://t.me/khatmsaz",
        )
        assert banner.title == "تست پویش صلوات"
        assert banner.banner_type == BannerType.SYSTEM_CULTURAL
        mock_create.assert_called_once()

    with patch.object(ad_service.ad_repository, "toggle_banner_active", return_value=False) as mock_toggle:
        new_active = await ad_service.toggle_banner_active(mock_session, mock_banner.id)
        assert new_active is False
        mock_toggle.assert_called_once_with(mock_session, mock_banner.id)


@pytest.mark.asyncio
async def test_cultural_vs_commercial_opt_in_separation():
    """Verify that commercial ads are strictly hidden in khatms without advertising opt-in."""
    mock_cultural = AdvertisingBanner(
        id=new_id(),
        title="اطلاعیه مذهبی",
        content_text="دعای روز جمعه",
        banner_type=BannerType.SYSTEM_CULTURAL,
        placement=BannerPlacement.PORTION_FOOTER,
        is_active=True,
        status=BannerStatus.APPROVED,
    )
    mock_commercial = AdvertisingBanner(
        id=new_id(),
        title="تبلیغ فروشگاه",
        content_text="تخفیف کتب مذهبی",
        banner_type=BannerType.COMMERCIAL_AD,
        placement=BannerPlacement.PORTION_FOOTER,
        is_active=True,
        status=BannerStatus.APPROVED,
    )

    mock_session = AsyncMock()

    # When khatm_advertising_enabled is False: only cultural returned
    with patch.object(ad_service.ad_repository, "get_active_banners_for_placement", return_value=[mock_cultural]) as mock_get:
        banners = await ad_service.get_active_banners_for_placement(
            mock_session, BannerPlacement.PORTION_FOOTER, khatm_advertising_enabled=False
        )
        assert len(banners) == 1
        assert banners[0].banner_type == BannerType.SYSTEM_CULTURAL
        mock_get.assert_called_once_with(
            mock_session, BannerPlacement.PORTION_FOOTER, banner_type=None, khatm_advertising_enabled=False, now=None
        )

    # When khatm_advertising_enabled is True: both returned
    with patch.object(ad_service.ad_repository, "get_active_banners_for_placement", return_value=[mock_cultural, mock_commercial]) as mock_get:
        banners = await ad_service.get_active_banners_for_placement(
            mock_session, BannerPlacement.PORTION_FOOTER, khatm_advertising_enabled=True
        )
        assert len(banners) == 2
        mock_get.assert_called_once_with(
            mock_session, BannerPlacement.PORTION_FOOTER, banner_type=None, khatm_advertising_enabled=True, now=None
        )


@pytest.mark.asyncio
async def test_review_banner_and_refund_on_rejection():
    """Verify that rejecting a creator-paid banner refunds cost to their wallet."""
    creator_id = new_id()
    mock_banner = AdvertisingBanner(
        id=new_id(),
        title="بنر تبلیغاتی سازنده",
        content_text="متن پیام تبلیغاتی",
        banner_type=BannerType.COMMERCIAL_AD,
        placement=BannerPlacement.ALL,
        creator_user_id=creator_id,
        cost_toman=50000,
        status=BannerStatus.PENDING,
        is_active=True,
    )

    mock_session = AsyncMock()
    mock_wallet = AsyncMock()
    mock_wallet.id = new_id()

    with patch.object(ad_service.ad_repository, "get_banner", return_value=mock_banner), \
         patch.object(ad_service.wallet_service, "get_or_create_wallet", return_value=mock_wallet), \
         patch.object(ad_service.wallet_repository, "add_balance") as mock_add_balance, \
         patch.object(ad_service.wallet_repository, "record_transaction") as mock_record_tx, \
         patch.object(ad_service.ad_repository, "update_banner_status") as mock_update_status:

        await ad_service.review_banner(mock_session, mock_banner.id, "reject", admin_note="نامناسب")

        mock_add_balance.assert_called_once_with(mock_session, mock_wallet.id, 50000)
        mock_record_tx.assert_called_once()
        mock_update_status.assert_called_once_with(
            mock_session, mock_banner.id, status=BannerStatus.REJECTED, admin_note="نامناسب"
        )


def test_banners_dashboard_renders_and_actions():
    """Verify /banners GET, POST /banners/create, and POST /banners/{id}/toggle routes."""
    mock_admin = AsyncMock()
    mock_admin.id = new_id()
    mock_admin.permissions = [AdminPermission.MODERATION_MANAGE, AdminPermission.SUPPORT_USERS]

    mock_banner = AdvertisingBanner(
        id=new_id(),
        title="بنر سراسری تست",
        content_text="توضیحات تست",
        banner_type=BannerType.SYSTEM_CULTURAL,
        placement=BannerPlacement.ALL,
        is_active=True,
        status=BannerStatus.APPROVED,
        impressions_count=100,
        clicks_count=10,
        created_at=datetime.now(timezone.utc),
    )

    stats = {
        "total_banners": 1,
        "active_banners": 1,
        "pending_review": 0,
        "total_impressions": 100,
        "total_clicks": 10,
    }

    with patch("khatmsaz.web.app._admin", return_value=(mock_admin, "raw_cookie")), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.modules.advertising.service.get_banner_stats", return_value=stats), \
         patch("khatmsaz.modules.advertising.service.list_banners", return_value=[mock_banner]):

        client = TestClient(app)
        res = client.get("/banners")
        assert res.status_code == 200
        assert "مرکز مدیریت بنرها" in res.text
        assert "بنر سراسری تست" in res.text

    # Test POST /banners/create
    with patch("khatmsaz.web.app._admin", return_value=(mock_admin, "raw_cookie")), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.modules.advertising.service.create_banner", return_value=mock_banner), \
         patch("khatmsaz.modules.audit_log.service.record") as mock_audit:

        client = TestClient(app)
        res = client.post(
            "/banners/create",
            data={
                "title": "بنر جدید",
                "banner_type": "SYSTEM_CULTURAL",
                "placement": "ALL",
                "content_text": "متن بنر جدید",
                "is_active": "1",
                "csrf": "dummy_csrf",
            },
            follow_redirects=False,
        )
        assert res.status_code == 303
        assert res.headers["location"] == "/banners?saved=banner_created"
        mock_audit.assert_called_once()
