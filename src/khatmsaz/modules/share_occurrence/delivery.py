"""One local-day share, immutable quantities, and receipt-based retries.

The caller commits each member independently. Messenger success followed by a
process crash before commit can still repeat a message: Telegram has no send
idempotency key. Persisted receipts prevent repeats on ordinary scan retries.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select

from khatmsaz.modules.share_occurrence import repository, service
from khatmsaz.modules.participation import repository as memberships
from khatmsaz.modules.participation.commitment import is_regular_due
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.khatm import service as khatms
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.notification import service as preferences
from khatmsaz.modules.open_contribution import repository as contributions


def timezone_for(name):
    try:
        return ZoneInfo(name)
    except (KeyError, ValueError, TypeError):
        return ZoneInfo("Asia/Tehran")


def is_managed(participation, khatm):
    return bool(participation.joined_via_bot_instance_id) and (
        khatm.template_type == "QURAN_PAGE" or participation.commitment_mode in ("REGULAR", "COUNT")
    )


async def candidate_ids(session):
    from sqlalchemy import func
    from khatmsaz.modules.notification.models import NotificationPreference
    from khatmsaz.modules.share_occurrence.models import ShareOccurrence

    effective_hour = func.coalesce(Participation.schedule_hour, NotificationPreference.reminder_hour, 12)
    return list((await session.execute(
        select(Participation.id)
        .outerjoin(NotificationPreference, NotificationPreference.participation_id == Participation.id)
        .where(
            Participation.joined_via_bot_instance_id.is_not(None),
            (Participation.status == "ACTIVE") | select(ShareOccurrence.id).where(
                ShareOccurrence.participation_id == Participation.id, ShareOccurrence.completed_at.is_(None),
            ).exists(),
        )
        .order_by(effective_hour.asc(), Participation.joined_at.asc())
    )).scalars())


def _calc_deadline(local: datetime, deadline_hour: int | None) -> datetime | None:
    if deadline_hour is None:
        return None
    if deadline_hour >= 24:
        return (local + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    if 0 <= deadline_hour <= 23:
        return local.replace(hour=deadline_hour, minute=0, second=0, microsecond=0)
    return None


async def prepare(session, participation_id, *, now=None, manual=False):
    now = now or datetime.now(timezone.utc)
    part = await memberships.get_by_id(session, participation_id)
    if part is None:
        return None
    # Same lock order as reservation/goal writers: khatm, membership, occurrence.
    khatm = await khatms.get_khatm_for_update(session, part.khatm_id)
    part = await memberships.get_by_id_for_update(session, participation_id)
    if khatm is None or not is_managed(part, khatm):
        return None
    settings = await settings_service.get_or_create(session, part.user_id)
    local = now.astimezone(timezone_for(settings.timezone))
    key = f"daily:{local.date().isoformat()}"
    existing = await repository.get_by_source(session, part.id, key)
    if existing is not None and existing.delivered_at is not None:
        return existing
    if part.status != "ACTIVE" or not khatms.has_started(khatm, now=now) or khatm.status != "ACTIVE":
        return None
    if part.paused_until and part.paused_until > now:
        return None
    if part.commitment_mode == "COUNT":
        return None
    pref = await preferences.get_preference(session, part.id)
    if not manual and pref is not None and (not pref.enabled or (pref.snoozed_until and pref.snoozed_until > now)):
        return None
    hour, minute = await preferences.get_reminder_time(session, part)
    quran = khatm.template_type == "QURAN_PAGE"
    fixed = khatm.commitment_policy == "FIXED_DAILY"
    # Existing page plans take precedence over accidentally stored Salawat mode.
    amount = (khatm.daily_commitment_amount if fixed else
              part.open_reading_pages_per_day if quran else part.commitment_per_occurrence)
    if not amount and quran and part.is_committed:
        from khatmsaz.modules.allocation.models import KhatmPortion
        latest = (await session.execute(select(KhatmPortion).where(
            KhatmPortion.participation_id == part.id,
        ).order_by(KhatmPortion.sequence.desc()).limit(1))).scalar_one_or_none()
        if latest is not None and latest.unit_start and latest.unit_end:
            amount = latest.unit_end - latest.unit_start + 1
    if not amount:
        return None
    last = part.open_reading_last_sent_at if quran else part.schedule_last_sent_at
    last_date = last.astimezone(local.tzinfo).date() if last else None
    # Do not duplicate a legacy delivery already sent before this cutover.
    if last_date is not None and last_date >= local.date():
        return None
    freq = "DAILY" if fixed else (part.schedule_freq or "DAILY")
    if not manual and not is_regular_due(local, freq or "DAILY", hour, minute, last_date, weekdays=part.schedule_weekdays):
        return None
    total = await contributions.total_for_khatm(session, khatm.id)
    if khatm.repetition_target is not None and total >= khatm.repetition_target:
        return None
    # Finish one attempted share instead of skipping its pages after an outage.
    # Only a successful delivery today creates today's actionable obligation.
    pending = await repository.list_outstanding(session, part.id)
    attempted = next((item for item in pending if item.source_key.startswith("daily:") and item.delivered_at is None), None)
    if attempted is not None:
        attempted.scheduled_for = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
        attempted.deadline_at = _calc_deadline(local, khatm.daily_deadline_hour)
        await session.flush()
        return attempted
    spec = {}
    if quran:
        from khatmsaz.modules.content import service as content
        total_pages = content.get_quran_total_pages(khatm)
        if part.is_committed:
            from khatmsaz.modules.allocation import service as allocation
            ranges = await allocation.allocate_page_amount(session, khatm.id, part.id, amount)
            if not ranges:
                return None
            spec = {"ranges": [[p.unit_start, p.unit_end] for p in ranges],
                    "portion_ids": [str(p.id) for p in ranges]}
            amount = sum(b - a + 1 for a, b in spec["ranges"])
        else:
            start = part.open_reading_next_page
            amount = min(amount, total_pages - start + 1)
            if amount <= 0:
                return None
            spec = {"ranges": [[start, start + amount - 1]]}
    else:
        from khatmsaz.bot.member_copy import content_family
        fam = await content_family(session, khatm)
        if fam == "khutbah":
            from sqlalchemy import func
            from khatmsaz.modules.share_occurrence.models import ShareOccurrence
            from khatmsaz.modules.content import service as content_service
            completed_count = (await session.scalar(
                select(func.count()).select_from(ShareOccurrence).where(
                    ShareOccurrence.participation_id == part.id,
                    ShareOccurrence.completed_at.is_not(None),
                )
            )) or 0
            total_sections = 5
            category, slug = await content_service.resolve_khatm_devotional_source(session, khatm)
            if slug:
                videos = await content_service.list_devotional_video_pages(session, slug, "TELEGRAM")
                if videos:
                    total_sections = max(v.page_number for v in videos) or 5
            sec_start = ((completed_count * amount) % total_sections) + 1
            sec_end = min(sec_start + amount - 1, total_sections)
            spec = {"ranges": [[sec_start, sec_end]], "family": "khutbah"}
    deadline = _calc_deadline(local, khatm.daily_deadline_hour)
    occurrence, _ = await service.create_once(
        session, participation_id=part.id, bot_instance_id=part.joined_via_bot_instance_id,
        source_key=key, amount=amount, unit="PAGE" if quran else "COUNT",
        committed=part.is_committed, scheduled_for=local.replace(hour=hour, minute=minute, second=0, microsecond=0),
        deadline_at=deadline, content_spec=spec,
    )
    return occurrence


async def prepare_numeric(session, participation_id, amount, *, user_id, bot_instance_id, now=None):
    """Issue one exact numeric share; only OPEN has a reservation expiry."""
    from uuid import uuid4
    from khatmsaz.modules.open_contribution import service as reservations
    from khatmsaz.modules.content import service as content
    from khatmsaz.modules.allocation import service as allocation
    now = now or datetime.now(timezone.utc)
    if not isinstance(amount, int) or isinstance(amount, bool) or not 0 < amount <= 2147483647:
        raise ValueError("Invalid numeric amount")
    part = await memberships.get_by_id(session, participation_id)
    if part is None or part.user_id != user_id or bot_instance_id is None or part.joined_via_bot_instance_id != bot_instance_id:
        raise service.OccurrenceAccessError("Membership does not belong to this member bot")
    khatm = await khatms.get_khatm_for_update(session, part.khatm_id)
    part = await memberships.get_by_id_for_update(session, part.id)
    if part.status != "ACTIVE" or khatm.status != "ACTIVE" or not khatms.has_started(khatm, now=now) or khatm.commitment_policy == "FIXED_DAILY":
        raise ValueError("Numeric mode is unavailable")
    for old in await repository.list_outstanding(session, part.id):
        if old.source_key.startswith(("count:", "reservation:")):
            return old
    total = await contributions.total_for_khatm(session, khatm.id)
    if khatm.repetition_target is not None and total >= khatm.repetition_target:
        return None
    quran = khatm.template_type == "QURAN_PAGE"
    if quran and amount > content.get_quran_total_pages(khatm):
        raise ValueError("Page amount exceeds the edition")
    reservation = None
    if khatm.khatm_type == "OPEN":
        reservation, _ = await reservations.create_reservation(session, khatm.id, part.id, amount, khatm.repetition_target)
        if reservation is None:
            return None
        amount = int(reservation.amount)
    spec = {}
    if quran:
        if part.is_committed:
            portions = await allocation.allocate_page_amount(session, khatm.id, part.id, amount)
            if not portions:
                raise ValueError("No Quran pages available")
            spec = {"ranges": [[p.unit_start,p.unit_end] for p in portions], "portion_ids": [str(p.id) for p in portions]}
            amount = sum(b-a+1 for a,b in spec["ranges"])
        else:
            total_pages = content.get_quran_total_pages(khatm)
            start = (part.open_reading_next_page-1) % total_pages + 1
            end = min(total_pages, start+amount-1)
            ranges = [[start,end]]
            if end-start+1 < amount:
                ranges.append([1,amount-(end-start+1)])
            spec = {"ranges": ranges}
    part.commitment_mode = "COUNT"
    part.commitment_target = amount
    key = f"reservation:{reservation.id}" if reservation else f"count:{uuid4()}"
    occurrence, _ = await service.create_once(session, participation_id=part.id,
        bot_instance_id=part.joined_via_bot_instance_id, reservation_id=reservation.id if reservation else None,
        source_key=key, amount=amount, unit="PAGE" if quran else "COUNT", committed=part.is_committed,
        scheduled_for=now, content_spec=spec)
    return occurrence


async def record_progress(session, part, occurrence):
    from khatmsaz.modules.open_contribution import service as progress
    from khatmsaz.modules.allocation import repository as portions
    khatm = await khatms.get_khatm(session, part.khatm_id)
    for portion_id in occurrence.content_spec.get("portion_ids", []):
        await portions.complete_portion(session, portion_id)
    target = khatm.repetition_target
    if target is None and khatm.status == "COMPLETED":
        target = await contributions.total_for_khatm(session, khatm.id)
    _, _, total = await progress.log_contribution(session, khatm.id, part.id, occurrence.amount, target)
    goal_reached = target is not None and total >= target
    if occurrence.unit == "PAGE" and occurrence.content_spec.get("portion_ids") and khatm.repetition_target is None:
        from khatmsaz.modules.allocation import service as allocation
        completed, planned = await allocation.progress(session, khatm.id)
        goal_reached = planned > 0 and completed >= planned
    if goal_reached and khatm.status == "ACTIVE":
        await khatms.complete_khatm(session, khatm.id)
    from khatmsaz.modules.advertising import service as advertising
    await advertising.accrue_first_completed_action(session, part.id)


async def deliver(session, occurrence, *, now=None):
    from khatmsaz.bot.occurrence_adapter import deliver_occurrence
    now = now or datetime.now(timezone.utc)
    if occurrence.delivered_at is not None:
        return False
    part = await memberships.get_by_id(session, occurrence.participation_id)
    khatm = await khatms.get_khatm(session, part.khatm_id)
    if not await deliver_occurrence(session, part, khatm, occurrence, now=now):
        return False
    await service.mark_delivered(session, occurrence.id, bot_instance_id=occurrence.bot_instance_id, when=now)
    if occurrence.unit == "PAGE":
        if not occurrence.content_spec.get("portion_ids"):
            part.open_reading_next_page = occurrence.content_spec["ranges"][-1][1] + 1
        part.open_reading_last_sent_at = now
    else:
        part.schedule_last_sent_at = now
    await session.flush()
    return True


async def remind(session, participation_id, *, now=None):
    from khatmsaz.bot.occurrence_adapter import send_control
    now = now or datetime.now(timezone.utc)
    part = await memberships.get_by_id(session, participation_id)
    khatm = await khatms.get_khatm(session, part.khatm_id)
    pref = await preferences.get_preference(session, part.id)
    if pref and (not pref.enabled or (pref.snoozed_until and pref.snoozed_until > now)):
        return
    for occurrence in await repository.list_outstanding(session, participation_id):
        if not occurrence.committed or occurrence.delivered_at is None:
            continue
        for purpose, due in (("FOLLOWUP", occurrence.delivered_at + timedelta(hours=2)),
                             ("DEADLINE", occurrence.deadline_at - timedelta(hours=1) if occurrence.deadline_at else None)):
            if due is None or now < due:
                continue
            if purpose == "DEADLINE" and now >= occurrence.deadline_at:
                continue
            await send_control(session, part, khatm, occurrence, purpose, now=now)
