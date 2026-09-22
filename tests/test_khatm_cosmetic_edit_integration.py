import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_can_edit_only_cosmetic_fields_on_active_khatm():
    user_id, other_id, active_id, draft_id = [new_id() for _ in range(4)]
    async with session_scope() as session:
        session.add_all([
            User(id=user_id), User(id=other_id),
            Khatm(
                id=active_id, creator_user_id=user_id, title="قدیم",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE, welcome_text="قبلی",
            ),
            Khatm(
                id=draft_id, creator_user_id=user_id, title="پیش‌نویس",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.DRAFT,
            ),
        ])
        await session.flush()
        edited = await khatm_service.update_title(
            session, khatm_id=active_id, creator_user_id=user_id, title="جدید"
        )
        edited = await khatm_service.update_welcome_text(
            session, khatm_id=active_id, creator_user_id=user_id, welcome_text=None
        )
        assert edited.title == "جدید"
        assert edited.welcome_text is None
        with pytest.raises(ValueError):
            await khatm_service.update_title(
                session, khatm_id=active_id, creator_user_id=other_id, title="غیرمجاز"
            )
        with pytest.raises(ValueError):
            await khatm_service.update_title(
                session, khatm_id=draft_id, creator_user_id=user_id, title="نباید"
            )
        await session.execute(delete(Khatm).where(Khatm.id.in_([active_id, draft_id])))
        await session.execute(delete(User).where(User.id.in_([user_id, other_id])))
