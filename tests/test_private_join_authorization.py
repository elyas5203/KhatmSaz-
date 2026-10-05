from types import SimpleNamespace

import pytest

from khatmsaz.core.ids import new_id
from khatmsaz.modules.khatm_workflow import service as workflow_service


@pytest.mark.asyncio
async def test_private_join_approval_rejects_non_creator_before_join(monkeypatch):
    creator_id = new_id()
    attacker_id = new_id()
    khatm_id = new_id()
    requester_id = new_id()

    async def fake_get_khatm(_session, requested_khatm_id):
        assert requested_khatm_id == khatm_id
        return SimpleNamespace(id=khatm_id, creator_user_id=creator_id)

    async def must_not_join(*_args, **_kwargs):
        raise AssertionError("unauthorized approval reached the join path")

    monkeypatch.setattr(workflow_service.khatm_service, "get_khatm_for_update", fake_get_khatm)
    monkeypatch.setattr(workflow_service, "_complete_join", must_not_join)

    with pytest.raises(PermissionError, match="only the khatm creator"):
        await workflow_service.approve_join_request(
            object(), khatm_id, requester_id, creator_user_id=attacker_id
        )
