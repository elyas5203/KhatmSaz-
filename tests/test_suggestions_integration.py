"""Real PostgreSQL coverage for member -> creator ticket routing."""

import pytest
from sqlalchemy import delete

from khatmsaz.bot.handlers.suggestions import _member_creators
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.bot_registry.models import BotCategory, BotInstance, BotRole
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation


@pytest.mark.integration
@pytest.mark.asyncio
async def test_member_can_choose_each_creator_and_keeps_exact_member_bot_route():
    member_id, first_creator_id, second_creator_id = new_id(), new_id(), new_id()
    first_khatm_id, second_khatm_id = new_id(), new_id()
    telegram_bot_id, bale_bot_id = new_id(), new_id()
    participation_ids = [new_id(), new_id()]
    async with session_scope() as session:
        session.add_all([
            User(id=member_id, display_name="عضو"),
            User(id=first_creator_id, role=UserRole.CREATOR, display_name="سازنده یک"),
            User(id=second_creator_id, role=UserRole.CREATOR, display_name="سازنده دو"),
            BotInstance(id=telegram_bot_id, platform="TELEGRAM", bot_role=BotRole.MEMBER.value,
                        category=BotCategory.QURAN.value, language="fa", username=f"ticket_tg_{telegram_bot_id}", display_name="عضو قرآن"),
            BotInstance(id=bale_bot_id, platform="BALE", bot_role=BotRole.MEMBER.value,
                        category=BotCategory.SALAWAT.value, language="fa", username=f"ticket_bale_{bale_bot_id}", display_name="عضو صلوات"),
            Khatm(id=first_khatm_id, creator_user_id=first_creator_id, title="ختم یک",
                  template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.OPEN, status=KhatmStatus.ACTIVE),
            Khatm(id=second_khatm_id, creator_user_id=second_creator_id, title="ختم دو",
                  template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN, status=KhatmStatus.ACTIVE),
        ])
        await session.flush()
        session.add_all([
            Participation(id=participation_ids[0], khatm_id=first_khatm_id, user_id=member_id,
                          joined_via_bot_instance_id=telegram_bot_id),
            Participation(id=participation_ids[1], khatm_id=second_khatm_id, user_id=member_id,
                          joined_via_bot_instance_id=bale_bot_id),
        ])
        await session.flush()

        choices = await _member_creators(session, member_id)
        assert {row["id"] for row in choices} == {first_creator_id, second_creator_id}
        assert {row["bot_instance_id"] for row in choices} == {telegram_bot_id, bale_bot_id}

        await session.execute(delete(Participation).where(Participation.id.in_(participation_ids)))
        await session.execute(delete(Khatm).where(Khatm.id.in_([first_khatm_id, second_khatm_id])))
        await session.execute(delete(BotInstance).where(BotInstance.id.in_([telegram_bot_id, bale_bot_id])))
        await session.execute(delete(User).where(User.id.in_([member_id, first_creator_id, second_creator_id])))
