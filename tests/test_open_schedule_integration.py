from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import delete

import khatmsaz.core.model_registry  # noqa: F401  # register all FK targets in focused runs
from khatmsaz.core.db import session_scope
from khatmsaz.config import get_settings
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm import service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum


@pytest.mark.integration
@pytest.mark.asyncio
async def test_open_khatm_schedule_validation_and_due_rules():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        session.add(Khatm(
            id=khatm_id, creator_user_id=user_id, title="برنامه آزاد",
            template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
            status=KhatmStatus.ACTIVE,
        ))
        await session.flush()
        khatm = await service.set_schedule(session, khatm_id=khatm_id, creator_user_id=user_id, raw="weekly:0,2,4")
        assert khatm.schedule_kind == "WEEKLY"
        assert service.schedule_is_due(khatm, date(2026, 9, 14))
        assert not service.schedule_is_due(khatm, date(2026, 9, 15))
        khatm = await service.set_schedule(session, khatm_id=khatm_id, creator_user_id=user_id, raw="off")
        assert khatm.schedule_kind == "NONE"
        with pytest.raises(ValueError):
            await service.set_schedule(session, khatm_id=khatm_id, creator_user_id=user_id, raw="every:0")
        local_today = datetime.now(ZoneInfo(get_settings().app_timezone)).date()
        yesterday = (local_today - timedelta(days=1)).isoformat()
        with pytest.raises(ValueError):
            await service.set_schedule(session, khatm_id=khatm_id, creator_user_id=user_id, raw=f"date:{yesterday}")
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
