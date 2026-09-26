"""Portion completion (Quran pages, commitment) and free-form contribution
logging (Salawat, open). See DOMAIN_MODEL.md §3: completion is single-tap,
no confirmation dialog, no proof required.
"""

from datetime import datetime, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import (
    bail_if_menu_button,
    contribute_keyboard,
    commitment_quantity_keyboard,
    delivery_hour_keyboard,
    home_keyboard_for_bot,
    is_member_bot,
    main_menu_keyboard,
    pause_duration_keyboard,
    portion_done_keyboard,
    post_completion_keyboard,
    safe_answer_callback,
    safe_clear_inline_keyboard,
    snooze_keyboard,
)
from khatmsaz.core.db import session_scope
from khatmsaz.config import get_settings
from khatmsaz.i18n import t
from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmTemplateType
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.open_contribution import service as contribution_service
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.advertising import service as advertising_service
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.participation import repository as participation_repository
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings import service as settings_service

router = Router(name="portions")


class LogContribution(StatesGroup):
    entering_amount = State()


class SetupOpenQuranReading(StatesGroup):
    """Owner request (2026-09-21): the first time a non-committed (open or
    waitlisted) Quran reader taps "ثبت مشارکت", ask how many pages/day they
    want and what hour to send them, instead of only ever logging a bare
    number with no actual page content delivered — see
    `reminder_engine.service.deliver_due_open_quran_reading`."""

    entering_pages_per_day = State()
    entering_hour = State()


class PauseCommitment(StatesGroup):
    entering_until = State()


class CustomSnooze(StatesGroup):
    entering_until = State()


async def _lang_for(chat_id, bot) -> str:
    if is_member_bot(bot):
        return getattr(bot, "khatmsaz_language", "fa")
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


# Owner-reported bug (2026-09-21): plain Salawat must never ask the
# creator for text — Salawat wording is always the fixed standard text.
# A creator-authored recitation text (`Khatm.description`, from
# create_khatm.py's `entering_recitation_text` step) now only exists for
# La'an khatms. Dua/Salawat content comes from the admin-managed
# devotional library via `KhatmCategory.devotional_slug` — an explicit
# link (BACKLOG.md §14), replacing the old fragile name-matching hint
# dict (kept only as a fallback for categories an admin hasn't linked
# yet, so nothing silently stops working after this change).
_CATEGORY_DEVOTIONAL_SLUG_HINTS = {"عاشورا": "ziyarat-ashura"}


async def _send_recitation_content(session, message: Message, khatm) -> None:
    if khatm.template_type != KhatmTemplateType.SALAWAT:
        return
    if khatm.description:
        # Creator-authored free text (La'an only) — escape it since the
        # bot's default parse mode is HTML and this is untrusted creator
        # input, unlike the curated devotional-library text below.
        await message.answer(escape(khatm.description))
        return
    slug = "salawat"
    if khatm.content_category_id:
        category = await category_service.get(session, khatm.content_category_id)
        slug = None
        if category:
            slug = category.devotional_slug
            if slug is None:
                for hint, hint_slug in _CATEGORY_DEVOTIONAL_SLUG_HINTS.items():
                    if hint in category.title:
                        slug = hint_slug
                        break
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = await _lang_for(message.chat.id, message.bot)

    if category and category.image_url:
        from aiogram.types import URLInputFile
        try:
            await message.answer_photo(URLInputFile(category.image_url))
        except Exception:
            pass # fallback if URL is invalid

    if slug is None:
        if category and category.body_text:
            await message.answer(escape(category.body_text))
        return

    asset = await content_service.get_devotional_asset(session, slug)
    if asset is None:
        if category and category.body_text:
            await message.answer(escape(category.body_text))
        return

    if asset.text_body:
        for chunk in asset.text_body.split("\x1e"):
            await message.answer(chunk)
    elif category and category.body_text:
        await message.answer(escape(category.body_text))

    from khatmsaz.bot.handlers.devotional import deliver_devotional_media
    await deliver_devotional_media(session, message, slug=slug, asset=asset, platform=platform, lang=lang)


async def _invite_friends_line(session, khatm, creator_user_id, platform: Platform, lang: str, *, bot=None) -> str:
    """Owner request (2026-09-20): every "your portion was logged" message
    ends with an invite link to this same khatm, so a participant can share
    their own moment of sawab with friends — mirrors a sample message from a
    comparable bot. Same URL-building rule as the QR invite in
    `my_khatms.py::send_invite_qr`."""
    settings = get_settings()
    # For member bots, use that bot's own username so the link points to the
    # correct member bot rather than the creator bot.
    member_username = getattr(bot, "khatmsaz_username", None) if bot else None
    if member_username:
        if platform == Platform.TELEGRAM:
            base_url = f"https://t.me/{member_username}"
        else:
            base_url = f"https://ble.ir/{member_username}"
    else:
        if platform == Platform.TELEGRAM:
            username = settings.telegram_bot_username
            base_url = f"https://t.me/{username}" if username else ""
        else:
            username = settings.bale_bot_username
            base_url = f"https://ble.ir/{username}" if username else ""
    if not base_url:
        return ""
    token = await invitation_service.create_invitation(session, khatm.id, creator_user_id)
    invite_url = (
        f"{settings.public_web_base_url.rstrip('/')}/join/{token}"
        if settings.public_web_base_url
        else f"{base_url}?start=join_{token}"
    )
    return t("portions.invite_friends_line", lang, invite_url=invite_url)


@router.callback_query(F.data.startswith("snooze_ask:"))
async def ask_snooze(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or not khatm.allow_snooze:
        await safe_answer_callback(callback, t("portions.snooze_not_allowed", lang), show_alert=True)
        return
    await callback.message.answer(
        t("portions.ask_snooze_duration", lang),
        reply_markup=snooze_keyboard(khatm_id),
    )
    await safe_answer_callback(callback)


_SNOOZE_LABEL_KEYS = {30: "portions.snooze_label.30", 60: "portions.snooze_label.60", 180: "portions.snooze_label.180"}


@router.callback_query(F.data.startswith("snooze:"))
async def apply_snooze(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _, khatm_id, minutes_text = callback.data.split(":", 2)
    minutes = int(minutes_text)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        if participation is None:
            await safe_answer_callback(callback, t("portions.not_a_member", lang), show_alert=True)
            return
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or not khatm.allow_snooze:
            await safe_answer_callback(callback, t("portions.snooze_not_allowed", lang), show_alert=True)
            return
        await notification_service.snooze(session, participation.id, minutes)
    await safe_clear_inline_keyboard(callback.message)
    label = t(_SNOOZE_LABEL_KEYS[minutes], lang)
    await callback.message.answer(t("portions.snoozed", lang, label=label))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("snooze_custom:"))
async def ask_custom_snooze(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or not khatm.allow_snooze:
        await safe_answer_callback(callback, t("portions.snooze_not_allowed", lang), show_alert=True)
        return
    await state.set_state(CustomSnooze.entering_until)
    await state.update_data(snooze_khatm_id=khatm_id, lang=lang)
    await callback.message.answer(t("portions.ask_custom_snooze_time", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(CustomSnooze.entering_until))
async def receive_custom_snooze(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    text = (message.text or "").strip()
    try:
        hours = float(text)
        if hours <= 0 or hours > 24 * 365:
            raise ValueError
        local_until = datetime.now(ZoneInfo(get_settings().app_timezone)) + timedelta(hours=hours)
        until = local_until.astimezone(timezone.utc)
    except ValueError:
        try:
            local_until = datetime.strptime(text, "%Y-%m-%d %H:%M").replace(
                tzinfo=ZoneInfo(get_settings().app_timezone)
            )
            until = local_until.astimezone(timezone.utc)
        except ValueError:
            await message.answer(t("portions.time_format_invalid", lang))
            return
    khatm_id = data["snooze_khatm_id"]
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if participation is None or khatm is None or not khatm.allow_snooze:
            await state.clear()
            await message.answer(t("portions.khatm_inactive_or_not_member", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
            return
        try:
            await notification_service.snooze_until(session, participation.id, until)
        except ValueError:
            await message.answer(t("portions.snooze_must_be_future", lang))
            return
    await state.clear()
    await message.answer(t("portions.snooze_custom_saved", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))


def _unit_label(template_type: KhatmTemplateType, lang: str = "fa") -> str:
    return t("portions.unit.page", lang) if template_type == KhatmTemplateType.QURAN_PAGE else t("portions.unit.time", lang)


async def _send_registered_assets(message: Message, assets, kind: str) -> None:
    """Send each physical source post once, even when it covers several pages."""
    seen: set[str] = set()
    for asset in assets or []:
        if asset.asset_ref in seen:
            continue
        seen.add(asset.asset_ref)
        forward_source = content_service.decode_telegram_forward_ref(asset.asset_ref)
        if forward_source is not None:
            source_chat_id, source_message_id = forward_source
            await message.bot.forward_message(
                chat_id=message.chat.id,
                from_chat_id=source_chat_id,
                message_id=source_message_id,
            )
        elif kind == "image":
            await message.answer_photo(asset.asset_ref)
        elif kind == "audio":
            await message.answer_audio(asset.asset_ref)
        else:
            await message.answer(asset.asset_ref)


async def _deliver_quran_pages(
    session, message: Message, *, khatm, user_id, page_start: int, page_end: int, platform: Platform
) -> bool:
    """Send real Quran content (image/audio/text) for a page range —
    shared by the open-Quran-reading setup flow and its manual "ثبت
    مشارکت" logging (owner request, 2026-09-21: an open/waitlisted reader
    should actually receive the pages they read or were scheduled,
    not just have a bare number logged). Returns True if anything was
    sent."""
    delivery = await content_service.resolve_current_quran_delivery(
        session, khatm=khatm, user_id=user_id, page_start=page_start, page_end=page_end,
        asset_platform=platform.value,
    )
    sent = False
    for assets, kind in ((delivery["image"], "image"), (delivery["audio"], "audio"), (delivery["text"], "text")):
        if assets:
            sent = True
        await _send_registered_assets(message, assets, kind)
    return sent


@router.callback_query(F.data.startswith("content:"))
async def show_current_content(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if participation is None or khatm is None or khatm.template_type != KhatmTemplateType.QURAN_PAGE:
            await safe_answer_callback(callback, t("portions.no_active_quran_portion", lang), show_alert=True)
            return
        portion = await allocation_service.get_current_portion(session, khatm.id, participation.id)
        if portion is None or portion.unit_start is None or portion.unit_end is None:
            await safe_answer_callback(callback, t("portions.no_active_portion_to_show", lang), show_alert=True)
            return
        delivery = await content_service.resolve_current_quran_delivery(
            session, khatm=khatm, user_id=user.id,
            page_start=portion.unit_start, page_end=portion.unit_end,
            asset_platform=platform.value,
        )

    images = delivery["image"]
    audio = delivery["audio"]
    text_assets = delivery["text"]
    if not images and not audio and not text_assets:
        await callback.message.answer(
            t("portions.content_not_registered", lang, start=portion.unit_start, end=portion.unit_end)
        )
        await safe_answer_callback(callback)
        return
    await callback.message.answer(
        t("portions.your_portion_header", lang, start=portion.unit_start, end=portion.unit_end)
    )
    try:
        await _send_registered_assets(callback.message, images, "image")
        await _send_registered_assets(callback.message, audio, "audio")
        await _send_registered_assets(callback.message, text_assets, "text")
    except Exception:
        await callback.message.answer(t("portions.content_send_failed", lang))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("done:"))
async def mark_portion_done(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        if participation is None:
            await safe_answer_callback(callback, t("portions.not_a_member", lang), show_alert=True)
            return

        completed, _ = await allocation_service.complete_current_portion_and_advance(
            session, khatm_id, participation.id
        )
        khatm = await khatm_service.get_khatm(session, khatm_id)
        plan_completed = False
        has_more_ahead = False
        stacked_portion = None
        if completed is not None:
            done_count, total_count = await allocation_service.progress(session, khatm_id)
            plan_completed = total_count > 0 and done_count >= total_count
            if plan_completed:
                await khatm_service.complete_khatm(session, khatm_id)
            else:
                # Check if they have another portion already assigned (stacked up).
                # If they do, we'll prompt them to continue.
                # Otherwise, it arrives tomorrow at the participant's own reminder hour.
                stacked_portion = await allocation_service.get_current_portion(session, khatm_id, participation.id)
                has_more_ahead = (
                    await allocation_service.peek_next_open_portion(session, khatm_id) is not None
                )
        invite_line = ""
        if completed is not None and not plan_completed and khatm is not None:
            invite_line = await _invite_friends_line(session, khatm, khatm.creator_user_id, platform, lang)

    if completed is None:
        await safe_answer_callback(callback, t("portions.no_portion_to_complete", lang), show_alert=True)
        return

    await safe_clear_inline_keyboard(callback.message)
    if plan_completed:
        await callback.message.answer(
            t("portions.plan_completed", lang),
            reply_markup=post_completion_keyboard(
                khatm_id, undo_completed_id=str(completed.id), undo_next_id=None, lang=lang,
            ),
        )
    elif stacked_portion is not None:
        allow_snooze = bool(khatm and khatm.allow_snooze)
        await callback.message.answer(
            f"✅ سهم شما ({completed.unit_start} تا {completed.unit_end}) با موفقیت ثبت شد.\n\nشما هنوز سهم‌های عقب‌افتاده دارید (سهم بعدی: {stacked_portion.unit_start} تا {stacked_portion.unit_end}). هر زمان آماده بودید، دکمه «امروز» را از منو انتخاب کنید.{invite_line}",
            reply_markup=post_completion_keyboard(
                khatm_id, allow_snooze=allow_snooze,
                undo_completed_id=str(completed.id), undo_next_id=None, lang=lang,
            ),
        )
    elif has_more_ahead:
        allow_snooze = bool(khatm and khatm.allow_snooze)
        await callback.message.answer(
            t(
                "portions.page_done_next_tomorrow", lang,
                start=completed.unit_start, end=completed.unit_end,
                invite_line=invite_line,
            ),
            reply_markup=post_completion_keyboard(
                khatm_id, allow_snooze=allow_snooze,
                undo_completed_id=str(completed.id), undo_next_id=None, lang=lang,
            ),
        )
    else:
        allow_snooze = bool(khatm and khatm.allow_snooze)
        await callback.message.answer(
            t("portions.personal_portion_done", lang, invite_line=invite_line),
            reply_markup=post_completion_keyboard(
                khatm_id, allow_snooze=allow_snooze, undo_completed_id=str(completed.id), undo_next_id=None, lang=lang,
            ),
        )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("undo:"))
async def undo_last_completion(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _, completed_id, next_id = callback.data.split(":", 2)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        # The callback carries a portion id, so resolve ownership by the user
        # through the completed portion instead of trusting callback payload.
        portion = await session.get(allocation_service.KhatmPortion, completed_id)
        if portion is None:
            await safe_answer_callback(callback, t("portions.undo_not_found", lang), show_alert=True)
            return
        participation = await participation_repository.get_active(session, portion.khatm_id, user.id)
        if participation is None:
            await safe_answer_callback(callback, t("portions.undo_not_yours", lang), show_alert=True)
            return
        undone = await allocation_service.undo_completion(
            session, completed_id, participation.id, None if next_id == "none" else next_id
        )
        if undone:
            await khatm_service.reopen_after_completion_undo(session, portion.khatm_id)
    if not undone:
        await safe_answer_callback(callback, t("portions.undo_expired", lang), show_alert=True)
        return
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("portions.undo_done", lang), reply_markup=home_keyboard_for_bot(callback.message.bot, lang))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("contribute:"))
async def ask_contribution_amount(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        khatm = await khatm_service.get_khatm(session, khatm_id)
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)

    # Owner request (2026-09-21): the FIRST time a non-committed (open or
    # waitlisted) Quran reader wants to log/read, ask their daily page
    # count and delivery hour once, instead of only ever asking for a bare
    # number with nothing actually sent (BACKLOG.md — open Quran reading).
    if (
        khatm is not None and khatm.template_type == KhatmTemplateType.QURAN_PAGE
        and participation is not None and not participation.is_committed
        and participation.open_reading_pages_per_day is None
    ):
        await state.set_state(SetupOpenQuranReading.entering_pages_per_day)
        await state.update_data(khatm_id=khatm_id, lang=lang)
        await callback.message.answer(t("portions.open_quran.setup_ask_pages_per_day", lang))
        await safe_answer_callback(callback)
        return

    unit = _unit_label(khatm.template_type, lang) if khatm is not None else t("portions.unit.time", lang)

    await state.set_state(LogContribution.entering_amount)
    await state.update_data(khatm_id=khatm_id, lang=lang)
    await callback.message.answer(t("portions.ask_open_amount", lang, unit=unit))
    await safe_answer_callback(callback)


@router.message(StateFilter(SetupOpenQuranReading.entering_pages_per_day))
async def receive_open_quran_pages_per_day(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("portions.open_quran.pages_per_day_invalid", lang))
        return
    await state.update_data(pages_per_day=int(raw))
    await state.set_state(SetupOpenQuranReading.entering_hour)
    await message.answer(
        t("portions.open_quran.setup_ask_hour", lang),
        reply_markup=delivery_hour_keyboard("open_quran_hour", lang),
    )


async def _finish_open_quran_setup(message: Message, state: FSMContext, data: dict, hour: int) -> None:
    lang = data.get("lang", "fa")
    pages_per_day = data["pages_per_day"]
    khatm_id = data["khatm_id"]
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if participation is None or khatm is None:
            await state.clear()
            await message.answer(t("portions.not_a_member", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
            return
        await participation_service.set_open_reading_pages_per_day(session, participation.id, pages_per_day)
        await notification_service.set_reminder_preference(
            session, participation.id, reminder_hour=hour, enabled=True
        )
        total_pages = content_service.get_quran_total_pages(khatm)
        remaining = max(0, total_pages - participation.open_reading_next_page + 1)
        first_batch = min(pages_per_day, remaining)
        if first_batch <= 0:
            await state.clear()
            await message.answer(t("portions.open_quran.already_finished", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
            return
        reserved = await participation_service.advance_open_reading(session, participation.id, first_batch)
        start, end = reserved
        await participation_service.mark_open_reading_sent_now(session, participation.id)
        await _deliver_quran_pages(
            session, message, khatm=khatm, user_id=user.id, page_start=start, page_end=end, platform=platform
        )

    await state.clear()
    await message.answer(
        t("portions.open_quran.setup_done", lang, hour=hour, pages_per_day=pages_per_day, start=start, end=end),
        reply_markup=contribute_keyboard(khatm_id, lang),
    )


@router.callback_query(F.data.startswith("open_quran_hour:"), StateFilter(SetupOpenQuranReading.entering_hour))
async def receive_open_quran_hour_button(callback: CallbackQuery, state: FSMContext) -> None:
    hour = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await _finish_open_quran_setup(callback.message, state, data, hour)
    await safe_answer_callback(callback)


@router.message(StateFilter(SetupOpenQuranReading.entering_hour))
async def receive_open_quran_hour(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw = (message.text or "").strip()
    if not raw.isdigit() or not 0 <= int(raw) <= 23:
        await message.answer(t("portions.open_quran.hour_invalid", lang))
        return
    await _finish_open_quran_setup(message, state, data, int(raw))


@router.callback_query(F.data.startswith("commitment_contribute:"))
async def ask_commitment_quantity(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    await state.set_state(LogContribution.entering_amount)
    await state.update_data(khatm_id=khatm_id, commitment=True, lang=lang)
    await callback.message.answer(t("portions.ask_commitment_amount", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(LogContribution.entering_amount))
async def receive_contribution_amount(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("portions.positive_number_required", lang))
        return

    khatm_id = data["khatm_id"]
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        if participation is None:
            await state.clear()
            await message.answer(t("portions.not_a_member", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
            return

        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or khatm.status.name != "ACTIVE":
            await state.clear()
            await message.answer(t("portions.khatm_not_active", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
            return
        if data.get("commitment"):
            portion, counted, surplus = await allocation_service.record_quantity_commitment_progress(
                session, khatm_id, participation.id, int(raw)
            )
            if portion is None:
                await state.clear()
                await message.answer(t("portions.no_active_commitment", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
                return
            done = portion.status.name == "COMPLETED"
            target = portion.quantity or 0
            completed = portion.completed_quantity
            today_total, yesterday_total = await allocation_service.today_vs_yesterday_committed(
                session, khatm_id, get_settings().app_timezone
            )
            unit = _unit_label(khatm.template_type, lang)
            lines = [
                t("portions.commitment_recorded", lang, counted=int(counted)),
                t("portions.commitment_progress", lang, completed=completed, target=target),
            ]
            if surplus:
                lines.append(t("portions.commitment_surplus", lang, surplus=int(surplus)))
            if not done:
                lines.append(
                    t("portions.today_vs_yesterday", lang, unit=unit, today=today_total, yesterday=yesterday_total)
                )
            if done:
                await advertising_service.accrue_first_completed_action(session, participation.id)
                lines.append(t("portions.personal_commitment_done", lang))
            else:
                lines.append(await _invite_friends_line(session, khatm, khatm.creator_user_id, platform, lang))
            await state.clear()
            await message.answer(
                "\n".join(lines),
                reply_markup=home_keyboard_for_bot(message.bot, lang) if done else commitment_quantity_keyboard(khatm_id, lang),
            )
            await _send_recitation_content(session, message, khatm)
            return
        counted, surplus, new_total = await contribution_service.log_contribution(
            session, khatm_id, participation.id, int(raw), khatm.repetition_target
        )
        await advertising_service.accrue_first_completed_action(session, participation.id)
        reached = khatm.repetition_target is not None and new_total >= khatm.repetition_target

        # Owner request (2026-09-21): an open/waitlisted Quran reader who
        # self-reports reading N pages should actually be sent those N
        # pages' real content (image/audio/text) — not just have a bare
        # number logged with nothing delivered. Advances the same cursor
        # the daily auto-send uses, capped to what's left in the edition,
        # and marks "sent today" so the auto-send doesn't duplicate it.
        quran_pages_sent = None
        if khatm.template_type == KhatmTemplateType.QURAN_PAGE:
            total_pages = content_service.get_quran_total_pages(khatm)
            remaining = max(0, total_pages - participation.open_reading_next_page + 1)
            to_send = min(int(raw), remaining)
            if to_send > 0:
                reserved = await participation_service.advance_open_reading(session, participation.id, to_send)
                quran_pages_sent = reserved
                await participation_service.mark_open_reading_sent_now(session, participation.id)
                await _deliver_quran_pages(
                    session, message, khatm=khatm, user_id=user.id,
                    page_start=reserved[0], page_end=reserved[1], platform=platform,
                )

        invite_line = "" if reached else await _invite_friends_line(session, khatm, khatm.creator_user_id, platform, lang)
        today_total, yesterday_total = await contribution_service.today_vs_yesterday(
            session, khatm_id, get_settings().app_timezone
        )

    await state.clear()
    unit = _unit_label(khatm.template_type, lang)

    lines = [t("portions.open_recorded", lang, amount=int(raw), unit=unit)]
    if quran_pages_sent is not None:
        lines.append(t("portions.open_quran.pages_sent", lang, start=quran_pages_sent[0], end=quran_pages_sent[1]))
    if surplus > 0:
        lines.append(t("portions.open_surplus_split", lang, counted=int(counted), surplus=int(surplus), unit=unit))

    if khatm.repetition_target:
        lines.append(
            t(
                "portions.overall_progress", lang,
                done=int(min(new_total, khatm.repetition_target)), target=khatm.repetition_target,
            )
        )

    if not reached:
        # Owner request (2026-09-20): show the group's running today-vs-
        # yesterday total so a member sees the number keep growing (others
        # log throughout the day, up to local midnight), instead of a
        # single frozen snapshot.
        lines.append(
            t("portions.today_vs_yesterday", lang, unit=unit, today=int(today_total), yesterday=int(yesterday_total))
        )
        lines.append(invite_line)

    if reached:
        lines.append(t("portions.goal_reached", lang))
        async with session_scope() as session:
            await khatm_service.complete_khatm(session, khatm_id)
        await message.answer("\n".join(lines), reply_markup=home_keyboard_for_bot(message.bot, lang))
    else:
        await message.answer("\n".join(lines), reply_markup=contribute_keyboard(khatm_id, lang))

    async with session_scope() as session:
        await _send_recitation_content(session, message, khatm)


@router.callback_query(F.data.startswith("pause_ask:"))
async def ask_pause_duration(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or not khatm.allow_pause:
        await safe_answer_callback(callback, t("portions.pause_not_allowed", lang), show_alert=True)
        return
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("portions.ask_pause_days", lang),
        reply_markup=pause_duration_keyboard(khatm_id),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("pause_custom:"))
async def ask_custom_pause_until(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    khatm_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or not khatm.allow_pause:
        await safe_answer_callback(callback, t("portions.pause_not_allowed", lang), show_alert=True)
        return
    await state.set_state(PauseCommitment.entering_until)
    await state.update_data(pause_khatm_id=khatm_id, lang=lang)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("portions.ask_custom_pause_until", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(PauseCommitment.entering_until))
async def receive_custom_pause_until(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw = (message.text or "").strip()
    try:
        local_until = datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(
            tzinfo=ZoneInfo(get_settings().app_timezone)
        )
    except ValueError:
        await message.answer(t("portions.pause_date_format_invalid", lang))
        return
    until = local_until.astimezone(timezone.utc)
    if until <= datetime.now(timezone.utc):
        await message.answer(t("portions.pause_must_be_future", lang))
        return
    khatm_id = data["pause_khatm_id"]
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if participation is None or khatm is None or not khatm.allow_pause:
            await state.clear()
            await message.answer(t("portions.khatm_inactive_or_not_yours", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))
            return
        await workflow_service.pause_commitment(session, participation.id, khatm_id, until)
    await state.clear()
    await message.answer(t("portions.pause_custom_saved", lang), reply_markup=home_keyboard_for_bot(message.bot, lang))


@router.callback_query(F.data.startswith("pause:"))
async def pause_commitment(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _, khatm_id, days_str = callback.data.split(":", 2)
    days = int(days_str)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        participation = await participation_repository.get_active(session, khatm_id, user.id)
        if participation is None:
            await safe_answer_callback(callback, t("portions.not_a_member", lang), show_alert=True)
            return
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or not khatm.allow_pause:
            await safe_answer_callback(callback, t("portions.pause_not_allowed", lang), show_alert=True)
            return
        until = datetime.now(timezone.utc) + timedelta(days=days)
        await workflow_service.pause_commitment(session, participation.id, khatm_id, until)

    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("portions.pause_days_saved", lang, days=days))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("resume:"))
async def resume_commitment(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    participation_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        await workflow_service.resume_commitment(session, participation_id)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("portions.resumed", lang))
    await safe_answer_callback(callback)
