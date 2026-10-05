"""Real PostgreSQL transactions; messenger calls are isolated fakes."""
import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select, func

from khatmsaz.core import model_registry  # noqa: F401
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.bot_registry.models import BotInstance
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.allocation.models import KhatmAllocationPlan, KhatmPortion
from khatmsaz.modules.open_contribution.models import OpenContribution, OpenReservation
from khatmsaz.modules.open_contribution import service as reservations
from khatmsaz.modules.share_occurrence import service, repository, delivery
from khatmsaz.modules.share_occurrence.models import ShareOccurrence
from khatmsaz.modules.notification import service as notification
from khatmsaz.bot import occurrence_adapter as adapter

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]
NOW = datetime(2026, 10, 4, 9, tzinfo=timezone.utc)


async def membership(*, quran=True, fixed=False, opened=False):
    uid, kid, pid, bid = [new_id() for _ in range(4)]
    async with session_scope() as session:
        session.add(User(id=uid, display_name="تست بازطراحی"))
        session.add(BotInstance(id=bid, platform="TELEGRAM", bot_role="MEMBER", display_name="test", is_active=True))
        await session.flush()
        session.add(Khatm(id=kid, creator_user_id=uid, title="تست", template_type="QURAN_PAGE" if quran else "SALAWAT",
            khatm_type="OPEN" if opened else "COMMITMENT", status="ACTIVE", repetition_target=604 if quran else 100,
            commitment_policy="FIXED_DAILY" if fixed else "MEMBER_CHOICE", daily_commitment_amount=5 if fixed else None,
            daily_deadline_hour=18, quran_edition_id="madani_604"))
        await session.flush()
        session.add(Participation(id=pid, khatm_id=kid, user_id=uid, joined_via_bot_instance_id=bid,
            is_committed=not opened, open_reading_pages_per_day=3 if quran else None,
            commitment_mode=None if quran else "REGULAR", commitment_per_occurrence=3,
            schedule_freq="DAILY", schedule_hour=9, schedule_anchor=0))
        if quran and not opened:
            session.add(KhatmAllocationPlan(id=new_id(), khatm_id=kid, unit_kind="POSITIONAL", total_portions=3,
                allocation_strategy="ROTATING", positional_boundaries=[[1,3],[4,5],[6,604]]))
        await session.flush()
        await notification.set_reminder_preference(session, pid, reminder_hour=9, enabled=True)
    return uid, kid, pid, bid


def fake_messenger(monkeypatch, fail_action=False):
    calls = []
    async def send(**kwargs):
        if fail_action and "reply_markup" in kwargs:
            raise RuntimeError("simulated API failure")
        calls.append(kwargs)
        return SimpleNamespace(message_id=len(calls))
    bot = SimpleNamespace(send_message=send, send_photo=send, send_audio=send, forward_message=send,
        delete_message=AsyncMock(), khatmsaz_platform=SimpleNamespace(value="TELEGRAM"))
    monkeypatch.setattr(adapter, "route", AsyncMock(return_value=(bot, 123)))
    monkeypatch.setattr(adapter.content, "resolve_current_quran_delivery", AsyncMock(return_value={
        "image": [SimpleNamespace(asset_ref="https://example.test/page.jpg")], "audio": [], "text": [],
    }))
    return bot, calls


@pytest.mark.parametrize("fixed,amount", [(False,3),(True,5)])
async def test_first_quran_share_exact_amount_and_independent_next_day(monkeypatch, fixed, amount):
    fake_messenger(monkeypatch)
    uid, kid, pid, bid = await membership(fixed=fixed)
    async with session_scope() as session:
        first = await delivery.prepare(session, pid, now=NOW)
        assert first.amount == amount
        assert first.content_spec["ranges"] == [[1,amount]]
        assert await delivery.deliver(session, first, now=NOW)
        first_id = first.id
    async with session_scope() as session:
        part = await session.get(Participation, pid)
        part.open_reading_pages_per_day = 7
    async with session_scope() as session:
        today = await delivery.prepare(session, pid, now=NOW+timedelta(days=3))
        assert today.amount == (5 if fixed else 7)
        assert today.content_spec["ranges"][0][0] == amount+1
        await delivery.deliver(session, today, now=NOW+timedelta(days=3))
        assert len(await repository.list_outstanding(session,pid)) == 2
        assert (await repository.get(session,first_id)).amount == amount
        assert await session.scalar(select(func.count()).select_from(ShareOccurrence).where(ShareOccurrence.participation_id==pid)) == 2
    async def finish():
        async with session_scope() as session:
            from khatmsaz.modules.khatm import service as khatms
            await khatms.get_khatm_for_update(session,kid)
            return (await service.complete(session,first_id,user_id=uid,bot_instance_id=bid,record_progress=delivery.record_progress))[1]
    assert sorted(await asyncio.gather(finish(),finish())) == [False,True]
    async with session_scope() as session:
        assert len(await repository.list_outstanding(session,pid)) == 1
        assert await session.scalar(select(func.count()).select_from(OpenContribution).where(OpenContribution.participation_id==pid)) == 1
        portions = list((await session.execute(select(KhatmPortion).where(KhatmPortion.participation_id==pid).order_by(KhatmPortion.sequence))).scalars())
        assert [p.status for p in portions] == ["COMPLETED","ASSIGNED"]


async def test_partial_send_keeps_cursor_and_reuses_content_receipt(monkeypatch):
    _, calls = fake_messenger(monkeypatch,fail_action=True)
    _, _, pid, _ = await membership(opened=True)
    async with session_scope() as session:
        occurrence = await delivery.prepare(session,pid,now=NOW)
        with pytest.raises(RuntimeError):
            await delivery.deliver(session,occurrence,now=NOW)
        oid = occurrence.id
        assert (await session.get(Participation,pid)).open_reading_next_page == 1
    _, retried = fake_messenger(monkeypatch)
    async with session_scope() as session:
        occurrence = await delivery.prepare(session,pid,now=NOW)
        assert occurrence.id == oid
        await delivery.deliver(session,occurrence,now=NOW)
        assert (await session.get(Participation,pid)).open_reading_next_page == 4
        assert not await delivery.deliver(session,occurrence,now=NOW)
    assert len(calls) == 1
    assert len(retried) == 1 and "reply_markup" in retried[0]


async def test_two_reminders_once_and_cleanup_preserves_content(monkeypatch):
    bot, calls = fake_messenger(monkeypatch)
    uid,kid,pid,bid = await membership()
    async with session_scope() as session:
        occurrence = await delivery.prepare(session,pid,now=NOW)
        await delivery.deliver(session,occurrence,now=NOW)
        await delivery.remind(session,pid,now=NOW+timedelta(hours=2))
        await delivery.remind(session,pid,now=NOW+timedelta(hours=2))
        await delivery.remind(session,pid,now=occurrence.deadline_at-timedelta(minutes=30))
        assert [r.purpose for r in await repository.list_messages(session,occurrence.id)] == ["CONTENT","ACTION","FOLLOWUP","DEADLINE"]
        await service.complete(session,occurrence.id,user_id=uid,bot_instance_id=bid,record_progress=delivery.record_progress)
        await adapter.cleanup(session,await session.get(Participation,pid),occurrence)
        assert bot.delete_message.await_count == 3
        assert len(calls) == 4


async def test_reservation_race_capacity_owner_and_expiry():
    uid,kid,pid,bid = await membership(quran=False,opened=True)
    async def reserve():
        async with session_scope() as session:
            r,made = await reservations.create_reservation(session,kid,pid,80,100)
            return r.id,made
    first,second = await asyncio.gather(reserve(),reserve())
    assert first[0]==second[0] and sum([first[1],second[1]])==1
    async with session_scope() as session:
        with pytest.raises(ValueError):
            await reservations.complete_reservation(session,first[0],100,user_id=new_id(),bot_instance_id=bid)
        r=await session.get(OpenReservation,first[0])
        r.expires_at=datetime.now(timezone.utc)-timedelta(seconds=1)
    async with session_scope() as session:
        with pytest.raises(ValueError):
            await reservations.complete_reservation(session,first[0],100,user_id=uid,bot_instance_id=bid)
        assert await session.scalar(select(func.count()).select_from(OpenContribution).where(OpenContribution.participation_id==pid))==0


@pytest.mark.parametrize("opened", [True,False])
async def test_numeric_quran_has_exact_pages_and_only_open_expires(monkeypatch, opened):
    fake_messenger(monkeypatch)
    uid,kid,pid,bid = await membership(opened=opened)
    async with session_scope() as session:
        occurrence = await delivery.prepare_numeric(session,pid,10,user_id=uid,bot_instance_id=bid,now=NOW)
        assert occurrence.amount == 10 and occurrence.content_spec["ranges"] == [[1,10]]
        assert (occurrence.reservation_id is not None) == opened
        await delivery.deliver(session,occurrence,now=NOW)
        oid=occurrence.id
        if opened:
            reservation=await session.get(OpenReservation,occurrence.reservation_id)
            assert timedelta(hours=167,minutes=59) < reservation.expires_at-reservation.created_at <= timedelta(hours=168,seconds=1)
            with pytest.raises(service.OccurrenceAccessError):
                await service.complete(session,oid,user_id=uid,bot_instance_id=bid,record_progress=delivery.record_progress,when=reservation.expires_at)
        else:
            _,changed=await service.complete(session,oid,user_id=uid,bot_instance_id=bid,
                record_progress=delivery.record_progress,when=NOW+timedelta(days=30))
            assert changed
    async with session_scope() as session:
        assert await delivery.prepare(session,pid,now=NOW+timedelta(days=1)) is None


async def test_quran_weekdays_and_changed_amount_leave_issued_payload_untouched(monkeypatch):
    fake_messenger(monkeypatch)
    _,_,pid,_=await membership()
    async with session_scope() as session:
        part=await session.get(Participation,pid)
        part.commitment_mode="REGULAR"
        part.schedule_freq="WEEKLY"
        part.schedule_weekdays="0,2,6"
    saturday=datetime(2026,10,3,9,tzinfo=timezone.utc)
    async with session_scope() as session:
        occurrence=await delivery.prepare(session,pid,now=saturday)
        await delivery.deliver(session,occurrence,now=saturday)
        assert await delivery.prepare(session,pid,now=saturday+timedelta(days=1)) is None
        monday=await delivery.prepare(session,pid,now=saturday+timedelta(days=2))
        assert monday is not None


async def test_goal_stops_new_shares_but_old_shares_complete_as_surplus(monkeypatch):
    fake_messenger(monkeypatch)
    uid,kid,pid,bid=await membership(opened=True)
    async with session_scope() as session:
        khatm=await session.get(Khatm,kid)
        khatm.repetition_target=8
        first=await delivery.prepare(session,pid,now=NOW)
        await delivery.deliver(session,first,now=NOW)
        second=await delivery.prepare(session,pid,now=NOW+timedelta(days=1))
        await delivery.deliver(session,second,now=NOW+timedelta(days=1))
        session.add(OpenContribution(id=new_id(),khatm_id=kid,participation_id=pid,amount=8,counted_amount=8,surplus_amount=0))
        await session.flush()
        assert await delivery.prepare(session,pid,now=NOW+timedelta(days=2)) is None
        _,changed=await service.complete(session,first.id,user_id=uid,bot_instance_id=bid,record_progress=delivery.record_progress)
        assert changed
        logs=list((await session.execute(select(OpenContribution).where(OpenContribution.participation_id==pid))).scalars())
        assert sum(log.surplus_amount for log in logs)==3
        assert len(await repository.list_outstanding(session,pid))==1


async def test_legacy_debt_has_separate_completion_and_new_share_cannot_be_completed_through_it(monkeypatch):
    fake_messenger(monkeypatch)
    uid,kid,pid,bid=await membership()
    from khatmsaz.modules.allocation import service as allocation
    async with session_scope() as session:
        old=(await allocation.allocate_page_amount(session,kid,pid,2))[0]
        new=await delivery.prepare(session,pid,now=NOW)
        await delivery.deliver(session,new,now=NOW)
        assert [p.id for p in await repository.list_legacy_portions(session,pid)]==[old.id]
        assert await service.complete_legacy_portion(session,old.id,user_id=uid,bot_instance_id=bid)
        assert not await service.complete_legacy_portion(session,old.id,user_id=uid,bot_instance_id=bid)
        from uuid import UUID
        with pytest.raises(ValueError):
            await service.complete_legacy_portion(session,UUID(new.content_spec["portion_ids"][0]),user_id=uid,bot_instance_id=bid)
        assert (await repository.get(session,new.id)).completed_at is None


async def test_reservation_warning_at_sixth_local_noon_once_then_expiry(monkeypatch):
    fake_messenger(monkeypatch)
    from zoneinfo import ZoneInfo
    from khatmsaz.modules.reminder_engine import service as reminders
    uid,_,pid,bid=await membership(opened=True)
    async with session_scope() as session:
        occurrence=await delivery.prepare_numeric(session,pid,10,user_id=uid,bot_instance_id=bid)
        await delivery.deliver(session,occurrence)
        reservation=await session.get(OpenReservation,occurrence.reservation_id)
        reservation.created_at=datetime(2026,10,5,18,tzinfo=ZoneInfo("Asia/Tehran"))
        reservation.expires_at=reservation.created_at+timedelta(days=7)
        due=datetime(2026,10,11,12,tzinfo=ZoneInfo("Asia/Tehran"))
        await reminders.process_open_reservations(session,None,reservation_id=reservation.id,now=due-timedelta(seconds=1))
        assert reservation.reminded_at is None
        await reminders.process_open_reservations(session,None,reservation_id=reservation.id,now=due)
        await reminders.process_open_reservations(session,None,reservation_id=reservation.id,now=due+timedelta(minutes=1))
        messages=await repository.list_messages(session,occurrence.id)
        assert sum(r.component_key=="RESERVATION_WARNING" for r in messages)==1
        await reminders.process_open_reservations(session,None,reservation_id=reservation.id,now=reservation.expires_at)
        assert reservation.status=="EXPIRED"


async def test_left_member_can_still_find_delivered_debt(monkeypatch):
    fake_messenger(monkeypatch)
    uid, _, pid, bid = await membership()
    from khatmsaz.modules.participation import service as memberships
    async with session_scope() as session:
        share = await delivery.prepare(session, pid, now=NOW)
        await delivery.deliver(session, share, now=NOW)
        part = await session.get(Participation, pid)
        part.status = "LEFT"
        await session.flush()
        assert not await memberships.list_my_active(session, uid)
        assert [p.id for p in await memberships.list_my_active(session, uid, include_owed=True)] == [pid]
        await service.complete(session, share.id, user_id=uid, bot_instance_id=bid, record_progress=delivery.record_progress)
        assert not await memberships.list_my_active(session, uid, include_owed=True)


async def test_audio_only_quran_and_bot_language_are_delivered(monkeypatch):
    bot, calls = fake_messenger(monkeypatch)
    bot.khatmsaz_language = "en"
    monkeypatch.setattr(adapter.content, "resolve_current_quran_delivery", AsyncMock(return_value={
        "image": [], "audio": [SimpleNamespace(asset_ref="https://example.test/recitation.mp3")], "text": [],
    }))
    _, _, pid, _ = await membership()
    async with session_scope() as session:
        share = await delivery.prepare(session, pid, now=NOW)
        assert await delivery.deliver(session, share, now=NOW)
        assert share.content_spec["language"] == "en"
        assert calls[0]["audio"] == "https://example.test/recitation.mp3"
        assert calls[-1]["reply_markup"].inline_keyboard[0][0].callback_data == f"share_done:{share.id}"


async def test_variable_pages_complete_original_plan_only_after_full_coverage(monkeypatch):
    fake_messenger(monkeypatch)
    uid, kid, pid, bid = await membership()
    from khatmsaz.modules.allocation import service as allocation
    async with session_scope() as session:
        khatm = await session.get(Khatm, kid)
        khatm.repetition_target = None
        plan = await session.scalar(select(KhatmAllocationPlan).where(KhatmAllocationPlan.khatm_id == kid))
        plan.positional_boundaries = [[1, 3], [4, 5], [6, 10]]
        part = await session.get(Participation, pid)
        part.open_reading_pages_per_day = 5
        first = await delivery.prepare(session, pid, now=NOW)
        await delivery.deliver(session, first, now=NOW)
        second = await delivery.prepare(session, pid, now=NOW+timedelta(days=1))
        await delivery.deliver(session, second, now=NOW+timedelta(days=1))
        extra = await delivery.prepare(session, pid, now=NOW+timedelta(days=2))
        await delivery.deliver(session, extra, now=NOW+timedelta(days=2))
        await service.complete(session, first.id, user_id=uid, bot_instance_id=bid, record_progress=delivery.record_progress)
        assert await allocation.progress(session, kid) == (2, 3)
        assert khatm.status == "ACTIVE"
        await service.complete(session, second.id, user_id=uid, bot_instance_id=bid, record_progress=delivery.record_progress)
        assert await allocation.progress(session, kid) == (3, 3)
        assert khatm.status == "COMPLETED"
        assert await delivery.prepare(session, pid, now=NOW+timedelta(days=3)) is None
        await service.complete(session, extra.id, user_id=uid, bot_instance_id=bid, record_progress=delivery.record_progress)
        logs = list((await session.execute(select(OpenContribution).where(OpenContribution.participation_id == pid))).scalars())
        assert sum(row.surplus_amount for row in logs) == 5


async def test_partial_outage_retry_retains_pages_but_uses_current_day_deadline(monkeypatch):
    fake_messenger(monkeypatch, fail_action=True)
    _, _, pid, _ = await membership()
    async with session_scope() as session:
        first = await delivery.prepare(session, pid, now=NOW)
        with pytest.raises(RuntimeError):
            await delivery.deliver(session, first, now=NOW)
        share_id, ranges = first.id, first.content_spec["ranges"]
    _, calls = fake_messenger(monkeypatch)
    async with session_scope() as session:
        later = NOW + timedelta(days=3)
        retry = await delivery.prepare(session, pid, now=later)
        assert retry.id == share_id
        assert retry.content_spec["ranges"] == ranges
        assert retry.deadline_at.date() == later.date()
        assert await delivery.deliver(session, retry, now=later)
        assert len(calls) == 1  # the previously delivered image is retained
        assert await delivery.prepare(session, pid, now=later) is None
        assert await session.scalar(select(func.count()).select_from(ShareOccurrence).where(ShareOccurrence.participation_id == pid)) == 1


@pytest.mark.parametrize("family", ["salawat", "dua", "ziyarat", "laan"])
@pytest.mark.parametrize("platform_name", ["TELEGRAM", "BALE"])
@pytest.mark.parametrize("lang", ["fa", "ar", "en"])
@pytest.mark.parametrize("mode", ["regular_commitment", "numeric_commitment", "regular_open", "numeric_open", "fixed"])
async def test_devotional_family_route_language_and_exact_completion(monkeypatch, family, platform_name, lang, mode):
    from khatmsaz.modules.identity.models import Platform, PlatformIdentity
    from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup
    from khatmsaz.modules.content.models import DevotionalAsset
    from khatmsaz.modules.content import service as content
    from khatmsaz.bot import notify_adapter
    uid, kid, pid, bid = await membership(quran=False, opened=mode.endswith("open"), fixed=mode == "fixed")
    platform = Platform(platform_name)
    calls = []
    async def send(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(message_id=len(calls))
    bot = SimpleNamespace(khatmsaz_platform=platform, khatmsaz_role="MEMBER", khatmsaz_language=lang,
        send_message=send, send_photo=send, send_audio=send, send_document=send)
    registry = SimpleNamespace(get_by_instance_id=lambda value: bot if value == bid else None,
                               get_creator_bot=lambda *_: None)
    monkeypatch.setattr(adapter, "get_registry", lambda: registry)
    monkeypatch.setattr("khatmsaz.core.bot_registry.get_registry", lambda: registry)
    async with session_scope() as session:
        record = await session.get(BotInstance, bid)
        record.platform = platform_name
        session.add(PlatformIdentity(id=new_id(), user_id=uid, platform=platform, subject=str(new_id().int % (2**51))))
        khatm = await session.get(Khatm, kid)
        if family == "salawat":
            asset = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == content.SALAWAT_SLUG))
            if asset is None:
                asset = DevotionalAsset(id=new_id(), slug=content.SALAWAT_SLUG, content_type="DUA", title="صلوات", text_body=content.SALAWAT_TEXT)
                session.add(asset)
            asset.enabled = True
            asset.image_ref = None
            asset.audio_ref = None
        else:
            category = KhatmCategory(id=new_id(), group=KhatmCategoryGroup.LAAN if family == "laan" else KhatmCategoryGroup.DUA,
                title="زیارت آزمایشی" if family == "ziyarat" else "متن آزمایشی", body_text="متن قرائت آزمایشی")
            session.add(category)
            await session.flush()
            khatm.content_category_id = category.id
        await session.flush()
        if mode.startswith("numeric"):
            share = await delivery.prepare_numeric(session, pid, 3, user_id=uid, bot_instance_id=bid, now=NOW)
        else:
            share = await delivery.prepare(session, pid, now=NOW)
        assert await delivery.deliver(session, share, now=NOW)
        assert share.content_spec["family"] == family
        assert share.content_spec["language"] == lang
        assert len(calls) >= 2
        assert calls[-1]["reply_markup"].inline_keyboard[0][0].callback_data == f"share_done:{share.id}"
        assert all(call["chat_id"] == calls[0]["chat_id"] for call in calls)
        _, changed = await service.complete(session, share.id, user_id=uid, bot_instance_id=bid, record_progress=delivery.record_progress)
        assert changed
        assert await session.scalar(select(func.sum(OpenContribution.amount)).where(OpenContribution.participation_id == pid)) == (5 if mode == "fixed" else 3)
        assert bool(share.reservation_id) == (mode == "numeric_open")


async def test_completed_control_cleanup_retries_after_api_failure(monkeypatch):
    bot, _ = fake_messenger(monkeypatch)
    uid, _, pid, bid = await membership()
    from khatmsaz.modules.reminder_engine import service as reminders
    async with session_scope() as session:
        share = await delivery.prepare(session, pid, now=NOW)
        await delivery.deliver(session, share, now=NOW)
        await service.complete(session, share.id, user_id=uid, bot_instance_id=bid, record_progress=delivery.record_progress)
        oid = share.id
    # Limit this scanner test to its own persisted occurrence.
    monkeypatch.setattr(repository, "pending_cleanup_ids", AsyncMock(return_value=[oid]))
    bot.delete_message = AsyncMock(side_effect=RuntimeError("temporary API failure"))
    await reminders.cleanup_completed_shares()
    async with session_scope() as session:
        assert len(await service.cleanup_candidates(session, oid)) == 1
    bot.delete_message = AsyncMock()
    await reminders.cleanup_completed_shares()
    async with session_scope() as session:
        assert not await service.cleanup_candidates(session, oid)
        content_receipts = [r for r in await repository.list_messages(session, oid) if r.purpose == "CONTENT"]
        assert content_receipts and all(r.deleted_at is None for r in content_receipts)
