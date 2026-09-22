from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.sms_subscription.models import SmsPlanOption, SmsSubscription


async def list_active_options(session: AsyncSession) -> list[SmsPlanOption]:
    stmt = select(SmsPlanOption).where(SmsPlanOption.enabled.is_(True)).order_by(SmsPlanOption.months)
    return list((await session.execute(stmt)).scalars().all())


async def get_option(session: AsyncSession, months: int) -> SmsPlanOption | None:
    return await session.get(SmsPlanOption, months)


async def upsert_option(session: AsyncSession, *, months: int, price_toman: int, enabled: bool) -> SmsPlanOption:
    option = await session.get(SmsPlanOption, months)
    if option is None:
        option = SmsPlanOption(months=months, price_toman=price_toman, enabled=enabled)
        session.add(option)
    else:
        option.price_toman = price_toman
        option.enabled = enabled
    await session.flush()
    return option


async def get_subscription(session: AsyncSession, user_id) -> SmsSubscription | None:
    return await session.get(SmsSubscription, user_id)


async def upsert_subscription(session: AsyncSession, user_id, expires_at) -> SmsSubscription:
    sub = await session.get(SmsSubscription, user_id)
    if sub is None:
        sub = SmsSubscription(user_id=user_id, expires_at=expires_at, expiry_notified=False)
        session.add(sub)
    else:
        sub.expires_at = expires_at
        sub.expiry_notified = False
    await session.flush()
    return sub


async def list_newly_expired(session: AsyncSession, *, now) -> list[SmsSubscription]:
    stmt = select(SmsSubscription).where(
        SmsSubscription.expires_at <= now,
        SmsSubscription.expiry_notified.is_(False),
    )
    return list((await session.execute(stmt)).scalars().all())


async def mark_notified(session: AsyncSession, sub: SmsSubscription) -> None:
    sub.expiry_notified = True
    await session.flush()
