"""Owner request (2026-09-21): every freshly-committed member should be
asked what hour their daily portion should be delivered, right at join
time, instead of silently defaulting to hour 9 unless they discover the
hidden `/reminder` command themselves. See
`bot/handlers/start.py::AskDeliveryHour` and `resume_join_after_registration`.

Owner request (2026-09-22): extended to ALL khatm types (salawat, dua,
laan, ...), not only Quran-page khatms."""

from types import SimpleNamespace

import pytest
from sqlalchemy import delete

from khatmsaz.bot.handlers.start import AskDeliveryHour, resume_join_after_registration
from khatmsaz.bot.handlers.join_flow import receive_delivery_hour
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, User
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
import khatmsaz.modules.khatm_category.models  # noqa: F401 — registers FK target table
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation import repository as participation_repository


class FakeState:
    def __init__(self):
        self.data = {}
        self.state = None

    async def get_data(self):
        return self.data

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value

    async def clear(self):
        self.data = {}
        self.state = None


class FakeMessage:
    def __init__(self, chat_id: int):
        self.chat = SimpleNamespace(id=chat_id)
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM)
        self.from_user = SimpleNamespace(full_name="کاربر تست")
        self.text = None
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it():
    creator_id, member_id, khatm_id = new_id(), new_id(), new_id()
    # A fresh chat_id per run (rather than a fixed constant) so
    # `resolve_or_provision_user` can't return a persistent identity left
    # over from a previous, possibly-failed run of this same test.
    chat_id = 9_800_000_000 + (int.from_bytes(bytes.fromhex(str(member_id).replace("-", ""))[:4], "big") % 1_000_000)

    async with session_scope() as session:
        session.add(User(id=creator_id))
        await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
        member_identity = await identity_service.find_by_platform(session, Platform.TELEGRAM, str(chat_id))
        member_id = member_identity.id
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="قرآن تست پرسش ساعت",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, quran_edition_id="madina-hafs",
        )
        session.add(khatm)
        await session.flush()
        await allocation_service.generate_quran_page_plan(session, khatm_id, total_pages=10, pages_per_portion=2)
        token = await invitation_service.create_invitation(session, khatm_id, creator_id)

    # `resume_join_after_registration` takes an already-open session (as it
    # does in real handlers), but `receive_delivery_hour` — a real message
    # handler — opens its own via `session_scope()` internally, so setup
    # must be committed first or its FK lookups see nothing.
    state = FakeState()
    message = FakeMessage(chat_id)
    async with session_scope() as session:
        await resume_join_after_registration(
            message, session, member_id, token, state=state, consent_accepted=True,
        )

    # Join message was sent, and — since this is a fresh commitment with
    # a real first portion assigned — the bot should now be asking for
    # a delivery hour instead of silently defaulting to 9.
    assert len(message.answers) == 2
    assert state.state == AskDeliveryHour.entering_hour

    async with session_scope() as session:
        participation = await participation_repository.get_active(session, khatm_id, member_id)
        participation_id = participation.id
        assert await notification_service.get_preference(session, participation_id) is None

    # Reject an invalid hour first.
    message.text = "99"
    await receive_delivery_hour(message, state)
    assert state.state == AskDeliveryHour.entering_hour
    async with session_scope() as session:
        assert await notification_service.get_preference(session, participation_id) is None

    # Then accept a valid one.
    message.text = "14"
    await receive_delivery_hour(message, state)
    assert state.state is None
    async with session_scope() as session:
        preference = await notification_service.get_preference(session, participation_id)
        assert preference is not None
        assert preference.reminder_hour == 14

        from khatmsaz.modules.notification.models import NotificationPreference
        from khatmsaz.modules.allocation.models import KhatmAllocationPlan, KhatmPortion
        from khatmsaz.modules.settings.models import UserSettings
        from sqlalchemy import or_
        from khatmsaz.modules.invitation.models import KhatmInvitation
        # Reusing a fixed chat_id means `resolve_or_provision_user` returns
        # the SAME persistent user across repeated test runs — clean up any
        # invitation referencing this user at all, not just this run's own
        # khatm_id, so a prior failed run's leftovers can't block this one.
        await session.execute(delete(KhatmInvitation).where(
            or_(
                KhatmInvitation.khatm_id == khatm_id,
                KhatmInvitation.created_by_user_id.in_([creator_id, member_id]),
                KhatmInvitation.accepted_by_user_id.in_([creator_id, member_id]),
            )
        ))
        await session.execute(delete(NotificationPreference).where(NotificationPreference.participation_id == participation_id))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.khatm_id == khatm_id))
        await session.execute(delete(type(participation)).where(type(participation).khatm_id == khatm_id))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([creator_id, member_id])))
        from khatmsaz.modules.identity.models import PlatformIdentity
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == member_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fresh_committed_salawat_join_asks_commitment_mode():
    """R11 supersedes the old bare delivery-hour question for repetitions."""
    creator_id, khatm_id = new_id(), new_id()
    chat_id = 9_900_000_000 + (int.from_bytes(new_id().bytes[:4], "big") % 1_000_000)

    async with session_scope() as session:
        session.add(User(id=creator_id))
        await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
        member_identity = await identity_service.find_by_platform(session, Platform.TELEGRAM, str(chat_id))
        member_id = member_identity.id
        from khatmsaz.modules.khatm.models import KhatmTemplateType as KTT
        khatm = Khatm(
            id=khatm_id, creator_user_id=creator_id, title="صلوات تست پرسش ساعت",
            template_type=KTT.SALAWAT, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, repetition_target=100,
        )
        session.add(khatm)
        await session.flush()
        token = await invitation_service.create_invitation(session, khatm_id, creator_id)

    state = FakeState()
    message = FakeMessage(chat_id)
    async with session_scope() as session:
        await resume_join_after_registration(
            message, session, member_id, token, state=state, consent_accepted=True,
        )

    assert len(message.answers) == 3, "join success + commitment explanation + mode picker expected"
    assert "چطور می‌خوای بخونی" in message.answers[-1][0]
    assert state.state is None

    async with session_scope() as session:
        participation = await participation_repository.get_active(session, khatm_id, member_id)
        participation_id = participation.id

    async with session_scope() as session:
        preference = await notification_service.get_preference(session, participation_id)
        assert preference is None

        from khatmsaz.modules.notification.models import NotificationPreference
        from khatmsaz.modules.allocation.models import KhatmAllocationPlan, KhatmPortion
        from khatmsaz.modules.settings.models import UserSettings
        from khatmsaz.modules.invitation.models import KhatmInvitation
        from sqlalchemy import or_
        await session.execute(delete(KhatmInvitation).where(
            or_(
                KhatmInvitation.khatm_id == khatm_id,
                KhatmInvitation.created_by_user_id == creator_id,
            )
        ))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.khatm_id == khatm_id))
        await session.execute(delete(type(participation)).where(type(participation).khatm_id == khatm_id))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([creator_id, member_id])))
        from khatmsaz.modules.identity.models import PlatformIdentity
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == member_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
