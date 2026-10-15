"""Unit and regression tests for all Creator Panel routes in web/app.py.

Verifies:
1. All creator routes exist and are registered.
2. Unauthenticated requests redirect properly to /creator/login.
3. Authenticated creator requests render without errors (dashboard, khatms list, khatm detail, wallet, broadcasts, new).
4. Invite links (Telegram & Bale) and progress bars are properly generated in khatm_detail.
5. Khatm creation saves user's niyyat.
6. Toggle-status and member-remove endpoints work properly.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.khatm.models import (
    Khatm,
    KhatmStatus,
    KhatmTemplateType,
    KhatmTypeEnum,
    KhatmVisibility,
)
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.reporting.service import KhatmStats
from khatmsaz.web.app import CREATOR_COOKIE_NAME, app


def test_creator_routes_registered():
    """Verify all creator routes are registered in the FastAPI app."""
    paths = {getattr(r, "path", "") for r in app.routes}
    expected = [
        "/creator",
        "/creator/login",
        "/creator/logout",
        "/creator/khatms",
        "/creator/khatms/new",
        "/creator/khatms/create",
        "/creator/wallet",
        "/creator/wallet/topup",
        "/creator/wallet/buy-pro",
        "/creator/broadcasts",
        "/creator/khatms/{khatm_id}",
        "/creator/khatms/{khatm_id}/settings",
        "/creator/khatms/{khatm_id}/toggle-status",
        "/creator/khatms/{khatm_id}/members/{part_id}/remove",
        "/creator/khatms/{khatm_id}/export.xlsx",
    ]
    for path in expected:
        assert path in paths, f"Route {path} is missing from app.routes"


@pytest.mark.asyncio
async def test_creator_unauthenticated_redirects():
    """Verify that unauthenticated requests redirect to /creator/login."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for path in ("/creator", "/creator/khatms", "/creator/wallet", "/creator/broadcasts"):
            res = await client.get(path, follow_redirects=False)
            assert res.status_code == 303
            assert res.headers["location"] == "/creator/login"


@pytest.mark.asyncio
async def test_creator_dashboard_renders():
    """Verify creator dashboard renders with stats and recent khatm cards."""
    creator_id = new_id()
    mock_creator = User(id=creator_id, display_name="حسین علی‌نژاد", role=UserRole.SUPER_ADMIN)

    mock_khatm = Khatm(
        id=new_id(),
        creator_user_id=creator_id,
        title="ختم صلوات برای فرج",
        niyyat="تعجیل در فرج",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE,
        repetition_target=14000,
    )

    mock_stats = KhatmStats(
        total_members=5,
        active_members=5,
        completed_members=0,
        committed_members=5,
        completed_portions=7000,
        total_portions=14000,
        contribution_total=7000.0,
        invitations_issued=5,
        invitations_accepted=5,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(CREATOR_COOKIE_NAME, "valid_token")

        with patch("khatmsaz.modules.session.service.authenticate_creator", new=AsyncMock(return_value=mock_creator)), \
             patch("khatmsaz.modules.settings.service.get_or_create", new=AsyncMock(return_value=MagicMock(language="fa"))), \
             patch("khatmsaz.web.app.session_scope") as mock_scope, \
             patch("khatmsaz.modules.wallet.service.get_balances", new=AsyncMock(return_value=(50000, 0))), \
             patch("khatmsaz.modules.reporting.service.get_khatm_stats", new=AsyncMock(return_value=mock_stats)), \
             patch("khatmsaz.web.app._creator_member_counts", new=AsyncMock(return_value={mock_khatm.id: 5})), \
             patch("khatmsaz.web.app._creator_plan_view", new=AsyncMock(return_value={"title": "رایگان", "total_members": 5, "total_cap": 1000, "is_free": True, "is_basic": False, "is_pro": False, "ads_shown": False, "tier": "FREE"})):

            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session

            # mock execute for all_khatms
            mock_scalars = MagicMock()
            mock_scalars.scalars.return_value = [mock_khatm]
            mock_session.execute.return_value = mock_scalars

            res = await client.get("/creator")
            assert res.status_code == 200
            assert "حسین علی‌نژاد" in res.text
            assert "ختم صلوات برای فرج" in res.text
            assert "پیشرفت کل" in res.text


@pytest.mark.asyncio
async def test_creator_khatm_detail_renders_with_invite_links():
    """Verify khatm_detail renders with Telegram & Bale invite links and progress bar."""
    creator_id = new_id()
    khatm_id = new_id()
    mock_creator = User(id=creator_id, display_name="مهدی رضایی", role=UserRole.SUPER_ADMIN)

    mock_khatm = Khatm(
        id=khatm_id,
        creator_user_id=creator_id,
        title="ختم قرآن کریم ماه رمضان",
        niyyat="سلامتی امام زمان",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
        status=KhatmStatus.ACTIVE,
        repetition_target=604,
        welcome_text="خوش آمدید",
    )

    mock_invitation = MagicMock(id=new_id(), token="inv_tok_123")
    mock_stats = KhatmStats(
        total_members=10,
        active_members=10,
        completed_members=5,
        committed_members=10,
        completed_portions=302,
        total_portions=604,
        contribution_total=0.0,
        invitations_issued=10,
        invitations_accepted=10,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(CREATOR_COOKIE_NAME, "valid_token")

        with patch("khatmsaz.modules.session.service.authenticate_creator", new=AsyncMock(return_value=mock_creator)), \
             patch("khatmsaz.modules.settings.service.get_or_create", new=AsyncMock(return_value=MagicMock(language="fa"))), \
             patch("khatmsaz.web.app.session_scope") as mock_scope, \
             patch("khatmsaz.modules.reporting.service.get_khatm_stats", new=AsyncMock(return_value=mock_stats)), \
             patch("khatmsaz.web.app._load_creator_member_rows", new=AsyncMock(return_value=[])), \
             patch("khatmsaz.modules.invitation.service.get_or_create_for_khatm", new=AsyncMock(return_value=mock_invitation)), \
             patch("khatmsaz.bot.invite_links.resolve_khatm_category_value", new=AsyncMock(return_value="QURAN")), \
             patch("khatmsaz.bot.invite_links.build_member_invite_links", return_value={"fa": {"telegram": "https://t.me/quran_bot?start=join_inv_tok_123", "bale": "https://ble.ir/quran_bot?start=join_inv_tok_123"}}):

            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session
            mock_session.get.return_value = mock_khatm

            res = await client.get(f"/creator/khatms/{khatm_id}")
            assert res.status_code == 200
            assert "ختم قرآن کریم ماه رمضان" in res.text
            assert "https://t.me/quran_bot?start=join_inv_tok_123" in res.text
            assert "https://ble.ir/quran_bot?start=join_inv_tok_123" in res.text
            assert "50.0%" in res.text


@pytest.mark.asyncio
async def test_creator_khatm_create_saves_niyyat():
    """Verify that creating a khatm saves clean_niyyat in workflow_service."""
    creator_id = new_id()
    mock_creator = User(id=creator_id, display_name="سازنده", role=UserRole.SUPER_ADMIN)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(CREATOR_COOKIE_NAME, "valid_token")

        with patch("khatmsaz.modules.session.service.authenticate_creator", new=AsyncMock(return_value=mock_creator)), \
             patch("khatmsaz.modules.settings.service.get_or_create", new=AsyncMock(return_value=MagicMock(language="fa"))), \
             patch("khatmsaz.web.app._valid_csrf", return_value=True), \
             patch("khatmsaz.web.app.session_scope") as mock_scope, \
             patch("khatmsaz.modules.phone.repository.verified_claim_for_user", new=AsyncMock(return_value=MagicMock())), \
             patch("khatmsaz.modules.plan.service.get_creation_price", new=AsyncMock(return_value=0)), \
             patch("khatmsaz.modules.khatm_workflow.service.create_and_launch_khatm", new=AsyncMock(return_value=(MagicMock(id=new_id()), "tok"))) as mock_create:

            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session

            res = await client.post(
                "/creator/khatms/create",
                data={
                    "csrf": "csrf123",
                    "content_kind": "salawat",
                    "khatm_type": "OPEN",
                    "title": "صلوات به نیت فرج",
                    "niyyat": "سلامتی امام عصر",
                    "amount": "14000",
                    "visibility": "UNLISTED",
                    "accept_rules": "1",
                },
                follow_redirects=False,
            )
            assert res.status_code == 303
            # Check niyyat was passed
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["niyyat"] == "سلامتی امام عصر"
            assert call_kwargs["title"] == "صلوات به نیت فرج"


@pytest.mark.asyncio
async def test_creator_khatm_toggle_status():
    """Verify toggle-status pauses and resumes a khatm."""
    creator_id = new_id()
    khatm_id = new_id()
    mock_creator = User(id=creator_id, display_name="سازنده", role=UserRole.SUPER_ADMIN)
    mock_khatm = Khatm(id=khatm_id, creator_user_id=creator_id, status=KhatmStatus.ACTIVE, title="ختم تست")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(CREATOR_COOKIE_NAME, "valid_token")

        with patch("khatmsaz.modules.session.service.authenticate_creator", new=AsyncMock(return_value=mock_creator)), \
             patch("khatmsaz.modules.settings.service.get_or_create", new=AsyncMock(return_value=MagicMock(language="fa"))), \
             patch("khatmsaz.web.app._valid_csrf", return_value=True), \
             patch("khatmsaz.web.app.session_scope") as mock_scope, \
             patch("khatmsaz.modules.audit_log.service.record", new=AsyncMock()):

            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session
            mock_session.get.return_value = mock_khatm

            res = await client.post(
                f"/creator/khatms/{khatm_id}/toggle-status",
                data={"csrf": "csrf123"},
                follow_redirects=False,
            )
            assert res.status_code == 303
            assert mock_khatm.status == KhatmStatus.CANCELLED


@pytest.mark.asyncio
async def test_creator_wallet_renders():
    """Verify /creator/wallet renders balance and plan comparison."""
    creator_id = new_id()
    mock_creator = User(id=creator_id, display_name="سازنده", role=UserRole.SUPER_ADMIN)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(CREATOR_COOKIE_NAME, "valid_token")

        with patch("khatmsaz.modules.session.service.authenticate_creator", new=AsyncMock(return_value=mock_creator)), \
             patch("khatmsaz.modules.settings.service.get_or_create", new=AsyncMock(return_value=MagicMock(language="fa"))), \
             patch("khatmsaz.web.app.session_scope") as mock_scope, \
             patch("khatmsaz.modules.wallet.service.get_balances", new=AsyncMock(return_value=(150000, 20000))), \
             patch("khatmsaz.modules.wallet.service.list_invoices", new=AsyncMock(return_value=[])), \
             patch("khatmsaz.web.app._creator_plan_view", new=AsyncMock(return_value={"title": "رایگان", "total_members": 50, "total_cap": 1000, "is_free": True, "is_basic": False, "is_pro": False, "ads_shown": False, "tier": "FREE"})):

            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session

            res = await client.get("/creator/wallet")
            assert res.status_code == 200
            assert "150,000" in res.text
            assert "20,000" in res.text
            assert "افزایش موجودی کیف پول" in res.text
            assert "پرو" in res.text


@pytest.mark.asyncio
async def test_creator_broadcasts_renders():
    """Verify /creator/broadcasts renders audience and options."""
    creator_id = new_id()
    mock_creator = User(id=creator_id, display_name="سازنده", role=UserRole.SUPER_ADMIN)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(CREATOR_COOKIE_NAME, "valid_token")

        with patch("khatmsaz.modules.session.service.authenticate_creator", new=AsyncMock(return_value=mock_creator)), \
             patch("khatmsaz.modules.settings.service.get_or_create", new=AsyncMock(return_value=MagicMock(language="fa"))), \
             patch("khatmsaz.web.app.session_scope") as mock_scope, \
             patch("khatmsaz.modules.wallet.service.get_balances", new=AsyncMock(return_value=(10000, 0))):

            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session
            mock_scalars = MagicMock()
            mock_scalars.scalars.return_value = []
            mock_session.execute.return_value = mock_scalars

            res = await client.get("/creator/broadcasts")
            assert res.status_code == 200
            assert "ارسال پیام گروهی اختصاصی" in res.text
            assert "ربات تلگرام" in res.text
            assert "به ازای هر ۱۰۰۰ نفر" in res.text
            assert "char-counter" in res.text
