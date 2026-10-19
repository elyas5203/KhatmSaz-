"""Unit and integration tests for MASTER-50: Admins, Roles, Permissions (RBAC) & Security Audit Hub."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Request
from starlette.testclient import TestClient

from khatmsaz.modules.authorization.models import AdminRole, AdminRoleGrant
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.web.app import (
    app,
    admins,
    change_admin_role,
    promote_super_admin,
    demote_super_admin,
    audit_timeline,
)


def test_admins_template_structure():
    """Verify that admins.html template contains all MASTER-50 required UI elements, KPIs and tabs."""
    with open("src/khatmsaz/web/templates/admins.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Header and Help
    assert "مدیران، نقش‌ها و ردپای امنیتی" in content
    assert "help_button" in content

    # 4 Security KPI Cards
    assert "کل مدیران فعال سیستم" in content
    assert "مدیران ارشد (Super Admin)" in content
    assert "کل رویدادهای ممیزی ثبت‌شده" in content
    assert "رویدادهای امنیتی ۲۴ ساعت اخیر" in content

    # 3 Unified Tabs
    assert 'id="tabBtn_active"' in content
    assert 'id="tabBtn_grant"' in content
    assert 'id="tabBtn_audit"' in content

    # Super Admins & Delegated Admins Sections
    assert "مدیران ارشد سامانه (Super Admins)" in content
    assert "مدیران تفویض‌شده و سطوح دسترسی" in content

    # Grant & Audit Sections
    assert "جستجوی کاربر و اعطای نقش مدیریتی" in content
    assert "دفتر کل ممیزی و رویدادهای امنیتی" in content
    assert 'name="action_query"' in content
    assert 'name="time_range"' in content


def test_admins_page_unauthenticated():
    """Unauthenticated access to /admins must redirect to /login."""
    client = TestClient(app, follow_redirects=False)
    response = client.get("/admins")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


@pytest.mark.asyncio
async def test_admins_page_authenticated():
    """Authenticated admin can load /admins and receive full context and KPIs."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN
    admin_user.display_name = "Super Admin"

    audit_entry = MagicMock()
    audit_entry.actor_user_id = admin_user.id
    audit_entry.target_user_id = None
    audit_entry.target_khatm_id = None
    audit_entry.action = "WEB_ADMIN_ROLE_GRANTED"
    audit_entry.created_at = None
    audit_entry.details = {}

    res_grants = MagicMock(all=MagicMock(return_value=[]), scalars=MagicMock(return_value=[]))
    res_supers = MagicMock(all=MagicMock(return_value=[]), scalars=MagicMock(return_value=[admin_user]))
    res_audit = MagicMock(all=MagicMock(return_value=[]), scalars=MagicMock(return_value=[audit_entry]))
    res_users = MagicMock(all=MagicMock(return_value=[]), scalars=MagicMock(return_value=[admin_user]))
    res_khatms = MagicMock(all=MagicMock(return_value=[]), scalars=MagicMock(return_value=[]))

    dummy_session = AsyncMock()
    dummy_session.execute.side_effect = [res_grants, res_supers, res_audit, res_users, res_khatms]
    dummy_session.scalar.return_value = 10

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()
    req.query_params = {}

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.identity.service.search_users", AsyncMock(return_value=[])):

        resp = await admins(request=req)
        assert resp.status_code == 200
        html = resp.body.decode("utf-8")
        assert "مدیران، نقش‌ها و ردپای امنیتی" in html
        assert "کل مدیران فعال سیستم" in html


@pytest.mark.asyncio
async def test_admins_page_with_filters():
    """Testing /admins with tab=audit, time_range and action_query filters."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

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
    req.query_params = {"tab": "audit", "time_range": "today", "action_query": "ROLE"}

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.identity.service.search_users", AsyncMock(return_value=[])):

        resp = await admins(request=req, tab="audit", time_range="today", action_query="ROLE")
        assert resp.status_code == 200
        assert dummy_session.execute.called


@pytest.mark.asyncio
async def test_grant_admin_role():
    """Testing granting a delegated admin role to a target user."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    target_user = MagicMock(spec=User)
    target_user.id = uuid4()

    dummy_session = AsyncMock()
    dummy_session.scalars.return_value = MagicMock(all=MagicMock(return_value=[]))
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.identity.service.find_by_id", AsyncMock(side_effect=[admin_user, target_user])), \
         patch("khatmsaz.modules.authorization.service.grant_role", AsyncMock()) as mock_grant, \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await change_admin_role(
            request=req,
            user_id=target_user.id,
            csrf="mock_cookie",
            role="FINANCE_ADMIN",
            action="grant",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == "/admins?tab=grant&saved=1"

        mock_grant.assert_awaited_once_with(
            dummy_session,
            actor=admin_user,
            target=target_user,
            role=AdminRole.FINANCE_ADMIN,
        )
        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "WEB_ADMIN_ROLE_GRANTED"


@pytest.mark.asyncio
async def test_revoke_admin_role_self_lockout_prevented():
    """An admin cannot revoke roles from their own account (Anti Self-Lockout guard)."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True):

        # Attempt to revoke own role
        resp = await change_admin_role(
            request=req,
            user_id=admin_user.id,
            csrf="mock_cookie",
            role="FINANCE_ADMIN",
            action="revoke",
        )

        assert resp.status_code == 400
        assert "Anti Self-Lockout" in resp.body.decode("utf-8")


@pytest.mark.asyncio
async def test_promote_super_admin():
    """Testing promoting an active user to SUPER_ADMIN."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    target_user = MagicMock(spec=User)
    target_user.id = uuid4()
    target_user.role = UserRole.USER

    dummy_session = AsyncMock()
    dummy_session.scalars.return_value = MagicMock(all=MagicMock(return_value=[]))
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.identity.service.find_by_id", AsyncMock(return_value=target_user)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await promote_super_admin(
            request=req,
            user_id=target_user.id,
            csrf="mock_cookie",
        )

        assert resp.status_code == 303
        assert resp.headers["location"] == "/admins?tab=active&saved=super_promoted"
        assert target_user.role == UserRole.SUPER_ADMIN
        mock_audit.assert_awaited_once()
        assert mock_audit.await_args[1]["action"] == "SUPER_ADMIN_PROMOTED"


@pytest.mark.asyncio
async def test_demote_super_admin_last_super_guard():
    """Cannot demote the last super admin remaining in the system."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    target_user = MagicMock(spec=User)
    target_user.id = uuid4()

    dummy_session = AsyncMock()
    # Mock only 1 super admin count
    dummy_session.scalar.return_value = 1
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope):

        resp = await demote_super_admin(
            request=req,
            user_id=target_user.id,
            csrf="mock_cookie",
        )

        assert resp.status_code == 400
        assert "آخرین مدیر ارشد" in resp.body.decode("utf-8")


@pytest.mark.asyncio
async def test_demote_super_admin_self_lockout():
    """A super admin cannot demote themselves directly."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    req = MagicMock(spec=Request)
    req.state = MagicMock()

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True):

        resp = await demote_super_admin(
            request=req,
            user_id=admin_user.id,
            csrf="mock_cookie",
        )

        assert resp.status_code == 400
        assert "Anti Self-Lockout" in resp.body.decode("utf-8")


@pytest.mark.asyncio
async def test_audit_route_redirect():
    """GET /audit redirects to /admins?tab=audit with query params."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    req = MagicMock(spec=Request)

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))):
        resp = await audit_timeline(request=req, q="WALLET", time_range="7d")
        assert resp.status_code == 303
        assert "/admins?tab=audit&action_query=WALLET&time_range=7d" in resp.headers["location"]
