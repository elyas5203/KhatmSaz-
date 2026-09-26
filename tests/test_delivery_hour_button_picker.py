"""Owner request (2026-09-22, "put yourself in a confused user's shoes"
pass): asking someone to type a raw 0-23 hour to pick when their daily
portion should arrive is real friction for anyone unsure about 24-hour
clock notation. Added plain-language time-of-day buttons
(`keyboards.py::delivery_hour_keyboard`) as an alternative to typing, for
both places that ask this: the join-time delivery-hour question
(`start.py`) and the open-Quran-reading setup wizard (`portions.py`).
Typing a precise hour must still work as a fallback."""

from types import SimpleNamespace

import pytest
from sqlalchemy import delete

from khatmsaz.bot.handlers.start import AskDeliveryHour
from khatmsaz.bot.handlers.join_flow import receive_delivery_hour_button
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401 — registers FK target table
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation import repository as participation_repository


class FakeState:
    def __init__(self, data):
        self.data = data
        self.state = AskDeliveryHour.entering_hour

    async def get_data(self):
        return dict(self.data)

    async def clear(self):
        self.data = {}
        self.state = None


class FakeMessage:
    def __init__(self):
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))

    async def edit_reply_markup(self, **kwargs):
        pass


class FakeCallback:
    def __init__(self, data):
        self.data = data
        self.message = FakeMessage()

    async def answer(self, *a, **k):
        pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tapping_a_time_of_day_button_saves_the_hour_without_typing():
    creator_id, member_id, khatm_id = new_id(), new_id(), new_id()
    async with session_scope() as session:
        session.add_all([User(id=creator_id), User(id=member_id)])
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="تست دکمهٔ ساعت",
            template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE,
        )
        session.add(khatm)
        await session.flush()
        participation = await participation_repository.create(session, khatm_id, member_id)
        participation_id = participation.id

    state = FakeState({"lang": "fa", "delivery_hour_participation_id": str(participation_id)})
    callback = FakeCallback("join_hour:18")  # 🌇 غروب
    await receive_delivery_hour_button(callback, state)

    assert state.state is None  # wizard finished — no more typing needed
    async with session_scope() as session:
        preference = await notification_service.get_preference(session, participation_id)
        assert preference is not None
        assert preference.reminder_hour == 18
        assert preference.enabled is True

        from khatmsaz.modules.notification.models import NotificationPreference
        await session.execute(delete(NotificationPreference).where(NotificationPreference.participation_id == participation_id))
        await session.execute(delete(type(participation)).where(type(participation).khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
