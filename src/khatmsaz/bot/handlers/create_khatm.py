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
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
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
from khatmsaz.bot import invite_links
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.invitation import service as invitation_service
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
    entering_niyyat = State()
    entering_welcome = State()
    entering_creator_contact = State()       # R4: contact ID shown in welcome
    entering_recitation_text = State()
    entering_open_target = State()
    entering_commitment_quantity = State()
    choosing_commitment_total = State()      # R5: creator picks the khatm TOTAL
    entering_commitment_total_custom = State()
    choosing_edition = State()
    choosing_content_delivery_mode = State()
    entering_deadline_hour = State()
    choosing_capacity_mode = State()
    entering_capacity_number = State()
    choosing_visibility = State()
    choosing_allowed_platforms = State()
    choosing_reminder_tone = State()
    choosing_creator_display = State()
    entering_creator_pseudonym = State()
    choosing_start_schedule = State()
    entering_start_at = State()
    entering_coupon = State()
    confirming = State()
    choosing_invite_platform = State()
    choosing_invite_languages = State()


async def _resolve_lang(message: Message) -> str:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


async def _lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("lang", "fa")


def _bot_category_for(template_type: str, category_group: str | None) -> str:
    """Map a wizard's (template_type, category_group) to the member-bot category
    value (mirrors bot_registry.resolve_bot_category without needing a Khatm)."""
    from khatmsaz.modules.bot_registry.models import BotCategory
    if template_type in (KhatmTemplateType.QURAN_PAGE.value, KhatmTemplateType.QURAN_SURAH.value):
        return BotCategory.QURAN.value
    if category_group == KhatmCategoryGroup.LAAN.value:
        return BotCategory.LAAN.value
    if category_group == KhatmCategoryGroup.DUA.value:
        return BotCategory.DUA_ZIYARAT.value
    return BotCategory.SALAWAT.value


async def _show_intro_image(message: Message, state: FSMContext) -> None:
    """R2 (owner 2026-09-28): after the creator picks commitment/free, show the
    member bot's intro image (uploaded in the admin panel) with the fixed
    «همه ختم‌ها به نیت صاحب‌الزمان» caption, so the creator sees how the khatm is
    presented. Falls back to a text-only caption when no image is configured.
    It is a wizard step, so it is removed as soon as the next question is
    shown (the owner does not want completed questions left in the chat)."""
    lang = await _lang(state)
    data = await state.get_data()
    caption = t("intro.image_caption", lang)
    category = _bot_category_for(data.get("template_type"), data.get("category_group"))
    from khatmsaz.modules.bot_registry import service as bot_registry_service
    image = None
    try:
        async with session_scope() as session:
            image = await bot_registry_service.get_intro_image_for_category(session, category)
    except Exception:
        image = None
    sent = None
    if image:
        try:
            sent = await message.answer_photo(image, caption=caption)
        except Exception:
            pass
    if sent is None:
        sent = await message.answer(caption)
    await state.update_data(_wiz_extra_mids=[getattr(sent, "message_id", None)])


async def _wiz(
    message: Message, state: FSMContext, text: str, reply_markup=None, *,
    keep_extra: bool = False,
):
    """R1 (owner 2026-09-28): keep the wizard from cluttering the chat. Each new
    wizard prompt deletes the previous *bot* prompt AND the user's own typed
    answer (bots CAN delete incoming messages in a private chat), so only the
    current step remains — «فقط اون پیام آخر باشه، پیامای خودم و بات پاک بشن».
    Best-effort: a failed delete (message too old / already gone) never blocks
    the new prompt. Tracks the last prompt id in FSM data."""
    data = await state.get_data()
    prev = data.get("_wiz_mid")
    if prev:
        try:
            await message.bot.delete_message(message.chat.id, prev)
        except Exception:
            pass
    if not keep_extra:
        for extra in data.get("_wiz_extra_mids", []):
            if extra:
                try:
                    await message.bot.delete_message(message.chat.id, extra)
                except Exception:
                    pass
    # Delete the user's incoming typed message too (only when THIS call was
    # triggered by a user text message, not a callback's bot-owned message).
    if getattr(getattr(message, "from_user", None), "is_bot", True) is False:
        try:
            await message.bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
    sent = await message.answer(text, reply_markup=reply_markup)
    update = {"_wiz_mid": getattr(sent, "message_id", None)}
    if not keep_extra:
        update["_wiz_extra_mids"] = []
    await state.update_data(**update)
    return sent


@router.message(F.text.in_(CREATE_BUTTON_TEXTS))
async def start_wizard(message: Message, state: FSMContext) -> None:
    from khatmsaz.modules.identity.models import UserRole
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        # DEC-PY-0093: entering the creator bot and choosing to create is the
        # creator-registration intent. No separate approval request/menu gate.
        if user.role == UserRole.USER:
            await identity_service.promote_creator(session, user.id)

    await state.clear()
    if not await ensure_creator_phone_verified(message, state):
        if await state.get_state() is not None:
            await state.update_data(resume_khatm_creation_from_start=True)
        return
    lang = await _resolve_lang(message)
    await state.update_data(lang=lang)
    await state.set_state(CreateKhatm.choosing_template)
    await _wiz(message, state, t("create_khatm.ask_template", lang), reply_markup=template_choice_keyboard(lang))


@router.message(Command("new_khatm"))
@router.message(Command("create"))
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
            lang=lang,
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
    await _wiz(
        message, state,
        t("create_khatm.ask_mode", lang, explanation=t(explanation_key, lang)),
        reply_markup=commitment_mode_keyboard(lang),
    )


def _default_khatm_title(data: dict, lang: str) -> str:
    """Build the standard title without asking the creator an extra question."""
    if data.get("content_category_title"):
        return t(
            "create_khatm.default_title.category", lang,
            name=data["content_category_title"],
        )
    if data["template_type"] == KhatmTemplateType.QURAN_PAGE.value:
        return t("create_khatm.default_title.quran", lang)
    return t("create_khatm.default_title.salawat", lang)


@router.callback_query(F.data.startswith("ck:mode:"), StateFilter(CreateKhatm.choosing_mode))
async def choose_mode(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    mode = callback.data.split(":")[2]
    await state.update_data(khatm_type=mode)
    await safe_clear_inline_keyboard(callback.message)
    # R2: show the intro image + fixed niyyat caption right after the mode choice.
    await _show_intro_image(callback.message, state)
    data = await state.get_data()
    title = _default_khatm_title(data, lang)
    await state.update_data(title=title)
    await state.set_state(CreateKhatm.entering_niyyat)
    await _wiz(
        callback.message, state, t("create_khatm.ask_niyyat", lang),
        reply_markup=skip_niyyat_keyboard(lang),
        keep_extra=True,
    )
    await safe_answer_callback(callback)


def _compose_niyyat(lang: str, proxy_name: str | None) -> str:
    """Owner rule (2026-09-27, DEC-PY-0090): the niyyat is FIXED for every
    khatm — «به نیت ظهور امام زمان علیه السلام». The creator may not write a
    free niyyat; they may only optionally dedicate the khatm on someone's
    behalf (نیابت), which is appended as a suffix."""
    niyyat = t("create_khatm.fixed_niyyat", lang)
    if proxy_name:
        name = proxy_name.strip()
        # The user may or may not type the «به نیابت از» prefix themselves —
        # strip any leading dedication phrase so it is never doubled
        # («به نیابت از به نیابت از …», owner report 2026-09-28).
        for prefix in ("به نیابت از", "نیابت از", "به نيابة عن", "نيابة عن", "on behalf of"):
            if name.lower().startswith(prefix.lower()):
                name = name[len(prefix):].strip(" :،-") or name
                break
        niyyat += t("create_khatm.niyyat_proxy_suffix", lang, name=name)
    return niyyat


@router.message(StateFilter(CreateKhatm.entering_niyyat))
async def enter_niyyat(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    proxy = (message.text or "").strip() or None
    await state.update_data(niyyat=_compose_niyyat(lang, proxy))
    await _ask_welcome(message, state)


@router.callback_query(F.data == "ck:skip_niyyat", StateFilter(CreateKhatm.entering_niyyat))
async def skip_niyyat(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    await state.update_data(niyyat=_compose_niyyat(lang, None))
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
    await _wiz(message, state, text, reply_markup=skip_niyyat_keyboard(lang))


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
    await _ask_creator_contact(message, state)


@router.callback_query(F.data == "ck:skip_niyyat", StateFilter(CreateKhatm.entering_welcome))
async def skip_welcome(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(welcome_text=None)
    await safe_clear_inline_keyboard(callback.message)
    await _ask_creator_contact(callback.message, state, actor=callback.from_user)
    await safe_answer_callback(callback)


def _creator_contact_keyboard(lang: str, contact: str | None) -> InlineKeyboardMarkup | None:
    """R4 (owner 2026-09-28): the creator MUST provide a contact so members can
    reach them — «نباید بتونن رد بکنن». No skip button. Offers only a one-tap
    "use my @username" when available; otherwise the creator has to type one."""
    if not contact:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=t("create_khatm.contact.use_username", lang, username=contact),
        callback_data="ck:contact:self",
    )]])


def _compose_welcome_with_contact(
    welcome_text: str | None, contact: str | None, lang: str
) -> str | None:
    """R4: the creator's contact handle is appended to the welcome text so
    members always see how to reach the organizer. Migration-free — reuses the
    existing ``welcome_text`` column instead of a new one."""
    if not contact:
        return welcome_text
    contact_line = t("create_khatm.welcome_contact_line", lang, contact=contact)
    if welcome_text:
        return f"{welcome_text}\n\n{contact_line}"[:500]
    return contact_line[:500]


async def _ask_creator_contact(message: Message, state: FSMContext, *, actor=None) -> None:
    lang = await _lang(state)
    # A callback's ``message.from_user`` is the bot itself.  Always prefer the
    # human callback actor; otherwise the bot username was offered/stored as
    # the creator's contact (owner report 2026-09-28).
    human = actor or getattr(message, "from_user", None)
    username = getattr(human, "username", None) or None
    own_contact = f"@{username}" if username else None
    if own_contact is None:
        platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(
                session, platform, getattr(human, "id", message.chat.id)
            )
            settings = await settings_service.get_or_create(session, user.id)
            own_contact = settings.contact_phone
    await state.update_data(_creator_own_contact=own_contact)
    await state.set_state(CreateKhatm.entering_creator_contact)
    await _wiz(
        message, state,
        t("create_khatm.ask_creator_contact", lang),
        reply_markup=_creator_contact_keyboard(lang, own_contact),
    )


def _normalize_contact(raw: str) -> str:
    """Accept an @id, a bare id, a t.me/… link, or a phone number and store a
    clean, tappable handle."""
    raw = raw.strip()
    for prefix in ("https://t.me/", "http://t.me/", "t.me/", "https://ble.ir/", "ble.ir/"):
        if raw.lower().startswith(prefix):
            raw = raw[len(prefix):]
            break
    if raw and not raw.startswith("@") and not raw[0].isdigit() and "+" not in raw:
        raw = "@" + raw
    return raw[:64]


@router.message(StateFilter(CreateKhatm.entering_creator_contact))
async def enter_creator_contact(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    contact = _normalize_contact(message.text or "")
    if not contact:
        # Mandatory (owner 2026-09-28): re-ask until a real contact is given.
        data = await state.get_data()
        await _wiz(
            message, state,
            t("create_khatm.creator_contact_required", lang),
            reply_markup=_creator_contact_keyboard(lang, data.get("_creator_own_contact")),
        )
        return
    await state.update_data(creator_contact=contact)
    await _after_welcome(message, state)


@router.callback_query(F.data == "ck:contact:self", StateFilter(CreateKhatm.entering_creator_contact))
async def use_own_contact(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(creator_contact=data.get("_creator_own_contact"))
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
        await _wiz(
            message, state,
            t("create_khatm.ask_recitation_text", lang),
            reply_markup=skip_niyyat_keyboard(lang),
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
    await _wiz(
        message, state,
        t("create_khatm.ask_creator_display", lang),
        reply_markup=creator_display_keyboard(lang),
    )


@router.callback_query(F.data.startswith("ck:creator_display:"), StateFilter(CreateKhatm.choosing_creator_display))
async def choose_creator_display(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    mode = callback.data.split(":")[2]
    await state.update_data(creator_display_mode=mode)
    await safe_clear_inline_keyboard(callback.message)
    if mode == CreatorDisplayMode.PSEUDONYM.value:
        await state.set_state(CreateKhatm.entering_creator_pseudonym)
        await _wiz(callback.message, state, t("create_khatm.ask_pseudonym", lang))
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
    # Owner (2026-09-28): a khatm always starts now — the «شروع در تاریخ آینده»
    # option was removed. Skip the start-schedule question entirely (start_at=None
    # means "start immediately") and go straight to the next step.
    await state.update_data(start_at=None)
    await _after_start_schedule(message, state)


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
        await _wiz(message, state, t("create_khatm.ask_open_target", lang, title=title, unit=unit))
    elif template == KhatmTemplateType.SALAWAT.value and mode == KhatmTypeEnum.COMMITMENT.value:
        # R5 (owner 2026-09-28): the creator picks the khatm's TOTAL goal from
        # preset buttons (not a per-person quantity); each participant later
        # sets their own share on the member bot (R11).
        unit = (
            t("create_khatm.unit.salawat", lang)
            if data.get("category_group") == KhatmCategoryGroup.SALAWAT.value
            else t("create_khatm.unit.time", lang)
        )
        await state.set_state(CreateKhatm.choosing_commitment_total)
        await _wiz(
            message, state,
            t("create_khatm.ask_commitment_total", lang, unit=unit),
            reply_markup=_commitment_total_keyboard(lang),
        )
    else:  # QURAN_PAGE, either mode
        await state.set_state(CreateKhatm.choosing_edition)
        await _wiz(message, state, t("create_khatm.ask_edition", lang), reply_markup=edition_choice_keyboard())


def _commitment_total_keyboard(lang: str) -> InlineKeyboardMarkup:
    """R5: preset total-goal buttons for a commitment khatm."""
    presets = [10, 14, 40, 110, 313]
    rows = [[InlineKeyboardButton(text=str(n), callback_data=f"ck:total:{n}") for n in presets[:3]],
            [InlineKeyboardButton(text=str(n), callback_data=f"ck:total:{n}") for n in presets[3:]]]
    rows.append([InlineKeyboardButton(text=t("create_khatm.commitment_total.custom", lang), callback_data="ck:total:custom")])
    rows.append([InlineKeyboardButton(text=t("create_khatm.commitment_total.unlimited", lang), callback_data="ck:total:unlimited")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _after_commitment_total(message: Message, state: FSMContext, total: int | None) -> None:
    # Store the khatm TOTAL goal; per-person share is chosen by each member.
    await state.update_data(salawat_open_target=total, salawat_commitment_quantity=None, capacity=None)
    await _ask_visibility(message, state)


@router.callback_query(F.data.startswith("ck:total:"), StateFilter(CreateKhatm.choosing_commitment_total))
async def choose_commitment_total(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    value = callback.data.split(":", 2)[2]
    await safe_clear_inline_keyboard(callback.message)
    if value == "custom":
        await state.set_state(CreateKhatm.entering_commitment_total_custom)
        await callback.message.answer(t("create_khatm.ask_commitment_total_custom", lang))
        await safe_answer_callback(callback)
        return
    total = None if value == "unlimited" else int(value)
    await _after_commitment_total(callback.message, state, total)
    await safe_answer_callback(callback)


@router.message(StateFilter(CreateKhatm.entering_commitment_total_custom))
async def enter_commitment_total_custom(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    lang = await _lang(state)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("create_khatm.positive_number_required", lang))
        return
    await _after_commitment_total(message, state, int(raw))


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
    # Owner (2026-09-28): drop the capacity question entirely — it's an
    # unnecessary extra step; khatms are unlimited by default.
    await state.update_data(salawat_commitment_quantity=int(raw), capacity=None)
    await _ask_visibility(message, state)


@router.callback_query(F.data.startswith("ck:edition:"), StateFilter(CreateKhatm.choosing_edition))
async def choose_edition(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    edition_id = callback.data.split(":", 2)[2]
    # Owner rule (2026-09-27, DEC-PY-0091): drop the content-format question
    # from the creation wizard entirely — the bot should just send whatever
    # content it has for each page (AUTO). The per-khatm content-mode override
    # still exists in khatm management (cs:modes) for anyone who needs it.
    await state.update_data(
        quran_edition_id=edition_id,
        content_delivery_mode=ContentDeliveryMode.AUTO.value,
    )
    await safe_clear_inline_keyboard(callback.message)

    data = await state.get_data()
    if data["khatm_type"] == KhatmTypeEnum.COMMITMENT.value:
        await state.set_state(CreateKhatm.entering_deadline_hour)
        await _wiz(callback.message, state, t("create_khatm.ask_deadline_hour", lang))
    else:
        await _ask_visibility(callback.message, state)
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
        await _wiz(callback.message, state, t("create_khatm.ask_deadline_hour", lang))
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
    # Owner (2026-09-28): capacity question removed (unnecessary step).
    await state.update_data(daily_deadline_hour=int(raw), capacity=None)
    await _ask_visibility(message, state)


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
    await _wiz(
        message, state,
        t("create_khatm.ask_reminder_tone", lang),
        reply_markup=reminder_tone_keyboard(lang),
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
    await _wiz(
        callback.message, state,
        t("create_khatm.ask_visibility", lang), reply_markup=visibility_choice_keyboard(lang)
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("ck:visibility:"), StateFilter(CreateKhatm.choosing_visibility))
async def choose_visibility(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[2]
    await state.update_data(visibility=value)
    await safe_clear_inline_keyboard(callback.message)
    
    # Next step: Ask for allowed platforms
    lang = await _lang(state)
    await state.set_state(CreateKhatm.choosing_allowed_platforms)
    
    # Owner (2026-09-28): order = هر دو (default) first, then تلگرام, then بله.
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 هر دو پیام‌رسان (پیشنهادی)", callback_data="ck:platforms:BOTH")],
            [InlineKeyboardButton(text="تلگرام", callback_data="ck:platforms:TELEGRAM")],
            [InlineKeyboardButton(text="بله", callback_data="ck:platforms:BALE")],
        ]
    )
    
    await _wiz(
        callback.message, state,
        "این ختم برای کاربران کدام پیام‌رسان‌ها قابل عضویت باشد؟",
        reply_markup=markup
    )
    await safe_answer_callback(callback)

@router.callback_query(F.data.startswith("ck:platforms:"), StateFilter(CreateKhatm.choosing_allowed_platforms))
async def choose_allowed_platforms(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[2]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    await state.update_data(allowed_platforms=value)
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
    
    platforms = data.get("allowed_platforms", "BOTH")
    if platforms == "TELEGRAM":
        lines.append("📱 پلتفرم‌های مجاز: فقط تلگرام")
    elif platforms == "BALE":
        lines.append("📱 پلتفرم‌های مجاز: فقط بله")
    else:
        lines.append("📱 پلتفرم‌های مجاز: همه (تلگرام و بله)")
        
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
        # R5: both open and commitment now show the TOTAL goal (per-person
        # share is set by each member). Unlimited → no number line.
        total = data.get("salawat_open_target")
        if total:
            lines.append(t("create_khatm.confirm.total_target", lang, amount=total, unit=unit))
        else:
            lines.append(t("create_khatm.confirm.total_unlimited", lang))
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
    await message.answer("\n".join(lines), reply_markup=confirm_keyboard(allow_coupon=price > 0, lang=lang))


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
        reply_markup=coupon_entry_keyboard(lang),
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
                reply_markup=coupon_entry_keyboard(lang),
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
        reply_markup=confirm_keyboard(allow_coupon=True, lang=lang),
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
            reply_markup=coupon_entry_keyboard(lang),
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
                welcome_text=_compose_welcome_with_contact(
                    data.get("welcome_text"), data.get("creator_contact"), lang
                ),
                creator_display_mode=data.get("creator_display_mode", CreatorDisplayMode.FULL_NAME.value),
                creator_pseudonym=data.get("creator_pseudonym"),
                start_at=data.get("start_at"),
                salawat_open_target=data.get("salawat_open_target"),
                salawat_commitment_quantity=data.get("salawat_commitment_quantity"),
                quran_edition_id=data.get("quran_edition_id"),
                daily_deadline_hour=data.get("daily_deadline_hour"),
                capacity=data.get("capacity"),
                visibility=KhatmVisibility(data["visibility"]),
                allowed_platforms=data.get("allowed_platforms", "BOTH"),
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
                reply_markup=confirm_keyboard(allow_coupon=price > 0, lang=lang),
            )
            return

    # DO NOT clear state here. We need to preserve created_khatm_id and created_token.
    # We also need to save them into the state.
    await state.update_data(created_khatm_id=str(khatm.id), created_token=token)
    # R9 (owner 2026-09-28): skip the platform/language selection — give the
    # Farsi member-bot link straight away; a button offers the ar/en links only
    # if the creator wants them.
    await state.update_data(selected_invite_languages=["fa"], selected_invite_platform="ALL")
    await finish_invite_links(message, state, lang)


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
    lang = data.get("lang", "fa")
    
    if data.get("resume_khatm_creation_from_start"):
        from khatmsaz.bot.handlers.change_phone import ensure_creator_phone_verified
        verified = await ensure_creator_phone_verified(message, state)
        if not verified:
            if await state.get_state() is not None:
                await state.update_data(**data)
            return True
        await start_wizard(message, state)
        return True

    if not data.get("resume_khatm_creation"):
        return False
        
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

from khatmsaz.core.bot_registry import get_registry
from khatmsaz.modules.khatm.models import Khatm

async def show_invite_platform_keyboard(message: Message, state: FSMContext, lang: str):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    # If no member bots are configured at all, skip the platform/language
    # selection steps entirely and go straight to the result screen.
    if not get_registry().member_bots():
        await state.update_data(selected_invite_platform="ALL", selected_invite_languages=["fa"])
        await finish_invite_links(message, state, lang)
        return

    buttons = [
        [InlineKeyboardButton(text="تلگرام", callback_data="invite_plat:TELEGRAM"),
         InlineKeyboardButton(text="بله", callback_data="invite_plat:BALE")],
        [InlineKeyboardButton(text="همه ربات‌ها", callback_data="invite_plat:ALL")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    text = "لینک دعوت برای کدام پیام‌رسان ساخته شود؟"
    if isinstance(message, CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=kb)
        except Exception:
            # Editing can fail (message too old, deleted, or the client raced
            # two taps). Never leave the creator on a dead screen — send the
            # step as a fresh message so the flow always visibly advances.
            await message.message.answer(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("invite_plat:"), CreateKhatm.choosing_invite_platform)
async def handle_invite_platform(callback: CallbackQuery, state: FSMContext) -> None:
    plat = callback.data.split(":")[1]
    await state.update_data(selected_invite_platform=plat)
    lang = await _lang(state)
    await state.set_state(CreateKhatm.choosing_invite_languages)
    await show_invite_languages_keyboard(callback, state, lang)
    await callback.answer()


async def show_invite_languages_keyboard(message: Message | CallbackQuery, state: FSMContext, lang: str):
    data = await state.get_data()
    khatm_id = data["created_khatm_id"]
    selected = data.get("selected_invite_languages", ["fa"])
    
    async with session_scope() as session:
        khatm = await session.get(Khatm, khatm_id)
        khatm_bot_cat = await invite_links.resolve_khatm_category_value(session, khatm)

    # Find available languages for this category and selected platform
    available_langs = set()
    registry = get_registry()
    plat_choice = data.get("selected_invite_platform", "ALL")
    
    for bot in registry.member_bots():
        # filter by category
        if getattr(bot, "khatmsaz_category", None) and getattr(bot, "khatmsaz_category") == khatm_bot_cat:
            # filter by platform if not ALL
            if plat_choice != "ALL" and getattr(bot, "khatmsaz_platform", None) != Platform(plat_choice):
                continue
            available_langs.add(getattr(bot, "khatmsaz_language"))
            
    if not available_langs:
        # Fallback to single-bot if no member bots match
        await finish_invite_links(message, state, lang)
        return
        
    # Build keyboard
    buttons = []
    lang_names = {"fa": "فارسی", "ar": "عربی", "en": "انگلیسی"}
    for l in sorted(available_langs):
        mark = "✅ " if l in selected else ""
        buttons.append([InlineKeyboardButton(text=f"{mark}{lang_names.get(l, l)}", callback_data=f"toggle_lang:{l}")])
        
    buttons.append([InlineKeyboardButton(text=t("button.confirm", lang), callback_data="confirm_invite_langs")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    text = "لینک دعوت برای کدام زبان‌ها ساخته شود؟"
    if isinstance(message, CallbackQuery):
        try:
            await message.message.edit_text(text, reply_markup=kb)
        except Exception:
            # Fall back to a fresh message so the language step never silently
            # disappears when the edit fails.
            await message.message.answer(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("toggle_lang:"), CreateKhatm.choosing_invite_languages)
async def handle_toggle_lang(callback: CallbackQuery, state: FSMContext) -> None:
    l = callback.data.split(":")[1]
    data = await state.get_data()
    selected = set(data.get("selected_invite_languages", ["fa"]))
    if l in selected:
        selected.remove(l)
    else:
        selected.add(l)
    
    if not selected:
        await callback.answer("حداقل یک زبان باید انتخاب شود.", show_alert=True)
        return
        
    await state.update_data(selected_invite_languages=list(selected))
    lang = await _lang(state)
    await show_invite_languages_keyboard(callback, state, lang)
    await callback.answer()


@router.callback_query(F.data == "confirm_invite_langs", CreateKhatm.choosing_invite_languages)
async def handle_confirm_invite_langs(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(state)
    await finish_invite_links(callback.message, state, lang)
    await callback.answer()


async def finish_invite_links(message: Message, state: FSMContext, lang: str):
    data = await state.get_data()
    khatm_id = data.get("created_khatm_id")
    token = data.get("created_token")
    selected_langs = data.get("selected_invite_languages", ["fa"])
    plat_choice = data.get("selected_invite_platform", "ALL")
    
    async with session_scope() as session:
        khatm = await session.get(Khatm, khatm_id)
        khatm_bot_cat = await invite_links.resolve_khatm_category_value(session, khatm)

    settings = get_settings()

    landing_line = ""
    if settings.public_web_base_url:
        landing_line = t(
            "create_khatm.landing_line",
            lang,
            url=f"{settings.public_web_base_url.rstrip('/')}/join/{token}",
        )

    # Build per-language member bot invite links via the shared helper so this
    # wizard and the "QR دعوت" button in khatm management never drift apart.
    by_lang = invite_links.build_member_invite_links(
        khatm_bot_cat, token, langs=selected_langs, plat_choice=plat_choice,
    )
    invite_lines_str = invite_links.format_invite_lines(by_lang)
    if not invite_lines_str:
        # No member bots have active tokens configured yet.
        invite_lines_str = "⚠️ هیچ ربات عضوی با توکن فعال تنظیم نشده.\nبعد از تنظیم توکن ربات‌ها در پنل مدیریت، لینک را از «🔗 QR دعوت» در مدیریت این ختم دریافت کنید."

    await safe_clear_inline_keyboard(message)
    await state.clear()
    
    from aiogram.types import LinkPreviewOptions
    # Clean up edit message if it was a callback
    if hasattr(message, "edit_text"):
        try:
            await message.delete()
        except Exception:
            pass
            
    # Need original message or callback's message for answer
    target_msg = message if isinstance(message, Message) else message.message
    
    # R9: offer the Arabic/English links on request (only when this default
    # Farsi-only call ran, and other member-bot languages actually exist).
    other_langs_btn = None
    if selected_langs == ["fa"]:
        other = invite_links.build_member_invite_links(khatm_bot_cat, token, plat_choice="ALL")
        if any(l != "fa" for l in other.keys()):
            other_langs_btn = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=t("create_khatm.want_other_lang_links", lang),
                                     callback_data=f"ck:invlangs:{token}")
            ]])

    await target_msg.answer(
        t(
            "create_khatm.success",
            lang,
            title=khatm.title,
            invite_line=invite_lines_str,
            landing_line=landing_line,
        ),
        reply_markup=main_menu_keyboard(lang, is_creator=True),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    if other_langs_btn is not None:
        await target_msg.answer(t("create_khatm.other_lang_hint", lang), reply_markup=other_langs_btn)


@router.callback_query(F.data.startswith("ck:invlangs:"))
async def send_other_language_links(callback: CallbackQuery) -> None:
    """R9: on request, send the Arabic + English member-bot invite links."""
    from aiogram.types import LinkPreviewOptions
    token = callback.data.split(":", 2)[2]
    lang = getattr(callback.message.bot, "khatmsaz_language", None) or "fa"
    async with session_scope() as session:
        khatm_id = await invitation_service.resolve_khatm_id(session, token)
        khatm = await session.get(Khatm, khatm_id)
        khatm_bot_cat = await invite_links.resolve_khatm_category_value(session, khatm)
    by_lang = invite_links.build_member_invite_links(khatm_bot_cat, token, langs=["ar", "en"], plat_choice="ALL")
    lines = invite_links.format_invite_lines(by_lang) or t("create_khatm.no_other_lang_links", lang)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(lines, link_preview_options=LinkPreviewOptions(is_disabled=True))
    await safe_answer_callback(callback)
