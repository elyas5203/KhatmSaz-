"""Member bot "My Khatms" handler — lists khatms the user joined via this bot instance."""
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.allocation.models import PortionUnitKind
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.bot.keyboards import (
    MY_KHATMS_BUTTON_TEXTS,
    commitment_quantity_keyboard,
    contribute_keyboard,
    delivery_hour_keyboard,
    home_keyboard_for_bot,
    portion_done_keyboard,
    safe_answer_callback,
)
from khatmsaz.modules.notification import service as notification_service

router = Router(name="member_my_khatms")


@router.message(F.text.in_(MY_KHATMS_BUTTON_TEXTS))
async def list_member_khatms(message: Message) -> None:
    bot = message.bot
    platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = getattr(bot, "khatmsaz_language", "fa")
    instance_id = getattr(bot, "khatmsaz_instance_id", None)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)

        # Get participations filtered by instance_id
        stmt = (
            select(Participation)
            .join(Khatm)
            .where(Participation.user_id == user.id)
            .where(Participation.status == ParticipationStatus.ACTIVE)
        )
        if instance_id is not None:
            stmt = stmt.where(Participation.joined_via_bot_instance_id == instance_id)

        result = await session.execute(stmt)
        participations = result.scalars().all()

        if not participations:
            await message.answer(t("my_khatms.empty", lang), reply_markup=home_keyboard_for_bot(bot, lang))
            return

        for p in participations:
            khatm = await session.get(Khatm, p.khatm_id)
            if khatm is None:
                continue

            buttons = [
                [InlineKeyboardButton(
                    text="📅 " + t("menu.today", lang),
                    callback_data=f"mk_portion:{khatm.id}",
                )],
                # Per-khatm reminder time: someone in several khatms can set a
                # different delivery hour for each (owner request 2026-09-27).
                [InlineKeyboardButton(
                    text=t("my_khatms.button.reminder_hour", lang),
                    callback_data=f"mk_hourmenu:{p.id}",
                )],
                [InlineKeyboardButton(
                    text="🚪 " + t("my_khatms.button.leave", lang),
                    callback_data=f"leave_ask:{p.id}",
                )],
            ]
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(f"🔹 {khatm.title}", reply_markup=kb)


@router.callback_query(F.data.startswith("mk_hourmenu:"))
async def show_member_reminder_hours(callback: CallbackQuery) -> None:
    """Show the per-khatm reminder-hour picker for one participation."""
    lang = getattr(callback.message.bot, "khatmsaz_language", "fa")
    participation_id = callback.data.split(":", 1)[1]
    await callback.message.answer(
        t("my_khatms.pick_reminder_hour", lang),
        reply_markup=delivery_hour_keyboard(f"mk_sethour:{participation_id}", lang),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("mk_sethour:"))
async def set_member_reminder_hour(callback: CallbackQuery) -> None:
    """Save the chosen reminder hour for exactly this khatm's participation."""
    lang = getattr(callback.message.bot, "khatmsaz_language", "fa")
    # callback data: mk_sethour:<participation_id>:<hour>
    _, participation_id, hour_raw = callback.data.split(":", 2)
    try:
        hour = int(hour_raw)
    except ValueError:
        await safe_answer_callback(callback)
        return
    async with session_scope() as session:
        await notification_service.set_reminder_preference(
            session, participation_id, reminder_hour=hour, reminder_minute=0, enabled=True
        )
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(t("my_khatms.reminder_hour_saved", lang, hour=hour))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("mk_portion:"))
async def show_member_portion(callback: CallbackQuery) -> None:
    """Show the current portion for one joined khatm, with the same action
    buttons the daily "امروز" overview uses — so the buttons wire back into
    the shared portions handlers (content/done/contribute)."""
    bot = callback.message.bot
    platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = getattr(bot, "khatmsaz_language", "fa")
    khatm_id = callback.data.split(":", 1)[1]

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        stmt = (
            select(Participation)
            .where(Participation.khatm_id == khatm_id)
            .where(Participation.user_id == user.id)
            .where(Participation.status == ParticipationStatus.ACTIVE)
        )
        participation = (await session.execute(stmt)).scalars().first()
        khatm = await session.get(Khatm, khatm_id)
        if participation is None or khatm is None:
            await safe_answer_callback(callback, t("portions.not_a_member", lang), show_alert=True)
            return
        portion = await allocation_service.get_current_portion(session, khatm.id, participation.id)

    if portion is None:
        await callback.message.answer(
            t("report.no_portion_today", lang),
            reply_markup=home_keyboard_for_bot(bot, lang),
        )
        await safe_answer_callback(callback)
        return

    if portion.unit_kind == PortionUnitKind.POSITIONAL:
        await callback.message.answer(
            t("report.today_page_label", lang, title=khatm.title, start=portion.unit_start, end=portion.unit_end),
            reply_markup=portion_done_keyboard(
                str(khatm.id),
                allow_skip_today=bool(khatm.allow_skip_today),
                allow_snooze=bool(khatm.allow_snooze),
                lang=lang,
            ),
        )
    elif portion.unit_kind == PortionUnitKind.QUANTITY:
        await callback.message.answer(
            t("report.today_quantity_label", lang, title=khatm.title, quantity=portion.quantity),
            reply_markup=commitment_quantity_keyboard(str(khatm.id), lang),
        )
    else:
        await callback.message.answer(
            f"🔹 {khatm.title}",
            reply_markup=contribute_keyboard(str(khatm.id), lang),
        )
    await safe_answer_callback(callback)
