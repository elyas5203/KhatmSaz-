"""Manual verification for foreign numbers that cannot receive Iranian SMS."""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.identity.models import User, UserStatus
from khatmsaz.modules.manual_phone_verification import repository
from khatmsaz.modules.phone import repository as phone_repository
from khatmsaz.modules.phone.service import normalize_e164
from khatmsaz.modules.settings import service as settings_service


class ManualVerificationError(ValueError):
    pass


def requires_manual_review(e164: str) -> bool:
    return not normalize_e164(e164).startswith("+98")


async def submit(
    session: AsyncSession, *, user_id, e164: str, purpose: str = "CREATOR_VERIFY"
):
    phone = normalize_e164(e164)
    if not requires_manual_review(phone):
        raise ManualVerificationError("Iranian numbers must use SMS OTP")
    user = await session.get(User, user_id, with_for_update=True)
    if (
        user is None
        or user.deleted_at is not None
        or user.status in {UserStatus.MERGED, UserStatus.SUSPENDED, UserStatus.BANNED}
    ):
        raise ManualVerificationError("account is not available")
    await phone_repository.lock_phone(session, phone)
    owner = await phone_repository.verified_claim(session, phone)
    if owner is not None and owner.user_id != user_id:
        raise ManualVerificationError("phone belongs to another account")
    if owner is not None:
        raise ManualVerificationError("phone is already verified")

    pending = await repository.pending_for_user(session, user_id)
    if pending is not None:
        if pending.e164 == phone and pending.purpose == purpose:
            return pending, False
        pending.status = "CANCELLED"
        pending.admin_note = "Superseded by a newer request"
    request = await repository.create(
        session, user_id=user_id, e164=phone, purpose=purpose
    )
    return request, True


async def approve(session: AsyncSession, *, request_id, admin_user_id):
    request = await repository.get_for_update(session, request_id)
    if request is None or request.status != "PENDING":
        raise ManualVerificationError("request is no longer pending")
    await phone_repository.lock_phone(session, request.e164)
    owner = await phone_repository.verified_claim(session, request.e164)
    if owner is not None and owner.user_id != request.user_id:
        raise ManualVerificationError("phone belongs to another account")
    previous = await phone_repository.verified_claim_for_user(session, request.user_id)
    await phone_repository.revoke_user_verified_claims(session, user_id=request.user_id)
    claim = await phone_repository.create_or_verify_claim(
        session, user_id=request.user_id, e164=request.e164
    )
    profile = await settings_service.get_or_create(session, request.user_id)
    profile.contact_phone = request.e164
    await repository.decide(
        session, request, status="APPROVED", reviewed_by_user_id=admin_user_id
    )
    await audit_service.record(
        session,
        actor_user_id=admin_user_id,
        target_user_id=request.user_id,
        action="MANUAL_PHONE_VERIFY_APPROVE",
        details={
            "request_id": str(request.id),
            "phone_last4": request.e164[-4:],
            "purpose": request.purpose,
            "replaced_previous": previous is not None,
        },
    )
    await session.flush()
    return request, claim


async def reject(
    session: AsyncSession, *, request_id, admin_user_id, note: str | None = None
):
    request = await repository.get_for_update(session, request_id)
    if request is None or request.status != "PENDING":
        raise ManualVerificationError("request is no longer pending")
    await repository.decide(
        session,
        request,
        status="REJECTED",
        reviewed_by_user_id=admin_user_id,
        admin_note=note,
    )
    await audit_service.record(
        session,
        actor_user_id=admin_user_id,
        target_user_id=request.user_id,
        action="MANUAL_PHONE_VERIFY_REJECT",
        details={"request_id": str(request.id), "phone_last4": request.e164[-4:]},
    )
    return request
