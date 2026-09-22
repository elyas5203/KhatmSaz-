"""Plan module: assigned plan tier per user (FREE / BASIC / PRO). Missing row implies FREE."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class PlanTier(str, enum.Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"


class PricingMode(str, enum.Enum):
    FIXED = "FIXED"
    USAGE_BASED = "USAGE_BASED"


class PlanDefinition(Base):
    """Admin-managed pricing and feature entitlements for a plan tier."""

    __tablename__ = "plan_definitions"

    plan: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(80))
    # String storage keeps future pricing modes migration-free.
    pricing_mode: Mapped[str] = mapped_column(String(20), default=PricingMode.FIXED.value)
    price_toman: Mapped[int] = mapped_column(Integer, default=0)
    unit_price_toman: Mapped[int] = mapped_column(Integer, default=0)
    entitlements: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UserPlan(Base):
    __tablename__ = "user_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    plan: Mapped[PlanTier] = mapped_column(default=PlanTier.FREE)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
