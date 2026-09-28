"""Short first-join registration (DOMAIN_MODEL.md §1): name → phone
(unverified, trust-based) → province → city → gender. Triggered from
`start.py`'s join flow the first time an unregistered participant taps a
join link — never at bare `/start`, matching the spec's "show khatm info
first, register only after they choose to join" order.

Registration fields:
  - display_name lives on `User` (identity module).
  - phone/province/city/gender live on `UserSettings` (settings module).
Province is a picklist of the 31 official Iranian provinces; city is free
text for everyone (DECISIONS.md DEC-PY-0015 — a full province→city dataset
would be large and error-prone to hand-write, so this is a deliberate
scoping choice, not an oversight).
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from khatmsaz.bot.iran_provinces import IRAN_PROVINCES, OUTSIDE_IRAN, province_labels
from khatmsaz.bot.keyboards import bail_if_menu_button, main_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import Gender
from khatmsaz.modules.phone import service as phone_service
from khatmsaz.i18n import t
from khatmsaz.modules.identity.models import Platform

router = Router(name="registration")


class Registration(StatesGroup):
    entering_name = State()
    entering_phone = State()
    choosing_province = State()
    entering_city = State()
    choosing_gender = State()


def _province_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    # Owner request (2026-09-20): 31 one-per-row buttons made this list feel
    # endless to scroll; pairing two provinces per row roughly halves its
    # height without shrinking any single button's tap target.
    buttons = [InlineKeyboardButton(text=p, callback_data=f"reg:province:{i}") for i, p in enumerate(province_labels(lang))]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text=t("registration.outside_iran", lang), callback_data="reg:province:outside")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _phone_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    """Telegram-only feature: a "share my number" button next to the option
    to just type it. `request_contact` isn't supported by Bale's Bot API as
    far as documented, so a Bale user always sees the plain typing path —
    the handler below accepts either regardless of platform."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("registration.share_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _gender_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("registration.gender_male", lang), callback_data="reg:gender:MALE"),
                InlineKeyboardButton(text=t("registration.gender_female", lang), callback_data="reg:gender:FEMALE"),
            ]
        ]
    )


async def start_registration(message: Message, state: FSMContext, *, pending_join_token: str | None) -> None:
    """Called by `start.py` when an unregistered participant tries to join."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
    await state.update_data(pending_join_token=pending_join_token, language=lang)
    await state.set_state(Registration.entering_name)
    await message.answer(t("registration.ask_name", lang))


@router.message(Registration.entering_name)
async def enter_name(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    name = (message.text or "").strip()
    lang = (await state.get_data()).get("language", "fa")
    if not name or name.startswith("/"):
        await message.answer(t("registration.name_required", lang))
        return
    await state.update_data(full_name=name)
    await state.set_state(Registration.entering_phone)
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    ask_key = "registration.ask_phone_share_only" if platform == Platform.TELEGRAM else "registration.ask_phone"
    await message.answer(
        t(ask_key, lang, share_button=t("registration.share_phone", lang)),
        reply_markup=_phone_keyboard(lang),
    )


@router.message(Registration.entering_phone, F.contact)
async def receive_shared_contact(message: Message, state: FSMContext) -> None:
    lang = (await state.get_data()).get("language", "fa")
    try:
        phone = phone_service.normalize_e164(message.contact.phone_number)
    except phone_service.OtpError:
        await message.answer(t("registration.shared_phone_invalid", lang))
        return
    await state.update_data(phone=phone)
    if not phone.startswith("+98"):
        await state.update_data(foreign_verified_phone=True)
    await state.set_state(Registration.choosing_province)
    # Two messages are unavoidable here: Telegram can't attach both a
    # ReplyKeyboardRemove (clears the "share my number" button) and an
    # InlineKeyboardMarkup to the same message.
    await message.answer(t("registration.phone_saved", lang), reply_markup=ReplyKeyboardRemove())
    await message.answer(t("registration.ask_province", lang), reply_markup=_province_keyboard(lang))


@router.message(Registration.entering_phone)
async def enter_phone(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = (await state.get_data()).get("language", "fa")
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if platform == Platform.TELEGRAM:
        # Owner request (2026-09-22): during initial registration on
        # Telegram, only the "share my number" button should work — no
        # manually typed number — since a self-typed number is more
        # error-prone (typos, wrong format) than Telegram's own verified
        # contact-share. Bale has no `request_contact` equivalent (see
        # `_phone_keyboard`'s docstring), so Bale users still must type.
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
    await state.set_state(Registration.choosing_province)
    await message.answer(t("registration.phone_saved", lang), reply_markup=ReplyKeyboardRemove())
    await message.answer(t("registration.ask_province", lang), reply_markup=_province_keyboard(lang))


@router.callback_query(F.data.startswith("reg:province:"), Registration.choosing_province)
async def choose_province(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 2)[2]
    province = OUTSIDE_IRAN if value == "outside" else IRAN_PROVINCES[int(value)]
    await state.update_data(province=province)
    await state.set_state(Registration.entering_city)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    lang = (await state.get_data()).get("language", "fa")
    await callback.message.answer(t("registration.ask_city", lang))
    await callback.answer()


@router.message(Registration.entering_city)
async def enter_city(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    city = (message.text or "").strip()
    lang = (await state.get_data()).get("language", "fa")
    if not city:
        await message.answer(t("registration.city_required", lang))
        return
    await state.update_data(city=city)
    await state.set_state(Registration.choosing_gender)
    await message.answer(
        t("registration.ask_gender", lang),
        reply_markup=_gender_keyboard(lang),
    )


@router.callback_query(F.data.startswith("reg:gender:"), Registration.choosing_gender)
async def choose_gender(callback: CallbackQuery, state: FSMContext) -> None:
    gender = Gender(callback.data.split(":", 2)[2])
    data = await state.get_data()
    lang = data.get("language", "fa")

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
        # Deferred import to avoid a circular import (start.py triggers
        # registration; registration resumes start.py's join logic).
        from khatmsaz.bot.handlers.start import resume_join_after_registration

        async with session_scope() as session:
            await resume_join_after_registration(callback.message, session, user_id, pending_token, state=state)
    else:
        # Owner request (2026-09-23): after registration without a pending
        # join, automatically open the khatm creation wizard — this is why
        # the user registered, so don't make them hunt for the button.
        await callback.message.answer(t("registration.completed", lang))
        from khatmsaz.bot.handlers.create_khatm import start_wizard
        await start_wizard(callback.message, state)
