"""Real PostgreSQL coverage for creator analytics and invite conversion."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.invitation.models import KhatmInvitation
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.reporting.service import get_khatm_stats


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creator_khatm_stats_include_members_contributions_and_funnel():
    creator_id, member_id = new_id(), new_id()
    khatm_id = new_id()
    participation_id = new_id()
    invitation_ids = [new_id(), new_id(), new_id()]
    async with session_scope() as session:
        session.add_all([User(id=creator_id), User(id=member_id)])
        session.add(
            Khatm(
                id=khatm_id,
                creator_user_id=creator_id,
                title="آمار آزمایشی",
                template_type=KhatmTemplateType.SALAWAT,
                khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE,
            )
        )
        await session.flush()
        session.add(Participation(id=participation_id, khatm_id=khatm_id, user_id=member_id, is_committed=False))
        await session.flush()
        session.add(OpenContribution(id=new_id(), khatm_id=khatm_id, participation_id=participation_id, amount=12.5))
        await session.flush()
        now = datetime.now(timezone.utc)
        session.add_all(
            [
                KhatmInvitation(
                    id=invitation_ids[0], khatm_id=khatm_id, created_by_user_id=creator_id,
                    token_hash="stats-invite-1", expires_at=now + timedelta(days=1),
                    accepted_at=now, accepted_by_user_id=member_id,
                ),
                KhatmInvitation(
                    id=invitation_ids[1], khatm_id=khatm_id, created_by_user_id=creator_id,
                    token_hash="stats-invite-2", expires_at=now + timedelta(days=1),
                ),
                KhatmInvitation(
                    id=invitation_ids[2], khatm_id=khatm_id, created_by_user_id=creator_id,
                    token_hash="stats-invite-3", expires_at=now + timedelta(days=1),
                    accepted_at=now, accepted_by_user_id=member_id,
                ),
            ]
        )
        await session.flush()

        stats = await get_khatm_stats(session, khatm_id)
        assert stats.total_members == 1
        assert stats.active_members == 1
        assert stats.committed_members == 0
        assert stats.contribution_total == 12.5
        assert (stats.invitations_accepted, stats.invitations_issued) == (2, 3)
        assert stats.invitation_conversion_percent == 66.7

        await session.execute(delete(OpenContribution).where(OpenContribution.khatm_id == khatm_id))
        await session.execute(delete(KhatmInvitation).where(KhatmInvitation.khatm_id == khatm_id))
        await session.execute(delete(Participation).where(Participation.khatm_id == khatm_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
