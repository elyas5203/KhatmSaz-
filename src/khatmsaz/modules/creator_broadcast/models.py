import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class CreatorBroadcast(Base):
    __tablename__ = "creator_broadcasts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    
    message_text: Mapped[str | None] = mapped_column(String, nullable=True)
    media_file_id: Mapped[str | None] = mapped_column(String, nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(16), nullable=True) # photo, video, document, etc.
    
    # 0 = free, >0 = paid (Tomans)
    cost_toman: Mapped[int] = mapped_column(Integer, default=0)
    is_paid: Mapped[bool] = mapped_column(default=False)
    
    audience_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
