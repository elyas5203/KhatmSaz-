"""Khatm business logic. Orchestration across modules (allocation, invitation,
participation) lives in `khatm_workflow.service`, not here — this module only
knows about the `Khatm` aggregate itself.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.config import get_settings
from khatmsaz.modules.khatm import repository
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


async def create_draft_khatm(
    session: AsyncSession,
    *,
    creator_user_id,
    title: str,
    template_type: KhatmTemplateType,
    khatm_type: KhatmTypeEnum,
    niyyat: str | None = None,
    description: str | None = None,
    creation_price_toman: int = 0,
    **template_fields,
) -> Khatm:
    """`khatm_type` (COMMITMENT vs OPEN) is an explicit creator choice made
    independently of `template_type` (DOMAIN_MODEL.md §2: "creator asks
    commitment-or-free first, then picks the content"). See DECISIONS.md
    DEC-PY-0007 — this used to be hard-wired per template (DEC-PY-0004,
    now superseded)."""
    return await repository.create(
        session,
        creator_user_id=creator_user_id,
        title=title,
        description=description,
        template_type=template_type,
        khatm_type=khatm_type,
        niyyat=niyyat,
        creation_price_toman=creation_price_toman,
        **template_fields,
    )


async def activate_khatm(session: AsyncSession, khatm_id) -> None:
    await repository.set_status(session, khatm_id, KhatmStatus.ACTIVE)


async def complete_khatm(session: AsyncSession, khatm_id) -> Khatm | None:
    """Transition an active khatm to Completed exactly once."""
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.status != KhatmStatus.ACTIVE:
        return khatm
    await repository.set_status(session, khatm_id, KhatmStatus.COMPLETED)
    return await repository.get_by_id(session, khatm_id)


async def cancel_khatm(session: AsyncSession, khatm_id) -> None:
    await repository.set_status(session, khatm_id, KhatmStatus.CANCELLED)


async def set_allow_skip_today(session: AsyncSession, *, khatm_id, creator_user_id, enabled: bool) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise ValueError("khatm is not owned by creator")
    if khatm.template_type != KhatmTemplateType.QURAN_PAGE or khatm.khatm_type != KhatmTypeEnum.COMMITMENT:
        raise ValueError("skip-today applies only to committed Quran khatms")
    updated = await repository.set_allow_skip_today(session, khatm_id, enabled)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def set_allow_pause(session: AsyncSession, *, khatm_id, creator_user_id, enabled: bool) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise ValueError("khatm is not owned by creator")
    if khatm.khatm_type != KhatmTypeEnum.COMMITMENT or khatm.status != KhatmStatus.ACTIVE:
        raise ValueError("pause applies only to active commitment khatms")
    updated = await repository.set_allow_pause(session, khatm_id, enabled)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def set_allow_snooze(session: AsyncSession, *, khatm_id, creator_user_id, enabled: bool) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise ValueError("khatm is not owned by creator")
    if khatm.khatm_type != KhatmTypeEnum.COMMITMENT or khatm.status != KhatmStatus.ACTIVE:
        raise ValueError("snooze applies only to active commitment khatms")
    updated = await repository.set_allow_snooze(session, khatm_id, enabled)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def set_completion_announcement(
    session: AsyncSession, *, khatm_id, creator_user_id, enabled: bool
) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise ValueError("khatm is not owned by creator")
    if khatm.status == KhatmStatus.CANCELLED or khatm.completion_announced_at is not None:
        raise ValueError("completion announcement can no longer be changed")
    updated = await repository.set_completion_announcement_enabled(session, khatm_id, enabled)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def reopen_after_completion_undo(session: AsyncSession, khatm_id) -> Khatm | None:
    """Reopen only before the delayed completion announcement was claimed."""
    return await repository.reopen_after_unannounced_undo(session, khatm_id)


async def set_miss_notice_policy(
    session: AsyncSession, *, khatm_id, creator_user_id, threshold: int, window_days: int
) -> Khatm:
    if not 1 <= threshold <= 20 or not 1 <= window_days <= 90:
        raise ValueError("threshold/window out of range")
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id or khatm.status != KhatmStatus.ACTIVE:
        raise ValueError("only the creator of an active khatm may set miss policy")
    updated = await repository.set_miss_notice_policy(session, khatm_id, threshold, window_days)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def set_end_at(session: AsyncSession, *, khatm_id, creator_user_id, end_at: datetime | None) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise ValueError("khatm is not owned by creator")
    if khatm.status not in (KhatmStatus.DRAFT, KhatmStatus.ACTIVE):
        raise ValueError("only draft or active khatms may set an end time")
    if end_at is not None:
        current = datetime.now(timezone.utc)
        if end_at.tzinfo is None:
            end_at = end_at.replace(tzinfo=timezone.utc)
        if end_at <= current:
            raise ValueError("end time must be in the future")
    updated = await repository.set_end_at(session, khatm_id, end_at)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def submit_cover(session: AsyncSession, *, khatm_id, creator_user_id, cover_ref: str, platform: str) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise ValueError("khatm is not owned by creator")
    if khatm.status not in (KhatmStatus.DRAFT, KhatmStatus.ACTIVE):
        raise ValueError("only draft or active khatms may submit a cover")
    updated = await repository.set_cover_pending(session, khatm_id, cover_ref=cover_ref, platform=platform)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def list_pending_covers(session: AsyncSession) -> list[Khatm]:
    return await repository.list_pending_covers(session)


async def review_cover(session: AsyncSession, *, khatm_id, approved: bool, note: str | None = None) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or getattr(khatm, "cover_status", "NONE") != "PENDING":
        raise ValueError("cover is not pending")
    updated = await repository.review_cover(session, khatm_id, approved=approved, note=note)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def set_schedule(session: AsyncSession, *, khatm_id, creator_user_id, raw: str) -> Khatm:
    """Configure an open-khatm schedule: off, daily, weekly:0,2,4,
    every:3, or date:YYYY-MM-DD (Monday is 0)."""
    value = raw.strip().lower()
    if value == "off":
        kind, stored = "NONE", None
    elif value == "daily":
        kind, stored = "DAILY", None
    elif value.startswith("weekly:"):
        days = value.removeprefix("weekly:").split(",")
        if not days or any(not d.isdigit() or not 0 <= int(d) <= 6 for d in days):
            raise ValueError("invalid weekly schedule")
        kind, stored = "WEEKLY", ",".join(str(int(d)) for d in days)
    elif value.startswith("every:"):
        days = value.removeprefix("every:")
        if not days.isdigit() or not 1 <= int(days) <= 90:
            raise ValueError("invalid interval schedule")
        kind, stored = "INTERVAL", str(int(days))
    elif value.startswith("date:"):
        date_value = value.removeprefix("date:")
        try:
            selected_date = datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("invalid date schedule") from exc
        local_today = datetime.now(ZoneInfo(get_settings().app_timezone)).date()
        if selected_date < local_today:
            raise ValueError("date schedule cannot be in the past")
        kind, stored = "DATE", date_value
    else:
        raise ValueError("unknown schedule")
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id or khatm.status != KhatmStatus.ACTIVE:
        raise ValueError("only the creator of an active khatm may set schedule")
    if khatm.khatm_type != KhatmTypeEnum.OPEN:
        raise ValueError("schedules apply only to open khatms")
    updated = await repository.set_schedule(session, khatm_id, kind=kind, value=stored)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


def schedule_is_due(khatm: Khatm, current_date) -> bool:
    kind = getattr(khatm, "schedule_kind", "NONE")
    value = getattr(khatm, "schedule_value", None)
    if kind == "DAILY":
        return True
    if kind == "WEEKLY":
        return current_date.weekday() in {int(v) for v in (value or "").split(",") if v}
    if kind == "DATE":
        return current_date.isoformat() == value
    if kind == "INTERVAL":
        created = khatm.created_at.date() if khatm.created_at else current_date
        return value is not None and (current_date - created).days % int(value) == 0
    return False


async def close_due_khatms(session: AsyncSession, *, now: datetime | None = None) -> int:
    completed_at = now or datetime.now(timezone.utc)
    due = await repository.list_due_endings(session, completed_at)
    for khatm in due:
        khatm.status = KhatmStatus.COMPLETED
        khatm.completed_at = completed_at
    if due:
        await session.flush()
    return len(due)


async def update_title(session: AsyncSession, *, khatm_id, creator_user_id, title: str) -> Khatm:
    title = title.strip()
    if not title or len(title) > 200:
        raise ValueError("title must be between 1 and 200 characters")
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id or khatm.status != KhatmStatus.ACTIVE:
        raise ValueError("only the creator of an active khatm may edit the title")
    updated = await repository.update_cosmetic(session, khatm_id, title=title)
    if updated is None:
        raise ValueError("khatm not found")
    return updated


async def update_welcome_text(session: AsyncSession, *, khatm_id, creator_user_id, welcome_text: str | None) -> Khatm:
    khatm = await repository.get_by_id(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id or khatm.status != KhatmStatus.ACTIVE:
        raise ValueError("only the creator of an active khatm may edit the welcome text")
    welcome_text = preserve_creator_contact(khatm.welcome_text, welcome_text)
    updated = await repository.update_cosmetic(
        session, khatm_id, welcome_text=welcome_text, update_welcome=True
    )
    if updated is None:
        raise ValueError("khatm not found")
    return updated


def _contact_line(text: str | None) -> str | None:
    return next(
        (line.strip() for line in (text or "").splitlines() if line.strip().startswith("📬 ")),
        None,
    )


def welcome_body_without_contact(text: str | None) -> str:
    """Return the editable greeting while hiding the mandatory contact line."""
    return "\n".join(
        line for line in (text or "").splitlines() if not line.strip().startswith("📬 ")
    ).strip()


def preserve_creator_contact(existing: str | None, edited_body: str | None) -> str | None:
    """Keep the creator contact immutable when their greeting is edited."""
    contact = _contact_line(existing)
    body = welcome_body_without_contact(edited_body)
    if contact is None:
        normalized = body or None
        if normalized is not None and len(normalized) > 500:
            raise ValueError("welcome text cannot exceed 500 characters")
        return normalized
    max_body = 500 - len(contact) - 2
    if len(body) > max_body:
        raise ValueError("welcome text cannot exceed 500 characters")
    return f"{body}\n\n{contact}" if body else contact


async def get_khatm(session: AsyncSession, khatm_id) -> Khatm | None:
    return await repository.get_by_id(session, khatm_id)


def has_started(khatm: Khatm, *, now: datetime | None = None) -> bool:
    """Return whether a scheduled khatm is allowed to deliver work yet."""
    if khatm.start_at is None:
        return True
    current = now or datetime.now(timezone.utc)
    start = khatm.start_at
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return start <= current


async def list_my_created(session: AsyncSession, user_id) -> list[Khatm]:
    return await repository.list_created_by(session, user_id)


async def list_public_active(session: AsyncSession, *, limit: int = 20) -> list[Khatm]:
    return await repository.list_public_active(session, limit=limit)
