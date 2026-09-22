"""User settings module: per-user configurable preferences (1:1 extension of User)."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class FontSize(str, enum.Enum):
    NORMAL = "NORMAL"
    LARGE = "LARGE"


class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    reminder_hour: Mapped[int] = mapped_column(Integer, default=9)
    reminder_minute: Mapped[int] = mapped_column(Integer, default=0)
    timezone: Mapped[str] = mapped_column(String, default="Asia/Tehran")
    font_size: Mapped[FontSize] = mapped_column(default=FontSize.NORMAL)
    preferred_reciter: Mapped[str | None] = mapped_column(String, nullable=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    province: Mapped[str | None] = mapped_column(String, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(nullable=True)
    # Unverified contact info for a regular participant (DOMAIN_MODEL.md §1:
    # "مورد اول باشه اعتماد کنیم" — trust-based, no OTP for non-creators).
    contact_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, default="fa")
    # Owner request (2026-09-20): ask each brand-new user their language
    # exactly once, right after the welcome message. This flag — not the
    # `language` value itself, which defaults to "fa" for everyone — is
    # what distinguishes "never asked" from "chose fa".
    language_prompted: Mapped[bool] = mapped_column(Boolean, default=False)
    daily_digest_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    translation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    tafsir_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    # Audio is opt-in: Quran images are always the primary, least surprising
    # delivery and a participant receives recitation only after enabling it.
    quran_audio_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    # YYYY-MM of the last closed calendar month processed by the positive
    # monthly-report worker. A string keeps the dedup key timezone-neutral.
    last_monthly_report_period: Mapped[str | None] = mapped_column(String(7), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
