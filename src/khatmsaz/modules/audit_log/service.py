"""Business facade for recording privileged actions."""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.audit_log import repository


async def record(
    session: AsyncSession, *, actor_user_id, action: str, target_user_id=None, target_khatm_id=None, details=None
):
    return await repository.record(
        session, actor_user_id=actor_user_id, action=action,
        target_user_id=target_user_id, target_khatm_id=target_khatm_id, details=details,
    )


async def list_recent(session: AsyncSession, *, action_query: str = "", limit: int = 100):
    return await repository.list_recent(session, action_query=action_query, limit=limit)
