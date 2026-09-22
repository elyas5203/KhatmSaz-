"""Persistence access for khatm — the only place that runs SQL for this module."""

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum, KhatmVisibility


async def create(
    session: AsyncSession,
    *,
    creator_user_id,
    title: str,
    template_type: KhatmTemplateType,
    khatm_type: KhatmTypeEnum,
    niyyat: str | None = None,
    description: str | None = None,
    quran_edition_id: str | None = None,
    surah_number: int | None = None,
    repetition_target: int | None = None,
    daily_deadline_hour: int | None = None,
    welcome_text: str | None = None,
    capacity: int | None = None,
    allow_skip_today: bool = True,
    allow_pause: bool = True,
    allow_snooze: bool = True,
    completion_announcement_enabled: bool = True,
    miss_notice_threshold: int = 2,
    miss_notice_window_days: int = 3,
    visibility: KhatmVisibility = KhatmVisibility.UNLISTED,
    creation_price_toman: int = 0,
    advertising_enabled: bool = False,
    creator_display_mode: str = "FULL_NAME",
    creator_pseudonym: str | None = None,
    reminder_tone: str = "FRIENDLY",
    content_delivery_mode: str = "AUTO",
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    schedule_kind: str = "NONE",
    schedule_value: str | None = None,
    content_category_id=None,
) -> Khatm:
    khatm = Khatm(
        id=new_id(),
        creator_user_id=creator_user_id,
        title=title,
        description=description,
        template_type=template_type,
        khatm_type=khatm_type,
        niyyat=niyyat,
        quran_edition_id=quran_edition_id,
        surah_number=surah_number,
        repetition_target=repetition_target,
        daily_deadline_hour=daily_deadline_hour,
        welcome_text=welcome_text,
        capacity=capacity,
        allow_skip_today=allow_skip_today,
        allow_pause=allow_pause,
        allow_snooze=allow_snooze,
        completion_announcement_enabled=completion_announcement_enabled,
        miss_notice_threshold=miss_notice_threshold,
        miss_notice_window_days=miss_notice_window_days,
        visibility=visibility,
        status=KhatmStatus.DRAFT,
        creation_price_toman=creation_price_toman,
        advertising_enabled=advertising_enabled,
        creator_display_mode=creator_display_mode,
        creator_pseudonym=creator_pseudonym,
        reminder_tone=reminder_tone,
        content_delivery_mode=content_delivery_mode,
        start_at=start_at,
        end_at=end_at,
        schedule_kind=schedule_kind,
        schedule_value=schedule_value,
        content_category_id=content_category_id,
    )
    session.add(khatm)
    await session.flush()
    return khatm


async def get_by_id(session: AsyncSession, khatm_id) -> Khatm | None:
    return await session.get(Khatm, khatm_id)


async def set_status(session: AsyncSession, khatm_id, status: KhatmStatus) -> None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return
    previous = khatm.status
    khatm.status = status
    if status == KhatmStatus.COMPLETED and previous != KhatmStatus.COMPLETED:
        khatm.completed_at = datetime.now(timezone.utc)
    await session.flush()


async def set_allow_skip_today(session: AsyncSession, khatm_id, enabled: bool) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.allow_skip_today = enabled
    await session.flush()
    return khatm


async def set_allow_pause(session: AsyncSession, khatm_id, enabled: bool) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.allow_pause = enabled
    await session.flush()
    return khatm


async def set_allow_snooze(session: AsyncSession, khatm_id, enabled: bool) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.allow_snooze = enabled
    await session.flush()
    return khatm


async def set_completion_announcement_enabled(
    session: AsyncSession, khatm_id, enabled: bool
) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.completion_announcement_enabled = enabled
    await session.flush()
    return khatm


async def list_pending_completion_announcement_ids(
    session: AsyncSession, *, completed_before: datetime, limit: int = 50
) -> list:
    result = await session.execute(
        select(Khatm.id)
        .where(
            Khatm.status == KhatmStatus.COMPLETED,
            Khatm.completion_announcement_enabled.is_(True),
            Khatm.completion_announced_at.is_(None),
            Khatm.completed_at.is_not(None),
            Khatm.completed_at <= completed_before,
        )
        .order_by(Khatm.completed_at.asc())
        .limit(max(1, min(limit, 100)))
    )
    return list(result.scalars())


async def claim_completion_announcement(
    session: AsyncSession, khatm_id, *, completed_before: datetime
) -> Khatm | None:
    result = await session.execute(
        update(Khatm)
        .where(
            Khatm.id == khatm_id,
            Khatm.status == KhatmStatus.COMPLETED,
            Khatm.completion_announcement_enabled.is_(True),
            Khatm.completion_announced_at.is_(None),
            Khatm.completed_at.is_not(None),
            Khatm.completed_at <= completed_before,
        )
        .values(completion_announced_at=datetime.now(timezone.utc))
        .returning(Khatm.id)
    )
    claimed_id = result.scalar_one_or_none()
    if claimed_id is None:
        return None
    await session.flush()
    return await session.get(Khatm, claimed_id)


async def reopen_after_unannounced_undo(session: AsyncSession, khatm_id) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if (
        khatm is None
        or khatm.status != KhatmStatus.COMPLETED
        or khatm.completion_announced_at is not None
    ):
        return None
    khatm.status = KhatmStatus.ACTIVE
    khatm.completed_at = None
    await session.flush()
    return khatm


async def set_miss_notice_policy(session: AsyncSession, khatm_id, threshold: int, window_days: int) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.miss_notice_threshold = threshold
    khatm.miss_notice_window_days = window_days
    await session.flush()
    return khatm


async def set_end_at(session: AsyncSession, khatm_id, end_at: datetime | None) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.end_at = end_at
    await session.flush()
    return khatm


async def set_cover_pending(session: AsyncSession, khatm_id, *, cover_ref: str, platform: str) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.cover_ref = cover_ref
    khatm.cover_platform = platform
    khatm.cover_status = "PENDING"
    khatm.cover_admin_note = None
    await session.flush()
    return khatm


async def list_pending_covers(session: AsyncSession) -> list[Khatm]:
    result = await session.execute(
        select(Khatm).where(Khatm.cover_status == "PENDING").order_by(Khatm.created_at.asc())
    )
    return list(result.scalars())


async def review_cover(session: AsyncSession, khatm_id, *, approved: bool, note: str | None = None) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.cover_status = "APPROVED" if approved else "REJECTED"
    khatm.cover_admin_note = note
    await session.flush()
    return khatm


async def set_schedule(session: AsyncSession, khatm_id, *, kind: str, value: str | None) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    khatm.schedule_kind = kind
    khatm.schedule_value = value
    await session.flush()
    return khatm


async def list_due_endings(session: AsyncSession, now: datetime) -> list[Khatm]:
    result = await session.execute(
        select(Khatm).where(Khatm.status == KhatmStatus.ACTIVE, Khatm.end_at.is_not(None), Khatm.end_at <= now)
    )
    return list(result.scalars())


async def update_cosmetic(
    session: AsyncSession, khatm_id, *, title: str | None = None,
    welcome_text: str | None = None, update_welcome: bool = False,
) -> Khatm | None:
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None:
        return None
    if title is not None:
        khatm.title = title
    if update_welcome:
        khatm.welcome_text = welcome_text
    await session.flush()
    return khatm


async def list_created_by(session: AsyncSession, user_id) -> list[Khatm]:
    stmt = select(Khatm).where(Khatm.creator_user_id == user_id).order_by(Khatm.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars())


async def list_public_active(session: AsyncSession, *, limit: int = 20) -> list[Khatm]:
    stmt = (
        select(Khatm)
        .where(Khatm.status == KhatmStatus.ACTIVE, Khatm.visibility == KhatmVisibility.PUBLIC)
        .order_by(Khatm.created_at.desc())
        .limit(max(1, min(limit, 50)))
    )
    result = await session.execute(stmt)
    return list(result.scalars())
