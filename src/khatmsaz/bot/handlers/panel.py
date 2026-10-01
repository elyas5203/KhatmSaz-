from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from khatmsaz.bot.keyboards import creator_finance_keyboard, main_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t, variants
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.settings import service as settings_service

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
            [InlineKeyboardButton(
                text=t("panel.creator.open_mini_app", lang),
                callback_data="creator:web_login",
            )],
            [
                InlineKeyboardButton(text=t("menu.create", lang), callback_data="creator_panel:create"),
                InlineKeyboardButton(text=t("menu.my_khatms", lang), callback_data="creator_panel:my_khatms")
            ],
            [InlineKeyboardButton(text="📢 ارسال پیام گروهی اختصاصی", callback_data="creator_panel:broadcast")],
            [
                InlineKeyboardButton(text=t("menu.report", lang), callback_data="creator_panel:finance"),
                InlineKeyboardButton(text=t("menu.creator.wallet", lang), callback_data="creator_panel:wallet"),
            ],
            [InlineKeyboardButton(text=t("menu.settings", lang), callback_data="creator_panel:settings")]
        ]
    )

def admin_panel_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t("panel.admin.open_mini_app", lang),
                callback_data="admin:web_login",
            )],
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
    """Open the finance submenu instead of confusing it with one report."""
    user, lang = await _get_context(message)
    if user.role not in (UserRole.CREATOR, UserRole.SUPER_ADMIN):
        return
    await message.answer(
        t("creator.finance.menu_intro", lang),
        reply_markup=creator_finance_keyboard(lang),
    )


@router.message(F.text.in_(variants("menu.creator.wallet")))
async def handle_creator_wallet(message: Message) -> None:
    """«💳 شارژ کیف پول» — open the wallet overview + top-up options.

    The top-up flow (balance, PayPing amounts, invoices) already exists in
    `handlers/wallet.py`; before this button it was only reachable via the
    `/wallet` command, so creators had no tap-only entry (owner request)."""
    user, _lang = await _get_context(message)
    if user.role not in (UserRole.CREATOR, UserRole.SUPER_ADMIN):
        return
    from khatmsaz.bot.handlers.wallet import _show_wallet
    await _show_wallet(message)


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
async def handle_creator_panel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Open the broadcast khatm-picker directly instead of a how-to text."""
    from khatmsaz.bot.handlers.creator_broadcast import start_broadcast
    await start_broadcast(callback, state)

@router.callback_query(F.data == "creator_panel:finance")
async def handle_creator_panel_finance(callback: CallbackQuery) -> None:
    """Open the real personal report instead of a "coming soon" dead-end."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    from khatmsaz.bot.handlers.report import personal_report
    await personal_report(callback.message)
    await callback.answer()

@router.callback_query(F.data == "creator_panel:wallet")
async def handle_creator_panel_wallet(callback: CallbackQuery) -> None:
    """Open the wallet overview + top-up options from the inline panel."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    from khatmsaz.bot.handlers.wallet import _show_wallet
    await _show_wallet(callback.message)
    await callback.answer()


@router.callback_query(F.data == "creator_panel:settings")
async def handle_creator_panel_settings(callback: CallbackQuery) -> None:
    """Open the real settings menu instead of a placeholder."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    from khatmsaz.bot.handlers.settings_menu import settings_overview
    await settings_overview(callback.message)
    await callback.answer()

@router.callback_query(F.data == "admin_panel:creator_requests")
async def handle_admin_panel_requests(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text(
        "📝 <b>تأیید سازندگان جدید</b>\n\n"
        "حالا می‌توانید همهٔ درخواست‌های سازنده‌شدن را مستقیم در «پنل وب ادمین» ببینید و با یک لمس تأیید یا رد کنید — بخش «تأیید سازندگان».\n\n"
        "برای باز کردن پنل، دکمهٔ وب‌اپ بالای همین منو را بزنید.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:admin")]]),
    )
    await callback.answer()

@router.callback_query(F.data == "admin_panel:users")
async def handle_admin_panel_users(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("👥 <b>مدیریت کاربران</b>\n\nلیست کاربران، جست‌وجو و مدیریت آن‌ها در «پنل وب ادمین» (بخش «کاربران») در دسترس است. لطفاً دکمهٔ وب‌اپ بالای همین منو را بزنید.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:admin")]]))
    await callback.answer()

@router.callback_query(F.data == "admin_panel:broadcast")
async def handle_admin_panel_broadcast(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    await callback.message.edit_text("📢 <b>پیام گروهی سراسری</b>\n\nصف پیام‌های گروهی و تأیید آن‌ها در «پنل وب ادمین» (بخش «پیام گروهی») مدیریت می‌شود. لطفاً دکمهٔ وب‌اپ بالای همین منو را بزنید.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 برگشت", callback_data="panel:back:admin")]]))
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
