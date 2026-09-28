"""R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/
Bale ID or phone) that gets shown to every member inside the welcome message.
Migration-free — the handle is folded into the existing ``welcome_text`` column.
"""
from khatmsaz.bot.handlers.create_khatm import (
    _compose_welcome_with_contact,
    _normalize_contact,
)


def test_normalize_adds_at_for_bare_id():
    assert _normalize_contact("khatm_organizer") == "@khatm_organizer"
    assert _normalize_contact("@already") == "@already"


def test_normalize_strips_tme_link():
    assert _normalize_contact("https://t.me/someone") == "@someone"
    assert _normalize_contact("ble.ir/someone") == "@someone"


def test_normalize_keeps_phone_untouched():
    assert _normalize_contact("+989121234567") == "+989121234567"
    assert _normalize_contact("09121234567") == "09121234567"


def test_compose_appends_contact_line_to_welcome():
    out = _compose_welcome_with_contact("خوش اومدید", "@ali", "fa")
    assert "خوش اومدید" in out
    assert "@ali" in out


def test_compose_contact_only_when_no_welcome():
    out = _compose_welcome_with_contact(None, "@ali", "fa")
    assert "@ali" in out


def test_compose_none_contact_passes_welcome_through():
    assert _compose_welcome_with_contact("سلام", None, "fa") == "سلام"
    assert _compose_welcome_with_contact(None, None, "fa") is None


def test_compose_truncates_at_500():
    out = _compose_welcome_with_contact("x" * 490, "@averylonghandlehere", "fa")
    assert len(out) <= 500
