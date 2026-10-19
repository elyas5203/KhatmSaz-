"""Unit and integration tests for MASTER-53: Bot Fleet Management & Intro Images Hub.

Tests cover:
- Unauthenticated access redirect to /login
- Authenticated view of /bots across all 4 tabs (telegram, bale, intro_images, guide)
- Verification of 4 fleet KPI cards (Total slots, Configured bots, Active bots, Service restart status)
- Protection of Creator Bot tokens from web admin edit
- Confirmation name validation on Member Bot token save
- Bot token save and encryption
- Bot active/inactive status toggle
- Family intro images update via URL and direct multipart file upload
"""

from contextlib import asynccontextmanager
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi import UploadFile

from khatmsaz.web.app import (
    bots_page,
    save_bot_token,
    save_family_intro_images,
    toggle_bot_instance,
)


@pytest.fixture
def mock_admin():
    return SimpleNamespace(
        id=uuid.uuid4(),
        display_name="مدیر عملیات",
        is_super_admin=True,
        _admin_permissions={"OPERATIONS_VIEW"},
    )


@pytest.fixture
def sample_bot_instances():
    creator_id = uuid.uuid4()
    member1_id = uuid.uuid4()
    member2_id = uuid.uuid4()
    return [
        SimpleNamespace(
            id=creator_id,
            platform="TELEGRAM",
            bot_role="CREATOR",
            category=None,
            language=None,
            display_name="ختم‌ساز تلگرام",
            username="Khatm_Saz_bot",
            token_encrypted="encrypted-creator-token",
            is_active=True,
            updated_at=None,
        ),
        SimpleNamespace(
            id=member1_id,
            platform="TELEGRAM",
            bot_role="MEMBER",
            category="quran",
            language="fa",
            display_name="ختم قرآن تلگرام",
            username="quran_khatm_fa_bot",
            token_encrypted="encrypted-member-token",
            is_active=True,
            updated_at=None,
        ),
        SimpleNamespace(
            id=member2_id,
            platform="BALE",
            bot_role="MEMBER",
            category="salawat",
            language="fa",
            display_name="ختم صلوات بله",
            username="salawat_khatm_fa_bot",
            token_encrypted="",
            is_active=False,
            updated_at=None,
        ),
    ]


def _make_request(path: str = "/bots", query_string: bytes = b"", query_params: dict | None = None) -> Request:
    req = Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": query_string,
        }
    )
    if query_params:
        req._query_params = query_params
    return req


# -----------------------------------------------------------------------------
# 1. Access Control Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_bots_page_unauthenticated_redirect(monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(None, None)))
    req = _make_request("/bots")
    resp = await bots_page(req)
    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


# -----------------------------------------------------------------------------
# 2. Authenticated Hub Tabs & 4 KPIs Rendering
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_bots_page_authenticated_telegram_tab(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.list_all_instances", AsyncMock(return_value=sample_bot_instances))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_str", AsyncMock(return_value=""))

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/bots", query_string=b"tab=telegram")

    resp = await bots_page(req, platform="TELEGRAM", tab="telegram")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    # Header and KPIs
    assert "مرکز جامع مدیریت ناوگان ربات‌ها و تصاویر معرفی" in html
    assert "MASTER-53" in html
    assert "کل اسلات‌های ناوگان" in html
    assert "دارای توکن متصل" in html
    assert "فعال در چرخه خدمت" in html
    assert "وضعیت ری‌استارت سرویس" in html

    # Tab content
    assert "ناوگان ربات‌های تلگرام (Telegram)" in html
    assert "ختم‌ساز تلگرام" in html
    assert "ختم قرآن تلگرام" in html


@pytest.mark.asyncio
async def test_bots_page_authenticated_bale_tab(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.list_all_instances", AsyncMock(return_value=sample_bot_instances))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_str", AsyncMock(return_value=""))

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/bots", query_string=b"tab=bale")

    resp = await bots_page(req, platform="BALE", tab="bale")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "ناوگان ربات‌های بله (Bale)" in html
    assert "ختم صلوات بله" in html


@pytest.mark.asyncio
async def test_bots_page_authenticated_intro_images_tab(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.list_all_instances", AsyncMock(return_value=sample_bot_instances))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_str", AsyncMock(return_value="https://example.com/quran.jpg"))

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/bots", query_string=b"tab=intro_images")

    resp = await bots_page(req, tab="intro_images")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "تصاویر معرفی ۵ خانواده ختم" in html
    assert "۱. ختم قرآن کریم" in html
    assert "۲. ختم صلوات" in html
    assert "۳. ادعیه و زیارات" in html
    assert "۴. اذکار لعن و برائت" in html
    assert "۵. خطبه‌های مقدس" in html


@pytest.mark.asyncio
async def test_bots_page_authenticated_guide_tab(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.list_all_instances", AsyncMock(return_value=sample_bot_instances))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_str", AsyncMock(return_value=""))

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/bots", query_string=b"tab=guide")

    resp = await bots_page(req, tab="guide")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "راهنمای جامع اتصال و ساخت ربات‌ها (BotFather)" in html
    assert "راه‌اندازی در تلگرام (Telegram)" in html
    assert "راه‌اندازی در پیام‌رسان بله (Bale)" in html
    assert "/newbot" in html
    assert "/setprivacy" in html


# -----------------------------------------------------------------------------
# 3. Bot Token Save & Guards
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_save_bot_token_blocks_creator_bot(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    creator_bot = sample_bot_instances[0]
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.get_instance", AsyncMock(return_value=creator_bot))

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request(f"/bots/{creator_bot.id}/token")

    resp = await save_bot_token(
        request=req,
        instance_id=creator_bot.id,
        csrf="valid-csrf",
        token="123456:FAKE-TOKEN",
        username="new_username",
        confirm_name=creator_bot.display_name,
        tab="telegram",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]


@pytest.mark.asyncio
async def test_save_bot_token_requires_confirm_name(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    member_bot = sample_bot_instances[1]
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.get_instance", AsyncMock(return_value=member_bot))

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request(f"/bots/{member_bot.id}/token")

    resp = await save_bot_token(
        request=req,
        instance_id=member_bot.id,
        csrf="valid-csrf",
        token="123456:NEW-TOKEN",
        username="quran_new_bot",
        confirm_name="نام اشتباه",
        tab="telegram",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]


@pytest.mark.asyncio
async def test_save_bot_token_success(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    member_bot = sample_bot_instances[1]
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.get_instance", AsyncMock(return_value=member_bot))
    mock_set_token = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.set_bot_token", mock_set_token)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request(f"/bots/{member_bot.id}/token")

    resp = await save_bot_token(
        request=req,
        instance_id=member_bot.id,
        csrf="valid-csrf",
        token="123456:VALID-TOKEN",
        username="quran_khatm_fa_bot",
        confirm_name=member_bot.display_name,
        tab="telegram",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "/bots?tab=telegram&platform=TELEGRAM&saved=token_saved" in resp.headers["location"]
    mock_set_token.assert_called_once_with(
        mock_session, member_bot.id, "123456:VALID-TOKEN", "quran_khatm_fa_bot"
    )


# -----------------------------------------------------------------------------
# 4. Bot Active Toggle Action
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_toggle_bot_instance_success(mock_admin, sample_bot_instances, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    member_bot = sample_bot_instances[1]
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.get_instance", AsyncMock(return_value=member_bot))
    mock_toggle = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.bot_registry.service.toggle_bot_active", mock_toggle)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request(f"/bots/{member_bot.id}/toggle")

    resp = await toggle_bot_instance(
        request=req,
        instance_id=member_bot.id,
        csrf="valid-csrf",
        tab="telegram",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "/bots?tab=telegram&platform=TELEGRAM&saved=toggled" in resp.headers["location"]
    mock_toggle.assert_called_once_with(mock_session, member_bot.id, False)


# -----------------------------------------------------------------------------
# 5. Family Intro Images Update & Direct File Upload
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_save_family_intro_images_with_url_and_direct_file(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    mock_set_str = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.set_str", mock_set_str)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    mock_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)

    # Fake upload for Quran intro image
    file_bytes = b"fake image content"
    upload_quran = UploadFile(filename="quran_intro.jpg", file=BytesIO(file_bytes))

    req = _make_request("/bots/family-intro-images")
    resp = await save_family_intro_images(
        request=req,
        csrf="valid-csrf",
        tab="intro_images",
        quran="",
        salawat="https://example.com/salawat.jpg",
        dua_ziyarat="",
        laan="",
        khutbah="",
        file_quran=upload_quran,
        file_salawat=None,
        file_dua_ziyarat=None,
        file_laan=None,
        file_khutbah=None,
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "/bots?tab=intro_images&saved=family_images" in resp.headers["location"]

    # Verify set_str calls
    calls = {call[0][1]: call[0][2] for call in mock_set_str.call_args_list}
    assert "intro_image_quran" in calls
    assert calls["intro_image_quran"].startswith("/static/uploads/intro/")
    assert "quran_intro.jpg" in calls["intro_image_quran"]
    assert calls["intro_image_salawat"] == "https://example.com/salawat.jpg"
