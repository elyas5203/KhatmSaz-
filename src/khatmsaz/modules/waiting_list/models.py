"""Waiting-list module: queue for full-capacity COMMITMENT khatms."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class WaitingList(Base):
    __tablename__ = "waiting_list"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    khatm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khatms.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    position: Mapped[int] = mapped_column(Integer)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("khatm_id", "user_id", name="uq_waiting_list_khatm_user"),
        Index("ix_waiting_list_khatm_position", "khatm_id", "position"),
    )
