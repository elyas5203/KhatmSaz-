"""Owner decision (2026-09-21): a committed Quran participant only ever gets
one portion per calendar day — completing today's portion does not hand out
tomorrow's immediately (see allocation/service.py::complete_current_portion_and_advance).
Instead, `reminder_engine.service.deliver_due_next_portions` hands out the
next portion once a full day has passed (in the member's own timezone) and
the local clock reaches their own reminder hour. This also replaces the old
emergency-portion/backup-reader system, which is fully removed: a missed
portion no longer notifies anyone and nobody else can claim it — the same
member just gets it whenever they're ready."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation import repository as allocation_repository
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401 — registers FK target table
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.reminder_engine import service as reminder_service
from khatmsaz.modules.settings import service as settings_service


def _iana_offset_for_local_hour(target_hour: int) -> str:
    """A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N`
    is UTC+N) whose local hour is `target_hour` right now, so the test doesn't
    depend on the machine's current wall-clock hour."""
    utc_hour = datetime.now(timezone.utc).hour
    offset = (target_hour - utc_hour) % 24
    if offset > 14:
        offset -= 24
    sign = "-" if offset >= 0 else "+"
    return f"Etc/GMT{sign}{abs(offset)}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_next_portion_is_withheld_until_next_local_day_at_reminder_hour():
    creator_id, member_id, khatm_id = (new_id() for _ in range(3))
    member_identity_id = new_id()
    reminder_hour = 9
    tz_name = _iana_offset_for_local_hour(reminder_hour)

    async with session_scope() as session:
        session.add_all([
            User(id=creator_id),
            User(id=member_id),
            PlatformIdentity(id=member_identity_id, user_id=member_id, platform=Platform.TELEGRAM, subject="one-per-day-member"),
        ])
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="یک سهم در روز",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, daily_deadline_hour=23,
        )
        session.add(khatm)
        await session.flush()

        member_settings = await settings_service.get_or_create(session, member_id)
        member_settings.timezone = tz_name
        await session.flush()

        member = await participation_repository.create(session, khatm_id, member_id)
        await notification_service.set_reminder_preference(
            session, member.id, reminder_hour=reminder_hour,
            reminder_minute=datetime.now(timezone.utc).minute, enabled=True,
        )
        await allocation_service.generate_quran_page_plan(session, khatm_id, 6, pages_per_portion=2)

        first = await allocation_service.allocate_next_portion_to(session, khatm_id, member.id)
        assert first is not None

        completed, next_immediately = await allocation_service.complete_current_portion_and_advance(
            session, khatm_id, member.id
        )
        assert completed is not None
        # Core of the owner's decision: no auto-advance in the same call.
        assert next_immediately is None
        assert await allocation_service.get_current_portion(session, khatm_id, member.id) is None
        assert (await allocation_service.peek_next_open_portion(session, khatm_id)) is not None

        sent = []

        async def notify(platform, subject, text):
            sent.append((platform, subject, text))

        # Same day, reminder hour reached: still too early (< 1 full day since completion).
        delivered_same_day = await reminder_service.deliver_due_next_portions(session, notify, tz_name)
        assert delivered_same_day == 0
        assert not sent
        assert await allocation_service.get_current_portion(session, khatm_id, member.id) is None

        # Simulate a full day having passed since completion.
        completed.completed_at = datetime.now(timezone.utc) - timedelta(days=1, hours=1)
        await session.flush()

        delivered_next_day = await reminder_service.deliver_due_next_portions(session, notify, tz_name)
        assert delivered_next_day == 1
        assert len(sent) == 1
        assert "سهم" in sent[0][2]

        next_portion = await allocation_service.get_current_portion(session, khatm_id, member.id)
        assert next_portion is not None
        assert next_portion.unit_start == 3 and next_portion.unit_end == 4

        # Cleanup.
        await session.execute(delete(type(next_portion)).where(type(next_portion).khatm_id == khatm_id))
        plan = await allocation_repository.get_plan_by_khatm(session, khatm_id)
        if plan is not None:
            await session.execute(delete(type(plan)).where(type(plan).id == plan.id))
        from khatmsaz.modules.notification.models import NotificationPreference
        await session.execute(delete(NotificationPreference).where(NotificationPreference.participation_id == member.id))
        await session.execute(delete(type(member)).where(type(member).khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.id == member_identity_id))
        await session.execute(delete(type(member_settings)).where(type(member_settings).user_id.in_([creator_id, member_id])))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
