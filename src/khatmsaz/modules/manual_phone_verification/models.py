"""Persistent manual phone-verification requests and their decisions."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class ManualPhoneVerification(Base):
    __tablename__ = "manual_phone_verifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    e164: Mapped[str] = mapped_column(String(16))
    purpose: Mapped[str] = mapped_column(String(24), default="CREATOR_VERIFY")
    status: Mapped[str] = mapped_column(String(16), default="PENDING")
    reviewed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    admin_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_manual_phone_verifications_user", "user_id", "created_at"),
        Index("ix_manual_phone_verifications_status", "status", "created_at"),
        Index("ix_manual_phone_verifications_e164", "e164"),
    )
