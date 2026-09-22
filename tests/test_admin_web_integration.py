"""Real PostgreSQL + ASGI coverage for the admin dashboard entry flow."""

import re

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.authorization.models import AdminRole, AdminRoleGrant
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.session.models import Session
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.audit_log.models import AuditLog
from khatmsaz.modules.wallet.models import DiscountCoupon
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryRequest
from khatmsaz.web.app import COOKIE_NAME, app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_session_opens_mobile_dashboard_routes():
    admin_id = new_id()
    async with session_scope() as session:
        admin = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="مدیر تست")
        session.add(admin)
        await session.flush()
        token = await session_service.issue_admin_session(session, admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        anonymous = await client.get("/", follow_redirects=False)
        assert anonymous.status_code == 303
        assert anonymous.headers["location"] == "/login"

        client.cookies.set(COOKIE_NAME, token)
        for path, expected in (
            ("/", "وضعیت ختم‌ها روشن است"),
            ("/khatms", "همهٔ ختم‌ها"),
            ("/users", "جست‌وجوی کاربران"),
            ("/templates", "نسخه‌های پیام"),
            ("/finance", "مرکز مالی"),
            ("/admins", "مدیران و نقش‌ها"),
            ("/audit", "خط زمانی فعالیت‌های حساس"),
            ("/operations", "سلامت سرویس‌ها"),
            ("/broadcasts", "پیام‌های گروهی سازنده‌ها"),
            ("/categories", "صلوات، لعن و ادعیه"),
            ("/phone-verifications", "تأیید شماره‌های خارج از ایران"),
        ):
            response = await client.get(path)
            assert response.status_code == 200
            assert expected in response.text
            assert response.headers["x-frame-options"] == "DENY"
            assert response.headers["cache-control"] == "no-store"

        finance = await client.get("/finance")
        csrf_match = re.search(r'name="csrf" value="([^"]+)"', finance.text)
        assert csrf_match is not None
        csrf = csrf_match.group(1)
        created = await client.post(
            "/finance/coupons",
            data={
                "csrf": csrf,
                "code": "WEB20",
                "discount_type": "PERCENT",
                "value": "20",
                "min_purchase_toman": "1000",
                "total_redemption_limit": "5",
                "per_user_limit": "1",
                "max_discount_toman": "2000",
            },
            follow_redirects=False,
        )
        assert created.status_code == 303
        saved = await client.get(created.headers["location"])
        assert "WEB20" in saved.text
        assert "ذخیره و فعال شد" in saved.text

    async with session_scope() as session:
        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == admin_id))
        await session.execute(delete(DiscountCoupon).where(DiscountCoupon.code == "WEB20"))
        await session.execute(delete(Session).where(Session.user_id == admin_id))
        await session.execute(delete(User).where(User.id == admin_id))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_category_admin_lifecycle_is_audited_and_request_cannot_be_replayed():
    admin_id, requester_id = new_id(), new_id()
    async with session_scope() as session:
        admin = User(id=admin_id, role=UserRole.SUPER_ADMIN, display_name="مدیر محتوا")
        requester = User(id=requester_id, display_name="درخواست‌دهنده")
        session.add_all([admin, requester])
        await session.flush()
        request_item = await category_service.submit_request(
            session, requested_title="دعای تست یکپارچه", requested_by_user_id=requester_id
        )
        request_id = request_item.id
        token = await session_service.issue_admin_session(session, admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(COOKIE_NAME, token)
        page = await client.get("/categories")
        assert page.status_code == 200
        assert "دعای تست یکپارچه" in page.text
        csrf_match = re.search(r'name="csrf" value="([^"]+)"', page.text)
        assert csrf_match is not None
        csrf = csrf_match.group(1)

        fulfilled = await client.post(
            f"/categories/requests/{request_id}/fulfill",
            data={
                "csrf": csrf, "group": "DUA", "title": "دعای تست نهایی",
                "body_text": "متن آزمایشی", "source_note": "integration-test",
            },
            follow_redirects=False,
        )
        assert fulfilled.status_code == 303
        saved = await client.get(fulfilled.headers["location"])
        assert "دعای تست نهایی" in saved.text
        assert "دعای تست یکپارچه" not in saved.text

        replay = await client.post(
            f"/categories/requests/{request_id}/fulfill",
            data={"csrf": csrf, "group": "DUA", "title": "کپی ناخواسته"},
            follow_redirects=False,
        )
        assert replay.status_code == 409

    async with session_scope() as session:
        category = (
            await session.execute(
                select(KhatmCategory).where(KhatmCategory.title == "دعای تست نهایی")
            )
        ).scalar_one()
        audit = (
            await session.execute(
                select(AuditLog).where(
                    AuditLog.actor_user_id == admin_id,
                    AuditLog.action == "KHATM_CATEGORY_REQUEST_FULFILL",
                )
            )
        ).scalar_one()
        assert audit.target_user_id == requester_id
        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == admin_id))
        await session.execute(delete(KhatmCategoryRequest).where(KhatmCategoryRequest.id == request_id))
        await session.execute(delete(KhatmCategory).where(KhatmCategory.id == category.id))
        await session.execute(delete(Session).where(Session.user_id == admin_id))
        await session.execute(delete(User).where(User.id.in_([admin_id, requester_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delegated_finance_admin_sees_only_finance_area():
    super_id, finance_id = new_id(), new_id()
    async with session_scope() as session:
        super_admin = User(id=super_id, role=UserRole.SUPER_ADMIN)
        finance_admin = User(id=finance_id, display_name="مدیر مالی")
        session.add_all([super_admin, finance_admin])
        await session.flush()
        await authorization_service.grant_role(
            session,
            actor=super_admin,
            target=finance_admin,
            role=AdminRole.FINANCE_ADMIN,
        )
        token = await session_service.issue_admin_session(session, finance_admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(COOKIE_NAME, token)
        dashboard = await client.get("/")
        assert dashboard.status_code == 200
        assert 'href="/finance"' in dashboard.text
        assert 'href="/templates"' not in dashboard.text
        assert 'href="/users"' not in dashboard.text
        assert (await client.get("/finance")).status_code == 200
        for denied_path in (
            "/templates", "/users", "/khatms", "/admins", "/audit",
            "/phone-verifications",
        ):
            denied = await client.get(denied_path, follow_redirects=False)
            assert denied.status_code == 303
            assert denied.headers["location"] == "/login"

    async with session_scope() as session:
        await session.execute(delete(Session).where(Session.user_id == finance_id))
        await session.execute(delete(AdminRoleGrant).where(AdminRoleGrant.user_id == finance_id))
        await session.execute(delete(User).where(User.id.in_([super_id, finance_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_operations_admin_can_read_but_not_mutate_filtered_audit_timeline():
    super_id, operations_id, target_id = new_id(), new_id(), new_id()
    async with session_scope() as session:
        super_admin = User(id=super_id, role=UserRole.SUPER_ADMIN, display_name="مدیر اصلی")
        operations_admin = User(id=operations_id, display_name="مدیر عملیات")
        target = User(id=target_id, display_name="کاربر هدف")
        session.add_all([super_admin, operations_admin, target])
        await session.flush()
        await authorization_service.grant_role(
            session,
            actor=super_admin,
            target=operations_admin,
            role=AdminRole.OPERATIONS_ADMIN,
        )
        await audit_service.record(
            session,
            actor_user_id=super_id,
            target_user_id=target_id,
            action="USER_WARN",
            details={"reason": "تست خط زمانی"},
        )
        token = await session_service.issue_admin_session(session, operations_admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(COOKIE_NAME, token)
        page = await client.get("/audit?q=USER_WARN")
        assert page.status_code == 200
        assert "اخطار به کاربر" in page.text
        assert "مدیر اصلی" in page.text
        assert "کاربر هدف" in page.text
        assert "تست خط زمانی" in page.text
        assert 'href="/audit"' in page.text
        assert 'method="post"' not in page.text.replace('action="/logout" method="post"', "")
        empty = await client.get("/audit?q=DOES_NOT_EXIST")
        assert "رویدادی با این فیلتر پیدا نشد" in empty.text
        operations = await client.get("/operations")
        assert operations.status_code == 200
        assert "سلامت سرویس‌ها" in operations.text
        assert "پایگاه داده" in operations.text
        assert "پردازشگر یادآوری" in operations.text
        assert 'href="/operations"' in operations.text

    async with session_scope() as session:
        await session.execute(
            delete(AuditLog).where(
                AuditLog.actor_user_id.in_([super_id, operations_id]),
            )
        )
        await session.execute(delete(Session).where(Session.user_id == operations_id))
        await session.execute(delete(AdminRoleGrant).where(AdminRoleGrant.user_id == operations_id))
        await session.execute(delete(User).where(User.id.in_([super_id, operations_id, target_id])))
