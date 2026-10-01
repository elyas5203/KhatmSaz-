"""Self-service verified phone replacement that keeps all account history."""

from uuid import UUID

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from khatmsaz.bot.keyboards import bail_if_menu_button, main_menu_keyboard
from khatmsaz.bot.handlers.manual_phone_verification import notify_admins_of_manual_request
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.manual_phone_verification import service as manual_phone_service
from khatmsaz.modules.phone import service as phone_service
from khatmsaz.modules.phone import repository as phone_repository
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.sms.provider import build_provider

router = Router(name="change_phone")


class ChangePhone(StatesGroup):
    entering_phone = State()
    entering_code = State()


async def _remember_otp_prompt(message: Message, state: FSMContext, text: str) -> None:
    sent = await message.answer(text)
    await state.update_data(_phone_verify_mid=getattr(sent, "message_id", None))


async def _remove_otp_exchange(message: Message, data: dict) -> None:
    """Remove the OTP question and typed code after verification completes."""
    try:
        await message.delete()
    except Exception:
        pass
    prompt_id = data.get("_phone_verify_mid")
    if prompt_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_id)
        except Exception:
            pass


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


async def ensure_creator_phone_verified(message: Message, state: FSMContext) -> bool:
    """Return true when creation may continue; otherwise start the OTP step."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    settings = get_settings()
    manual_request = None
    lang = "fa"
    try:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(
                session, platform, str(message.chat.id)
            )
            profile = await settings_service.get_or_create(session, user.id)
            lang = profile.language
            if not (
                user.display_name
                and profile.contact_phone
                and profile.province
                and profile.city
                and profile.gender
            ):
                from khatmsaz.bot.handlers.profile import begin_profile

                await message.answer(t("change_phone.complete_profile_first", lang))
                await begin_profile(message, state)
                return False
            claim = await phone_repository.verified_claim_for_user(session, user.id)
            if claim is not None:
                return True
            phone = phone_service.normalize_e164(profile.contact_phone)
            if manual_phone_service.requires_manual_review(phone):
                request, created = await manual_phone_service.submit(
                    session,
                    user_id=user.id,
                    e164=phone,
                    purpose="CREATOR_VERIFY",
                )
                manual_request = (request.id, user.display_name, phone, created)
            else:
                challenge, code = await phone_service.request_phone_change_challenge(
                    session, user_id=user.id, e164=phone
                )
                user_id = user.id
                challenge_id = challenge.id
                phone = challenge.e164
    except (phone_service.OtpError, manual_phone_service.ManualVerificationError) as exc:
        await state.clear()
        if str(exc) == "phone belongs to another account":
            text = t("change_phone.phone_taken", lang)
        else:
            text = t("change_phone.currently_unavailable", lang)
        await message.answer(text, reply_markup=main_menu_keyboard(lang))
        return False

    if manual_request is not None:
        request_id, display_name, phone, created = manual_request
        await state.clear()
        if created:
            await notify_admins_of_manual_request(
                request_id=request_id,
                display_name=display_name,
                e164=phone,
                purpose="CREATOR_VERIFY",
            )
        await message.answer(
            t("change_phone.manual_review_creator", lang),
            reply_markup=main_menu_keyboard(lang),
        )
        return False

    if code is not None:
        result = await build_provider(settings).send(
            phone=phone,
            text=t("change_phone.otp_sms_text", lang, code=code),
            sender=settings.sms_sender or None,
            otp_code=code,
        )
        if not result.accepted and not settings.dev_otp:
            await state.clear()
            await message.answer(
                t("change_phone.sms_gateway_down_creator", lang),
                reply_markup=main_menu_keyboard(lang),
            )
            return False

    await state.update_data(
        user_id=str(user_id),
        challenge_id=str(challenge_id),
        verification_context="creator",
        lang=lang,
    )
    await state.set_state(ChangePhone.entering_code)
    text = t("change_phone.ask_creator_otp", lang)
    if settings.dev_otp and code is not None:
        text += t("change_phone.dev_otp_hint", lang, code=code)
    await _remember_otp_prompt(message, state, text)
    return False


@router.message(Command("verify_phone"))
async def verify_creator_phone(message: Message, state: FSMContext) -> None:
    await state.clear()
    if await ensure_creator_phone_verified(message, state):
        lang = await _lang_for(message.chat.id, message.bot)
        await message.answer(
            t("change_phone.already_verified", lang),
            reply_markup=main_menu_keyboard(lang),
        )


@router.message(Command("change_phone"))
async def begin_phone_change(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    await state.clear()
    await state.set_state(ChangePhone.entering_phone)
    await state.update_data(lang=lang)
    await message.answer(t("change_phone.begin_prompt", lang))


@router.message(ChangePhone.entering_phone)
async def receive_new_phone(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    settings = get_settings()
    manual_request = None
    try:
        async with session_scope() as session:
            user = await identity_service.find_by_platform(
                session, platform, str(message.chat.id)
            )
            if user is None:
                raise phone_service.OtpError("account not found")
            phone = phone_service.normalize_e164((message.text or "").strip())
            if manual_phone_service.requires_manual_review(phone):
                request, created = await manual_phone_service.submit(
                    session,
                    user_id=user.id,
                    e164=phone,
                    purpose="PHONE_CHANGE",
                )
                manual_request = (request.id, user.display_name, phone, created)
            else:
                challenge, code = await phone_service.request_phone_change_challenge(
                    session, user_id=user.id, e164=phone
                )
                user_id = user.id
                challenge_id = challenge.id
                phone = challenge.e164
    except (phone_service.OtpError, manual_phone_service.ManualVerificationError) as exc:
        if str(exc) == "phone belongs to another account":
            text = t("change_phone.phone_taken_secure", lang)
        elif str(exc) == "phone is already verified for this account":
            text = t("change_phone.already_verified_same", lang)
        else:
            text = t("change_phone.invalid_or_locked", lang)
        await state.clear()
        await message.answer(text, reply_markup=main_menu_keyboard(lang))
        return

    if manual_request is not None:
        request_id, display_name, phone, created = manual_request
        await state.clear()
        if created:
            await notify_admins_of_manual_request(
                request_id=request_id,
                display_name=display_name,
                e164=phone,
                purpose="PHONE_CHANGE",
            )
        await message.answer(
            t("change_phone.manual_review_change", lang),
            reply_markup=main_menu_keyboard(lang),
        )
        return

    if code is not None:
        result = await build_provider(settings).send(
            phone=phone,
            text=t("change_phone.otp_sms_text_change", lang, code=code),
            sender=settings.sms_sender or None,
            otp_code=code,
        )
        if not result.accepted and not settings.dev_otp:
            await state.clear()
            await message.answer(
                t("change_phone.sms_gateway_down_change", lang),
                reply_markup=main_menu_keyboard(lang),
            )
            return

    await state.update_data(
        user_id=str(user_id), challenge_id=str(challenge_id), verification_context="change", lang=lang
    )
    await state.set_state(ChangePhone.entering_code)
    text = t("change_phone.ask_change_otp", lang)
    if settings.dev_otp and code is not None:
        text += t("change_phone.dev_otp_hint", lang, code=code)
    await _remember_otp_prompt(message, state, text)


@router.message(ChangePhone.entering_code)
async def receive_change_code(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    code = (message.text or "").strip()
    if len(code) != 6 or not code.isdigit():
        try:
            await message.delete()
        except Exception:
            pass
        prompt_id = data.get("_phone_verify_mid")
        retry = f"⚠️ {t('change_phone.code_must_be_six_digits', lang)}\n\n{t('change_phone.ask_creator_otp' if data.get('verification_context') == 'creator' else 'change_phone.ask_change_otp', lang)}"
        if prompt_id:
            try:
                await message.bot.edit_message_text(chat_id=message.chat.id, message_id=prompt_id, text=retry)
                return
            except Exception:
                pass
        await _remember_otp_prompt(message, state, retry)
        return
    try:
        async with session_scope() as session:
            claim = await phone_service.complete_phone_change(
                session,
                user_id=UUID(data["user_id"]),
                challenge_id=UUID(data["challenge_id"]),
                code=code,
            )
            phone = claim.e164
    except phone_service.OtpError as exc:
        if str(exc) != "invalid code":
            await state.clear()
        await message.answer(t("change_phone.otp_invalid_or_expired", lang))
        return
    except (KeyError, ValueError):
        await state.clear()
        await message.answer(t("change_phone.request_data_lost", lang))
        return

    await _remove_otp_exchange(message, data)

    # Owner-reported bug (2026-09-21/22): if this OTP verification was
    # itself triggered mid-way through creating a khatm, don't just say
    # "phone verified" and drop them at the main menu — actually finish
    # creating the khatm now that the phone is verified.
    from khatmsaz.bot.handlers.create_khatm import resume_khatm_creation_if_pending
    if await resume_khatm_creation_if_pending(message, state):
        return

    await state.clear()
    if data.get("verification_context") == "creator":
        text = t("change_phone.creator_verified_success", lang, phone=phone)
    else:
        text = t("change_phone.number_changed_success", lang, phone=phone)
    await message.answer(text, reply_markup=main_menu_keyboard(lang))
