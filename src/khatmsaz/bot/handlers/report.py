"""Participant-facing today picker and positive monthly progress report."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from khatmsaz.bot.keyboards import (
    REPORT_BUTTON_TEXTS, TODAY_BUTTON_TEXTS,
    commitment_count_log_keyboard, commitment_quantity_keyboard, contribute_keyboard,
    creator_finance_keyboard, home_keyboard_for_bot, portion_done_keyboard,
    safe_answer_callback,
)
from khatmsaz.i18n import t
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmTemplateType
from khatmsaz.modules.allocation.models import PortionUnitKind
from khatmsaz.modules.notification.models import NotificationKind
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation.commitment import CommitmentMode
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings import service as settings_service

from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.reporting import service as reporting_service
from khatmsaz.bot.member_scope import ensure_participation_matches_bot

router = Router(name="report")


@router.message(F.text.in_(TODAY_BUTTON_TEXTS))
async def today_overview(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    available: list[tuple[object, object]] = []
    bot_lang = getattr(message.bot, "khatmsaz_language", None)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        if bot_lang:
            lang = bot_lang
        else:
            settings = await settings_service.get_or_create(session, user.id)
            lang = settings.language
        for participation in await participation_service.list_my_active(session, user.id, include_owed=True):
            khatm = await khatm_service.get_khatm(session, participation.khatm_id)
            if khatm is None:
                continue
            if not await ensure_participation_matches_bot(session, participation, khatm, message.bot):
                continue
            if not khatm_service.has_started(khatm):
                continue
            available.append((khatm, participation))
    if not available:
        await message.answer(t("report.no_portion_today", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🌱 {khatm.title}", callback_data=f"today_pick:{participation.id}")]
        for khatm, participation in available
    ])
    await message.answer(t("report.today_pick", lang, count=len(available)), reply_markup=keyboard)


@router.callback_query(F.data.startswith("today_pick:"))
async def deliver_today_early(callback: CallbackQuery) -> None:
    """Deliver one selected khatm now and mark today's scheduled send consumed."""
    bot = callback.message.bot
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = getattr(bot, "khatmsaz_language", "fa")
    participation_id = callback.data.split(":", 1)[1]

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        participation = await participation_service.get_by_id(session, participation_id)
        if participation is None or participation.user_id != user.id:
            await safe_answer_callback(callback, t("portions.not_a_member", lang), show_alert=True)
            return
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        if khatm is None or not await ensure_participation_matches_bot(session, participation, khatm, bot) or not khatm_service.has_started(khatm):
            await safe_answer_callback(callback, t("report.no_portion_today", lang), show_alert=True)
            return
        settings = await settings_service.get_or_create(session, user.id)
        try:
            user_tz = ZoneInfo(settings.timezone)
        except (KeyError, ValueError):
            user_tz = ZoneInfo("Asia/Tehran")
        now_utc = datetime.now(timezone.utc)
        today = now_utc.astimezone(user_tz).date()

        from khatmsaz.modules.share_occurrence import delivery, repository as shares
        if delivery.is_managed(participation, khatm):
            occurrence = await delivery.prepare(session, participation.id, now=now_utc, manual=True)
            if occurrence is not None and occurrence.delivered_at is None:
                try:
                    await delivery.deliver(session, occurrence, now=now_utc)
                except Exception:
                    if not session.is_active:
                        raise
                    # Preserve successful component receipts on API failure;
                    # the next attempt sends only the remaining components.
                    await safe_answer_callback(callback, t("report.content_unavailable", lang), show_alert=True)
                    return
            pending = await shares.list_outstanding(session, participation.id)
            delivered = [item for item in pending if item.delivered_at is not None]
            legacy = await shares.list_legacy_portions(session, participation.id)
            for item in legacy:
                await callback.message.answer(f"📖 سهم قبلی شما: صفحات {item.unit_start} تا {item.unit_end}",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                        text="✅ انجام همین سهم قبلی", callback_data=f"legacy_share_done:{item.id}")]]))
            if delivered:
                from khatmsaz.bot.occurrence_adapter import label, keyboard
                from khatmsaz.modules.share_occurrence import service as occurrence_service
                # Actions refer to each old debt; content is never re-forwarded.
                for item in delivered:
                    receipts = await shares.list_messages(session, item.id)
                    action = next((r for r in receipts if r.purpose == "ACTION"), None)
                    reply_options = {"reply_markup": keyboard(item)}
                    if action and platform == Platform.TELEGRAM:
                        reply_options.update(reply_to_message_id=action.message_id, allow_sending_without_reply=True)
                    view = await callback.message.answer(label(khatm, item), **reply_options)
                    await occurrence_service.record_message(session, occurrence_id=item.id,
                        bot_instance_id=item.bot_instance_id, component_key=f"view:{view.message_id}",
                        purpose="ACTION", chat_id=str(callback.message.chat.id), message_id=view.message_id,
                        sent_at=now_utc)
            elif not legacy:
                await callback.message.answer(t("report.no_portion_today", lang))
            await safe_answer_callback(callback)
            return

        # Open/member-controlled Quran: reserve today's configured page count
        # now and stamp last_sent, so the scheduler cannot send it again later.
        if khatm.template_type == KhatmTemplateType.QURAN_PAGE and participation.open_reading_pages_per_day:
            if (
                participation.open_reading_last_sent_at is not None
                and participation.open_reading_last_sent_at.astimezone(user_tz).date() == today
            ):
                await safe_answer_callback(callback, t("report.today_already_delivered", lang), show_alert=True)
                return
            from khatmsaz.modules.content import service as content_service
            total_pages = content_service.get_quran_total_pages(khatm)
            pages = min(
                participation.open_reading_pages_per_day,
                total_pages - participation.open_reading_next_page + 1,
            )
            if pages <= 0:
                await safe_answer_callback(callback, t("report.no_portion_today", lang), show_alert=True)
                return
            start = participation.open_reading_next_page
            end = start + pages - 1
            from khatmsaz.bot.handlers.portions import _deliver_quran_pages
            delivered = await _deliver_quran_pages(
                session, callback.message, khatm=khatm, user_id=user.id,
                page_start=start, page_end=end, platform=platform,
            )
            if not delivered:
                await safe_answer_callback(callback, t("report.content_unavailable", lang), show_alert=True)
                return
            reserved = await participation_service.advance_open_reading(session, participation.id, pages)
            if reserved is None:
                await safe_answer_callback(callback, t("report.no_portion_today", lang), show_alert=True)
                return
            await participation_service.mark_open_reading_sent_now(session, participation.id)
            await callback.message.answer(
                t("report.today_page_label", lang, title=khatm.title, start=start, end=end),
                reply_markup=contribute_keyboard(str(khatm.id), lang),
            )
            await safe_answer_callback(callback)
            return

        # Regular Salawat/Dua/Ziyarat/La'an: merely opening early does NOT
        # consume the scheduled reminder. Only tapping «done» does that.
        if participation.commitment_mode == CommitmentMode.REGULAR.value and khatm.template_type not in (KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.QURAN_SURAH):
            if (
                participation.schedule_last_sent_at is not None
                and participation.schedule_last_sent_at.astimezone(user_tz).date() == today
            ):
                await safe_answer_callback(callback, t("report.today_already_delivered", lang), show_alert=True)
                return
            count = participation.commitment_per_occurrence or 1
            # L5 (owner 2026-09-30): deliver the actual zekr/dua/ziyarat/salawat
            # content first, then the «انجام سهم» button as the LAST message.
            from khatmsaz.bot.handlers.portions import _send_recitation_content
            await callback.message.answer(t("reminder.regular_commitment", lang, title=khatm.title, count=count))
            if not await _send_recitation_content(session, callback.message, khatm):
                await safe_answer_callback(callback, t("report.content_unavailable", lang), show_alert=True)
                return
            early_done_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=t("commit.regular.done_button", lang),
                    callback_data=f"regular_early_done:{participation.id}",
                )
            ]])
            await callback.message.answer(t("report.today_do_share", lang), reply_markup=early_done_keyboard)
            await safe_answer_callback(callback)
            return

        # Count commitments are not clock-triggered; expose their logging action.
        if participation.commitment_mode == CommitmentMode.COUNT.value:
            from khatmsaz.bot.handlers.portions import _send_recitation_content
            await callback.message.answer(f"🌱 {khatm.title}")
            if not await _send_recitation_content(session, callback.message, khatm):
                await safe_answer_callback(callback, t("report.content_unavailable", lang), show_alert=True)
                return
            await callback.message.answer(
                t("report.today_do_share", lang),
                reply_markup=commitment_count_log_keyboard(str(participation.id), lang),
            )
            await safe_answer_callback(callback)
            return

        portion = await allocation_service.get_current_portion(session, khatm.id, participation.id)
        if khatm.template_type == KhatmTemplateType.QURAN_PAGE:
            if portion is None:
                latest = next((p for p in await allocation_service.list_latest_portion_per_participation(
                    session
                ) if p.participation_id == participation.id), None)
                if (
                    latest is not None and latest.updated_at is not None
                    and latest.updated_at.astimezone(user_tz).date() == today
                ):
                    await safe_answer_callback(callback, t("report.today_already_completed", lang), show_alert=True)
                    return
                portion = await allocation_service.allocate_next_portion_to(session, khatm.id, participation.id)
            if portion is None:
                await safe_answer_callback(callback, t("report.no_portion_today", lang), show_alert=True)
                return
            from khatmsaz.bot.handlers.portions import _deliver_quran_pages
            delivered = await _deliver_quran_pages(
                session, callback.message, khatm=khatm, user_id=user.id,
                page_start=portion.unit_start, page_end=portion.unit_end, platform=platform,
            )
            if not delivered:
                await safe_answer_callback(callback, t("report.content_unavailable", lang), show_alert=True)
                return
            # Only consume today's share after its content was really delivered.
            portion.updated_at = now_utc
            await notification_service.record_sent(session, participation.id, NotificationKind.DAILY_REMINDER)
            await callback.message.answer(
                t("report.today_page_label", lang, title=khatm.title, start=portion.unit_start, end=portion.unit_end),
                reply_markup=portion_done_keyboard(str(khatm.id), allow_snooze=bool(khatm.allow_snooze), lang=lang),
            )
            await safe_answer_callback(callback)
            return

        if portion is not None and portion.unit_kind == PortionUnitKind.QUANTITY:
            from khatmsaz.bot.handlers.portions import _send_recitation_content
            if not await _send_recitation_content(session, callback.message, khatm):
                await safe_answer_callback(callback, t("report.content_unavailable", lang), show_alert=True)
                return
            await callback.message.answer(
                t("report.today_quantity_label", lang, title=khatm.title, quantity=portion.quantity),
                reply_markup=commitment_quantity_keyboard(str(khatm.id), lang),
            )
        else:
            if await notification_service.already_sent_today(
                session, participation.id, NotificationKind.DAILY_REMINDER
            ):
                await safe_answer_callback(callback, t("report.today_already_delivered", lang), show_alert=True)
                return
            if khatm.template_type == KhatmTemplateType.SALAWAT:
                from khatmsaz.bot.handlers.portions import _send_recitation_content
                if not await _send_recitation_content(session, callback.message, khatm):
                    await safe_answer_callback(callback, t("report.content_unavailable", lang), show_alert=True)
                    return
            await notification_service.record_sent(session, participation.id, NotificationKind.DAILY_REMINDER)
            await callback.message.answer(
                t("report.today_open", lang, title=khatm.title),
                reply_markup=contribute_keyboard(str(khatm.id), lang),
            )
    await safe_answer_callback(callback)


def _to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    """Gregorian → Jalali (jalaali algorithm). No external dependency."""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy - 1600
    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    g_day_no += g_d_m[gm - 1] + (gd - 1)
    if gm > 2 and ((gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0):
        g_day_no += 1
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30
    return jy, jm, jd


def _report_date_line(tz_name: str) -> str:
    """Jalali date for Iran/Tehran timezones, Gregorian otherwise (owner 2026-10-01)."""
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("Asia/Tehran")
    now = datetime.now(tz)
    if "Tehran" in tz_name or "Iran" in tz_name:
        jy, jm, jd = _to_jalali(now.year, now.month, now.day)
        return f"📅 گزارش {jd:02d}/{jm:02d}/{jy} (به وقت {now.strftime('%H:%M')})"
    return f"📅 Report {now.strftime('%Y-%m-%d %H:%M')}"


async def creator_finance_report_entry(message: Message) -> None:
    """Khatm report for a creator (owner 2026-10-01): members, read-today vs not,
    progress %, today-vs-yesterday and remaining — with a Jalali date for Iran.
    An empty creator report must never fall back to the member participation report."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTypeEnum
    from khatmsaz.modules.open_contribution import service as _oc
    from khatmsaz.config import get_settings as _gs
    from sqlalchemy import select as _select, func as _func
    from khatmsaz.modules.open_contribution.models import OpenContribution
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        tz_name = settings.timezone or "Asia/Tehran"
        khatms = list((await session.execute(
            _select(Khatm).where(Khatm.creator_user_id == user.id, Khatm.status == KhatmStatus.ACTIVE)
            .order_by(Khatm.created_at.desc()).limit(20)
        )).scalars())
        if not khatms:
            await message.answer(
                t("report.creator_no_active_khatms", lang),
                reply_markup=creator_finance_keyboard(lang),
            )
            return
        app_tz = _gs().app_timezone
        lines = [_report_date_line(tz_name), ""]
        for khatm in khatms:
            stats = await reporting_service.get_khatm_stats(session, khatm.id)
            # read today = distinct active participations with a contribution today
            read_today = int((await session.execute(
                _select(_func.count(_func.distinct(OpenContribution.participation_id)))
                .where(OpenContribution.khatm_id == khatm.id,
                       OpenContribution.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0))
            )).scalar_one())
            not_read = max(0, stats.active_members - read_today)
            if khatm.template_type.value == "QURAN_PAGE" and stats.total_portions:
                progress = round(stats.completed_portions * 100 / stats.total_portions, 1)
                remaining_line = f"⏳ باقی‌مانده: {max(0, stats.total_portions - stats.completed_portions)} سهم"
            elif khatm.repetition_target:
                progress = round(min(100.0, stats.contribution_total * 100 / khatm.repetition_target), 1)
                remaining_line = f"⏳ باقی‌مانده: {max(0, int(khatm.repetition_target - stats.contribution_total))} از {khatm.repetition_target}"
            else:
                progress = None
                remaining_line = f"🔢 تا این لحظه: {int(stats.contribution_total)} مرتبه"
            today_amt, yest_amt = await _oc.today_vs_yesterday(session, khatm.id, app_tz)
            lines.append(f"🔸 <b>{khatm.title}</b>")
            lines.append(f"👥 اعضا: {stats.active_members} نفر")
            lines.append(f"✅ امروز خوانده‌اند: {read_today} نفر | ⛔ نخوانده: {not_read} نفر")
            if progress is not None:
                lines.append(f"📈 پیشرفت: {progress}%")
            lines.append(remaining_line)
            lines.append(f"🔁 امروز {int(today_amt)} / دیروز {int(yest_amt)}")
            lines.append("")
    await message.answer("\n".join(lines).strip(), reply_markup=creator_finance_keyboard(lang))


@router.message(F.text.in_(REPORT_BUTTON_TEXTS))
async def report_menu_button(message: Message) -> None:
    await creator_finance_report_entry(message)


@router.message(Command("report"))
async def personal_report(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        report = await reporting_service.get_personal_report(
            session,
            user.id,
            joined_via_bot_instance_id=member_instance_id(message.bot),
        )

    lines = [
        t("report.header", lang),
        t("report.active_khatms", lang, count=report.active_khatms),
        t("report.completed_khatms", lang, count=report.completed_khatms),
        t("report.completed_portions_month", lang, count=report.completed_portions_this_month),
        t("report.completed_portions_total", lang, count=report.completed_portions_total),
    ]
    if report.contributions_this_month:
        lines.append(t("report.contributions_month", lang, amount=f"{report.contributions_this_month:g}"))
    lines.append(t("report.closing_line", lang))
    await message.answer("\n".join(lines))
