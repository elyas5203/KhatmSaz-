"""OTP-backed phone ownership and safe cross-platform identity linking."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.config import get_settings
from khatmsaz.core.ids import new_id
from khatmsaz.modules.account_merge.models import AccountMerge
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.identity import repository as identity_repository
from khatmsaz.modules.identity.models import Platform, User, UserStatus
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.phone import repository
from khatmsaz.modules.phone.models import OtpPurpose
from khatmsaz.modules.settings import repository as settings_repository
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.wallet.models import Wallet

OTP_TTL = timedelta(minutes=10)
MAX_ATTEMPTS = 5


class OtpError(ValueError):
    pass


def normalize_e164(raw: str) -> str:
    value = "".join(raw.strip().replace("-", "").split())
    if value.startswith("00"):
        value = "+" + value[2:]
    elif value.startswith("09") and len(value) == 11:
        value = "+98" + value[1:]
    elif value.startswith("98") and not value.startswith("+"):
        value = "+" + value
    if not value.startswith("+") or not value[1:].isdigit() or not (8 <= len(value[1:]) <= 15):
        raise OtpError("phone must be a valid E.164 number")
    return value


def phone_storage_variants(e164: str) -> set[str]:
    """Forms accepted by the old registration flow before E.164 normalization."""
    normalized = normalize_e164(e164)
    values = {normalized, normalized.removeprefix("+")}
    if normalized.startswith("+98"):
        values.add("0" + normalized[3:])
    return values


def _hash_code(code: str) -> str:
    secret = get_settings().otp_hmac_secret
    if not secret:
        raise OtpError("OTP service is not configured")
    return hmac.new(secret.encode(), code.encode(), hashlib.sha256).hexdigest()


async def request_challenge(session: AsyncSession, *, user_id, e164: str, purpose: OtpPurpose = OtpPurpose.PHONE_LOGIN) -> tuple[object, str | None]:
    phone = normalize_e164(e164)
    await repository.supersede_open_challenges(session, user_id=user_id, e164=phone, purpose=purpose)
    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge = await repository.create_challenge(
        session, user_id=user_id, e164=phone, purpose=purpose, code_hash=_hash_code(code),
        attempts=0, max_attempts=MAX_ATTEMPTS, expires_at=datetime.now(timezone.utc) + OTP_TTL,
    )
    # The raw code is returned only to the caller that owns the SMS provider.
    # Production handlers must send it through SmsProvider and never display it.
    return challenge, code


async def _assert_pristine_source_account(session: AsyncSession, source: User) -> None:
    settings = await settings_repository.get_by_user(session, source.id)
    has_profile = bool(
        source.display_name
        or (
            settings
            and (settings.contact_phone or settings.province or settings.city or settings.gender)
        )
    )
    owned_khatms = int(
        await session.scalar(
            select(func.count()).select_from(Khatm).where(Khatm.creator_user_id == source.id)
        )
        or 0
    )
    participations = int(
        await session.scalar(
            select(func.count()).select_from(Participation).where(Participation.user_id == source.id)
        )
        or 0
    )
    wallet = await session.scalar(select(Wallet.id).where(Wallet.user_id == source.id))
    if has_profile or owned_khatms or participations or wallet is not None:
        raise OtpError("current provisional account is no longer empty")


async def request_account_link_challenge(
    session: AsyncSession, *, source_user_id, e164: str
):
    """Find the existing profile by phone and bind an OTP to that owner."""
    phone = normalize_e164(e164)
    source = await session.get(User, source_user_id)
    if source is None:
        raise OtpError("source account not found")
    await _assert_pristine_source_account(session, source)
    matches = await settings_repository.find_by_contact_phones(
        session, phone_storage_variants(phone)
    )
    owner_ids = {item.user_id for item in matches}
    if not owner_ids:
        raise OtpError("existing account not found")
    if len(owner_ids) != 1:
        raise OtpError("phone is attached to multiple accounts")
    target_user_id = owner_ids.pop()
    if target_user_id == source.id:
        raise OtpError("account is already linked")
    target = await session.get(User, target_user_id)
    if target is None or target.deleted_at is not None or target.status == UserStatus.MERGED:
        raise OtpError("existing account is not available")
    challenge, code = await request_challenge(
        session,
        user_id=target.id,
        e164=phone,
        purpose=OtpPurpose.PHONE_LOGIN,
    )
    return target, challenge, code


async def request_phone_change_challenge(session: AsyncSession, *, user_id, e164: str):
    """Start verification of a replacement number without moving the user account."""
    phone = normalize_e164(e164)
    user = await session.get(User, user_id)
    if (
        user is None
        or user.deleted_at is not None
        or user.status in {UserStatus.MERGED, UserStatus.SUSPENDED, UserStatus.BANNED}
    ):
        raise OtpError("account is not available")
    current = await repository.get_user_verified_claim(session, user_id, phone)
    if current is not None:
        raise OtpError("phone is already verified for this account")
    owner = await repository.verified_claim(session, phone)
    if owner is not None and owner.user_id != user_id:
        raise OtpError("phone belongs to another account")
    return await request_challenge(
        session,
        user_id=user_id,
        e164=phone,
        purpose=OtpPurpose.PHONE_VERIFICATION,
    )


async def complete_account_link(
    session: AsyncSession,
    *,
    source_user_id,
    target_user_id,
    challenge_id,
    code: str,
    platform: Platform,
    subject: str,
) -> User:
    """Move one provisional platform identity to the verified canonical user."""
    if source_user_id == target_user_id:
        raise OtpError("account is already linked")
    await verify_challenge(
        session, challenge_id=challenge_id, user_id=target_user_id, code=code
    )
    source = await session.get(User, source_user_id, with_for_update=True)
    target = await session.get(User, target_user_id, with_for_update=True)
    if source is None or target is None:
        raise OtpError("account not found")
    await _assert_pristine_source_account(session, source)
    identity = await identity_repository.get_platform_identity(session, platform, str(subject))
    if identity is None or identity.user_id != source.id:
        raise OtpError("platform identity changed during verification")
    identity.user_id = target.id
    source.status = UserStatus.MERGED
    source.merged_into_id = target.id
    session.add(
        AccountMerge(
            id=new_id(),
            winner_user_id=target.id,
            loser_user_id=source.id,
            verified_e164=normalize_e164(
                (await repository.get_challenge(session, challenge_id)).e164
            ),
            initiating_challenge_id=challenge_id,
            moved_platform_identities=1,
            moved_phone_claims=0,
            context="SELF_SERVICE_PLATFORM_LINK",
        )
    )
    await session.flush()
    return target


async def _consume_challenge(
    session: AsyncSession,
    *,
    challenge_id,
    user_id,
    code: str,
    expected_purpose: OtpPurpose | None = None,
):
    challenge = await repository.get_challenge(session, challenge_id)
    if challenge is None or challenge.user_id != user_id:
        raise OtpError("challenge not found")
    if expected_purpose is not None and challenge.purpose != expected_purpose:
        raise OtpError("challenge purpose mismatch")
    if challenge.consumed_at is not None or challenge.superseded_at is not None:
        raise OtpError("challenge is no longer valid")
    if challenge.expires_at <= datetime.now(timezone.utc):
        raise OtpError("challenge expired")
    if challenge.attempts >= challenge.max_attempts:
        raise OtpError("too many attempts")
    challenge.attempts += 1
    if not hmac.compare_digest(challenge.code_hash, _hash_code(code.strip())):
        await session.flush()
        raise OtpError("invalid code")
    challenge.consumed_at = datetime.now(timezone.utc)
    await session.flush()
    return challenge


async def verify_challenge(session: AsyncSession, *, challenge_id, user_id, code: str):
    challenge = await _consume_challenge(
        session, challenge_id=challenge_id, user_id=user_id, code=code
    )
    await repository.lock_phone(session, challenge.e164)
    owner = await repository.verified_claim(session, challenge.e164)
    if owner is not None and owner.user_id != user_id:
        raise OtpError("phone belongs to another account")
    return await repository.create_or_verify_claim(
        session, user_id=user_id, e164=challenge.e164
    )


async def complete_phone_change(
    session: AsyncSession, *, user_id, challenge_id, code: str
):
    """Atomically replace the verified phone while preserving the canonical user."""
    user = await session.get(User, user_id, with_for_update=True)
    if (
        user is None
        or user.deleted_at is not None
        or user.status in {UserStatus.MERGED, UserStatus.SUSPENDED, UserStatus.BANNED}
    ):
        raise OtpError("account is not available")
    challenge = await _consume_challenge(
        session,
        challenge_id=challenge_id,
        user_id=user_id,
        code=code,
        expected_purpose=OtpPurpose.PHONE_VERIFICATION,
    )
    await repository.lock_phone(session, challenge.e164)
    owner = await repository.verified_claim(session, challenge.e164)
    if owner is not None and owner.user_id != user_id:
        raise OtpError("phone belongs to another account")

    previous_claim = await repository.verified_claim_for_user(session, user_id)
    # The database allows only one verified claim per user. Revoke the old
    # claim first; both changes are still part of one transaction and roll
    # back together if insertion of the replacement fails.
    await repository.revoke_user_verified_claims(session, user_id=user_id)
    claim = await repository.create_or_verify_claim(
        session, user_id=user_id, e164=challenge.e164
    )
    user_settings = await settings_service.get_or_create(session, user_id)
    user_settings.contact_phone = challenge.e164
    await audit_service.record(
        session,
        actor_user_id=user_id,
        target_user_id=user_id,
        action="PHONE_CHANGE" if previous_claim is not None else "PHONE_VERIFY",
        details={"new_phone_last4": challenge.e164[-4:]},
    )
    await session.flush()
    return claim


async def verify_and_link_platform_identity(
    session: AsyncSession, *, challenge_id, user_id, code: str, platform: Platform, subject: str
) -> None:
    claim = await verify_challenge(session, challenge_id=challenge_id, user_id=user_id, code=code)
    existing = await identity_repository.find_by_platform_identity(session, platform, str(subject))
    if existing is not None and existing.id != user_id:
        raise OtpError("platform identity belongs to another account")
    if existing is None:
        try:
            await identity_repository.attach_platform_identity(session, user_id, platform, str(subject))
        except IntegrityError as exc:
            raise OtpError("platform identity could not be linked") from exc
    return claim
