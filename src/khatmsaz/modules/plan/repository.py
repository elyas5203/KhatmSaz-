from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.plan.models import PlanDefinition, PlanTier, PricingMode, UserPlan


async def lock_plan_change(session: AsyncSession, user_id) -> None:
    """Serialize purchases/manual changes for one user's plan."""
    await session.execute(select(func.pg_advisory_xact_lock(func.hashtext(f"plan:{user_id}"))))


async def get_by_user(session: AsyncSession, user_id) -> UserPlan | None:
    return await session.get(UserPlan, user_id)


async def upsert(
    session: AsyncSession,
    user_id,
    plan: PlanTier,
    *,
    expires_at: datetime | None = None,
) -> UserPlan:
    row = await session.get(UserPlan, user_id)
    if row is None:
        row = UserPlan(user_id=user_id, plan=plan, expires_at=expires_at)
        session.add(row)
    else:
        row.plan = plan
        if expires_at is not None:
            row.expires_at = expires_at
    await session.flush()
    return row


async def extend_pro_plan(
    session: AsyncSession,
    user_id,
    days: int = 30,
) -> tuple[UserPlan, datetime]:
    """Charge or award 30 days of PRO. Extends additively if already active."""
    await lock_plan_change(session, user_id)
    row = await session.get(UserPlan, user_id)
    now = datetime.now(timezone.utc)
    if row is None:
        new_expiry = now + timedelta(days=days)
        row = UserPlan(
            user_id=user_id,
            plan=PlanTier.PRO,
            starts_at=now,
            expires_at=new_expiry,
            reminded_7d=False,
            reminded_24h=False,
            expired_notified=False,
        )
        session.add(row)
    else:
        base = row.expires_at if (row.plan == PlanTier.PRO and row.expires_at and row.expires_at > now) else now
        new_expiry = base + timedelta(days=days)
        row.plan = PlanTier.PRO
        row.expires_at = new_expiry
        row.reminded_7d = False
        row.reminded_24h = False
        row.expired_notified = False
    await session.flush()
    return row, new_expiry


async def list_needing_7d_reminder(session: AsyncSession, *, now: datetime) -> list[UserPlan]:
    """Find PRO users expiring within 7 days who have not received 7d warning."""
    stmt = (
        select(UserPlan)
        .where(
            UserPlan.plan == PlanTier.PRO,
            UserPlan.expires_at.is_not(None),
            UserPlan.expires_at > now,
            UserPlan.expires_at <= now + timedelta(days=7),
            UserPlan.reminded_7d.is_(False),
        )
    )
    return list((await session.execute(stmt)).scalars().all())


async def list_needing_24h_reminder(session: AsyncSession, *, now: datetime) -> list[UserPlan]:
    """Find PRO users expiring within 24 hours who have not received 24h warning."""
    stmt = (
        select(UserPlan)
        .where(
            UserPlan.plan == PlanTier.PRO,
            UserPlan.expires_at.is_not(None),
            UserPlan.expires_at > now,
            UserPlan.expires_at <= now + timedelta(hours=24),
            UserPlan.reminded_24h.is_(False),
        )
    )
    return list((await session.execute(stmt)).scalars().all())


async def list_newly_expired_pro(session: AsyncSession, *, now: datetime) -> list[UserPlan]:
    """Find PRO users whose expires_at is past and haven't been notified of lapse."""
    stmt = (
        select(UserPlan)
        .where(
            UserPlan.plan == PlanTier.PRO,
            UserPlan.expires_at.is_not(None),
            UserPlan.expires_at <= now,
            UserPlan.expired_notified.is_(False),
        )
    )
    return list((await session.execute(stmt)).scalars().all())


async def mark_7d_reminded(session: AsyncSession, user_id) -> None:
    row = await session.get(UserPlan, user_id)
    if row is not None:
        row.reminded_7d = True
        await session.flush()


async def mark_24h_reminded(session: AsyncSession, user_id) -> None:
    row = await session.get(UserPlan, user_id)
    if row is not None:
        row.reminded_24h = True
        await session.flush()


async def downgrade_expired_pro(
    session: AsyncSession,
    user_id,
    fallback_plan: PlanTier,
) -> UserPlan | None:
    row = await session.get(UserPlan, user_id)
    if row is not None:
        row.plan = fallback_plan
        row.expired_notified = True
        await session.flush()
    return row


async def get_definition(session: AsyncSession, plan: PlanTier | str) -> PlanDefinition | None:
    key = plan.value if isinstance(plan, PlanTier) else plan
    return await session.get(PlanDefinition, key)


async def upsert_definition(
    session: AsyncSession, *, plan: PlanTier, title: str, pricing_mode: PricingMode,
    price_toman: int, unit_price_toman: int, entitlements: dict
) -> PlanDefinition:
    definition = await get_definition(session, plan)
    if definition is None:
        definition = PlanDefinition(plan=plan.value, title=title)
        session.add(definition)
    definition.title = title
    definition.pricing_mode = pricing_mode
    definition.price_toman = price_toman
    definition.unit_price_toman = unit_price_toman
    definition.entitlements = entitlements
    definition.enabled = True
    await session.flush()
    return definition
