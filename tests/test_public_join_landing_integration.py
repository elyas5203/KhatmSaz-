"""Public invitation landing page backed by the real invitation record."""

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.core.security import hash_token
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.invitation import repository as invitation_repository
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.invitation.models import KhatmInvitation
from khatmsaz.modules.khatm.models import (
    CreatorDisplayMode,
    Khatm,
    KhatmStatus,
    KhatmTemplateType,
    KhatmTypeEnum,
)
from khatmsaz.web.app import app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_public_join_page_previews_without_joining_and_rejects_cancelled_link():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="خادم آزمون"))
        session.add(
            Khatm(
                id=khatm_id,
                creator_user_id=user_id,
                title="ختم عمومی آزمایشی",
                niyyat="به نیت سلامتی",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE,
                creator_display_mode=CreatorDisplayMode.FIRST_NAME.value,
            )
        )
        await session.flush()
        token = await invitation_service.create_invitation(session, khatm_id, user_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        page = await client.get(f"/join/{token}")
        assert page.status_code == 200
        assert "ختم عمومی آزمایشی" in page.text
        assert "به نیت سلامتی" in page.text
        assert "بازکردن این صفحه یعنی عضو نشده‌اید" in page.text
        assert "خادم" in page.text

        async with session_scope() as session:
            invitation = await invitation_repository.get_by_token_hash(
                session, hash_token(token)
            )
            invitation.cancelled_at = datetime.now(timezone.utc)
            await session.flush()

        cancelled = await client.get(f"/join/{token}")
        assert cancelled.status_code == 404
        assert "لینک منقضی یا لغو شده است" in cancelled.text

    async with session_scope() as session:
        await session.execute(delete(KhatmInvitation).where(KhatmInvitation.khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
