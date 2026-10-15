"""Tests for MASTER-37: Admin Panel Comprehensive Redesign and Progressive Disclosure Audit."""

from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "src" / "khatmsaz" / "web" / "templates"


def test_templates_directory_exists():
    assert TEMPLATES_DIR.exists(), f"Templates directory {TEMPLATES_DIR} does not exist"


def test_all_templates_compile_cleanly_with_jinja():
    """Verify all templates in the admin panel compile without Jinja syntax errors."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template_files = list(TEMPLATES_DIR.glob("*.html"))
    assert len(template_files) >= 10, f"Expected at least 10 html templates, found {len(template_files)}"

    for tmpl_path in template_files:
        tmpl_name = tmpl_path.name
        try:
            env.get_template(tmpl_name)
        except Exception as exc:
            pytest.fail(f"Template {tmpl_name} failed Jinja2 compilation: {exc}")


def test_finance_template_refund_url_syntax_fixed():
    """Verify line in finance.html has proper Jinja variable tag {{ invoice.id }}."""
    finance_html = (TEMPLATES_DIR / "finance.html").read_text(encoding="utf-8")
    assert "/finance/invoices/{{ invoice.id }}/refund" in finance_html
    assert "/finance/invoices/{ invoice.id }/refund" not in finance_html


def test_khatm_detail_status_form_has_submit_button():
    """Verify khatm_detail.html has submit button in status changer form."""
    khatm_detail_html = (TEMPLATES_DIR / "khatm_detail.html").read_text(encoding="utf-8")
    assert 'action="/khatms/{{ khatm.id }}/status"' in khatm_detail_html
    assert 'type="submit"' in khatm_detail_html
    assert "ثبت وضعیت" in khatm_detail_html


def test_khatms_progressive_disclosure_cards():
    """Verify khatms.html uses Smart Khatm Cards with progressive disclosure."""
    khatms_html = (TEMPLATES_DIR / "khatms.html").read_text(encoding="utf-8")
    assert "toggleKhatmDisclosure" in khatms_html
    assert "body-khatm-{{ item.id }}" in khatms_html
    assert "chevron-khatm-{{ item.id }}" in khatms_html


def test_tooltip_scoping_prevents_persistent_display_bug():
    """Verify components.html uses group/tip to avoid accordion hover collision."""
    components_html = (TEMPLATES_DIR / "components.html").read_text(encoding="utf-8")
    assert "group/tip" in components_html
    assert "group-hover/tip:opacity-100" in components_html
    assert "group-hover/tip:visible" in components_html
