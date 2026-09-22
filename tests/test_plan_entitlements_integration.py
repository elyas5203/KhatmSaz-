import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanTier, PricingMode


@pytest.mark.integration
@pytest.mark.asyncio
async def test_plan_entitlement_lookup_uses_definition_not_plan_name_branching():
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        await session.flush()
        assert await plan_service.has_feature(session, user_id, "report.view") is True
        assert await plan_service.has_feature(session, user_id, "excel.export") is False
        assert (await plan_service.get_definition(session, PlanTier.FREE)).price_toman == 0
        await session.execute(delete(User).where(User.id == user_id))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_creation_price_resolves_fixed_and_usage_based_plan_definitions():
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        await session.flush()
        definition = await plan_service.get_definition(session, PlanTier.FREE)
        original = (definition.pricing_mode, definition.price_toman, definition.unit_price_toman)
        try:
            definition.pricing_mode = PricingMode.USAGE_BASED.value
            definition.price_toman = 999
            definition.unit_price_toman = 123
            await session.flush()
            assert await plan_service.get_creation_price(session, user_id, fallback_price_toman=77) == 123

            definition.pricing_mode = PricingMode.FIXED.value
            definition.price_toman = 456
            await session.flush()
            assert await plan_service.get_creation_price(session, user_id, fallback_price_toman=77) == 456
        finally:
            definition.pricing_mode, definition.price_toman, definition.unit_price_toman = original
            await session.flush()
            await session.execute(delete(User).where(User.id == user_id))
