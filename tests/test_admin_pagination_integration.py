"""Real PostgreSQL pagination coverage for large Mini App lists."""

import re

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.session.models import Session
from khatmsaz.web.app import COOKIE_NAME, app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_khatm_and_user_searches_paginate_without_losing_filters():
    admin_id, creator_id = new_id(), new_id()
    khatm_ids = [new_id() for _ in range(26)]
    user_ids = [new_id() for _ in range(26)]
    async with session_scope() as session:
        admin = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="مدیر صفحه‌بندی")
        creator = User(id=creator_id, display_name="سازنده صفحه‌بندی")
        users = [User(id=user_id, display_name=f"کاربر صفحه‌بندی {index:02d}") for index, user_id in enumerate(user_ids)]
        session.add_all([admin, creator, *users])
        await session.flush()
        session.add_all([
            Khatm(
                id=khatm_id, creator_user_id=creator_id,
                title=f"ختم صفحه‌بندی {index:02d}",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN, status=KhatmStatus.ACTIVE,
                repetition_target=100,
            )
            for index, khatm_id in enumerate(khatm_ids)
        ])
        await session.flush()
        token = await session_service.issue_admin_session(session, admin)

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            client.cookies.set(COOKIE_NAME, token)
            khatm_page_1 = await client.get("/khatms", params={"q": "ختم صفحه‌بندی", "status": "ACTIVE"})
            khatm_page_2 = await client.get("/khatms", params={"q": "ختم صفحه‌بندی", "status": "ACTIVE", "page": 2})
            assert len(re.findall(r"ختم صفحه‌بندی \d{2}", khatm_page_1.text)) == 25
            assert len(re.findall(r"ختم صفحه‌بندی \d{2}", khatm_page_2.text)) == 1
            assert "صفحه بعد" in khatm_page_1.text and "صفحه قبل" in khatm_page_2.text
            assert 'name="status" value="ACTIVE"' in khatm_page_1.text

            user_page_1 = await client.get("/users", params={"q": "کاربر صفحه‌بندی"})
            user_page_2 = await client.get("/users", params={"q": "کاربر صفحه‌بندی", "page": 2})
            assert len(re.findall(r"کاربر صفحه‌بندی \d{2}", user_page_1.text)) == 25
            assert len(re.findall(r"کاربر صفحه‌بندی \d{2}", user_page_2.text)) == 1
            assert "صفحه بعد" in user_page_1.text and "صفحه قبل" in user_page_2.text
    finally:
        async with session_scope() as session:
            await session.execute(delete(Session).where(Session.user_id == admin_id))
            await session.execute(delete(Khatm).where(Khatm.id.in_(khatm_ids)))
            await session.execute(delete(User).where(User.id.in_([admin_id, creator_id, *user_ids])))
