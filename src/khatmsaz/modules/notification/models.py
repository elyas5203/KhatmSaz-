"""Notification module: scheduled reminder jobs, per-participation preferences, and send log."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class NotifChannel(str, enum.Enum):
    TELEGRAM = "TELEGRAM"
    BALE = "BALE"
    SMS = "SMS"


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class NotificationKind(str, enum.Enum):
    DAILY_REMINDER = "DAILY_REMINDER"
    SECOND_REMINDER = "SECOND_REMINDER"
    FINAL_REMINDER = "FINAL_REMINDER"
    FOLLOW_UP = "FOLLOW_UP"


class NotificationJob(Base):
    __tablename__ = "notification_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    portion_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str] = mapped_column(String, default="Asia/Tehran")
    channel: Mapped[NotifChannel] = mapped_column()
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_notification_jobs_user_status", "user_id", "status"),
        Index("ix_notification_jobs_khatm_id", "khatm_id"),
        Index("ix_notification_jobs_scheduled_status", "scheduled_for", "status"),
    )


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    participation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_participations.id"), unique=True
    )
    reminder_hour: Mapped[int] = mapped_column(Integer, default=9)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    snoozed_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    participation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_participations.id")
    )
    kind: Mapped[NotificationKind] = mapped_column()
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_notification_log_participation_sent", "participation_id", "sent_at"),)
