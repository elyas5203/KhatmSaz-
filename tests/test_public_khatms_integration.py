import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum, KhatmVisibility


@pytest.mark.integration
@pytest.mark.asyncio
async def test_public_listing_only_returns_active_public_khatms():
    user_id, public_id, private_id, inactive_id = [new_id() for _ in range(4)]
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add_all([
            Khatm(
                id=public_id, creator_user_id=user_id, title="عمومی",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE, visibility=KhatmVisibility.PUBLIC,
            ),
            Khatm(
                id=private_id, creator_user_id=user_id, title="خصوصی",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE, visibility=KhatmVisibility.PRIVATE,
            ),
            Khatm(
                id=inactive_id, creator_user_id=user_id, title="غیرفعال",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.DRAFT, visibility=KhatmVisibility.PUBLIC,
            ),
        ])
        await session.flush()
        listed = await khatm_service.list_public_active(session)
        assert [item.id for item in listed] == [public_id]

        await session.execute(delete(Khatm).where(Khatm.id.in_([public_id, private_id, inactive_id])))
        await session.execute(delete(User).where(User.id == user_id))
