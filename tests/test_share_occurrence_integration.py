"""Concurrency and receipt contracts on real PostgreSQL, never sqlite."""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from khatmsaz.core import model_registry  # noqa: F401
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.bot_registry.models import BotInstance
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.share_occurrence import service
from khatmsaz.modules.share_occurrence.models import ShareMessage, ShareOccurrence

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]
NOW = datetime(2026, 10, 3, 12, tzinfo=timezone.utc)


async def setup_membership():
    uid, kid, pid, bid = [new_id() for _ in range(4)]
    async with session_scope() as session:
        session.add(User(id=uid, display_name="عضو تست نوبت"))
        # NULL category/language avoid competing with seeded production slots.
        session.add(BotInstance(id=bid, platform="TELEGRAM", bot_role="MEMBER", display_name="بات تست", is_active=True))
        await session.flush()
        session.add(Khatm(id=kid, creator_user_id=uid, title="نوبت تست", template_type=KhatmTemplateType.SALAWAT))
        await session.flush()
        session.add(Participation(id=pid, khatm_id=kid, user_id=uid, joined_via_bot_instance_id=bid))
    return uid, kid, pid, bid


async def create(pid, bid, key="daily:2026-10-03", **overrides):
    values = dict(
        participation_id=pid, bot_instance_id=bid, source_key=key,
        amount=10, unit="COUNT", committed=True, scheduled_for=NOW,
    )
    values.update(overrides)
    async with session_scope() as session:
        occurrence, made = await service.create_once(session, **values)
        return occurrence.id, made


async def delivered(oid, bid):
    async with session_scope() as session:
        for key, purpose, mid in [("content:0", "CONTENT", 10), ("action", "ACTION", 11)]:
            await service.record_message(
                session, occurrence_id=oid, bot_instance_id=bid,
                component_key=key, purpose=purpose, chat_id="123", message_id=mid, sent_at=NOW,
            )
        await service.mark_delivered(session, oid, bot_instance_id=bid, when=NOW)


async def progress_writer(session, participation, occurrence):
    session.add(OpenContribution(
        id=new_id(), khatm_id=participation.khatm_id, participation_id=participation.id,
        amount=occurrence.amount, counted_amount=occurrence.amount, surplus_amount=0,
        note=str(occurrence.id),
    ))
    await session.flush()


async def test_concurrent_creation_returns_one_immutable_share():
    _, _, pid, bid = await setup_membership()
    results = await asyncio.gather(create(pid, bid), create(pid, bid))
    assert results[0][0] == results[1][0]
    assert sum(made for _, made in results) == 1
    with pytest.raises(service.OccurrenceConflictError):
        await create(pid, bid, amount=20)


async def test_concurrent_done_counts_exactly_once_and_keeps_tomorrow_outstanding():
    uid, _, pid, bid = await setup_membership()
    yesterday, _ = await create(pid, bid, "daily:2026-10-02", scheduled_for=NOW - timedelta(days=1))
    today, _ = await create(pid, bid)
    await delivered(yesterday, bid)
    await delivered(today, bid)

    async def finish():
        async with session_scope() as session:
            _, changed = await service.complete(
                session, yesterday, user_id=uid, bot_instance_id=bid, record_progress=progress_writer,
            )
            return changed

    assert sorted(await asyncio.gather(finish(), finish())) == [False, True]
    async with session_scope() as session:
        assert [item.id for item in await service.list_outstanding(session, pid)] == [today]
        count = await session.scalar(select(func.count()).select_from(OpenContribution).where(OpenContribution.participation_id == pid))
        assert count == 1
        assert (await session.get(ShareOccurrence, today)).completed_at is None


async def test_wrong_member_wrong_bot_and_no_content_cannot_complete():
    uid, _, pid, bid = await setup_membership()
    oid, _ = await create(pid, bid)
    async with session_scope() as session:
        with pytest.raises(ValueError, match="undelivered"):
            await service.complete(session, oid, user_id=uid, bot_instance_id=bid, record_progress=progress_writer)
        with pytest.raises(service.OccurrenceAccessError):
            await service.complete(session, oid, user_id=new_id(), bot_instance_id=bid, record_progress=progress_writer)
        with pytest.raises(service.OccurrenceAccessError):
            await service.complete(session, oid, user_id=uid, bot_instance_id=new_id(), record_progress=progress_writer)
        with pytest.raises(ValueError, match="receipts"):
            await service.mark_delivered(session, oid, bot_instance_id=bid)
        assert await service.cleanup_candidates(session, oid) == []


async def test_progress_failure_rolls_back_completion_and_contribution():
    uid, _, pid, bid = await setup_membership()
    oid, _ = await create(pid, bid)
    await delivered(oid, bid)

    async def fail_after_write(session, participation, occurrence):
        await progress_writer(session, participation, occurrence)
        raise RuntimeError("simulated failure")

    with pytest.raises(RuntimeError):
        async with session_scope() as session:
            await service.complete(session, oid, user_id=uid, bot_instance_id=bid, record_progress=fail_after_write)
    async with session_scope() as session:
        assert (await session.get(ShareOccurrence, oid)).completed_at is None
        assert await session.scalar(select(func.count()).select_from(OpenContribution).where(OpenContribution.participation_id == pid)) == 0
        _, changed = await service.complete(session, oid, user_id=uid, bot_instance_id=bid, record_progress=progress_writer)
        assert changed


async def test_cleanup_excludes_reading_media_and_tracks_only_successful_deletes():
    uid, _, pid, bid = await setup_membership()
    oid, _ = await create(pid, bid)
    await delivered(oid, bid)
    async with session_scope() as session:
        await service.record_message(
            session, occurrence_id=oid, bot_instance_id=bid, component_key="followup", purpose="FOLLOWUP",
            chat_id="123", message_id=12, sent_at=NOW + timedelta(hours=2),
        )
        await service.complete(session, oid, user_id=uid, bot_instance_id=bid, record_progress=progress_writer)
        candidates = await service.cleanup_candidates(session, oid)
        assert {item.message_id for item in candidates} == {11, 12}
        assert await service.record_message_deleted(session, oid, candidates[0].id)
    async with session_scope() as session:
        assert len(await service.cleanup_candidates(session, oid)) == 1
        content = (await session.execute(select(ShareMessage).where(
            ShareMessage.occurrence_id == oid, ShareMessage.purpose == "CONTENT",
        ))).scalar_one()
        assert not await service.record_message_deleted(session, oid, content.id)
        assert content.deleted_at is None


async def test_mismatched_receipt_cannot_replace_original_or_mix_chats():
    _, _, pid, bid = await setup_membership()
    oid, _ = await create(pid, bid)
    values = dict(occurrence_id=oid, bot_instance_id=bid, component_key="content:0", purpose="CONTENT",
                  chat_id="123", message_id=10, sent_at=NOW)
    async with session_scope() as session:
        message = await service.record_message(session, **values)
        again = await service.record_message(session, **values)
        assert again.id == message.id
        with pytest.raises(service.OccurrenceConflictError):
            await service.record_message(session, **{**values, "message_id": 20})
        with pytest.raises(service.OccurrenceAccessError):
            await service.record_message(session, **{**values, "component_key": "action", "chat_id": "456"})


async def test_database_rejects_completion_without_delivery_and_content_deletion():
    _, _, pid, bid = await setup_membership()
    oid, _ = await create(pid, bid)
    with pytest.raises(IntegrityError):
        async with session_scope() as session:
            occurrence = await session.get(ShareOccurrence, oid)
            occurrence.completed_at = NOW
            await session.flush()
    await delivered(oid, bid)
    with pytest.raises(IntegrityError):
        async with session_scope() as session:
            message = (await session.execute(select(ShareMessage).where(
                ShareMessage.occurrence_id == oid, ShareMessage.purpose == "CONTENT",
            ))).scalar_one()
            message.deleted_at = NOW
            await session.flush()
