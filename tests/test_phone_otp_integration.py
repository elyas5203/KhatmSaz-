import pytest
from sqlalchemy import delete, select

from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.audit_log.models import AuditLog
from khatmsaz.modules.phone import service
from khatmsaz.modules.phone.models import OtpChallenge, OtpPurpose, PhoneClaim, PhoneClaimStatus
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.modules.wallet.models import Wallet


def test_phone_normalization_accepts_common_iranian_forms():
    assert service.normalize_e164("0912 123 4567") == "+989121234567"
    assert service.normalize_e164("989121234567") == "+989121234567"
    assert service.normalize_e164("00989121234567") == "+989121234567"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_phone_otp_verification_and_platform_link(monkeypatch):
    monkeypatch.setenv("OTP_HMAC_SECRET", "integration-secret")
    monkeypatch.setenv("DEV_OTP", "true")
    get_settings.cache_clear()
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        await session.flush()
        challenge, code = await service.request_challenge(
            session, user_id=user_id, e164="+989121234567", purpose=OtpPurpose.PHONE_LOGIN
        )
        assert code is not None
        claim = await service.verify_and_link_platform_identity(
            session, challenge_id=challenge.id, user_id=user_id, code=code,
            platform=Platform.BALE, subject="bale-user-1",
        )
        assert claim.e164 == "+989121234567"
        with pytest.raises(service.OtpError):
            await service.verify_challenge(session, challenge_id=challenge.id, user_id=user_id, code=code)
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
    get_settings.cache_clear()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_phone_change_preserves_account_history(monkeypatch):
    monkeypatch.setenv("OTP_HMAC_SECRET", "integration-secret")
    monkeypatch.setenv("DEV_OTP", "true")
    get_settings.cache_clear()
    user_id = new_id()
    wallet_id = new_id()
    old_phone = "+989121110001"
    new_phone = "+989121110002"
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="Phone Change Test"))
        session.add(UserSettings(user_id=user_id, contact_phone=old_phone))
        session.add(Wallet(id=wallet_id, user_id=user_id, balance_toman=125_000, credit_toman=500))
        old_claim = PhoneClaim(
            id=new_id(),
            user_id=user_id,
            e164=old_phone,
            status=PhoneClaimStatus.VERIFIED,
        )
        session.add(old_claim)
        await session.flush()

        challenge, code = await service.request_phone_change_challenge(
            session, user_id=user_id, e164="0912 111 0002"
        )
        claim = await service.complete_phone_change(
            session, user_id=user_id, challenge_id=challenge.id, code=code
        )

        assert claim.user_id == user_id
        assert claim.e164 == new_phone
        assert old_claim.status == PhoneClaimStatus.REVOKED
        assert old_claim.revoked_at is not None
        settings = await session.get(UserSettings, user_id)
        wallet = await session.get(Wallet, wallet_id)
        assert settings.contact_phone == new_phone
        assert wallet.user_id == user_id
        assert wallet.balance_toman == 125_000
        audit = await session.scalar(
            select(AuditLog).where(
                AuditLog.actor_user_id == user_id,
                AuditLog.action == "PHONE_CHANGE",
            )
        )
        assert audit.target_user_id == user_id
        assert audit.details == {"new_phone_last4": "0002"}

        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user_id))
        await session.execute(delete(OtpChallenge).where(OtpChallenge.user_id == user_id))
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == user_id))
        await session.execute(delete(Wallet).where(Wallet.user_id == user_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
    get_settings.cache_clear()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_phone_change_rejects_number_owned_by_another_account(monkeypatch):
    monkeypatch.setenv("OTP_HMAC_SECRET", "integration-secret")
    get_settings.cache_clear()
    user_id = new_id()
    owner_id = new_id()
    owned_phone = "+989121110003"
    async with session_scope() as session:
        session.add_all([User(id=user_id), User(id=owner_id)])
        session.add(
            PhoneClaim(
                id=new_id(),
                user_id=owner_id,
                e164=owned_phone,
                status=PhoneClaimStatus.VERIFIED,
            )
        )
        await session.flush()

        with pytest.raises(service.OtpError, match="another account"):
            await service.request_phone_change_challenge(
                session, user_id=user_id, e164=owned_phone
            )
        assert await session.scalar(
            select(PhoneClaim).where(
                PhoneClaim.user_id == owner_id,
                PhoneClaim.e164 == owned_phone,
                PhoneClaim.status == PhoneClaimStatus.VERIFIED,
            )
        )

        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == owner_id))
        await session.execute(delete(User).where(User.id.in_([user_id, owner_id])))
    get_settings.cache_clear()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_first_creator_phone_verification_keeps_same_user(monkeypatch):
    monkeypatch.setenv("OTP_HMAC_SECRET", "integration-secret")
    get_settings.cache_clear()
    user_id = new_id()
    phone = "+989121110004"
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="Creator Verification Test"))
        session.add(UserSettings(user_id=user_id, contact_phone=phone))
        await session.flush()

        challenge, code = await service.request_phone_change_challenge(
            session, user_id=user_id, e164=phone
        )
        claim = await service.complete_phone_change(
            session, user_id=user_id, challenge_id=challenge.id, code=code
        )

        assert claim.user_id == user_id
        assert claim.e164 == phone
        audit = await session.scalar(
            select(AuditLog).where(
                AuditLog.actor_user_id == user_id,
                AuditLog.action == "PHONE_VERIFY",
            )
        )
        assert audit is not None
        assert audit.details == {"new_phone_last4": "0004"}

        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user_id))
        await session.execute(delete(OtpChallenge).where(OtpChallenge.user_id == user_id))
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == user_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
    get_settings.cache_clear()
