"""Admin-managed content library for independent devotional families.

Owner requirement (2026-09-18): صلوات، لعن (لعن عایشه، لعن عمر، ...) و ادعیهٔ
نام‌دار (زیارت عاشورا، دعای مشمول، عهد، آل‌یاسین) باید بدون دیپلوی جدید، از
پنل ادمین اضافه/ویرایش/حذف بشن. Confirmed by the owner: a دعا/لعن khatm is
completed exactly like a صلوات khatm — a plain repetition counter — so this
module only carries *content* (title + recitation text/audio). SALAWAT, LAAN,
and DUA are separate top-level product choices even though their counting
workflows reuse the same internal quantity engine; that implementation detail
must never collapse the user-facing taxonomy.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class KhatmCategoryGroup(str, enum.Enum):
    SALAWAT = "SALAWAT"
    LAAN = "LAAN"
    DUA = "DUA"


class KhatmCategory(Base):
    __tablename__ = "khatm_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    group: Mapped[KhatmCategoryGroup] = mapped_column()
    title: Mapped[str] = mapped_column(String(200))
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # Explicit link to a `devotional_assets` row (BACKLOG.md §14, fixed
    # 2026-09-21) — replaces the old fragile name-matching hack in
    # `bot/handlers/portions.py` (checking if "عاشورا" appeared in the
    # category title) that broke if a creator renamed the category.
    devotional_slug: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class KhatmCategoryRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    FULFILLED = "FULFILLED"
    DECLINED = "DECLINED"


class KhatmCategoryRequest(Base):
    """A participant's typed request for a دعا that isn't in the library yet
    (owner rule: goes to the admin, and once handled it "میره به لیست دائمی
    دعاها" — i.e. becomes a normal `KhatmCategory` row)."""

    __tablename__ = "khatm_category_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    requested_title: Mapped[str] = mapped_column(String(200))
    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[KhatmCategoryRequestStatus] = mapped_column(default=KhatmCategoryRequestStatus.PENDING)
    fulfilled_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("khatm_categories.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
