"""List of khatms the user created or joined."""

import csv
import io
from datetime import datetime, timezone
from html import escape
from uuid import UUID
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from khatmsaz.bot.keyboards import (
    MY_KHATMS_BUTTON_TEXT, MY_KHATMS_BUTTON_TEXTS, bail_if_menu_button, cancel_khatm_confirm_keyboard, contribute_keyboard,
    creator_khatm_keyboard,
    creator_content_mode_keyboard, creator_edit_cancel_keyboard,
    creator_schedule_keyboard,
    creator_settings_keyboard,
    main_menu_keyboard, safe_answer_callback,
    safe_clear_inline_keyboard,
)
from khatmsaz.bot.qr import build_qr_png
from khatmsaz.bot import invite_links
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.khatm.models import ContentDeliveryMode
from khatmsaz.modules.open_contribution import repository as contribution_repository
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.reporting import service as reporting_service
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.phone import repository as phone_repository
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.i18n import t
from khatmsaz.modules.settings import service as settings_service

router = Router(name="my_khatms")


class CreatorKhatmEdit(StatesGroup):
    entering_value = State()


def _creator_settings_markup(khatm, lang: str = "fa"):
    return creator_settings_keyboard(
        str(khatm.id),
        is_quran=khatm.template_type == KhatmTemplateType.QURAN_PAGE,
        is_commitment=khatm.khatm_type == KhatmTypeEnum.COMMITMENT,
        is_open=khatm.khatm_type == KhatmTypeEnum.OPEN,
        allow_pause=bool(khatm.allow_pause),
        allow_snooze=bool(khatm.allow_snooze),
        miss_threshold=int(khatm.miss_notice_threshold),
        miss_window_days=int(khatm.miss_notice_window_days),
        content_mode=getattr(khatm, "content_delivery_mode", ContentDeliveryMode.AUTO.value),
        lang=lang,
    )


async def _owned_khatm_for_callback(callback, khatm_id: str):
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if user is None or khatm is None or khatm.creator_user_id != user.id:
            return None, None
        return user.id, khatm


_SCHEDULE_LABEL_KEYS = {
    "NONE": "my_khatms.creator.schedule_label.none",
    "DAILY": "my_khatms.creator.schedule_label.daily",
    "WEEKLY": "my_khatms.creator.schedule_label.weekly",
}


def _creator_settings_text(khatm, lang: str) -> str:
    text = t("my_khatms.creator.settings_intro", lang, title=khatm.title)
    if khatm.khatm_type == KhatmTypeEnum.OPEN:
        if khatm.schedule_kind == "INTERVAL":
            label = t("my_khatms.creator.schedule_label.interval", lang, value=khatm.schedule_value or "?")
        elif khatm.schedule_kind == "DATE":
            label = t("my_khatms.creator.schedule_label.date", lang, value=khatm.schedule_value or "?")
        else:
            key = _SCHEDULE_LABEL_KEYS.get(khatm.schedule_kind, "my_khatms.creator.schedule_label.unknown")
            label = t(key, lang)
        text += t("my_khatms.creator.schedule_current", lang, label=label)
    return text


@router.callback_query(F.data.startswith("cs:menu:"))
async def creator_settings_menu(callback) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None:
        await safe_answer_callback(callback, t("my_khatms.no_permission", lang), show_alert=True)
        return
    await callback.message.edit_text(
        _creator_settings_text(khatm, lang), reply_markup=_creator_settings_markup(khatm, lang)
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cs:modes:"))
async def creator_content_modes(callback) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None or khatm.template_type != KhatmTemplateType.QURAN_PAGE:
        await safe_answer_callback(callback, t("my_khatms.creator.quran_only", lang), show_alert=True)
        return
    await callback.message.edit_text(
        t("my_khatms.creator.content_mode_prompt", lang),
        reply_markup=creator_content_mode_keyboard(khatm_id, lang),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cs:schedule:"))
async def creator_schedule_menu(callback) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None or khatm.khatm_type != KhatmTypeEnum.OPEN:
        await safe_answer_callback(callback, t("my_khatms.creator.open_only", lang), show_alert=True)
        return
    await callback.message.edit_text(
        t("my_khatms.creator.schedule_prompt", lang),
        reply_markup=creator_schedule_keyboard(khatm_id, lang),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cs:schedule_set:"))
async def creator_set_schedule(callback) -> None:
    parts = callback.data.split(":")
    khatm_id = parts[2]
    raw = ":".join(parts[3:])
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if user is None:
            await safe_answer_callback(callback, t("my_khatms.creator.account_not_found", lang), show_alert=True)
            return
        try:
            khatm = await khatm_service.set_schedule(
                session, khatm_id=khatm_id, creator_user_id=user.id, raw=raw
            )
        except ValueError:
            await safe_answer_callback(callback, t("my_khatms.creator.schedule_invalid", lang), show_alert=True)
            return
    await callback.message.edit_text(
        _creator_settings_text(khatm, lang), reply_markup=_creator_settings_markup(khatm, lang)
    )
    await safe_answer_callback(callback, t("my_khatms.creator.schedule_saved", lang))


@router.callback_query(F.data.startswith("cs:schedule_date:"))
async def creator_begin_schedule_date(callback, state: FSMContext) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None or khatm.khatm_type != KhatmTypeEnum.OPEN:
        await safe_answer_callback(callback, t("my_khatms.creator.open_only", lang), show_alert=True)
        return
    await state.update_data(creator_edit_khatm_id=khatm_id, creator_edit_field="schedule_date", lang=lang)
    await state.set_state(CreatorKhatmEdit.entering_value)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("my_khatms.creator.ask_schedule_date", lang),
        reply_markup=creator_edit_cancel_keyboard(khatm_id, lang),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cs:end:"))
async def creator_begin_end_at(callback, state: FSMContext) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None or khatm.status.value not in {"DRAFT", "ACTIVE"}:
        await safe_answer_callback(callback, t("my_khatms.creator.end_at_not_allowed", lang), show_alert=True)
        return
    await state.update_data(creator_edit_khatm_id=khatm_id, creator_edit_field="end_at", lang=lang)
    await state.set_state(CreatorKhatmEdit.entering_value)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("my_khatms.creator.ask_end_at", lang),
        reply_markup=creator_edit_cancel_keyboard(khatm_id, lang),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cs:end_clear:"))
async def creator_clear_end_at(callback) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if user is None:
            await safe_answer_callback(callback, t("my_khatms.creator.account_not_found", lang), show_alert=True)
            return
        try:
            khatm = await khatm_service.set_end_at(
                session, khatm_id=khatm_id, creator_user_id=user.id, end_at=None
            )
        except ValueError:
            await safe_answer_callback(callback, t("my_khatms.creator.end_at_cannot_clear", lang), show_alert=True)
            return
    from aiogram.exceptions import TelegramBadRequest
    try:
        await callback.message.edit_text(
            _creator_settings_text(khatm, lang), reply_markup=_creator_settings_markup(khatm, lang)
        )
    except TelegramBadRequest:
        pass
    await safe_answer_callback(callback, t("my_khatms.creator.end_at_cleared", lang))


@router.callback_query(F.data.startswith("cs:edit:"))
async def creator_begin_cosmetic_edit(callback, state: FSMContext) -> None:
    _prefix, _edit, khatm_id, field = callback.data.split(":", 3)
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    if field not in {"title", "welcome", "target", "deadline"}:
        await safe_answer_callback(callback, t("my_khatms.creator.edit_field_invalid", lang), show_alert=True)
        return
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None:
        await safe_answer_callback(callback, t("my_khatms.creator.active_only_edit", lang), show_alert=True)
        return
    await state.update_data(creator_edit_khatm_id=khatm_id, creator_edit_field=field, lang=lang)
    await state.set_state(CreatorKhatmEdit.entering_value)
    await safe_clear_inline_keyboard(callback.message)
    prompt_key = {
        "title": "my_khatms.creator.ask_new_title",
        "welcome": "my_khatms.creator.ask_new_welcome",
        "target": "my_khatms.creator.ask_new_target",
        "deadline": "my_khatms.creator.ask_new_deadline",
    }[field]
    prompt = t(prompt_key, lang)
    await callback.message.answer(prompt, reply_markup=creator_edit_cancel_keyboard(khatm_id, lang))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cs:edit_cancel:"))
async def creator_cancel_cosmetic_edit(callback, state: FSMContext) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await state.clear()
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None:
        await safe_answer_callback(callback, t("my_khatms.creator.edit_gone", lang), show_alert=True)
        return
    await callback.message.edit_text(
        _creator_settings_text(khatm, lang), reply_markup=_creator_settings_markup(khatm, lang)
    )
    await safe_answer_callback(callback, t("my_khatms.creator.edit_cancelled", lang))


@router.message(CreatorKhatmEdit.entering_value)
async def creator_save_cosmetic_edit(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    value = (message.text or "").strip()
    data = await state.get_data()
    lang = data.get("lang", "fa")
    khatm_id = data.get("creator_edit_khatm_id")
    field = data.get("creator_edit_field")
    if not khatm_id or field not in {"title", "welcome", "target", "deadline", "end_at", "schedule_date"}:
        await state.clear()
        await message.answer(t("my_khatms.creator.edit_data_lost", lang))
        return
    if field == "title" and not value:
        await message.answer(t("my_khatms.creator.title_required", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await state.clear()
            await message.answer(t("my_khatms.creator.account_not_found", lang), reply_markup=main_menu_keyboard(lang))
            return
        try:
            if field == "title":
                khatm = await khatm_service.update_title(
                    session, khatm_id=khatm_id, creator_user_id=user.id, title=value
                )
                result = t("my_khatms.creator.title_saved", lang)
            elif field == "welcome":
                welcome_text = None if value.lower() in {"پاک کردن", "حذف", "clear"} else value
                khatm = await khatm_service.update_welcome_text(
                    session, khatm_id=khatm_id, creator_user_id=user.id,
                    welcome_text=welcome_text,
                )
                result = t(
                    "my_khatms.creator.welcome_cleared" if welcome_text is None else "my_khatms.creator.welcome_saved",
                    lang,
                )
            elif field in {"target", "deadline"}:
                if not value.isdigit():
                    raise ValueError("numeric setting required")
                kwargs = (
                    {"repetition_target": int(value)}
                    if field == "target"
                    else {"daily_deadline_hour": int(value)}
                )
                khatm = await khatm_service.update_creator_runtime_settings(
                    session, khatm_id=khatm_id, creator_user_id=user.id, **kwargs
                )
                result = t(
                    "my_khatms.creator.target_saved" if field == "target"
                    else "my_khatms.creator.deadline_saved",
                    lang, value=value,
                )
            elif field == "end_at":
                end_at = datetime.strptime(value, "%Y-%m-%d %H:%M").replace(
                    tzinfo=ZoneInfo(get_settings().app_timezone)
                )
                khatm = await khatm_service.set_end_at(
                    session, khatm_id=khatm_id, creator_user_id=user.id, end_at=end_at
                )
                result = t("my_khatms.creator.end_at_saved", lang, value=value)
            else:
                datetime.strptime(value, "%Y-%m-%d")
                khatm = await khatm_service.set_schedule(
                    session, khatm_id=khatm_id, creator_user_id=user.id,
                    raw=f"date:{value}",
                )
                result = t("my_khatms.creator.schedule_date_saved", lang, value=value)
        except ValueError:
            await message.answer(t("my_khatms.creator.edit_value_invalid", lang))
            return
    await state.clear()
    await message.answer(result, reply_markup=_creator_settings_markup(khatm, lang))


@router.callback_query(F.data.startswith("cs:mode:"))
async def creator_set_content_mode(callback) -> None:
    _prefix, _mode_key, khatm_id, raw_mode = callback.data.split(":", 3)
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        mode = ContentDeliveryMode(raw_mode)
    except ValueError:
        await safe_answer_callback(callback, t("my_khatms.creator.mode_invalid", lang), show_alert=True)
        return
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if user is None:
            await safe_answer_callback(callback, t("my_khatms.creator.account_not_found", lang), show_alert=True)
            return
        try:
            await content_service.set_content_delivery_mode(
                session, khatm_id=khatm_id, creator_user_id=user.id, mode=mode
            )
            khatm = await khatm_service.get_khatm(session, khatm_id)
        except (ValueError, TypeError):
            await safe_answer_callback(callback, t("my_khatms.creator.setting_not_available", lang), show_alert=True)
            return
    await callback.message.edit_text(
        _creator_settings_text(khatm, lang), reply_markup=_creator_settings_markup(khatm, lang)
    )
    await safe_answer_callback(callback, t("my_khatms.creator.mode_saved", lang))


@router.callback_query(F.data.startswith("cs:pause:") | F.data.startswith("cs:snooze:"))
async def creator_toggle_policy(callback) -> None:
    _prefix, action, khatm_id = callback.data.split(":", 2)
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if user is None or khatm is None or khatm.creator_user_id != user.id:
            await safe_answer_callback(callback, t("my_khatms.no_permission", lang), show_alert=True)
            return
        try:
            if action == "pause":
                khatm = await khatm_service.set_allow_pause(
                    session, khatm_id=khatm.id, creator_user_id=user.id,
                    enabled=not bool(khatm.allow_pause),
                )
                label = t("my_khatms.creator.policy_label.pause", lang)
            else:
                khatm = await khatm_service.set_allow_snooze(
                    session, khatm_id=khatm.id, creator_user_id=user.id,
                    enabled=not bool(khatm.allow_snooze),
                )
                label = t("my_khatms.creator.policy_label.snooze", lang)
        except ValueError:
            await safe_answer_callback(callback, t("my_khatms.creator.setting_not_available", lang), show_alert=True)
            return
    await callback.message.edit_text(
        _creator_settings_text(khatm, lang), reply_markup=_creator_settings_markup(khatm, lang)
    )
    enabled = {"pause": khatm.allow_pause, "snooze": khatm.allow_snooze}[action]
    await safe_answer_callback(
        callback,
        t(
            "my_khatms.creator.policy_toggled_on" if enabled else "my_khatms.creator.policy_toggled_off",
            lang, label=label,
        ),
    )


@router.message(Command("creator_app", "creator_web_login"))
async def creator_web_login(message: Message) -> None:
    """Open the signed Telegram Mini App for a khatm creator."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    base_url = get_settings().admin_web_base_url.rstrip("/")
    if not base_url.lower().startswith("https://"):
        # Reject before any DB access so the error path is safe without a live DB.
        await message.answer(t("my_khatms.creator.mini_app_https_pending", "fa"))
        return
    lang = await _lang_for(message.chat.id, message.bot)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(
            session, platform, str(message.chat.id)
        )
        if user is None or not await khatm_service.list_my_created(session, user.id):
            await message.answer(t("my_khatms.creator.mini_app_needs_khatm", lang))
            return
    if platform != Platform.TELEGRAM:
        await message.answer(t("my_khatms.creator.mini_app_bale_unsupported", lang))
        return
    login_url = f"{base_url}/mini/creator"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=t("my_khatms.creator.mini_app_open_button", lang), web_app=WebAppInfo(url=login_url)
        )]]
    )
    await message.answer(
        t("my_khatms.creator.mini_app_open_prompt", lang),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "creator:web_login")
async def creator_web_login_button(callback) -> None:
    await creator_web_login(callback.message)
    await safe_answer_callback(callback)


def _khatm_bucket(khatm) -> str:
    """Canonical (language-independent) bucket key; translate at display
    time with `_BUCKET_KEYS[bucket]` — see `list_my_khatms`."""
    if khatm.status.value in {"COMPLETED", "CANCELLED"}:
        return "FINISHED"
    if not khatm_service.has_started(khatm):
        return "UPCOMING"
    return "ACTIVE"


_BUCKET_KEYS = {
    "ACTIVE": "my_khatms.bucket.active",
    "UPCOMING": "my_khatms.bucket.upcoming",
    "FINISHED": "my_khatms.bucket.finished",
}


@router.message(Command("khatm_members"))
async def khatm_members(message: Message, command: CommandObject) -> None:
    """Show a creator a compact, private member/progress overview."""
    lang = await _lang_for(message.chat.id, message.bot)
    raw_id = (command.args or "").strip()
    try:
        khatm_id = UUID(raw_id)
    except ValueError:
        await message.answer(t("my_khatms.creator.members_usage", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or khatm.creator_user_id != user.id:
            await message.answer(t("my_khatms.creator.khatm_not_found", lang))
            return
        members = await participation_service.list_active_with_users(session, khatm.id)
        portions = await allocation_service.list_for_khatm(session, khatm.id)

    if not members:
        await message.answer(t("my_khatms.creator.members_none", lang, title=khatm.title))
        return
    by_member: dict[object, list] = {}
    for portion in portions:
        if portion.participation_id is not None:
            by_member.setdefault(portion.participation_id, []).append(portion)
    lines = [t("my_khatms.creator.members_header", lang, title=khatm.title, count=len(members))]
    no_name = t("my_khatms.creator.member_no_name", lang)
    for participation, member in members:
        name = member.display_name or no_name
        assigned = by_member.get(participation.id, [])
        if assigned and assigned[0].quantity is not None:
            done = sum(p.completed_quantity for p in assigned)
            total = sum(p.quantity or 0 for p in assigned)
            progress_text = t("my_khatms.creator.member_progress_quantity", lang, done=done, total=total)
        elif assigned:
            done = sum(p.status.value == "COMPLETED" for p in assigned)
            progress_text = t(
                "my_khatms.creator.member_progress_portions", lang, current=len(assigned) - done, done=done
            )
        else:
            progress_text = t("my_khatms.creator.member_no_portion_yet", lang)
        flags = []
        if participation.is_committed:
            flags.append(t("my_khatms.creator.member_flag_committed", lang))
        if participation.backup_reader_opt_in:
            flags.append(t("my_khatms.creator.member_flag_backup", lang))
        lines.append(f"— {name}: {progress_text}" + (f" ({'، '.join(flags)})" if flags else ""))
    await message.answer("\n".join(lines))


@router.message(Command("khatm_member"))
async def khatm_member_detail(message: Message, command: CommandObject) -> None:
    """Show one active participant's private creator-facing detail."""
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split()
    if len(parts) != 2:
        await message.answer(t("my_khatms.creator.member_detail_usage", lang))
        return
    try:
        khatm_id, participation_id = UUID(parts[0]), UUID(parts[1])
    except ValueError:
        await message.answer(t("my_khatms.creator.member_detail_invalid_ids", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        creator = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        khatm = await khatm_service.get_khatm(session, khatm_id)
        participation = await participation_service.get_by_id(session, participation_id)
        if (
            creator is None or khatm is None or khatm.creator_user_id != creator.id
            or participation is None or participation.khatm_id != khatm.id
            or participation.status.value != "ACTIVE"
        ):
            await message.answer(t("my_khatms.creator.member_not_found", lang))
            return
        member = await identity_service.find_by_id(session, participation.user_id)
        current = await allocation_service.get_current_portion(session, khatm.id, participation.id)
        portions = await allocation_service.list_for_khatm(session, khatm.id)
        owned = [p for p in portions if p.participation_id == participation.id]
        misses = await notification_service.total_miss_count(
            session, participation.id,
            window_days=getattr(khatm, "miss_notice_window_days", 7),
        )
        preference = await notification_service.get_preference(session, participation.id)
    name = member.display_name if member and member.display_name else t("my_khatms.creator.member_no_name", lang)
    if owned and owned[0].quantity is not None:
        progress = f"{sum(p.completed_quantity for p in owned)}/{sum(p.quantity or 0 for p in owned)}"
    elif owned:
        done = sum(p.status.value == "COMPLETED" for p in owned)
        progress = f"{done}/{len(owned)}"
    else:
        progress = t("my_khatms.creator.no_portion", lang)
    if current is None:
        current_text = t("my_khatms.creator.no_portion", lang)
    elif current.quantity is not None:
        current_text = t(
            "my_khatms.creator.current_portion_quantity", lang, done=current.completed_quantity, total=current.quantity
        )
    else:
        current_text = t(
            "my_khatms.creator.current_portion_pages", lang, start=current.unit_start, end=current.unit_end
        )
    pause_text = t("my_khatms.creator.pause_none", lang) if participation.paused_until is None else str(participation.paused_until)
    reminder_text = (
        t("my_khatms.creator.reminder_off", lang)
        if preference is not None and not preference.enabled
        else f"{preference.reminder_hour if preference else 9}:00"
    )
    await message.answer(
        t(
            "my_khatms.creator.member_detail", lang,
            name=name, title=khatm.title, progress=progress, current=current_text,
            misses=misses, reminder=reminder_text, pause=pause_text,
            committed=t("my_khatms.creator.yes", lang) if participation.is_committed else t("my_khatms.creator.no", lang),
        )
    )


@router.message(Command("khatm_attention"))
async def khatm_attention(message: Message, command: CommandObject) -> None:
    """Show active members with recorded missed-deadline follow-ups."""
    lang = await _lang_for(message.chat.id, message.bot)
    raw_id = (command.args or "").strip()
    try:
        khatm_id = UUID(raw_id)
    except ValueError:
        await message.answer(t("my_khatms.creator.attention_usage", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or khatm.creator_user_id != user.id:
            await message.answer(t("my_khatms.creator.khatm_not_found", lang))
            return
        members = await participation_service.list_active_with_users(session, khatm.id)
        attention = []
        no_name = t("my_khatms.creator.member_no_name", lang)
        for participation, member in members:
            misses = await notification_service.total_miss_count(
                session, participation.id,
                window_days=getattr(khatm, "miss_notice_window_days", 7),
            )
            if misses:
                attention.append((member.display_name or no_name, misses))
    if not attention:
        await message.answer(t("my_khatms.creator.attention_empty", lang, title=khatm.title))
        return
    lines = [t("my_khatms.creator.attention_header", lang, title=khatm.title)]
    lines.extend(
        t("my_khatms.creator.attention_line", lang, name=name, misses=misses) for name, misses in attention
    )
    await message.answer("\n".join(lines))


@router.message(Command("khatm_export"))
async def khatm_export(message: Message, command: CommandObject) -> None:
    """Export the creator's active-member overview as an in-memory CSV."""
    lang = await _lang_for(message.chat.id, message.bot)
    raw_id = (command.args or "").strip()
    try:
        khatm_id = UUID(raw_id)
    except ValueError:
        await message.answer(t("my_khatms.creator.export_usage", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or khatm.creator_user_id != user.id:
            await message.answer(t("my_khatms.creator.khatm_not_found", lang))
            return
        members = await participation_service.list_active_with_users(session, khatm.id)
        portions = await allocation_service.list_for_khatm(session, khatm.id)
        by_member: dict[object, list] = {}
        for portion in portions:
            if portion.participation_id is not None:
                by_member.setdefault(portion.participation_id, []).append(portion)
        no_name = t("my_khatms.creator.member_no_name", lang)
        yes_label, no_label = t("my_khatms.creator.yes", lang), t("my_khatms.creator.no", lang)
        rows = []
        for participation, member in members:
            assigned = by_member.get(participation.id, [])
            if assigned and assigned[0].quantity is not None:
                progress = f"{sum(p.completed_quantity for p in assigned)}/{sum(p.quantity or 0 for p in assigned)}"
            elif assigned:
                done = sum(p.status.value == "COMPLETED" for p in assigned)
                progress = f"{done}/{len(assigned)}"
            else:
                progress = "0/0"
            misses = await notification_service.total_miss_count(
                session, participation.id,
                window_days=getattr(khatm, "miss_notice_window_days", 7),
            )
            rows.append([
                member.display_name or no_name,
                yes_label if participation.is_committed else no_label,
                yes_label if participation.backup_reader_opt_in else no_label,
                progress,
                misses,
            ])
    if not rows:
        await message.answer(t("my_khatms.creator.export_empty", lang, title=khatm.title))
        return
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([
        t("my_khatms.creator.export_column.name", lang),
        t("my_khatms.creator.export_column.committed", lang),
        t("my_khatms.creator.export_column.backup", lang),
        t("my_khatms.creator.export_column.progress", lang),
        t("my_khatms.creator.export_column.misses", lang),
    ])
    writer.writerows(rows)
    document = BufferedInputFile(output.getvalue().encode("utf-8-sig"), filename="khatm_members.csv")
    await message.answer_document(document=document, caption=t("my_khatms.creator.export_caption", lang, title=khatm.title))


@router.message(Command("khatm_stats"))
async def khatm_stats(message: Message, command: CommandObject) -> None:
    """Show creator analytics and invitation-funnel counts for one khatm."""
    lang = await _lang_for(message.chat.id, message.bot)
    raw_id = (command.args or "").strip()
    try:
        khatm_id = UUID(raw_id)
    except ValueError:
        await message.answer(t("my_khatms.creator.stats_usage", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if user is None or khatm is None or khatm.creator_user_id != user.id:
            await message.answer(t("my_khatms.creator.khatm_not_found", lang))
            return
        if await phone_repository.verified_claim_for_user(session, user.id) is None:
            # Real bug fixed here (2026-09-21): this branch referenced an
            # undefined `callback` — this handler only ever receives a
            # `Message`, never a `CallbackQuery` (it's a typed-command
            # handler, and `creator_report_callback` only forwards to it
            # with a fabricated `CommandObject`, not a real callback). Any
            # creator with an unverified phone hitting /khatm_stats would
            # have gotten a NameError instead of this message.
            await message.answer(t("my_khatms.creator.phone_not_verified", lang))
            return
        stats = await reporting_service.get_khatm_stats(session, khatm.id)
    await message.answer(
        t(
            "my_khatms.creator.stats_message", lang,
            title=khatm.title, total_members=stats.total_members, active_members=stats.active_members,
            completed_members=stats.completed_members, committed_members=stats.committed_members,
            completed_portions=stats.completed_portions, total_portions=stats.total_portions,
            contribution_total=stats.contribution_total, invitations_accepted=stats.invitations_accepted,
            invitations_issued=stats.invitations_issued,
            invitation_conversion_percent=stats.invitation_conversion_percent,
        )
    )


@router.message(Command("khatm_qr"))
async def khatm_qr(message: Message, command: CommandObject) -> None:
    """Issue a tracked invitation and return the member-bot join links + QR."""
    lang = await _lang_for(message.chat.id, message.bot)
    raw_id = (command.args or "").strip()
    try:
        khatm_id = UUID(raw_id)
    except ValueError:
        await message.answer(t("my_khatms.creator.qr_usage", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    settings = get_settings()
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if user is None or khatm is None or khatm.creator_user_id != user.id:
            await message.answer(t("my_khatms.creator.khatm_not_found", lang))
            return
        if khatm.status.value != "ACTIVE":
            await message.answer(t("my_khatms.creator.qr_active_only", lang))
            return
        token = await invitation_service.create_invitation(session, khatm.id, user.id)
        khatm_bot_cat = await invite_links.resolve_khatm_category_value(session, khatm)

    # Build the correct per-language member-bot deep links (the whole point of
    # the multi-bot split — the creator must be able to share the member links,
    # not just the web landing page).
    by_lang = invite_links.build_member_invite_links(khatm_bot_cat, token)
    if not by_lang:
        # No member bot configured for this category yet — fall back to the web
        # landing page so the creator still has something shareable.
        if settings.public_web_base_url:
            invite_url = f"{settings.public_web_base_url.rstrip('/')}/join/{token}"
            photo = BufferedInputFile(build_qr_png(invite_url), filename="khatm_invite_qr.png")
            await message.answer_photo(
                photo=photo,
                caption=t("my_khatms.creator.qr_caption", lang, title=escape(khatm.title), url=invite_url),
            )
        else:
            await message.answer(t("my_khatms.creator.qr_no_member_bots", lang))
        return

    invite_lines = invite_links.format_invite_lines(by_lang)
    primary = invite_links.pick_primary_link(
        by_lang, preferred_lang=lang, preferred_platform=platform.value
    )
    from aiogram.types import LinkPreviewOptions

    caption = t(
        "my_khatms.creator.qr_caption_with_links",
        lang, title=escape(khatm.title), invite_lines=invite_lines,
    )
    if primary:
        photo = BufferedInputFile(build_qr_png(primary), filename="khatm_invite_qr.png")
        await message.answer_photo(photo=photo, caption=caption)
    else:
        await message.answer(caption, link_preview_options=LinkPreviewOptions(is_disabled=True))


@router.callback_query(F.data.startswith("creator_report:"))
async def creator_report_callback(callback) -> None:
    """Route creator report buttons through the same guarded command handlers."""
    _, report_kind, khatm_id = callback.data.split(":", 2)
    command = CommandObject(args=khatm_id)
    if report_kind == "members":
        await khatm_members(callback.message, command)
    elif report_kind == "attention":
        await khatm_attention(callback.message, command)
    elif report_kind == "export":
        await khatm_export(callback.message, command)
    elif report_kind == "stats":
        await khatm_stats(callback.message, command)
    elif report_kind == "qr":
        await khatm_qr(callback.message, command)
    await safe_answer_callback(callback)


@router.message(F.caption.startswith("/khatm_cover"))
async def submit_khatm_cover(message: Message) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (message.caption or "").strip().split()
    if len(parts) != 2:
        await message.answer(t("my_khatms.creator.cover_usage", lang))
        return
    try:
        khatm_id = UUID(parts[1])
    except ValueError:
        await message.answer(t("my_khatms.creator.cover_invalid_id", lang))
        return
    cover_ref = message.photo[-1].file_id if message.photo else (
        message.document.file_id if message.document else None
    )
    if not cover_ref:
        await message.answer(t("my_khatms.creator.cover_needs_image", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        try:
            khatm = await khatm_service.submit_cover(
                session, khatm_id=khatm_id, creator_user_id=user.id,
                cover_ref=cover_ref, platform=platform.value,
            )
        except ValueError:
            await message.answer(t("my_khatms.creator.cover_invalid", lang))
            return
        await audit_service.record(
            session, actor_user_id=user.id, target_khatm_id=khatm.id,
            action="KHATM_COVER_SUBMIT", details={"platform": platform.value},
        )
    await message.answer(t("my_khatms.creator.cover_submitted", lang))


@router.message(Command("khatm_content_mode"))
async def set_khatm_content_mode(message: Message, command: CommandObject) -> None:
    """Creator-only content format selector: auto, photo, or text."""
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split()
    if len(parts) != 2:
        await message.answer(t("my_khatms.creator.content_mode_usage", lang))
        return
    try:
        khatm_id = UUID(parts[0])
        mode = ContentDeliveryMode(parts[1].upper())
    except ValueError:
        await message.answer(t("my_khatms.creator.content_mode_choice_invalid", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        try:
            await content_service.set_content_delivery_mode(
                session, khatm_id=khatm_id, creator_user_id=user.id, mode=mode,
            )
        except (ValueError, TypeError):
            await message.answer(t("my_khatms.creator.khatm_not_found", lang))
            return
    label_keys = {
        ContentDeliveryMode.AUTO: "my_khatms.creator.content_mode_label.auto",
        ContentDeliveryMode.PHOTO: "my_khatms.creator.content_mode_label.photo",
        ContentDeliveryMode.TEXT: "my_khatms.creator.content_mode_label.text",
    }
    await message.answer(
        t("my_khatms.creator.content_mode_command_saved", lang, label=t(label_keys[mode], lang))
    )


@router.message(Command("khatm_pause"))
async def set_khatm_pause(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split()
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer(t("my_khatms.creator.on_off_usage", lang, command="/khatm_pause"))
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer(t("my_khatms.creator.invalid_khatm_id", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        try:
            khatm = await khatm_service.set_allow_pause(
                session, khatm_id=khatm_id, creator_user_id=user.id,
                enabled=parts[1].lower() == "on",
            )
        except ValueError:
            await message.answer(t("my_khatms.creator.pause_command_error", lang))
            return
    status = t("my_khatms.creator.status.on", lang) if khatm.allow_pause else t("my_khatms.creator.status.off", lang)
    await message.answer(t("my_khatms.creator.pause_command_saved", lang, title=khatm.title, status=status))


@router.message(Command("khatm_snooze"))
async def set_khatm_snooze(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split()
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer(t("my_khatms.creator.on_off_usage", lang, command="/khatm_snooze"))
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer(t("my_khatms.creator.invalid_khatm_id", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        try:
            khatm = await khatm_service.set_allow_snooze(
                session, khatm_id=khatm_id, creator_user_id=user.id,
                enabled=parts[1].lower() == "on",
            )
        except ValueError:
            await message.answer(t("my_khatms.creator.pause_command_error", lang))
            return
    status = t("my_khatms.creator.status.on", lang) if khatm.allow_snooze else t("my_khatms.creator.status.off", lang)
    await message.answer(t("my_khatms.creator.snooze_command_saved", lang, title=khatm.title, status=status))


@router.message(Command("khatm_end_at"))
async def set_khatm_end_at(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split(maxsplit=1)
    if len(parts) != 2:
        await message.answer(t("my_khatms.creator.end_at_usage", lang))
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer(t("my_khatms.creator.invalid_khatm_id", lang))
        return
    raw = parts[1].strip()
    end_at = None
    if raw.lower() != "clear":
        try:
            end_at = datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(
                tzinfo=ZoneInfo(get_settings().app_timezone)
            )
        except ValueError:
            await message.answer(t("my_khatms.creator.end_at_format_invalid", lang))
            return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        try:
            khatm = await khatm_service.set_end_at(
                session, khatm_id=khatm_id, creator_user_id=user.id,
                end_at=end_at,
            )
        except ValueError:
            await message.answer(t("my_khatms.creator.end_at_command_invalid", lang))
            return
    if khatm.end_at is None:
        await message.answer(t("my_khatms.creator.end_at_command_cleared", lang, title=khatm.title))
    else:
        value = khatm.end_at.astimezone(ZoneInfo(get_settings().app_timezone)).strftime('%Y-%m-%d %H:%M')
        await message.answer(t("my_khatms.creator.end_at_command_set", lang, title=khatm.title, value=value))


@router.message(Command("khatm_schedule"))
async def set_khatm_schedule(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split(maxsplit=1)
    if len(parts) != 2:
        await message.answer(t("my_khatms.creator.schedule_command_usage", lang))
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer(t("my_khatms.creator.invalid_khatm_id", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer(t("my_khatms.creator.account_not_found", lang))
            return
        try:
            khatm = await khatm_service.set_schedule(
                session, khatm_id=khatm_id, creator_user_id=user.id, raw=parts[1]
            )
        except ValueError:
            await message.answer(t("my_khatms.creator.schedule_command_invalid", lang))
            return
    await message.answer(t("my_khatms.creator.schedule_command_saved", lang, title=khatm.title))


@router.message(Command("khatm_edit_title"))
async def edit_khatm_title(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split(maxsplit=1)
    if len(parts) != 2:
        await message.answer(t("my_khatms.creator.title_usage", lang))
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer(t("my_khatms.creator.invalid_khatm_id", lang))
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        try:
            khatm = await khatm_service.update_title(session, khatm_id=khatm_id, creator_user_id=user.id, title=parts[1])
        except (AttributeError, ValueError):
            await message.answer(t("my_khatms.creator.title_command_invalid", lang))
            return
    await message.answer(t("my_khatms.creator.title_command_saved", lang, title=khatm.title))


@router.message(Command("khatm_edit_welcome"))
async def edit_khatm_welcome(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.chat.id, message.bot)
    parts = (command.args or "").strip().split(maxsplit=1)
    if len(parts) != 2:
        await message.answer(t("my_khatms.creator.welcome_usage", lang))
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer(t("my_khatms.creator.invalid_khatm_id", lang))
        return
    welcome = None if parts[1].lower() == "clear" else parts[1]
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        try:
            khatm = await khatm_service.update_welcome_text(
                session, khatm_id=khatm_id, creator_user_id=user.id, welcome_text=welcome
            )
        except (AttributeError, ValueError):
            await message.answer(t("my_khatms.creator.welcome_command_invalid", lang))
            return
    await message.answer(t("my_khatms.creator.welcome_command_saved", lang, title=khatm.title))


_BRANCHES = ("created", "joined", "finished")
_CATEGORY_ORDER = ("quran", "salawat", "dua", "laan")
_CATEGORY_LABEL_KEYS = {
    "quran": "my_khatms.category.quran",
    "salawat": "my_khatms.category.salawat",
    "dua": "my_khatms.category.dua",
    "laan": "my_khatms.category.laan",
}

# Item shape stored in the tree built by `_build_my_khatms_tree`: one line
# of summary text plus whatever action buttons apply to it (manage/
# contribute/pause/resume/leave) — exactly the buttons the old flat list
# used to show, just grouped now instead of dumped in one long message.
_TreeItem = dict  # {"line": str, "buttons": list[InlineKeyboardButton]}
_Tree = dict  # {branch: {category: list[_TreeItem]}}


async def _content_group(session, khatm) -> str:
    """Which of the four top-level content families (BACKLOG.md §18 level 2)
    a khatm belongs to, for grouping in the hierarchical "my khatms" view."""
    if khatm.template_type == KhatmTemplateType.QURAN_PAGE:
        return "quran"
    if khatm.content_category_id:
        category = await category_service.get(session, khatm.content_category_id)
        if category is not None:
            return category.group.value.lower()
    return "salawat"


async def _build_my_khatms_tree(session, user_id, lang: str) -> _Tree:
    """Owner request (2026-09-21, BACKLOG.md §18): "ختم‌های من" needs three
    top-level branches (created / joined / finished) each split by content
    type (Quran/Salawat/Dua/La'an), instead of one long scrolling text.
    This builds that nested structure fresh from the DB; navigation
    callbacks (`mk:*`) below just re-render slices of it — no FSM state is
    kept, so the view is always current."""
    tree: _Tree = {branch: {} for branch in _BRANCHES}

    created = await khatm_service.list_my_created(session, user_id)
    for khatm in created:
        bucket = _khatm_bucket(khatm)
        branch = "finished" if bucket == "FINISHED" else "created"
        category = await _content_group(session, khatm)
        line = t("my_khatms.created_line", lang, title=khatm.title, status=khatm.status.value)
        buttons = [InlineKeyboardButton(
            text=t("my_khatms.button.manage", lang, title=khatm.title),
            callback_data=f"my_khatms:manage:{khatm.id}",
        )]
        tree[branch].setdefault(category, []).append({"line": line, "buttons": buttons})

    for participation in await participation_service.list_my_active(session, user_id):
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        if khatm is None:
            continue
        bucket = _khatm_bucket(khatm)
        bucket_label = t(_BUCKET_KEYS[bucket], lang)
        branch = "finished" if bucket == "FINISHED" else "joined"
        category = await _content_group(session, khatm)
        buttons: list[InlineKeyboardButton] = []

        if khatm.khatm_type == KhatmTypeEnum.OPEN:
            total = await contribution_repository.total_for_participation(session, participation.id)
            line = t("my_khatms.open_line", lang, bucket=bucket_label, title=khatm.title, total=int(total))
            if bucket == "ACTIVE":
                buttons.append(InlineKeyboardButton(
                    text=t("my_khatms.button.contribute", lang, title=khatm.title),
                    callback_data=f"contribute:{khatm.id}",
                ))
        else:
            waiting_note = "" if participation.is_committed else t("my_khatms.waiting_note", lang)
            done, total_portions = await allocation_service.progress(session, khatm.id)
            line = t(
                "my_khatms.progress_line", lang,
                bucket=bucket_label, title=khatm.title, waiting_note=waiting_note,
                done=done, total=total_portions,
            )
            if bucket == "ACTIVE":
                if not participation.is_committed:
                    # Waitlisted (owner decision, 2026-09-20): free to
                    # contribute casually via the open pool (DEC-PY-0010).
                    buttons.append(InlineKeyboardButton(
                        text=t("my_khatms.button.contribute", lang, title=khatm.title),
                        callback_data=f"contribute:{khatm.id}",
                    ))
                elif khatm.template_type == KhatmTemplateType.QURAN_PAGE:
                    is_paused = await participation_service.is_paused(participation)
                    if is_paused:
                        buttons.append(InlineKeyboardButton(
                            text=t("my_khatms.button.resume", lang, title=khatm.title),
                            callback_data=f"resume:{participation.id}",
                        ))
                    elif khatm.allow_pause:
                        buttons.append(InlineKeyboardButton(
                            text=t("my_khatms.button.pause", lang, title=khatm.title),
                            callback_data=f"pause_ask:{khatm.id}",
                        ))

        buttons.append(InlineKeyboardButton(
            text=f"🚪 خروج از «{khatm.title}»", callback_data=f"leave_ask:{participation.id}",
        ))
        tree[branch].setdefault(category, []).append({"line": line, "buttons": buttons})

    return tree


def _tree_is_empty(tree: _Tree) -> bool:
    return not any(tree[branch] for branch in _BRANCHES)


def _render_my_khatms_root(tree: _Tree, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    text = t("my_khatms.root.header", lang)
    rows = [
        [InlineKeyboardButton(
            text=t(f"my_khatms.root.button.{branch}", lang, count=sum(len(v) for v in tree[branch].values())),
            callback_data=f"mk:b:{branch}",
        )]
        for branch in _BRANCHES
    ]
    return text, InlineKeyboardMarkup(inline_keyboard=rows)


def _render_my_khatms_branch(tree: _Tree, branch: str, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    categories = tree.get(branch, {})
    title = t(f"my_khatms.branch.title.{branch}", lang)
    text = f"{title}\n\n" + (
        t("my_khatms.branch.choose_category", lang) if categories else t("my_khatms.branch.empty", lang)
    )
    rows = []
    for category in _CATEGORY_ORDER:
        items = categories.get(category)
        if not items:
            continue
        label = t(_CATEGORY_LABEL_KEYS[category], lang)
        rows.append([InlineKeyboardButton(text=f"{label} ({len(items)})", callback_data=f"mk:c:{branch}:{category}")])
    rows.append([InlineKeyboardButton(text=t("my_khatms.button.back", lang), callback_data="mk:root")])
    return text, InlineKeyboardMarkup(inline_keyboard=rows)


def _render_my_khatms_category(tree: _Tree, branch: str, category: str, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    items = tree.get(branch, {}).get(category, [])
    label = t(_CATEGORY_LABEL_KEYS.get(category, "my_khatms.category.salawat"), lang)
    lines = [f"{t(f'my_khatms.branch.title.{branch}', lang)} — {label}", ""]
    rows: list[list[InlineKeyboardButton]] = []
    for item in items:
        lines.append(item["line"])
        if item["buttons"]:
            rows.append(item["buttons"])
    rows.append([InlineKeyboardButton(text=t("my_khatms.button.back", lang), callback_data=f"mk:b:{branch}")])
    return "\n".join(lines), InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("my_khatms"))
@router.message(F.text.in_(MY_KHATMS_BUTTON_TEXTS))
async def list_my_khatms(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        tree = await _build_my_khatms_tree(session, user.id, lang)

    if _tree_is_empty(tree):
        await message.answer(t("my_khatms.empty", lang))
        return

    text, keyboard = _render_my_khatms_root(tree, lang)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "mk:root")
async def my_khatms_show_root(callback) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        tree = await _build_my_khatms_tree(session, user.id, lang)
    text, keyboard = _render_my_khatms_root(tree, lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("mk:b:"))
async def my_khatms_show_branch(callback) -> None:
    branch = callback.data.split(":", 2)[2]
    if branch not in _BRANCHES:
        await safe_answer_callback(callback)
        return
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        tree = await _build_my_khatms_tree(session, user.id, lang)
    text, keyboard = _render_my_khatms_branch(tree, branch, lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("mk:c:"))
async def my_khatms_show_category(callback) -> None:
    _, _, branch, category = callback.data.split(":", 3)
    if branch not in _BRANCHES or category not in _CATEGORY_ORDER:
        await safe_answer_callback(callback)
        return
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        tree = await _build_my_khatms_tree(session, user.id, lang)
    text, keyboard = _render_my_khatms_category(tree, branch, category, lang)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("my_khatms:manage:"))
async def open_creator_management(callback) -> None:
    khatm_id = callback.data.split(":", 2)[2]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _user_id, khatm = await _owned_khatm_for_callback(callback, khatm_id)
    if khatm is None:
        await safe_answer_callback(callback, t("my_khatms.no_permission", lang), show_alert=True)
        return
    await callback.message.answer(
        t("my_khatms.manage_header", lang, title=khatm.title),
        reply_markup=creator_khatm_keyboard(
            khatm_id,
            can_cancel=khatm.status.value == "ACTIVE",
            lang=lang,
        ),
    )
    await safe_answer_callback(callback)


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


@router.callback_query(F.data.startswith("cat:"))
async def toggle_completion_announcement(callback) -> None:
    khatm_id = callback.data.split(":", 1)[1]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(
            session, platform, str(callback.from_user.id)
        )
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if user is None or khatm is None or khatm.creator_user_id != user.id:
            await safe_answer_callback(callback, t("my_khatms.no_permission", lang), show_alert=True)
            return
        try:
            updated = await khatm_service.set_completion_announcement(
                session,
                khatm_id=khatm.id,
                creator_user_id=user.id,
                enabled=not bool(khatm.completion_announcement_enabled),
            )
        except ValueError:
            await safe_answer_callback(
                callback, t("my_khatms.creator.completion_announcement_locked", lang), show_alert=True
            )
            return
    await callback.message.edit_reply_markup(
        reply_markup=creator_khatm_keyboard(
            str(updated.id),
            can_cancel=updated.status.value == "ACTIVE",
            lang=lang,
        )
    )
    await safe_answer_callback(
        callback,
        t(
            "my_khatms.creator.completion_announcement_on"
            if updated.completion_announcement_enabled
            else "my_khatms.creator.completion_announcement_off",
            lang,
        ),
    )


@router.callback_query(F.data.startswith("cancel_khatm_ask:"))
async def ask_cancel_khatm(callback) -> None:
    khatm_id = callback.data.split(":", 1)[1]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if user is None or khatm is None or khatm.creator_user_id != user.id:
            await safe_answer_callback(callback, t("my_khatms.no_permission", lang), show_alert=True)
            return
        await callback.message.answer(
            t(
                "my_khatms.creator.cancel_ask", lang,
                title=khatm.title, amount=max(0, khatm.creation_price_toman),
            ),
            reply_markup=cancel_khatm_confirm_keyboard(khatm_id, lang),
        )
    await safe_answer_callback(callback)


@router.callback_query(F.data == "cancel_khatm_cancel")
async def cancel_cancel_khatm(callback) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await safe_clear_inline_keyboard(callback.message)
    await safe_answer_callback(callback, t("my_khatms.creator.cancel_declined", lang))


@router.callback_query(F.data.startswith("cancel_khatm:"))
async def confirm_cancel_khatm(callback) -> None:
    khatm_id = callback.data.split(":", 1)[1]
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if user is None:
            await safe_answer_callback(callback, t("my_khatms.creator.cancel_no_access", lang), show_alert=True)
            return
        try:
            khatm, refunded = await workflow_service.cancel_khatm(
                session, khatm_id=khatm_id, creator_user_id=user.id
            )
        except workflow_service.KhatmCancellationError as exc:
            await safe_answer_callback(callback, str(exc), show_alert=True)
            return
        await audit_service.record(
            session, actor_user_id=user.id, target_khatm_id=khatm.id,
            action="KHATM_CANCEL_REFUND", details={"amount_toman": refunded},
        )
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("my_khatms.creator.cancelled", lang, title=khatm.title, amount=refunded),
        reply_markup=main_menu_keyboard(lang),
    )
    await safe_answer_callback(callback)
