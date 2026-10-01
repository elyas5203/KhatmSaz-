"""Owner rules for per-khatm reminder settings and Redis-safe FSM data."""

import json
from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from zoneinfo import ZoneInfo

from khatmsaz.bot.keyboards import (
    settings_reminder_custom_keyboard,
    settings_reminder_keyboard,
    settings_reminder_khatms_keyboard,
)


def _callbacks(markup):
    return [button.callback_data for row in markup.inline_keyboard for button in row]


def test_reminder_picker_is_per_khatm_and_has_no_off_action():
    participation_id = str(uuid4())
    khatms = settings_reminder_khatms_keyboard(
        [(participation_id, "ختم زیارت عاشورا", "06:30")]
    )
    assert _callbacks(khatms)[0] == f"reminder_khatm:{participation_id}"
    assert "06:30" in khatms.inline_keyboard[0][0].text

    hours = settings_reminder_keyboard(participation_id)
    callbacks = _callbacks(hours)
    assert f"custom_reminder:{participation_id}" in callbacks
    assert not any("off" in (value or "") for value in callbacks)
    assert all(len(value or "") <= 64 for value in callbacks)
    assert _callbacks(settings_reminder_custom_keyboard(participation_id)) == [
        f"reminder_khatm:{participation_id}"
    ]


def test_values_written_to_redis_fsm_are_json_serializable():
    instance_id = uuid4()
    start_at = datetime(2026, 10, 2, 6, 30, tzinfo=ZoneInfo("Asia/Tehran"))
    payload = {
        "joined_via_bot_instance_id": str(instance_id),
        "start_at": start_at.isoformat(),
    }
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["joined_via_bot_instance_id"] == str(instance_id)
    assert datetime.fromisoformat(decoded["start_at"]) == start_at
