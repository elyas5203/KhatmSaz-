"""Immutable per-occurrence payloads; no latest-membership callback identity."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class ShareOccurrence(Base):
    __tablename__ = "share_occurrences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    participation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatm_participations.id"))
    bot_instance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bot_instances.id"))
    source_key: Mapped[str] = mapped_column(String(80))
    amount: Mapped[int] = mapped_column(Integer)
    unit: Mapped[str] = mapped_column(String(16))
    # Snapshot includes Quran ranges or a devotional reference; it must not
    # change when a member edits tomorrow's schedule.
    content_spec: Mapped[dict] = mapped_column(JSONB, default=dict)
    committed: Mapped[bool] = mapped_column(Boolean)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("participation_id", "source_key", name="uq_share_occurrence_source"),
        CheckConstraint("amount > 0", name="ck_share_occurrence_amount"),
        CheckConstraint("unit IN ('PAGE', 'COUNT', 'REPETITION')", name="ck_share_occurrence_unit"),
        CheckConstraint("completed_at IS NULL OR delivered_at IS NOT NULL", name="ck_share_occurrence_completed_delivery"),
        Index("ix_share_occurrence_due", "scheduled_for", postgresql_where=text("delivered_at IS NULL")),
        Index("ix_share_occurrence_outstanding", "participation_id", "scheduled_for", postgresql_where=text("completed_at IS NULL")),
    )


class ShareMessage(Base):
    __tablename__ = "share_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    occurrence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("share_occurrences.id"))
    component_key: Mapped[str] = mapped_column(String(80))
    purpose: Mapped[str] = mapped_column(String(16))
    chat_id: Mapped[str] = mapped_column(String(32))
    message_id: Mapped[int] = mapped_column(BigInteger)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("occurrence_id", "component_key", name="uq_share_message_component"),
        CheckConstraint("purpose IN ('CONTENT', 'ACTION', 'FOLLOWUP', 'DEADLINE')", name="ck_share_message_purpose"),
        CheckConstraint("message_id > 0", name="ck_share_message_id"),
        CheckConstraint("purpose <> 'CONTENT' OR deleted_at IS NULL", name="ck_share_message_preserve_content"),
    )
