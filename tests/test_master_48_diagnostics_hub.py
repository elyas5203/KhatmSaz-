"""Unit and integration tests for MASTER-48: Bot Fleet Diagnostics & Real-Time System Health Hub."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from starlette.testclient import TestClient

from khatmsaz.modules.authorization.models import AdminRole, AdminRoleGrant
from khatmsaz.modules.bot_registry.models import BotInstance, BotRole
from khatmsaz.modules.identity.models import User
from khatmsaz.web.app import app


@pytest.fixture
def mock_admin():
    admin = MagicMock(spec=User)
    admin.id = uuid.uuid4()
    admin.display_name = "Super Admin"
    admin.is_active = True
    return admin


@pytest.fixture
def mock_admin_grant(mock_admin):
    grant = MagicMock(spec=AdminRoleGrant)
    grant.user_id = mock_admin.id
    grant.role = AdminRole.ADMIN
    grant.revoked_at = None
    return grant


@pytest.fixture
def sample_bot_instance():
    inst = MagicMock(spec=BotInstance)
    inst.id = uuid.uuid4()
    inst.platform = "TELEGRAM"
    inst.bot_role = BotRole.MEMBER
    inst.category = "QURAN"
    inst.language = "fa"
    inst.display_name = "بات قرآن فارسی"
    inst.username = "KhatmQuranFA_bot"
    inst.token_encrypted = "mock_encrypted_token"
    inst.is_active = True
    return inst


def test_operations_page_unauthenticated():
    """Unauthenticated access to /operations redirects to /login."""
    client = TestClient(app, follow_redirects=False)
    response = client.get("/operations")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_operations_page_authenticated(mock_admin, mock_admin_grant, sample_bot_instance):
    """Authenticated admin can load /operations with Bot Fleet and Diagnostics."""
    client = TestClient(app)

    async def fake_admin(request, *args, **kwargs):
        return mock_admin, "raw_cookie"

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock()
    mock_session.scalar.return_value = 0

    fake_scope = MagicMock()
    fake_scope.__aenter__.return_value = mock_session
    fake_scope.__aexit__.return_value = None

    with patch("khatmsaz.web.app._admin", side_effect=fake_admin), \
         patch("khatmsaz.web.app.session_scope", return_value=fake_scope), \
         patch("khatmsaz.web.app.bot_registry_service.list_all_instances", AsyncMock(return_value=[sample_bot_instance])):
        response = client.get("/operations")
        assert response.status_code == 200
        html = response.text
        assert "مرکز عملیات، پایش ناوگان و سلامت زیرساخت" in html
        assert "ناوگان ۱۸ ربات تلگرام و بله" in html
        assert "کنسول خطایابی و لاگ‌های زندهٔ سیستم" in html
        assert "اجرای دستی اسکن یادآوری‌ها" in html
        assert "تست دسته‌جمعی ناوگان ربات‌ها" in html
        assert "بات قرآن فارسی" in html


def test_ping_single_bot_success(mock_admin, mock_admin_grant, sample_bot_instance):
    """POST /operations/bots/{id}/ping calls ping_bot_instance and returns JSON."""
    client = TestClient(app)

    async def fake_admin(request, *args, **kwargs):
        return mock_admin, "raw_cookie"

    bot_id = sample_bot_instance.id
    mock_result = {
        "ok": True,
        "latency_ms": 142,
        "username": "KhatmQuranFA_bot",
        "display_name": "بات قرآن فارسی",
        "bot_id": 99887766,
        "error": None,
    }

    with patch("khatmsaz.web.app._admin", side_effect=fake_admin), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.bot_registry_service.get_instance", AsyncMock(return_value=sample_bot_instance)), \
         patch("khatmsaz.web.app.bot_registry_service.ping_bot_instance", AsyncMock(return_value=mock_result)):
        
        response = client.post(
            f"/operations/bots/{bot_id}/ping",
            headers={"x-csrf-token": "valid_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["latency_ms"] == 142
        assert data["username"] == "KhatmQuranFA_bot"


def test_ping_single_bot_not_found(mock_admin, mock_admin_grant):
    """POST /operations/bots/{id}/ping for non-existent bot returns 404."""
    client = TestClient(app)

    async def fake_admin(request, *args, **kwargs):
        return mock_admin, "raw_cookie"

    with patch("khatmsaz.web.app._admin", side_effect=fake_admin), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.bot_registry_service.get_instance", AsyncMock(return_value=None)):
        
        random_id = uuid.uuid4()
        response = client.post(
            f"/operations/bots/{random_id}/ping",
            headers={"x-csrf-token": "valid_token"},
        )
        assert response.status_code == 404
        assert response.json()["ok"] is False


def test_ping_all_bots(mock_admin, mock_admin_grant, sample_bot_instance):
    """POST /operations/bots/ping-all calls ping_all_instances and returns JSON array."""
    client = TestClient(app)

    async def fake_admin(request, *args, **kwargs):
        return mock_admin, "raw_cookie"

    mock_results = [
        {
            "id": str(sample_bot_instance.id),
            "name": "بات قرآن فارسی",
            "platform": "TELEGRAM",
            "ok": True,
            "latency_ms": 115,
            "username": "KhatmQuranFA_bot",
        }
    ]

    with patch("khatmsaz.web.app._admin", side_effect=fake_admin), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.bot_registry_service.ping_all_instances", AsyncMock(return_value=mock_results)):
        
        response = client.post(
            "/operations/bots/ping-all",
            headers={"x-csrf-token": "valid_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert len(data["results"]) == 1
        assert data["results"][0]["latency_ms"] == 115


def test_trigger_manual_scan_authenticated(mock_admin, mock_admin_grant):
    """POST /operations/trigger-scan executes run_once and records audit log."""
    client = TestClient(app)

    async def fake_admin(request, *args, **kwargs):
        return mock_admin, "raw_cookie"

    with patch("khatmsaz.web.app._admin", side_effect=fake_admin), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.modules.reminder_engine.service.run_once", AsyncMock()) as mock_run_once, \
         patch("khatmsaz.web.app.audit_service.record", AsyncMock()) as mock_audit:
        
        response = client.post(
            "/operations/trigger-scan",
            headers={"x-csrf-token": "valid_token", "accept": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "اسکن یادآوری‌ها" in data["message"]
        mock_run_once.assert_awaited_once()
        mock_audit.assert_awaited_once()


def test_logs_tail_endpoint(mock_admin, mock_admin_grant):
    """GET /operations/logs/tail returns last error log lines in JSON."""
    client = TestClient(app)

    async def fake_admin(request, *args, **kwargs):
        return mock_admin, "raw_cookie"

    fake_lines = [
        "2026-10-19 12:00:00 [INFO] KhatmSaz starting...",
        "2026-10-19 12:05:00 [ERROR] Sample test error occurred",
    ]

    with patch("khatmsaz.web.app._admin", side_effect=fake_admin), \
         patch("khatmsaz.web.app._read_recent_errors", return_value=fake_lines):
        
        response = client.get("/operations/logs/tail?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["count"] == 2
        assert "Sample test error occurred" in data["lines"][1]


def test_logs_download_endpoint(mock_admin, mock_admin_grant, tmp_path):
    """GET /operations/logs/download returns FileResponse when log file exists."""
    client = TestClient(app)

    async def fake_admin(request, *args, **kwargs):
        return mock_admin, "raw_cookie"

    temp_log = tmp_path / "errors.log"
    temp_log.write_text("Test error log content", encoding="utf-8")

    with patch("khatmsaz.web.app._admin", side_effect=fake_admin), \
         patch("khatmsaz.web.app.Path", return_value=temp_log):
        
        response = client.get("/operations/logs/download")
        assert response.status_code == 200
        assert "Test error log content" in response.text
