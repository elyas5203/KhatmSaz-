"""Real PostgreSQL + ASGI coverage for admin khatm search."""

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
async def test_admin_can_search_khatms_by_title_creator_and_uuid():
    admin_id, creator_id, khatm_id = new_id(), new_id(), new_id()
    async with session_scope() as session:
        admin = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="مدیر جست‌وجو")
        creator = User(id=creator_id, display_name="سازنده یکتای نیلوفر")
        session.add_all([admin, creator])
        await session.flush()
        session.add(
            Khatm(
                id=khatm_id, creator_user_id=creator_id, title="ختم یکتای سحرگاهی",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN, status=KhatmStatus.ACTIVE,
                repetition_target=100,
            )
        )
        await session.flush()
        token = await session_service.issue_admin_session(session, admin)

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            client.cookies.set(COOKIE_NAME, token)
            for query in ("سحرگاهی", "نیلوفر", str(khatm_id)):
                response = await client.get("/khatms", params={"q": query})
                assert response.status_code == 200
                assert "ختم یکتای سحرگاهی" in response.text
            empty = await client.get("/khatms", params={"q": "عبارت ناموجود قطعی"})
            assert "ختم یکتای سحرگاهی" not in empty.text
            assert "نتیجه‌ای پیدا نشد" in empty.text
    finally:
        async with session_scope() as session:
            await session.execute(delete(Session).where(Session.user_id == admin_id))
            await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
            await session.execute(delete(User).where(User.id.in_([admin_id, creator_id])))
