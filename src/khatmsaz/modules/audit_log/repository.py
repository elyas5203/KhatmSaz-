"""Persistence access for the append-only audit module."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.audit_log.models import AuditLog


async def record(
    session: AsyncSession, *, actor_user_id, action: str, target_user_id=None, target_khatm_id=None, details=None
) -> AuditLog:
    entry = AuditLog(
        id=new_id(), actor_user_id=actor_user_id, action=action,
        target_user_id=target_user_id, target_khatm_id=target_khatm_id,
        details=details or {},
    )
    session.add(entry)
    await session.flush()
    return entry


async def list_recent(
    session: AsyncSession, *, action_query: str = "", limit: int = 100
) -> list[AuditLog]:
    """Return a bounded newest-first timeline without exposing mutation APIs."""
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(min(max(limit, 1), 250))
    query = action_query.strip()
    if query:
        stmt = stmt.where(AuditLog.action.ilike(f"%{query}%"))
    return list((await session.execute(stmt)).scalars())
