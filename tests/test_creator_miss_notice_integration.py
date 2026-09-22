"""Owner decision (2026-09-21/22): missed portions never notify the member or
release their portion. After 2 consecutive missed days (threshold=2, window=3),
the **creator** is told the member's name, phone number, and asked "what should
we do?" so they can contact the member and decide whether to remove them. See
`reminder_engine.service._maybe_record_miss_and_notify_creator`."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401 — registers FK target table
from khatmsaz.modules.notification.models import NotificationKind, NotificationLog
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.reminder_engine import service as reminder_service


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_notified_only_after_threshold_and_member_never_notified():
    creator_id, member_id, khatm_id = (new_id() for _ in range(3))
    creator_identity_id, member_identity_id = new_id(), new_id()

    async with session_scope() as session:
        session.add_all([
            User(id=creator_id),
            User(id=member_id),
            PlatformIdentity(id=creator_identity_id, user_id=creator_id, platform=Platform.TELEGRAM, subject="miss-notice-creator"),
            PlatformIdentity(id=member_identity_id, user_id=member_id, platform=Platform.TELEGRAM, subject="miss-notice-member"),
        ])
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="ختم آستانه دیرکرد",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, daily_deadline_hour=23,
        )
        session.add(khatm)
        await session.flush()
        khatm = await khatm_service.set_miss_notice_policy(
            session, khatm_id=khatm_id, creator_user_id=creator_id, threshold=2, window_days=7
        )
        member = await participation_repository.create(session, khatm_id, member_id)

        sent = []

        async def fake_notify(platform, subject, text):
            sent.append((platform, subject, text))

        # First miss ever: below threshold (1 < 2) — no creator notification yet.
        await reminder_service._maybe_record_miss_and_notify_creator(session, fake_notify, member, khatm)
        assert sent == []

        # Backdate that first miss log so today's call isn't deduped by
        # "already sent today" and counts as a second, separate miss day.
        await session.execute(
            NotificationLog.__table__.update()
            .where(NotificationLog.participation_id == member.id)
            .values(sent_at=datetime.now(timezone.utc) - timedelta(days=1))
        )

        # Second miss (today): reaches threshold=2 — creator gets notified.
        await reminder_service._maybe_record_miss_and_notify_creator(session, fake_notify, member, khatm)
        assert len(sent) == 1
        platform, subject, text = sent[0]
        assert subject == "miss-notice-creator"
        assert "۲" in text or "2" in text  # mentions the miss count somehow

        # The member themself must never be notified by this function.
        assert all(subject != "miss-notice-member" for _, subject, _ in sent)

        from khatmsaz.modules.settings.models import UserSettings
        await session.execute(delete(NotificationLog).where(NotificationLog.participation_id == member.id))
        await session.execute(delete(type(member)).where(type(member).khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.id.in_([creator_identity_id, member_identity_id])))
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([creator_id, member_id])))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_notified_with_phone_after_two_consecutive_missed_days():
    """Owner decision (2026-09-22): creator notification must include member's
    phone number and ask 'what should we do?' Default window is now 3 days
    (threshold=2 = consecutive missed days)."""
    from khatmsaz.modules.settings import service as settings_service

    creator_id, member_id, khatm_id = (new_id() for _ in range(3))
    creator_identity_id, member_identity_id = new_id(), new_id()

    async with session_scope() as session:
        session.add_all([
            User(id=creator_id),
            User(id=member_id),
            PlatformIdentity(id=creator_identity_id, user_id=creator_id, platform=Platform.TELEGRAM, subject="miss-phone-creator"),
            PlatformIdentity(id=member_identity_id, user_id=member_id, platform=Platform.TELEGRAM, subject="miss-phone-member"),
        ])
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="ختم شماره‌تلفن",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, daily_deadline_hour=23,
            miss_notice_threshold=2, miss_notice_window_days=3,
        )
        session.add(khatm)
        await session.flush()

        # Give the member a contact phone
        member_settings = await settings_service.get_or_create(session, member_id)
        member_settings.contact_phone = "09123456789"

        member = await participation_repository.create(session, khatm_id, member_id)
        sent = []

        async def fake_notify(platform, subject, text):
            sent.append((platform, subject, text))

        # First miss (below threshold)
        await reminder_service._maybe_record_miss_and_notify_creator(session, fake_notify, member, khatm)
        assert sent == []

        # Back-date to simulate yesterday's miss
        await session.execute(
            NotificationLog.__table__.update()
            .where(NotificationLog.participation_id == member.id)
            .values(sent_at=datetime.now(timezone.utc) - timedelta(days=1))
        )

        # Second miss — threshold reached
        await reminder_service._maybe_record_miss_and_notify_creator(session, fake_notify, member, khatm)
        assert len(sent) == 1
        _, subject, text = sent[0]
        assert subject == "miss-phone-creator"
        assert "09123456789" in text
        assert "miss-phone-member" not in [s for _, s, _ in sent]

        from khatmsaz.modules.settings.models import UserSettings
        await session.execute(delete(NotificationLog).where(NotificationLog.participation_id == member.id))
        await session.execute(delete(type(member)).where(type(member).khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.id.in_([creator_identity_id, member_identity_id])))
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([creator_id, member_id])))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
