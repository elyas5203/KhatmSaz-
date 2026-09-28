"""Owner request (2026-09-21): "سهم امروز باید اتومات باشه و اصلا دکمه
نداشته باشه" — a committed Quran participant's daily portion (both the
very first one and every subsequent day's, via
`reminder_engine.service.deliver_due_next_portions`) should have its real
page content (image/audio/text) auto-pushed alongside the reminder text,
instead of requiring a manual "📖 نمایش محتوای سهم" tap every time."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401 — registers FK target table
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation import repository as participation_repository
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
async def test_deliver_due_next_portions_pushes_real_content_not_just_text():
    creator_id, member_id, khatm_id = (new_id() for _ in range(3))
    member_identity_id = new_id()
    reminder_hour = 10
    tz_name = _iana_offset_for_local_hour(reminder_hour)

    async with session_scope() as session:
        session.add_all([
            User(id=creator_id),
            User(id=member_id),
            PlatformIdentity(id=member_identity_id, user_id=member_id, platform=Platform.TELEGRAM, subject="committed-quran-reader"),
        ])
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="قرآن تعهدی تست ارسال خودکار",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, quran_edition_id="madina-hafs", daily_deadline_hour=23,
        )
        session.add(khatm)
        await session.flush()

        member = await participation_repository.create(session, khatm_id, member_id, is_committed=True)
        member_settings = await settings_service.get_or_create(session, member_id)
        member_settings.timezone = tz_name
        await session.flush()
        await notification_service.set_reminder_preference(
            session, member.id, reminder_hour=reminder_hour,
            reminder_minute=datetime.now(timezone.utc).minute, enabled=True,
        )

        await allocation_service.generate_quran_page_plan(session, khatm_id, total_pages=10, pages_per_portion=2)
        first = await allocation_service.allocate_next_portion_to(session, khatm_id, member.id)
        assert (first.unit_start, first.unit_end) == (1, 2)
        await allocation_service.complete_current_portion_and_advance(session, khatm_id, member.id)

        pushed = []

        async def fake_notify(platform, subject, text, **kwargs):
            pass

        async def fake_send_quran_pages(session, platform_value, chat_id, *, khatm, user_id, page_start, page_end, **kwargs):
            pushed.append((page_start, page_end))

        # Same day: one-portion-per-day means nothing is due yet.
        delivered_today = await reminder_service.deliver_due_next_portions(session, fake_notify, tz_name, fake_send_quran_pages)
        assert delivered_today == 0
        assert pushed == []

        # Simulate a full day having passed since completion.
        completed = await allocation_service.get_current_portion(session, khatm_id, member.id)
        assert completed is None  # nothing assigned yet — confirms one-portion-per-day held
        from sqlalchemy import select
        from khatmsaz.modules.allocation.models import KhatmPortion, PortionStatus
        completed_portion = (
            await session.execute(
                select(KhatmPortion).where(
                    KhatmPortion.khatm_id == khatm_id, KhatmPortion.status == PortionStatus.COMPLETED
                )
            )
        ).scalar_one()
        completed_portion.completed_at = datetime.now(timezone.utc) - timedelta(days=1, hours=1)
        completed_portion.updated_at = completed_portion.completed_at
        await session.flush()

        delivered_next_day = await reminder_service.deliver_due_next_portions(session, fake_notify, tz_name, fake_send_quran_pages)
        assert delivered_next_day == 1
        assert pushed == [(3, 4)]

        from khatmsaz.modules.notification.models import NotificationPreference
        from khatmsaz.modules.settings.models import UserSettings
        await session.execute(delete(NotificationPreference).where(NotificationPreference.participation_id == member.id))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.khatm_id == khatm_id))
        from khatmsaz.modules.allocation.models import KhatmAllocationPlan
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.khatm_id == khatm_id))
        await session.execute(delete(type(member)).where(type(member).khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.id == member_identity_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == member_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
