"""Real PostgreSQL coverage for positive, timezone-aware monthly delivery."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation.models import (
    KhatmAllocationPlan,
    KhatmPortion,
    PortionStatus,
    PortionUnitKind,
)
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.monthly_report import service as monthly_report_service
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_previous_month_report_is_positive_localized_and_sent_once():
    user_id = new_id()
    quran_id, salawat_id = new_id(), new_id()
    quran_participation_id, salawat_participation_id, plan_id = new_id(), new_id(), new_id()
    september = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)
    now = datetime(2026, 10, 2, 8, 30, tzinfo=timezone.utc)
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="گزارش ماهانه"))
        session.add(
            PlatformIdentity(
                id=new_id(), user_id=user_id, platform=Platform.TELEGRAM, subject="82001"
            )
        )
        session.add(
            UserSettings(user_id=user_id, timezone="Asia/Tehran", language="fa")
        )
        session.add_all(
            [
                Khatm(
                    id=quran_id,
                    creator_user_id=user_id,
                    title="قرآن ماهانه",
                    template_type=KhatmTemplateType.QURAN_PAGE,
                    khatm_type=KhatmTypeEnum.COMMITMENT,
                    status=KhatmStatus.COMPLETED,
                    completed_at=september,
                ),
                Khatm(
                    id=salawat_id,
                    creator_user_id=user_id,
                    title="صلوات ماهانه",
                    template_type=KhatmTemplateType.SALAWAT,
                    khatm_type=KhatmTypeEnum.OPEN,
                    status=KhatmStatus.ACTIVE,
                ),
                Participation(
                    id=quran_participation_id, khatm_id=quran_id, user_id=user_id
                ),
                Participation(
                    id=salawat_participation_id, khatm_id=salawat_id, user_id=user_id
                ),
            ]
        )
        await session.flush()
        session.add(
            KhatmAllocationPlan(
                id=plan_id, khatm_id=quran_id,
                unit_kind=PortionUnitKind.POSITIONAL, total_portions=1,
            )
        )
        session.add(
            KhatmPortion(
                id=new_id(), plan_id=plan_id, khatm_id=quran_id, sequence=1,
                unit_kind=PortionUnitKind.POSITIONAL, unit_start=3, unit_end=4,
                status=PortionStatus.COMPLETED,
                participation_id=quran_participation_id,
                completed_at=september,
            )
        )
        session.add(
            OpenContribution(
                id=new_id(), khatm_id=salawat_id,
                participation_id=salawat_participation_id,
                amount=120, counted_amount=120, surplus_amount=0,
                recorded_at=september,
            )
        )

    sent: list[tuple[str, str, str]] = []

    async def notify(platform: str, subject: str, text: str) -> None:
        sent.append((platform, subject, text))

    async with session_scope() as session:
        assert await monthly_report_service.deliver_due(
            session, notify, now=now, report_day=1, report_hour=10, user_ids={user_id}
        ) == 1
        assert len(sent) == 1
        platform, subject, text = sent[0]
        assert (platform, subject) == ("TELEGRAM", "82001")
        assert "2026-09" in text
        assert "صفحه قرآن: 2" in text
        assert "صلوات: 120" in text
        assert "ختم به‌پایان‌رسیده: 1" in text
        assert "Miss" not in text and "غیبت" not in text
        settings = await session.get(UserSettings, user_id)
        assert settings.last_monthly_report_period == "2026-09"
        assert await monthly_report_service.deliver_due(
            session, notify, now=now, report_day=1, report_hour=10, user_ids={user_id}
        ) == 0
        assert len(sent) == 1

    async with session_scope() as session:
        await session.execute(delete(OpenContribution).where(OpenContribution.khatm_id == salawat_id))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.plan_id == plan_id))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.id == plan_id))
        await session.execute(delete(Participation).where(Participation.khatm_id.in_([quran_id, salawat_id])))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == user_id))
        await session.execute(delete(Khatm).where(Khatm.id.in_([quran_id, salawat_id])))
        await session.execute(delete(User).where(User.id == user_id))
