"""Authorization module: creator capabilities and delegated admin roles."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class CapabilityType(str, enum.Enum):
    CREATOR = "CREATOR"


class AdminRole(str, enum.Enum):
    CONTENT_ADMIN = "CONTENT_ADMIN"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"
    MODERATION_ADMIN = "MODERATION_ADMIN"
    MARKETING_ADMIN = "MARKETING_ADMIN"
    OPERATIONS_ADMIN = "OPERATIONS_ADMIN"


class AdminPermission(str, enum.Enum):
    DASHBOARD_ACCESS = "DASHBOARD_ACCESS"
    CONTENT_MANAGE = "CONTENT_MANAGE"
    FINANCE_MANAGE = "FINANCE_MANAGE"
    SUPPORT_USERS = "SUPPORT_USERS"
    MODERATION_MANAGE = "MODERATION_MANAGE"
    MARKETING_MANAGE = "MARKETING_MANAGE"
    OPERATIONS_VIEW = "OPERATIONS_VIEW"
    ADMIN_ROLES_MANAGE = "ADMIN_ROLES_MANAGE"


class UserCapability(Base):
    __tablename__ = "user_capabilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    type: Mapped[CapabilityType] = mapped_column()
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("ix_user_capabilities_user_id", "user_id"),)


class AdminRoleGrant(Base):
    """A revocable role assignment. Historical rows are reactivated, not deleted."""

    __tablename__ = "admin_role_grants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(32))
    granted_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "role", name="uq_admin_role_grants_user_role"),
        Index("ix_admin_role_grants_user_id", "user_id"),
    )
