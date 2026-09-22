from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation import repository as allocation_repository
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.reminder_engine import service as reminder_service


@pytest.mark.integration
@pytest.mark.asyncio
async def test_thirty_day_inactive_member_portion_moves_to_backup_without_miss():
    creator_id, member_id, backup_id, khatm_id = (new_id() for _ in range(4))
    member_identity_id, backup_identity_id = new_id(), new_id()
    async with session_scope() as session:
        session.add_all([
            User(id=creator_id),
            User(id=member_id, last_activity_at=datetime.now(timezone.utc) - timedelta(days=31)),
            User(id=backup_id),
            PlatformIdentity(id=member_identity_id, user_id=member_id, platform=Platform.TELEGRAM, subject="inactive-member"),
            PlatformIdentity(id=backup_identity_id, user_id=backup_id, platform=Platform.TELEGRAM, subject="backup-reader"),
        ])
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="واگذاری عدم فعالیت",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, daily_deadline_hour=23,
        )
        session.add(khatm)
        await session.flush()
        member = await participation_repository.create(session, khatm_id, member_id)
        backup = await participation_repository.create(session, khatm_id, backup_id)
        await participation_repository.set_backup_reader_opt_in(session, backup.id, True)
        await allocation_service.generate_quran_page_plan(session, khatm_id, 4, pages_per_portion=2)
        assigned = await allocation_service.allocate_next_portion_to(session, khatm_id, member.id)
        assert assigned is not None
        sent = []

        async def notify(platform, subject, text):
            sent.append((platform, subject, text))

        moved = await reminder_service.delegate_inactive_portions(session, notify)
        refreshed = await session.get(type(assigned), assigned.id)
        assert moved == 1
        assert refreshed is not None and refreshed.participation_id == backup.id
        assert len(sent) == 2
        assert all("واگذار" in text for _, _, text in sent)

        await session.execute(delete(type(assigned)).where(type(assigned).khatm_id == khatm_id))
        plan = await allocation_repository.get_plan_by_khatm(session, khatm_id)
        if plan is not None:
            await session.execute(delete(type(plan)).where(type(plan).id == plan.id))
        await session.execute(delete(type(member)).where(type(member).khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(
            delete(PlatformIdentity).where(
                PlatformIdentity.id.in_([member_identity_id, backup_identity_id])
            )
        )
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id, backup_id])))
