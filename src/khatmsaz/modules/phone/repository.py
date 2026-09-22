"""Persistence helpers for phone ownership and one-time challenges."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.phone.models import OtpChallenge, OtpPurpose, PhoneClaim, PhoneClaimStatus


async def create_challenge(session: AsyncSession, **values) -> OtpChallenge:
    challenge = OtpChallenge(id=new_id(), **values)
    session.add(challenge)
    await session.flush()
    return challenge


async def get_challenge(session: AsyncSession, challenge_id) -> OtpChallenge | None:
    return await session.get(OtpChallenge, challenge_id)


async def supersede_open_challenges(session: AsyncSession, *, user_id, e164: str, purpose: OtpPurpose) -> None:
    result = await session.execute(
        select(OtpChallenge).where(
            OtpChallenge.user_id == user_id,
            OtpChallenge.e164 == e164,
            OtpChallenge.purpose == purpose,
            OtpChallenge.consumed_at.is_(None),
            OtpChallenge.superseded_at.is_(None),
        )
    )
    now = datetime.now(timezone.utc)
    for challenge in result.scalars():
        challenge.superseded_at = now
    await session.flush()


async def verified_claim(session: AsyncSession, e164: str) -> PhoneClaim | None:
    result = await session.execute(
        select(PhoneClaim).where(PhoneClaim.e164 == e164, PhoneClaim.status == PhoneClaimStatus.VERIFIED)
    )
    return result.scalar_one_or_none()


async def lock_phone(session: AsyncSession, e164: str) -> None:
    """Serialize ownership changes for one canonical number in PostgreSQL."""
    await session.execute(select(func.pg_advisory_xact_lock(func.hashtext(e164))))


async def get_user_verified_claim(session: AsyncSession, user_id, e164: str) -> PhoneClaim | None:
    result = await session.execute(
        select(PhoneClaim).where(
            PhoneClaim.user_id == user_id,
            PhoneClaim.e164 == e164,
            PhoneClaim.status == PhoneClaimStatus.VERIFIED,
        )
    )
    return result.scalar_one_or_none()


async def verified_claim_for_user(session: AsyncSession, user_id) -> PhoneClaim | None:
    result = await session.execute(
        select(PhoneClaim).where(
            PhoneClaim.user_id == user_id,
            PhoneClaim.status == PhoneClaimStatus.VERIFIED,
        )
    )
    return result.scalar_one_or_none()


async def revoke_user_verified_claims(
    session: AsyncSession, *, user_id, except_e164: str | None = None
) -> None:
    """Revoke the user's current phone claim while retaining its audit history."""
    result = await session.execute(
        select(PhoneClaim)
        .where(
            PhoneClaim.user_id == user_id,
            PhoneClaim.status == PhoneClaimStatus.VERIFIED,
        )
        .with_for_update()
    )
    now = datetime.now(timezone.utc)
    for claim in result.scalars():
        if except_e164 is not None and claim.e164 == except_e164:
            continue
        claim.status = PhoneClaimStatus.REVOKED
        claim.revoked_at = now
    await session.flush()


async def create_or_verify_claim(session: AsyncSession, *, user_id, e164: str, region: str | None = None) -> PhoneClaim:
    claim = await get_user_verified_claim(session, user_id, e164)
    if claim is None:
        claim = PhoneClaim(id=new_id(), user_id=user_id, e164=e164, region=region, status=PhoneClaimStatus.VERIFIED)
        claim.verified_at = datetime.now(timezone.utc)
        session.add(claim)
    else:
        claim.verified_at = claim.verified_at or datetime.now(timezone.utc)
    await session.flush()
    return claim
