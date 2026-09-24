"""User feedback/bug-report inbox to admins (owner request, 2026-09-21).

A plain-text suggestion box reachable from the Help menu's "💡 پیشنهاد یا
گزارش مشکل" button. No new table: the submission is recorded in the
existing append-only `audit_logs` (action `USER_SUGGESTION`, actor is the
submitter, no target) so there's a durable record, and it's pushed live to
every Super Admin chat via the same `super_admin_telegram_chat_ids`
broadcast pattern `manual_phone_verification.py` uses for foreign-number
review requests — no separate admin inbox UI needed for a first version.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import SUPPORT_BUTTON_TEXTS, bail_if_menu_button, main_menu_keyboard, safe_answer_callback, safe_clear_inline_keyboard
from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="suggestions")


class Suggestion(StatesGroup):
    entering_text = State()


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


@router.message(F.text.in_(SUPPORT_BUTTON_TEXTS))
async def start_suggestion_message(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await state.set_state(Suggestion.entering_text)
    await state.update_data(lang=lang)
    await message.answer(t("suggestions.ask_text", lang))

@router.callback_query(F.data == "suggest:start")
async def start_suggestion(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await state.set_state(Suggestion.entering_text)
    await state.update_data(lang=lang)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("suggestions.ask_text", lang))
    await safe_answer_callback(callback)


@router.message(Suggestion.entering_text)
async def receive_suggestion(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    text = (message.text or "").strip()
    if not text:
        await message.answer(t("suggestions.text_required", lang))
        return
    if len(text) > 1000:
        await message.answer(t("suggestions.text_too_long", lang))
        return

    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        display_name = user.display_name or t("suggestions.default_name", lang)
        await audit_service.record(
            session, actor_user_id=user.id, action="USER_SUGGESTION", details={"text": text},
        )

    await state.clear()
    await message.answer(t("suggestions.submitted", lang), reply_markup=main_menu_keyboard(lang))

    admin_ids = [
        item.strip() for item in get_settings().super_admin_telegram_chat_ids.split(",") if item.strip()
    ]
    notify = get_notify_fn()
    admin_text = t("suggestions.admin_notice", "fa", name=display_name, text=text)
    for chat_id in admin_ids:
        await notify(Platform.TELEGRAM.value, chat_id, admin_text)
