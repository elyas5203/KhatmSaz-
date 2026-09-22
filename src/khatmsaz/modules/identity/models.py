"""Identity module: the canonical User and external PlatformIdentity links.

Mirrors the `User` / `PlatformIdentity` models in the original Prisma schema.
A User is the internal canonical actor — never a phone number or platform
account. A PlatformIdentity is only an external claim/link (Telegram or Bale
numeric chat id), never a source of canonical identity.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from khatmsaz.core.db import Base


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    MERGED = "MERGED"
    WARNED = "WARNED"
    SUSPENDED = "SUSPENDED"
    BANNED = "BANNED"


class UserRole(str, enum.Enum):
    USER = "USER"
    SUPER_ADMIN = "SUPER_ADMIN"


class Platform(str, enum.Enum):
    TELEGRAM = "TELEGRAM"
    BALE = "BALE"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    display_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    merged_into_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Soft-deletion marker: preserve ledger/report history while preventing
    # further use of the account (SPEC Q39).
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    platform_identities: Mapped[list["PlatformIdentity"]] = relationship(back_populates="user")

    __table_args__ = (Index("ix_users_merged_into_id", "merged_into_id"),)


class PlatformIdentity(Base):
    __tablename__ = "platform_identities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    platform: Mapped[Platform] = mapped_column()
    subject: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="platform_identities")

    __table_args__ = (
        UniqueConstraint("platform", "subject", name="uq_platform_identities_platform_subject"),
        Index("ix_platform_identities_user_id", "user_id"),
    )
