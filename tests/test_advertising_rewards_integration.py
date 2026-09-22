from datetime import datetime, timezone

import pytest
from sqlalchemy import delete, select

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.advertising import service as advertising_service
from khatmsaz.modules.advertising.models import AdvertisingRewardRate
from khatmsaz.modules.allocation.models import KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.wallet.models import Wallet, WalletTransaction
from khatmsaz.modules.wallet.service import get_balances
from khatmsaz.modules.open_contribution.models import OpenContribution


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ad_reward_requires_opt_in_and_is_idempotent():
    user_id, open_user_id, khatm_id, participation_id, open_participation_id, plan_id, portion_id, rate_id = [new_id() for _ in range(8)]
    async with session_scope() as session:
        session.add_all([User(id=user_id), User(id=open_user_id)])
        session.add(Khatm(
            id=khatm_id, creator_user_id=user_id, title="تبلیغات تستی",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            status=KhatmStatus.ACTIVE, advertising_enabled=True,
        ))
        await session.flush()
        session.add(Participation(
            id=participation_id, khatm_id=khatm_id, user_id=user_id,
            status=ParticipationStatus.ACTIVE,
        ))
        session.add(Participation(
            id=open_participation_id, khatm_id=khatm_id, user_id=open_user_id,
            status=ParticipationStatus.ACTIVE,
        ))
        session.add(KhatmAllocationPlan(
            id=plan_id, khatm_id=khatm_id, unit_kind=PortionUnitKind.POSITIONAL, total_portions=1,
        ))
        await session.flush()
        session.add(KhatmPortion(
            id=portion_id, plan_id=plan_id, khatm_id=khatm_id, sequence=1,
            unit_kind=PortionUnitKind.POSITIONAL, unit_start=1, unit_end=2,
            status=PortionStatus.COMPLETED, participation_id=participation_id,
        ))
        session.add(AdvertisingRewardRate(id=rate_id, amount_toman=100, effective_from=datetime.now(timezone.utc)))
        await session.flush()

        assert await advertising_service.accrue_first_completed_action(session, participation_id) is True
        assert await advertising_service.accrue_first_completed_action(session, participation_id) is False
        assert await get_balances(session, user_id) == (0, 100)
        txs = await session.execute(
            select(WalletTransaction).where(WalletTransaction.ref == f"ad-reward:first-action:{participation_id}")
        )
        assert len(txs.scalars().all()) == 1

        session.add(OpenContribution(
            id=new_id(), khatm_id=khatm_id, participation_id=open_participation_id, amount=1,
        ))
        await session.flush()
        assert await advertising_service.accrue_first_completed_action(session, open_participation_id) is True
        assert await get_balances(session, open_user_id) == (0, 100)

        await session.execute(
            delete(WalletTransaction).where(
                WalletTransaction.wallet_id.in_(
                    select(Wallet.id).where(Wallet.user_id.in_([user_id, open_user_id]))
                )
            )
        )
        await session.execute(delete(Wallet).where(Wallet.user_id.in_([user_id, open_user_id])))
        await session.execute(delete(AdvertisingRewardRate).where(AdvertisingRewardRate.id == rate_id))
        await session.execute(delete(KhatmPortion).where(KhatmPortion.id == portion_id))
        await session.execute(delete(KhatmAllocationPlan).where(KhatmAllocationPlan.id == plan_id))
        await session.execute(delete(OpenContribution).where(OpenContribution.participation_id == open_participation_id))
        await session.execute(delete(Participation).where(Participation.id == participation_id))
        await session.execute(delete(Participation).where(Participation.id == open_participation_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id.in_([user_id, open_user_id])))
