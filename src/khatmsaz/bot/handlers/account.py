"""Account lifecycle commands, including safe account deletion (SPEC Q39)."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="account")


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


def _confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("account.delete_button", lang), callback_data="account_delete:confirm"),
                InlineKeyboardButton(text=t("account.cancel_button", lang), callback_data="account_delete:cancel"),
            ]
        ]
    )


@router.message(F.text == "/delete_account")
async def request_account_deletion(message: Message) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await message.answer(
        t("account.delete_confirm_prompt", lang),
        reply_markup=_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "account_delete:cancel")
async def cancel_account_deletion(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await callback.answer(t("account.deletion_cancelled", lang))
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data == "account_delete:confirm")
async def confirm_account_deletion(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if user is None:
            await callback.answer(t("account.not_found", lang), show_alert=True)
            return
        try:
            await identity_service.delete_account(session, user.id)
        except identity_service.AccountDeletionBlocked as exc:
            parts = []
            if exc.committed_count:
                parts.append(t("account.blocked_committed_count", lang, count=exc.committed_count))
            if exc.active_created_count:
                parts.append(t("account.blocked_active_created_count", lang, count=exc.active_created_count))
            join_word = t("account.blocked_join_word", lang)
            await callback.answer(t("account.blocked_prefix", lang) + join_word.join(parts), show_alert=True)
            return
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(t("account.deleted", lang))
    await callback.answer(t("account.deleted_toast", lang))
