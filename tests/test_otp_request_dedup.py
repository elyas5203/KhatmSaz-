from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from khatmsaz.modules.phone import service
from khatmsaz.modules.phone.models import OtpPurpose


@pytest.mark.asyncio
async def test_active_otp_is_reused_without_returning_another_sms_code(monkeypatch):
    existing = SimpleNamespace(id=uuid4())
    calls = []

    async def fake_lock(*args, **kwargs):
        calls.append("lock")

    async def fake_reusable(*args, **kwargs):
        calls.append("lookup")
        return existing

    async def must_not_run(*args, **kwargs):
        raise AssertionError("an active OTP must not be superseded or recreated")

    monkeypatch.setattr(service.repository, "lock_challenge_request", fake_lock)
    monkeypatch.setattr(service.repository, "get_reusable_challenge", fake_reusable)
    monkeypatch.setattr(service.repository, "supersede_open_challenges", must_not_run)
    monkeypatch.setattr(service.repository, "create_challenge", must_not_run)

    challenge, code = await service.request_challenge(
        object(), user_id=uuid4(), e164="09126807599",
        purpose=OtpPurpose.PHONE_VERIFICATION,
    )

    assert challenge is existing
    assert code is None
    assert calls == ["lock", "lookup"]


def test_otp_is_valid_for_five_minutes():
    assert service.OTP_TTL == timedelta(minutes=5)
