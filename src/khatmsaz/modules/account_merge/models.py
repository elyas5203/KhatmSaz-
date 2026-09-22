"""Account-merge module: append-only audit of completed account merges."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class AccountMerge(Base):
    __tablename__ = "account_merges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    winner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    loser_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    verified_e164: Mapped[str] = mapped_column(String)
    initiating_challenge_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    moved_platform_identities: Mapped[int] = mapped_column(Integer, default=0)
    moved_phone_claims: Mapped[int] = mapped_column(Integer, default=0)
    context: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_account_merges_winner_user_id", "winner_user_id"),
        Index("ix_account_merges_loser_user_id", "loser_user_id"),
    )
