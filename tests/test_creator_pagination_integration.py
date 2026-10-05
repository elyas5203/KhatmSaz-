"""Real PostgreSQL pagination for creator-owned khatms and member reports."""

import re

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.session.models import Session
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.web.app import CREATOR_COOKIE_NAME, app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_recent_list_and_member_report_pagination():
    creator_id = new_id()
    khatm_ids = [new_id() for _ in range(26)]
    member_ids = [new_id() for _ in range(26)]
    participation_ids = [new_id() for _ in range(26)]
    report_khatm_id = khatm_ids[0]
    async with session_scope() as session:
        creator = User(id=creator_id, display_name="سازنده صفحه‌بندی گزارش")
        members = [
            User(id=user_id, display_name=f"عضو گزارش صفحه‌بندی {index:02d}")
            for index, user_id in enumerate(member_ids)
        ]
        session.add_all([creator, *members])
        await session.flush()
        session.add_all([
            Khatm(
                id=khatm_id, creator_user_id=creator_id,
                title=f"ختم سازنده صفحه‌بندی {index:02d}",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN, status=KhatmStatus.ACTIVE,
                repetition_target=100,
            )
            for index, khatm_id in enumerate(khatm_ids)
        ])
        await session.flush()
        session.add_all([
            Participation(
                id=participation_id, khatm_id=report_khatm_id, user_id=user_id
            )
            for participation_id, user_id in zip(participation_ids, member_ids, strict=True)
        ])
        await session.flush()
        token = await session_service.issue_creator_session(session, creator)

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            client.cookies.set(CREATOR_COOKIE_NAME, token)
            first = await client.get("/creator")
            listing = await client.get("/creator/khatms")
            assert len(re.findall(r"ختم سازنده صفحه‌بندی \d{2}", first.text)) == 6
            assert len(re.findall(r"ختم سازنده صفحه‌بندی \d{2}", listing.text)) == 26

            detail_first = await client.get(
                f"/creator/khatms/{report_khatm_id}", params={"q": "عضو گزارش صفحه‌بندی"}
            )
            detail_second = await client.get(
                f"/creator/khatms/{report_khatm_id}",
                params={"q": "عضو گزارش صفحه‌بندی", "page": 2},
            )
            assert len(re.findall(r"عضو گزارش صفحه‌بندی \d{2}", detail_first.text)) == 25
            assert len(re.findall(r"عضو گزارش صفحه‌بندی \d{2}", detail_second.text)) == 1
            assert "صفحه بعد" in detail_first.text and "صفحه قبل" in detail_second.text
            assert 'name="q" value="عضو گزارش صفحه‌بندی"' in detail_first.text
    finally:
        async with session_scope() as session:
            await session.execute(delete(Participation).where(Participation.id.in_(participation_ids)))
            await session.execute(delete(Session).where(Session.user_id == creator_id))
            # `_creator()` in web/app.py resolves the creator's language via
            # `settings_service.get_or_create`, which creates a UserSettings
            # row for the creator as a side effect of hitting `/creator`.
            await session.execute(delete(UserSettings).where(UserSettings.user_id == creator_id))
            await session.execute(delete(Khatm).where(Khatm.id.in_(khatm_ids)))
            from khatmsaz.modules.wallet.models import Wallet
            await session.execute(delete(Wallet).where(Wallet.user_id == creator_id))
            await session.execute(delete(User).where(User.id.in_([creator_id, *member_ids])))
