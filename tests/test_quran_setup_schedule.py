from contextlib import asynccontextmanager
from types import SimpleNamespace
from uuid import uuid4

import pytest

from khatmsaz.bot.handlers import portions
from khatmsaz.modules.identity.models import Platform


class FakeState:
    def __init__(self):
        self.cleared = False

    async def clear(self):
        self.cleared = True


class FakeMessage:
    def __init__(self):
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM)
        self.chat = SimpleNamespace(id=123)
        self.answers = []

    async def answer(self, text, reply_markup=None):
        self.answers.append((text, reply_markup))


@pytest.mark.asyncio
async def test_quran_setup_waits_for_selected_hour_before_sending(monkeypatch):
    participation = SimpleNamespace(id=uuid4())
    khatm = SimpleNamespace(id=uuid4())
    session = object()

    @asynccontextmanager
    async def fake_scope():
        yield session

    async def fake_user(*args, **kwargs):
        return SimpleNamespace(id=uuid4())

    async def fake_participation(*args, **kwargs):
        return participation

    async def fake_khatm(*args, **kwargs):
        return khatm

    saved = {}

    async def fake_pages(_session, participation_id, pages):
        saved["pages"] = (participation_id, pages)

    async def fake_preference(_session, participation_id, **kwargs):
        saved["preference"] = (participation_id, kwargs)

    async def must_not_send(*args, **kwargs):
        raise AssertionError("setup must not send or reserve Quran pages immediately")

    monkeypatch.setattr(portions, "session_scope", fake_scope)
    monkeypatch.setattr(portions.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(portions, "_active_participation_for_current_bot", fake_participation)
    monkeypatch.setattr(portions.khatm_service, "get_khatm", fake_khatm)
    monkeypatch.setattr(portions.participation_service, "set_open_reading_pages_per_day", fake_pages)
    monkeypatch.setattr(portions.notification_service, "set_reminder_preference", fake_preference)
    monkeypatch.setattr(portions.participation_service, "advance_open_reading", must_not_send)
    monkeypatch.setattr(portions, "_deliver_quran_pages", must_not_send)

    message = FakeMessage()
    state = FakeState()
    await portions._finish_open_quran_setup(
        message, state,
        {"lang": "fa", "pages_per_day": 4, "khatm_id": str(khatm.id)},
        21,
    )

    assert saved["pages"] == (participation.id, 4)
    assert saved["preference"][1] == {"reminder_hour": 21, "enabled": True}
    assert state.cleared is True
    assert "اولین صفحات هم در همین ساعت می‌رسه" in message.answers[0][0]
