"""Real PostgreSQL coverage for secure admin web sessions."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.session import service
from khatmsaz.modules.session.models import Session


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_web_session_is_role_gated_authenticates_and_revokes():
    admin_id, regular_id = new_id(), new_id()
    async with session_scope() as session:
        admin = User(id=admin_id, role=UserRole.SUPER_ADMIN)
        regular = User(id=regular_id)
        session.add_all([admin, regular])
        await session.flush()

        with pytest.raises(PermissionError):
            await service.issue_admin_session(session, regular)

        raw = await service.issue_admin_session(session, admin)
        authenticated = await service.authenticate_admin(session, raw)
        assert authenticated.id == admin_id

        await service.revoke_admin_session(session, raw)
        assert await service.authenticate_admin(session, raw) is None

        await session.execute(delete(Session).where(Session.user_id == admin_id))
        await session.execute(delete(User).where(User.id.in_([admin_id, regular_id])))
