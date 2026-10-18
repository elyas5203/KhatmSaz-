"""Database repository for support tickets."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.support_ticket.models import SupportTicket, SupportTicketStatus


async def create(
    session: AsyncSession,
    *,
    sender_user_id: uuid.UUID,
    body: str,
    target_role: str = "SUPER_ADMIN",
    target_creator_id: uuid.UUID | None = None,
    subject: str | None = None,
) -> SupportTicket:
    ticket = SupportTicket(
        id=uuid.uuid4(),
        sender_user_id=sender_user_id,
        target_role=target_role,
        target_creator_id=target_creator_id,
        subject=subject,
        body=body.strip(),
        status=SupportTicketStatus.PENDING,
    )
    session.add(ticket)
    await session.flush()
    return ticket


async def get(session: AsyncSession, ticket_id: uuid.UUID) -> SupportTicket | None:
    return await session.get(SupportTicket, ticket_id)


async def list_admin_tickets(
    session: AsyncSession,
    *,
    status: SupportTicketStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[SupportTicket]:
    stmt = (
        select(SupportTicket)
        .where(SupportTicket.target_role == "SUPER_ADMIN")
        .order_by(SupportTicket.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status is not None:
        stmt = stmt.where(SupportTicket.status == status)
    return list((await session.execute(stmt)).scalars().all())


async def count_pending_for_admin(session: AsyncSession) -> int:
    stmt = (
        select(func.count())
        .select_from(SupportTicket)
        .where(
            SupportTicket.target_role == "SUPER_ADMIN",
            SupportTicket.status == SupportTicketStatus.PENDING,
        )
    )
    return int((await session.scalar(stmt)) or 0)


async def answer_ticket(
    session: AsyncSession,
    *,
    ticket_id: uuid.UUID,
    reply_text: str,
    replied_by_user_id: uuid.UUID,
) -> SupportTicket:
    ticket = await session.get(SupportTicket, ticket_id)
    if ticket is None:
        raise ValueError(f"SupportTicket {ticket_id} not found")
    ticket.reply_text = reply_text.strip()
    ticket.replied_by_user_id = replied_by_user_id
    ticket.replied_at = datetime.now(timezone.utc)
    ticket.status = SupportTicketStatus.ANSWERED
    await session.flush()
    return ticket


async def close_ticket(session: AsyncSession, ticket_id: uuid.UUID) -> SupportTicket:
    ticket = await session.get(SupportTicket, ticket_id)
    if ticket is None:
        raise ValueError(f"SupportTicket {ticket_id} not found")
    ticket.status = SupportTicketStatus.CLOSED
    await session.flush()
    return ticket
