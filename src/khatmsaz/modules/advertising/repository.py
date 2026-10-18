import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.advertising.models import (
    AdvertisingBanner,
    BannerPlacement,
    BannerStatus,
    BannerType,
)


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
    if isinstance(banner_type, str):
        banner_type = BannerType(banner_type)
    if isinstance(placement, str):
        placement = BannerPlacement(placement)
    if isinstance(status, str):
        status = BannerStatus(status)

    banner = AdvertisingBanner(
        id=new_id(),
        title=title.strip(),
        content_text=content_text.strip(),
        banner_type=banner_type,
        placement=placement,
        image_url=image_url.strip() if image_url else None,
        button_text=button_text.strip() if button_text else None,
        button_url=button_url.strip() if button_url else None,
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
    session.add(banner)
    await session.flush()
    return banner


async def get_banner(session: AsyncSession, banner_id: uuid.UUID) -> AdvertisingBanner | None:
    return await session.get(AdvertisingBanner, banner_id)


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
    query = select(AdvertisingBanner)
    if is_active is not None:
        query = query.where(AdvertisingBanner.is_active == is_active)
    if status is not None:
        if isinstance(status, str):
            status = BannerStatus(status)
        query = query.where(AdvertisingBanner.status == status)
    if banner_type is not None:
        if isinstance(banner_type, str):
            banner_type = BannerType(banner_type)
        query = query.where(AdvertisingBanner.banner_type == banner_type)
    if placement is not None:
        if isinstance(placement, str):
            placement = BannerPlacement(placement)
        query = query.where(AdvertisingBanner.placement == placement)

    query = query.order_by(AdvertisingBanner.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    scalars = result.scalars()
    if hasattr(scalars, "all"):
        return list(scalars.all())
    return list(scalars)


async def toggle_banner_active(session: AsyncSession, banner_id: uuid.UUID) -> bool:
    banner = await session.get(AdvertisingBanner, banner_id)
    if banner is None:
        return False
    banner.is_active = not banner.is_active
    await session.flush()
    return banner.is_active


async def update_banner_status(
    session: AsyncSession,
    banner_id: uuid.UUID,
    *,
    status: BannerStatus | str,
    admin_note: str | None = None,
) -> AdvertisingBanner | None:
    banner = await session.get(AdvertisingBanner, banner_id)
    if banner is None:
        return None
    if isinstance(status, str):
        status = BannerStatus(status)
    banner.status = status
    if admin_note is not None:
        banner.admin_note = admin_note
    if status == BannerStatus.APPROVED:
        banner.is_active = True
    elif status in (BannerStatus.REJECTED, BannerStatus.ARCHIVED):
        banner.is_active = False
    await session.flush()
    return banner


async def get_active_banners_for_placement(
    session: AsyncSession,
    placement: BannerPlacement | str,
    *,
    banner_type: BannerType | str | None = None,
    khatm_advertising_enabled: bool = False,
    now: datetime | None = None,
) -> list[AdvertisingBanner]:
    current_time = now or datetime.now(timezone.utc)
    if isinstance(placement, str):
        placement = BannerPlacement(placement)

    query = (
        select(AdvertisingBanner)
        .where(
            AdvertisingBanner.is_active == True,  # noqa: E712
            AdvertisingBanner.status == BannerStatus.APPROVED,
            or_(
                AdvertisingBanner.placement == placement,
                AdvertisingBanner.placement == BannerPlacement.ALL,
            ),
            or_(
                AdvertisingBanner.starts_at.is_(None),
                AdvertisingBanner.starts_at <= current_time,
            ),
            or_(
                AdvertisingBanner.ends_at.is_(None),
                AdvertisingBanner.ends_at >= current_time,
            ),
        )
    )

    if banner_type is not None:
        if isinstance(banner_type, str):
            banner_type = BannerType(banner_type)
        query = query.where(AdvertisingBanner.banner_type == banner_type)
    else:
        # If no specific banner_type requested:
        # Cultural banners are always eligible.
        # Commercial ads are only eligible if khatm_advertising_enabled is True!
        if not khatm_advertising_enabled:
            query = query.where(AdvertisingBanner.banner_type == BannerType.SYSTEM_CULTURAL)

    query = query.order_by(AdvertisingBanner.created_at.desc())
    result = await session.execute(query)
    scalars = result.scalars()
    if hasattr(scalars, "all"):
        return list(scalars.all())
    return list(scalars)


async def record_impression(session: AsyncSession, banner_id: uuid.UUID) -> None:
    await session.execute(
        update(AdvertisingBanner)
        .where(AdvertisingBanner.id == banner_id)
        .values(impressions_count=AdvertisingBanner.impressions_count + 1)
    )
    await session.flush()


async def record_click(session: AsyncSession, banner_id: uuid.UUID) -> None:
    await session.execute(
        update(AdvertisingBanner)
        .where(AdvertisingBanner.id == banner_id)
        .values(clicks_count=AdvertisingBanner.clicks_count + 1)
    )
    await session.flush()


async def get_banner_stats(session: AsyncSession) -> dict[str, int]:
    total_banners = (await session.execute(select(func.count(AdvertisingBanner.id)))).scalar_one() or 0
    active_banners = (
        await session.execute(
            select(func.count(AdvertisingBanner.id)).where(
                AdvertisingBanner.is_active == True,  # noqa: E712
                AdvertisingBanner.status == BannerStatus.APPROVED,
            )
        )
    ).scalar_one() or 0
    pending_review = (
        await session.execute(
            select(func.count(AdvertisingBanner.id)).where(AdvertisingBanner.status == BannerStatus.PENDING)
        )
    ).scalar_one() or 0
    total_impressions = (await session.execute(select(func.sum(AdvertisingBanner.impressions_count)))).scalar_one() or 0
    total_clicks = (await session.execute(select(func.sum(AdvertisingBanner.clicks_count)))).scalar_one() or 0

    return {
        "total_banners": int(total_banners),
        "active_banners": int(active_banners),
        "pending_review": int(pending_review),
        "total_impressions": int(total_impressions),
        "total_clicks": int(total_clicks),
    }
