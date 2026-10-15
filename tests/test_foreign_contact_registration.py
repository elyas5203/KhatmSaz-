"""Shared-contact registration records foreign numbers immediately and safely."""

from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers import member_registration, profile, registration
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.phone import service as phone_service


class State:
    def __init__(self):
        self.data = {"language": "fa"}
        self.current = None

    async def get_data(self):
        return self.data.copy()

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.current = value


@pytest.mark.parametrize("raw,expected", [
    ("4915112345678", "+4915112345678"),
    ("+4915112345678", "+4915112345678"),
    ("00989121234567", "+989121234567"),
    ("09121234567", "+989121234567"),
])
def test_shared_contact_normalization(raw, expected):
    assert phone_service.normalize_shared_contact(raw) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("module", [registration, member_registration])
@pytest.mark.parametrize("raw,contact_user_id,expected_calls,expected_phone", [
    ("4915112345678", 42, 1, "+4915112345678"),
    ("09121234567", 42, 0, "+989121234567"),
    ("4915112345678", 99, 0, None),
    ("4915112345678", None, 0, None),
])
async def test_contact_handler_records_only_self_shared_foreign_number(
    monkeypatch, module, raw, contact_user_id, expected_calls, expected_phone,
):
    calls = []

    @asynccontextmanager
    async def fake_session():
        yield object()

    async def fake_find(*args):
        return SimpleNamespace(id="account-id")

    async def fake_accept(*args, **kwargs):
        calls.append(kwargs)

    async def fake_prompt(*args, **kwargs):
        return None

    async def fake_remove(*args):
        return None

    monkeypatch.setattr(module, "session_scope", fake_session)
    monkeypatch.setattr(module.identity_service, "find_by_platform", fake_find)
    monkeypatch.setattr(module.phone_service, "direct_verify_phone", fake_accept)
    monkeypatch.setattr(module, "_remove_phone_keyboard", fake_remove)
    monkeypatch.setattr(
        module, "_registration_prompt" if module is registration else "_member_reg_prompt",
        fake_prompt,
    )
    state = State()
    message = SimpleNamespace(
        bot=SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM, khatmsaz_language="fa"),
        from_user=SimpleNamespace(id=42),
        contact=SimpleNamespace(phone_number=raw, user_id=contact_user_id),
    )
    await module.receive_shared_contact(message, state)
    assert len(calls) == expected_calls
    assert state.data.get("phone") == expected_phone
    if expected_calls:
        assert calls[0]["e164"] == expected_phone
        assert "FOREIGN_SHARED_CONTACT" in calls[0]["action_context"]


@pytest.mark.asyncio
async def test_profile_share_records_foreign_phone_before_other_questions(monkeypatch):
    calls = []

    @asynccontextmanager
    async def fake_session():
        yield object()

    async def fake_find(*args):
        return SimpleNamespace(id="account-id")

    async def no_claim(*args):
        return None

    async def fake_verify(*args, **kwargs):
        calls.append(kwargs)

    async def fake_prompt(*args, **kwargs):
        return None

    async def answer(*args, **kwargs):
        return SimpleNamespace(delete=fake_prompt)

    monkeypatch.setattr(profile, "session_scope", fake_session)
    monkeypatch.setattr(profile.identity_service, "find_by_platform", fake_find)
    monkeypatch.setattr(profile.phone_repository, "verified_claim_for_user", no_claim)
    monkeypatch.setattr(profile.phone_service, "direct_verify_phone", fake_verify)
    monkeypatch.setattr(profile, "_profile_prompt", fake_prompt)
    state = State()
    message = SimpleNamespace(
        bot=SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM),
        chat=SimpleNamespace(id=42),
        from_user=SimpleNamespace(id=42),
        contact=SimpleNamespace(phone_number="4915112345678", user_id=42),
        answer=answer,
    )
    await profile.enter_phone(message, state)
    assert state.data["phone"] == "+4915112345678"
    assert calls[0]["e164"] == "+4915112345678"
