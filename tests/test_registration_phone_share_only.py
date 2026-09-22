"""Owner request (2026-09-22): during initial registration on Telegram,
only the "share my number" button should work — a manually typed number
must be rejected (asked again), since Telegram's own verified contact
share is less error-prone than free-typed text. Bale has no
`request_contact` equivalent, so Bale users must still be able to type.
See `bot/handlers/registration.py::enter_phone`."""

from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers.registration import Registration, enter_phone
from khatmsaz.modules.identity.models import Platform


class FakeState:
    def __init__(self, data):
        self.data = data
        self.state = Registration.entering_phone

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value

    async def clear(self):
        self.data = {}
        self.state = None


class FakeMessage:
    def __init__(self, text, platform):
        self.chat = SimpleNamespace(id=1)
        self.bot = SimpleNamespace(khatmsaz_platform=platform)
        self.text = text
        self.contact = None
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))


@pytest.mark.asyncio
async def test_telegram_typed_phone_is_rejected_during_registration():
    state = FakeState({"language": "fa"})
    message = FakeMessage("09121234567", Platform.TELEGRAM)
    await enter_phone(message, state)
    assert state.state == Registration.entering_phone  # did not advance
    assert "phone" not in state.data
    assert "دکمه" in message.answers[0][0]


@pytest.mark.asyncio
async def test_bale_typed_phone_is_still_accepted_during_registration():
    state = FakeState({"language": "fa"})
    message = FakeMessage("09121234567", Platform.BALE)
    await enter_phone(message, state)
    assert state.state == Registration.choosing_province
    assert state.data.get("phone") == "+989121234567"
