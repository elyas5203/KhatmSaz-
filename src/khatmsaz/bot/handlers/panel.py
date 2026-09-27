from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from khatmsaz.bot.keyboards import main_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t, variants
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.settings import service as settings_service
from aiogram.types import WebAppInfo
from khatmsaz.config import get_settings

router = Router(name="panel")

async def _get_context(event):
    platform: Platform = getattr(event.bot, "khatmsaz_platform", Platform.TELEGRAM)
    chat_id = event.from_user.id
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return user, settings.language

def creator_panel_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("menu.create", lang), callback_data="creator_panel:create"),
                InlineKeyboardButton(text=t("menu.my_khatms", lang), callback_data="creator_panel:my_khatms")
            ],
            [InlineKeyboardButton(text="📢 ارسال پیام گروهی اختصاصی", callback_data="creator_panel:broadcast")],
            [InlineKeyboardButton(text=t("menu.report", lang), callback_data="creator_panel:finance")],
            [InlineKeyboardButton(text=t("menu.settings", lang), callback_data="creator_panel:settings")]
        ]
    )

def admin_panel_keyboard(lang: str) -> InlineKeyboardMarkup:
    base_url = get_settings().admin_web_base_url
    login_url = f"{base_url}/mini/admin"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 پنل وب ادمین (کامل)", web_app=WebAppInfo(url=login_url))],
            [InlineKeyboardButton(text="📝 تایید درخواست‌های سازندگان", callback_data="admin_panel:creator_requests")],
            [InlineKeyboardButton(text="👥 مدیریت لیست کاربران", callback_data="admin_panel:users")],
            [InlineKeyboardButton(text="📢 پیام گروهی سراسری (اعلان)", callback_data="admin_panel:broadcast")],
        ]
    )

@router.message(F.text.in_(variants("menu.creator.management")))
async def handle_creator_management(message: Message) -> None:
    user, lang = await _get_context(message)
    if user.role not in (UserRole.CREATOR, UserRole.SUPER_ADMIN):
        return
    await message.answer(
        "🎛 <b>پنل مدیریت سازنده</b>\n\nلطفاً یکی از بخش‌های زیر را انتخاب کنید:",
        reply_markup=creator_panel_keyboard(lang)
    )

@router.message(F.text.in_(variants("menu.creator.finance")))
async def handle_creator_finance(message: Message) -> None:
    """The creator reply-menu button «📊 گزارش و مالی» previously had no
    handler at all (reported by QA 2026-09-27) — tapping it did nothing.
    Route it to the personal report, which is the closest existing view."""
    user, _lang = await _get_context(message)
    if user.role not in (UserRole.CREATOR, UserRole.SUPER_ADMIN):
        return
    from khatmsaz.bot.handlers.report import personal_report
    await personal_report(message)


@router.message(F.text.in_(variants("menu.creator.support")))
async def handle_creator_support(message: Message) -> None:
    """«❓ راهنما و پشتیبانی» reply button had no handler either — route it to
    the help home, which already offers the contact-support entry."""
    from khatmsaz.bot.handlers.help import help_command
    await help_command(message)


@router.message(F.text.in_(variants("help.button.admin_panel")))
async def handle_admin_panel(message: Message) -> None:
    user, lang = await _get_context(message)
    if user.role != UserRole.SUPER_ADMIN:
        return
    await message.answer(
        "🎛 <b>پنل مدیریت ادمین</b>\n\nلطفاً یکی از بخش‌های زیر را انتخاب کنید:",
        reply_markup=admin_panel_keyboard(lang)
    )

from aiogram.fsm.context import FSMContext

@router.callback_query(F.data == "creator_panel:create")
async def handle_creator_panel_create(callback: CallbackQuery, state: FSMContext) -> None:
    from khatmsaz.bot.handlers.create_khatm import start_wizard
    try:
        await callback.message.delete()
    except:
        pass
    # start_wizard expects a message to reply to.
    # since we deleted the panel, we construct a dummy message or just pass callback.message
    await start_wizard(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "creator_panel:my_khatms")
async def handle_creator_panel_my_khatms(callback: CallbackQuery) -> None:
    from khatmsaz.bot.handlers.my_khatms import list_my_khatms
    try:
        await callback.message.delete()
    except:
        pass
    await list_my_khatms(callback.message)
    await callback.answer()

@router.callback_query(F.data == "creator_panel:broadcast")
async def handle_creator_panel_broadcast(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("📢 برای ارسال پیام گروهی اختصاصی:\n\nباید به لیست «ختم‌های من» بروید، روی یکی از ختم‌های خود کلیک کنید تا پنل مدیریت آن باز شود. سپس دکمه <b>ارسال پیام گروهی</b> را برای اعضای آن ختم انتخاب کنید.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:creator")]]))
    await callback.answer()

@router.callback_query(F.data == "creator_panel:finance")
async def handle_creator_panel_finance(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("💳 بخش مالی و گزارش‌ها\n\nاین بخش به زودی فعال خواهد شد. شما می‌توانید لیست شرکت‌کنندگان هر ختم و مبالغ پرداخت شده را از طریق دریافت فایل Excel از داخل پنل مدیریت همان ختم دانلود کنید.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:creator")]]))
    await callback.answer()

@router.callback_query(F.data == "creator_panel:settings")
async def handle_creator_panel_settings(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("⚙️ تنظیمات سازنده.\n\nدر حال حاضر تنظیمات شما همان تنظیمات حساب کاربری است.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:creator")]]))
    await callback.answer()

@router.callback_query(F.data == "admin_panel:creator_requests")
async def handle_admin_panel_requests(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("📝 <b>تایید سازندگان جدید</b>\n\nبرای تبدیل یک کاربر به سازنده، اگر درخواست او در پنل وب ادمین وجود دارد، می‌توانید دستور زیر را همراه با آیدی درخواست ارسال کنید:\n<code>/admin_approve_creator &lt;request_id&gt;</code>\n\nدر صورت عدم وجود درخواست، باید از طریق دیتابیس اقدام کنید.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:admin")]]))
    await callback.answer()

@router.callback_query(F.data == "admin_panel:users")
async def handle_admin_panel_users(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("👥 <b>مدیریت کاربران</b>\n\nلیست مخاطبین و امکان مسدودسازی کاربران تنها از طریق «پنل وب ادمین» (WebApp) قابل دسترسی است. لطفاً از دکمه وب‌اپ استفاده کنید.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:admin")]]))
    await callback.answer()

@router.callback_query(F.data == "admin_panel:broadcast")
async def handle_admin_panel_broadcast(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("📢 ارسال پیام گروهی سراسری\n\nاین قابلیت (ارسال پیام به تمام کاربران ربات) باید از طریق اسکریپت‌های مدیریت سرور یا در نسخه‌های بعدی ربات تلگرام انجام شود.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:admin")]]))
    await callback.answer()

@router.callback_query(F.data.startswith("panel:back:"))
async def handle_panel_back(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    target = callback.data.split(":")[2]
    if target == "creator":
        await callback.message.edit_text("🎛 <b>پنل مدیریت سازنده</b>\n\nلطفاً یکی از بخش‌های زیر را انتخاب کنید:", reply_markup=creator_panel_keyboard(lang))
    elif target == "admin":
        await callback.message.edit_text("🎛 <b>پنل مدیریت ادمین</b>\n\nلطفاً یکی از بخش‌های زیر را انتخاب کنید:", reply_markup=admin_panel_keyboard(lang))
    await callback.answer()
