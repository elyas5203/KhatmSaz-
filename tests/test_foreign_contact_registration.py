"""Shared-contact registration records foreign numbers immediately and safely."""

from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers import member_registration, registration
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
    monkeypatch.setattr(module.phone_service, "accept_shared_foreign_contact", fake_accept)
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
        assert calls[0]["contact_user_id"] == 42


@pytest.mark.asyncio
async def test_foreign_contact_service_saves_phone_and_claim_in_one_step(monkeypatch):
    events = []
    profile = SimpleNamespace(contact_phone=None)

    class Session:
        async def get(self, *args, **kwargs):
            return SimpleNamespace(deleted_at=None, status=None)

        async def flush(self):
            events.append("flush")

    async def lock(*args, **kwargs):
        events.append("lock")

    async def owner(*args, **kwargs):
        return None

    async def revoke(*args, **kwargs):
        events.append("revoke")

    async def create(*args, **kwargs):
        events.append("claim")

    async def get_profile(*args, **kwargs):
        return profile

    monkeypatch.setattr(phone_service.repository, "lock_phone", lock)
    monkeypatch.setattr(phone_service.repository, "verified_claim", owner)
    monkeypatch.setattr(phone_service.repository, "revoke_user_verified_claims", revoke)
    monkeypatch.setattr(phone_service.repository, "create_or_verify_claim", create)
    monkeypatch.setattr(phone_service.settings_service, "get_or_create", get_profile)

    await phone_service.accept_shared_foreign_contact(
        Session(), user_id="account-id", e164="+4915112345678",
        contact_user_id=42, sender_id=42,
    )
    assert profile.contact_phone == "+4915112345678"
    assert events == ["lock", "revoke", "claim", "flush"]

    with pytest.raises(phone_service.OtpError):
        await phone_service.accept_shared_foreign_contact(
            Session(), user_id="account-id", e164="+989121234567",
            contact_user_id=42, sender_id=42,
        )
