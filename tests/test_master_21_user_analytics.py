"""Unit and regression tests for MASTER-21: Admin Panel User Analytics & Devotional Breakdown."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from khatmsaz.core.ids import new_id
from khatmsaz.modules.authorization.models import AdminPermission
from khatmsaz.modules.identity.models import User, UserRole, UserStatus
from khatmsaz.modules.reporting import service as reporting_service
from khatmsaz.web.app import COOKIE_NAME, app
from khatmsaz.bot.handlers.admin_bot import handlers as admin_bot_handlers


@pytest.mark.asyncio
async def test_get_system_user_analytics_empty_database():
    """Verify get_system_user_analytics handles an empty database safely."""
    mock_session = AsyncMock()
    # 1. user_counts
    mock_user_counts = MagicMock()
    mock_user_counts.one.return_value = (0, 0, 0, 0, 0)

    # 2. plat_counts
    mock_plat_counts = MagicMock()
    mock_plat_counts.one.return_value = (0, 0)

    # 3. dual subq count
    mock_dual_res = MagicMock()
    mock_dual_res.scalar.return_value = 0

    # 4. khatm_rows
    mock_khatm_rows = MagicMock()
    mock_khatm_rows.all.return_value = []

    # 5. part_rows
    mock_part_rows = MagicMock()
    mock_part_rows.all.return_value = []

    # 6. engaged_rows
    mock_engaged_rows = MagicMock()
    mock_engaged_rows.all.return_value = []

    mock_session.execute.side_effect = [
        mock_user_counts,
        mock_plat_counts,
        mock_dual_res,
        mock_khatm_rows,
        mock_part_rows,
        mock_engaged_rows,
    ]

    analytics = await reporting_service.get_system_user_analytics(mock_session)

    assert analytics["platform"]["total_users"] == 0
    assert analytics["platform"]["telegram_users"] == 0
    assert analytics["platform"]["bale_users"] == 0
    assert analytics["platform"]["dual_platform_users"] == 0
    assert len(analytics["categories"]) == 5

    cat_keys = {c["key"] for c in analytics["categories"]}
    assert cat_keys == {"QURAN", "LAAN", "SALAWAT", "DUA", "KHUTBAH"}
    assert analytics["top_category"] is None


@pytest.mark.asyncio
async def test_get_system_user_analytics_popularity_ranking():
    """Verify categories are correctly ranked by popularity and adoption percentage."""
    mock_session = AsyncMock()

    mock_user_counts = MagicMock()
    mock_user_counts.one.return_value = (100, 95, 10, 2, 88)

    mock_plat_counts = MagicMock()
    mock_plat_counts.one.return_value = (70, 35)

    mock_dual_res = MagicMock()
    mock_dual_res.scalar.return_value = 5

    # Mock khatms: QURAN: 12, SALAWAT: 6, LAAN: 4, DUA: 3, KHUTBAH: 1
    k_rows = [
        MagicMock(category_key="QURAN", total_khatms=12, active_khatms=8),
        MagicMock(category_key="SALAWAT", total_khatms=6, active_khatms=4),
        MagicMock(category_key="LAAN", total_khatms=4, active_khatms=2),
        MagicMock(category_key="DUA", total_khatms=3, active_khatms=1),
        MagicMock(category_key="KHUTBAH", total_khatms=1, active_khatms=1),
    ]
    mock_khatm_res = MagicMock()
    mock_khatm_res.all.return_value = k_rows

    # Mock participations
    p_rows = [
        MagicMock(category_key="QURAN", unique_participants=50, active_participations=40, active_readers=45, total_participations=60),
        MagicMock(category_key="SALAWAT", unique_participants=25, active_participations=20, active_readers=22, total_participations=30),
        MagicMock(category_key="LAAN", unique_participants=15, active_participations=10, active_readers=12, total_participations=18),
        MagicMock(category_key="DUA", unique_participants=8, active_participations=6, active_readers=7, total_participations=10),
        MagicMock(category_key="KHUTBAH", unique_participants=2, active_participations=2, active_readers=2, total_participations=2),
    ]
    mock_part_res = MagicMock()
    mock_part_res.all.return_value = p_rows

    # Mock engaged users
    eng_rows = [
        MagicMock(category_key="QURAN", engaged_users=50),
        MagicMock(category_key="SALAWAT", engaged_users=25),
        MagicMock(category_key="LAAN", engaged_users=15),
        MagicMock(category_key="DUA", engaged_users=8),
        MagicMock(category_key="KHUTBAH", engaged_users=2),
    ]
    mock_eng_res = MagicMock()
    mock_eng_res.all.return_value = eng_rows

    mock_session.execute.side_effect = [
        mock_user_counts,
        mock_plat_counts,
        mock_dual_res,
        mock_khatm_res,
        mock_part_res,
        mock_eng_res,
    ]

    analytics = await reporting_service.get_system_user_analytics(mock_session)

    assert analytics["platform"]["total_users"] == 100
    assert analytics["platform"]["telegram_users"] == 70
    assert analytics["platform"]["bale_users"] == 35
    assert analytics["platform"]["dual_platform_users"] == 5

    # Total engaged = 50 + 25 + 15 + 8 + 2 = 100
    assert analytics["total_engaged_users"] == 100

    # Top category must be QURAN with 50%
    top = analytics["top_category"]
    assert top is not None
    assert top["key"] == "QURAN"
    assert top["rank"] == 1
    assert top["is_top"] is True
    assert top["popularity_percent"] == 50.0

    # Verify order of categories: QURAN (50%), SALAWAT (25%), LAAN (15%), DUA (8%), KHUTBAH (2%)
    keys = [c["key"] for c in analytics["categories"]]
    assert keys == ["QURAN", "SALAWAT", "LAAN", "DUA", "KHUTBAH"]


@pytest.mark.asyncio
async def test_dashboard_renders_user_analytics_section():
    """Verify the / dashboard renders user_analytics cards and devotional ranking."""
    admin_id = new_id()
    mock_admin = User(id=admin_id, display_name="مدیر کل", role=UserRole.SUPER_ADMIN)
    mock_admin._admin_permissions = {p.value for p in AdminPermission}

    mock_analytics = {
        "platform": {
            "total_users": 150,
            "active_users": 140,
            "telegram_users": 110,
            "bale_users": 55,
            "dual_platform_users": 15,
            "creators_count": 8,
            "super_admins_count": 2,
            "regular_users_count": 140,
        },
        "categories": [
            {
                "key": "QURAN",
                "title": "قرآن کریم",
                "icon": "📖",
                "bot_category_key": "QURAN",
                "order": 1,
                "engaged_users": 80,
                "total_khatms": 20,
                "active_khatms": 15,
                "total_participations": 90,
                "popularity_percent": 53.3,
                "rank": 1,
                "is_top": True,
            },
            {
                "key": "SALAWAT",
                "title": "صلوات و اذکار",
                "icon": "📿",
                "bot_category_key": "SALAWAT",
                "order": 3,
                "engaged_users": 40,
                "total_khatms": 10,
                "active_khatms": 6,
                "total_participations": 45,
                "popularity_percent": 26.7,
                "rank": 2,
                "is_top": False,
            },
        ],
        "top_category": {
            "title": "قرآن کریم",
            "popularity_percent": 53.3,
        },
        "total_engaged_users": 150,
        "total_khatms": 30,
        "total_participations": 135,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(COOKIE_NAME, "mock_admin_token")

        with patch("khatmsaz.web.app._admin", new=AsyncMock(return_value=(mock_admin, "mock_raw_token"))), \
             patch("khatmsaz.modules.reporting.service.get_system_user_analytics", new=AsyncMock(return_value=mock_analytics)), \
             patch("khatmsaz.web.app.session_scope") as mock_scope:

            mock_session = AsyncMock()
            mock_session.scalar.return_value = 150
            exec_res = MagicMock()
            exec_res.scalars.return_value = []
            mock_session.execute.return_value = exec_res
            mock_scope.return_value.__aenter__.return_value = mock_session

            response = await client.get("/")
            assert response.status_code == 200
            assert "تحلیل جامع استقبال و تفکیک کاربران" in response.text
            assert "قرآن کریم" in response.text
            assert "تلگرام" in response.text
            assert "بله" in response.text


@pytest.mark.asyncio
async def test_users_page_renders_user_analytics_summary():
    """Verify the /users page renders the user analytics header strip."""
    admin_id = new_id()
    mock_admin = User(id=admin_id, display_name="مدیر کل", role=UserRole.SUPER_ADMIN)
    mock_admin._admin_permissions = {p.value for p in AdminPermission}

    mock_analytics = {
        "platform": {
            "total_users": 120,
            "telegram_users": 90,
            "bale_users": 40,
        },
        "categories": [
            {
                "key": "QURAN",
                "title": "قرآن کریم",
                "icon": "📖",
                "engaged_users": 70,
                "total_khatms": 15,
                "popularity_percent": 58.3,
                "is_top": True,
            }
        ],
        "top_category": {
            "title": "قرآن کریم",
            "popularity_percent": 58.3,
        },
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(COOKIE_NAME, "mock_admin_token")

        with patch("khatmsaz.web.app._admin", new=AsyncMock(return_value=(mock_admin, "mock_raw_token"))), \
             patch("khatmsaz.modules.reporting.service.get_system_user_analytics", new=AsyncMock(return_value=mock_analytics)), \
             patch("khatmsaz.modules.identity.service.search_users", new=AsyncMock(return_value=[])), \
             patch("khatmsaz.web.app.session_scope") as mock_scope:

            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session

            response = await client.get("/users")
            assert response.status_code == 200
            assert "تفکیک جامع کاربران و استقبال دسته‌ها" in response.text
            assert "قرآن کریم" in response.text


@pytest.mark.asyncio
async def test_admin_bot_user_analytics_handler():
    """Verify the admin bot handles admin:user_analytics callback."""
    from aiogram.types import CallbackQuery

    mock_event = MagicMock(spec=CallbackQuery)
    mock_event.message = MagicMock()
    mock_event.message.edit_text = AsyncMock()
    mock_event.answer = AsyncMock()

    mock_analytics = {
        "platform": {
            "total_users": 200,
            "active_users": 180,
            "telegram_users": 140,
            "bale_users": 70,
            "dual_platform_users": 10,
            "creators_count": 12,
            "super_admins_count": 3,
            "regular_users_count": 185,
        },
        "categories": [
            {
                "key": "QURAN",
                "title": "قرآن کریم",
                "icon": "📖",
                "engaged_users": 110,
                "total_khatms": 35,
                "popularity_percent": 55.0,
                "rank": 1,
                "is_top": True,
            },
            {
                "key": "LAAN",
                "title": "لعن و برائت",
                "icon": "🔥",
                "engaged_users": 40,
                "total_khatms": 12,
                "popularity_percent": 20.0,
                "rank": 2,
                "is_top": False,
            },
        ],
        "top_category": {
            "title": "قرآن کریم",
            "popularity_percent": 55.0,
        },
    }

    with patch.object(admin_bot_handlers, "_is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.modules.reporting.service.get_system_user_analytics", new=AsyncMock(return_value=mock_analytics)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope") as mock_scope:

        mock_scope.return_value.__aenter__.return_value = AsyncMock()
        await admin_bot_handlers.admin_user_analytics_handler(mock_event)

        assert mock_event.message.edit_text.called
        sent_text = mock_event.message.edit_text.call_args[0][0]
        assert "تحلیل جامع کاربران و تفکیک دسته‌ها" in sent_text
        assert "200" in sent_text
        assert "قرآن کریم" in sent_text
        assert "لعن و برائت" in sent_text
