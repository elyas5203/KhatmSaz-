"""Domain service for support tickets and user feedback."""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.support_ticket import repository
from khatmsaz.modules.support_ticket.models import SupportTicket, SupportTicketStatus

logger = logging.getLogger("khatmsaz")


async def submit_ticket(
    session: AsyncSession,
    *,
    sender_user_id: uuid.UUID,
    body: str,
    target_role: str = "SUPER_ADMIN",
    target_creator_id: uuid.UUID | None = None,
    subject: str | None = None,
) -> SupportTicket:
    return await repository.create(
        session,
        sender_user_id=sender_user_id,
        body=body,
        target_role=target_role,
        target_creator_id=target_creator_id,
        subject=subject,
    )


async def get_ticket(session: AsyncSession, ticket_id: uuid.UUID) -> SupportTicket | None:
    return await repository.get(session, ticket_id)


async def list_admin_tickets(
    session: AsyncSession,
    *,
    status: SupportTicketStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[SupportTicket]:
    return await repository.list_admin_tickets(session, status=status, limit=limit, offset=offset)


async def count_pending_for_admin(session: AsyncSession) -> int:
    return await repository.count_pending_for_admin(session)


async def answer_ticket_by_admin(
    session: AsyncSession,
    *,
    ticket_id: uuid.UUID,
    reply_text: str,
    admin_user_id: uuid.UUID,
) -> SupportTicket:
    ticket = await repository.answer_ticket(
        session,
        ticket_id=ticket_id,
        reply_text=reply_text,
        replied_by_user_id=admin_user_id,
    )

    # 1. Audit log
    await audit_service.record(
        session,
        actor_user_id=admin_user_id,
        action="SUPPORT_TICKET_REPLY",
        details={
            "ticket_id": str(ticket.id),
            "sender_user_id": str(ticket.sender_user_id),
            "reply_length": len(reply_text),
        },
    )

    # 2. Dispatch reply notification to user across their linked platforms
    try:
        notify = get_notify_fn()
    except RuntimeError:
        notify = None

    if notify is not None:
        identities = await identity_service.list_identities_for_user(session, ticket.sender_user_id)
        msg = (
            "📨 <b>پاسخ پشتیبانی سامانه ختم‌ساز:</b>\n\n"
            f"{reply_text.strip()}\n\n"
            "🌱 <i>با تشکر از همراهی شما.</i>"
        )
        for identity in identities:
            try:
                await notify(identity.platform.value, identity.subject, msg)
            except Exception as exc:
                logger.warning(
                    "Failed to notify user %s on platform %s for ticket %s: %s",
                    ticket.sender_user_id,
                    identity.platform,
                    ticket.id,
                    exc,
                )

    return ticket


async def close_ticket_by_admin(
    session: AsyncSession,
    *,
    ticket_id: uuid.UUID,
    admin_user_id: uuid.UUID,
) -> SupportTicket:
    ticket = await repository.close_ticket(session, ticket_id)
    await audit_service.record(
        session,
        actor_user_id=admin_user_id,
        action="SUPPORT_TICKET_CLOSE",
        details={"ticket_id": str(ticket.id)},
    )
    return ticket
