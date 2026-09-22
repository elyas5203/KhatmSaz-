"""Moderated creator messages for a khatm."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class BroadcastStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SENT = "SENT"


class KhatmBroadcast(Base):
    __tablename__ = "khatm_broadcasts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    creator_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[BroadcastStatus] = mapped_column(default=BroadcastStatus.PENDING)
    admin_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_khatm_broadcasts_status_created", "status", "created_at"),
        Index("ix_khatm_broadcasts_khatm_created", "khatm_id", "created_at"),
    )
