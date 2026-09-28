"""Regression: join_via_token used to NOT accept joined_via_bot_instance_id,
so every member-bot commitment/open join crashed with
`TypeError: join_via_token() got an unexpected keyword argument
'joined_via_bot_instance_id'` (live QA, 2026-09-27). This asserts the value
threads all the way to participation_service.join without a DB."""
from types import SimpleNamespace
from uuid import uuid4

import pytest

from khatmsaz.modules.khatm_workflow import service as workflow
from khatmsaz.modules.khatm.models import KhatmStatus, KhatmTypeEnum, KhatmVisibility, KhatmTemplateType


@pytest.mark.asyncio
async def test_join_via_token_threads_bot_instance_id(monkeypatch):
    khatm_id = uuid4()
    instance_id = uuid4()
    recorded = {}

    khatm = SimpleNamespace(
        id=khatm_id, status=KhatmStatus.ACTIVE, visibility=KhatmVisibility.PUBLIC,
        khatm_type=KhatmTypeEnum.OPEN, template_type=KhatmTemplateType.SALAWAT,
        capacity=None, repetition_target=100,
    )

    async def fake_resolve(_session, _token):
        return khatm_id

    async def fake_get_khatm(_session, _kid):
        return khatm

    async def fake_join(
        _session, _kid, _uid, *, capacity=None, joined_via_bot_instance_id=None,
        force_open=False,
    ):
        recorded["capacity"] = capacity
        recorded["instance"] = joined_via_bot_instance_id
        recorded["force_open"] = force_open
        return SimpleNamespace(id=uuid4()), False  # (participation, was_waitlisted)

    monkeypatch.setattr(workflow.invitation_service, "resolve_khatm_id", fake_resolve)
    monkeypatch.setattr(workflow.khatm_service, "get_khatm", fake_get_khatm)
    monkeypatch.setattr(workflow.participation_service, "join", fake_join)

    khatm_out, participation, first_portion, waitlisted = await workflow.join_via_token(
        object(), token="TOK", user_id=uuid4(), joined_via_bot_instance_id=instance_id,
    )

    assert recorded["instance"] == instance_id, "bot instance id not threaded to participation.join"
    assert recorded["force_open"] is False
    assert waitlisted is False
    assert first_portion is None  # OPEN khatm → no immediate portion


@pytest.mark.asyncio
async def test_quran_join_is_member_controlled_without_auto_allocation(monkeypatch):
    khatm_id = uuid4()
    recorded = {}
    khatm = SimpleNamespace(
        id=khatm_id, status=KhatmStatus.ACTIVE, visibility=KhatmVisibility.PUBLIC,
        khatm_type=KhatmTypeEnum.COMMITMENT,
        template_type=KhatmTemplateType.QURAN_PAGE,
        capacity=10, repetition_target=None,
    )

    async def fake_resolve(_session, _token):
        return khatm_id

    async def fake_get_khatm(_session, _kid):
        return khatm

    async def fake_join(
        _session, _kid, _uid, *, capacity=None, joined_via_bot_instance_id=None,
        force_open=False,
    ):
        recorded.update(capacity=capacity, force_open=force_open)
        return SimpleNamespace(id=uuid4()), False

    async def must_not_allocate(*_args, **_kwargs):
        raise AssertionError("Quran join must not allocate a fixed portion")

    monkeypatch.setattr(workflow.invitation_service, "resolve_khatm_id", fake_resolve)
    monkeypatch.setattr(workflow.khatm_service, "get_khatm", fake_get_khatm)
    monkeypatch.setattr(workflow.participation_service, "join", fake_join)
    monkeypatch.setattr(workflow.allocation_service, "allocate_next_portion_to", must_not_allocate)

    _, _, first_portion, waitlisted = await workflow.join_via_token(
        object(), token="TOK", user_id=uuid4()
    )

    assert recorded == {"capacity": None, "force_open": True}
    assert first_portion is None
    assert waitlisted is False
