"""Participant-facing today picker and positive monthly progress report."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from khatmsaz.bot.keyboards import (
    REPORT_BUTTON_TEXTS, TODAY_BUTTON_TEXTS,
    commitment_count_log_keyboard, commitment_quantity_keyboard, contribute_keyboard,
    home_keyboard_for_bot, portion_done_keyboard,
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
from khatmsaz.bot.member_scope import member_instance_id, participation_matches_bot

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
        for participation in await participation_service.list_my_active(
            session, user.id, joined_via_bot_instance_id=member_instance_id(message.bot)
        ):
            khatm = await khatm_service.get_khatm(session, participation.khatm_id)
            if khatm is None:
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
        if (
            participation is None
            or participation.user_id != user.id
            or not participation_matches_bot(participation, bot)
        ):
            await safe_answer_callback(callback, t("portions.not_a_member", lang), show_alert=True)
            return
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        if khatm is None or not khatm_service.has_started(khatm):
            await safe_answer_callback(callback, t("report.no_portion_today", lang), show_alert=True)
            return
        settings = await settings_service.get_or_create(session, user.id)
        try:
            user_tz = ZoneInfo(settings.timezone)
        except (KeyError, ValueError):
            user_tz = ZoneInfo("Asia/Tehran")
        now_utc = datetime.now(timezone.utc)
        today = now_utc.astimezone(user_tz).date()

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
            reserved = await participation_service.advance_open_reading(session, participation.id, pages)
            if reserved is None:
                await safe_answer_callback(callback, t("report.no_portion_today", lang), show_alert=True)
                return
            await participation_service.mark_open_reading_sent_now(session, participation.id)
            start, end = reserved
            from khatmsaz.bot.handlers.portions import _deliver_quran_pages
            await _deliver_quran_pages(
                session, callback.message, khatm=khatm, user_id=user.id,
                page_start=start, page_end=end, platform=platform,
            )
            await callback.message.answer(
                t("report.today_page_label", lang, title=khatm.title, start=start, end=end),
                reply_markup=contribute_keyboard(str(khatm.id), lang),
            )
            await safe_answer_callback(callback)
            return

        # Regular Salawat/Dua/Ziyarat/La'an: merely opening early does NOT
        # consume the scheduled reminder. Only tapping «done» does that.
        if participation.commitment_mode == CommitmentMode.REGULAR.value:
            if (
                participation.schedule_last_sent_at is not None
                and participation.schedule_last_sent_at.astimezone(user_tz).date() == today
            ):
                await safe_answer_callback(callback, t("report.today_already_delivered", lang), show_alert=True)
                return
            count = participation.commitment_per_occurrence or 1
            early_done_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=t("commit.regular.done_button", lang),
                    callback_data=f"regular_early_done:{participation.id}",
                )
            ]])
            await callback.message.answer(
                t("reminder.regular_commitment", lang, title=khatm.title, count=count),
                reply_markup=early_done_keyboard,
            )
            await safe_answer_callback(callback)
            return

        # Count commitments are not clock-triggered; expose their logging action.
        if participation.commitment_mode == CommitmentMode.COUNT.value:
            await callback.message.answer(
                f"🌱 {khatm.title}",
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
            # `deliver_due_next_portions` uses updated_at as its daily gate.
            portion.updated_at = now_utc
            await notification_service.record_sent(session, participation.id, NotificationKind.DAILY_REMINDER)
            from khatmsaz.bot.handlers.portions import _deliver_quran_pages
            await _deliver_quran_pages(
                session, callback.message, khatm=khatm, user_id=user.id,
                page_start=portion.unit_start, page_end=portion.unit_end, platform=platform,
            )
            await callback.message.answer(
                t("report.today_page_label", lang, title=khatm.title, start=portion.unit_start, end=portion.unit_end),
                reply_markup=portion_done_keyboard(str(khatm.id), allow_snooze=bool(khatm.allow_snooze), lang=lang),
            )
            await safe_answer_callback(callback)
            return

        if portion is not None and portion.unit_kind == PortionUnitKind.QUANTITY:
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
            await notification_service.record_sent(session, participation.id, NotificationKind.DAILY_REMINDER)
            await callback.message.answer(
                t("report.today_open", lang, title=khatm.title),
                reply_markup=contribute_keyboard(str(khatm.id), lang),
            )
    await safe_answer_callback(callback)


@router.message(F.text.in_(REPORT_BUTTON_TEXTS))
async def report_menu_button(message: Message) -> None:
    await personal_report(message)


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
