"""Fully button-driven personal settings menu.

Every preference here used to be a typed slash command (`/language fa`,
`/timezone Asia/Tehran`, ...). The project's hard rule is that all bot
functionality must be reachable purely by tapping buttons (2026-09-18 user
instruction), so this router replaces the old text-heavy `settings_overview`
message with an inline-keyboard tree under the `settings:` / `set_*:`
callback namespaces. The old per-preference command handlers keep working
(harmless, still useful for power users who prefer typing) — this file does
not remove them, it only stops presenting them as the only way in.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import (
    SETTINGS_BUTTON_TEXTS,
    home_keyboard_for_bot,
    is_member_bot,
    main_menu_keyboard,
    member_menu_keyboard,
    settings_content_keyboard,
    settings_font_keyboard,
    settings_home_keyboard,
    settings_language_keyboard,
    settings_on_off_keyboard,
    settings_reciter_keyboard,
    settings_reminder_keyboard,
    settings_timezone_keyboard,
    sms_subscription_keyboard,
)
from khatmsaz.bot.handlers.profile import begin_profile
from khatmsaz.bot.handlers.change_phone import begin_phone_change
from khatmsaz.bot.handlers.account_link import begin_account_link
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.bot.member_scope import member_instance_id
from khatmsaz.modules.settings.models import FontSize
from khatmsaz.modules.sms_subscription import service as sms_subscription_service
from khatmsaz.modules.wallet.service import InsufficientFundsError

router = Router(name="settings_menu")


async def _current_platform_user(message: Message):
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        return user, settings


async def _lang_for(chat_id, bot) -> str:
    if is_member_bot(bot):
        return getattr(bot, "khatmsaz_language", "fa")
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


def _can_open_creator_panel(bot, user) -> bool:
    """Creators/Super-Admins on the creator bot may open their Mini App from
    Settings (owner 2026-09-29). Never on a member bot (no creator panel there;
    the `creator:web_login` handler is creator-dispatcher-only)."""
    from khatmsaz.modules.identity.models import UserRole
    if is_member_bot(bot):
        return False
    return getattr(user, "role", None) in (UserRole.CREATOR, UserRole.SUPER_ADMIN)


@router.message(F.text.in_(SETTINGS_BUTTON_TEXTS))
async def settings_overview(message: Message) -> None:
    user, settings = await _current_platform_user(message)
    lang = settings.language
    await message.answer(
        t("settings.home_text", lang),
        reply_markup=settings_home_keyboard(
            audio_enabled=settings.quran_audio_enabled, lang=lang,
            show_creator_panel=_can_open_creator_panel(message.bot, user),
        ),
    )


@router.callback_query(F.data == "settings:home")
async def settings_home(callback: CallbackQuery) -> None:
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
    lang = settings.language
    await callback.message.edit_text(
        t("settings.home_text", lang),
        reply_markup=settings_home_keyboard(
            audio_enabled=settings.quran_audio_enabled, lang=lang,
            show_creator_panel=_can_open_creator_panel(callback.bot, user),
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "settings:language")
async def settings_language_menu(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await callback.message.edit_text(t("settings.choose_language", lang), reply_markup=settings_language_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("set_language:"))
async def set_language(callback: CallbackQuery) -> None:
    # Member bots have a fixed language per bot — ignore language change attempts.
    if is_member_bot(callback.bot):
        lang = getattr(callback.bot, "khatmsaz_language", "fa")
        await callback.answer(t("settings.language_saved", lang))
        await settings_home(callback)
        await callback.message.answer(t("settings.language_saved", lang), reply_markup=member_menu_keyboard(lang))
        return
    value = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        await settings_service.set_language(session, user.id, value)
    await callback.answer(t("settings.language_saved", value))
    await settings_home(callback)
    # Bug fix (owner report, 2026-09-20): changing language only edited the
    # inline settings message; the persistent bottom Reply Keyboard (📅
    # امروز / 🕋 ختم‌های من / ...) is a *separate* keyboard that Telegram
    # only refreshes when a *new* message carries a new reply_markup — so
    # it silently stayed in the old language until some other action sent
    # a fresh main-menu message. Send one now so it updates immediately.
    await callback.message.answer(t("settings.language_saved", value), reply_markup=home_keyboard_for_bot(callback.message.bot, value))


@router.callback_query(F.data == "settings:font")
async def settings_font_menu(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await callback.message.edit_text(t("settings.choose_font", lang), reply_markup=settings_font_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("set_font:"))
async def set_font(callback: CallbackQuery) -> None:
    value = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        await settings_service.set_font_size(session, user.id, FontSize(value.upper()))
        settings = await settings_service.get_or_create(session, user.id)
    await callback.answer(t("settings.font_saved", settings.language))
    await settings_home(callback)


@router.callback_query(F.data == "settings:reciter")
async def settings_reciter_menu(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    reciters = content_service.list_reciters()
    await callback.message.edit_text(
        t("settings.choose_reciter", lang), reply_markup=settings_reciter_keyboard(reciters, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_reciter:"))
async def set_reciter(callback: CallbackQuery) -> None:
    value = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        await content_service.set_user_favorite(session, user.id, value)
        # Owner-reported bug (2026-09-21): "قاری رو فعال میکنم اما صوت
        # ارسال نمیشه" — picking a reciter here is an unambiguous "I want
        # audio" signal, but `quran_audio_enabled` is a separate flag
        # (default off, buried in a different settings screen) that this
        # never touched, so audio silently never sent. Turning it on here
        # matches the obvious intent of choosing a reciter at all.
        settings = await settings_service.set_quran_audio_enabled(session, user.id, True)
    await callback.answer(t("settings.reciter_saved", settings.language))
    await settings_home(callback)


@router.callback_query(F.data == "settings:content")
async def settings_content_menu(callback: CallbackQuery) -> None:
    _, settings = await _current_platform_user(callback.message)
    lang = settings.language
    await callback.message.edit_text(
        t("settings.content_menu", lang),
        reply_markup=settings_content_keyboard(
            translation_enabled=settings.translation_enabled, tafsir_enabled=settings.tafsir_enabled, lang=lang
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_content:"))
async def set_content_option(callback: CallbackQuery) -> None:
    _, option, value = callback.data.split(":", 2)
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        settings = await settings_service.set_content_option(session, user.id, option, value == "on")
    lang = settings.language
    await callback.answer(t("settings.saved", lang))
    await callback.message.edit_text(
        t("settings.content_menu", lang),
        reply_markup=settings_content_keyboard(
            translation_enabled=settings.translation_enabled, tafsir_enabled=settings.tafsir_enabled, lang=lang
        ),
    )


@router.callback_query(F.data == "settings:reminder")
async def settings_reminder_menu(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await callback.message.edit_text(
        t("settings.choose_reminder_hour", lang), reply_markup=settings_reminder_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_reminder:"))
async def set_reminder(callback: CallbackQuery) -> None:
    value = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        participations = await participation_service.list_my_active(
            session, user.id, joined_via_bot_instance_id=member_instance_id(callback.bot)
        )
        committed = [p for p in participations if p.is_committed]
        if value == "off":
            for participation in committed:
                await notification_service.set_reminder_preference(
                    session, participation.id, reminder_hour=9, enabled=False
                )
        else:
            hour = int(value)
            for participation in committed:
                await notification_service.set_reminder_preference(
                    session, participation.id, reminder_hour=hour, enabled=True
                )
    await callback.answer(t("settings.reminder_saved", settings.language))
    await settings_home(callback)


@router.callback_query(F.data == "settings:digest")
async def settings_digest_menu(callback: CallbackQuery) -> None:
    _, settings = await _current_platform_user(callback.message)
    lang = settings.language
    await callback.message.edit_text(
        t("settings.digest_menu", lang),
        reply_markup=settings_on_off_keyboard(prefix="set_digest", enabled=settings.daily_digest_enabled, lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_digest:"))
async def set_digest(callback: CallbackQuery) -> None:
    value = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        settings.daily_digest_enabled = value == "on"
        await session.flush()
        lang = settings.language
    await callback.answer(t("settings.saved", lang))
    await callback.message.edit_text(
        t("settings.digest_menu", lang),
        reply_markup=settings_on_off_keyboard(prefix="set_digest", enabled=(value == "on"), lang=lang),
    )


async def _sms_menu_text_and_keyboard(session, user_id, lang: str):
    active = await sms_subscription_service.is_active(session, user_id)
    expires_at = await sms_subscription_service.get_expiry(session, user_id)
    options = await sms_subscription_service.list_options(session)
    text = t("settings.sms_menu_title", lang)
    if active and expires_at is not None:
        text += t("settings.sms_active", lang, date=expires_at.strftime("%Y-%m-%d"))
    else:
        text += t("settings.sms_inactive", lang)
    text += t("settings.sms_buy_prompt", lang)
    return text, sms_subscription_keyboard(options, active=active, lang=lang)


@router.callback_query(F.data == "settings:sms")
async def settings_sms_menu(callback: CallbackQuery) -> None:
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        text, keyboard = await _sms_menu_text_and_keyboard(session, user.id, settings.language)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "set_sms:off")
async def turn_off_sms(callback: CallbackQuery) -> None:
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        await settings_service.set_sms_enabled(session, user.id, False)
        settings = await settings_service.get_or_create(session, user.id)
        text, keyboard = await _sms_menu_text_and_keyboard(session, user.id, settings.language)
    await callback.answer(t("settings.sms_off", settings.language))
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("sms_buy:"))
async def buy_sms_plan(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    try:
        months = int(callback.data.split(":", 1)[1])
    except (TypeError, ValueError, IndexError):
        await callback.answer(t("settings.sms_option_invalid", lang), show_alert=True)
        return
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        try:
            new_expiry = await sms_subscription_service.purchase(session, user.id, months)
        except sms_subscription_service.SmsContactPhoneRequiredError:
            await callback.answer(t("settings.sms_phone_required", lang), show_alert=True)
            return
        except InsufficientFundsError:
            await callback.answer(t("settings.sms_insufficient_funds", lang), show_alert=True)
            return
        except sms_subscription_service.SmsPlanUnavailableError:
            await callback.answer(t("settings.sms_plan_unavailable", lang), show_alert=True)
            return
        text, keyboard = await _sms_menu_text_and_keyboard(session, user.id, lang)
    await callback.answer(t("settings.sms_activated", lang, date=new_expiry.strftime("%Y-%m-%d")))
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "settings:timezone")
async def settings_timezone_menu(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await callback.message.edit_text(t("settings.choose_timezone", lang), reply_markup=settings_timezone_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("set_timezone:"))
async def set_timezone(callback: CallbackQuery) -> None:
    value = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        await settings_service.set_timezone(session, user.id, value)
        settings = await settings_service.get_or_create(session, user.id)
    await callback.answer(t("settings.timezone_saved", settings.language))
    await settings_home(callback)


@router.callback_query(F.data == "settings:profile")
async def settings_profile(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await begin_profile(callback.message, state)


@router.callback_query(F.data == "settings:change_phone")
async def settings_change_phone(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await begin_phone_change(callback.message, state)


@router.callback_query(F.data == "settings:link_account")
async def settings_link_account(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await begin_account_link(callback.message, state)
