"""Persistence access for open_contribution — the only place that runs SQL for this module."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.open_contribution.models import OpenContribution


async def create(
    session: AsyncSession, khatm_id, participation_id, amount: float,
    note: str | None = None, *, counted_amount: float | None = None,
    surplus_amount: float = 0.0,
) -> OpenContribution:
    contribution = OpenContribution(
        id=new_id(), khatm_id=khatm_id, participation_id=participation_id,
        amount=amount, counted_amount=amount if counted_amount is None else counted_amount,
        surplus_amount=surplus_amount, note=note,
    )
    session.add(contribution)
    await session.flush()
    return contribution


async def total_for_khatm(session: AsyncSession, khatm_id) -> float:
    stmt = select(func.coalesce(func.sum(OpenContribution.amount), 0.0)).where(OpenContribution.khatm_id == khatm_id)
    result = await session.execute(stmt)
    return float(result.scalar_one())


async def total_for_participation(session: AsyncSession, participation_id) -> float:
    stmt = select(func.coalesce(func.sum(OpenContribution.amount), 0.0)).where(
        OpenContribution.participation_id == participation_id
    )
    result = await session.execute(stmt)
    return float(result.scalar_one())


async def has_for_participation_since(
    session: AsyncSession, participation_id, since: datetime,
) -> bool:
    stmt = select(OpenContribution.id).where(
        OpenContribution.participation_id == participation_id,
        OpenContribution.recorded_at >= since,
    ).limit(1)
    return (await session.execute(stmt)).scalar_one_or_none() is not None


async def total_for_khatm_between(
    session: AsyncSession, khatm_id, start: datetime, end: datetime
) -> float:
    stmt = select(func.coalesce(func.sum(OpenContribution.amount), 0.0)).where(
        OpenContribution.khatm_id == khatm_id,
        OpenContribution.recorded_at >= start,
        OpenContribution.recorded_at < end,
    )
    result = await session.execute(stmt)
    return float(result.scalar_one())
