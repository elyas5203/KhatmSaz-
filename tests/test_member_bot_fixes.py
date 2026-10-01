"""Regression for the 2026-09-29 member-bot fixes (owner live report):

1. Open-Quran delivery-hour accepts an exact time «14:27», not only 0–23.
2. The Quran join card drops the «ثبت مشارکت» button when the in-bot setup
   auto-starts (no pages sent yet → the button pointed at nothing).
3. `/my_khatms` command (not only the button label) works on member bots.
4. Settings shows «ورود به پنل سازنده» only for creators/admins.
"""
from types import SimpleNamespace

import pytest
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


def test_committed_quran_portion_uses_one_tap_done_not_numeric_contribution():
    from khatmsaz.bot.handlers.start import build_join_success_message
    from khatmsaz.modules.allocation.models import PortionUnitKind

    khatm = _make_khatm()
    khatm.khatm_type = KhatmTypeEnum.COMMITMENT
    portion = SimpleNamespace(unit_kind=PortionUnitKind.POSITIONAL, unit_start=1, unit_end=3)
    _text, keyboard = build_join_success_message(
        khatm, SimpleNamespace(id="p1"), portion, False, "علی", "", "fa",
    )
    callbacks = [b.callback_data for row in keyboard.inline_keyboard for b in row]
    assert "done:k1" in callbacks
    assert "contribute:k1" not in callbacks


def test_niyyat_proxy_strips_repeated_be_niyyat_prefix():
    from khatmsaz.bot.handlers.create_khatm import _compose_niyyat

    assert _compose_niyyat("fa", "به نیت تست آخر بات") == (
        "به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از تست آخر بات"
    )


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


@pytest.mark.asyncio
async def test_next_portion_delivery_records_daily_reminder_to_prevent_duplicate(monkeypatch):
    """E1 audit (2026-09-30): after allocating+sending the next committed-Quran
    portion, the engine must record DAILY_REMINDER so the digest path doesn't
    re-send the same fresh portion on the next 1-minute scan."""
    import pytest as _pytest
    from datetime import datetime, timezone
    from types import SimpleNamespace
    from khatmsaz.modules.reminder_engine import service as re
    from khatmsaz.modules.notification.models import NotificationKind

    part = SimpleNamespace(id="part-1", user_id="user-1", joined_via_bot_instance_id=None)
    khatm = SimpleNamespace(id="k1", title="ختم قرآن", allow_snooze=False)
    old_portion = SimpleNamespace(
        participation_id="part-1", khatm_id="k1",
        updated_at=datetime(2020, 1, 1, tzinfo=timezone.utc),  # long ago → due
    )
    next_portion = SimpleNamespace(unit_start=4, unit_end=6)
    recorded = []

    async def _list_latest(_s): return [old_portion]
    async def _get_by_id(_s, _pid): return part
    async def _get_khatm(_s, _kid): return khatm
    def _has_started(_k): return True
    async def _get_pref(_s, _pid): return SimpleNamespace(enabled=True, reminder_hour=0, reminder_minute=0)
    async def _get_settings(_s, _uid): return SimpleNamespace(timezone="Asia/Tehran", language="fa")
    async def _allocate(_s, _kid, _pid): return next_portion
    async def _push(*a, **k): return None
    async def _render(_s, *a, **k): return "متن"
    async def _kb(_s, _uid, _text, _markup, *, bot_instance_id=None): return 1
    async def _record(_s, pid, kind): recorded.append((pid, kind))

    monkeypatch.setattr(re.allocation_service, "list_latest_portion_per_participation", _list_latest)
    monkeypatch.setattr(re.participation_repository, "get_by_id", _get_by_id)
    monkeypatch.setattr(re.khatm_service, "get_khatm", _get_khatm)
    monkeypatch.setattr(re.khatm_service, "has_started", _has_started)
    monkeypatch.setattr(re.notification_service, "get_preference", _get_pref)
    monkeypatch.setattr(re.settings_service, "get_or_create", _get_settings)
    monkeypatch.setattr(re.allocation_service, "allocate_next_portion_to", _allocate)
    monkeypatch.setattr(re, "_push_portion_content", _push)
    monkeypatch.setattr(re, "_render_or_default", _render)
    monkeypatch.setattr(re, "_notify_user_with_keyboard", _kb)
    monkeypatch.setattr(re.notification_service, "record_sent", _record)

    async def _noop_notify(*a, **k): return None
    delivered = await re.deliver_due_next_portions(object(), _noop_notify, "Asia/Tehran", None)

    assert delivered == 1
    assert ("part-1", NotificationKind.DAILY_REMINDER) in recorded
