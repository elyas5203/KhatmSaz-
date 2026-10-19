"""Unit and integration tests for MASTER-52: Quran Bank, Reciters & Media Studio.

Tests cover:
- Unauthenticated access redirect to /login
- Authenticated view of /quran across all 4 tabs (inspector, coverage, reciters, sync)
- Verification of 4 coverage KPI cards (Telegram Images, Telegram Audio, Bale Images, Bale Audio)
- Page navigation and page asset listing in Inspector tab
- 604-page matrix and status filtering in Coverage tab
- Reciters metadata and audio counts in Reciters tab
- Registration of Quran page asset via remote file ID
- Conversion of Telegram channel message link (t.me/...) to tg_forward ref
- Registration of Quran page asset via direct multipart file upload
- Deletion of Quran page asset
- Seed channel map execution
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

from khatmsaz.modules.content.models import QuranAssetKind, QuranPageAsset
from khatmsaz.web.app import (
    delete_quran_asset,
    quran_bank_page,
    save_quran_asset,
    seed_quran_channel,
)


@pytest.fixture
def mock_admin():
    return SimpleNamespace(
        id=uuid.uuid4(),
        display_name="مدیر سامانه",
        is_super_admin=True,
        _admin_permissions={"CONTENT_MANAGE"},
    )


@pytest.fixture
def sample_quran_assets():
    return [
        SimpleNamespace(
            id=uuid.uuid4(),
            edition_id="madani_604",
            page_number=1,
            kind="IMAGE",
            reciter_id="",
            asset_ref="tg_img_page_1",
            asset_platform="TELEGRAM",
            channel_post_id=1,
            created_at=None,
        ),
        SimpleNamespace(
            id=uuid.uuid4(),
            edition_id="madani_604",
            page_number=1,
            kind="AUDIO",
            reciter_id="parhizgar",
            asset_ref="tg_audio_page_1",
            asset_platform="TELEGRAM",
            channel_post_id=2,
            created_at=None,
        ),
        SimpleNamespace(
            id=uuid.uuid4(),
            edition_id="madani_604",
            page_number=1,
            kind="IMAGE",
            reciter_id="",
            asset_ref="bale_img_page_1",
            asset_platform="BALE",
            channel_post_id=None,
            created_at=None,
        ),
        SimpleNamespace(
            id=uuid.uuid4(),
            edition_id="madani_604",
            page_number=1,
            kind="AUDIO",
            reciter_id="parhizgar",
            asset_ref="bale_audio_page_1",
            asset_platform="BALE",
            channel_post_id=None,
            created_at=None,
        ),
    ]


def _make_request(path: str = "/quran", query_string: bytes = b"", query_params: dict | None = None) -> Request:
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
async def test_quran_page_unauthenticated_redirect(monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(None, None)))
    req = _make_request("/quran")
    resp = await quran_bank_page(req)
    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


# -----------------------------------------------------------------------------
# 2. Authenticated Studio Tabs Rendering
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quran_page_authenticated_inspector_tab(mock_admin, sample_quran_assets, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=sample_quran_assets)
    )

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/quran", query_string=b"tab=inspector&page_num=1")

    resp = await quran_bank_page(req, page_num=1, tab="inspector")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    # Studio title and help button
    assert "استودیو و بانک جامع ۶۰۴ صفحه قرآن کریم" in html
    assert "MASTER-52" in html
    assert "بازرس صفحه" in html
    assert "از ۶۰۴" in html
    assert "تصاویر تلگرام" in html
    assert "صوت‌های تلگرام" in html
    assert "تصاویر بله" in html
    assert "صوت‌های بله" in html
    assert "tg_img_page_1" in html


@pytest.mark.asyncio
async def test_quran_page_coverage_matrix_tab(mock_admin, sample_quran_assets, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=sample_quran_assets)
    )

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/quran", query_string=b"tab=coverage&filter_status=all")

    resp = await quran_bank_page(req, tab="coverage", filter_status="all")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "ماتریس پوشش ۶۰۴ صفحه قرآن کریم" in html
    assert "همه صفحات (۶۰۴)" in html
    assert "کامل (هر ۴ فایل)" in html
    assert "راهنمای نشانگرها" in html


@pytest.mark.asyncio
async def test_quran_page_reciters_tab(mock_admin, sample_quran_assets, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=sample_quran_assets)
    )

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/quran", query_string=b"tab=reciters")

    resp = await quran_bank_page(req, tab="reciters")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "مدیریت قاریان و بسته‌های صوتی ترتیل" in html
    assert "شهریار پرهیزگار" in html
    assert "محمد صدیق منشاوی" in html
    assert "عبدالباسط عبدالصمد" in html
    assert "محمود خلیل حصری" in html


@pytest.mark.asyncio
async def test_quran_page_sync_tools_tab(mock_admin, sample_quran_assets, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))

    mock_session = AsyncMock()
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=sample_quran_assets)
    )

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    req = _make_request("/quran", query_string=b"tab=sync")

    resp = await quran_bank_page(req, tab="sync")
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    html = resp.body.decode("utf-8")

    assert "ابزارهای خودکارسازی، بذر کانال و همگام‌سازی" in html
    assert 'action="/quran/seed-channel"' in html
    assert "پایپ‌لاین انتقال رسانه به بله" in html


# -----------------------------------------------------------------------------
# 3. Asset Save, Link Parsing & Direct File Upload
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quran_asset_save_with_remote_file_id(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    mock_register = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.content.service.register_quran_page_asset", mock_register)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    req = _make_request("/quran/asset/save")
    resp = await save_quran_asset(
        request=req,
        csrf="valid-csrf",
        page_number=5,
        kind="IMAGE",
        platform="TELEGRAM",
        asset_platform="TELEGRAM",
        reciter_id="",
        asset_ref="",
        remote_file_id="BQACAgQAAxkBAAE...",
        channel_post_id="105",
        tab="inspector",
        file=None,
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "/quran?page_num=5&tab=inspector&saved=asset_saved" in resp.headers["location"]
    assert mock_register.call_count == 1
    call_kwargs = mock_register.call_args[1]
    assert call_kwargs["page_number"] == 5
    assert call_kwargs["kind"] == "IMAGE"
    assert call_kwargs["asset_ref"] == "BQACAgQAAxkBAAE..."
    assert call_kwargs["asset_platform"] == "TELEGRAM"


@pytest.mark.asyncio
async def test_quran_asset_save_normalizes_telegram_channel_url(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    mock_register = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.content.service.register_quran_page_asset", mock_register)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    req = _make_request("/quran/asset/save")
    resp = await save_quran_asset(
        request=req,
        csrf="valid-csrf",
        page_number=10,
        kind="AUDIO",
        platform="TELEGRAM",
        asset_platform="TELEGRAM",
        reciter_id="parhizgar",
        asset_ref="https://t.me/quran_channel_official/2048",
        remote_file_id="",
        channel_post_id="",
        tab="inspector",
        file=None,
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    call_kwargs = mock_register.call_args[1]
    assert call_kwargs["page_number"] == 10
    assert call_kwargs["kind"] == "AUDIO"
    assert call_kwargs["reciter_id"] == "parhizgar"
    assert call_kwargs["asset_ref"] == "tg_forward:@quran_channel_official:2048"


@pytest.mark.asyncio
async def test_quran_asset_save_direct_file_upload(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    mock_register = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.content.service.register_quran_page_asset", mock_register)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    # Create dummy upload file
    file_bytes = b"fake audio mp3 content for page 1"
    upload = UploadFile(filename="page001.mp3", file=BytesIO(file_bytes))

    req = _make_request("/quran/asset/save")
    resp = await save_quran_asset(
        request=req,
        csrf="valid-csrf",
        page_number=1,
        kind="AUDIO",
        platform="TELEGRAM",
        asset_platform="TELEGRAM",
        reciter_id="parhizgar",
        asset_ref="",
        remote_file_id="",
        channel_post_id="",
        tab="inspector",
        file=upload,
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    call_kwargs = mock_register.call_args[1]
    assert call_kwargs["page_number"] == 1
    assert call_kwargs["kind"] == "AUDIO"
    assert call_kwargs["asset_ref"].startswith("/static/uploads/quran/")
    assert "page001.mp3" in call_kwargs["asset_ref"]


# -----------------------------------------------------------------------------
# 4. Asset Delete Action Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quran_asset_delete(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)

    asset_id = uuid.uuid4()
    dummy_asset = SimpleNamespace(
        id=asset_id,
        page_number=42,
        kind=QuranAssetKind.IMAGE,
        asset_platform="TELEGRAM",
        reciter_id="",
    )

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=dummy_asset)
    mock_session.delete = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield mock_session

    monkeypatch.setattr("khatmsaz.web.app.session_scope", mock_scope)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    req = _make_request(f"/quran/asset/{asset_id}/delete")
    resp = await delete_quran_asset(
        request=req,
        asset_id=str(asset_id),
        csrf="valid-csrf",
        page_num=42,
        tab="inspector",
    )

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "/quran?page_num=42&tab=inspector&saved=asset_deleted" in resp.headers["location"]
    mock_session.delete.assert_called_once_with(dummy_asset)


# -----------------------------------------------------------------------------
# 5. Channel Seed Execution
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quran_seed_channel_action(mock_admin, monkeypatch):
    monkeypatch.setattr("khatmsaz.web.app._admin", AsyncMock(return_value=(mock_admin, "raw-session")))
    monkeypatch.setattr("khatmsaz.web.app._valid_csrf", lambda raw, token: True)
    mock_seed = AsyncMock(return_value={"image_count": 604, "audio_count": 604})
    monkeypatch.setattr("khatmsaz.modules.content.service.seed_verified_quran_channel_map", mock_seed)
    monkeypatch.setattr("khatmsaz.modules.audit_log.service.record", AsyncMock())

    req = _make_request("/quran/seed-channel")
    resp = await seed_quran_channel(request=req, csrf="valid-csrf", tab="sync")

    assert isinstance(resp, RedirectResponse)
    assert resp.status_code == 303
    assert "/quran?tab=sync&saved=seeded" in resp.headers["location"]
    assert mock_seed.call_count == 1
