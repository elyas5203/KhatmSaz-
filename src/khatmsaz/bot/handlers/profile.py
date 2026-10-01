"""Short profile editing flow required by the original specification."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from khatmsaz.bot.handlers.registration import _phone_keyboard
from khatmsaz.bot.iran_provinces import IRAN_PROVINCES, OUTSIDE_IRAN, province_labels
from khatmsaz.bot.keyboards import bail_if_menu_button
from khatmsaz.bot.navigation import resolve_home_navigation
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import Gender
from khatmsaz.modules.phone import service as phone_service
from khatmsaz.modules.phone import repository as phone_repository
from khatmsaz.i18n import t

router = Router(name="profile")


class ProfileEdit(StatesGroup):
    entering_name = State()
    entering_phone = State()
    choosing_province = State()
    entering_city = State()
    choosing_gender = State()


async def _profile_prompt(message: Message, state: FSMContext, text: str, reply_markup=None) -> Message:
    """Replace the completed profile question and remove the typed answer."""
    data = await state.get_data()
    previous = data.get("_profile_mid")
    error_mid = data.get("_profile_error_mid")
    if getattr(getattr(message, "from_user", None), "is_bot", True) is False:
        try:
            await message.bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
    if previous:
        try:
            await message.bot.delete_message(message.chat.id, previous)
        except Exception:
            pass
    if error_mid:
        try:
            await message.bot.delete_message(message.chat.id, error_mid)
        except Exception:
            pass
    sent = await message.answer(text, reply_markup=reply_markup)
    await state.update_data(_profile_mid=sent.message_id, _profile_error_mid=None)
    return sent


async def _delete_profile_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    mids = [data.get("_profile_mid"), data.get("_profile_error_mid"), *data.get("_profile_cleanup_mids", [])]
    for mid in mids:
        if not mid:
            continue
        try:
            await message.bot.delete_message(message.chat.id, mid)
        except Exception:
            pass


async def _profile_error(message: Message, state: FSMContext, text: str) -> None:
    data = await state.get_data()
    for mid in (getattr(message, "message_id", None), data.get("_profile_error_mid")):
        if mid:
            try:
                await message.bot.delete_message(message.chat.id, mid)
            except Exception:
                pass
    sent = await message.answer(text)
    await state.update_data(_profile_error_mid=sent.message_id)


def _province_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    # Same 2-per-row pairing as registration.py's province keyboard (owner
    # request, 2026-09-20) — one-per-row made 31 provinces feel endless.
    # Three columns are intentionally avoided because long labels can be
    # truncated on narrow Telegram clients (owner condition, 2026-09-28).
    buttons = [InlineKeyboardButton(text=p, callback_data=f"profile:province:{i}") for i, p in enumerate(province_labels(lang))]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text=t("registration.outside_iran", lang), callback_data="profile:province:outside")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _gender_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t("registration.gender_male", lang), callback_data="profile:gender:MALE"),
        InlineKeyboardButton(text=t("registration.gender_female", lang), callback_data="profile:gender:FEMALE"),
    ]])


async def begin_profile(message: Message, state: FSMContext, *, cleanup_message_ids: list[int] | None = None) -> None:
    await state.clear()
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
    await state.update_data(language=lang, _profile_cleanup_mids=cleanup_message_ids or [])
    await state.set_state(ProfileEdit.entering_name)
    await _profile_prompt(message, state, t("profile.ask_name", lang))


@router.message(F.text == "/profile")
async def start_profile(message: Message, state: FSMContext) -> None:
    await begin_profile(message, state)


@router.message(ProfileEdit.entering_name, ~F.text.startswith("/"))
async def enter_name(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    value = (message.text or "").strip()
    lang = (await state.get_data()).get("language", "fa")
    if not value:
        await _profile_error(message, state, t("registration.name_required", lang))
        return
    await state.update_data(full_name=value)
    await state.set_state(ProfileEdit.entering_phone)
    await _profile_prompt(message, state, t("profile.ask_phone", lang), reply_markup=_phone_keyboard(lang))


@router.message(ProfileEdit.entering_phone, ~F.text.startswith("/"))
async def enter_phone(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data()).get("language", "fa")
    if message.contact:
        phone = message.contact.phone_number
    else:
        if await bail_if_menu_button(message, state):
            return
        phone = (message.text or "").strip()
    try:
        phone = phone_service.normalize_e164(phone)
    except phone_service.OtpError:
        await _profile_error(message, state, t("registration.phone_invalid", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(
            session, platform, str(message.chat.id)
        )
        verified = (
            await phone_repository.verified_claim_for_user(session, user.id)
            if user is not None
            else None
        )
    if verified is not None and verified.e164 != phone:
        await state.clear()
        _lang, _role, keyboard = await resolve_home_navigation(message, lang)
        await message.answer(
            t("profile.verified_phone_locked", lang),
            reply_markup=keyboard,
        )
        return
    await state.update_data(phone=phone)
    await state.set_state(ProfileEdit.choosing_province)
    await _profile_prompt(
        message, state, t("registration.ask_province", lang),
        reply_markup=_province_keyboard(lang),
    )


@router.callback_query(F.data.startswith("profile:province:"), ProfileEdit.choosing_province)
async def choose_province(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 2)[2]
    province = OUTSIDE_IRAN if value == "outside" else IRAN_PROVINCES[int(value)]
    await state.update_data(province=province)
    await state.set_state(ProfileEdit.entering_city)
    lang = (await state.get_data()).get("language", "fa")
    await _profile_prompt(callback.message, state, t("registration.ask_city", lang))
    await callback.answer()


@router.message(ProfileEdit.entering_city, ~F.text.startswith("/"))
async def enter_city(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    value = (message.text or "").strip()
    lang = (await state.get_data()).get("language", "fa")
    if not value:
        await _profile_error(message, state, t("registration.city_required", lang))
        return
    await state.update_data(city=value)
    await state.set_state(ProfileEdit.choosing_gender)
    await _profile_prompt(
        message, state,
        t("registration.ask_gender", lang),
        reply_markup=_gender_keyboard(lang),
    )


@router.callback_query(F.data.startswith("profile:gender:"), ProfileEdit.choosing_gender)
async def choose_gender(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "fa")
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if user is None:
            await callback.answer(t("profile.user_not_found", lang), show_alert=True)
            return
        await identity_service.set_display_name(session, user.id, data["full_name"])
        await settings_service.save_profile(session, user.id, contact_phone=data["phone"], province=data["province"], city=data["city"], gender=Gender(callback.data.split(":", 2)[2]))
    await _delete_profile_prompt(callback.message, state)
    await callback.answer()

    # Owner-reported bug (2026-09-21/22): if this profile completion was
    # itself triggered mid-way through creating a khatm (see
    # create_khatm.py's `ensure_creator_phone_verified` call), don't just
    # say "profile updated" and drop them at the main menu — continue on
    # to phone verification (still needed) or finish creating the khatm.
    from khatmsaz.bot.handlers.create_khatm import resume_khatm_creation_if_pending
    if await resume_khatm_creation_if_pending(callback.message, state):
        return
    await state.clear()
    _lang, _role, keyboard = await resolve_home_navigation(callback.message, lang)
    await callback.message.answer(t("profile.updated", lang), reply_markup=keyboard)
