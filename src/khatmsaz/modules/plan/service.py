"""Plan business logic. A missing row means FREE — never create a row just
to read someone's plan (DOMAIN_MODEL.md §7: keep this cheap and lazy)."""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.plan import repository
from khatmsaz.modules.plan.models import PlanTier, PricingMode


class PlanFeatureUnavailableError(Exception):
    """The active plan does not permit the requested feature."""


async def get_plan(session: AsyncSession, user_id) -> PlanTier:
    row = await repository.get_by_user(session, user_id)
    return row.plan if row is not None else PlanTier.FREE


async def set_plan(session: AsyncSession, user_id, plan: PlanTier) -> None:
    await repository.upsert(session, user_id, plan)


async def get_definition(session: AsyncSession, plan: PlanTier | str):
    return await repository.get_definition(session, plan)


async def has_feature(session: AsyncSession, user_id, feature_key: str) -> bool:
    """Check an entitlement by key; callers need not branch on plan names."""
    definition = await get_definition(session, await get_plan(session, user_id))
    return bool(definition and definition.enabled and definition.entitlements.get(feature_key, False))


async def get_creation_price(
    session: AsyncSession, user_id, *, fallback_price_toman: int = 0
) -> int:
    """Resolve the authoritative charge for creating one khatm.

    Plan definitions are the source of truth. The fallback keeps deployments
    that predate the plan-definition migration compatible. A usage-based
    definition charges its per-use amount for one creation.
    """
    definition = await get_definition(session, await get_plan(session, user_id))
    if definition is None:
        return max(0, fallback_price_toman)
    if not definition.enabled or not definition.entitlements.get("khatm.create", False):
        raise PlanFeatureUnavailableError("khatm.create")
    if definition.pricing_mode == PricingMode.USAGE_BASED.value:
        return max(0, definition.unit_price_toman)
    return max(0, definition.price_toman)


async def set_definition(
    session: AsyncSession, *, plan: PlanTier, title: str, pricing_mode: PricingMode,
    price_toman: int, unit_price_toman: int, entitlements: dict
):
    if price_toman < 0 or unit_price_toman < 0:
        raise ValueError("prices cannot be negative")
    normalized_mode = pricing_mode.value if isinstance(pricing_mode, PricingMode) else pricing_mode
    return await repository.upsert_definition(
        session, plan=plan, title=title, pricing_mode=normalized_mode,
        price_toman=price_toman, unit_price_toman=unit_price_toman,
        entitlements=entitlements,
    )
