"""Khatm creation wizard — a short multi-step conversation.

Flow: **commitment mode (تعهدی/آزاد) → content template → title → niyyat
(optional) → template+mode-specific config → confirm → create + activate +
generate invite link.** Commitment mode is asked first and independently of
the content template (DOMAIN_MODEL.md §2, DEC-PY-0007) — a creator can make
a committed Quran khatm, a committed Salawat khatm, an open Quran khatm, or
an open Salawat khatm; the two questions don't determine each other.

Business logic lives in `khatm_workflow.service`; this file only drives the
conversation and formats text (ARCHITECTURE.md's "handlers hold no business
logic" rule). The user's language is resolved once at wizard start and
carried in FSM state (`lang`) for the rest of the flow — see
docs/ai/I18N_MIGRATION.md for why this pattern is required.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from datetime import datetime
from zoneinfo import ZoneInfo

from khatmsaz.bot.keyboards import (
    CREATE_BUTTON_TEXTS,
    bail_if_menu_button,
    capacity_choice_keyboard,
    category_choice_keyboard,
    commitment_mode_keyboard,
    confirm_keyboard,
    coupon_entry_keyboard,
    content_delivery_mode_keyboard,
    creator_display_keyboard,
    start_schedule_keyboard,
    reminder_tone_keyboard,
    edition_choice_keyboard,
    main_menu_keyboard,
    safe_answer_callback,
    safe_clear_inline_keyboard,
    skip_niyyat_keyboard,
    template_choice_keyboard,
    visibility_choice_keyboard,
)
from khatmsaz.bot.handlers.change_phone import ensure_creator_phone_verified
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm.models import ContentDeliveryMode, CreatorDisplayMode, KhatmTemplateType, KhatmTypeEnum, KhatmVisibility, ReminderTone
from khatmsaz.modules.khatm.quran_editions import QURAN_EDITIONS
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.service import InsufficientFundsError

router = Router(name="create_khatm")


class CreateKhatm(StatesGroup):
    choosing_template = State()
    choosing_category = State()
    entering_custom_dua_title = State()
    choosing_mode = State()
    entering_title = State()
    entering_niyyat = State()
    entering_welcome = State()
    entering_recitation_text = State()
    entering_open_target = State()
    entering_commitment_quantity = State()
    choosing_edition = State()
    choosing_content_delivery_mode = State()
    entering_deadline_hour = State()
    choosing_capacity_mode = State()
    entering_capacity_number = State()
    choosing_visibility = State()
    choosing_reminder_tone = State()
    choosing_creator_display = State()
    entering_creator_pseudonym = State()
    choosing_start_schedule = State()
    entering_start_at = State()
    entering_coupon = State()
    confirming = State()


async def _resolve_lang(message: Message) -> str:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


async def _lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("lang", "fa")


@router.message(F.text.in_(CREATE_BUTTON_TEXTS))
async def start_wizard(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not await ensure_creator_phone_verified(message, state):
        return
    lang = await _resolve_lang(message)
    await state.update_data(lang=lang)
    await state.set_state(CreateKhatm.choosing_template)
    await message.answer(t("create_khatm.ask_template", lang), reply_markup=template_choice_keyboard())


@router.message(Command("new_khatm"))
async def start_wizard_command(message: Message, state: FSMContext) -> None:
    await start_wizard(message, state)


@router.callback_query(F.data.startswith("ck:tpl:"), StateFilter(CreateKhatm.choosing_template))
async def choose_template(callback: CallbackQuery, state: FSMContext) -> None:
    template_name = callback.data.split(":")[2]
    await state.update_data(template_type=template_name)
    await safe_clear_inline_keyboard(callback.message)
    if template_name == KhatmTemplateType.SALAWAT.value:
        # Compatibility for buttons sent before devotional families became
        # separate top-level choices: old SALAWAT buttons now open only the
        # Salawat family, never Dua or La'an children.
        await _show_category_group(callback, state, KhatmCategoryGroup.SALAWAT)
        return
    # QURAN_PAGE has no subcategory step — ask commitment/free right away.
    await _ask_mode(callback.message, state)
    await safe_answer_callback(callback)


_CATEGORY_GROUP_PROMPT_KEYS = {
    KhatmCategoryGroup.SALAWAT: "create_khatm.category_prompt.SALAWAT",
    KhatmCategoryGroup.DUA: "create_khatm.category_prompt.DUA",
    KhatmCategoryGroup.LAAN: "create_khatm.category_prompt.LAAN",
}


@router.callback_query(F.data.startswith("ck:group:"), StateFilter(CreateKhatm.choosing_template))
async def choose_category_group(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    try:
        group = KhatmCategoryGroup(callback.data.split(":", 2)[2])
    except (ValueError, IndexError):
        await safe_answer_callback(callback, t("create_khatm.category_gone", lang), show_alert=True)
        return
    await _show_category_group(callback, state, group)


async def _show_category_group(
    callback: CallbackQuery, state: FSMContext, group: KhatmCategoryGroup
) -> None:
    lang = await _lang(state)
    async with session_scope() as session:
        categories = await category_service.list_active(session, group)
    await state.update_data(
        template_type=KhatmTemplateType.SALAWAT.value,
        category_group=group.value,
        content_category_id=None,
        content_category_title=None,
    )
    await state.set_state(CreateKhatm.choosing_category)
    await safe_clear_inline_keyboard(callback.message)
    if not categories and group != KhatmCategoryGroup.DUA:
        await callback.message.answer(t("create_khatm.category_empty", lang))
        await safe_answer_callback(callback)
        return
    await callback.message.answer(
        t(_CATEGORY_GROUP_PROMPT_KEYS[group], lang),
        reply_markup=category_choice_keyboard(
            categories,
            group=group.value,
            allow_custom_request=group == KhatmCategoryGroup.DUA,
        ),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data == "ck:cat:custom", StateFilter(CreateKhatm.choosing_category))
async def choose_custom_category(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    if data.get("category_group") != KhatmCategoryGroup.DUA.value:
        await safe_answer_callback(callback, t("create_khatm.custom_request_dua_only", lang), show_alert=True)
        return
    await safe_clear_inline_keyboard(callback.message)
    await state.set_state(CreateKhatm.entering_custom_dua_title)
    await callback.message.answer(t("create_khatm.ask_custom_dua_title", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(CreateKhatm.entering_custom_dua_title))
async def enter_custom_dua_title(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    title = (message.text or "").strip()
    if not title:
        await message.answer(t("create_khatm.custom_dua_title_required", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        try:
            await category_service.submit_request(session, requested_title=title, requested_by_user_id=user.id)
        except ValueError:
            await message.answer(t("create_khatm.custom_dua_title_too_long", lang))
            return
    await state.clear()
    await message.answer(
        t("create_khatm.custom_dua_submitted", lang, title=title),
        reply_markup=main_menu_keyboard(lang),
    )


@router.callback_query(F.data.startswith("ck:cat:"), StateFilter(CreateKhatm.choosing_category))
async def choose_category(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    category_id = callback.data.split(":", 2)[2]
    data = await state.get_data()
    expected_group = data.get("category_group")
    async with session_scope() as session:
        category = await category_service.get(session, category_id)
        if (
            category is None
            or not category.is_active
            or category.group.value != expected_group
        ):
            await safe_answer_callback(callback, t("create_khatm.category_gone", lang), show_alert=True)
            return
    await state.update_data(
        content_category_id=str(category.id),
        content_category_title=category.title,
    )
    await safe_clear_inline_keyboard(callback.message)
    await _ask_mode(callback.message, state)
    await safe_answer_callback(callback)


_MODE_EXPLANATION_KEYS = {
    (KhatmTemplateType.QURAN_PAGE.value, None): "create_khatm.mode_explanation.quran",
    (KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.SALAWAT.value): "create_khatm.mode_explanation.salawat",
    (KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.DUA.value): "create_khatm.mode_explanation.dua",
    (KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.LAAN.value): "create_khatm.mode_explanation.laan",
}


async def _ask_mode(message: Message, state: FSMContext) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    key = (data["template_type"], data.get("category_group"))
    explanation_key = _MODE_EXPLANATION_KEYS.get(key, _MODE_EXPLANATION_KEYS[(KhatmTemplateType.QURAN_PAGE.value, None)])
    await state.set_state(CreateKhatm.choosing_mode)
    await message.answer(
        t("create_khatm.ask_mode", lang, explanation=t(explanation_key, lang)),
        reply_markup=commitment_mode_keyboard(),
    )


@router.callback_query(F.data.startswith("ck:mode:"), StateFilter(CreateKhatm.choosing_mode))
async def choose_mode(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    mode = callback.data.split(":")[2]
    await state.update_data(khatm_type=mode)
    await state.set_state(CreateKhatm.entering_title)
    await safe_clear_inline_keyboard(callback.message)
    data = await state.get_data()
    title_hint = data.get("content_category_title") or (
        t("create_khatm.title_hint.quran", lang)
        if data["template_type"] == KhatmTemplateType.QURAN_PAGE.value
        else t("create_khatm.title_hint.salawat", lang)
    )
    await callback.message.answer(t("create_khatm.ask_title", lang, hint=title_hint))
    await safe_answer_callback(callback)


@router.message(StateFilter(CreateKhatm.entering_title))
async def enter_title(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    title = (message.text or "").strip()
    if not title:
        await message.answer(t("create_khatm.title_required", lang))
        return
    await state.update_data(title=title)
    await state.set_state(CreateKhatm.entering_niyyat)
    await message.answer(
        t("create_khatm.ask_niyyat", lang),
        reply_markup=skip_niyyat_keyboard(),
    )


@router.message(StateFilter(CreateKhatm.entering_niyyat))
async def enter_niyyat(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    await state.update_data(niyyat=(message.text or "").strip() or None)
    await _ask_welcome(message, state)


@router.callback_query(F.data == "ck:skip_niyyat", StateFilter(CreateKhatm.entering_niyyat))
async def skip_niyyat(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(niyyat=None)
    await safe_clear_inline_keyboard(callback.message)
    await _ask_welcome(callback.message, state)
    await safe_answer_callback(callback)


_WELCOME_EXAMPLE_KEYS = {
    (KhatmTemplateType.QURAN_PAGE.value, None): "create_khatm.welcome_example.quran",
    (KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.SALAWAT.value): "create_khatm.welcome_example.salawat",
    (KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.DUA.value): "create_khatm.welcome_example.dua",
    (KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.LAAN.value): "create_khatm.welcome_example.laan",
}


async def _ask_welcome(message: Message, state: FSMContext) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    await state.set_state(CreateKhatm.entering_welcome)
    # Owner request (2026-09-21): show an example matching the actual
    # khatm content instead of one generic prompt for every type.
    key = (data.get("template_type"), data.get("category_group"))
    example_key = _WELCOME_EXAMPLE_KEYS.get(key, _WELCOME_EXAMPLE_KEYS[(KhatmTemplateType.QURAN_PAGE.value, None)])
    text = t("create_khatm.welcome_intro", lang) + t(example_key, lang) + t("create_khatm.welcome_suffix", lang)
    await message.answer(text, reply_markup=skip_niyyat_keyboard())


@router.message(StateFilter(CreateKhatm.entering_welcome))
async def enter_welcome(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    welcome = (message.text or "").strip()
    if len(welcome) > 500:
        await message.answer(t("create_khatm.welcome_too_long", lang))
        return
    await state.update_data(welcome_text=welcome or None)
    await _after_welcome(message, state)


@router.callback_query(F.data == "ck:skip_niyyat", StateFilter(CreateKhatm.entering_welcome))
async def skip_welcome(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(welcome_text=None)
    await safe_clear_inline_keyboard(callback.message)
    await _after_welcome(callback.message, state)
    await safe_answer_callback(callback)


async def _after_welcome(message: Message, state: FSMContext) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    # Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر
    # بخواد؛ متن صلوات همیشه ثابته — این متنی که میگه اگه متن لعن/دعا/ذکر
    # دارین، فقط باید برای لعن باشه." Plain Salawat text is fixed/standard
    # (delivered from the devotional library, never creator-authored) and
    # Dua text comes from the admin-managed `KhatmCategory` library too —
    # only La'an actually needs the creator's own wording, since there's
    # no single canonical "la'an text" to fall back to. Quran khatms don't
    # reach this step at all (real page/audio content instead).
    if data.get("category_group") == KhatmCategoryGroup.LAAN.value:
        await state.set_state(CreateKhatm.entering_recitation_text)
        await message.answer(
            t("create_khatm.ask_recitation_text", lang),
            reply_markup=skip_niyyat_keyboard(),
        )
        return
    await _after_recitation_text(message, state)


@router.message(StateFilter(CreateKhatm.entering_recitation_text))
async def enter_recitation_text(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    text = (message.text or "").strip()
    if len(text) > 3500:
        await message.answer(t("create_khatm.recitation_text_too_long", lang))
        return
    await state.update_data(recitation_text=text or None)
    await _after_recitation_text(message, state)


@router.callback_query(F.data == "ck:skip_niyyat", StateFilter(CreateKhatm.entering_recitation_text))
async def skip_recitation_text(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(recitation_text=None)
    await safe_clear_inline_keyboard(callback.message)
    await _after_recitation_text(callback.message, state)
    await safe_answer_callback(callback)


async def _after_recitation_text(message: Message, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.set_state(CreateKhatm.choosing_creator_display)
    await message.answer(
        t("create_khatm.ask_creator_display", lang),
        reply_markup=creator_display_keyboard(),
    )


@router.callback_query(F.data.startswith("ck:creator_display:"), StateFilter(CreateKhatm.choosing_creator_display))
async def choose_creator_display(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    mode = callback.data.split(":")[2]
    await state.update_data(creator_display_mode=mode)
    await safe_clear_inline_keyboard(callback.message)
    if mode == CreatorDisplayMode.PSEUDONYM.value:
        await state.set_state(CreateKhatm.entering_creator_pseudonym)
        await callback.message.answer(t("create_khatm.ask_pseudonym", lang))
    else:
        await _after_creator_display(callback.message, state)
    await safe_answer_callback(callback)


@router.message(StateFilter(CreateKhatm.entering_creator_pseudonym))
async def enter_creator_pseudonym(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    pseudonym = (message.text or "").strip()
    if not pseudonym or len(pseudonym) > 64:
        await message.answer(t("create_khatm.pseudonym_invalid", lang))
        return
    await state.update_data(creator_pseudonym=pseudonym)
    await _after_creator_display(message, state)


async def _after_creator_display(message: Message, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.set_state(CreateKhatm.choosing_start_schedule)
    await message.answer(
        t("create_khatm.ask_start_schedule", lang),
        reply_markup=start_schedule_keyboard(),
    )


async def _after_start_schedule(message: Message, state: FSMContext) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    template = data["template_type"]
    mode = data["khatm_type"]

    if template == KhatmTemplateType.SALAWAT.value and mode == KhatmTypeEnum.OPEN.value:
        await state.set_state(CreateKhatm.entering_open_target)
        unit = (
            t("create_khatm.unit.salawat", lang)
            if data.get("category_group") == KhatmCategoryGroup.SALAWAT.value
            else t("create_khatm.unit.time", lang)
        )
        title = data.get("content_category_title") or t("create_khatm.group_label.generic", lang)
        await message.answer(t("create_khatm.ask_open_target", lang, title=title, unit=unit))
    elif template == KhatmTemplateType.SALAWAT.value and mode == KhatmTypeEnum.COMMITMENT.value:
        await state.set_state(CreateKhatm.entering_commitment_quantity)
        unit = (
            t("create_khatm.unit.salawat", lang)
            if data.get("category_group") == KhatmCategoryGroup.SALAWAT.value
            else t("create_khatm.unit.time", lang)
        )
        title = data.get("content_category_title") or t("create_khatm.group_label.generic", lang)
        await message.answer(t("create_khatm.ask_commitment_quantity", lang, title=title, unit=unit))
    else:  # QURAN_PAGE, either mode
        await state.set_state(CreateKhatm.choosing_edition)
        await message.answer(t("create_khatm.ask_edition", lang), reply_markup=edition_choice_keyboard())


@router.callback_query(F.data == "ck:start:now", StateFilter(CreateKhatm.choosing_start_schedule))
async def choose_start_now(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(start_at=None)
    await safe_clear_inline_keyboard(callback.message)
    await _after_start_schedule(callback.message, state)
    await safe_answer_callback(callback)


@router.callback_query(F.data == "ck:start:future", StateFilter(CreateKhatm.choosing_start_schedule))
async def choose_start_future(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.set_state(CreateKhatm.entering_start_at)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("create_khatm.ask_start_at", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(CreateKhatm.entering_start_at))
async def enter_start_at(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    raw = (message.text or "").strip()
    try:
        start_at = datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(
            tzinfo=ZoneInfo(get_settings().app_timezone)
        )
    except ValueError:
        await message.answer(t("create_khatm.start_at_format_invalid", lang))
        return
    if start_at <= datetime.now(start_at.tzinfo):
        await message.answer(t("create_khatm.start_at_must_be_future", lang))
        return
    await state.update_data(start_at=start_at)
    await _after_start_schedule(message, state)


@router.message(StateFilter(CreateKhatm.entering_open_target))
async def enter_open_target(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("create_khatm.positive_number_required", lang))
        return
    await state.update_data(salawat_open_target=int(raw))
    await _ask_visibility(message, state)


@router.message(StateFilter(CreateKhatm.entering_commitment_quantity))
async def enter_commitment_quantity(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("create_khatm.positive_number_required", lang))
        return
    await state.update_data(salawat_commitment_quantity=int(raw))
    await state.set_state(CreateKhatm.choosing_capacity_mode)
    await message.answer(
        t("create_khatm.ask_capacity_salawat", lang),
        reply_markup=capacity_choice_keyboard(),
    )


@router.callback_query(F.data.startswith("ck:edition:"), StateFilter(CreateKhatm.choosing_edition))
async def choose_edition(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    edition_id = callback.data.split(":", 2)[2]
    await state.update_data(quran_edition_id=edition_id)
    await safe_clear_inline_keyboard(callback.message)

    await state.set_state(CreateKhatm.choosing_content_delivery_mode)
    await callback.message.answer(
        t("create_khatm.ask_content_delivery_mode", lang), reply_markup=content_delivery_mode_keyboard()
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("ck:content_mode:"), StateFilter(CreateKhatm.choosing_content_delivery_mode))
async def choose_content_delivery_mode(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    mode = callback.data.split(":")[2]
    await state.update_data(content_delivery_mode=mode)
    await safe_clear_inline_keyboard(callback.message)
    data = await state.get_data()
    if data["khatm_type"] == KhatmTypeEnum.COMMITMENT.value:
        await state.set_state(CreateKhatm.entering_deadline_hour)
        await callback.message.answer(t("create_khatm.ask_deadline_hour", lang))
    else:
        await _ask_visibility(callback.message, state)
    await safe_answer_callback(callback)


@router.message(StateFilter(CreateKhatm.entering_deadline_hour))
async def enter_deadline_hour(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    raw = (message.text or "").strip()
    if not raw.isdigit() or not (0 <= int(raw) <= 23):
        await message.answer(t("create_khatm.hour_required", lang))
        return
    await state.update_data(daily_deadline_hour=int(raw))
    await state.set_state(CreateKhatm.choosing_capacity_mode)
    await message.answer(
        t("create_khatm.ask_capacity_quran", lang),
        reply_markup=capacity_choice_keyboard(),
    )


@router.callback_query(F.data == "ck:capacity:unlimited", StateFilter(CreateKhatm.choosing_capacity_mode))
async def choose_unlimited_capacity(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(capacity=None)
    await safe_clear_inline_keyboard(callback.message)
    await _ask_visibility(callback.message, state)
    await safe_answer_callback(callback)


@router.callback_query(F.data == "ck:capacity:limited", StateFilter(CreateKhatm.choosing_capacity_mode))
async def choose_limited_capacity(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.set_state(CreateKhatm.entering_capacity_number)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("create_khatm.ask_capacity_number", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(CreateKhatm.entering_capacity_number))
async def enter_capacity_number(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("create_khatm.positive_number_required", lang))
        return
    await state.update_data(capacity=int(raw))
    await _ask_visibility(message, state)


async def _ask_visibility(message: Message, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.set_state(CreateKhatm.choosing_reminder_tone)
    await message.answer(
        t("create_khatm.ask_reminder_tone", lang),
        reply_markup=reminder_tone_keyboard(),
    )


@router.callback_query(F.data.startswith("ck:tone:"), StateFilter(CreateKhatm.choosing_reminder_tone))
async def choose_reminder_tone(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    tone = callback.data.split(":")[2]
    await state.update_data(reminder_tone=tone, advertising_enabled=False)
    await safe_clear_inline_keyboard(callback.message)
    # Owner request (2026-09-22): removed the "فعال بشه؟" cash-gift/
    # advertising question from the wizard — "منطق ارسال پیام تبلیغاتی
    # رو اشتباه فهمیدی، بعداً توضیح میدم." Defaults to off; the owner
    # will describe the intended logic separately before this gets
    # rebuilt properly, rather than guessing at it now.
    await state.set_state(CreateKhatm.choosing_visibility)
    await callback.message.answer(
        t("create_khatm.ask_visibility", lang), reply_markup=visibility_choice_keyboard()
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("ck:visibility:"), StateFilter(CreateKhatm.choosing_visibility))
async def choose_visibility(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[2]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    await state.update_data(visibility=value)
    await safe_clear_inline_keyboard(callback.message)
    await _show_confirmation(callback.message, state, platform=platform, platform_subject=str(callback.from_user.id))
    await safe_answer_callback(callback)


_MODE_LABEL_KEYS = {
    KhatmTypeEnum.COMMITMENT.value: "create_khatm.mode_label.COMMITMENT",
    KhatmTypeEnum.OPEN.value: "create_khatm.mode_label.OPEN",
}

_VISIBILITY_LABEL_KEYS = {
    KhatmVisibility.PUBLIC.value: "create_khatm.visibility_label.PUBLIC",
    KhatmVisibility.UNLISTED.value: "create_khatm.visibility_label.UNLISTED",
    KhatmVisibility.PRIVATE.value: "create_khatm.visibility_label.PRIVATE",
}

_DISPLAY_LABEL_KEYS = {
    "FULL_NAME": "create_khatm.display_label.FULL_NAME",
    "FIRST_NAME": "create_khatm.display_label.FIRST_NAME",
    "PSEUDONYM": "create_khatm.display_label.PSEUDONYM",
    "ANONYMOUS": "create_khatm.display_label.ANONYMOUS",
}

_TONE_LABEL_KEYS = {
    "FRIENDLY": "create_khatm.tone_label.FRIENDLY",
    "FORMAL": "create_khatm.tone_label.FORMAL",
    "DEVOTIONAL": "create_khatm.tone_label.DEVOTIONAL",
    "SHORT": "create_khatm.tone_label.SHORT",
}

_CONTENT_MODE_LABEL_KEYS = {
    "AUTO": "create_khatm.content_mode_label.AUTO",
    "PHOTO": "create_khatm.content_mode_label.PHOTO",
    "TEXT": "create_khatm.content_mode_label.TEXT",
}

_GROUP_LABEL_KEYS = {
    KhatmCategoryGroup.SALAWAT.value: "create_khatm.group_label.SALAWAT",
    KhatmCategoryGroup.DUA.value: "create_khatm.group_label.DUA",
    KhatmCategoryGroup.LAAN.value: "create_khatm.group_label.LAAN",
}


async def _show_confirmation(
    message: Message,
    state: FSMContext,
    *,
    platform: Platform | None = None,
    platform_subject: str | None = None,
) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    template = data["template_type"]
    mode = data["khatm_type"]

    lines = [t("create_khatm.confirm.title", lang, value=data["title"])]
    if data.get("niyyat"):
        lines.append(t("create_khatm.confirm.niyyat", lang, value=data["niyyat"]))
    if data.get("welcome_text"):
        lines.append(t("create_khatm.confirm.welcome", lang, value=data["welcome_text"]))
    if data.get("recitation_text"):
        lines.append(t("create_khatm.confirm.recitation_text_set", lang))
    display_key = _DISPLAY_LABEL_KEYS.get(data.get("creator_display_mode", "FULL_NAME"), _DISPLAY_LABEL_KEYS["FULL_NAME"])
    lines.append(t("create_khatm.confirm.creator_display", lang, value=t(display_key, lang)))
    lines.append(t("create_khatm.confirm.mode", lang, value=t(_MODE_LABEL_KEYS[mode], lang)))
    lines.append(t("create_khatm.confirm.membership", lang, value=t(_VISIBILITY_LABEL_KEYS[data["visibility"]], lang)))
    tone_key = _TONE_LABEL_KEYS.get(data.get("reminder_tone", ReminderTone.FRIENDLY.value), _TONE_LABEL_KEYS["FRIENDLY"])
    lines.append(t("create_khatm.confirm.tone", lang, value=t(tone_key, lang)))
    if data.get("start_at"):
        lines.append(t("create_khatm.confirm.start_at", lang, value=data["start_at"].strftime("%Y-%m-%d %H:%M")))
    else:
        lines.append(t("create_khatm.confirm.start_now", lang))

    if template == KhatmTemplateType.SALAWAT.value:
        group_key = _GROUP_LABEL_KEYS.get(data.get("category_group"), "create_khatm.group_label.generic")
        group_label = t(group_key, lang)
        category_title = data.get("content_category_title")
        lines.append(
            t("create_khatm.confirm.content_type", lang, value=group_label)
            + (f" — {category_title}" if category_title else "")
        )
        unit = (
            t("create_khatm.unit.salawat", lang)
            if data.get("category_group") == KhatmCategoryGroup.SALAWAT.value
            else t("create_khatm.unit.time", lang)
        )
        if mode == KhatmTypeEnum.OPEN.value:
            lines.append(t("create_khatm.confirm.total_target", lang, amount=data["salawat_open_target"], unit=unit))
        else:
            lines.append(t("create_khatm.confirm.per_member_share", lang, amount=data["salawat_commitment_quantity"], unit=unit))
            capacity = data.get("capacity")
            capacity_text = capacity if capacity else t("create_khatm.capacity_unlimited", lang)
            lines.append(t("create_khatm.confirm.capacity", lang, value=capacity_text))
    else:
        edition = QURAN_EDITIONS[data["quran_edition_id"]]
        lines.append(t("create_khatm.confirm.quran_content", lang))
        lines.append(t("create_khatm.confirm.edition", lang, value=edition["label"]))
        mode_label_key = _CONTENT_MODE_LABEL_KEYS.get(data.get("content_delivery_mode", "AUTO"), _CONTENT_MODE_LABEL_KEYS["AUTO"])
        lines.append(t("create_khatm.confirm.delivery_format", lang, value=t(mode_label_key, lang)))
        if mode == KhatmTypeEnum.COMMITMENT.value:
            lines.append(t("create_khatm.confirm.deadline", lang, hour=data["daily_deadline_hour"]))
            capacity = data.get("capacity")
            capacity_text = capacity if capacity else t("create_khatm.capacity_unlimited", lang)
            lines.append(t("create_khatm.confirm.capacity", lang, value=capacity_text))

    price = get_settings().khatm_creation_price_toman
    if platform is not None and platform_subject is not None:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(session, platform, platform_subject)
            try:
                price = await plan_service.get_creation_price(
                    session, user.id, fallback_price_toman=price
                )
            except plan_service.PlanFeatureUnavailableError:
                await state.clear()
                await message.answer(
                    t("create_khatm.plan_unavailable", lang), reply_markup=main_menu_keyboard(lang)
                )
                return
        await state.update_data(creation_price_toman=price)
    if price > 0:
        lines.append(t("create_khatm.confirm.cost_line", lang, amount=f"{price:,}"))
        lines.append(t("create_khatm.confirm.coupon_hint", lang))

    lines.append(t("create_khatm.confirm.final_warning", lang))
    await state.set_state(CreateKhatm.confirming)
    await message.answer("\n".join(lines), reply_markup=confirm_keyboard(allow_coupon=price > 0))


@router.callback_query(F.data == "ck:coupon", StateFilter(CreateKhatm.confirming))
async def ask_creation_coupon(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    if int(data.get("creation_price_toman") or 0) <= 0:
        await safe_answer_callback(callback, t("create_khatm.coupon_free_khatm", lang), show_alert=True)
        return
    await state.set_state(CreateKhatm.entering_coupon)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("create_khatm.ask_coupon", lang),
        reply_markup=coupon_entry_keyboard(),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data == "ck:coupon_back", StateFilter(CreateKhatm.entering_coupon))
async def skip_creation_coupon(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(coupon_code=None, coupon_discount_toman=None)
    await safe_clear_inline_keyboard(callback.message)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    await _show_confirmation(
        callback.message,
        state,
        platform=platform,
        platform_subject=str(callback.from_user.id),
    )
    await safe_answer_callback(callback)


async def _apply_coupon_code(message: Message, state: FSMContext, code: str) -> bool:
    lang = await _lang(state)
    code = code.strip().upper()
    if not code:
        await message.answer(t("create_khatm.coupon_empty", lang))
        return False
    data = await state.get_data()
    gross = int(data.get("creation_price_toman") or 0)
    if gross <= 0:
        await message.answer(t("create_khatm.coupon_not_needed", lang))
        return False
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        try:
            discount = await wallet_service.quote_coupon(
                session,
                code=code,
                user_id=user.id,
                gross_amount_toman=gross,
            )
        except wallet_service.InvalidCouponError:
            await message.answer(
                t("create_khatm.coupon_invalid", lang),
                reply_markup=coupon_entry_keyboard(),
            )
            return False
    await state.update_data(coupon_code=code, coupon_discount_toman=discount)
    await state.set_state(CreateKhatm.confirming)
    await message.answer(
        t(
            "create_khatm.coupon_accepted",
            lang,
            gross=f"{gross:,}",
            discount=f"{discount:,}",
            net=f"{gross - discount:,}",
        ),
        reply_markup=confirm_keyboard(allow_coupon=True),
    )
    return True


@router.message(StateFilter(CreateKhatm.entering_coupon))
async def receive_creation_coupon(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    await _apply_coupon_code(message, state, message.text or "")


@router.message(Command("coupon"), StateFilter(CreateKhatm.confirming))
async def apply_creation_coupon(
    message: Message, command: CommandObject, state: FSMContext
) -> None:
    lang = await _lang(state)
    code = (command.args or "").strip().upper()
    if not code:
        await state.set_state(CreateKhatm.entering_coupon)
        await message.answer(
            t("create_khatm.ask_coupon_command", lang),
            reply_markup=coupon_entry_keyboard(),
        )
        return
    await _apply_coupon_code(message, state, code)


@router.callback_query(F.data == "ck:cancel")
async def cancel_wizard(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.clear()
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("create_khatm.cancelled", lang), reply_markup=main_menu_keyboard(lang))
    await safe_answer_callback(callback)


async def _finish_creating_khatm(message: Message, state: FSMContext, lang: str, data: dict) -> None:
    """Owner-reported bug (2026-09-21/22): a creator whose phone wasn't
    verified yet used to have the *entire* wizard thrown away — told to
    run /verify_phone and start over from scratch. Extracted so both the
    normal confirm path and the post-verification resume path (see
    `_resume_khatm_creation_if_pending` below) can share the exact same
    creation logic instead of duplicating it."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    price = get_settings().khatm_creation_price_toman

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        try:
            price = await plan_service.get_creation_price(
                session, user.id, fallback_price_toman=price
            )
        except plan_service.PlanFeatureUnavailableError:
            await message.answer(t("create_khatm.plan_unavailable_support", lang), reply_markup=main_menu_keyboard(lang))
            return
        try:
            khatm, token = await workflow_service.create_and_launch_khatm(
                session,
                creator_user_id=user.id,
                template_type=KhatmTemplateType(data["template_type"]),
                khatm_type=KhatmTypeEnum(data["khatm_type"]),
                title=data["title"],
                niyyat=data.get("niyyat"),
                welcome_text=data.get("welcome_text"),
                creator_display_mode=data.get("creator_display_mode", CreatorDisplayMode.FULL_NAME.value),
                creator_pseudonym=data.get("creator_pseudonym"),
                start_at=data.get("start_at"),
                salawat_open_target=data.get("salawat_open_target"),
                salawat_commitment_quantity=data.get("salawat_commitment_quantity"),
                quran_edition_id=data.get("quran_edition_id"),
                daily_deadline_hour=data.get("daily_deadline_hour"),
                capacity=data.get("capacity"),
                visibility=KhatmVisibility(data["visibility"]),
                advertising_enabled=bool(data.get("advertising_enabled", False)),
                creation_price_toman=price,
                content_delivery_mode=data.get("content_delivery_mode", ContentDeliveryMode.AUTO.value),
                reminder_tone=data.get("reminder_tone", ReminderTone.FRIENDLY.value),
                coupon_code=data.get("coupon_code"),
                content_category_id=data.get("content_category_id"),
                description=data.get("recitation_text"),
            )
        except InsufficientFundsError:
            await message.answer(t("create_khatm.insufficient_funds", lang, price=f"{price:,}"), reply_markup=main_menu_keyboard(lang))
            return
        except workflow_service.PlanCapExceededError as exc:
            await message.answer(exc.message, reply_markup=main_menu_keyboard(lang))
            return
        except wallet_service.InvalidCouponError:
            await state.update_data(coupon_code=None, coupon_discount_toman=None)
            await message.answer(
                t("create_khatm.coupon_expired_at_confirm", lang),
                reply_markup=confirm_keyboard(allow_coupon=price > 0),
            )
            return

    await state.clear()

    settings = get_settings()
    landing_line = ""
    if settings.public_web_base_url:
        landing_line = t(
            "create_khatm.landing_line",
            lang,
            url=f"{settings.public_web_base_url.rstrip('/')}/join/{token}",
        )
    if platform == Platform.TELEGRAM and settings.telegram_bot_username:
        invite_line = f"https://t.me/{settings.telegram_bot_username}?start=join_{token}"
    elif platform == Platform.BALE and settings.bale_bot_username:
        # Owner-reported bug (2026-09-22): the raw "/start join_<token>"
        # text instruction wasn't usable as a real invite ("لینک... خرابه") —
        # a manually-typed command is error-prone (typos, no clickable
        # link). Use the same ble.ir deep-link format `_invite_friends_line`
        # in portions.py already relies on elsewhere in this codebase, for
        # consistency — a real clickable link instead of dictated text.
        invite_line = f"https://ble.ir/{settings.bale_bot_username}?start=join_{token}"
    else:
        invite_line = t("create_khatm.bale_invite_instruction", lang, token=token)

    await message.answer(
        t(
            "create_khatm.success",
            lang,
            title=khatm.title,
            invite_line=invite_line,
            landing_line=landing_line,
        ),
        reply_markup=main_menu_keyboard(lang),
    )


async def resume_khatm_creation_if_pending(message: Message, state: FSMContext) -> bool:
    """Owner-reported bug: finishing phone verification (or the profile-
    completion step verification requires first) used to just drop the
    creator back at the main menu, discarding the entire in-progress
    create-khatm wizard — they had to start over from scratch. Called by
    `change_phone.py` (after OTP success) and `profile.py` (after profile
    save) to check whether *they* were triggered from mid-wizard
    (`confirm_wizard` marks this before redirecting) and, if so, either
    continue to the next verification step or actually finish creating
    the khatm. Returns True if it handled the message (caller should skip
    its own normal "all done" message), False if there was nothing pending."""
    data = await state.get_data()
    if not data.get("resume_khatm_creation"):
        return False
    lang = data.get("lang", "fa")
    from khatmsaz.bot.handlers.change_phone import ensure_creator_phone_verified

    verified = await ensure_creator_phone_verified(message, state)
    if not verified:
        if await state.get_state() is not None:
            # A further step (OTP code entry, manual-review notice was
            # already shown, etc.) is now active — keep the wizard data
            # and the resume marker alive for when that step finishes too.
            await state.update_data(**data)
        return True
    await _finish_creating_khatm(message, state, lang, data)
    return True


@router.callback_query(F.data == "ck:confirm", StateFilter(CreateKhatm.confirming))
async def confirm_wizard(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    data = await state.get_data()
    from khatmsaz.bot.handlers.change_phone import ensure_creator_phone_verified

    verified = await ensure_creator_phone_verified(callback.message, state)
    await safe_clear_inline_keyboard(callback.message)
    if not verified:
        if await state.get_state() is not None:
            # Phone/profile verification just started — keep the wizard's
            # answers so far and mark that creation should resume once
            # that finishes (see `resume_khatm_creation_if_pending`).
            await state.update_data(**data, resume_khatm_creation=True)
        await safe_answer_callback(callback)
        return
    await _finish_creating_khatm(callback.message, state, lang, data)
    await safe_answer_callback(callback)
