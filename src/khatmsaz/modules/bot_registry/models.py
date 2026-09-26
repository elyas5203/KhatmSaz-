import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class BotRole(str, enum.Enum):
    CREATOR = "CREATOR"
    MEMBER = "MEMBER"


class BotCategory(str, enum.Enum):
    QURAN = "QURAN"
    SALAWAT = "SALAWAT"
    DUA_ZIYARAT = "DUA_ZIYARAT"
    LAAN = "LAAN"


class BotInstance(Base):
    __tablename__ = "bot_instances"
    __table_args__ = (
        UniqueConstraint(
            "platform", "bot_role", "category", "language",
            name="uq_bot_instance_slot",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    platform: Mapped[str] = mapped_column(String(10), nullable=False)
    bot_role: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str | None] = mapped_column(String(2), nullable=True)
    token_encrypted: Mapped[str] = mapped_column(Text, nullable=False, default="")
    username: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )
