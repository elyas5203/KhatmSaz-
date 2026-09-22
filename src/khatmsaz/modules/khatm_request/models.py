"""Khatm-request module: a creator asking for a khatm type not in the
picker yet (DOMAIN_MODEL.md §2 "درخواست ختم جدید"). Admin reviews and either
approves (and separately, manually, adds real support for it — see
DECISIONS.md DEC-PY-0014 for why the wizard integration is NOT built yet) or
rejects with a note.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class KhatmRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class KhatmRequest(Base):
    __tablename__ = "khatm_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    requester_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(String(1000))
    attachment_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attachment_platform: Mapped[str | None] = mapped_column(String(16), nullable=True)
    status: Mapped[KhatmRequestStatus] = mapped_column(default=KhatmRequestStatus.PENDING)
    admin_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_khatm_requests_requester", "requester_user_id"),
        Index("ix_khatm_requests_status", "status"),
    )
