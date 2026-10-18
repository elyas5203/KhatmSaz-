import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class AdvertisingRewardRate(Base):
    """Append-only reward-rate history; the newest effective rate is active."""

    __tablename__ = "advertising_reward_rates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    amount_toman: Mapped[int] = mapped_column(Integer)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BannerType(str, enum.Enum):
    SYSTEM_CULTURAL = "SYSTEM_CULTURAL"
    COMMERCIAL_AD = "COMMERCIAL_AD"


class BannerPlacement(str, enum.Enum):
    ALL = "ALL"
    PORTION_FOOTER = "PORTION_FOOTER"
    INVITE_PAGE = "INVITE_PAGE"
    DIRECT_BROADCAST = "DIRECT_BROADCAST"


class BannerStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class AdvertisingBanner(Base):
    """Banners and advertisements for portions, invite pages, and direct broadcasts."""

    __tablename__ = "advertising_banners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    banner_type: Mapped[BannerType] = mapped_column(String(32), default=BannerType.SYSTEM_CULTURAL)
    placement: Mapped[BannerPlacement] = mapped_column(String(32), default=BannerPlacement.ALL)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    button_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    button_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    creator_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    khatm_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[BannerStatus] = mapped_column(String(32), default=BannerStatus.APPROVED)
    audience_count: Mapped[int] = mapped_column(Integer, default=0)
    cost_toman: Mapped[int] = mapped_column(Integer, default=0)
    impressions_count: Mapped[int] = mapped_column(Integer, default=0)
    clicks_count: Mapped[int] = mapped_column(Integer, default=0)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    admin_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_advertising_banners_status_active", "status", "is_active"),
        Index("ix_advertising_banners_placement", "placement"),
        Index("ix_advertising_banners_banner_type", "banner_type"),
        Index("ix_advertising_banners_created_at", "created_at"),
    )
