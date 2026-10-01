"""Render the redesigned admin pages with real Jinja templates.

These tests intentionally avoid PostgreSQL: they catch missing context,
broken template expressions, and the UX regressions the owner can otherwise
only discover after deployment.
"""

from types import SimpleNamespace
from uuid import uuid4
from pathlib import Path

from starlette.requests import Request

from khatmsaz.web.app import app, templates
from khatmsaz.i18n import t


def _request(path: str) -> Request:
    return Request({"type": "http", "method": "GET", "path": path, "headers": [], "query_string": b""})


def _admin(*permissions: str):
    return SimpleNamespace(display_name="مدیر آزمایشی", _admin_permissions=set(permissions))


def _render(name: str, path: str, **context) -> str:
    return templates.get_template(name).render(
        request=_request(path), admin=_admin("CONTENT_MANAGE", "FINANCE_MANAGE"),
        csrf="test-csrf", fa_label=lambda value: str(value), panel_logo_url="", **context,
    )


def test_operations_page_renders_panel_logo_setting():
    html = _render(
        "operations.html", "/operations", saved="", services=[],
        queues=SimpleNamespace(broadcasts=0, covers=0, phones=0, categories=0),
        worker=SimpleNamespace(
            scheduler_started_at=None, last_scan_succeeded_at=None,
            last_scan_error=None,
        ),
        scan_interval=5,
    )

    assert 'action="/operations/panel-logo"' in html
    assert 'name="panel_logo_url"' in html
    assert "نشان پیش‌فرض «خ»" in html


def test_public_join_uses_configured_logo_and_inlines_critical_styles():
    request = Request({"type": "http", "method": "GET", "path": "/join/test", "headers": [], "scheme": "https", "server": ("example.test", 443), "query_string": b"", "root_path": "", "app": app})
    khatm = SimpleNamespace(
        title="ختم زیارت عاشورا", khatm_type=SimpleNamespace(value="COMMITMENT"),
        niyyat="به نیت سلامتی", welcome_text="همراه ما باشید",
    )
    html = templates.get_template("join.html").render(
        request=request, unavailable=False, khatm=khatm, creator_name="الیاس",
        member_count=3, links=[{"name": "ادامه در تلگرام", "url": "https://t.me/test", "is_telegram": True}],
        no_bots=False, panel_logo_url="https://cdn.example/logo.png",
    )
    assert 'src="https://cdn.example/logo.png"' in html
    assert ".brand-mark" in html
    assert "request.url_for('static'" not in html
    assert "تلگرام · عربی" not in html


def test_both_panel_headers_support_configured_logo_and_fallback():
    admin_template = templates.get_template("base.html")
    creator_template = templates.get_template("creator_base.html")
    request = _request("/")
    common = {"request": request, "csrf": "test", "panel_logo_url": "https://cdn.example/logo.png"}

    admin_html = admin_template.render(admin=_admin(), **common)
    creator_html = creator_template.render(
        creator=SimpleNamespace(display_name="سازنده"), lang="fa", t=t,
        label=lambda value: str(value), **common,
    )
    assert 'src="https://cdn.example/logo.png"' in admin_html
    assert 'src="https://cdn.example/logo.png"' in creator_html

    common["panel_logo_url"] = ""
    assert ">خ</div>" in admin_template.render(admin=_admin(), **common)
    assert ">خ</div>" in creator_template.render(
        creator=SimpleNamespace(display_name="سازنده"), lang="fa", t=t,
        label=lambda value: str(value), **common,
    )


def test_both_panel_shells_use_pinned_estedad_with_system_fallbacks():
    for template_name in ("base.html", "creator_base.html"):
        source = (Path("src/khatmsaz/web/templates") / template_name).read_text(encoding="utf-8")
        assert "@fontsource/estedad@5.3.0/400.css" in source
        assert "@fontsource/estedad@5.3.0/800.css" in source
        assert "['Estedad', 'system-ui', 'Tahoma', 'sans-serif']" in source
        assert "Vazirmatn" not in source


def test_finance_page_renders_plain_language_guide_and_forms():
    plan = SimpleNamespace(
        plan="FREE", title="رایگان", pricing_mode="USAGE_BASED",
        price_toman=0, unit_price_toman=20_000,
        entitlements={"khatm.create": True, "max_quran_members": 30}, enabled=True,
    )
    html = _render(
        "finance.html", "/finance", saved="", paid_total=120_000,
        refunded_total=10_000, coupons=[], invoice_rows=[],
        plan_definitions=[plan], sms_plan_options=[],
        broadcast_policies={"TELEGRAM": (3, 0), "BALE": (3, 0), "SMS": (0, 1000)},
    )

    assert "کاربر عادی کیست؟" in html
    assert "سازنده کیست؟" in html
    assert "برای هر ختم تازه" in html
    assert 'action="/finance/plans/FREE"' in html


def test_categories_page_renders_library_picker_and_explicit_statuses():
    assets = [SimpleNamespace(slug="dua-ahd", title="دعای عهد")]
    active = SimpleNamespace(
        id=uuid4(), title="دعای عهد", group=SimpleNamespace(value="DUA"),
        body_text=None, devotional_slug="dua-ahd", image_url=None,
        source_note=None, is_active=True, sort_order=10,
    )
    inactive = SimpleNamespace(
        id=uuid4(), title="ذکر آزمایشی", group=SimpleNamespace(value="LAAN"),
        body_text="متن کوتاه", devotional_slug=None, image_url=None,
        source_note=None, is_active=False, sort_order=20,
    )
    html = _render(
        "categories.html", "/categories", saved="", requests=[],
        items=[active, inactive], devotional_assets=assets,
        grouped_items={"DUA": [active], "LAAN": [inactive]},
        group_labels={"DUA": "دعا / زیارت", "LAAN": "لعن"},
    )

    assert "متن آماده از کتابخانه" in html
    assert '<option value="dua-ahd" selected>دعای عهد</option>' in html
    assert "✅ فعال (در ویزارد دیده می‌شود)" in html
    assert "⛔ غیرفعال (پنهان)" in html
    assert "جایگاه نمایش در ویزارد" in html
    assert "دعاها و زیارت‌ها" in html
    assert "نام فایل یا لینک تصویر" in html
    assert "laan-omar.jpg" in html
    assert "کد اتصال صوت/متن آماده" not in html


def test_devotionals_page_renders_clear_library_workflow_and_statuses():
    items = [
        {
            "slug": "dua-ahd", "title": "دعای عهد", "content_type": "DUA",
            "type_label": "دعا", "enabled": True, "text": "متن دعا",
            "char_count": 8, "has_image": False, "has_audio": False,
        },
        {
            "slug": "ziyarat-test", "title": "زیارت آزمایشی", "content_type": "ZIYARAT",
            "type_label": "زیارت", "enabled": False, "text": "متن زیارت",
            "char_count": 10, "has_image": False, "has_audio": False,
        },
    ]
    html = _render(
        "devotionals.html", "/devotionals", saved="", items=items,
        grouped_items={"DUA": [items[0]], "ZIYARAT": [items[1]]},
        salawat_text="اللهم صل علی محمد و آل محمد",
        salawat_image_url="salawat.jpg", type_labels={"DUA": "دعا", "ZIYARAT": "زیارت"},
    )

    assert "شناسهٔ داخلی (انگلیسی)" in html
    assert "نیازی به کپی‌کردن شناسه نیست" in html
    assert "✅ فعال (به کاربران نمایش داده می‌شود)" in html
    assert "⛔ غیرفعال (پنهان)" in html
    assert "فرم هر مورد فقط هنگام نیاز باز می‌شود" in html
    assert "نام فایل یا لینک تصویر صلوات" in html
    assert 'value="salawat.jpg"' in html


def test_creator_detail_renders_manage_stats_members_export_and_settings():
    enum_value = lambda value: SimpleNamespace(value=value)
    khatm = SimpleNamespace(
        id=uuid4(), title="ختم آزمایشی", welcome_text="خوش آمدید",
        status=enum_value("ACTIVE"), khatm_type=enum_value("COMMITMENT"),
        template_type=enum_value("QURAN_PAGE"), allow_pause=True,
        allow_snooze=False, allow_skip_today=True, miss_notice_threshold=3,
        miss_notice_window_days=7, completion_announcement_enabled=True,
        schedule_kind="NONE", schedule_value=None,
        repetition_target=None, visibility=enum_value("UNLISTED"),
        allowed_platforms="BOTH", reminder_tone="FRIENDLY",
        daily_deadline_hour=23,
    )
    stats = SimpleNamespace(
        active_members=2, completed_portions=4, total_portions=10,
        contribution_total=0,
    )
    html = templates.get_template("creator_khatm_detail.html").render(
        request=_request(f"/creator/khatms/{khatm.id}"),
        creator=SimpleNamespace(display_name="سازنده"), csrf="test-csrf",
        lang="fa", t=t, label=lambda value: value.value,
        khatm=khatm, stats=stats, rows=[], query="", page=1,
        has_next=False, saved="", editable_welcome_text="خوش آمدید",
    )

    assert "تنظیمات این ختم" in html
    assert "عضوی با این جست‌وجو پیدا نشد." in html
    assert "دریافت اکسل کامل اعضا" in html
    assert 'name="allow_pause"' in html
    assert 'name="allow_skip_today"' not in html
    assert 'action="/creator/khatms/' in html


def test_creator_new_khatm_form_renders_all_four_types_and_creation_route():
    category = lambda title: SimpleNamespace(id=uuid4(), title=title)
    html = templates.get_template("creator_khatm_new.html").render(
        request=_request("/creator/khatms/new"),
        creator=SimpleNamespace(display_name="سازنده"), csrf="test-csrf",
        lang="fa", t=t, label=lambda value: str(value), error="",
        dua_categories=[category("دعای عهد")], laan_categories=[category("لعن نمونه")],
        creation_price=20_000,
    )

    assert 'action="/creator/khatms/create"' in html
    assert 'value="quran"' in html
    assert 'value="salawat"' in html
    assert 'value="dua"' in html
    assert 'value="laan"' in html
    assert 'name="quran_edition_id"' not in html
    assert "مدینه (حفص) — ۶۰۴ صفحه" in html
    assert "20,000 تومان" in html


def test_creator_wallet_shows_three_tier_audience_view():
    """Owner model §A (2026-09-30): the wallet plan card shows the real tier, the
    total-audience usage vs the free cap, the ads status, and a FREE/BASIC/PRO
    comparison — no fake purchase button yet."""
    base = dict(
        request=_request("/creator/wallet"), creator=SimpleNamespace(display_name="سازنده"),
        csrf="test-csrf", lang="fa", t=t, label=lambda value: str(value),
        balance="500,000", credit="0", plan_label="رایگان",
        plan_view={
            "title": "رایگان", "tier": "FREE", "is_free": True, "is_basic": False,
            "is_pro": False, "ads_shown": False, "total_members": 120, "total_cap": 1000,
            "caps": None,
        },
        invoices=[], topup_amounts=(), gateway_ready=False,
        free_caps={"quran": 100, "devotional": 100},
    )
    html = templates.get_template("creator_wallet.html").render(**base, pro_threshold=0)

    assert 'action="/creator/plan/upgrade"' not in html
    assert t("web.creator.plan_total_audience", "fa") in html
    assert "120" in html and "1000" in html
    assert t("web.creator.plan_basic_name", "fa") in html
    assert t("web.creator.plan_ads_off", "fa") in html
    assert "web.creator.plan_" not in html  # no raw i18n keys leaked
