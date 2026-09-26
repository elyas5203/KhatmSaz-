"""Participation module: a user's membership in a Khatm, and per-participant assignments."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class ParticipationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    LEFT = "LEFT"
    REMOVED = "REMOVED"


class AssignmentUnitKind(str, enum.Enum):
    POSITIONAL = "POSITIONAL"
    QUANTITY = "QUANTITY"


class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class Participation(Base):
    __tablename__ = "khatm_participations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[ParticipationStatus] = mapped_column(default=ParticipationStatus.ACTIVE)
    # Whether THIS participant is committed (vs. reading along casually while
    # waiting for a committed slot — DEC-PY-0010). For a plain COMMITMENT
    # khatm under capacity, this is always True at join time; a joiner past
    # capacity gets False + a waiting_list row, until promoted.
    is_committed: Mapped[bool] = mapped_column(Boolean, default=True)
    # Creator's resolution after repeated missed deadlines (SPEC Q77).
    # Kept as a string so adding future resolution states does not require a
    # PostgreSQL enum migration.
    creator_resolution: Mapped[str] = mapped_column(String(32), default="PENDING")
    # Explicit volunteer role for missed Quran portions; separate from the
    # waiting list and ordinary participation (DOMAIN_MODEL.md §3 Q75).
    backup_reader_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    # "موقتاً متوقف کن" (DOMAIN_MODEL.md §3 Q80): while set and in the
    # future, this participation is skipped entirely by reminder_engine
    # (no reminder, no miss) and can't claim a fresh portion.
    paused_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Quick-pick reason captured when leaving (DOMAIN_MODEL.md §3 Q98) — for
    # churn analysis later, not shown to the creator today.
    leave_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Owner request (2026-09-21): an OPEN (or waitlisted, is_committed=False)
    # QURAN_PAGE reader can set "N pages/day" once, instead of only being
    # able to self-report a bare number with no actual page content ever
    # sent. NULL means the reader hasn't set this up yet — see
    # `bot/handlers/portions.py`'s open-Quran setup flow and
    # `reminder_engine.service.deliver_due_open_quran_reading`.
    open_reading_pages_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 1-based cursor into the khatm's Quran edition — the next page this
    # reader hasn't been sent yet. Advances every time content is actually
    # delivered, whether by the daily auto-send or a manual "ثبت مشارکت".
    open_reading_next_page: Mapped[int] = mapped_column(Integer, default=1)
    # Last time this reader was actually sent Quran content (auto or
    # manual) — used to make sure the daily auto-send fires at most once
    # per local calendar day, mirroring the committed one-portion-per-day
    # rule without reusing its machinery (no KhatmPortion exists here).
    open_reading_last_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_via_bot_instance_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bot_instances.id"), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_participations_khatm_id", "khatm_id"),
        Index("ix_participations_user_id", "user_id"),
        # Hand-written partial unique index (Alembic migration, not expressible here):
        #   UNIQUE (khatm_id, user_id) WHERE status = 'ACTIVE'
    )


class Assignment(Base):
    """The Phase-4 flat per-khatm assignment (legacy shape, kept for parity).

    The allocation-engine `KhatmPortion` below is the one actually used for
    portion tracking; this table mirrors the original schema 1:1.
    """

    __tablename__ = "assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    participation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_participations.id")
    )
    unit_kind: Mapped[AssignmentUnitKind] = mapped_column()
    unit_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[AssignmentStatus] = mapped_column(default=AssignmentStatus.PENDING)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_assignments_khatm_id", "khatm_id"),
        Index("ix_assignments_participation_id", "participation_id"),
        Index("ix_assignments_status", "status"),
    )
