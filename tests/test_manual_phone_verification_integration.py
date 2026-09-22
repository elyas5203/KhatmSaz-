import pytest
from sqlalchemy import delete, select

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.audit_log.models import AuditLog
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.manual_phone_verification import service
from khatmsaz.modules.manual_phone_verification.models import ManualPhoneVerification
from khatmsaz.modules.phone.models import PhoneClaim, PhoneClaimStatus
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_approval_permanently_verifies_foreign_number():
    user_id = new_id()
    admin_id = new_id()
    phone = "+4915112345678"
    async with session_scope() as session:
        session.add_all(
            [User(id=user_id, display_name="Foreign Creator"), User(id=admin_id, role=UserRole.SUPER_ADMIN)]
        )
        session.add(UserSettings(user_id=user_id, contact_phone=phone))
        await session.flush()

        request, created = await service.submit(
            session, user_id=user_id, e164=phone, purpose="CREATOR_VERIFY"
        )
        duplicate, duplicate_created = await service.submit(
            session, user_id=user_id, e164=phone, purpose="CREATOR_VERIFY"
        )
        assert created is True
        assert duplicate_created is False
        assert duplicate.id == request.id

        approved, claim = await service.approve(
            session, request_id=request.id, admin_user_id=admin_id
        )
        assert approved.status == "APPROVED"
        assert approved.reviewed_by_user_id == admin_id
        assert claim.user_id == user_id
        assert claim.e164 == phone
        assert claim.status == PhoneClaimStatus.VERIFIED
        assert (await session.get(UserSettings, user_id)).contact_phone == phone
        audit = await session.scalar(
            select(AuditLog).where(
                AuditLog.action == "MANUAL_PHONE_VERIFY_APPROVE",
                AuditLog.target_user_id == user_id,
            )
        )
        assert audit.actor_user_id == admin_id
        assert audit.details["phone_last4"] == "5678"

        with pytest.raises(service.ManualVerificationError, match="no longer pending"):
            await service.approve(session, request_id=request.id, admin_user_id=admin_id)

        await session.execute(delete(AuditLog).where(AuditLog.target_user_id == user_id))
        await session.execute(
            delete(ManualPhoneVerification).where(ManualPhoneVerification.user_id == user_id)
        )
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == user_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id.in_([user_id, admin_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_manual_rejection_does_not_verify_or_change_profile():
    user_id = new_id()
    admin_id = new_id()
    phone = "+447700900123"
    async with session_scope() as session:
        session.add_all([User(id=user_id), User(id=admin_id, role=UserRole.SUPER_ADMIN)])
        session.add(UserSettings(user_id=user_id, contact_phone=phone))
        await session.flush()
        request, _ = await service.submit(session, user_id=user_id, e164=phone)
        rejected = await service.reject(
            session,
            request_id=request.id,
            admin_user_id=admin_id,
            note="مدرک کافی نیست",
        )
        assert rejected.status == "REJECTED"
        assert rejected.admin_note == "مدرک کافی نیست"
        assert await session.scalar(
            select(PhoneClaim).where(PhoneClaim.user_id == user_id)
        ) is None
        assert (await session.get(UserSettings, user_id)).contact_phone == phone

        await session.execute(delete(AuditLog).where(AuditLog.target_user_id == user_id))
        await session.execute(
            delete(ManualPhoneVerification).where(ManualPhoneVerification.user_id == user_id)
        )
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id.in_([user_id, admin_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_manual_review_rejects_iranian_and_already_owned_numbers():
    user_id = new_id()
    owner_id = new_id()
    owned_foreign = "+14155550123"
    async with session_scope() as session:
        session.add_all([User(id=user_id), User(id=owner_id)])
        session.add(
            PhoneClaim(
                id=new_id(),
                user_id=owner_id,
                e164=owned_foreign,
                status=PhoneClaimStatus.VERIFIED,
            )
        )
        await session.flush()
        with pytest.raises(service.ManualVerificationError, match="Iranian"):
            await service.submit(session, user_id=user_id, e164="+989121234567")
        with pytest.raises(service.ManualVerificationError, match="another account"):
            await service.submit(session, user_id=user_id, e164=owned_foreign)

        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == owner_id))
        await session.execute(delete(User).where(User.id.in_([user_id, owner_id])))
