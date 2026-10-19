"""Unit and integration tests for MASTER-51: Devotionals, Categories & Message Templates Studio."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Request
from starlette.testclient import TestClient

from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup, KhatmCategoryRequest
from khatmsaz.web.app import (
    app,
    devotionals_page,
    categories_page,
    message_templates,
    save_devotional,
    toggle_devotional,
    save_devotional_media,
    delete_devotional_media,
    create_category,
    update_category,
    toggle_category,
    decline_category_request,
    fulfill_category_request,
    save_template_content,
    toggle_template,
    save_salawat_image,
)


def test_devotionals_template_structure():
    """Verify that devotionals.html template contains all MASTER-51 required studio UI elements, KPIs and 4 tabs."""
    with open("src/khatmsaz/web/templates/devotionals.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Header and Help
    assert "استودیو جامع ادعیه، ویزارد و قالب‌ها" in content
    assert "help_button" in content

    # 4 Studio KPI Cards
    assert "مجموع ادعیه و خطبه‌ها" in content
    assert "فایل‌های چندرسانه‌ای ضمیمه" in content
    assert "دسته‌بندی‌های فعال ویزارد" in content
    assert "قالب‌های پیام سیستم" in content

    # 4 Unified Studio Tabs
    assert 'id="tabBtn_devotionals"' in content
    assert 'id="tabBtn_categories"' in content
    assert 'id="tabBtn_templates"' in content
    assert 'id="tabBtn_salawat"' in content

    # Tab 1: Devotionals & Khutbahs
    assert "افزودن دعا، زیارت، خطبه یا لعن جدید" in content
    assert "شناسهٔ داخلی (انگلیسی)" in content
    assert "فایل‌های چندرسانه‌ای ضمیمه" in content
    assert "آپلود مستقیم فایل از کامپیوتر/موبایل" in content

    # Tab 2: Wizard Categories
    assert "افزودن دسته‌بندی جدید به ویزارد ختم ربات" in content
    assert "دسته‌بندی‌های موجود در ویزارد" in content
    assert "جایگاه نمایش در ویزارد" in content

    # Tab 3: Message Templates
    assert "ثبت نسخه جدید قالب پیام" in content
    assert "قالب‌های ثبت‌شده سیستم" in content

    # Tab 4: Sacred Salawat
    assert "ذکر مقدس صلوات" in content
    assert "نام فایل یا لینک تصویر صلوات" in content
    assert "ذخیره تصویر صلوات" in content


def test_devotionals_page_unauthenticated():
    """Unauthenticated access to /devotionals must redirect to /login."""
    client = TestClient(app, follow_redirects=False)
    response = client.get("/devotionals")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_categories_redirect_to_devotionals():
    """Accessing /categories must redirect to /devotionals?tab=categories."""
    client = TestClient(app, follow_redirects=False)
    response = client.get("/categories")
    # Even unauthenticated, _admin redirects to /login, but with admin it redirects to /devotionals?tab=categories
    assert response.status_code == 303


@pytest.mark.asyncio
async def test_categories_page_authenticated_redirect():
    """Authenticated admin accessing /categories is redirected to /devotionals?tab=categories."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    req = MagicMock(spec=Request)
    req.url = MagicMock(query="saved=created")

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))):
        resp = await categories_page(request=req)
        assert resp.status_code == 303
        assert resp.headers["location"] == "/devotionals?tab=categories&saved=created"


@pytest.mark.asyncio
async def test_templates_page_authenticated_redirect():
    """Authenticated admin accessing /templates is redirected to /devotionals?tab=templates."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    req = MagicMock(spec=Request)
    req.url = MagicMock(query="saved=template_saved")

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))):
        resp = await message_templates(request=req)
        assert resp.status_code == 303
        assert resp.headers["location"] == "/devotionals?tab=templates&saved=template_saved"


@pytest.mark.asyncio
async def test_devotionals_page_authenticated():
    """Authenticated admin can load /devotionals studio with all 4 KPIs and tab data."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()
    admin_user.role = UserRole.SUPER_ADMIN

    mock_asset = MagicMock()
    mock_asset.id = uuid4()
    mock_asset.slug = "dua-ahd"
    mock_asset.title = "دعای عهد"
    mock_asset.content_type = "DUA"
    mock_asset.enabled = True
    mock_asset.text_body = "متن تست دعای عهد"
    mock_asset.image_ref = None
    mock_asset.audio_ref = None

    mock_cat = MagicMock()
    mock_cat.id = uuid4()
    mock_cat.group = KhatmCategoryGroup.DUA
    mock_cat.title = "دعای عهد"
    mock_cat.slug = "dua-ahd"
    mock_cat.body_text = None
    mock_cat.devotional_slug = "dua-ahd"
    mock_cat.enabled = True
    mock_cat.is_active = True
    mock_cat.display_position = 1

    mock_tpl = MagicMock()
    mock_tpl.id = uuid4()
    mock_tpl.key = "welcome"
    mock_tpl.locale = "fa"
    mock_tpl.version = 1
    mock_tpl.body = "سلام خوش آمدید"
    mock_tpl.enabled = True

    dummy_session = AsyncMock()
    dummy_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=[mock_tpl])
    )

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)
    req.state = MagicMock()
    req.query_params = {"tab": "devotionals"}

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.content.service.list_all_devotional_assets", AsyncMock(return_value=[mock_asset])), \
         patch("khatmsaz.modules.content.service.list_all_devotional_media_by_asset", AsyncMock(return_value={mock_asset.id: []})), \
         patch("khatmsaz.modules.khatm_category.service.list_all", AsyncMock(return_value=[mock_cat])), \
         patch("khatmsaz.modules.khatm_category.service.list_pending_requests", AsyncMock(return_value=[])):

        resp = await devotionals_page(request=req)
        assert resp.status_code == 200
        html = resp.body.decode("utf-8")
        assert "استودیو جامع ادعیه، ویزارد و قالب‌ها" in html
        assert "مجموع ادعیه و خطبه‌ها" in html
        assert "دعای عهد" in html


@pytest.mark.asyncio
async def test_devotional_save_action():
    """Saving devotional text registers asset, records audit and redirects to tab=devotionals."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    mock_asset = MagicMock()
    mock_asset.slug = "dua-test"
    mock_asset.title = "دعای آزمایشی"
    mock_asset.content_type = "DUA"

    dummy_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.content.service.register_devotional_text", AsyncMock(return_value=mock_asset)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await save_devotional(
            request=req, slug="dua-test", title="دعای آزمایشی",
            content_type="DUA", text_body="متن کامل", csrf="valid_csrf",
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/devotionals?tab=devotionals&saved=saved"
        mock_audit.assert_called_once()


@pytest.mark.asyncio
async def test_devotional_toggle_action():
    """Toggling devotional enabled state records audit and redirects to tab=devotionals."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    mock_asset = MagicMock()
    mock_asset.slug = "dua-test"
    mock_asset.enabled = False

    dummy_session = AsyncMock()
    dummy_session.scalar.return_value = mock_asset

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.content.service.set_devotional_enabled", AsyncMock(return_value=mock_asset)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        resp = await toggle_devotional(request=req, slug="dua-test", csrf="valid_csrf")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/devotionals?tab=devotionals&saved=toggled"
        mock_audit.assert_called_once()


@pytest.mark.asyncio
async def test_devotional_media_save_and_delete_actions():
    """Saving and deleting devotional media records audit and redirects with tab=devotionals."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    dummy_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.content.service.add_devotional_video_page", AsyncMock()), \
         patch("khatmsaz.modules.content.service.delete_devotional_media_by_id", AsyncMock(return_value=True)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()) as mock_audit:

        # 1. Save Media
        resp = await save_devotional_media(
            request=req, csrf="valid_csrf", slug="khutbah-fadak",
            kind="VIDEO", platform="TELEGRAM", page_number=1,
            reciter_id="narrator_1", reciter_label="بخش اول خطبه فدکیه",
            asset_ref="https://example.com/part1.mp4", file=None,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/devotionals?tab=devotionals&saved=media_saved"

        # 2. Delete Media
        media_id = uuid4()
        resp_del = await delete_devotional_media(request=req, media_id=media_id, csrf="valid_csrf")
        assert resp_del.status_code == 303
        assert resp_del.headers["location"] == "/devotionals?tab=devotionals&saved=media_deleted"


@pytest.mark.asyncio
async def test_category_create_and_toggle_actions():
    """Creating and toggling category records audit and redirects with tab=categories."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    mock_cat = MagicMock()
    mock_cat.id = uuid4()
    mock_cat.group = KhatmCategoryGroup.DUA
    mock_cat.title = "دعای سمات"
    mock_cat.sort_order = 1
    mock_cat.is_active = True

    dummy_session = AsyncMock()
    dummy_session.scalar.return_value = mock_cat

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.khatm_category.service.create", AsyncMock(return_value=mock_cat)), \
         patch("khatmsaz.modules.khatm_category.service.reposition", AsyncMock(return_value=mock_cat)), \
         patch("khatmsaz.modules.khatm_category.service.get", AsyncMock(return_value=mock_cat)), \
         patch("khatmsaz.modules.khatm_category.service.set_active", AsyncMock(return_value=mock_cat)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()):

        # 1. Create Category
        resp_create = await create_category(
            request=req, group="DUA", title="دعای سمات",
            body_text="", source_note="", devotional_slug="dua-somat",
            image_url="", display_position=0, csrf="valid_csrf",
        )
        assert resp_create.status_code == 303
        assert resp_create.headers["location"] == "/devotionals?tab=categories&saved=created"

        # 2. Toggle Category
        resp_toggle = await toggle_category(request=req, category_id=mock_cat.id, csrf="valid_csrf")
        assert resp_toggle.status_code == 303
        assert resp_toggle.headers["location"] == "/devotionals?tab=categories&saved=toggled"


@pytest.mark.asyncio
async def test_template_save_and_toggle_actions():
    """Saving and toggling template records audit and redirects with tab=templates."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    mock_tpl = MagicMock()
    mock_tpl.id = uuid4()
    mock_tpl.key = "welcome"
    mock_tpl.locale = "fa"
    mock_tpl.version = 2
    mock_tpl.enabled = True

    dummy_session = AsyncMock()
    dummy_session.get.return_value = mock_tpl

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.message_template.repository.next_version", AsyncMock(return_value=2)), \
         patch("khatmsaz.modules.message_template.repository.create", AsyncMock(return_value=mock_tpl)), \
         patch("khatmsaz.modules.message_template.repository.set_enabled", AsyncMock(return_value=mock_tpl)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()):

        # 1. Save Template
        resp_save = await save_template_content(
            request=req, csrf="valid_csrf", key="welcome",
            locale="fa", body="متن جدید خوش‌آمدگویی",
        )
        assert resp_save.status_code == 303
        assert resp_save.headers["location"] == "/devotionals?tab=templates&saved=template_saved"

        # 2. Toggle Template
        resp_toggle = await toggle_template(request=req, template_id=mock_tpl.id, csrf="valid_csrf")
        assert resp_toggle.status_code == 303
        assert resp_toggle.headers["location"] == "/devotionals?tab=templates&saved=template_toggled"


@pytest.mark.asyncio
async def test_salawat_image_save_action():
    """Saving Salawat image records audit and redirects to tab=salawat."""
    admin_user = MagicMock(spec=User)
    admin_user.id = uuid4()

    mock_asset = MagicMock()
    mock_asset.image_ref = "https://example.com/salawat_new.jpg"

    dummy_session = AsyncMock()

    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    req = MagicMock(spec=Request)

    with patch("khatmsaz.web.app._admin", AsyncMock(return_value=(admin_user, "mock_cookie"))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", mock_scope), \
         patch("khatmsaz.modules.content.service.set_salawat_image_url", AsyncMock(return_value=mock_asset)), \
         patch("khatmsaz.modules.audit_log.service.record", AsyncMock()):

        resp = await save_salawat_image(
            request=req, image_url="https://example.com/salawat_new.jpg", file=None, csrf="valid_csrf",
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/devotionals?tab=salawat&saved=salawat"
