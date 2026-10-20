"""Unit and integration tests for MASTER-56: Executive Commander Dashboard & Overview Hub (/).

Tests cover:
- Unauthenticated access redirect to /login
- Authenticated view of / with full dashboard KPIs:
  - 5 live system metrics (active_khatms, active_members, users, paid_total, pending)
  - 6 action queues (laan, covers, requests, tickets, banners, broadcasts)
  - 10 modern command hubs links
  - Devotional reception ranking & platform breakdown
  - Recent khatms list
- Verification of pending queues querying support tickets and advertising banners
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from khatmsaz.modules.authorization.models import AdminPermission
from khatmsaz.web.app import dashboard


@pytest.fixture
def mock_admin():
    return SimpleNamespace(
        id=uuid.uuid4(),
        display_name="فرمانده ارشد سامانه",
        is_super_admin=True,
        _admin_permissions={p.value for p in AdminPermission},
    )


def _make_request(path: str = "/", query_string: bytes = b"") -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": query_string,
        }
    )


# -----------------------------------------------------------------------------
# 1. Access Control Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_unauthenticated_redirect(monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(None, None)))
    req = _make_request("/")
    resp = await dashboard(req)
    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


# -----------------------------------------------------------------------------
# 2. Authenticated Dashboard KPIs & Modern Hubs
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_authenticated_render_with_kpis_and_queues(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))

    mock_analytics = {
        "platform": {
            "total_users": 2500,
            "active_users": 2100,
            "telegram_users": 1800,
            "bale_users": 700,
            "dual_platform_users": 250,
            "creators_count": 85,
            "super_admins_count": 3,
            "regular_users_count": 2412,
        },
        "categories": [
            {
                "key": "QURAN",
                "title": "قرآن کریم",
                "icon": "📖",
                "bot_category_key": "QURAN",
                "order": 1,
                "engaged_users": 1200,
                "total_khatms": 80,
                "active_khatms": 45,
                "total_participations": 3500,
                "popularity_percent": 48.0,
                "rank": 1,
                "is_top": True,
            },
            {
                "key": "SALAWAT",
                "title": "صلوات و ادعیه",
                "icon": "📿",
                "bot_category_key": "SALAWAT",
                "order": 2,
                "engaged_users": 800,
                "total_khatms": 40,
                "active_khatms": 25,
                "total_participations": 1800,
                "popularity_percent": 32.0,
                "rank": 2,
                "is_top": False,
            },
        ],
        "top_category": {
            "title": "قرآن کریم",
            "popularity_percent": 48.0,
        },
        "total_engaged_users": 2500,
        "total_khatms": 120,
        "total_participations": 5300,
    }
    monkeypatch.setattr(
        "khatmsaz.modules.reporting.service.get_system_user_analytics",
        AsyncMock(return_value=mock_analytics),
    )

    mock_session = AsyncMock()
    # Mocking sequential scalar responses:
    # 1: users (2500)
    # 2: active_khatms (70)
    # 3: active_members (350)
    # 4: pending_laan (3)
    # 5: pending_covers (2)
    # 6: pending_broadcasts (1)
    # 7: pending_phones (0)
    # 8: pending_creators (0)
    # 9: pending_categories (0)
    # 10: pending_requests (4)
    # 11: pending_tickets (5)
    # 12: pending_banners (2)
    # 13: paid_total (12500000)
    mock_session.scalar = AsyncMock(
        side_effect=[
            2500,
            70,
            350,
            3,
            2,
            1,
            0,
            0,
            0,
            4,
            5,
            2,
            12500000,
        ]
    )

    sample_khatm = SimpleNamespace(
        id=uuid.uuid4(),
        title="ختم صلوات فرج روزانه",
        template_type="SALAWAT",
        khatm_type="COLLECTIVE",
        status=SimpleNamespace(value="ACTIVE"),
        created_at=datetime.now(timezone.utc),
    )
    mock_exec = MagicMock()
    mock_exec.scalars.return_value = [sample_khatm]
    mock_session.execute = AsyncMock(return_value=mock_exec)

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/")

    resp = await dashboard(req)
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    # Header and greeting
    assert "مرکز کنترل و مانیتورینگ ربات‌های ختم‌ساز" in html
    assert "سلام فرمانده ارشد سامانه؛ وضعیت سامانه پایدار است." in html

    # KPIs
    assert "ختم‌های فعال" in html
    assert "مشارکت فعال" in html
    assert "کل کاربران" in html
    assert "کل درآمد موفق" in html
    assert "در انتظار بررسی" in html
    assert "12,500,000" in html

    # 6 Action Queues
    assert "صف‌های اقدام فوری و نظارت" in html
    assert "لعن سفارشی" in html
    assert "کاور ختم" in html
    assert "پیشنهاد ختم" in html
    assert "تیکت‌های پشتیبانی" in html
    assert "بنرها و تبلیغات" in html
    assert "پیام‌های گروهی" in html

    # 10 Modern Command Hubs
    assert "مراکز ۱۰‌گانه فرماندهی سامانه" in html
    assert "مرکز جامع نظارت" in html
    assert "مدیریت ختم‌ها" in html
    assert "استودیو محتوا و ادعیه" in html
    assert "بانک قرآن کریم" in html
    assert "امور مالی و پلن‌ها" in html
    assert "کاربران ۳۶۰°" in html
    assert "پیام‌های گروهی و کمپین" in html
    assert "ناوگان ۱۸ ربات" in html
    assert "تحلیل و خروجی اکسل" in html
    assert "مدیران و ممیزی" in html

    # Analytics
    assert "تحلیل جامع استقبال و تفکیک کاربران" in html
    assert "تلگرام" in html
    assert "بله" in html
    assert "ختم صلوات فرج روزانه" in html
