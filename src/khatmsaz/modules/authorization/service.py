"""Role-to-permission policy for bot and web administration."""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.authorization import repository
from khatmsaz.modules.authorization.models import AdminPermission, AdminRole
from khatmsaz.modules.identity.models import User, UserRole


ROLE_PERMISSIONS: dict[AdminRole, frozenset[AdminPermission]] = {
    AdminRole.CONTENT_ADMIN: frozenset(
        {AdminPermission.DASHBOARD_ACCESS, AdminPermission.CONTENT_MANAGE}
    ),
    AdminRole.FINANCE_ADMIN: frozenset(
        {AdminPermission.DASHBOARD_ACCESS, AdminPermission.FINANCE_MANAGE}
    ),
    AdminRole.SUPPORT_ADMIN: frozenset(
        {AdminPermission.DASHBOARD_ACCESS, AdminPermission.SUPPORT_USERS}
    ),
    AdminRole.MODERATION_ADMIN: frozenset(
        {AdminPermission.DASHBOARD_ACCESS, AdminPermission.MODERATION_MANAGE}
    ),
    AdminRole.MARKETING_ADMIN: frozenset(
        {AdminPermission.DASHBOARD_ACCESS, AdminPermission.MARKETING_MANAGE}
    ),
    AdminRole.OPERATIONS_ADMIN: frozenset(
        {AdminPermission.DASHBOARD_ACCESS, AdminPermission.OPERATIONS_VIEW}
    ),
}


async def list_roles(session: AsyncSession, user_id) -> tuple[AdminRole, ...]:
    grants = await repository.list_active_grants(session, user_id)
    return tuple(AdminRole(item.role) for item in grants)


async def permissions_for(session: AsyncSession, user: User) -> frozenset[AdminPermission]:
    if user.role == UserRole.SUPER_ADMIN:
        return frozenset(AdminPermission)
    permissions: set[AdminPermission] = set()
    for role in await list_roles(session, user.id):
        permissions.update(ROLE_PERMISSIONS[role])
    return frozenset(permissions)


async def has_permission(
    session: AsyncSession, user: User | None, permission: AdminPermission
) -> bool:
    if user is None or user.deleted_at is not None:
        return False
    return permission in await permissions_for(session, user)


async def is_admin(session: AsyncSession, user: User | None) -> bool:
    return await has_permission(session, user, AdminPermission.DASHBOARD_ACCESS)


async def grant_role(
    session: AsyncSession, *, actor: User, target: User, role: AdminRole
):
    if actor.role != UserRole.SUPER_ADMIN:
        raise PermissionError("only a super admin may grant delegated roles")
    if target.deleted_at is not None:
        raise ValueError("cannot grant an admin role to a deleted user")
    return await repository.grant_role(
        session, user_id=target.id, role=role, granted_by_user_id=actor.id
    )


async def revoke_role(
    session: AsyncSession, *, actor: User, target: User, role: AdminRole
) -> bool:
    if actor.role != UserRole.SUPER_ADMIN:
        raise PermissionError("only a super admin may revoke delegated roles")
    return await repository.revoke_role(session, user_id=target.id, role=role)
