"""Persistence helpers for delegated admin roles."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.authorization.models import AdminRole, AdminRoleGrant


async def list_active_grants(session: AsyncSession, user_id) -> list[AdminRoleGrant]:
    result = await session.execute(
        select(AdminRoleGrant)
        .where(AdminRoleGrant.user_id == user_id, AdminRoleGrant.revoked_at.is_(None))
        .order_by(AdminRoleGrant.role)
    )
    return list(result.scalars())


async def grant_role(
    session: AsyncSession, *, user_id, role: AdminRole, granted_by_user_id
) -> AdminRoleGrant:
    item = await session.scalar(
        select(AdminRoleGrant)
        .where(AdminRoleGrant.user_id == user_id, AdminRoleGrant.role == role.value)
        .with_for_update()
    )
    if item is None:
        item = AdminRoleGrant(
            id=new_id(),
            user_id=user_id,
            role=role.value,
            granted_by_user_id=granted_by_user_id,
        )
        session.add(item)
    else:
        item.granted_by_user_id = granted_by_user_id
        item.granted_at = datetime.now(timezone.utc)
        item.revoked_at = None
    await session.flush()
    return item


async def revoke_role(session: AsyncSession, *, user_id, role: AdminRole) -> bool:
    item = await session.scalar(
        select(AdminRoleGrant)
        .where(
            AdminRoleGrant.user_id == user_id,
            AdminRoleGrant.role == role.value,
            AdminRoleGrant.revoked_at.is_(None),
        )
        .with_for_update()
    )
    if item is None:
        return False
    item.revoked_at = datetime.now(timezone.utc)
    await session.flush()
    return True
