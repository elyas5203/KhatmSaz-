from html import escape
from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from khatmsaz.bot.keyboards import creator_finance_keyboard, main_menu_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t, variants
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.authorization.models import AdminPermission, AdminRole, AdminRoleGrant
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.bot.admin_sync import notify_new_admin_appointed

router = Router(name="panel")


class AdminUserSearchState(StatesGroup):
    waiting_for_query = State()


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
    from khatmsaz.modules.authorization import service as authorization_service
    async with session_scope() as session:
        is_admin = user.role == UserRole.SUPER_ADMIN or await authorization_service.is_admin(session, user)
    if not is_admin:
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

def admin_users_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 جست‌وجوی کاربر با نام، شماره یا آیدی چت", callback_data="admin_users:search")],
            [InlineKeyboardButton(text="📋 لیست آخرین کاربران", callback_data="admin_users:recent")],
            [InlineKeyboardButton(text="🛡 لیست مدیران فعلی", callback_data="admin_users:admins")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی ادمین", callback_data="panel:back:admin")],
        ]
    )


async def _render_user_list(
    session,
    users: list,
    title: str,
) -> tuple[str, InlineKeyboardMarkup]:
    if not users:
        return (
            f"{title}\n\nکاربری یافت نشد.",
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔍 جست‌وجوی مجدد", callback_data="admin_users:search")],
                    [InlineKeyboardButton(text="🔙 مدیریت کاربران", callback_data="admin_panel:users")],
                ]
            ),
        )

    user_ids = [u.id for u in users]
    stmt_settings = select(UserSettings).where(UserSettings.user_id.in_(user_ids))
    settings_map = {s.user_id: s for s in (await session.execute(stmt_settings)).scalars().all()}

    lines = [title, ""]
    buttons = []

    for idx, u in enumerate(users, 1):
        name = u.display_name or "کاربر بدون نام"
        sub = u.platform_identities[0].subject if u.platform_identities else "نامشخص"
        plat = u.platform_identities[0].platform.value if u.platform_identities else ""
        phone = settings_map.get(u.id).contact_phone if settings_map.get(u.id) else None

        roles = await authorization_service.list_roles(session, u.id)
        is_adm = (AdminRole.ADMIN in roles)

        if u.role == UserRole.SUPER_ADMIN:
            status = "مدیر کل (سوپرادمین) 👑"
        elif is_adm:
            status = "مدیر (ادمین) ⭐️"
        elif u.role == UserRole.CREATOR:
            status = "سازنده ختم 📝"
        else:
            status = "کاربر عادی"

        user_info = [
            f"{idx}. <b>{escape(name)}</b>",
            f"   🆔 آیدی چت: <code>{escape(sub)}</code> ({plat})",
        ]
        if phone:
            user_info.append(f"   📱 شماره: <code>{escape(phone)}</code>")
        user_info.append(f"   🔰 وضعیت: {status}")
        lines.append("\n".join(user_info) + "\n")

        if u.role != UserRole.SUPER_ADMIN:
            short_name = (u.display_name or "کاربر")[:16]
            if is_adm:
                btn_text = f"❌ لغو مدیر: {short_name}"
                btn_cb = f"admin_role:toggle:{u.id}:revoke"
            else:
                btn_text = f"⭐️ مدیر کردن: {short_name}"
                btn_cb = f"admin_role:toggle:{u.id}:grant"
            buttons.append([InlineKeyboardButton(text=btn_text, callback_data=btn_cb)])

    buttons.append([
        InlineKeyboardButton(text="🔍 جست‌وجوی جدید", callback_data="admin_users:search"),
        InlineKeyboardButton(text="🔙 مدیریت کاربران", callback_data="admin_panel:users"),
    ])

    return "\n".join(lines).strip(), InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "admin_panel:users")
async def handle_admin_panel_users(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    async with session_scope() as session:
        is_admin = user.role == UserRole.SUPER_ADMIN or await authorization_service.is_admin(session, user)
    if not is_admin:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    await callback.message.edit_text(
        "👥 <b>مدیریت کاربران و انتصاب مدیران</b>\n\n"
        "از این بخش می‌توانید کاربران سامانه را مشاهده و جست‌وجو کرده و دسترسی «مدیر (ادمین)» را مدیریت نمایید.\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=admin_users_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_users:search")
async def handle_admin_users_search(callback: CallbackQuery, state: FSMContext) -> None:
    user, lang = await _get_context(callback)
    async with session_scope() as session:
        is_admin = user.role == UserRole.SUPER_ADMIN or await authorization_service.is_admin(session, user)
    if not is_admin:
        await callback.answer("دسترسی ندارید.", show_alert=True)
        return
    await state.set_state(AdminUserSearchState.waiting_for_query)
    await callback.message.edit_text(
        "🔍 <b>جست‌وجوی کاربر</b>\n\n"
        "لطفاً <b>نام</b>، <b>شماره تلفن</b> یا <b>آیدی عددی تلگرام (Chat ID)</b> کاربر را ارسال کنید:\n\n"
        "<i>(می‌توانید آیدی را با یا بدون @ بفرستید)</i>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 انصراف", callback_data="admin_users:cancel_search")]
            ]
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_users:cancel_search")
async def handle_admin_users_cancel_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await handle_admin_panel_users(callback)


@router.callback_query(F.data == "admin_users:recent")
async def handle_admin_users_recent(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    async with session_scope() as session:
        is_admin = user.role == UserRole.SUPER_ADMIN or await authorization_service.is_admin(session, user)
        if not is_admin:
            await callback.answer("دسترسی ندارید.", show_alert=True)
            return
        users = await identity_service.search_users(session, "", limit=5)
        text, kb = await _render_user_list(session, users, "📋 <b>آخرین کاربران ثبت‌شده در سامانه:</b>")
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "admin_users:admins")
async def handle_admin_users_admins(callback: CallbackQuery) -> None:
    user, lang = await _get_context(callback)
    async with session_scope() as session:
        is_admin = user.role == UserRole.SUPER_ADMIN or await authorization_service.is_admin(session, user)
        if not is_admin:
            await callback.answer("دسترسی ندارید.", show_alert=True)
            return
        stmt = (
            select(AdminRoleGrant, User)
            .join(User, User.id == AdminRoleGrant.user_id)
            .where(
                AdminRoleGrant.revoked_at.is_(None),
                AdminRoleGrant.role == AdminRole.ADMIN,
            )
            .order_by(AdminRoleGrant.granted_at.desc())
        )
        grants = list((await session.execute(stmt)).all())
        if not grants:
            await callback.message.edit_text(
                "🛡 <b>لیست مدیران (ادمین‌های) فعال</b>\n\nهنوز مدیری اضافه نشده است.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🔍 جست‌وجوی کاربر برای افزودن", callback_data="admin_users:search")],
                        [InlineKeyboardButton(text="🔙 مدیریت کاربران", callback_data="admin_panel:users")],
                    ]
                ),
            )
            await callback.answer()
            return
        users = [u for _, u in grants]
        text, kb = await _render_user_list(session, users, "🛡 <b>لیست مدیران (ادمین‌های) فعال:</b>")
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.message(AdminUserSearchState.waiting_for_query)
async def handle_admin_user_search_query(message: Message, state: FSMContext) -> None:
    query = (message.text or "").strip()
    if not query or query in {"/cancel", "انصراف"}:
        await state.clear()
        await message.answer("جست‌وجو لغو شد.", reply_markup=main_menu_keyboard("fa"))
        return
    await state.clear()
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        actor = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if actor is None:
            return
        is_admin = actor.role == UserRole.SUPER_ADMIN or await authorization_service.is_admin(session, actor)
        if not is_admin:
            return
        users = await identity_service.search_users(session, query, limit=5)
        if not users:
            await message.answer(
                f"❌ کاربری با عبارت «{escape(query)}» پیدا نشد.\n\nمی‌توانید دوباره تلاش کنید:",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🔍 جست‌وجوی مجدد", callback_data="admin_users:search")],
                        [InlineKeyboardButton(text="🔙 مدیریت کاربران", callback_data="admin_panel:users")],
                    ]
                ),
            )
            return
        text, kb = await _render_user_list(
            session, users, f"🔍 <b>نتیجهٔ جست‌وجو برای «{escape(query)}»:</b>"
        )
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("admin_role:toggle:"))
async def handle_admin_role_toggle(callback: CallbackQuery) -> None:
    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("دستور نامعتبر است.", show_alert=True)
        return
    try:
        target_user_id = UUID(parts[2])
    except ValueError:
        await callback.answer("شناسه کاربر نامعتبر است.", show_alert=True)
        return
    action = parts[3]  # "grant" or "revoke"

    user, _ = await _get_context(callback)
    if user.role != UserRole.SUPER_ADMIN:
        await callback.answer("⚠️ فقط مدیر کل (سوپرادمین) اجازهٔ تعیین یا لغو نقش مدیران را دارد.", show_alert=True)
        return

    async with session_scope() as session:
        actor = await identity_service.find_by_id(session, user.id)
        target = await identity_service.find_by_id(session, target_user_id)
        if target is None:
            await callback.answer("کاربر یافت نشد.", show_alert=True)
            return

        if action == "grant":
            await authorization_service.grant_role(
                session, actor=actor, target=target, role=AdminRole.ADMIN
            )
            await audit_service.record(
                session,
                actor_user_id=actor.id,
                target_user_id=target.id,
                action="ADMIN_ROLE_GRANTED",
                details={"role": AdminRole.ADMIN.value, "via": "bot_panel"},
            )
            await notify_new_admin_appointed(session, target.id, bot=callback.bot)
            alert_msg = f"✅ «{target.display_name or 'کاربر'}» به عنوان مدیر (ادمین) فعال شد و پیام اطلاع‌رسانی برای او ارسال گردید."
        elif action == "revoke":
            await authorization_service.revoke_role(
                session, actor=actor, target=target, role=AdminRole.ADMIN
            )
            await audit_service.record(
                session,
                actor_user_id=actor.id,
                target_user_id=target.id,
                action="ADMIN_ROLE_REVOKED",
                details={"role": AdminRole.ADMIN.value, "via": "bot_panel"},
            )
            alert_msg = f"✅ دسترسی مدیر برای «{target.display_name or 'کاربر'}» لغو شد."
        else:
            await callback.answer("عملیات نامعتبر است.", show_alert=True)
            return

        # Flip the button on the current inline keyboard
        new_keyboard = []
        if callback.message.reply_markup and callback.message.reply_markup.inline_keyboard:
            for row in callback.message.reply_markup.inline_keyboard:
                new_row = []
                for btn in row:
                    if btn.callback_data == callback.data:
                        target_name = (target.display_name or "کاربر")[:16]
                        if action == "grant":
                            new_row.append(
                                InlineKeyboardButton(
                                    text=f"❌ لغو مدیر: {target_name}",
                                    callback_data=f"admin_role:toggle:{target.id}:revoke",
                                )
                            )
                        else:
                            new_row.append(
                                InlineKeyboardButton(
                                    text=f"⭐️ مدیر کردن: {target_name}",
                                    callback_data=f"admin_role:toggle:{target.id}:grant",
                                )
                            )
                    else:
                        new_row.append(btn)
                new_keyboard.append(new_row)

        await callback.answer(alert_msg, show_alert=True)
        try:
            await callback.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
            )
        except Exception:
            pass

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
