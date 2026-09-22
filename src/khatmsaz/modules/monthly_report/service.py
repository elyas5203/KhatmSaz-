"""Timezone-aware, idempotent delivery of the previous month's progress."""

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import UserStatus
from khatmsaz.modules.reporting import service as reporting_service
from khatmsaz.modules.settings import repository as settings_repository

NotifyFn = Callable[[str, str, str], Awaitable[None]]


def _previous_month_bounds(local_now: datetime) -> tuple[datetime, datetime, str]:
    end_local = local_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if end_local.month == 1:
        start_local = end_local.replace(year=end_local.year - 1, month=12)
    else:
        start_local = end_local.replace(month=end_local.month - 1)
    return (
        start_local.astimezone(timezone.utc),
        end_local.astimezone(timezone.utc),
        start_local.strftime("%Y-%m"),
    )


def _render(period: str, report, locale: str) -> str:
    if locale == "ar":
        lines = [f"🌙 تقريرك الإيجابي لشهر {period}", "تقبّل الله منك 🤍"]
        labels = ("صفحات القرآن", "الصلوات", "الختمات المكتملة")
    elif locale == "en":
        lines = [f"🌙 Your positive report for {period}", "May your devotion be accepted 🤍"]
        labels = ("Quran pages", "Salawat", "Completed khatms")
    else:
        lines = [f"🌙 گزارش مثبت شما برای ماه {period}", "همراهی‌تان ارزشمند است؛ خدا قبول کند 🤍"]
        labels = ("صفحه قرآن", "صلوات", "ختم به‌پایان‌رسیده")
    if report.quran_pages:
        lines.append(f"📖 {labels[0]}: {report.quran_pages}")
    if report.salawat_count:
        lines.append(f"📿 {labels[1]}: {report.salawat_count}")
    if report.completed_khatms:
        lines.append(f"🎉 {labels[2]}: {report.completed_khatms}")
    return "\n".join(lines)


async def deliver_due(
    session: AsyncSession,
    notify: NotifyFn,
    *,
    now: datetime | None = None,
    report_day: int = 1,
    report_hour: int = 10,
    user_ids: set | None = None,
) -> int:
    if not 1 <= report_day <= 28 or not 0 <= report_hour <= 23:
        raise ValueError("invalid monthly report schedule")
    current = now or datetime.now(timezone.utc)
    delivered = 0
    for settings in await settings_repository.list_all(session, user_ids=user_ids):
        try:
            local_now = current.astimezone(ZoneInfo(settings.timezone))
        except (ZoneInfoNotFoundError, ValueError):
            local_now = current.astimezone(ZoneInfo("Asia/Tehran"))
        if (local_now.day, local_now.hour) < (report_day, report_hour):
            continue
        start, end, period = _previous_month_bounds(local_now)
        if settings.last_monthly_report_period == period:
            continue
        user = await identity_service.find_by_id(session, settings.user_id)
        if user is None or user.status != UserStatus.ACTIVE or user.deleted_at is not None:
            settings.last_monthly_report_period = period
            continue
        report = await reporting_service.get_closed_month_report(
            session, user.id, start=start, end=end
        )
        if report.has_activity:
            text = _render(period, report, settings.language)
            for identity in await identity_service.list_identities_for_user(session, user.id):
                await notify(identity.platform.value, identity.subject, text)
            delivered += 1
        settings.last_monthly_report_period = period
    await session.flush()
    return delivered
