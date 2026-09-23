"""Owner request (2026-09-21): an OPEN (or waitlisted, is_committed=False)
Quran reader can set "N pages/day" once; the bot should then actually send
that many real Quran pages once a day at their chosen hour — not just log a
bare number with nothing delivered, which was the previous behavior. See
`reminder_engine.service.deliver_due_open_quran_reading` and
`bot/handlers/portions.py`'s open-Quran setup flow."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401 — registers FK target table
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.reminder_engine import service as reminder_service
from khatmsaz.modules.settings import service as settings_service


def _iana_offset_for_local_hour(target_hour: int) -> str:
    utc_hour = datetime.now(timezone.utc).hour
    offset = (target_hour - utc_hour) % 24
    if offset > 14:
        offset -= 24
    sign = "-" if offset >= 0 else "+"
    return f"Etc/GMT{sign}{abs(offset)}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour():
    creator_id, member_id, khatm_id = (new_id() for _ in range(3))
    member_identity_id = new_id()
    reminder_hour = 11
    tz_name = _iana_offset_for_local_hour(reminder_hour)

    async with session_scope() as session:
        session.add_all([
            User(id=creator_id),
            User(id=member_id),
            PlatformIdentity(id=member_identity_id, user_id=member_id, platform=Platform.TELEGRAM, subject="open-quran-reader"),
        ])
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="قرآن آزاد تست",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.OPEN,
            status=KhatmStatus.ACTIVE, quran_edition_id="madina-hafs", repetition_target=10,
        )
        session.add(khatm)
        await session.flush()

        member = await participation_repository.create(session, khatm_id, member_id, is_committed=False)
        await participation_service.set_open_reading_pages_per_day(session, member.id, 4)
        member_settings = await settings_service.get_or_create(session, member_id)
        member_settings.timezone = tz_name
        await session.flush()
        await notification_service.set_reminder_preference(
            session, member.id, reminder_hour=reminder_hour,
            reminder_minute=datetime.now(timezone.utc).minute, enabled=True,
        )

        sent_ranges = []

        async def fake_notify(platform, subject, text):
            pass

        async def fake_send_quran_pages(session, platform_value, chat_id, *, khatm, user_id, page_start, page_end):
            sent_ranges.append((page_start, page_end))

        delivered = await reminder_service.deliver_due_open_quran_reading(session, fake_notify, fake_send_quran_pages, tz_name)
        assert delivered == 1
        assert sent_ranges == [(1, 4)]

        refreshed = await participation_repository.get_by_id(session, member.id)
        assert refreshed.open_reading_next_page == 5
        assert refreshed.open_reading_last_sent_at is not None

        # Same day, same hour: must not send again.
        delivered_again = await reminder_service.deliver_due_open_quran_reading(session, fake_notify, fake_send_quran_pages, tz_name)
        assert delivered_again == 0
        assert sent_ranges == [(1, 4)]

        # Simulate a day passing: next batch should be capped to what's left (10 - 5 + 1 = 6, but pages_per_day=4).
        refreshed.open_reading_last_sent_at = datetime.now(timezone.utc) - timedelta(days=1, hours=1)
        await session.flush()
        delivered_day2 = await reminder_service.deliver_due_open_quran_reading(session, fake_notify, fake_send_quran_pages, tz_name)
        assert delivered_day2 == 1
        assert sent_ranges == [(1, 4), (5, 8)]

        # Advance to the edition boundary directly and confirm it stops cleanly.
        refreshed2 = await participation_repository.get_by_id(session, member.id)
        refreshed2.open_reading_next_page = 11  # past repetition_target=10
        refreshed2.open_reading_last_sent_at = datetime.now(timezone.utc) - timedelta(days=1, hours=1)
        await session.flush()
        delivered_done = await reminder_service.deliver_due_open_quran_reading(session, fake_notify, fake_send_quran_pages, tz_name)
        assert delivered_done == 0
        assert sent_ranges == [(1, 4), (5, 8)]

        from khatmsaz.modules.notification.models import NotificationPreference
        from khatmsaz.modules.settings.models import UserSettings
        await session.execute(delete(NotificationPreference).where(NotificationPreference.participation_id == member.id))
        await session.execute(delete(type(member)).where(type(member).khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.id == member_identity_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == member_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
