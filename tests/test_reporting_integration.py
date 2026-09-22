from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation.models import KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.reporting.service import get_personal_report
from khatmsaz.modules.identity.models import User


@pytest.mark.integration
@pytest.mark.asyncio
async def test_personal_report_aggregates_completed_work_and_monthly_contributions():
    user_id, khatm_id = new_id(), new_id()
    participation_id, plan_id = new_id(), new_id()
    current_portion_id, old_portion_id, contribution_id = new_id(), new_id(), new_id()
    now = datetime(2026, 9, 16, 12, tzinfo=timezone.utc)
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(
            Khatm(
                id=khatm_id, creator_user_id=user_id, title="گزارش آزمایشی",
                template_type=KhatmTemplateType.QURAN_PAGE,
                khatm_type=KhatmTypeEnum.COMMITMENT, status=KhatmStatus.ACTIVE,
            )
        )
        await session.flush()
        session.add(Participation(
            id=participation_id, khatm_id=khatm_id, user_id=user_id,
            status=ParticipationStatus.ACTIVE,
        ))
        await session.flush()
        session.add(KhatmAllocationPlan(
            id=plan_id, khatm_id=khatm_id, unit_kind=PortionUnitKind.POSITIONAL, total_portions=2,
        ))
        await session.flush()
        session.add_all([
            KhatmPortion(
                id=current_portion_id, plan_id=plan_id, khatm_id=khatm_id, sequence=1,
                unit_kind=PortionUnitKind.POSITIONAL, unit_start=1, unit_end=2,
                status=PortionStatus.COMPLETED, participation_id=participation_id,
                completed_at=datetime(2026, 9, 10, tzinfo=timezone.utc),
            ),
            KhatmPortion(
                id=old_portion_id, plan_id=plan_id, khatm_id=khatm_id, sequence=2,
                unit_kind=PortionUnitKind.POSITIONAL, unit_start=3, unit_end=4,
                status=PortionStatus.COMPLETED, participation_id=participation_id,
                completed_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
            ),
            OpenContribution(
                id=contribution_id, khatm_id=khatm_id, participation_id=participation_id,
                amount=125.0, recorded_at=datetime(2026, 9, 5, tzinfo=timezone.utc),
            ),
        ])
        await session.flush()

        report = await get_personal_report(session, user_id, now=now)
        assert report.active_khatms == 1
        assert report.completed_khatms == 0
        assert report.completed_portions_total == 2
        assert report.completed_portions_this_month == 1
        assert report.contributions_this_month == 125.0

        await session.execute(delete(OpenContribution).where(OpenContribution.id == contribution_id))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.id.in_([current_portion_id, old_portion_id])))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.id == plan_id))
        await session.execute(delete(Participation).where(Participation.id == participation_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
