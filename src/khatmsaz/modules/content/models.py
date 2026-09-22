import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class KhatmReciter(Base):
    """A creator-approved reciter for one khatm, in display priority order."""

    __tablename__ = "khatm_reciters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    reciter_id: Mapped[str] = mapped_column(String(64))
    priority: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("khatm_id", "reciter_id", name="uq_khatm_reciters_khatm_reciter"),
        Index("ix_khatm_reciters_khatm_priority", "khatm_id", "priority"),
    )


class QuranAssetKind(str, enum.Enum):
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    TEXT = "TEXT"


class QuranPageAsset(Base):
    """One immutable-addressable media asset for one canonical Quran page."""

    __tablename__ = "quran_page_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    edition_id: Mapped[str] = mapped_column(String(64))
    page_number: Mapped[int] = mapped_column(Integer)
    # Stored as text so deployments do not depend on PostgreSQL enum DDL.
    kind: Mapped[str] = mapped_column(String(16))
    reciter_id: Mapped[str] = mapped_column(String(64), default="")
    asset_ref: Mapped[str] = mapped_column(String(500))
    asset_platform: Mapped[str] = mapped_column(String(16), default="TELEGRAM")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "edition_id", "page_number", "kind", "reciter_id", "asset_platform",
            name="uq_quran_page_assets_identity",
        ),
        Index("ix_quran_page_assets_lookup", "edition_id", "page_number", "kind", "reciter_id", "asset_platform"),
    )


class DevotionalAsset(Base):
    """Admin-curated complete text/audio for a dua or ziyarat."""

    __tablename__ = "devotional_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    content_type: Mapped[str] = mapped_column(String(16))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    text_body: Mapped[str | None] = mapped_column(String, nullable=True)
    audio_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    audio_platform: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # Owner request (2026-09-22): an image of the devotional text (e.g. a
    # photo of the Ziyarat Ashura page), same idea as `audio_ref`.
    image_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_platform: Mapped[str | None] = mapped_column(String(16), nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_devotional_assets_type_enabled", "content_type", "enabled"),
    )


class DevotionalMedia(Base):
    """Owner request (2026-09-22): a devotional asset (dua/ziyarat) can
    have MORE than one audio (different reciters), more than one image
    (a long dua spanning several page photos), or a PDF — the single
    `audio_ref`/`image_ref` columns on `DevotionalAsset` only ever held
    one of each. Mirrors `QuranPageAsset`'s (kind, reciter_id) shape.
    `DevotionalAsset.audio_ref`/`image_ref` are kept, untouched, as the
    legacy single-slot fallback for content registered before this table
    existed — delivery code checks here first, falls back to those."""

    __tablename__ = "devotional_media"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    devotional_asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devotional_assets.id"))
    kind: Mapped[str] = mapped_column(String(16))  # AUDIO | IMAGE | PDF
    # Only meaningful for AUDIO — which reciter this variant is. "" (not
    # NULL, to keep the unique constraint simple) for IMAGE/PDF.
    reciter_id: Mapped[str] = mapped_column(String(64), default="")
    reciter_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Only meaningful for IMAGE — 1-based page order. 0 for AUDIO/PDF.
    page_number: Mapped[int] = mapped_column(Integer, default=0)
    asset_ref: Mapped[str] = mapped_column(String(500))
    asset_platform: Mapped[str] = mapped_column(String(16), default="TELEGRAM")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "devotional_asset_id", "kind", "reciter_id", "page_number", "asset_platform",
            name="uq_devotional_media_identity",
        ),
        Index("ix_devotional_media_lookup", "devotional_asset_id", "kind"),
    )
