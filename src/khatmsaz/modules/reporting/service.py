"""Positive personal progress reporting for the bot."""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.allocation.models import KhatmPortion, PortionStatus
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.invitation.models import KhatmInvitation


@dataclass(frozen=True)
class KhatmStats:
    total_members: int
    active_members: int
    completed_members: int
    committed_members: int
    completed_portions: int
    total_portions: int
    contribution_total: float
    invitations_issued: int
    invitations_accepted: int

    @property
    def invitation_conversion_percent(self) -> float:
        if not self.invitations_issued:
            return 0.0
        return round(self.invitations_accepted * 100 / self.invitations_issued, 1)


async def get_khatm_stats(session: AsyncSession, khatm_id) -> KhatmStats:
    member_counts = await session.execute(
        select(
            func.count(),
            func.count(case((Participation.status == ParticipationStatus.ACTIVE, 1))),
            func.count(case((Participation.status == ParticipationStatus.COMPLETED, 1))),
            func.count(case((Participation.is_committed.is_(True), 1))),
        ).where(Participation.khatm_id == khatm_id)
    )
    total_members, active_members, completed_members, committed_members = member_counts.one()

    portion_counts = await session.execute(
        select(
            func.count(),
            func.count(case((KhatmPortion.status == PortionStatus.COMPLETED, 1))),
        ).where(KhatmPortion.khatm_id == khatm_id)
    )
    total_portions, completed_portions = portion_counts.one()

    contribution = await session.execute(
        select(func.coalesce(func.sum(OpenContribution.amount), 0.0)).where(
            OpenContribution.khatm_id == khatm_id
        )
    )
    invitation_counts = await session.execute(
        select(
            func.count(),
            func.count(case((KhatmInvitation.accepted_at.is_not(None), 1))),
        ).where(KhatmInvitation.khatm_id == khatm_id)
    )
    invitations_issued, invitations_accepted = invitation_counts.one()
    return KhatmStats(
        total_members=int(total_members or 0),
        active_members=int(active_members or 0),
        completed_members=int(completed_members or 0),
        committed_members=int(committed_members or 0),
        completed_portions=int(completed_portions or 0),
        total_portions=int(total_portions or 0),
        contribution_total=float(contribution.scalar_one() or 0.0),
        invitations_issued=int(invitations_issued or 0),
        invitations_accepted=int(invitations_accepted or 0),
    )


@dataclass(frozen=True)
class PersonalReport:
    active_khatms: int
    completed_khatms: int
    completed_portions_total: int
    completed_portions_this_month: int
    contributions_this_month: float


@dataclass(frozen=True)
class ClosedMonthReport:
    quran_pages: int
    salawat_count: int
    completed_khatms: int

    @property
    def has_activity(self) -> bool:
        return bool(self.quran_pages or self.salawat_count or self.completed_khatms)


async def get_closed_month_report(
    session: AsyncSession, user_id, *, start: datetime, end: datetime
) -> ClosedMonthReport:
    """Aggregate one already-closed calendar month; never includes misses."""
    portion_result = await session.execute(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (
                            Khatm.template_type == KhatmTemplateType.QURAN_PAGE,
                            KhatmPortion.unit_end - KhatmPortion.unit_start + 1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (Khatm.template_type == KhatmTemplateType.SALAWAT, KhatmPortion.completed_quantity),
                        else_=0,
                    )
                ),
                0,
            ),
        )
        .select_from(KhatmPortion)
        .join(Participation, Participation.id == KhatmPortion.participation_id)
        .join(Khatm, Khatm.id == KhatmPortion.khatm_id)
        .where(
            Participation.user_id == user_id,
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= start,
            KhatmPortion.completed_at < end,
        )
    )
    committed_quran, committed_salawat = portion_result.one()
    open_result = await session.execute(
        select(
            func.coalesce(
                func.sum(case((Khatm.template_type == KhatmTemplateType.QURAN_PAGE, OpenContribution.amount), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(case((Khatm.template_type == KhatmTemplateType.SALAWAT, OpenContribution.amount), else_=0)),
                0,
            ),
        )
        .select_from(OpenContribution)
        .join(Participation, Participation.id == OpenContribution.participation_id)
        .join(Khatm, Khatm.id == OpenContribution.khatm_id)
        .where(
            Participation.user_id == user_id,
            OpenContribution.recorded_at >= start,
            OpenContribution.recorded_at < end,
        )
    )
    open_quran, open_salawat = open_result.one()
    completed_khatms = await session.scalar(
        select(func.count(func.distinct(Khatm.id)))
        .select_from(Khatm)
        .join(Participation, Participation.khatm_id == Khatm.id)
        .where(
            Participation.user_id == user_id,
            Khatm.completed_at >= start,
            Khatm.completed_at < end,
        )
    )
    return ClosedMonthReport(
        quran_pages=int(float(committed_quran or 0) + float(open_quran or 0)),
        salawat_count=int(float(committed_salawat or 0) + float(open_salawat or 0)),
        completed_khatms=int(completed_khatms or 0),
    )


async def get_personal_report(session: AsyncSession, user_id, *, now: datetime | None = None) -> PersonalReport:
    current = now or datetime.now(timezone.utc)
    month_start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    participation_counts = await session.execute(
        select(
            func.count(case((Participation.status == ParticipationStatus.ACTIVE, 1))),
            func.count(case((Participation.status == ParticipationStatus.COMPLETED, 1))),
        ).where(Participation.user_id == user_id)
    )
    active, completed_khatms = participation_counts.one()

    portion_counts = await session.execute(
        select(
            func.count(),
            func.count(case((KhatmPortion.completed_at >= month_start, 1))),
        )
        .select_from(KhatmPortion)
        .join(Participation, Participation.id == KhatmPortion.participation_id)
        .where(
            Participation.user_id == user_id,
            KhatmPortion.status == PortionStatus.COMPLETED,
        )
    )
    completed_total, completed_this_month = portion_counts.one()

    contribution_result = await session.execute(
        select(func.coalesce(func.sum(OpenContribution.amount), 0.0))
        .select_from(OpenContribution)
        .join(Participation, Participation.id == OpenContribution.participation_id)
        .where(
            Participation.user_id == user_id,
            OpenContribution.recorded_at >= month_start,
        )
    )
    contributions = float(contribution_result.scalar_one())
    return PersonalReport(
        active_khatms=int(active or 0),
        completed_khatms=int(completed_khatms or 0),
        completed_portions_total=int(completed_total or 0),
        completed_portions_this_month=int(completed_this_month or 0),
        contributions_this_month=contributions,
    )
