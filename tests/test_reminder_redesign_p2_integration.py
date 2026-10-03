"""Run on a migrated, disposable PostgreSQL database (RUN_INTEGRATION_TESTS=1)."""

from datetime import datetime, timezone

import pytest

from khatmsaz.core import model_registry  # noqa: F401
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.notification import service as notification_service


@pytest.mark.integration
@pytest.mark.asyncio
async def test_schedule_clock_persists_in_both_directions_and_only_selected_membership():
    uid, kid, other_kid, pid, other_pid = [new_id() for _ in range(5)]
    delivered = datetime(2026, 10, 2, 9, tzinfo=timezone.utc)
    async with session_scope() as session:
        session.add(User(id=uid, display_name="عضو آزمایشی"))
        await session.flush()
        for ident in (kid, other_kid):
            session.add(Khatm(id=ident, creator_user_id=uid, title="تست ساعت", template_type=KhatmTemplateType.SALAWAT))
        await session.flush()
        session.add_all([
            Participation(id=pid, khatm_id=kid, user_id=uid),
            Participation(id=other_pid, khatm_id=other_kid, user_id=uid),
        ])
        await session.flush()
        for ident in (pid, other_pid):
            await participation_service.set_commitment_schedule(
                session, ident, freq="WEEKLY", hour=9, minute=15,
                times_per_period=3, weekdays="0,2,6",
            )
        participation = await participation_service.get_by_id(session, pid)
        participation.schedule_last_sent_at = delivered

    # A separate session proves persistence rather than only an ORM identity-map update.
    async with session_scope() as session:
        await notification_service.set_reminder_preference(
            session, pid, reminder_hour=16, reminder_minute=35,
        )

    async with session_scope() as session:
        participation = await participation_service.get_by_id(session, pid)
        other = await participation_service.get_by_id(session, other_pid)
        preference = await notification_service.get_preference(session, pid)
        assert await notification_service.get_reminder_time(session, participation) == (16, 35)
        assert (preference.reminder_hour, preference.reminder_minute) == (16, 35)
        assert await notification_service.get_reminder_time(session, other) == (9, 15)
        assert participation.schedule_last_sent_at == delivered
        assert participation.schedule_weekdays == "0,2,6"
        assert participation.commitment_per_occurrence == 3
        await participation_service.set_commitment_schedule(
            session, pid, freq="DAILY", hour=6, minute=25, times_per_period=2,
        )

    async with session_scope() as session:
        participation = await participation_service.get_by_id(session, pid)
        preference = await notification_service.get_preference(session, pid)
        assert await notification_service.get_reminder_time(session, participation) == (6, 25)
        assert (preference.reminder_hour, preference.reminder_minute) == (6, 25)
        assert participation.schedule_weekdays is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clock_changes_roll_back_with_caller_transaction():
    uid, kid, pid = [new_id() for _ in range(3)]
    async with session_scope() as session:
        session.add(User(id=uid, display_name="تست تراکنش"))
        await session.flush()
        session.add(Khatm(id=kid, creator_user_id=uid, title="تراکنش", template_type=KhatmTemplateType.SALAWAT))
        await session.flush()
        session.add(Participation(id=pid, khatm_id=kid, user_id=uid))
        await session.flush()
        await participation_service.set_commitment_schedule(
            session, pid, freq="DAILY", hour=9, minute=0, times_per_period=1,
        )
    with pytest.raises(RuntimeError, match="rollback"):
        async with session_scope() as session:
            await notification_service.set_reminder_preference(session, pid, reminder_hour=20, reminder_minute=10)
            raise RuntimeError("rollback")
    async with session_scope() as session:
        participation = await participation_service.get_by_id(session, pid)
        preference = await notification_service.get_preference(session, pid)
        assert await notification_service.get_reminder_time(session, participation) == (9, 0)
        assert (preference.reminder_hour, preference.reminder_minute) == (9, 0)
