"""Invitation business logic: issue a shareable join token, resolve it back
to a khatm. Group invite links are meant to be reused by many joiners (this
is a "join my khatm" link, not a single-use ticket), so `accept` here never
marks the invitation consumed — see DOMAIN_MODEL.md §2 "join entry points."

Ported behavior from the original project's DEC-0075: no practical expiry
(links stay valid until the creator explicitly cancels them — cancellation
is not built yet, Phase 2+).
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.security import generate_token, hash_token
from khatmsaz.modules.invitation import repository

_NO_PRACTICAL_EXPIRY = timedelta(days=365 * 100)


class InvitationNotFoundError(Exception):
    pass


class InvitationExpiredError(Exception):
    pass


async def create_invitation(session: AsyncSession, khatm_id, created_by_user_id) -> str:
    token = generate_token()
    expires_at = datetime.now(timezone.utc) + _NO_PRACTICAL_EXPIRY
    await repository.create(session, khatm_id, created_by_user_id, hash_token(token), expires_at)
    return token  # raw token — returned to the caller once, never stored


async def resolve_khatm_id(session: AsyncSession, token: str):
    invitation = await repository.get_by_token_hash(session, hash_token(token))
    if invitation is None or invitation.cancelled_at is not None:
        raise InvitationNotFoundError()
    if invitation.expires_at < datetime.now(timezone.utc):
        raise InvitationExpiredError()
    return invitation.khatm_id


async def mark_accepted(session: AsyncSession, token: str, user_id) -> None:
    """Record the first successful acceptance for invitation-funnel metrics."""
    await repository.mark_accepted(session, hash_token(token), user_id)
