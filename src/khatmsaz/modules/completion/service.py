"""Idempotent, delayed completion announcements for every platform."""

from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.khatm import repository as khatm_repository
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.reporting import service as reporting_service
from khatmsaz.modules.settings import service as settings_service

NotifyFn = Callable[[str, str, str], Awaitable[None]]
UNDO_GRACE = timedelta(minutes=5)


def _message(title: str, stats, locale: str) -> str:
    if locale == "ar":
        lines = [f"🎉 اكتملت ختمة «{title}»", "تقبّل الله من الجميع 🤍"]
        member_label, portion_label, contribution_label = "المشاركون", "الحصص المكتملة", "مجموع المشاركات"
    elif locale == "en":
        lines = [f"🎉 “{title}” is complete", "May everyone’s devotion be accepted 🤍"]
        member_label, portion_label, contribution_label = "Participants", "Completed portions", "Total contributions"
    else:
        lines = [f"🎉 ختم «{title}» با همراهی شما به پایان رسید.", "خدا از همه قبول کند 🤍"]
        member_label, portion_label, contribution_label = "تعداد همراهان", "سهم‌های تکمیل‌شده", "مجموع مشارکت"
    lines.append(f"👥 {member_label}: {stats.total_members}")
    if stats.total_portions:
        lines.append(f"📖 {portion_label}: {stats.completed_portions} / {stats.total_portions}")
    if stats.contribution_total:
        lines.append(f"🌱 {contribution_label}: {int(stats.contribution_total)}")
    return "\n".join(lines)


async def deliver_pending(
    session: AsyncSession,
    notify: NotifyFn,
    *,
    now: datetime | None = None,
    khatm_id=None,
) -> int:
    """Claim each eligible announcement once, then notify creator + active members."""
    current = now or datetime.now(timezone.utc)
    cutoff = current - UNDO_GRACE
    candidate_ids = (
        [khatm_id]
        if khatm_id is not None
        else await khatm_repository.list_pending_completion_announcement_ids(
            session, completed_before=cutoff
        )
    )
    delivered = 0
    for candidate_id in candidate_ids:
        khatm = await khatm_repository.claim_completion_announcement(
            session, candidate_id, completed_before=cutoff
        )
        if khatm is None:
            continue
        stats = await reporting_service.get_khatm_stats(session, khatm.id)
        memberships = await participation_service.list_active_with_users(session, khatm.id)
        user_ids = {khatm.creator_user_id, *(user.id for _, user in memberships)}
        sent_to: set[tuple[str, str]] = set()
        for user_id in user_ids:
            settings = await settings_service.get_or_create(session, user_id)
            text = _message(khatm.title, stats, settings.language)
            for identity in await identity_service.list_identities_for_user(session, user_id):
                destination = (identity.platform.value, identity.subject)
                if destination in sent_to:
                    continue
                sent_to.add(destination)
                await notify(*destination, text)
        delivered += 1
    return delivered
