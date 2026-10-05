from types import SimpleNamespace
from uuid import uuid4

import pytest

from khatmsaz.bot.keyboards import (
    pack_join_callback_data,
    unpack_join_callback_data,
    unpack_join_callback_route,
)
from khatmsaz.modules.bot_registry.models import BotCategory
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm_workflow import service as workflow_service


def test_private_join_callback_preserves_member_bot_route_under_telegram_limit():
    khatm_id, user_id = uuid4(), uuid4()
    bot = SimpleNamespace(
        khatmsaz_platform=Platform.TELEGRAM,
        khatmsaz_category=BotCategory.SALAWAT,
        khatmsaz_language="fa",
    )

    packed = pack_join_callback_data("approve_join", khatm_id, user_id, member_bot=bot)

    assert len(packed.encode()) <= 64
    assert unpack_join_callback_data(packed.split(":", 1)[1]) == (str(khatm_id), str(user_id))
    assert unpack_join_callback_route(packed.split(":", 1)[1]) == ("TELEGRAM", "SALAWAT", "fa")


def test_old_private_join_callbacks_remain_compatible():
    packed = pack_join_callback_data("approve_join", uuid4(), uuid4())
    assert unpack_join_callback_route(packed.split(":", 1)[1]) is None


@pytest.mark.asyncio
async def test_private_approval_records_originating_member_bot(monkeypatch):
    creator_id, requester_id, khatm_id, bot_instance_id = [uuid4() for _ in range(4)]
    khatm = SimpleNamespace(id=khatm_id, creator_user_id=creator_id)
    recorded = {}

    async def fake_get_khatm(_session, _khatm_id):
        return khatm

    async def fake_complete(_session, _khatm, _user_id, *, joined_via_bot_instance_id=None):
        recorded["bot_instance_id"] = joined_via_bot_instance_id
        return khatm, object(), None, False

    monkeypatch.setattr(workflow_service.khatm_service, "get_khatm_for_update", fake_get_khatm)
    monkeypatch.setattr(workflow_service, "_complete_join", fake_complete)

    await workflow_service.approve_join_request(
        object(), khatm_id, requester_id, creator_user_id=creator_id,
        joined_via_bot_instance_id=bot_instance_id,
    )

    assert recorded["bot_instance_id"] == bot_instance_id
