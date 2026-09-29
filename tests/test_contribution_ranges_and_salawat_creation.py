from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers import create_khatm
from khatmsaz.bot.handlers.portions import parse_contribution_amount
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("20 تا 31", 12),
        ("۲۰-۳۱", 12),
        ("٢٠–٣١", 12),
        ("20 to 31", 12),
        ("۱۰", 10),
        ("31 تا 20", None),
    ],
)
def test_parse_contribution_amount_accepts_localized_quran_ranges(raw, expected):
    assert parse_contribution_amount(raw) == expected


@pytest.mark.asyncio
async def test_salawat_category_group_always_goes_directly_to_mode(monkeypatch):
    events = []

    class State:
        async def update_data(self, **kwargs):
            events.append(("data", kwargs))

        async def set_state(self, value):
            events.append(("state", value))

    class Message:
        async def answer(self, text, **kwargs):
            events.append(("answer", text))

    callback = SimpleNamespace(message=Message())

    @asynccontextmanager
    async def fake_session_scope():
        yield object()

    async def categories_must_not_be_queried(session, group):
        raise AssertionError("Salawat must never query or show subcategories")

    async def fake_ask_mode(message, state):
        events.append(("ask_mode", None))

    async def noop(*args, **kwargs):
        return None

    monkeypatch.setattr(create_khatm, "session_scope", fake_session_scope)
    monkeypatch.setattr(create_khatm.category_service, "list_active", categories_must_not_be_queried)
    monkeypatch.setattr(create_khatm, "_lang", lambda state: _async_value("fa"))
    monkeypatch.setattr(create_khatm, "_ask_mode", fake_ask_mode)
    monkeypatch.setattr(create_khatm, "safe_clear_inline_keyboard", noop)
    monkeypatch.setattr(create_khatm, "safe_answer_callback", noop)

    await create_khatm._show_category_group(callback, State(), KhatmCategoryGroup.SALAWAT)

    assert ("ask_mode", None) in events
    assert not any(event[0] == "answer" for event in events)


async def _async_value(value):
    return value
