from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

from khatmsaz.bot.handlers.registration import (
    IRAN_PROVINCES,
    OUTSIDE_IRAN,
    _phone_keyboard,
    _province_keyboard,
    _gender_keyboard,
)
from khatmsaz.bot.keyboards import bail_if_menu_button, member_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings.models import Gender
from khatmsaz.modules.phone import service as phone_service
from khatmsaz.modules.settings import service as settings_service

router = Router(name="member_registration")

class MemberRegistration(StatesGroup):
    entering_name = State()
    entering_phone = State()
    choosing_province = State()
    entering_city = State()
    choosing_gender = State()


async def start_member_registration(message: Message, state: FSMContext, *, pending_join_token: str | None) -> None:
    bot = message.bot
    lang = getattr(bot, "khatmsaz_language", "fa")
    await state.update_data(pending_join_token=pending_join_token)
    await state.set_state(MemberRegistration.entering_name)
    await message.answer(t("registration.ask_name", lang))


@router.message(MemberRegistration.entering_name)
async def enter_name(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    name = (message.text or "").strip()
    lang = getattr(message.bot, "khatmsaz_language", "fa")
    if not name:
        await message.answer(t("registration.name_required", lang))
        return
    await state.update_data(full_name=name)
    await state.set_state(MemberRegistration.entering_phone)
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    ask_key = "registration.ask_phone_share_only" if platform == Platform.TELEGRAM else "registration.ask_phone"
    await message.answer(
        t(ask_key, lang, share_button=t("registration.share_phone", lang)),
        reply_markup=_phone_keyboard(lang),
    )


@router.message(MemberRegistration.entering_phone, F.contact)
async def receive_shared_contact(message: Message, state: FSMContext) -> None:
    lang = getattr(message.bot, "khatmsaz_language", "fa")
    try:
        phone = phone_service.normalize_e164(message.contact.phone_number)
    except phone_service.OtpError:
        await message.answer(t("registration.shared_phone_invalid", lang))
        return
    await state.update_data(phone=phone)
    if not phone.startswith("+98"):
        await state.update_data(foreign_verified_phone=True)
    await state.set_state(MemberRegistration.choosing_province)
    await message.answer(t("registration.phone_saved", lang), reply_markup=ReplyKeyboardRemove())
    await message.answer(t("registration.ask_province", lang), reply_markup=_province_keyboard(lang))


@router.message(MemberRegistration.entering_phone)
async def enter_phone(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = getattr(message.bot, "khatmsaz_language", "fa")
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if platform == Platform.TELEGRAM:
        await message.answer(
            t("registration.use_share_button_only", lang, share_button=t("registration.share_phone", lang)),
            reply_markup=_phone_keyboard(lang),
        )
        return
    try:
        phone = phone_service.normalize_e164((message.text or "").strip())
    except phone_service.OtpError:
        await message.answer(t("registration.phone_invalid", lang))
        return
    await state.update_data(phone=phone)
    await state.set_state(MemberRegistration.choosing_province)
    await message.answer(t("registration.phone_saved", lang), reply_markup=ReplyKeyboardRemove())
    await message.answer(t("registration.ask_province", lang), reply_markup=_province_keyboard(lang))


@router.callback_query(F.data.startswith("reg:province:"), MemberRegistration.choosing_province)
async def choose_province(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 2)[2]
    province = OUTSIDE_IRAN if value == "outside" else IRAN_PROVINCES[int(value)]
    await state.update_data(province=province)
    await state.set_state(MemberRegistration.entering_city)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    lang = getattr(callback.message.bot, "khatmsaz_language", "fa")
    await callback.message.answer(t("registration.ask_city", lang))
    await callback.answer()


@router.message(MemberRegistration.entering_city)
async def enter_city(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    city = (message.text or "").strip()
    lang = getattr(message.bot, "khatmsaz_language", "fa")
    if not city:
        await message.answer(t("registration.city_required", lang))
        return
    await state.update_data(city=city)
    await state.set_state(MemberRegistration.choosing_gender)
    await message.answer(
        t("registration.ask_gender", lang),
        reply_markup=_gender_keyboard(lang),
    )


@router.callback_query(F.data.startswith("reg:gender:"), MemberRegistration.choosing_gender)
async def choose_gender(callback: CallbackQuery, state: FSMContext) -> None:
    gender = Gender(callback.data.split(":", 2)[2])
    data = await state.get_data()
    lang = getattr(callback.message.bot, "khatmsaz_language", "fa")

    async with session_scope() as session:
        user = await identity_service.find_by_platform(
            session,
            getattr(callback.message.bot, "khatmsaz_platform"),
            str(callback.from_user.id),
        )
        await identity_service.set_display_name(session, user.id, data["full_name"])
        await settings_service.save_profile(
            session,
            user.id,
            contact_phone=data["phone"],
            province=data["province"],
            city=data["city"],
            gender=gender,
        )
        if data.get("foreign_verified_phone"):
            from khatmsaz.modules.phone import repository as phone_repository
            await phone_repository.create_or_verify_claim(session, user_id=user.id, e164=data["phone"])
            
        pending_token = data.get("pending_join_token")
        user_id = user.id

    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.answer()

    if pending_token:
        from khatmsaz.bot.handlers.start import resume_join_after_registration
        async with session_scope() as session:
            await resume_join_after_registration(callback.message, session, user_id, pending_token, state=state)
    else:
        await callback.message.answer(t("registration.completed", lang), reply_markup=member_menu_keyboard(lang))
