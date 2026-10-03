"""Open-contribution module: freely-recorded contributions in an OPEN khatm."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class OpenContribution(Base):
    __tablename__ = "open_contributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    participation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_participations.id")
    )
    amount: Mapped[float] = mapped_column(Float)
    counted_amount: Mapped[float] = mapped_column(Float, default=0.0)
    surplus_amount: Mapped[float] = mapped_column(Float, default=0.0)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_open_contributions_khatm_id", "khatm_id"),
        Index("ix_open_contributions_participation_id", "participation_id"),
    )

import enum
class OpenReservationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

class OpenReservation(Base):
    __tablename__ = "open_reservations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    participation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_participations.id")
    )
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[OpenReservationStatus] = mapped_column(String(32), default=OpenReservationStatus.ACTIVE)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reminded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_open_reservations_khatm_id", "khatm_id"),
        Index("ix_open_reservations_participation_id", "participation_id"),
        Index("ix_open_reservations_status", "status"),
    )
