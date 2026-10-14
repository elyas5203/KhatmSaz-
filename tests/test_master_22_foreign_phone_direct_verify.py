"""Unit and integration tests for MASTER-22: Direct verification for foreign phone numbers."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from sqlalchemy import delete, select

from khatmsaz.bot.handlers.change_phone import (
    ChangePhone,
    ensure_creator_phone_verified,
    receive_new_phone,
)
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.audit_log.models import AuditLog
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole, UserStatus
from khatmsaz.modules.manual_phone_verification.models import ManualPhoneVerification
from khatmsaz.modules.phone import repository as phone_repository
from khatmsaz.modules.phone import service as phone_service
from khatmsaz.modules.phone.models import PhoneClaim, PhoneClaimStatus
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import Gender, UserSettings


class FakeState:
    def __init__(self, data=None):
        self.data = data or {}
        self.state = None

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value

    async def get_state(self):
        return self.state

    async def clear(self):
        self.data = {}
        self.state = None


class FakeMessage:
    def __init__(self, chat_id, text=None):
        self.chat = SimpleNamespace(id=chat_id)
        self.from_user = SimpleNamespace(id=chat_id, is_bot=False)
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM, id=1000)
        self.message = self
        self.text = text
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))
        return SimpleNamespace(message_id=999)

    async def delete(self):
        pass


def test_is_foreign_phone_classifier():
    """Verify foreign phone numbers are correctly identified."""
    assert phone_service.is_foreign_phone("+989121234567") is False
    assert phone_service.is_foreign_phone("09121234567") is False
    assert phone_service.is_foreign_phone("989121234567") is False
    assert phone_service.is_foreign_phone("+12025550123") is True
    assert phone_service.is_foreign_phone("+4915112345678") is True
    assert phone_service.is_foreign_phone("+447911123456") is True
    assert phone_service.is_foreign_phone("+9647701234567") is True
    assert phone_service.is_foreign_phone("invalid") is False


@pytest.mark.asyncio
async def test_direct_verify_phone_unit():
    """Unit test for direct_verify_phone with mocked session."""
    mock_session = AsyncMock()
    user_id = new_id()
    phone = "+12025550123"

    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.deleted_at = None
    mock_user.status = UserStatus.ACTIVE
    mock_session.get.return_value = mock_user

    with (
        patch("khatmsaz.modules.phone.repository.lock_phone", new_callable=AsyncMock) as mock_lock,
        patch("khatmsaz.modules.phone.repository.verified_claim", new_callable=AsyncMock) as mock_verified_claim,
        patch("khatmsaz.modules.phone.repository.verified_claim_for_user", new_callable=AsyncMock) as mock_user_claim,
        patch("khatmsaz.modules.phone.repository.revoke_user_verified_claims", new_callable=AsyncMock) as mock_revoke,
        patch("khatmsaz.modules.phone.repository.create_or_verify_claim", new_callable=AsyncMock) as mock_create_claim,
        patch("khatmsaz.modules.settings.service.get_or_create", new_callable=AsyncMock) as mock_settings,
        patch("khatmsaz.modules.audit_log.service.record", new_callable=AsyncMock) as mock_audit,
    ):
        mock_verified_claim.return_value = None  # Phone not taken
        mock_user_claim.return_value = None
        mock_created = MagicMock()
        mock_created.e164 = phone
        mock_created.user_id = user_id
        mock_create_claim.return_value = mock_created
        mock_user_settings = MagicMock()
        mock_settings.return_value = mock_user_settings

        claim = await phone_service.direct_verify_phone(
            mock_session, user_id=user_id, e164=phone, action_context="UNIT_TEST"
        )

        mock_lock.assert_awaited_once_with(mock_session, phone)
        mock_revoke.assert_awaited_once_with(mock_session, user_id=user_id)
        mock_create_claim.assert_awaited_once_with(mock_session, user_id=user_id, e164=phone)
        assert mock_user_settings.contact_phone == phone
        mock_audit.assert_awaited_once()
        audit_call = mock_audit.await_args[1]
        assert audit_call["details"]["foreign"] is True
        assert audit_call["details"]["context"] == "UNIT_TEST"
        assert claim == mock_created


@pytest.mark.asyncio
async def test_direct_verify_phone_unit_rejects_taken_phone():
    """Unit test: direct_verify_phone raises OtpError when phone belongs to someone else."""
    mock_session = AsyncMock()
    user_id = new_id()
    other_user_id = new_id()
    phone = "+4915112345678"

    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.deleted_at = None
    mock_user.status = UserStatus.ACTIVE
    mock_session.get.return_value = mock_user

    mock_owner = MagicMock()
    mock_owner.user_id = other_user_id

    with (
        patch("khatmsaz.modules.phone.repository.lock_phone", new_callable=AsyncMock),
        patch("khatmsaz.modules.phone.repository.verified_claim", new_callable=AsyncMock, return_value=mock_owner),
    ):
        with pytest.raises(phone_service.OtpError, match="belongs to another account"):
            await phone_service.direct_verify_phone(mock_session, user_id=user_id, e164=phone)


@pytest.mark.asyncio
async def test_ensure_creator_phone_verified_unit_foreign():
    """Unit test: ensure_creator_phone_verified directly verifies foreign numbers and returns True."""
    user_id = new_id()
    phone = "+447911123456"

    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.display_name = "Foreign Creator"

    mock_profile = MagicMock()
    mock_profile.language = "fa"
    mock_profile.contact_phone = phone
    mock_profile.province = "خارج از ایران"
    mock_profile.city = "London"
    mock_profile.gender = Gender.MALE

    mock_session = AsyncMock()
    mock_session_scope = AsyncMock()
    mock_session_scope.__aenter__.return_value = mock_session
    mock_session_scope.__aexit__.return_value = None

    with (
        patch("khatmsaz.bot.handlers.change_phone.session_scope", return_value=mock_session_scope),
        patch("khatmsaz.modules.identity.service.resolve_or_provision_user", new_callable=AsyncMock, return_value=mock_user),
        patch("khatmsaz.modules.settings.service.get_or_create", new_callable=AsyncMock, return_value=mock_profile),
        patch("khatmsaz.modules.phone.repository.verified_claim_for_user", new_callable=AsyncMock, return_value=None),
        patch("khatmsaz.modules.phone.service.direct_verify_phone", new_callable=AsyncMock) as mock_direct,
        patch("khatmsaz.bot.handlers.change_phone.notify_admins_of_manual_request", new_callable=AsyncMock) as mock_notify,
    ):
        msg = FakeMessage(chat_id="12345")
        state = FakeState()

        allowed = await ensure_creator_phone_verified(msg, state)

        assert allowed is True
        mock_direct.assert_awaited_once_with(
            mock_session,
            user_id=user_id,
            e164=phone,
            action_context="CREATOR_FOREIGN_DIRECT_VERIFY",
        )
        mock_notify.assert_not_called()
        assert await state.get_state() is None


@pytest.mark.asyncio
async def test_receive_new_phone_unit_foreign():
    """Unit test: receive_new_phone directly updates and verifies foreign numbers."""
    user_id = new_id()
    new_phone = "+12025550199"

    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.display_name = "New York User"

    mock_session = AsyncMock()
    mock_session_scope = AsyncMock()
    mock_session_scope.__aenter__.return_value = mock_session
    mock_session_scope.__aexit__.return_value = None

    with (
        patch("khatmsaz.bot.handlers.change_phone.session_scope", return_value=mock_session_scope),
        patch("khatmsaz.modules.identity.service.find_by_platform", new_callable=AsyncMock, return_value=mock_user),
        patch("khatmsaz.modules.phone.service.direct_verify_phone", new_callable=AsyncMock) as mock_direct,
        patch("khatmsaz.bot.handlers.change_phone.notify_admins_of_manual_request", new_callable=AsyncMock) as mock_notify,
    ):
        msg = FakeMessage(chat_id="12345", text=new_phone)
        state = FakeState(data={"lang": "fa"})
        await state.set_state(ChangePhone.entering_phone)

        await receive_new_phone(msg, state)

        mock_direct.assert_awaited_once_with(
            mock_session,
            user_id=user_id,
            e164=new_phone,
            action_context="CHANGE_PHONE_FOREIGN_DIRECT_VERIFY",
        )
        mock_notify.assert_not_called()
        assert await state.get_state() is None
        assert len(msg.answers) >= 1
        reply_text = msg.answers[-1][0]
        assert new_phone in reply_text or "تغییر یافت" in reply_text


# --- PostgreSQL Integration Tests (Run when RUN_INTEGRATION_TESTS=1) ---

@pytest.mark.integration
@pytest.mark.asyncio
async def test_direct_verify_phone_creates_verified_claim_and_audit():
    """Integration: direct_verify_phone against real PostgreSQL."""
    user_id = new_id()
    phone = "+12025550999"
    async with session_scope() as session:
        user = User(id=user_id, display_name="Foreign Member", role=UserRole.USER, status=UserStatus.ACTIVE)
        session.add(user)
        session.add(UserSettings(user_id=user_id))
        await session.flush()

        claim = await phone_service.direct_verify_phone(
            session, user_id=user_id, e164=phone, action_context="TEST_FOREIGN"
        )
        assert claim.user_id == user_id
        assert claim.e164 == phone
        assert claim.status == PhoneClaimStatus.VERIFIED
        assert claim.verified_at is not None

        # Check UserSettings updated
        settings = await session.get(UserSettings, user_id)
        assert settings.contact_phone == phone

        # Cleanup
        await session.execute(delete(AuditLog).where(AuditLog.target_user_id == user_id))
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == user_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_direct_verify_phone_rejects_taken_phone():
    """Integration: direct_verify_phone refuses to verify a phone already claimed by another account."""
    user1_id = new_id()
    user2_id = new_id()
    phone = "+4915199999999"
    async with session_scope() as session:
        session.add_all([
            User(id=user1_id, display_name="User 1", role=UserRole.USER, status=UserStatus.ACTIVE),
            User(id=user2_id, display_name="User 2", role=UserRole.USER, status=UserStatus.ACTIVE),
        ])
        await session.flush()

        # User 1 claims phone
        await phone_service.direct_verify_phone(session, user_id=user1_id, e164=phone)

        # User 2 tries to claim same phone -> must raise OtpError
        with pytest.raises(phone_service.OtpError, match="belongs to another account"):
            await phone_service.direct_verify_phone(session, user_id=user2_id, e164=phone)

        # Cleanup
        await session.execute(delete(AuditLog).where(AuditLog.target_user_id.in_([user1_id, user2_id])))
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id.in_([user1_id, user2_id])))
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([user1_id, user2_id])))
        await session.execute(delete(User).where(User.id.in_([user1_id, user2_id])))
