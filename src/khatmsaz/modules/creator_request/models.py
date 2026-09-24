"""Data model for creator-role requests.

A user submits a request to become a Creator; an admin reviews it.
On approval, the user's role in `identity.models.User` is upgraded to
CREATOR and they gain access to the khatm creation wizard and management
features.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func, Enum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class CreatorRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CreatorRequest(Base):
    __tablename__ = "creator_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False,
    )
    status: Mapped[CreatorRequestStatus] = mapped_column(
        Enum(CreatorRequestStatus, native_enum=False, length=50),
        default=CreatorRequestStatus.PENDING,
    )
    # Optional note from the admin when approving/rejecting.
    admin_note: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True,
    )
