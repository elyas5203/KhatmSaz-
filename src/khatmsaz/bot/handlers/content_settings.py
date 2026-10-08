"""Per-user translation/tafsir display preferences."""

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import content_preferences_keyboard, home_keyboard_for_bot, main_menu_keyboard, safe_answer_callback
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="content_settings")


async def _set_audio(message: Message, enabled: bool) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.set_quran_audio_enabled(session, user.id, enabled)
    if enabled:
        text = (
            "🔊 صوت قرآن روشن شد.\n\n"
            "از این به بعد وقتی «📖 نمایش محتوای سهم» را بزنید، اول تصویر صفحه‌های سهمتان و بعد "
            "تلاوت همان بخش برایتان فرستاده می‌شود. بعضی فایل‌های منبع دو یا سه صفحه را با هم دارند."
        )
    else:
        text = "🔇 صوت قرآن خاموش شد. از این به بعد فقط تصویر صفحه‌های سهمتان فرستاده می‌شود."
    await message.answer(
        text,
        reply_markup=content_preferences_keyboard(audio_enabled=settings.quran_audio_enabled),
    )


@router.message(Command("audio"))
async def set_audio_command(message: Message, command: CommandObject) -> None:
    value = (command.args or "").strip().lower()
    if value not in {"on", "off"}:
        await message.answer(
            "برای روشن یا خاموش کردن صوت لازم نیست چیزی تایپ کنید؛ از دکمه‌های زیر استفاده کنید.",
            reply_markup=content_preferences_keyboard(audio_enabled=False),
        )
        return
    await _set_audio(message, value == "on")


@router.callback_query(F.data.startswith("quran_audio:"))
async def set_audio_callback(callback: CallbackQuery) -> None:
    await _set_audio(callback.message, callback.data.endswith(":on"))
    await safe_answer_callback(callback, "تنظیم صوت ذخیره شد ✅")


@router.callback_query(F.data == "quran_help")
async def quran_help(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "📖 راهنمای خیلی سادهٔ سهم قرآن\n\n"
        "۱) در منوی اصلی روی «📖 اعلام انجام قرائت امروز» بزنید.\n"
        "۲) زیر سهم خودتان روی «📖 نمایش محتوای سهم» بزنید.\n"
        "۳) تصویر صفحه‌ها برایتان می‌آید. اگر صوت را روشن کرده باشید، تلاوت هم بعد از آن می‌آید.\n"
        "۴) بعد از خواندن، فقط یک بار روی «✅ اعلام انجام قرائت» بزنید.\n\n"
        "اگر فایل صوتی شامل یک صفحهٔ کناری هم بود نگران نباشید؛ فایل اصلی کانال گاهی دو یا سه صفحه را یکجا دارد، "
        "اما تصویرهای سهم شما دقیق انتخاب می‌شوند."
    )
    await safe_answer_callback(callback)


@router.message(Command("content"))
async def set_content_option(message: Message, command: CommandObject) -> None:
    parts = (command.args or "").strip().lower().split()
    if len(parts) != 2 or parts[0] not in {"translation", "tafsir"} or parts[1] not in {"on", "off"}:
        await message.answer("فرمت درست: /content translation on|off یا /content tafsir on|off")
        return
    option, value = parts
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = getattr(message.bot, "khatmsaz_language", "fa")
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        if not getattr(message.bot, "khatmsaz_language", None):
            settings = await settings_service.get_or_create(session, user.id)
            lang = settings.language
        await settings_service.set_content_option(session, user.id, option, value == "on")
    label = "ترجمه" if option == "translation" else "تفسیر"
    state = "روشن" if value == "on" else "خاموش"
    await message.answer(
        f"نمایش {label} {state} شد ✅\nاگر asset مربوط در کتابخانه موجود باشد، هنگام ارسال محتوا اعمال می‌شود.",
        reply_markup=home_keyboard_for_bot(message.bot, lang),
    )
