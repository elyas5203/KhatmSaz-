"""Real PostgreSQL coverage for plan controls exposed in the admin Mini App."""

import re

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.audit_log.models import AuditLog
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.plan.models import PlanDefinition, PlanTier
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.session.models import Session
from khatmsaz.modules.sms_subscription.models import SmsPlanOption
from khatmsaz.web.app import COOKIE_NAME, app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_finance_admin_can_edit_product_and_sms_plans_from_mini_app():
    admin_id = new_id()
    sms_months = 17
    async with session_scope() as session:
        admin = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="مدیر پلن")
        session.add(admin)
        await session.flush()
        token = await session_service.issue_admin_session(session, admin)
        free = await session.get(PlanDefinition, PlanTier.FREE.value)
        original = {
            "title": free.title,
            "pricing_mode": free.pricing_mode,
            "price_toman": free.price_toman,
            "unit_price_toman": free.unit_price_toman,
            "entitlements": dict(free.entitlements),
            "enabled": free.enabled,
        }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(COOKIE_NAME, token)
        page = await client.get("/finance")
        assert page.status_code == 200
        assert "پلن‌های ساخت ختم" in page.text
        assert "گزینه‌های اشتراک پیامک" in page.text
        csrf = re.search(r'name="csrf" value="([^"]+)"', page.text).group(1)

        plan_response = await client.post(
            "/finance/plans/FREE",
            data={
                "csrf": csrf,
                "title": "رایگان آزمایشی",
                "pricing_mode": "USAGE_BASED",
                "price_toman": "321",
                "max_devotional_members": "111",
                "max_quran_members": "",
                "khatm_create": "on",
                "enabled": "on",
            },
            follow_redirects=False,
        )
        assert plan_response.status_code == 303
        assert plan_response.headers["location"] == "/finance?saved=plan"

        sms_response = await client.post(
            "/finance/sms-plans",
            data={
                "csrf": csrf,
                "months": str(sms_months),
                "price_toman": "123456",
                "enabled": "on",
            },
            follow_redirects=False,
        )
        assert sms_response.status_code == 303
        assert sms_response.headers["location"] == "/finance?saved=sms"
        saved = await client.get("/finance?saved=sms")
        assert "گزینهٔ اشتراک پیامک ذخیره شد" in saved.text
        assert "123456" in saved.text

        invalid = await client.post(
            "/finance/sms-plans",
            data={"csrf": csrf, "months": "0", "price_toman": "1", "enabled": "on"},
        )
        assert invalid.status_code == 400

    async with session_scope() as session:
        free = await session.get(PlanDefinition, PlanTier.FREE.value)
        assert free.title == "رایگان آزمایشی"
        assert free.pricing_mode == "USAGE_BASED"
        assert free.unit_price_toman == 321
        assert free.price_toman == 0
        assert free.entitlements["max_devotional_members"] == 111
        assert "max_quran_members" not in free.entitlements
        assert free.entitlements["khatm.create"] is True
        sms = await session.get(SmsPlanOption, sms_months)
        assert sms.price_toman == 123456 and sms.enabled is True
        actions = set(
            (await session.execute(
                select(AuditLog.action).where(AuditLog.actor_user_id == admin_id)
            )).scalars()
        )
        assert {"PLAN_DEFINITION_UPDATE", "SMS_PLAN_OPTION_UPDATE"} <= actions

        free.title = original["title"]
        free.pricing_mode = original["pricing_mode"]
        free.price_toman = original["price_toman"]
        free.unit_price_toman = original["unit_price_toman"]
        free.entitlements = original["entitlements"]
        free.enabled = original["enabled"]
        await session.execute(delete(SmsPlanOption).where(SmsPlanOption.months == sms_months))
        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == admin_id))
        await session.execute(delete(Session).where(Session.user_id == admin_id))
        await session.execute(delete(User).where(User.id == admin_id))
