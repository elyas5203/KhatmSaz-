"""Data model for support tickets and user feedback.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class SupportTicketStatus(str, enum.Enum):
    PENDING = "PENDING"
    ANSWERED = "ANSWERED"
    CLOSED = "CLOSED"


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sender_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    target_role: Mapped[str] = mapped_column(String(32), default="SUPER_ADMIN")
    target_creator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    subject: Mapped[str | None] = mapped_column(String(200), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SupportTicketStatus] = mapped_column(
        Enum(SupportTicketStatus, native_enum=False, length=32),
        default=SupportTicketStatus.PENDING,
        nullable=False,
    )
    reply_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    replied_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    replied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("id", uuid.uuid4())
        kwargs.setdefault("status", SupportTicketStatus.PENDING)
        kwargs.setdefault("target_role", "SUPER_ADMIN")
        from datetime import timezone
        kwargs.setdefault("created_at", datetime.now(timezone.utc))
        super().__init__(**kwargs)

    __table_args__ = (
        Index("ix_support_tickets_status", "status"),
        Index("ix_support_tickets_sender", "sender_user_id"),
        Index("ix_support_tickets_target_creator", "target_creator_id"),
        Index("ix_support_tickets_created_at", "created_at"),
    )
