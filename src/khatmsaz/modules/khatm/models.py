"""Khatm module: the core collective-recitation aggregate."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class KhatmStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class KhatmTypeEnum(str, enum.Enum):
    COMMITMENT = "COMMITMENT"
    OPEN = "OPEN"


class KhatmVisibility(str, enum.Enum):
    PUBLIC = "PUBLIC"  # discoverable through /public_khatms
    UNLISTED = "UNLISTED"  # default: anyone with the invite link joins directly
    PRIVATE = "PRIVATE"  # anyone with the link can *request* to join; creator approves


class ContentDeliveryMode(str, enum.Enum):
    AUTO = "AUTO"
    PHOTO = "PHOTO"
    TEXT = "TEXT"


class ReminderTone(str, enum.Enum):
    FRIENDLY = "FRIENDLY"
    FORMAL = "FORMAL"
    DEVOTIONAL = "DEVOTIONAL"
    SHORT = "SHORT"


class CreatorDisplayMode(str, enum.Enum):
    FULL_NAME = "FULL_NAME"
    FIRST_NAME = "FIRST_NAME"
    PSEUDONYM = "PSEUDONYM"
    ANONYMOUS = "ANONYMOUS"


class CoverStatus(str, enum.Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class KhatmScheduleKind(str, enum.Enum):
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    INTERVAL = "INTERVAL"
    DATE = "DATE"


class KhatmTemplateType(str, enum.Enum):
    SURAH = "SURAH"
    QURAN_PAGE = "QURAN_PAGE"
    QURAN_SURAH = "QURAN_SURAH"
    SALAWAT = "SALAWAT"
    DUA = "DUA"
    ZIYARAT = "ZIYARAT"
    CUSTOM = "CUSTOM"


class Khatm(Base):
    __tablename__ = "khatms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    creator_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    template_type: Mapped[KhatmTemplateType] = mapped_column()
    khatm_type: Mapped[KhatmTypeEnum] = mapped_column(default=KhatmTypeEnum.COMMITMENT)
    status: Mapped[KhatmStatus] = mapped_column(default=KhatmStatus.DRAFT)

    quran_edition_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Admin-managed child content for one of the independent SALAWAT, LAAN or
    # DUA parents. They share a quantity engine internally but are never one
    # user-facing family. NULL means plain salawat with no specific text.
    content_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_categories.id"), nullable=True
    )
    content_delivery_mode: Mapped[str] = mapped_column(String(16), default=ContentDeliveryMode.AUTO.value)
    surah_number: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    repetition_target: Mapped[int | None] = mapped_column(Integer, nullable=True)

    public_slug: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    niyyat: Mapped[str | None] = mapped_column(String(500), nullable=True)
    welcome_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reminder_tone: Mapped[str] = mapped_column(String(16), default=ReminderTone.FRIENDLY.value)
    creator_display_mode: Mapped[str] = mapped_column(String(16), default=CreatorDisplayMode.FULL_NAME.value)
    creator_pseudonym: Mapped[str | None] = mapped_column(String(64), nullable=True)
    cover_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover_platform: Mapped[str | None] = mapped_column(String(16), nullable=True)
    cover_status: Mapped[str] = mapped_column(String(16), default=CoverStatus.NONE.value)
    cover_admin_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    schedule_kind: Mapped[str] = mapped_column(String(16), default=KhatmScheduleKind.NONE.value)
    schedule_value: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Only meaningful for QURAN_PAGE + COMMITMENT (Phase 2, DEC-PY-0008): the
    # daily cutoff hour (0-23, local timezone) by which an assigned page
    # portion should be completed before it counts as a miss. NULL for every
    # other (template_type, khatm_type) combination — there is no daily
    # cadence concept yet for a one-shot SALAWAT commitment.
    daily_deadline_hour: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    # Only meaningful for QURAN_PAGE + COMMITMENT (DEC-PY-0010): the max
    # number of COMMITTED participants. NULL means unlimited. Scoped to this
    # one combination for now — SALAWAT commitment has no natural "read
    # along without committing" fallback the way Quran pages do, so a
    # waiting-list-while-reading-casually model doesn't cleanly apply there
    # yet (see DECISIONS.md DEC-PY-0010).
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Only meaningful for QURAN_PAGE + COMMITMENT: whether the "امروز
    # نمی‌رسم" (release today's portion proactively, no miss) button shows
    # up. Creator-configurable per DOMAIN_MODEL.md §3 Q86. Defaults to
    # enabled — a stricter creator can turn it off.
    allow_skip_today: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_pause: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_snooze: Mapped[bool] = mapped_column(Boolean, default=True)
    miss_notice_threshold: Mapped[int] = mapped_column(SmallInteger, default=2)
    miss_notice_window_days: Mapped[int] = mapped_column(SmallInteger, default=3)

    # DOMAIN_MODEL.md §2 Q65-66. All three modes are creator-selectable;
    # PUBLIC khatms appear in /public_khatms.
    visibility: Mapped[KhatmVisibility] = mapped_column(default=KhatmVisibility.UNLISTED)
    creation_price_toman: Mapped[int] = mapped_column(Integer, default=0)
    # Creator-controlled advertising opt-in; rewards are only accrued for
    # eligible active members after their first completed action.
    advertising_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    # Optional scheduled start. The khatm remains ACTIVE for sharing, but
    # participation/reminders treat it as not started until this instant.
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Creator-controlled positive completion summary (SPEC Q95-96). Delivery
    # waits five minutes so a mistaken final tap can still be undone first.
    completion_announcement_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_announced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_khatms_creator_user_id", "creator_user_id"),
        Index("ix_khatms_status", "status"),
        Index(
            "ix_khatms_completion_announcement",
            "status", "completion_announcement_enabled", "completion_announced_at", "completed_at",
        ),
    )
