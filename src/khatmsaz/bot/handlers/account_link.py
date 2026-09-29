"""Self-service OTP flow for linking a new platform/chat to an existing user."""

from uuid import UUID

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from khatmsaz.bot.keyboards import bail_if_menu_button, main_menu_keyboard
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.phone import service as phone_service
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.sms.provider import build_provider

router = Router(name="account_link")


class AccountLink(StatesGroup):
    entering_phone = State()
    entering_code = State()


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


@router.message(Command("link_account"))
async def begin_account_link(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await state.clear()
    await state.set_state(AccountLink.entering_phone)
    await state.update_data(lang=lang)
    await message.answer(t("account_link.begin_prompt", lang))


@router.message(AccountLink.entering_phone)
async def receive_link_phone(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw_phone = (message.text or "").strip()
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    settings = get_settings()
    try:
        async with session_scope() as session:
            source = await identity_service.resolve_or_provision_user(
                session, platform, message.chat.id
            )
            target, challenge, code = await phone_service.request_account_link_challenge(
                session, source_user_id=source.id, e164=raw_phone
            )
            source_id = source.id
            target_id = target.id
            challenge_id = challenge.id
            phone = challenge.e164
    except phone_service.OtpError:
        await state.clear()
        await message.answer(
            t("account_link.no_account_found", lang),
            reply_markup=main_menu_keyboard(lang),
        )
        return

    if code is not None:
        provider = build_provider(settings)
        result = await provider.send(
            phone=phone,
            text=t("account_link.otp_sms_text", lang, code=code),
            sender=settings.sms_sender or None,
            otp_code=code,
        )
        if not result.accepted and not settings.dev_otp:
            await state.clear()
            await message.answer(
                t("account_link.sms_gateway_down", lang),
                reply_markup=main_menu_keyboard(lang),
            )
            return

    await state.update_data(
        source_user_id=str(source_id),
        target_user_id=str(target_id),
        challenge_id=str(challenge_id),
        lang=lang,
    )
    await state.set_state(AccountLink.entering_code)
    text = t("account_link.ask_otp", lang)
    if settings.dev_otp and code is not None:
        text += t("account_link.dev_otp_hint", lang, code=code)
    await message.answer(text)


@router.message(AccountLink.entering_code)
async def receive_link_code(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    code = (message.text or "").strip()
    if len(code) != 6 or not code.isdigit():
        await message.answer(t("account_link.code_must_be_six_digits", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        async with session_scope() as session:
            target = await phone_service.complete_account_link(
                session,
                source_user_id=UUID(data["source_user_id"]),
                target_user_id=UUID(data["target_user_id"]),
                challenge_id=UUID(data["challenge_id"]),
                code=code,
                platform=platform,
                subject=str(message.chat.id),
            )
            display_name = target.display_name or t("account_link.default_display_name", lang)
    except phone_service.OtpError as exc:
        if str(exc) != "invalid code":
            await state.clear()
        await message.answer(t("account_link.otp_invalid_or_expired", lang))
        return
    except (KeyError, ValueError):
        await state.clear()
        await message.answer(t("account_link.data_lost", lang))
        return
    await state.clear()
    await message.answer(
        t("account_link.success", lang, name=display_name),
        reply_markup=main_menu_keyboard(lang),
    )
