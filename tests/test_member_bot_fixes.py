"""Regression for the 2026-09-29 member-bot fixes (owner live report):

1. Open-Quran delivery-hour accepts an exact time «14:27», not only 0–23.
2. The Quran join card drops the «ثبت مشارکت» button when the in-bot setup
   auto-starts (no pages sent yet → the button pointed at nothing).
3. `/my_khatms` command (not only the button label) works on member bots.
4. Settings shows «ورود به پنل سازنده» only for creators/admins.
"""
from types import SimpleNamespace

from aiogram.filters import Command

from khatmsaz.bot import keyboards
from khatmsaz.bot.handlers.join_flow import _parse_delivery_time
from khatmsaz.i18n import t
from khatmsaz.modules.identity.models import UserRole
from khatmsaz.modules.khatm.models import (
    Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum,
)


def test_reminder_due_fires_at_or_after_target_not_only_in_window():
    """Owner report: pages/reminders stopped arriving on member bots. The old
    15-minute window dropped a whole day's delivery if a scan missed it. Delivery
    must fire on the first scan at/after the chosen time (dedupe keeps it once/day)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from khatmsaz.modules.reminder_engine.service import _is_reminder_due

    tz = ZoneInfo("Asia/Tehran")

    def at(h, m):
        return datetime(2026, 9, 29, h, m, tzinfo=tz)

    # reminder set for 12:08 — must be due at the 12:15 and 12:45 scans (old code
    # was only due in [12:08, 12:23), so 12:45 wrongly returned False and the day
    # was skipped if 12:15 was missed).
    assert _is_reminder_due(at(12, 15), 12, 8) is True
    assert _is_reminder_due(at(12, 45), 12, 8) is True
    assert _is_reminder_due(at(18, 0), 12, 8) is True
    # before the chosen time it is not due yet
    assert _is_reminder_due(at(12, 0), 12, 8) is False
    assert _is_reminder_due(at(9, 0), 12, 8) is False


def test_open_quran_hour_accepts_exact_time():
    assert _parse_delivery_time("14:27") == (14, 27)
    assert _parse_delivery_time("9") == (9, 0)
    assert _parse_delivery_time("24:00") is None
    assert _parse_delivery_time("aa") is None


def _make_khatm():
    return SimpleNamespace(
        id="k1", title="ختم قرآن", niyyat=None, welcome_text=None,
        template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.OPEN,
        allow_skip_today=False, allow_snooze=False, status=KhatmStatus.ACTIVE,
    )


def test_quran_join_card_button_suppressed_when_autosetup():
    from khatmsaz.bot.handlers.start import build_join_success_message

    khatm = _make_khatm()
    # auto-setup path: no button on the welcome card
    _text, kb = build_join_success_message(
        khatm, SimpleNamespace(id="p1"), None, False, "علی", "", "fa",
        quran_join_button=False,
    )
    assert kb is None
    # approval path keeps the button (can't start an FSM remotely)
    _text2, kb2 = build_join_success_message(
        khatm, SimpleNamespace(id="p1"), None, False, "علی", "", "fa",
        quran_join_button=True,
    )
    assert kb2 is not None


def test_my_khatms_command_wired_on_member_bot():
    from khatmsaz.bot.handlers import member_my_khatms

    handler = member_my_khatms.list_member_khatms
    # aiogram stores registered filters on the callback via the router; assert a
    # Command('my_khatms') filter is present among the handler's flags/filters.
    found = False
    for observer in member_my_khatms.router.message.handlers:
        if observer.callback is handler:
            for f in observer.filters:
                if isinstance(getattr(f, "callback", None), Command):
                    cmds = getattr(f.callback, "commands", ())
                    if "my_khatms" in cmds:
                        found = True
    assert found, "/my_khatms command is not wired on the member bot"


def test_settings_creator_panel_button_visibility():
    with_btn = keyboards.settings_home_keyboard(audio_enabled=False, lang="fa", show_creator_panel=True)
    without = keyboards.settings_home_keyboard(audio_enabled=False, lang="fa", show_creator_panel=False)
    label = t("settings.button.creator_panel", "fa")
    assert any(b.text == label for row in with_btn.inline_keyboard for b in row)
    assert not any(b.text == label for row in without.inline_keyboard for b in row)
    # the button opens the creator Mini App
    assert any(
        b.callback_data == "creator:web_login"
        for row in with_btn.inline_keyboard for b in row
    )
