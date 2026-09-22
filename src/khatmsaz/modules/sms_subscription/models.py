"""Time-limited SMS reminder subscriptions (owner request, 2026-09-20).

SMS reminders are gated behind a paid subscription of a fixed duration
(owner's examples: 3 months for 50,000 toman, 6 months for 87,000 toman).
When a subscription expires, SMS must turn itself off and the user must be
notified — never silently keep sending, and never silently stay off without
telling them why. Plan durations/prices are admin-editable, mirroring the
existing `plan.PlanDefinition` pattern, rather than hardcoded.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class SmsPlanOption(Base):
    """Admin-managed (duration, price) choice a user can buy."""

    __tablename__ = "sms_plan_options"

    months: Mapped[int] = mapped_column(Integer, primary_key=True)
    price_toman: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SmsSubscription(Base):
    """One active (or most-recently-expired) subscription per user."""

    __tablename__ = "sms_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Set when the expiry job has already turned SMS off and notified the
    # user for this expiry, so a scan that runs again before renewal never
    # re-notifies for the same lapse.
    expiry_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
