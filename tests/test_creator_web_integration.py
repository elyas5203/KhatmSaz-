"""Real PostgreSQL + ASGI coverage for the creator-owned dashboard."""

from io import BytesIO

import pytest
from httpx import ASGITransport, AsyncClient
from openpyxl import load_workbook
from sqlalchemy import delete, select

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation.models import (
    KhatmAllocationPlan,
    KhatmPortion,
    PortionStatus,
    PortionUnitKind,
)
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.notification.models import NotificationKind, NotificationLog
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.open_contribution import service as contribution_service
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.session.models import Session
from khatmsaz.modules.settings.models import Gender, UserSettings
from khatmsaz.web.app import CREATOR_COOKIE_NAME, app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_dashboard_is_scoped_and_shows_full_member_details():
    creator_id, member_id, other_id = new_id(), new_id(), new_id()
    khatm_id, other_khatm_id, participation_id, plan_id = new_id(), new_id(), new_id(), new_id()
    async with session_scope() as session:
        creator = User(id=creator_id, display_name="سازنده تست")
        member = User(id=member_id, display_name="عضو کامل")
        other = User(id=other_id, display_name="سازنده دیگر")
        session.add_all([creator, member, other])
        session.add_all(
            [
                Khatm(
                    id=khatm_id,
                    creator_user_id=creator_id,
                    title="ختم خصوصی گزارش",
                    template_type=KhatmTemplateType.QURAN_PAGE,
                    khatm_type=KhatmTypeEnum.COMMITMENT,
                    status=KhatmStatus.ACTIVE,
                ),
                Khatm(
                    id=other_khatm_id,
                    creator_user_id=other_id,
                    title="ختم شخص دیگر",
                    template_type=KhatmTemplateType.SALAWAT,
                    khatm_type=KhatmTypeEnum.OPEN,
                    status=KhatmStatus.ACTIVE,
                ),
                UserSettings(
                    user_id=member_id,
                    contact_phone="+989121234567",
                    province="تهران",
                    city="تهران",
                    gender=Gender.MALE,
                ),
                Participation(
                    id=participation_id,
                    khatm_id=khatm_id,
                    user_id=member_id,
                    is_committed=True,
                    backup_reader_opt_in=True,
                ),
            ]
        )
        await session.flush()
        session.add(KhatmAllocationPlan(id=plan_id, khatm_id=khatm_id, unit_kind=PortionUnitKind.POSITIONAL, total_portions=1))
        session.add(
            KhatmPortion(
                id=new_id(), plan_id=plan_id, khatm_id=khatm_id, sequence=1,
                unit_kind=PortionUnitKind.POSITIONAL, unit_start=1, unit_end=2,
                status=PortionStatus.COMPLETED, participation_id=participation_id,
            )
        )
        session.add(
            NotificationLog(
                id=new_id(), participation_id=participation_id, kind=NotificationKind.FOLLOW_UP
            )
        )
        session.add(
            OpenContribution(
                id=new_id(), khatm_id=khatm_id, participation_id=participation_id,
                amount=150, counted_amount=100, surplus_amount=50,
            )
        )
        await session.flush()
        token = await session_service.issue_creator_session(session, creator)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        anonymous = await client.get("/creator", follow_redirects=False)
        assert anonymous.status_code == 303
        assert anonymous.headers["location"] == "/creator/login"
        client.cookies.set(CREATOR_COOKIE_NAME, token)
        dashboard = await client.get("/creator")
        assert dashboard.status_code == 200
        assert "ختم خصوصی گزارش" in dashboard.text
        assert "ختم شخص دیگر" not in dashboard.text
        detail = await client.get(f"/creator/khatms/{khatm_id}")
        assert detail.status_code == 200
        for expected in (
            "عضو کامل", "+989121234567", "تهران", "آقا", "یار ذخیره",
            "پیگیری ثبت‌شده", ">1<", "مازاد", ">50<",
        ):
            assert expected in detail.text
        filtered = await client.get(f"/creator/khatms/{khatm_id}?q=+98912")
        assert "عضو کامل" in filtered.text
        exported = await client.get(f"/creator/khatms/{khatm_id}/export.xlsx")
        assert exported.status_code == 200
        workbook = load_workbook(BytesIO(exported.content), read_only=True)
        sheet = workbook["اعضا"]
        values = list(sheet.values)
        assert values[1][0] == "عضو کامل"
        assert values[1][1] == "+989121234567"
        assert isinstance(values[1][5], str) and "·" in values[1][5]
        denied = await client.get(f"/creator/khatms/{other_khatm_id}")
        assert denied.status_code == 404

    async with session_scope() as session:
        await session.execute(delete(NotificationLog).where(NotificationLog.participation_id == participation_id))
        await session.execute(delete(OpenContribution).where(OpenContribution.participation_id == participation_id))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.plan_id == plan_id))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.id == plan_id))
        await session.execute(delete(Participation).where(Participation.id == participation_id))
        # `_creator()` in web/app.py now resolves the creator's language via
        # `settings_service.get_or_create`, which creates a UserSettings row
        # for the creator too (previously only `member_id` had one) —
        # clean up all three, not just member_id.
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([creator_id, member_id, other_id])))
        await session.execute(delete(Session).where(Session.user_id == creator_id))
        await session.execute(delete(Khatm).where(Khatm.id.in_([khatm_id, other_khatm_id])))
        from khatmsaz.modules.wallet.models import Wallet
        await session.execute(delete(Wallet).where(Wallet.user_id == creator_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id, other_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_open_contribution_persists_counted_and_surplus_split():
    user_id, khatm_id, participation_id = new_id(), new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(
            Khatm(
                id=khatm_id,
                creator_user_id=user_id,
                title="ثبت مازاد",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE,
                repetition_target=100,
            )
        )
        session.add(Participation(id=participation_id, khatm_id=khatm_id, user_id=user_id))
        await session.flush()
        counted, surplus, total = await contribution_service.log_contribution(
            session, khatm_id, participation_id, 150, 100
        )
        assert (counted, surplus, total) == (100, 50, 150)
        row = (
            await session.execute(
                select(OpenContribution).where(
                    OpenContribution.participation_id == participation_id
                )
            )
        ).scalar_one()
        assert row.counted_amount == 100
        assert row.surplus_amount == 50

    async with session_scope() as session:
        await session.execute(delete(OpenContribution).where(OpenContribution.participation_id == participation_id))
        await session.execute(delete(Participation).where(Participation.id == participation_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
