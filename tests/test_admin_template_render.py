"""Render the redesigned admin pages with real Jinja templates.

These tests intentionally avoid PostgreSQL: they catch missing context,
broken template expressions, and the UX regressions the owner can otherwise
only discover after deployment.
"""

from types import SimpleNamespace
from uuid import uuid4

from starlette.requests import Request

from khatmsaz.web.app import templates
from khatmsaz.i18n import t


def _request(path: str) -> Request:
    return Request({"type": "http", "method": "GET", "path": path, "headers": [], "query_string": b""})


def _admin(*permissions: str):
    return SimpleNamespace(display_name="مدیر آزمایشی", _admin_permissions=set(permissions))


def _render(name: str, path: str, **context) -> str:
    return templates.get_template(name).render(
        request=_request(path), admin=_admin("CONTENT_MANAGE", "FINANCE_MANAGE"),
        csrf="test-csrf", fa_label=lambda value: str(value), **context,
    )


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
        source_note=None, is_active=True,
    )
    inactive = SimpleNamespace(
        id=uuid4(), title="ذکر آزمایشی", group=SimpleNamespace(value="SALAWAT"),
        body_text="متن کوتاه", devotional_slug=None, image_url=None,
        source_note=None, is_active=False,
    )
    html = _render(
        "categories.html", "/categories", saved="", requests=[],
        items=[active, inactive], devotional_assets=assets,
        group_labels={"DUA": "دعا / زیارت", "SALAWAT": "صلوات"},
    )

    assert "متن آماده از کتابخانه" in html
    assert '<option value="dua-ahd" selected>دعای عهد</option>' in html
    assert "✅ فعال (در ویزارد دیده می‌شود)" in html
    assert "⛔ غیرفعال (پنهان)" in html
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
    html = _render("devotionals.html", "/devotionals", saved="", items=items)

    assert "شناسهٔ داخلی (انگلیسی)" in html
    assert "نیازی به کپی‌کردن شناسه نیست" in html
    assert "✅ فعال (به کاربران نمایش داده می‌شود)" in html
    assert "⛔ غیرفعال (پنهان)" in html


def test_creator_detail_renders_manage_stats_members_export_and_settings():
    enum_value = lambda value: SimpleNamespace(value=value)
    khatm = SimpleNamespace(
        id=uuid4(), title="ختم آزمایشی", welcome_text="خوش آمدید",
        status=enum_value("ACTIVE"), khatm_type=enum_value("COMMITMENT"),
        template_type=enum_value("QURAN_PAGE"), allow_pause=True,
        allow_snooze=False, allow_skip_today=True, miss_notice_threshold=3,
        miss_notice_window_days=7, completion_announcement_enabled=True,
        schedule_kind="NONE", schedule_value=None,
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
        has_next=False, saved="",
    )

    assert "تنظیمات این ختم" in html
    assert "عضوی با این جست‌وجو پیدا نشد." in html
    assert "دریافت اکسل کامل اعضا" in html
    assert 'name="allow_pause"' in html
    assert 'name="allow_skip_today"' in html
    assert 'action="/creator/khatms/' in html


def test_creator_new_khatm_form_renders_all_four_types_and_creation_route():
    category = lambda title: SimpleNamespace(id=uuid4(), title=title)
    html = templates.get_template("creator_khatm_new.html").render(
        request=_request("/creator/khatms/new"),
        creator=SimpleNamespace(display_name="سازنده"), csrf="test-csrf",
        lang="fa", t=t, label=lambda value: str(value), error="",
        dua_categories=[category("دعای عهد")], laan_categories=[category("لعن نمونه")],
        quran_editions=[{"id": "madina-hafs", "label": "مدینه — ۶۰۴ صفحه"}],
        creation_price=20_000,
    )

    assert 'action="/creator/khatms/create"' in html
    assert 'value="quran"' in html
    assert 'value="salawat"' in html
    assert 'value="dua"' in html
    assert 'value="laan"' in html
    assert "20,000 تومان" in html
