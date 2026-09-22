"""Owner request (2026-09-22): BACKLOG item 8 — today-vs-yesterday group
comparison for quantity-commitment (salawat/dua/laan) khatms.

Verifies that CommittedQuantityLog rows are inserted on progress recording
and that today_vs_yesterday_committed returns correct sums per calendar day.
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, update

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation import repository as allocation_repository
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.allocation.models import CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion
from khatmsaz.modules.identity.models import Platform, User
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_committed_quantity_today_vs_yesterday():
    creator_id, member_id, khatm_id = new_id(), new_id(), new_id()

    async with session_scope() as session:
        session.add(User(id=creator_id))
        session.add(User(id=member_id))
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="صلوات تعهدی تست",
            template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, repetition_target=1000,
        )
        session.add(khatm)
        await session.flush()
        participation, _ = await participation_service.join(session, khatm_id, member_id)
        first_portion = await allocation_service.assign_quantity_commitment(
            session, khatm_id, participation.id, 500
        )

    # Record progress today: 100 + 50
    async with session_scope() as session:
        await allocation_service.record_quantity_commitment_progress(session, khatm_id, participation.id, 100)
    async with session_scope() as session:
        await allocation_service.record_quantity_commitment_progress(session, khatm_id, participation.id, 50)

    # Back-date one log entry to yesterday
    async with session_scope() as session:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        await session.execute(
            update(CommittedQuantityLog)
            .where(CommittedQuantityLog.khatm_id == khatm_id)
            .values(logged_at=yesterday)
            .execution_options(synchronize_session=False)
            # back-date only the first entry (100); leave the second (50) as today
        )
        # Re-date the second entry to today explicitly by resetting to now
        logs = list((await session.execute(
            __import__("sqlalchemy", fromlist=["select"]).select(CommittedQuantityLog)
            .where(CommittedQuantityLog.khatm_id == khatm_id)
            .order_by(CommittedQuantityLog.logged_at.asc())
        )).scalars())
        # After bulk update above, both are yesterday — reset the last one to now
        logs[-1].logged_at = datetime.now(timezone.utc)

    async with session_scope() as session:
        today, yesterday_total = await allocation_service.today_vs_yesterday_committed(
            session, khatm_id, "Asia/Tehran"
        )
    assert today == 50
    assert yesterday_total == 100

    # Cleanup
    async with session_scope() as session:
        from khatmsaz.modules.invitation.models import KhatmInvitation
        await session.execute(delete(KhatmInvitation).where(KhatmInvitation.khatm_id == khatm_id))
        await session.execute(delete(CommittedQuantityLog).where(CommittedQuantityLog.khatm_id == khatm_id))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.khatm_id == khatm_id))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.khatm_id == khatm_id))
        from khatmsaz.modules.participation.models import Participation as KhatmParticipation
        await session.execute(delete(KhatmParticipation).where(KhatmParticipation.khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([creator_id, member_id])))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
