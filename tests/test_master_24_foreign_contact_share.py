"""Unit and integration tests for MASTER-24:
Direct registration and verification for foreign phone numbers via Telegram Contact Share button."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from khatmsaz.bot.handlers.change_phone import (
    ChangePhone,
    ensure_creator_phone_verified,
    receive_new_phone,
)
from khatmsaz.bot.handlers.profile import (
    ProfileEdit,
    enter_phone as profile_enter_phone,
)
from khatmsaz.bot.handlers.registration import (
    Registration,
    receive_shared_contact as reg_receive_shared_contact,
)
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import Platform, User, UserStatus
from khatmsaz.modules.phone import service as phone_service


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
    def __init__(self, chat_id, text=None, contact_phone=None):
        self.chat = SimpleNamespace(id=chat_id)
        self.from_user = SimpleNamespace(id=chat_id, is_bot=False)
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM, id=1000)
        self.message = self
        self.text = text
        self.contact = SimpleNamespace(phone_number=contact_phone) if contact_phone else None
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))
        return SimpleNamespace(message_id=999, delete=AsyncMock())

    async def delete(self):
        pass


def test_normalize_e164_foreign_contact_share():
    """Verify normalize_e164 accurately parses foreign numbers without leading plus (Telegram contact format)."""
    # US / Canada (11 digits, starts with 1)
    assert phone_service.normalize_e164("14155552671") == "+14155552671"
    assert phone_service.is_foreign_phone("14155552671") is True

    # UK (12 digits, starts with 44)
    assert phone_service.normalize_e164("447911123456") == "+447911123456"
    assert phone_service.is_foreign_phone("447911123456") is True

    # Germany (12 digits, starts with 49)
    assert phone_service.normalize_e164("491512345678") == "+491512345678"
    assert phone_service.is_foreign_phone("491512345678") is True

    # Iraq (13 digits, starts with 964)
    assert phone_service.normalize_e164("9647701234567") == "+9647701234567"
    assert phone_service.is_foreign_phone("9647701234567") is True

    # Turkey (12 digits, starts with 90)
    assert phone_service.normalize_e164("905321234567") == "+905321234567"
    assert phone_service.is_foreign_phone("905321234567") is True

    # Afghanistan (11 digits, starts with 93)
    assert phone_service.normalize_e164("93701234567") == "+93701234567"
    assert phone_service.is_foreign_phone("93701234567") is True

    # UAE (12 digits, starts with 971)
    assert phone_service.normalize_e164("971501234567") == "+971501234567"
    assert phone_service.is_foreign_phone("971501234567") is True


def test_normalize_e164_iranian_numbers():
    """Verify Iranian numbers remain properly classified as non-foreign."""
    # Standard domestic mobile 09...
    assert phone_service.normalize_e164("09121234567") == "+989121234567"
    assert phone_service.is_foreign_phone("09121234567") is False

    # Iranian Telegram contact without plus 98...
    assert phone_service.normalize_e164("989121234567") == "+989121234567"
    assert phone_service.is_foreign_phone("989121234567") is False

    # Iranian with plus +98...
    assert phone_service.normalize_e164("+989121234567") == "+989121234567"
    assert phone_service.is_foreign_phone("+989121234567") is False

    # Iranian 10 digits without 0
    assert phone_service.normalize_e164("9121234567") == "+989121234567"
    assert phone_service.is_foreign_phone("9121234567") is False


def test_normalize_e164_persian_and_arabic_numerals():
    """Verify Persian and Arabic numerals are normalized to ASCII digits."""
    assert phone_service.normalize_e164("۰۹۱۲۱۲۳۴۵۶۷") == "+989121234567"
    assert phone_service.normalize_e164("۱۴۱۵۵۵۵۲۶۷۱") == "+14155552671"
    assert phone_service.normalize_e164("٠٩١٢١٢٣٤٥٦٧") == "+989121234567"


def test_normalize_e164_invalid_inputs():
    """Verify invalid inputs raise OtpError."""
    with pytest.raises(phone_service.OtpError):
        phone_service.normalize_e164("")
    with pytest.raises(phone_service.OtpError):
        phone_service.normalize_e164("123")
    with pytest.raises(phone_service.OtpError):
        phone_service.normalize_e164("abc")


@pytest.mark.asyncio
async def test_profile_contact_share_foreign_number_direct_verify():
    """When a creator shares a foreign contact in ProfileEdit, it directly verifies without error."""
    chat_id = 12345
    state = FakeState({"language": "fa"})
    message = FakeMessage(chat_id, contact_phone="14155552671")  # US number without plus

    mock_user = MagicMock(spec=User)
    mock_user.id = new_id()

    with (
        patch("khatmsaz.modules.identity.service.find_by_platform", new_callable=AsyncMock) as mock_find_user,
        patch("khatmsaz.modules.phone.repository.verified_claim_for_user", new_callable=AsyncMock) as mock_claim,
        patch("khatmsaz.modules.phone.service.direct_verify_phone", new_callable=AsyncMock) as mock_direct_verify,
        patch("khatmsaz.bot.handlers.profile._profile_prompt", new_callable=AsyncMock) as mock_prompt,
    ):
        mock_find_user.return_value = mock_user
        mock_claim.return_value = None

        await profile_enter_phone(message, state)

        # 1. State must advance to choosing_province
        assert state.state == ProfileEdit.choosing_province
        # 2. Normalized phone and foreign flag must be recorded in state
        assert state.data["phone"] == "+14155552671"
        assert state.data["foreign_verified_phone"] is True
        # 3. Direct verification was invoked immediately
        mock_direct_verify.assert_awaited_once()
        assert mock_direct_verify.call_args[1]["e164"] == "+14155552671"
        assert mock_direct_verify.call_args[1]["user_id"] == mock_user.id


@pytest.mark.asyncio
async def test_profile_contact_share_iranian_number_requires_otp():
    """When a creator shares an Iranian contact in ProfileEdit, it does NOT direct-verify."""
    chat_id = 12345
    state = FakeState({"language": "fa"})
    message = FakeMessage(chat_id, contact_phone="989121234567")  # Iranian number without plus

    mock_user = MagicMock(spec=User)
    mock_user.id = new_id()

    with (
        patch("khatmsaz.modules.identity.service.find_by_platform", new_callable=AsyncMock) as mock_find_user,
        patch("khatmsaz.modules.phone.repository.verified_claim_for_user", new_callable=AsyncMock) as mock_claim,
        patch("khatmsaz.modules.phone.service.direct_verify_phone", new_callable=AsyncMock) as mock_direct_verify,
        patch("khatmsaz.bot.handlers.profile._profile_prompt", new_callable=AsyncMock) as mock_prompt,
    ):
        mock_find_user.return_value = mock_user
        mock_claim.return_value = None

        await profile_enter_phone(message, state)

        assert state.state == ProfileEdit.choosing_province
        assert state.data["phone"] == "+989121234567"
        assert "foreign_verified_phone" not in state.data
        # Must NOT direct verify Iranian phone
        mock_direct_verify.assert_not_awaited()


@pytest.mark.asyncio
async def test_registration_contact_share_foreign_number_direct_verify():
    """When a user shares a foreign contact during initial registration, it directly verifies."""
    chat_id = 998877
    state = FakeState({"language": "fa"})
    message = FakeMessage(chat_id, contact_phone="447911123456")  # UK number without plus

    mock_user = MagicMock(spec=User)
    mock_user.id = new_id()

    with (
        patch("khatmsaz.modules.identity.service.find_by_platform", new_callable=AsyncMock) as mock_find_user,
        patch("khatmsaz.modules.phone.service.direct_verify_phone", new_callable=AsyncMock) as mock_direct_verify,
        patch("khatmsaz.bot.handlers.registration._registration_prompt", new_callable=AsyncMock) as mock_prompt,
        patch("khatmsaz.bot.handlers.registration._remove_phone_keyboard", new_callable=AsyncMock),
    ):
        mock_find_user.return_value = mock_user

        await reg_receive_shared_contact(message, state)

        assert state.state == Registration.choosing_province
        assert state.data["phone"] == "+447911123456"
        assert state.data["foreign_verified_phone"] is True
        mock_direct_verify.assert_awaited_once()
        assert mock_direct_verify.call_args[1]["e164"] == "+447911123456"


@pytest.mark.asyncio
async def test_change_phone_contact_share_foreign_number_direct_verify():
    """When a user changes phone and shares a foreign contact, it directly verifies and finishes."""
    chat_id = 776655
    state = FakeState({"lang": "fa"})
    message = FakeMessage(chat_id, contact_phone="9647701234567")  # Iraqi number without plus

    mock_user = MagicMock(spec=User)
    mock_user.id = new_id()

    with (
        patch("khatmsaz.modules.identity.service.find_by_platform", new_callable=AsyncMock) as mock_find_user,
        patch("khatmsaz.modules.phone.service.direct_verify_phone", new_callable=AsyncMock) as mock_direct_verify,
        patch("khatmsaz.bot.handlers.create_khatm.resume_khatm_creation_if_pending", new_callable=AsyncMock, return_value=False),
    ):
        mock_find_user.return_value = mock_user

        await receive_new_phone(message, state)

        # State should be cleared upon successful direct verification
        assert await state.get_state() is None
        mock_direct_verify.assert_awaited_once()
        assert mock_direct_verify.call_args[1]["e164"] == "+9647701234567"
        assert len(message.answers) == 1
        assert "+9647701234567" in message.answers[0][0]
