"""Advertising rewards: opt-in is per khatm and accrual is idempotent."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.allocation.models import KhatmPortion, PortionStatus
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.wallet import repository as wallet_repository
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import TxType, WalletTransaction
from khatmsaz.modules.advertising.models import AdvertisingRewardRate


async def set_reward_rate(
    session: AsyncSession, amount_toman: int, *, effective_from: datetime | None = None
) -> AdvertisingRewardRate:
    if amount_toman <= 0:
        raise ValueError("reward rate must be positive")
    rate = AdvertisingRewardRate(
        id=new_id(), amount_toman=amount_toman,
        effective_from=effective_from or datetime.now(timezone.utc),
    )
    session.add(rate)
    await session.flush()
    return rate


async def get_active_rate(session: AsyncSession, *, now: datetime | None = None) -> AdvertisingRewardRate | None:
    current = now or datetime.now(timezone.utc)
    result = await session.execute(
        select(AdvertisingRewardRate)
        .where(AdvertisingRewardRate.effective_from <= current)
        .order_by(AdvertisingRewardRate.effective_from.desc(), AdvertisingRewardRate.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def accrue_first_completed_action(session: AsyncSession, participation_id) -> bool:
    """Grant one reward only after the first completed assigned action.

    The transaction reference is the idempotency key, so retries cannot grant
    duplicate credit. Waiting/left members and non-opted-in khatms earn none.
    """
    participation = await session.get(Participation, participation_id)
    if participation is None or participation.status != ParticipationStatus.ACTIVE:
        return False
    khatm = await session.get(Khatm, participation.khatm_id)
    if khatm is None or not khatm.advertising_enabled:
        return False
    completed = await session.execute(
        select(KhatmPortion.id)
        .where(
            KhatmPortion.participation_id == participation.id,
            KhatmPortion.status == PortionStatus.COMPLETED,
        )
        .limit(1)
    )
    has_completed_portion = completed.scalar_one_or_none() is not None
    if not has_completed_portion:
        contribution = await session.execute(
            select(OpenContribution.id)
            .where(OpenContribution.participation_id == participation.id)
            .limit(1)
        )
        if contribution.scalar_one_or_none() is None:
            return False
    rate = await get_active_rate(session)
    if rate is None:
        return False
    ref = f"ad-reward:first-action:{participation.id}"
    wallet = await wallet_service.get_or_create_wallet(session, participation.user_id)
    existing = await session.execute(
        select(WalletTransaction.id).where(
            WalletTransaction.wallet_id == wallet.id, WalletTransaction.ref == ref
        ).limit(1)
    )
    if existing.scalar_one_or_none() is not None:
        return False
    await wallet_repository.add_credit(session, wallet.id, rate.amount_toman)
    await wallet_repository.record_transaction(
        session, wallet.id, rate.amount_toman, TxType.CREDIT,
        description="پاداش تبلیغات پس از اولین اقدام کامل‌شده", ref=ref,
    )
    return True
