"""Generic admin-editable key/value store for small system-wide numeric
defaults (reminder hour, inactivity days, ...) that previously lived only
as hardcoded Python constants. Owner request (2026-09-21): "همه چیز قابل
کنترل و تنظیم باشه، داینامیک باشه" — this is the cheap, reusable
foundation for that: any future "make this number admin-editable" request
can reuse this table instead of needing a new migration + new model each
time. Values are stored as plain strings and parsed by whichever service
reads them (see `system_settings/service.py::get_int`)."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
