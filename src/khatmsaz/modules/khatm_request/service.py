"""Khatm-request business logic: submit, list pending, approve/reject.

Deliberately simple (DOMAIN_MODEL.md §2: "فقط یک فرم ساده: نام پیشنهادی +
توضیح"): one free-text description, no structured fields. See
DECISIONS.md DEC-PY-0014 for why approving a request doesn't automatically
make the new khatm type usable — that's a separate, real piece of work.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.khatm_request import repository
from khatmsaz.modules.khatm_request.models import KhatmRequest, KhatmRequestStatus


async def submit(session: AsyncSession, requester_user_id, description: str, **attachment) -> KhatmRequest:
    return await repository.create(session, requester_user_id, description, **attachment)


async def list_pending(session: AsyncSession) -> list[KhatmRequest]:
    return await repository.list_pending(session)


async def get(session: AsyncSession, request_id) -> KhatmRequest | None:
    return await repository.get_by_id(session, request_id)


async def approve(session: AsyncSession, request_id, note: str | None = None) -> None:
    await repository.set_status(session, request_id, KhatmRequestStatus.APPROVED, note)


async def reject(session: AsyncSession, request_id, note: str | None = None) -> None:
    await repository.set_status(session, request_id, KhatmRequestStatus.REJECTED, note)
