"""Phone module: phone ownership claims and OTP challenges."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class PhoneClaimStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"


class OtpPurpose(str, enum.Enum):
    PHONE_VERIFICATION = "PHONE_VERIFICATION"
    PHONE_LOGIN = "PHONE_LOGIN"


class PhoneClaim(Base):
    __tablename__ = "phone_claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    e164: Mapped[str] = mapped_column(String)
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[PhoneClaimStatus] = mapped_column(default=PhoneClaimStatus.UNVERIFIED)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_phone_claims_user_id", "user_id"),
        Index("ix_phone_claims_e164", "e164"),
    )


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    e164: Mapped[str] = mapped_column(String)
    purpose: Mapped[OtpPurpose] = mapped_column()
    code_hash: Mapped[str] = mapped_column(String)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_otp_challenges_user_e164_purpose", "user_id", "e164", "purpose"),
        Index("ix_otp_challenges_e164", "e164"),
    )
