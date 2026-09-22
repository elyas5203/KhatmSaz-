"""Real PostgreSQL coverage for the safe account-deletion boundary."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_account_deletion_blocks_commitments_then_closes_open_membership():
    user_id = new_id()
    creator_id = new_id()
    committed_khatm_id = new_id()
    open_khatm_id = new_id()
    committed_participation_id = new_id()
    open_participation_id = new_id()

    async with session_scope() as session:
        session.add_all([User(id=user_id, display_name="حذف آزمایشی"), User(id=creator_id)])
        session.add(
            UserSettings(
                user_id=user_id,
                contact_phone="09120000000",
                city="تهران",
                province="تهران",
            )
        )
        session.add_all(
            [
                Khatm(
                    id=committed_khatm_id,
                    creator_user_id=creator_id,
                    title="تعهد آزمایشی",
                    template_type=KhatmTemplateType.QURAN_PAGE,
                    khatm_type=KhatmTypeEnum.COMMITMENT,
                    status=KhatmStatus.ACTIVE,
                ),
                Khatm(
                    id=open_khatm_id,
                    creator_user_id=creator_id,
                    title="آزاد آزمایشی",
                    template_type=KhatmTemplateType.SALAWAT,
                    khatm_type=KhatmTypeEnum.OPEN,
                    status=KhatmStatus.ACTIVE,
                ),
            ]
        )
        session.add_all(
            [
                Participation(
                    id=committed_participation_id,
                    khatm_id=committed_khatm_id,
                    user_id=user_id,
                    is_committed=True,
                ),
                Participation(
                    id=open_participation_id,
                    khatm_id=open_khatm_id,
                    user_id=user_id,
                    is_committed=False,
                ),
            ]
        )
        await session.flush()

        with pytest.raises(identity_service.AccountDeletionBlocked) as blocked:
            await identity_service.delete_account(session, user_id)
        assert blocked.value.committed_count == 1
        assert (await session.get(User, user_id)).deleted_at is None

        committed = await session.get(Participation, committed_participation_id)
        committed.status = ParticipationStatus.LEFT
        committed.leave_reason = "TEST_RESOLVED"
        await identity_service.delete_account(session, user_id)

        user = await session.get(User, user_id)
        settings = await session.get(UserSettings, user_id)
        open_participation = await session.get(Participation, open_participation_id)
        assert user.deleted_at is not None
        assert user.display_name is None
        assert open_participation.status == ParticipationStatus.LEFT
        assert open_participation.leave_reason == "ACCOUNT_DELETED"
        assert settings.contact_phone is None
        assert settings.city is None
        assert settings.province is None

        await session.execute(delete(Participation).where(Participation.id.in_([committed_participation_id, open_participation_id])))
        await session.execute(delete(Khatm).where(Khatm.id.in_([committed_khatm_id, open_khatm_id])))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id.in_([user_id, creator_id])))
