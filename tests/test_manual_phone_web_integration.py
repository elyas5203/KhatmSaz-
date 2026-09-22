import re

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.audit_log.models import AuditLog
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.authorization.models import AdminRole, AdminRoleGrant
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.manual_phone_verification import service as manual_service
from khatmsaz.modules.manual_phone_verification.models import ManualPhoneVerification
from khatmsaz.modules.phone.models import PhoneClaim, PhoneClaimStatus
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.session.models import Session
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.web.app import COOKIE_NAME, app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_support_admin_reviews_foreign_phone_from_mobile_web():
    super_id, support_id, user_id = new_id(), new_id(), new_id()
    phone = "+33612345678"
    async with session_scope() as session:
        super_admin = User(id=super_id, role=UserRole.SUPER_ADMIN)
        support = User(id=support_id, display_name="پشتیبان")
        user = User(id=user_id, display_name="کاربر خارج")
        session.add_all([super_admin, support, user])
        session.add(
            UserSettings(
                user_id=user_id,
                contact_phone=phone,
                province="خارج از ایران",
                city="Paris",
            )
        )
        await session.flush()
        await authorization_service.grant_role(
            session,
            actor=super_admin,
            target=support,
            role=AdminRole.SUPPORT_ADMIN,
        )
        manual_request, _ = await manual_service.submit(
            session, user_id=user_id, e164=phone, purpose="CREATOR_VERIFY"
        )
        token = await session_service.issue_admin_session(session, support)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set(COOKIE_NAME, token)
        page = await client.get("/phone-verifications")
        assert page.status_code == 200
        assert "تأیید شماره‌های خارج از ایران" in page.text
        assert "کاربر خارج" in page.text
        assert phone in page.text
        assert "Paris" in page.text
        assert 'href="/phone-verifications"' in page.text
        csrf = re.search(r'name="csrf" value="([^"]+)"', page.text).group(1)

        bad_csrf = await client.post(
            f"/phone-verifications/{manual_request.id}/decide",
            data={"csrf": "wrong", "decision": "approve"},
            follow_redirects=False,
        )
        assert bad_csrf.status_code == 403

        approved = await client.post(
            f"/phone-verifications/{manual_request.id}/decide",
            data={"csrf": csrf, "decision": "approve"},
            follow_redirects=False,
        )
        assert approved.status_code == 303
        assert approved.headers["location"] == "/phone-verifications?saved=approved"
        saved = await client.get(approved.headers["location"])
        assert "شماره با موفقیت تأیید شد" in saved.text
        assert "درخواستی در انتظار نیست" in saved.text

    async with session_scope() as session:
        request = await session.get(ManualPhoneVerification, manual_request.id)
        claim = await session.scalar(
            select(PhoneClaim).where(
                PhoneClaim.user_id == user_id,
                PhoneClaim.status == PhoneClaimStatus.VERIFIED,
            )
        )
        assert request.status == "APPROVED"
        assert request.reviewed_by_user_id == support_id
        assert claim.e164 == phone
        await session.execute(delete(AuditLog).where(AuditLog.target_user_id == user_id))
        await session.execute(
            delete(ManualPhoneVerification).where(ManualPhoneVerification.user_id == user_id)
        )
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == user_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(Session).where(Session.user_id == support_id))
        await session.execute(delete(AdminRoleGrant).where(AdminRoleGrant.user_id == support_id))
        await session.execute(delete(User).where(User.id.in_([super_id, support_id, user_id])))
