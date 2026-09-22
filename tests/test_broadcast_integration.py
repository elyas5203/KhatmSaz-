import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_broadcast_requires_moderation_before_send_state():
    user_id, other_id, khatm_id = new_id(), new_id(), new_id()
    async with session_scope() as session:
        session.add_all([
            User(id=user_id), User(id=other_id),
            Khatm(
                id=khatm_id, creator_user_id=user_id, title="ختم تست",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE,
            ),
        ])
        await session.flush()
        item = await broadcast_service.submit(session, khatm_id=khatm_id, creator_user_id=user_id, body="پیام تست")
        assert item.status == BroadcastStatus.PENDING
        with pytest.raises(ValueError):
            await broadcast_service.submit(session, khatm_id=khatm_id, creator_user_id=other_id, body="نباید ثبت شود")
        approved = await broadcast_service.approve(session, item.id, "بررسی شد")
        assert approved.status == BroadcastStatus.APPROVED
        with pytest.raises(ValueError):
            await broadcast_service.approve(session, item.id)
        await session.execute(delete(KhatmBroadcast).where(KhatmBroadcast.id == item.id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([user_id, other_id])))
