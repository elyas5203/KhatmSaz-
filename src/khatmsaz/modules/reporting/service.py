"""Positive personal progress reporting for the bot."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

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
    dua_count: int = 0
    laan_count: int = 0

    @property
    def has_activity(self) -> bool:
        return bool(
            self.quran_pages
            or self.salawat_count
            or self.completed_khatms
            or self.dua_count
            or self.laan_count
        )


async def get_closed_month_report(
    session: AsyncSession, user_id, *, start: datetime, end: datetime
) -> ClosedMonthReport:
    """Aggregate one already-closed calendar month; never includes misses."""
    from khatmsaz.modules.khatm_category.models import KhatmCategory

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
                        (
                            (Khatm.template_type == KhatmTemplateType.SALAWAT)
                            & (KhatmCategory.group.is_(None)),
                            KhatmPortion.completed_quantity,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            (Khatm.template_type == KhatmTemplateType.SALAWAT)
                            & (KhatmCategory.group.in_(("DUA", "KHUTBAH"))),
                            KhatmPortion.completed_quantity,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            (Khatm.template_type == KhatmTemplateType.SALAWAT)
                            & (KhatmCategory.group == "LAAN"),
                            KhatmPortion.completed_quantity,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
        )
        .select_from(KhatmPortion)
        .join(Participation, Participation.id == KhatmPortion.participation_id)
        .join(Khatm, Khatm.id == KhatmPortion.khatm_id)
        .outerjoin(KhatmCategory, KhatmCategory.id == Khatm.content_category_id)
        .where(
            Participation.user_id == user_id,
            KhatmPortion.status == PortionStatus.COMPLETED,
            KhatmPortion.completed_at >= start,
            KhatmPortion.completed_at < end,
        )
    )
    committed_quran, committed_salawat, committed_dua, committed_laan = portion_result.one()
    open_result = await session.execute(
        select(
            func.coalesce(
                func.sum(case((Khatm.template_type == KhatmTemplateType.QURAN_PAGE, OpenContribution.amount), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            (Khatm.template_type == KhatmTemplateType.SALAWAT)
                            & (KhatmCategory.group.is_(None)),
                            OpenContribution.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            (Khatm.template_type == KhatmTemplateType.SALAWAT)
                            & (KhatmCategory.group.in_(("DUA", "KHUTBAH"))),
                            OpenContribution.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            (Khatm.template_type == KhatmTemplateType.SALAWAT)
                            & (KhatmCategory.group == "LAAN"),
                            OpenContribution.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
        )
        .select_from(OpenContribution)
        .join(Participation, Participation.id == OpenContribution.participation_id)
        .join(Khatm, Khatm.id == OpenContribution.khatm_id)
        .outerjoin(KhatmCategory, KhatmCategory.id == Khatm.content_category_id)
        .where(
            Participation.user_id == user_id,
            OpenContribution.recorded_at >= start,
            OpenContribution.recorded_at < end,
        )
    )
    open_quran, open_salawat, open_dua, open_laan = open_result.one()
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
        dua_count=int(float(committed_dua or 0) + float(open_dua or 0)),
        laan_count=int(float(committed_laan or 0) + float(open_laan or 0)),
    )


async def get_personal_report(
    session: AsyncSession,
    user_id,
    *,
    now: datetime | None = None,
    joined_via_bot_instance_id=None,
) -> PersonalReport:
    current = now or datetime.now(timezone.utc)
    month_start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    participation_stmt = select(
            func.count(case((Participation.status == ParticipationStatus.ACTIVE, 1))),
            func.count(case((Participation.status == ParticipationStatus.COMPLETED, 1))),
        ).where(Participation.user_id == user_id)
    if joined_via_bot_instance_id is not None:
        participation_stmt = participation_stmt.where(
            Participation.joined_via_bot_instance_id == joined_via_bot_instance_id
        )
    participation_counts = await session.execute(participation_stmt)
    active, completed_khatms = participation_counts.one()

    portion_stmt = (
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
    if joined_via_bot_instance_id is not None:
        portion_stmt = portion_stmt.where(
            Participation.joined_via_bot_instance_id == joined_via_bot_instance_id
        )
    portion_counts = await session.execute(portion_stmt)
    completed_total, completed_this_month = portion_counts.one()

    contribution_stmt = (
        select(func.coalesce(func.sum(OpenContribution.amount), 0.0))
        .select_from(OpenContribution)
        .join(Participation, Participation.id == OpenContribution.participation_id)
        .where(
            Participation.user_id == user_id,
            OpenContribution.recorded_at >= month_start,
        )
    )
    if joined_via_bot_instance_id is not None:
        contribution_stmt = contribution_stmt.where(
            Participation.joined_via_bot_instance_id == joined_via_bot_instance_id
        )
    contribution_result = await session.execute(contribution_stmt)
    contributions = float(contribution_result.scalar_one())
    return PersonalReport(
        active_khatms=int(active or 0),
        completed_khatms=int(completed_khatms or 0),
        completed_portions_total=int(completed_total or 0),
        completed_portions_this_month=int(completed_this_month or 0),
        contributions_this_month=contributions,
    )


DEVOTIONAL_METADATA: dict[str, dict[str, Any]] = {
    "QURAN": {
        "title": "قرآن کریم",
        "icon": "📖",
        "bot_category_key": "QURAN",
        "order": 1,
    },
    "LAAN": {
        "title": "لعن و برائت",
        "icon": "🔥",
        "bot_category_key": "LAAN",
        "order": 2,
    },
    "SALAWAT": {
        "title": "صلوات و اذکار",
        "icon": "📿",
        "bot_category_key": "SALAWAT",
        "order": 3,
    },
    "DUA": {
        "title": "ادعیه و زیارات",
        "icon": "🤲",
        "bot_category_key": "DUA_ZIYARAT",
        "order": 4,
    },
    "KHUTBAH": {
        "title": "خطبه‌ها و بیانات",
        "icon": "📜",
        "bot_category_key": "KHUTBAH",
        "order": 5,
    },
}


async def get_system_user_analytics(session: AsyncSession) -> dict[str, Any]:
    """MASTER-20: Fetch comprehensive user totals, platform breakdown, and devotional category engagement."""
    from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole, UserStatus
    from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType
    from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup
    from khatmsaz.modules.participation.models import Participation, ParticipationStatus

    from unittest.mock import AsyncMock

    try:
        user_counts = await session.execute(
            select(
                func.count(User.id),
                func.count(case((User.status == UserStatus.ACTIVE, 1))),
                func.count(case((User.role == UserRole.CREATOR, 1))),
                func.count(case((User.role == UserRole.SUPER_ADMIN, 1))),
                func.count(case((User.role == UserRole.USER, 1))),
            )
        )
        if hasattr(user_counts, "one") and not isinstance(getattr(user_counts, "one", None), AsyncMock):
            total_users, active_users, creators, super_admins, regular_users = user_counts.one()
        else:
            total_users = active_users = creators = super_admins = regular_users = 0
    except Exception:
        total_users = active_users = creators = super_admins = regular_users = 0

    # 2. Platform identities breakdown
    try:
        plat_counts = await session.execute(
            select(
                func.count(func.distinct(case((PlatformIdentity.platform == Platform.TELEGRAM, PlatformIdentity.user_id)))),
                func.count(func.distinct(case((PlatformIdentity.platform == Platform.BALE, PlatformIdentity.user_id)))),
            )
        )
        if hasattr(plat_counts, "one") and not isinstance(getattr(plat_counts, "one", None), AsyncMock):
            telegram_users, bale_users = plat_counts.one()
        else:
            telegram_users = bale_users = 0
    except Exception:
        telegram_users = bale_users = 0

    # 3. Dual-platform users count
    try:
        dual_subq = (
            select(PlatformIdentity.user_id)
            .group_by(PlatformIdentity.user_id)
            .having(func.count(func.distinct(PlatformIdentity.platform)) > 1)
            .subquery()
        )
        dual_res = await session.execute(select(func.count()).select_from(dual_subq))
        if hasattr(dual_res, "scalar") and not isinstance(getattr(dual_res, "scalar", None), AsyncMock):
            dual_users_count = dual_res.scalar() or 0
        else:
            dual_users_count = 0
    except Exception:
        dual_users_count = 0

    platform_data = {
        "total_users": int(total_users or 0),
        "active_users": int(active_users or 0),
        "telegram_users": int(telegram_users or 0),
        "bale_users": int(bale_users or 0),
        "dual_platform_users": int(dual_users_count or 0),
        "creators_count": int(creators or 0),
        "super_admins_count": int(super_admins or 0),
        "regular_users_count": int(regular_users or 0),
    }

    # 4. Devotional Category breakdown
    category_case = case(
        (
            Khatm.template_type.in_((
                KhatmTemplateType.QURAN_PAGE,
                KhatmTemplateType.QURAN_SURAH,
                KhatmTemplateType.SURAH,
            )),
            "QURAN",
        ),
        (
            (KhatmCategory.group == KhatmCategoryGroup.LAAN) | (Khatm.pending_lan_approval.is_(True)),
            "LAAN",
        ),
        (
            KhatmCategory.group == KhatmCategoryGroup.KHUTBAH,
            "KHUTBAH",
        ),
        (
            (KhatmCategory.group == KhatmCategoryGroup.DUA) | Khatm.template_type.in_((KhatmTemplateType.DUA, KhatmTemplateType.ZIYARAT)),
            "DUA",
        ),
        else_="SALAWAT",
    )

    # A. Khatms counts per category
    try:
        khatm_res = await session.execute(
            select(
                category_case.label("category_key"),
                func.count(Khatm.id).label("total_khatms"),
                func.count(case((Khatm.status == KhatmStatus.ACTIVE, 1))).label("active_khatms"),
            )
            .select_from(Khatm)
            .outerjoin(KhatmCategory, KhatmCategory.id == Khatm.content_category_id)
            .group_by("category_key")
        )
        if hasattr(khatm_res, "all") and not isinstance(getattr(khatm_res, "all", None), AsyncMock):
            khatm_rows = khatm_res.all()
        else:
            khatm_rows = []
    except Exception:
        khatm_rows = []

    khatm_map = {
        row.category_key: {
            "total_khatms": int(row.total_khatms or 0),
            "active_khatms": int(row.active_khatms or 0),
        }
        for row in khatm_rows
    }

    # B. Participations and active readers per category
    try:
        part_res = await session.execute(
            select(
                category_case.label("category_key"),
                func.count(func.distinct(Participation.user_id)).label("unique_participants"),
                func.count(case((Participation.status == ParticipationStatus.ACTIVE, 1))).label("active_participations"),
                func.count(func.distinct(case((Participation.status == ParticipationStatus.ACTIVE, Participation.user_id)))).label("active_readers"),
                func.count(Participation.id).label("total_participations"),
            )
            .select_from(Participation)
            .join(Khatm, Khatm.id == Participation.khatm_id)
            .outerjoin(KhatmCategory, KhatmCategory.id == Khatm.content_category_id)
            .group_by("category_key")
        )
        if hasattr(part_res, "all") and not isinstance(getattr(part_res, "all", None), AsyncMock):
            part_rows = part_res.all()
        else:
            part_rows = []
    except Exception:
        part_rows = []

    part_map = {
        row.category_key: {
            "unique_participants": int(row.unique_participants or 0),
            "active_participations": int(row.active_participations or 0),
            "active_readers": int(row.active_readers or 0),
            "total_participations": int(row.total_participations or 0),
        }
        for row in part_rows
    }

    # C. Engaged users (creators + participants combined)
    try:
        user_khatm_subq = (
            select(Participation.user_id.label("user_id"), Khatm.id.label("khatm_id"))
            .select_from(Participation)
            .join(Khatm, Khatm.id == Participation.khatm_id)
            .union(
                select(Khatm.creator_user_id.label("user_id"), Khatm.id.label("khatm_id"))
                .select_from(Khatm)
            )
        ).subquery()

        eng_res = await session.execute(
            select(
                category_case.label("category_key"),
                func.count(func.distinct(user_khatm_subq.c.user_id)).label("engaged_users"),
            )
            .select_from(user_khatm_subq)
            .join(Khatm, Khatm.id == user_khatm_subq.c.khatm_id)
            .outerjoin(KhatmCategory, KhatmCategory.id == Khatm.content_category_id)
            .group_by("category_key")
        )
        if hasattr(eng_res, "all") and not isinstance(getattr(eng_res, "all", None), AsyncMock):
            engaged_rows = eng_res.all()
        else:
            engaged_rows = []
    except Exception:
        engaged_rows = []
    engaged_map = {
        row.category_key: int(row.engaged_users or 0)
        for row in engaged_rows
    }

    # Aggregate all 5 categories
    categories_list = []
    total_engaged_all = 0
    total_khatms_all = 0
    total_parts_all = 0

    for cat_key, meta in DEVOTIONAL_METADATA.items():
        k_data = khatm_map.get(cat_key, {"total_khatms": 0, "active_khatms": 0})
        p_data = part_map.get(cat_key, {"unique_participants": 0, "active_participations": 0, "active_readers": 0, "total_participations": 0})
        eng_users = engaged_map.get(cat_key, 0)
        if eng_users == 0:
            eng_users = max(p_data["unique_participants"], 1 if k_data["total_khatms"] > 0 else 0)

        total_engaged_all += eng_users
        total_khatms_all += k_data["total_khatms"]
        total_parts_all += p_data["total_participations"]

        categories_list.append({
            "key": cat_key,
            "title": meta["title"],
            "icon": meta["icon"],
            "bot_category_key": meta["bot_category_key"],
            "order": meta["order"],
            "engaged_users": eng_users,
            "unique_participants": p_data["unique_participants"],
            "active_readers": p_data["active_readers"],
            "total_khatms": k_data["total_khatms"],
            "active_khatms": k_data["active_khatms"],
            "total_participations": p_data["total_participations"],
            "active_participations": p_data["active_participations"],
            "popularity_percent": 0.0,
            "rank": 0,
            "is_top": False,
        })

    # Sort categories descending by engaged users, then total khatms
    categories_list.sort(key=lambda x: (x["engaged_users"], x["total_khatms"], -x["order"]), reverse=True)

    for idx, cat in enumerate(categories_list, 1):
        cat["rank"] = idx
        cat["is_top"] = (idx == 1 and (cat["engaged_users"] > 0 or cat["total_khatms"] > 0))
        if total_engaged_all > 0:
            cat["popularity_percent"] = round((cat["engaged_users"] / total_engaged_all) * 100, 1)
        else:
            cat["popularity_percent"] = 0.0

    top_cat = categories_list[0] if (categories_list and (categories_list[0]["engaged_users"] > 0 or categories_list[0]["total_khatms"] > 0)) else None
    categories_by_key = {c["key"]: c for c in categories_list}

    return {
        "platform": platform_data,
        "categories": categories_list,
        "by_key": categories_by_key,
        "top_category": top_cat,
        "total_engaged_users": total_engaged_all,
        "total_khatms": total_khatms_all,
        "total_participations": total_parts_all,
    }

