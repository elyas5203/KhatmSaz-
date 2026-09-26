"""Participant-facing positive monthly progress report."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from khatmsaz.bot.keyboards import (
    REPORT_BUTTON_TEXTS, TODAY_BUTTON_TEXTS,
    home_keyboard_for_bot, main_menu_keyboard, portion_done_keyboard,
)
from khatmsaz.i18n import t
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings import service as settings_service

from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.reporting import service as reporting_service

router = Router(name="report")


@router.message(F.text.in_(TODAY_BUTTON_TEXTS))
async def today_overview(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    pending: list[tuple[object, object, object]] = []
    bot_lang = getattr(message.bot, "khatmsaz_language", None)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        if bot_lang:
            lang = bot_lang
        else:
            settings = await settings_service.get_or_create(session, user.id)
            lang = settings.language
        for participation in await participation_service.list_my_active(session, user.id):
            khatm = await khatm_service.get_khatm(session, participation.khatm_id)
            if khatm is None:
                continue
            if not khatm_service.has_started(khatm):
                continue
            portion = await allocation_service.get_current_portion(session, khatm.id, participation.id)
            if portion is not None:
                pending.append((khatm, participation, portion))
    if not pending:
        await message.answer(t("report.no_portion_today", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
        return
    await message.answer(t("report.today_count", lang, count=len(pending)))
    for khatm, _participation, portion in pending:
        if portion.unit_kind.value == "POSITIONAL":
            label = t("report.today_page_label", lang, title=khatm.title, start=portion.unit_start, end=portion.unit_end)
            await message.answer(label, reply_markup=portion_done_keyboard(str(khatm.id), allow_skip_today=bool(khatm.allow_skip_today), allow_snooze=bool(khatm.allow_snooze), lang=lang))
        else:
            await message.answer(
                t("report.today_quantity_label", lang, title=khatm.title, quantity=portion.quantity),
                reply_markup=home_keyboard_for_bot(message.bot, lang),
            )


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
        report = await reporting_service.get_personal_report(session, user.id)

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
