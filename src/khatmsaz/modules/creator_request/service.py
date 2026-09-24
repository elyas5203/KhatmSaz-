"""Service layer for creator requests — business logic."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.creator_request import repository
from khatmsaz.modules.creator_request.models import CreatorRequest, CreatorRequestStatus
from khatmsaz.modules.identity import repository as identity_repo
from khatmsaz.modules.identity.models import UserRole


class AlreadyCreatorError(Exception):
    """User already has the CREATOR or SUPER_ADMIN role."""


class PendingRequestExistsError(Exception):
    """User already has a PENDING creator request."""


async def submit_request(
    session: AsyncSession, user_id: uuid.UUID,
) -> CreatorRequest:
    """Submit a new creator-role request.

    Raises AlreadyCreatorError if the user is already a creator/admin.
    Raises PendingRequestExistsError if they already have a pending request.
    """
    from khatmsaz.modules.identity import service as identity_service

    user = await identity_service.find_by_id(session, user_id)
    if user is None:
        raise ValueError("User not found")
    if user.role in (UserRole.CREATOR, UserRole.SUPER_ADMIN):
        raise AlreadyCreatorError()
    existing = await repository.get_pending_by_user(session, user_id)
    if existing is not None:
        raise PendingRequestExistsError()
    return await repository.create(session, user_id)


async def approve_request(
    session: AsyncSession,
    request_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    *,
    note: str | None = None,
) -> CreatorRequest | None:
    """Approve a pending creator request and upgrade the user's role."""
    req = await repository.approve(session, request_id, reviewer_id, note=note)
    if req is None:
        return None
    # Upgrade the user's role to CREATOR.
    await identity_repo.set_role(session, req.user_id, UserRole.CREATOR)
    return req


async def reject_request(
    session: AsyncSession,
    request_id: uuid.UUID,
    reviewer_id: uuid.UUID,
    *,
    note: str | None = None,
) -> CreatorRequest | None:
    """Reject a pending creator request."""
    return await repository.reject(session, request_id, reviewer_id, note=note)


async def list_pending(
    session: AsyncSession, *, limit: int = 50,
) -> list[CreatorRequest]:
    return await repository.list_pending(session, limit=limit)


async def has_pending_request(
    session: AsyncSession, user_id: uuid.UUID,
) -> bool:
    return await repository.get_pending_by_user(session, user_id) is not None
