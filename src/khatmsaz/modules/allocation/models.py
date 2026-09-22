"""Allocation module: the generic, template-driven portion engine.

A plan is generated once per khatm into a set of non-overlapping portions;
portions are then allocated to participations, completed, or released back
to the pool for reallocation (used by the waiting-list / backup-reader
replacement flow).
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class PortionUnitKind(str, enum.Enum):
    POSITIONAL = "POSITIONAL"
    QUANTITY = "QUANTITY"


class PortionStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"


class KhatmAllocationPlan(Base):
    __tablename__ = "khatm_allocation_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"), unique=True)
    unit_kind: Mapped[PortionUnitKind] = mapped_column()
    total_portions: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class KhatmPortion(Base):
    __tablename__ = "khatm_portions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatm_allocation_plans.id"))
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    unit_kind: Mapped[PortionUnitKind] = mapped_column()
    unit_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # For QUANTITY commitment portions, records partial progress such as
    # 300 + 200 + 500 without conflating it with the shared OPEN pool.
    completed_quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[PortionStatus] = mapped_column(default=PortionStatus.OPEN)
    participation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_participations.id"), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Set only for emergency-pool claims; an expired reservation returns to
    # OPEN so a volunteer cannot hold a portion indefinitely (SPEC Q102).
    claim_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("plan_id", "sequence", name="uq_khatm_portions_plan_sequence"),
        Index("ix_khatm_portions_khatm_id", "khatm_id"),
        Index("ix_khatm_portions_plan_id", "plan_id"),
        Index("ix_khatm_portions_participation_id", "participation_id"),
        Index("ix_khatm_portions_status", "status"),
        # Hand-written partial unique index (Alembic migration, not expressible here):
        #   UNIQUE (plan_id, unit_start) WHERE unit_kind = 'POSITIONAL'
    )


class CommittedQuantityLog(Base):
    """Per-submission log for quantity-commitment portions (salawat, dua, laan).

    Inserted each time a member records progress on their committed quantity
    so that a today-vs-yesterday group comparison can be computed — the portion
    table only stores a cumulative total, not timestamped entries.
    """

    __tablename__ = "committed_quantity_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    participation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_participations.id")
    )
    amount: Mapped[int] = mapped_column(Integer)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_committed_qty_log_khatm_logged", "khatm_id", "logged_at"),
    )
