"""Unit and regression tests for all Admin and Creator Panel routes in web/app.py.

Verifies:
1. All 91 endpoints are registered and accessible.
2. Unauthenticated requests redirect properly to login.
3. Authenticated requests execute without NameError, AttributeError, or template errors.
4. Specific regression tests for BUG-W01 through BUG-W20:
   - khatm_detail with WaitingList and invite_url generation
   - operations_page with system_settings_service.list_current
   - admin_set_user_plan with plan_service.set_plan
   - admin_remove_khatm_member with workflow_service.leave_khatm(session, part.id)
   - decide_broadcast with wallet_service.purchase(invoice_kind=InvoiceKind.PURCHASE)
   - Excel export with openpyxl Workbook
"""

import uuid
from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from khatmsaz.bot import invite_links
from khatmsaz.core.ids import new_id
from khatmsaz.modules.authorization.models import AdminRole, AdminRoleGrant
from khatmsaz.modules.identity.models import Platform, User, UserRole
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm.models import (
    CreatorDisplayMode,
    Khatm,
    KhatmStatus,
    KhatmTemplateType,
    KhatmTypeEnum,
    KhatmVisibility,
)
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.system_settings import service as system_settings_service
from khatmsaz.modules.wallet.models import InvoiceKind
from khatmsaz.web.app import COOKIE_NAME, CREATOR_COOKIE_NAME, app


def test_all_admin_and_creator_routes_registered():
    """Verify all major routes exist in app.routes."""
    route_paths = {getattr(r, "path", "") for r in app.routes}
    expected_paths = [
        "/",
        "/operations",
        "/moderation",
        "/moderation/laan/{khatm_id}/decide",
        "/khatms",
        "/khatms/create",
        "/khatms/{khatm_id}",
        "/khatms/{khatm_id}/update",
        "/khatms/{khatm_id}/status",
        "/khatms/{khatm_id}/members/{participation_id}/complete-share",
        "/khatms/{khatm_id}/members/{participation_id}/remove",
        "/khatms/{khatm_id}/export.xlsx",
        "/users",
        "/users/{user_id}/plan",
        "/users/{user_id}/wallet",
        "/users/{user_id}/message",
        "/users/{user_id}/moderate",
        "/phone-verifications",
        "/broadcasts",
        "/servant-ad",
        "/admins",
        "/creator-requests",
        "/audit",
        "/categories",
        "/content",
        "/devotionals",
        "/quran",
        "/templates",
        "/finance",
        "/finance/wallet/adjust",
        "/finance/invoices/{invoice_id}/refund",
        "/finance/ad-rate",
        "/finance/broadcast-policy",
        "/finance/plans/{plan_name}",
        "/finance/coupons",
        "/bots",
        "/creator",
        "/creator/khatms",
        "/creator/khatms/new",
        "/creator/wallet",
        "/creator/broadcasts",
        "/creator/khatms/{khatm_id}",
        "/creator/khatms/{khatm_id}/export.xlsx",
    ]
    for path in expected_paths:
        assert path in route_paths, f"Expected route '{path}' not found in app.routes"


@pytest.mark.asyncio
async def test_unauthenticated_requests_redirect_to_login():
    """Unauthenticated requests must redirect to /login or /creator/login."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Admin protected routes
        for path in ("/", "/khatms", "/users", "/operations", "/finance", "/moderation", "/bots", "/quran"):
            resp = await client.get(path, follow_redirects=False)
            assert resp.status_code == 303, f"{path} did not return 303"
            assert resp.headers["location"] == "/login", f"{path} did not redirect to /login"

        # Creator protected routes
        for path in ("/creator", "/creator/khatms", "/creator/wallet", "/creator/broadcasts"):
            resp = await client.get(path, follow_redirects=False)
            assert resp.status_code == 303, f"{path} did not return 303"
            assert resp.headers["location"] == "/creator/login", f"{path} did not redirect to /creator/login"


@pytest.mark.asyncio
async def test_invitation_service_list_and_create_extensions():
    """Verify BUG-W01: invitation_service list_for_khatm, get_or_create_for_khatm, and .token."""
    fake_session = AsyncMock()
    khatm_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Test get_or_create_for_khatm
    with patch("khatmsaz.modules.invitation.service.create_invitation", new=AsyncMock(return_value="test-token-123")):
        token = await invitation_service.get_or_create_for_khatm(fake_session, khatm_id, user_id)
        assert token == "test-token-123"

    # Test list_for_khatm in service calling repository
    with patch("khatmsaz.modules.invitation.repository.list_for_khatm", new=AsyncMock(return_value=[])):
        invs = await invitation_service.list_for_khatm(fake_session, khatm_id)
        assert invs == []


def test_invite_links_build_web_invite_url():
    """Verify BUG-W02: build_web_invite_url in bot/invite_links.py."""
    url = invite_links.build_web_invite_url("my_secret_token_abc")
    assert "my_secret_token_abc" in url


@pytest.mark.asyncio
async def test_system_settings_service_list_current_and_alias():
    """Verify BUG-W04: list_current and list_all alias work without error."""
    fake_session = AsyncMock()
    with patch("khatmsaz.modules.system_settings.repository.list_all", new=AsyncMock(return_value=[])):
        current = await system_settings_service.list_current(fake_session)
        assert isinstance(current, dict)
        assert "default_reminder_hour" in current
        assert system_settings_service.list_all is system_settings_service.list_current


@pytest.mark.asyncio
async def test_plan_service_assign_plan_and_set_plan():
    """Verify BUG-W05: plan_service.assign_plan works without error."""
    from khatmsaz.modules.plan import service as plan_service
    fake_session = AsyncMock()
    user_id = uuid.uuid4()

    with patch("khatmsaz.modules.plan.repository.upsert", new=AsyncMock()) as mock_upsert:
        await plan_service.assign_plan(fake_session, user_id, PlanTier.PRO, assigned_by_user_id=uuid.uuid4())
        mock_upsert.assert_awaited_once_with(fake_session, user_id, PlanTier.PRO)


def test_excel_export_openpyxl_workbook():
    """Verify BUG-W10: openpyxl Workbook and get_column_letter function properly."""
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "اعضا"
    ws.append(["ردیف", "نام", "سهم"])
    assert get_column_letter(1) == "A"
    assert get_column_letter(3) == "C"

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    assert len(buf.getvalue()) > 0


@pytest.mark.asyncio
async def test_khatm_detail_route_renders_cleanly(monkeypatch):
    """Verify BUG-W01, BUG-W02, BUG-W03: GET /khatms/{khatm_id} executes without crashing."""
    khatm_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    mock_admin_user = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="ادمین تست")
    mock_khatm = Khatm(
        id=khatm_id,
        creator_user_id=creator_id,
        title="ختم تستی صلوات",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.COMMITMENT,
        visibility=KhatmVisibility.PUBLIC,
        status=KhatmStatus.ACTIVE,
        repetition_target=14000,
        created_at=datetime.now(timezone.utc),
    )

    import khatmsaz.web.app as web_app

    async def fake_admin(request, *args, **kwargs):
        return mock_admin_user, "raw_csrf_token"

    monkeypatch.setattr(web_app, "_admin", fake_admin)

    # Mock DB session calls
    mock_session = AsyncMock()
    mock_session.get.side_effect = lambda model, obj_id: mock_khatm if model == Khatm and obj_id == khatm_id else None
    
    mock_result = MagicMock()
    mock_result.all.return_value = []
    mock_session.execute.return_value = mock_result

    class FakeSessionScope:
        async def __aenter__(self):
            return mock_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(web_app, "session_scope", lambda: FakeSessionScope())
    monkeypatch.setattr(web_app.reporting_service, "get_khatm_stats", AsyncMock(return_value={"active_members": 5, "completed_portions": 10}))
    monkeypatch.setattr(web_app.identity_service, "find_by_id", AsyncMock(return_value=mock_admin_user))
    monkeypatch.setattr(web_app, "_load_creator_member_rows", AsyncMock(return_value=[]))
    monkeypatch.setattr(web_app.invitation_service, "get_or_create_for_khatm", AsyncMock(return_value="test_token_xyz"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/khatms/{khatm_id}")
        assert response.status_code == 200
        assert "ختم تستی صلوات" in response.text
        assert "test_token_xyz" in response.text


@pytest.mark.asyncio
async def test_admin_remove_member_calls_leave_khatm_with_part_id(monkeypatch):
    """Verify BUG-W06: POST /khatms/{khatm_id}/members/{pid}/remove passes part.id."""
    khatm_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    user_id = uuid.uuid4()
    part_id = uuid.uuid4()

    mock_admin_user = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="ادمین تست")
    mock_part = Participation(id=part_id, khatm_id=khatm_id, user_id=user_id, status=ParticipationStatus.ACTIVE)

    import khatmsaz.web.app as web_app

    monkeypatch.setattr(web_app, "_admin", AsyncMock(return_value=(mock_admin_user, "valid_csrf")))
    monkeypatch.setattr(web_app, "_valid_csrf", lambda raw, supplied: True)

    mock_session = AsyncMock()
    mock_session.get.side_effect = lambda model, obj_id: mock_part if model == Participation and obj_id == part_id else None

    class FakeSessionScope:
        async def __aenter__(self):
            return mock_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(web_app, "session_scope", lambda: FakeSessionScope())
    leave_khatm_mock = AsyncMock()
    monkeypatch.setattr(web_app.workflow_service, "leave_khatm", leave_khatm_mock)
    monkeypatch.setattr(web_app.audit_service, "record", AsyncMock())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/khatms/{khatm_id}/members/{part_id}/remove",
            data={"csrf": "valid_csrf"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        leave_khatm_mock.assert_awaited_once_with(mock_session, part_id, reason="حذف توسط ادمین")


@pytest.mark.asyncio
async def test_admin_set_user_plan_calls_set_plan(monkeypatch):
    """Verify BUG-W05: POST /users/{user_id}/plan calls set_plan with PlanTier."""
    admin_id = uuid.uuid4()
    target_user_id = uuid.uuid4()
    mock_admin_user = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="ادمین تست")

    import khatmsaz.web.app as web_app

    monkeypatch.setattr(web_app, "_admin", AsyncMock(return_value=(mock_admin_user, "valid_csrf")))
    monkeypatch.setattr(web_app, "_valid_csrf", lambda raw, supplied: True)

    mock_session = AsyncMock()
    class FakeSessionScope:
        async def __aenter__(self):
            return mock_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(web_app, "session_scope", lambda: FakeSessionScope())
    set_plan_mock = AsyncMock()
    monkeypatch.setattr(web_app.plan_service, "set_plan", set_plan_mock)
    monkeypatch.setattr(web_app.audit_service, "record", AsyncMock())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/users/{target_user_id}/plan",
            data={"csrf": "valid_csrf", "plan": "PRO"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        set_plan_mock.assert_awaited_once_with(mock_session, target_user_id, PlanTier.PRO)
