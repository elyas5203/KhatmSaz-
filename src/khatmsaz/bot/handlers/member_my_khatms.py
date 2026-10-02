"""Member bot "My Khatms" handler — lists khatms the user joined via this bot instance."""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
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
from khatmsaz.bot.member_scope import ensure_participation_matches_bot

router = Router(name="member_my_khatms")


@router.message(F.text.in_(MY_KHATMS_BUTTON_TEXTS))
@router.message(Command("my_khatms"))
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
        result = await session.execute(stmt)
        participations = []
        for participation in result.scalars().all():
            candidate = await session.get(Khatm, participation.khatm_id)
            if candidate is not None and await ensure_participation_matches_bot(session, participation, candidate, bot):
                participations.append(participation)

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
                    callback_data=f"today_pick:{p.id}",
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
async def show_member_reminder_hours(callback: CallbackQuery, state: FSMContext) -> None:
    """Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow
    (join_flow) so BOTH the time-of-day buttons AND a typed exact time like
    «14:40» work (owner request 2026-09-28) — same tested parser/save path."""
    from khatmsaz.bot.handlers.start import AskDeliveryHour
    lang = getattr(callback.message.bot, "khatmsaz_language", "fa")
    participation_id = callback.data.split(":", 1)[1]
    await state.set_state(AskDeliveryHour.entering_hour)
    await state.update_data(delivery_hour_participation_id=participation_id, lang=lang)
    await callback.message.answer(
        t("my_khatms.pick_reminder_hour", lang),
        reply_markup=delivery_hour_keyboard("join_hour", lang),
    )
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
        if (
            participation is None
            or khatm is None
            or not await ensure_participation_matches_bot(session, participation, khatm, bot)
        ):
            await safe_answer_callback(callback, t("portions.not_a_member", lang), show_alert=True)
            return
    callback.data = f"today_pick:{participation.id}"
    from khatmsaz.bot.handlers.report import deliver_today_early
    await deliver_today_early(callback)
