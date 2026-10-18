"""Advertising and banner campaigns: opt-in per khatm, banners, and moderation."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.advertising import repository as ad_repository
from khatmsaz.modules.advertising.models import (
    AdvertisingBanner,
    AdvertisingRewardRate,
    BannerPlacement,
    BannerStatus,
    BannerType,
)
from khatmsaz.modules.allocation.models import KhatmPortion, PortionStatus
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.wallet import repository as wallet_repository
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import TxType, WalletTransaction


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


# ==============================================================================
# Banner Campaigns & Management
# ==============================================================================

async def create_banner(
    session: AsyncSession,
    *,
    title: str,
    content_text: str,
    banner_type: BannerType | str = BannerType.SYSTEM_CULTURAL,
    placement: BannerPlacement | str = BannerPlacement.ALL,
    image_url: str | None = None,
    button_text: str | None = None,
    button_url: str | None = None,
    creator_user_id: uuid.UUID | None = None,
    khatm_id: uuid.UUID | None = None,
    is_active: bool = True,
    status: BannerStatus | str = BannerStatus.APPROVED,
    audience_count: int = 0,
    cost_toman: int = 0,
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    admin_note: str | None = None,
) -> AdvertisingBanner:
    if not title or not title.strip():
        raise ValueError("عنوان بنر نمی‌تواند خالی باشد")
    if not content_text or not content_text.strip():
        raise ValueError("متن بنر نمی‌تواند خالی باشد")

    return await ad_repository.create_banner(
        session,
        title=title,
        content_text=content_text,
        banner_type=banner_type,
        placement=placement,
        image_url=image_url,
        button_text=button_text,
        button_url=button_url,
        creator_user_id=creator_user_id,
        khatm_id=khatm_id,
        is_active=is_active,
        status=status,
        audience_count=audience_count,
        cost_toman=cost_toman,
        starts_at=starts_at,
        ends_at=ends_at,
        admin_note=admin_note,
    )


async def get_banner(session: AsyncSession, banner_id: uuid.UUID) -> AdvertisingBanner | None:
    return await ad_repository.get_banner(session, banner_id)


async def list_banners(
    session: AsyncSession,
    *,
    is_active: bool | None = None,
    status: BannerStatus | str | None = None,
    banner_type: BannerType | str | None = None,
    placement: BannerPlacement | str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AdvertisingBanner]:
    return await ad_repository.list_banners(
        session,
        is_active=is_active,
        status=status,
        banner_type=banner_type,
        placement=placement,
        limit=limit,
        offset=offset,
    )


async def toggle_banner_active(session: AsyncSession, banner_id: uuid.UUID) -> bool:
    return await ad_repository.toggle_banner_active(session, banner_id)


async def review_banner(
    session: AsyncSession,
    banner_id: uuid.UUID,
    decision: str,
    *,
    admin_note: str | None = None,
) -> AdvertisingBanner:
    banner = await ad_repository.get_banner(session, banner_id)
    if banner is None:
        raise ValueError("بنر مورد نظر یافت نشد")

    if decision.lower() in ("approve", "approved", "accept"):
        new_status = BannerStatus.APPROVED
    elif decision.lower() in ("reject", "rejected"):
        new_status = BannerStatus.REJECTED
        # If rejected and creator paid for this banner, refund to wallet!
        if banner.creator_user_id and banner.cost_toman > 0:
            wallet = await wallet_service.get_or_create_wallet(session, banner.creator_user_id)
            ref = f"refund:banner:{banner.id}"
            await wallet_repository.add_balance(session, wallet.id, banner.cost_toman)
            await wallet_repository.record_transaction(
                session,
                wallet.id,
                banner.cost_toman,
                TxType.REFUND,
                description=f"استرداد هزینه تبلیغ رد شده «{banner.title}»",
                ref=ref,
            )
    else:
        raise ValueError(f"تصمیم نامعتبر: {decision}")

    updated = await ad_repository.update_banner_status(
        session,
        banner_id,
        status=new_status,
        admin_note=admin_note,
    )
    return updated or banner


async def get_active_banners_for_placement(
    session: AsyncSession,
    placement: BannerPlacement | str,
    *,
    banner_type: BannerType | str | None = None,
    khatm_advertising_enabled: bool = False,
    now: datetime | None = None,
) -> list[AdvertisingBanner]:
    return await ad_repository.get_active_banners_for_placement(
        session,
        placement,
        banner_type=banner_type,
        khatm_advertising_enabled=khatm_advertising_enabled,
        now=now,
    )


async def record_impression(session: AsyncSession, banner_id: uuid.UUID) -> None:
    await ad_repository.record_impression(session, banner_id)


async def record_click(session: AsyncSession, banner_id: uuid.UUID) -> None:
    await ad_repository.record_click(session, banner_id)


async def get_banner_stats(session: AsyncSession) -> dict[str, int]:
    return await ad_repository.get_banner_stats(session)


def format_banner_for_bot(banner: AdvertisingBanner) -> tuple[str, str | None, str | None]:
    """Format banner text, button_text, and button_url for bot message footer."""
    text = f"\n\n📢 {banner.title}\n{banner.content_text}"
    btn_text = banner.button_text
    btn_url = banner.button_url
    return text, btn_text, btn_url
