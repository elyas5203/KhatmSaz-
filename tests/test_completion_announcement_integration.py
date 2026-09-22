"""Real PostgreSQL coverage for delayed, creator-controlled completion messages."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.completion import service as completion_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member():
    creator_id, member_id, khatm_id, participation_id = new_id(), new_id(), new_id(), new_id()
    completed_at = datetime.now(timezone.utc) - timedelta(minutes=6)
    async with session_scope() as session:
        session.add_all(
            [
                User(id=creator_id, display_name="سازنده"),
                User(id=member_id, display_name="عضو"),
                PlatformIdentity(
                    id=new_id(), user_id=creator_id, platform=Platform.TELEGRAM, subject="81001"
                ),
                PlatformIdentity(
                    id=new_id(), user_id=member_id, platform=Platform.BALE, subject="81002"
                ),
                Khatm(
                    id=khatm_id,
                    creator_user_id=creator_id,
                    title="ختم اعلان تست",
                    template_type=KhatmTemplateType.SALAWAT,
                    khatm_type=KhatmTypeEnum.OPEN,
                    status=KhatmStatus.COMPLETED,
                    completed_at=completed_at,
                    completion_announcement_enabled=True,
                ),
                Participation(id=participation_id, khatm_id=khatm_id, user_id=member_id),
            ]
        )

    sent: list[tuple[str, str, str]] = []

    async def notify(platform: str, subject: str, text: str) -> None:
        sent.append((platform, subject, text))

    async with session_scope() as session:
        delivered = await completion_service.deliver_pending(
            session, notify, now=datetime.now(timezone.utc), khatm_id=khatm_id
        )
        assert delivered == 1
        khatm = await session.get(Khatm, khatm_id)
        assert khatm.completion_announced_at is not None
        assert {(platform, subject) for platform, subject, _ in sent} == {
            ("TELEGRAM", "81001"),
            ("BALE", "81002"),
        }
        assert all("ختم اعلان تست" in text and "تعداد همراهان: 1" in text for _, _, text in sent)
        assert await completion_service.deliver_pending(
            session, notify, now=datetime.now(timezone.utc), khatm_id=khatm_id
        ) == 0

    async with session_scope() as session:
        await session.execute(delete(UserSettings).where(UserSettings.user_id.in_([creator_id, member_id])))
        await session.execute(delete(Participation).where(Participation.id == participation_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id.in_([creator_id, member_id])))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_completion_grace_allows_reopen_and_creator_can_disable_message():
    creator_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=creator_id))
        session.add(
            Khatm(
                id=khatm_id,
                creator_user_id=creator_id,
                title="مهلت لغو",
                template_type=KhatmTemplateType.QURAN_PAGE,
                khatm_type=KhatmTypeEnum.COMMITMENT,
                status=KhatmStatus.ACTIVE,
            )
        )
        await session.flush()
        completed = await khatm_service.complete_khatm(session, khatm_id)
        assert completed.status == KhatmStatus.COMPLETED
        assert completed.completed_at is not None

        sent = []

        async def notify(platform: str, subject: str, text: str) -> None:
            sent.append((platform, subject, text))

        assert await completion_service.deliver_pending(
            session, notify, now=completed.completed_at + timedelta(minutes=4), khatm_id=khatm_id
        ) == 0
        reopened = await khatm_service.reopen_after_completion_undo(session, khatm_id)
        assert reopened is not None
        assert reopened.status == KhatmStatus.ACTIVE
        assert reopened.completed_at is None
        updated = await khatm_service.set_completion_announcement(
            session, khatm_id=khatm_id, creator_user_id=creator_id, enabled=False
        )
        assert updated.completion_announcement_enabled is False

        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == creator_id))


