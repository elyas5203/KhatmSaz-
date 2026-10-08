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
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton

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
    settings_reminder_custom_keyboard,
    settings_reminder_khatms_keyboard,
    settings_reminder_saved_keyboard,
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
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.bot.member_scope import member_instance_id
from khatmsaz.modules.settings.models import FontSize
from khatmsaz.modules.sms_subscription import service as sms_subscription_service
from khatmsaz.modules.wallet.service import InsufficientFundsError

router = Router(name="settings_menu")


class ReminderSettings(StatesGroup):
    entering_custom_time = State()
    entering_amount = State()


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
        t("settings.home_text", lang)
        + f"\n\nوضعیت فعلی:\n🕒 منطقه زمانی: {settings.timezone}\n🔊 صوت قرآن: {'روشن' if settings.quran_audio_enabled else 'خاموش'}",
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
        t("settings.home_text", lang)
        + f"\n\nوضعیت فعلی:\n🕒 منطقه زمانی: {settings.timezone}\n🔊 صوت قرآن: {'روشن' if settings.quran_audio_enabled else 'خاموش'}",
        reply_markup=settings_home_keyboard(
            audio_enabled=settings.quran_audio_enabled, lang=lang,
            show_creator_panel=_can_open_creator_panel(callback.bot, user),
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "settings:audio_toggle")
async def toggle_audio(callback: CallbackQuery) -> None:
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        new_val = not settings.quran_audio_enabled
        await settings_service.set_quran_audio_enabled(session, user.id, new_val)
    await settings_home(callback)


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
    _, settings = await _current_platform_user(callback.message)
    lang = settings.language
    current = "درشت" if settings.font_size == FontSize.LARGE else "معمولی"
    await callback.message.edit_text(f"اندازه فعلی متن: {current}\n\n{t('settings.choose_font', lang)}", reply_markup=settings_font_keyboard(lang))
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
    _, settings = await _current_platform_user(callback.message)
    lang = settings.language
    reciters = content_service.list_reciters()
    names = dict(reciters)
    current = names.get(settings.preferred_reciter or "", "انتخاب نشده")
    await callback.message.edit_text(
        f"قاری فعلی: {current}\n\n{t('settings.choose_reciter', lang)}", reply_markup=settings_reciter_keyboard(reciters, lang)
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
async def settings_reminder_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        participations = await participation_service.list_my_active(
            session, user.id, joined_via_bot_instance_id=member_instance_id(callback.bot)
        )
        items = []
        for participation in participations:
            khatm = await khatm_service.get_khatm(session, participation.khatm_id)
            if khatm is None:
                continue
            hour, minute = await notification_service.get_reminder_time(session, participation)
            items.append((str(participation.id), khatm.title, f"{hour:02d}:{minute:02d}"))
    text = "⏰ یادآوری هر ختم جدا تنظیم می‌شود.\n\nختم موردنظرت را انتخاب کن؛ ساعت فعلی روبه‌روی نامش نوشته شده است:"
    if not items:
        text = "فعلاً در این بات ختم فعالی نداری."
    await callback.message.edit_text(text, reply_markup=settings_reminder_khatms_keyboard(items, settings.language))
    await callback.answer()


async def _owned_reminder_context(session, callback: CallbackQuery, participation_id: str):
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
    settings = await settings_service.get_or_create(session, user.id)
    participations = await participation_service.list_my_active(
        session, user.id, joined_via_bot_instance_id=member_instance_id(callback.bot)
    )
    participation = next((item for item in participations if str(item.id) == participation_id), None)
    if participation is None:
        return settings, None, None
    return settings, participation, await khatm_service.get_khatm(session, participation.khatm_id)


@router.callback_query(F.data.startswith("reminder_khatm:"))
async def choose_reminder_khatm(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    participation_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        settings, participation, khatm = await _owned_reminder_context(session, callback, participation_id)
        if participation is None or khatm is None:
            await callback.answer("این ختم دیگر در فهرست فعال شما نیست.", show_alert=True)
            return
        hour, minute = await notification_service.get_reminder_time(session, participation)
    markup = settings_reminder_keyboard(participation_id, settings.language)
    if khatm.commitment_policy != "FIXED_DAILY":
        markup.inline_keyboard.insert(0, [InlineKeyboardButton(text="📖 تغییر مقدار سهم‌های بعدی", callback_data=f"share_amount:{participation_id}")])
    if khatm.template_type == "QURAN_PAGE":
        enabled = settings.quran_audio_enabled if participation.quran_audio_enabled is None else participation.quran_audio_enabled
        markup.inline_keyboard.insert(0, [InlineKeyboardButton(text=f"🔊 صوت این ختم: {'روشن' if enabled else 'خاموش'}", callback_data=f"share_audio:{participation_id}")])
    if khatm.commitment_policy != "FIXED_DAILY":
        markup.inline_keyboard.insert(0, [InlineKeyboardButton(text="📅 تغییر نوع و روزهای برنامه", callback_data=f"share_plan:{participation_id}")])
    await callback.message.edit_text(
        f"⏰ ختم «{khatm.title}»\n\nساعت فعلی یادآوری: {hour:02d}:{minute:02d}\n\nساعت تازه را انتخاب کن:",
        reply_markup=markup,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("share_audio:"))
async def toggle_share_audio(callback: CallbackQuery, state: FSMContext):
    pid = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        settings, part, khatm = await _owned_reminder_context(session, callback, pid)
        if part is None or khatm is None or khatm.template_type != "QURAN_PAGE":
            await callback.answer("این تنظیم برای این عضویت در دسترس نیست.", show_alert=True)
            return
        current = settings.quran_audio_enabled if part.quran_audio_enabled is None else part.quran_audio_enabled
        part.quran_audio_enabled = not current
    await callback.answer("صوت این ختم خاموش شد." if current else "صوت این ختم روشن شد.")


@router.callback_query(F.data.startswith("share_plan:"))
async def change_share_plan(callback: CallbackQuery, state: FSMContext):
    pid = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        settings, part, khatm = await _owned_reminder_context(session, callback, pid)
        if part is None or khatm is None or khatm.commitment_policy == "FIXED_DAILY":
            await callback.answer("برنامهٔ ثابت سازنده قابل تغییر نیست.", show_alert=True)
            return
        from khatmsaz.bot.member_copy import content_family
        family = (await content_family(session, khatm)).upper()
    from khatmsaz.bot.handlers.member_commitment import start_commitment_mode_picker
    await state.clear()
    await start_commitment_mode_picker(callback.message, state, part.id, settings.language, family=family)
    await callback.answer()


@router.callback_query(F.data.startswith("share_amount:"))
async def ask_share_amount(callback: CallbackQuery, state: FSMContext):
    pid = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        _, part, khatm = await _owned_reminder_context(session, callback, pid)
        if part is None or khatm is None or khatm.commitment_policy == "FIXED_DAILY":
            await callback.answer("مقدار ثابت سازنده قابل تغییر نیست.", show_alert=True)
            return
    await state.set_state(ReminderSettings.entering_amount)
    await state.update_data(amount_participation_id=pid)
    unit = "صفحه" if khatm.template_type == "QURAN_PAGE" else "مرتبه"
    await callback.message.answer(f"در هر نوبت چند {unit} می‌خواهید بخوانید؟\nتغییر فقط برای سهم‌های بعدی است؛ سهم‌های دریافت‌شده باقی می‌مانند.")
    await callback.answer()


@router.message(ReminderSettings.entering_amount)
async def save_share_amount(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    if not raw.isdecimal() or int(raw) <= 0 or int(raw) > 2147483647:
        await message.answer("لطفاً یک عدد مثبت معتبر بنویسید.")
        return
    data = await state.get_data()
    platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.from_user.id)
        part = await participation_service.get_by_id(session, data.get("amount_participation_id"))
        if part is None or part.user_id != user.id or part.joined_via_bot_instance_id != member_instance_id(message.bot):
            await state.clear()
            return
        khatm = await khatm_service.get_khatm_for_update(session, part.khatm_id)
        if khatm.commitment_policy == "FIXED_DAILY":
            await message.answer("مقدار این ختم را سازنده تعیین کرده است.")
        elif khatm.template_type == "QURAN_PAGE":
            if int(raw) > content_service.get_quran_total_pages(khatm):
                await message.answer("تعداد صفحات نباید از کل صفحات این قرآن بیشتر باشد.")
                return
            part.open_reading_pages_per_day = int(raw)
            await message.answer("✅ تعداد صفحات سهم‌های بعدی ذخیره شد.")
        else:
            part.commitment_per_occurrence = int(raw)
            await message.answer("✅ مقدار سهم‌های بعدی ذخیره شد.")
    await state.clear()


@router.callback_query(F.data.startswith("set_reminder:"))
async def set_reminder(callback: CallbackQuery) -> None:
    _, participation_id, raw_hour, raw_minute = callback.data.split(":", 3)
    hour, minute = int(raw_hour), int(raw_minute)
    async with session_scope() as session:
        settings, participation, khatm = await _owned_reminder_context(session, callback, participation_id)
        if participation is None or khatm is None:
            await callback.answer("این ختم دیگر در فهرست فعال شما نیست.", show_alert=True)
            return
        await notification_service.set_reminder_preference(
            session, participation.id, reminder_hour=hour, reminder_minute=minute, enabled=True
        )
    await callback.answer(t("settings.reminder_saved", settings.language))
    await callback.message.edit_text(
        f"✅ یادآوری ختم «{khatm.title}» روی ساعت {hour:02d}:{minute:02d} تنظیم شد.",
        reply_markup=settings_reminder_saved_keyboard(participation_id, settings.language),
    )


@router.callback_query(F.data.startswith("custom_reminder:"))
async def ask_custom_reminder(callback: CallbackQuery, state: FSMContext) -> None:
    participation_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        settings, participation, khatm = await _owned_reminder_context(session, callback, participation_id)
    if participation is None or khatm is None:
        await callback.answer("این ختم دیگر در فهرست فعال شما نیست.", show_alert=True)
        return
    await state.set_state(ReminderSettings.entering_custom_time)
    await state.update_data(reminder_participation_id=participation_id)
    await callback.message.edit_text(
        f"🕰 ساعت دلخواه برای ختم «{khatm.title}»\n\nساعت را مثل ۰۶:۳۰ یا 21:45 بفرست.",
        reply_markup=settings_reminder_custom_keyboard(participation_id),
    )
    await callback.answer()


@router.message(ReminderSettings.entering_custom_time)
async def save_custom_reminder(message: Message, state: FSMContext) -> None:
    digits = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    raw = (message.text or "").strip().translate(digits).replace(".", ":")
    try:
        hour_text, minute_text = raw.split(":", 1)
        hour, minute = int(hour_text), int(minute_text)
        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            raise ValueError
    except ValueError:
        await message.answer("ساعت درست نیست. لطفاً مثل ۰۶:۳۰ یا 21:45 بفرست.")
        return
    data = await state.get_data()
    participation_id = str(data.get("reminder_participation_id", ""))
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        participations = await participation_service.list_my_active(
            session, user.id, joined_via_bot_instance_id=member_instance_id(message.bot)
        )
        participation = next((item for item in participations if str(item.id) == participation_id), None)
        if participation is None:
            await state.clear()
            await message.answer("این ختم دیگر در فهرست فعال شما نیست.")
            return
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        await notification_service.set_reminder_preference(
            session, participation.id, reminder_hour=hour, reminder_minute=minute, enabled=True
        )
    await state.clear()
    await message.answer(
        f"✅ یادآوری ختم «{khatm.title}» روی ساعت {hour:02d}:{minute:02d} تنظیم شد.",
        reply_markup=settings_reminder_saved_keyboard(participation_id, settings.language),
    )


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
    _, settings = await _current_platform_user(callback.message)
    lang = settings.language
    await callback.message.edit_text(f"منطقه زمانی فعلی: {settings.timezone}\n\n{t('settings.choose_timezone', lang)}", reply_markup=settings_timezone_keyboard(lang))
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
