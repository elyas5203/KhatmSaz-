"""Discovery and joining for active PUBLIC khatms."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.handlers.start import resume_join_after_registration
from khatmsaz.bot.keyboards import PUBLIC_KHATMS_BUTTON_TEXTS, commitment_consent_keyboard, home_keyboard_for_bot, main_menu_keyboard, public_khatms_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmTypeEnum
from khatmsaz.modules.settings import service as settings_service

router = Router(name="public_khatms")


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


@router.message(F.text.in_(PUBLIC_KHATMS_BUTTON_TEXTS))
@router.message(Command("public_khatms"))
async def list_public_khatms(message: Message) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    async with session_scope() as session:
        khatms = await khatm_service.list_public_active(session, limit=20)
    if not khatms:
        await message.answer(t("public_khatms.none_active", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
        return
    await message.answer(
        t("public_khatms.list_prompt", lang),
        reply_markup=public_khatms_keyboard(khatms),
    )


@router.callback_query(lambda callback: callback.data and callback.data.startswith("public_join:"))
async def join_public_khatm(callback: CallbackQuery, state: FSMContext) -> None:
    khatm_id = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or khatm.khatm_type is None or khatm.status.value != "ACTIVE" or khatm.visibility.value != "PUBLIC":
            await callback.answer(t("public_khatms.no_longer_available", lang), show_alert=True)
            return
        token = await invitation_service.create_invitation(session, khatm.id, khatm.creator_user_id)
        if not await settings_service.is_registered(session, user.id) or not user.display_name:
            from khatmsaz.bot.handlers.registration import start_registration

            await start_registration(callback.message, state, pending_join_token=token)
            await callback.answer()
            return
        if khatm.khatm_type == KhatmTypeEnum.COMMITMENT:
            await state.update_data(pending_commitment_token=token)
            await callback.message.answer(
                t("public_khatms.commitment_consent_prompt", lang),
                reply_markup=commitment_consent_keyboard(token, lang),
            )
        else:
            await resume_join_after_registration(
                callback.message, session, user.id, token, state=state, consent_accepted=True
            )
    await callback.answer()
