"""Persistence access for plan — the only place that runs SQL for this module."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.plan.models import PlanDefinition, PlanTier, PricingMode, UserPlan


async def lock_plan_change(session: AsyncSession, user_id) -> None:
    """Serialize purchases/manual changes for one user's plan."""
    await session.execute(select(func.pg_advisory_xact_lock(func.hashtext(f"plan:{user_id}"))))


async def get_by_user(session: AsyncSession, user_id) -> UserPlan | None:
    return await session.get(UserPlan, user_id)


async def upsert(session: AsyncSession, user_id, plan: PlanTier) -> UserPlan:
    row = await session.get(UserPlan, user_id)
    if row is None:
        row = UserPlan(user_id=user_id, plan=plan)
        session.add(row)
    else:
        row.plan = plan
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
