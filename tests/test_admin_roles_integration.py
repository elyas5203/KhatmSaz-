"""Real PostgreSQL coverage for revocable delegated admin roles."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.authorization import service
from khatmsaz.modules.authorization.models import (
    AdminPermission,
    AdminRole,
    AdminRoleGrant,
)
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.session.models import Session


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delegated_admin_role_is_scoped_auditable_and_revocable():
    super_id, finance_id = new_id(), new_id()
    async with session_scope() as session:
        super_admin = User(id=super_id, role=UserRole.SUPER_ADMIN)
        finance_admin = User(id=finance_id)
        session.add_all([super_admin, finance_admin])
        await session.flush()

        assert not await service.is_admin(session, finance_admin)
        await service.grant_role(
            session,
            actor=super_admin,
            target=finance_admin,
            role=AdminRole.FINANCE_ADMIN,
        )
        assert await service.has_permission(
            session, finance_admin, AdminPermission.FINANCE_MANAGE
        )
        assert not await service.has_permission(
            session, finance_admin, AdminPermission.CONTENT_MANAGE
        )

        raw = await session_service.issue_admin_session(session, finance_admin)
        assert (await session_service.authenticate_admin(session, raw)).id == finance_id

        assert await service.revoke_role(
            session,
            actor=super_admin,
            target=finance_admin,
            role=AdminRole.FINANCE_ADMIN,
        )
        assert await session_service.authenticate_admin(session, raw) is None

        await session.execute(delete(Session).where(Session.user_id == finance_id))
        await session.execute(delete(AdminRoleGrant).where(AdminRoleGrant.user_id == finance_id))
        await session.execute(delete(User).where(User.id.in_([super_id, finance_id])))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_non_super_admin_cannot_delegate_roles():
    first_id, second_id = new_id(), new_id()
    async with session_scope() as session:
        first, second = User(id=first_id), User(id=second_id)
        session.add_all([first, second])
        await session.flush()
        with pytest.raises(PermissionError):
            await service.grant_role(
                session,
                actor=first,
                target=second,
                role=AdminRole.SUPPORT_ADMIN,
            )
        await session.execute(delete(User).where(User.id.in_([first_id, second_id])))
