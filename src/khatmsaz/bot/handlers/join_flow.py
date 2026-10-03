"""Join-continuation handlers shared by the creator and member dispatchers.

Joining a khatm can start on either the creator bot (`start.py`) or a
category member bot (`member_start.py`), but the two follow-up steps —
accepting a commitment and picking a daily delivery hour — used to live
only in `start.py`, which is registered on `dp_creator` alone. On a member
bot those callbacks hit no handler, so a member could never finish joining
a commitment khatm or set a delivery hour. These handlers are extracted
here and registered on *both* dispatchers (see bootstrap `_shared_module_paths`).

The `AskDeliveryHour` state class and `resume_join_after_registration` stay
in `start.py`; importing them here (rather than the reverse) keeps the
dependency one-directional and avoids a circular import.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import (
    bail_if_menu_button,
    home_keyboard_for_bot,
    safe_answer_callback,
)
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.settings import service as settings_service

from khatmsaz.bot.handlers.start import AskDeliveryHour, resume_join_after_registration

router = Router(name="join_flow")


async def _finish_join_prompt(message: Message, data: dict, text: str) -> None:
    """Replace only the bot-owned join wizard message, never unrelated chat history."""
    summary = (data.get("_join_summary") or "").strip()
    if summary and summary not in text:
        text = f"{summary}\n\n{text}"
    message_id = data.get("_join_wizard_mid")
    if message_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=text,
                reply_markup=None,
            )
            return
        except Exception:
            pass
    await message.answer(text)


async def _save_delivery_time(participation_id: str, hour: int, minute: int = 0) -> None:
    async with session_scope() as session:
        await notification_service.set_reminder_preference(
            session, participation_id, reminder_hour=hour, reminder_minute=minute, enabled=True
        )


def _parse_delivery_time(raw: str) -> tuple[int, int] | None:
    """Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid."""
    raw = raw.strip()
    if ":" in raw:
        parts = raw.split(":", 1)
        if not parts[0].isdigit() or not parts[1].isdigit():
            return None
        h, m = int(parts[0]), int(parts[1])
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m
        return None
    if raw.isdigit():
        h = int(raw)
        if 0 <= h <= 23:
            return h, 0
    return None


@router.callback_query(F.data.startswith("join_hour:"), AskDeliveryHour.entering_hour)
async def receive_delivery_hour_button(callback: CallbackQuery, state: FSMContext) -> None:
    hour = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    lang = data.get("lang", "fa")
    participation_id = data.get("delivery_hour_participation_id")
    if participation_id:
        await _save_delivery_time(participation_id, hour, 0)
    await _finish_join_prompt(
        callback.message,
        data,
        t("join.delivery_hour_saved", lang, hour=f"{hour:02d}:00"),
    )
    await state.clear()
    await callback.message.answer(
        t("join.menu_hint", lang),
        reply_markup=home_keyboard_for_bot(callback.message.bot, lang),
    )
    await callback.answer()


@router.message(AskDeliveryHour.entering_hour)
async def receive_delivery_hour(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw = (message.text or "").strip()
    parsed = _parse_delivery_time(raw)
    if parsed is None:
        try:
            await message.delete()
        except Exception:
            pass
        await _finish_join_prompt(message, data, t("join.delivery_hour_invalid", lang))
        return
    hour, minute = parsed
    participation_id = data.get("delivery_hour_participation_id")
    if participation_id:
        await _save_delivery_time(participation_id, hour, minute)
    time_str = f"{hour:02d}:{minute:02d}"
    try:
        await message.delete()
    except Exception:
        pass
    await _finish_join_prompt(message, data, t("join.delivery_hour_saved", lang, hour=time_str))
    await state.clear()
    await message.answer(
        t("join.menu_hint", lang),
        reply_markup=home_keyboard_for_bot(message.bot, lang),
    )


@router.callback_query(F.data.startswith("commitment_consent:accept"))
async def accept_commitment(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    callback_parts = callback.data.split(":", 2)
    token = callback_parts[2] if len(callback_parts) == 3 else data.get("pending_commitment_token")
    if not token:
        # Lang not available here without a DB call; use fa as safe default for a transient error message.
        await callback.answer(t("join.commitment_expired", "fa"), show_alert=True)
        return
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        await state.update_data(pending_commitment_token=None)
        await callback.answer()
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await state.clear()
        if not await settings_service.is_registered(session, user.id) or not user.display_name:
            if getattr(callback.message.bot, "khatmsaz_role", None) == BotRole.MEMBER:
                from khatmsaz.bot.handlers.member_registration import start_member_registration
                await start_member_registration(
                    callback.message, state, pending_join_token=token,
                    consent_accepted=True,
                )
            else:
                from khatmsaz.bot.handlers.registration import start_registration
                await start_registration(
                    callback.message, state, pending_join_token=token,
                    consent_accepted=True,
                )
        else:
            await resume_join_after_registration(
                callback.message, session, user.id, token, state=state, consent_accepted=True
            )
    # This is only the accepted invitation card, never the newly sent question,
    # welcome card or reading media. Cleanup must not undo a successful join.
    try:
        await callback.message.delete()
    except Exception:
        pass


@router.callback_query(F.data.startswith("commitment_consent:cancel"))
async def cancel_commitment(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as _sess:
        _u = await identity_service.resolve_or_provision_user(_sess, platform, callback.from_user.id)
        _s = await settings_service.get_or_create(_sess, _u.id)
        _lang = _s.language
    await callback.answer(t("join.commitment_expired", _lang), show_alert=False)
    await callback.message.answer(
        t("join.commitment_cancelled", _lang),
        reply_markup=home_keyboard_for_bot(callback.message.bot, _lang),
    )
