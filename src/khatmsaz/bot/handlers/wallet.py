"""Simple wallet balance and PayPing top-up flow."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from datetime import datetime, timezone
from uuid import UUID

from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import ReceiptClaimStatus
from khatmsaz.modules.wallet.gateway import GatewayError
from khatmsaz.modules.wallet.payping import PayPingGateway
from khatmsaz.bot.keyboards import bail_if_menu_button, safe_answer_callback, safe_clear_inline_keyboard

router = Router(name="wallet")

_PLAN_LABEL_KEYS = {"FREE": "wallet.plan_label.FREE", "BASIC": "wallet.plan_label.BASIC", "PRO": "wallet.plan_label.PRO"}
_TOPUP_AMOUNTS = (50_000, 100_000, 500_000)
_TOPUP_MIN = 10_000
_TOPUP_MAX = 50_000_000


def _localized_amount(amount: int, lang: str) -> str:
    rendered = f"{amount:,}"
    if lang == "fa":
        return rendered.translate(str.maketrans("0123456789,", "۰۱۲۳۴۵۶۷۸۹٬"))
    if lang == "ar":
        return rendered.translate(str.maketrans("0123456789,", "٠١٢٣٤٥٦٧٨٩٬"))
    return rendered


class WalletTopup(StatesGroup):
    entering_amount = State()
    entering_ref_id = State()


class WalletReceiptUpload(StatesGroup):
    entering_amount = State()
    uploading_photo = State()


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


def _topup_keyboard(lang: str, *, pro_price: int | None = None, is_pro: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if pro_price is not None and pro_price > 0:
        btn_text = (
            f"🔄 تمدید پلن حرفه‌ای ۳۰ روزه ({pro_price:,} تومان)"
            if is_pro
            else f"⭐ ارتقا به پلن حرفه‌ای ۳۰ روزه ({pro_price:,} تومان)"
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data="wallet:buy_pro",
                )
            ]
        )
    rows.extend([
        [
            InlineKeyboardButton(text="💳 ۵۰,۰۰۰ تومان", callback_data="wallet_topup:50000"),
            InlineKeyboardButton(text="💳 ۱۰۰,۰۰۰ تومان", callback_data="wallet_topup:100000"),
        ],
        [
            InlineKeyboardButton(text="💳 ۵۰۰,۰۰۰ تومان", callback_data="wallet_topup:500000"),
            InlineKeyboardButton(text="💰 مبلغ دلخواه", callback_data="wallet_topup_custom"),
        ],
        [
            InlineKeyboardButton(
                text="🔗 درگاه مستقیم شاپرک",
                callback_data="wallet:topup_info",
            ),
            InlineKeyboardButton(
                text="📸 ارسال تصویر فیش واریز",
                callback_data="wallet:receipt_upload",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🧾 سوابق تراکنش‌ها و فاکتورها",
                callback_data="wallet:invoices",
            )
        ],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _create_topup_payment(message: Message, bot, amount: int, lang: str) -> None:
    """Shared: build a PayPing intent for `amount` and send the pay link."""
    settings = get_settings()
    if not settings.payping_api_token or not settings.payping_callback_url.startswith("https://"):
        await message.answer(t("wallet.gateway_not_configured", lang))
        return
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
            pending, request = await wallet_service.create_payment_intent(
                session,
                PayPingGateway(settings.payping_api_token),
                user.id,
                amount_toman=amount,
                description=t("wallet.topup_description", lang, amount=f"{amount:,}"),
                callback_url=settings.payping_callback_url,
            )
    except GatewayError:
        await message.answer(t("wallet.gateway_unreachable", lang))
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("wallet.pay_button", lang, amount=f"{amount:,}"), url=request.payment_url)],
            [InlineKeyboardButton(text=t("wallet.check_button", lang), callback_data=f"wallet_check:{pending.id}")],
        ]
    )
    await message.answer(t("wallet.final_topup_step", lang, amount=f"{amount:,}"), reply_markup=keyboard)


async def _show_wallet(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    pro_price = None
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        balance, credit = await wallet_service.get_balances(session, user.id)
        plan_details = await plan_service.get_plan_details(session, user.id)
        pro_price = await plan_service.get_pro_plan_price(session)

    plan = plan_details["plan"]
    plan_label = t(_PLAN_LABEL_KEYS.get(plan.value, ""), lang) if plan.value in _PLAN_LABEL_KEYS else plan.value
    overview_text = t("wallet.overview", lang, balance=f"{balance:,}", credit=f"{credit:,}", plan=plan_label)
    if plan == PlanTier.PRO:
        days_left = plan_details.get("days_left") or 0
        overview_text += f"\n⏳ <b>اعتبار پلن حرفه‌ای:</b> {days_left} روز باقی‌مانده\n<i>(با تمدید، ۳۰ روز کامل به مهلت فعلی اضافه می‌شود)</i>"

    await message.answer(
        overview_text,
        reply_markup=_topup_keyboard(lang, pro_price=pro_price, is_pro=(plan == PlanTier.PRO)),
    )


@router.callback_query(F.data == "wallet:buy_pro")
async def buy_pro_from_wallet(callback: CallbackQuery) -> None:
    await safe_clear_inline_keyboard(callback.message)
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(
                session, platform, callback.from_user.id
            )
            prev_plan = await plan_service.get_plan(session, user.id)
            invoice, new_expiry = await plan_service.purchase_pro_plan(session, user.id)
    except wallet_service.InsufficientFundsError:
        await safe_answer_callback(
            callback,
            "موجودی کیف پول شما برای خرید یا تمدید پلن حرفه‌ای کافی نیست. ابتدا کیف پول خود را شارژ کنید.",
            show_alert=True,
        )
        return
    except Exception as exc:
        await safe_answer_callback(callback, str(exc), show_alert=True)
        return

    if prev_plan == PlanTier.PRO:
        msg = "🎉 پلن حرفه‌ای شما با موفقیت برای ۳۰ روز دیگر تمدید شد!"
    else:
        msg = "🎉 پلن شما با موفقیت به حرفه‌ای (PRO) ۳۰ روزه ارتقا یافت!"
    await safe_answer_callback(callback, msg, show_alert=True)
    await _show_wallet(callback.message)


@router.message(Command("wallet"))
async def show_wallet(message: Message) -> None:
    await _show_wallet(message)


@router.message(Command("topup"))
async def show_topup(message: Message) -> None:
    await _show_wallet(message)


@router.message(Command("invoices"))
async def show_invoices(message: Message) -> None:
    await _show_invoices(message)


async def _show_invoices(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        invoices = await wallet_service.list_invoices(session, user.id, limit=10)
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به کیف پول", callback_data="wallet:open")]]
    )
    if not invoices:
        await message.answer(t("wallet.no_invoices", lang), reply_markup=back_kb)
        return
    kind_keys = {
        "TOPUP": "wallet.invoice_kind.TOPUP",
        "KHATM_CREATION": "wallet.invoice_kind.KHATM_CREATION",
        "PURCHASE": "wallet.invoice_kind.PURCHASE",
    }
    status_keys = {"PAID": "wallet.invoice_status.PAID", "REFUNDED": "wallet.invoice_status.REFUNDED"}
    lines = [t("wallet.invoices_header", lang)]
    for invoice in invoices:
        kind_label = t(kind_keys[invoice.kind], lang) if invoice.kind in kind_keys else invoice.kind
        status_label = t(status_keys[invoice.status], lang) if invoice.status in status_keys else invoice.status
        lines.append(
            t(
                "wallet.invoice_line", lang,
                kind=kind_label, amount=f"{invoice.net_amount_toman:,}",
                status=status_label, number=str(invoice.id)[:8],
            )
        )
    await message.answer("\n".join(lines), reply_markup=back_kb)


@router.callback_query(F.data == "wallet:open")
async def open_wallet_from_button(callback: CallbackQuery) -> None:
    await _show_wallet(callback.message)
    await callback.answer()


@router.callback_query(F.data == "wallet:invoices")
async def open_invoices_from_button(callback: CallbackQuery) -> None:
    await _show_invoices(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("wallet_topup:"))
async def create_topup(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    try:
        amount = int(callback.data.split(":", 1)[1])
    except (AttributeError, ValueError):
        await callback.answer(t("wallet.invalid_amount", lang), show_alert=True)
        return
    if amount not in _TOPUP_AMOUNTS:
        await callback.answer(t("wallet.amount_not_selectable", lang), show_alert=True)
        return

    settings = get_settings()
    if not settings.payping_api_token or not settings.payping_callback_url.startswith("https://"):
        await callback.message.answer(t("wallet.gateway_not_configured", lang))
        await callback.answer()
        return

    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(
                session, platform, callback.message.chat.id
            )
            pending, request = await wallet_service.create_payment_intent(
                session,
                PayPingGateway(settings.payping_api_token),
                user.id,
                amount_toman=amount,
                description=t("wallet.topup_description", lang, amount=f"{amount:,}"),
                callback_url=settings.payping_callback_url,
            )
    except GatewayError:
        await callback.message.answer(t("wallet.gateway_unreachable", lang))
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("wallet.pay_button", lang, amount=f"{amount:,}"), url=request.payment_url)],
            [InlineKeyboardButton(text=t("wallet.check_button", lang), callback_data=f"wallet_check:{pending.id}")],
        ]
    )
    await callback.message.answer(
        t("wallet.final_topup_step", lang, amount=f"{amount:,}"),
        reply_markup=keyboard,
    )
    await callback.answer(t("wallet.link_created", lang))


@router.callback_query(F.data == "wallet_topup_custom")
async def ask_custom_topup(callback: CallbackQuery, state: FSMContext) -> None:
    """Owner (2026-09-29): let the user charge the wallet with any amount."""
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await state.set_state(WalletTopup.entering_amount)
    await state.update_data(lang=lang)
    await callback.message.answer(
        t("wallet.topup_custom_prompt", lang, min=_localized_amount(_TOPUP_MIN, lang), max=_localized_amount(_TOPUP_MAX, lang))
    )
    await callback.answer()


@router.message(WalletTopup.entering_amount)
async def receive_custom_topup(message: Message, state: FSMContext) -> None:
    from khatmsaz.bot.keyboards import bail_if_menu_button
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw = (message.text or "").strip().replace(",", "").replace("٬", "")
    # tolerate Persian/Arabic digits
    raw = raw.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
    if not raw.isdigit():
        await message.answer(t("wallet.topup_custom_invalid", lang, min=_localized_amount(_TOPUP_MIN, lang), max=_localized_amount(_TOPUP_MAX, lang)))
        return
    amount = int(raw)
    if amount < _TOPUP_MIN or amount > _TOPUP_MAX:
        await message.answer(t("wallet.topup_custom_invalid", lang, min=_localized_amount(_TOPUP_MIN, lang), max=_localized_amount(_TOPUP_MAX, lang)))
        return
    await state.clear()
    await _create_topup_payment(message, message.bot, amount, lang)


@router.callback_query(F.data.startswith("wallet_check:"))
async def handle_wallet_check(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    try:
        payment_id_str = callback.data.split(":", 1)[1]
        from uuid import UUID
        payment_id = UUID(payment_id_str)
    except Exception:
        await callback.answer(t("wallet.invalid_amount", lang), show_alert=True)
        return

    from datetime import datetime, timezone
    from khatmsaz.modules.wallet import repository as wallet_repo
    async with session_scope() as session:
        pending = await wallet_repo.get_pending_payment_by_id(session, payment_id)
        if pending is None:
            await callback.answer(t("wallet.check_expired", lang), show_alert=True)
            return
        if pending.used:
            await callback.answer(t("wallet.check_already_credited", lang), show_alert=True)
            return
        if pending.expires_at <= datetime.now(timezone.utc):
            await callback.answer(t("wallet.check_expired", lang), show_alert=True)
            return

    await state.set_state(WalletTopup.entering_ref_id)
    await state.update_data(payment_id=payment_id_str, lang=lang)
    await callback.message.answer(t("wallet.check_ask_ref", lang))
    await callback.answer()


@router.message(WalletTopup.entering_ref_id)
async def receive_ref_id_for_verification(message: Message, state: FSMContext) -> None:
    from khatmsaz.bot.keyboards import bail_if_menu_button
    if await bail_if_menu_button(message, state):
        return

    text = (message.text or "").strip()
    if text.lower() in ("/cancel", "cancel", "انصراف"):
        await state.clear()
        await message.answer("عملیات استعلام لغو شد.")
        return

    data = await state.get_data()
    lang = data.get("lang", "fa")
    payment_id_str = data.get("payment_id", "")
    from uuid import UUID
    from datetime import datetime, timezone

    # Tolerate Persian/Arabic digits
    normalized_ref = text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧۸۹", "01234567890123456789")).strip()
    if not normalized_ref or not normalized_ref.isdigit():
        await message.answer("لطفاً شماره پیگیری را فقط به صورت عدد (ارقام) ارسال فرمایید، یا برای انصراف /cancel بزنید.")
        return

    settings = get_settings()
    gateway = PayPingGateway(settings.payping_api_token)

    from khatmsaz.modules.wallet import repository as wallet_repo
    try:
        async with session_scope() as session:
            pending = await wallet_repo.get_pending_payment_by_id(session, UUID(payment_id_str))
            if not pending or pending.expires_at <= datetime.now(timezone.utc):
                await state.clear()
                await message.answer(t("wallet.check_expired", lang))
                return
            if pending.used:
                await state.clear()
                await message.answer(t("wallet.check_already_credited", lang))
                await _show_wallet(message)
                return

            verification = await wallet_service.verify_payping_callback_and_credit(
                session,
                gateway,
                client_ref_id=payment_id_str,
                authority=pending.authority,
                amount_toman=pending.amount_toman,
                transaction_ref=normalized_ref,
            )
            credited_amount = verification.amount_toman
    except wallet_service.PaymentAlreadyProcessedError:
        await state.clear()
        await message.answer(t("wallet.check_already_credited", lang))
        await _show_wallet(message)
        return
    except (wallet_service.InvalidPaymentError, GatewayError):
        await message.answer(t("wallet.check_failed", lang))
        return

    await state.clear()
    await message.answer(
        t("wallet.check_success", lang, amount=f"{credited_amount:,}", ref=normalized_ref)
    )
    await _show_wallet(message)


@router.callback_query(F.data == "wallet:topup_info")
async def show_topup_info(callback: CallbackQuery) -> None:
    settings = get_settings()
    direct_link = getattr(settings, "payping_direct_url", None) or "https://ppng.ir/d/VFBD"

    text = (
        "💳 <b>افزایش موجودی کیف پول</b>\n\n"
        "جهت شارژ حساب خود، می‌توانید مبلغ مورد نظر را از طریق لینک مستقیم زیر در درگاه امن شاپرک پرداخت نمایید:\n\n"
        f"🔗 <b>لینک پرداخت مستقیم شاپرک:</b>\n{direct_link}\n\n"
        "🌱 <b>پس از پرداخت:</b> لطفاً روی دکمهٔ «📸 ارسال تصویر فیش واریز» در زیر کلیک کرده و عکس رسید پرداخت خود را ارسال فرمایید تا پس از بررسی مدیریت، حساب شما به صورت خودکار شارژ گردد."
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 ارسال تصویر فیش واریز", callback_data="wallet:receipt_upload")],
            [InlineKeyboardButton(text="🔙 بازگشت به کیف پول", callback_data="wallet:open")],
        ]
    )
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "wallet:receipt_upload")
async def start_receipt_upload(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    await state.set_state(WalletReceiptUpload.entering_amount)
    await state.update_data(lang=lang)
    cancel_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data="wallet:cancel_receipt")]]
    )
    await callback.message.answer(
        "لطفاً مبلغ واریزشده را به تومان وارد فرمایید (مثلاً ۵۰,۰۰۰):\n\n"
        "(برای انصراف دکمه زیر یا /cancel بزنید)",
        reply_markup=cancel_kb,
    )
    await callback.answer()


@router.callback_query(F.data == "wallet:cancel_receipt")
async def cancel_receipt_upload(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer("ارسال فیش واریزی لغو شد.")
    await _show_wallet(callback.message)
    await safe_answer_callback(callback)


@router.message(WalletReceiptUpload.entering_amount)
async def receive_receipt_amount(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return

    text = (message.text or "").strip()
    if text.lower() in ("/cancel", "cancel", "انصراف"):
        await state.clear()
        await message.answer("ارسال فیش واریزی لغو شد.")
        return

    raw = text.replace(",", "").replace("٬", "")
    raw = raw.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
    if not raw.isdigit():
        await message.answer("لطفاً مبلغ را فقط به صورت عدد (ارقام) به تومان ارسال فرمایید:")
        return

    amount = int(raw)
    if amount < 5_000 or amount > 100_000_000:
        await message.answer("مبلغ باید بین ۵,۰۰۰ تا ۱۰۰,۰۰۰,۰۰۰ تومان باشد. لطفاً مبلغ معتبر وارد فرمایید:")
        return

    await state.update_data(amount_toman=amount)
    await state.set_state(WalletReceiptUpload.uploading_photo)
    cancel_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data="wallet:cancel_receipt")]]
    )
    await message.answer(
        f"مبلغ اعلام‌شده: <b>{amount:,} تومان</b>\n\n"
        "لطفاً تصویر یا عکس رسید پرداخت (فیش واریزی) را ارسال فرمایید:\n"
        "(برای انصراف دکمه زیر یا /cancel بزنید)",
        reply_markup=cancel_kb,
    )


@router.message(WalletReceiptUpload.uploading_photo)
async def receive_receipt_photo(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return

    if message.text and message.text.lower() in ("/cancel", "cancel", "انصراف"):
        await state.clear()
        await message.answer("ارسال فیش واریزی لغو شد.")
        return

    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id
    elif message.document and (message.document.mime_type or "").startswith("image/"):
        photo_file_id = message.document.file_id

    if not photo_file_id:
        await message.answer("لطفاً تصویر واضح فیش واریزی یا اسکرین‌شات رسید را به صورت عکس ارسال فرمایید:")
        return

    data = await state.get_data()
    amount_toman = data["amount_toman"]
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        claim = await wallet_service.submit_receipt_claim(
            session,
            user_id=user.id,
            amount_toman=amount_toman,
            photo_file_id=photo_file_id,
        )
        user_display = user.display_name or str(message.chat.id)

    # Clean, readable 8-digit numeric tracking code (MASTER-11)
    tracking_code = str((claim.id.int % 90000000) + 10000000)

    await state.clear()
    await message.answer(
        "✅ <b>فیش واریزی شما با موفقیت ثبت شد.</b>\n\n"
        f"💰 مبلغ اعلام‌شده: <b>{amount_toman:,} تومان</b>\n"
        f"🆔 کد رهگیری: <code>{tracking_code}</code>\n\n"
        "پس از بررسی و تأیید توسط مدیریت، کیف پول شما به صورت خودکار شارژ خواهد شد 🌱"
    )

    # Push to Super Admins in Telegram via Khatm_Saz_bot
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    admin_caption = (
        "🧾 <b>درخواست جدید شارژ کیف پول (فیش واریزی)</b>\n\n"
        f"👤 <b>کاربر:</b> {user_display} (شناسه: <code>{user.id}</code>)\n"
        f"💰 <b>مبلغ اعلام‌شده:</b> <b>{amount_toman:,} تومان</b>\n"
        f"📅 <b>زمان ثبت:</b> {now_str}\n"
        f"🆔 <b>کد رهگیری:</b> <code>{tracking_code}</code>\n\n"
        "لطفاً پس از تطبیق با حساب بانکی، وضعیت را تعیین فرمایید:"
    )
    admin_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✅ تأیید و افزایش اعتبار: {amount_toman:,} تومان",
                    callback_data=f"receipt:approve:{claim.id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ رد فیش واریزی",
                    callback_data=f"receipt:reject:{claim.id}",
                )
            ],
        ]
    )

    from khatmsaz.bot.admin_notifications import notify_super_admins_photo
    await notify_super_admins_photo(
        admin_caption,
        photo_file_id=photo_file_id if message.photo else None,
        source_bot=message.bot,
        reply_markup=admin_markup,
    )


@router.callback_query(F.data.startswith("receipt:approve:"))
async def approve_receipt_callback(callback: CallbackQuery) -> None:
    claim_id_str = callback.data.split(":", 2)[2]
    try:
        claim_id = UUID(claim_id_str)
    except ValueError:
        await safe_answer_callback(callback, "شناسه فیش نامعتبر است.", show_alert=True)
        return

    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(
            session, platform, str(callback.from_user.id)
        )
        settings = get_settings()
        admin_ids = {v.strip() for v in settings.super_admin_telegram_chat_ids.split(",") if v.strip()}
        is_allowed = str(callback.from_user.id) in admin_ids or (admin_user is not None and admin_user.role == UserRole.SUPER_ADMIN)
        if not is_allowed:
            await safe_answer_callback(callback, "شما دسترسی مدیریت برای تأیید این فیش را ندارید.", show_alert=True)
            return

        if admin_user is None:
            admin_user = await identity_service.resolve_or_provision_user(
                session, platform, callback.from_user.id
            )
            admin_user.role = UserRole.SUPER_ADMIN
            await session.flush()

        claim = await wallet_service.get_receipt_claim(session, claim_id)
        if claim is None or claim.status != ReceiptClaimStatus.PENDING.value:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return

        try:
            updated_claim, invoice = await wallet_service.approve_receipt_claim(
                session,
                claim_id=claim.id,
                admin_user_id=admin_user.id,
            )
        except ValueError:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return
        target_identities = await identity_service.list_identities_for_user(session, claim.user_id)
        new_balance, new_credit = await wallet_service.get_balances(session, claim.user_id)

    admin_name = callback.from_user.full_name or "مدیر"
    new_caption = (callback.message.caption or callback.message.text or "")
    new_caption += f"\n\n✅ <b>تأیید شد:</b> مبلغ {claim.amount_toman:,} تومان توسط {admin_name} تأیید و به کیف پول کاربر اضافه گردید."
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            await callback.message.edit_text(text=new_caption, reply_markup=None)
    except Exception:
        pass

    await safe_answer_callback(callback, f"✅ فیش با موفقیت تأیید شد و {claim.amount_toman:,} تومان شارژ گردید.", show_alert=True)

    user_notify_text = (
        "🎉 <b>واریز شما تأیید شد!</b>\n\n"
        f"مبلغ <b>{claim.amount_toman:,} تومان</b> با موفقیت به موجودی کیف پول شما افزوده شد 🌱\n\n"
        f"💰 موجودی فعلی کیف پول: <b>{new_balance:,} تومان</b>"
    )
    from khatmsaz.bot.notify_adapter import get_notify_fn
    try:
        notify = get_notify_fn()
        for ident in target_identities:
            await notify(ident.platform.value, ident.subject, user_notify_text)
    except Exception:
        pass


@router.callback_query(F.data.startswith("receipt:reject:"))
async def reject_receipt_callback(callback: CallbackQuery) -> None:
    claim_id_str = callback.data.split(":", 2)[2]
    try:
        claim_id = UUID(claim_id_str)
    except ValueError:
        await safe_answer_callback(callback, "شناسه فیش نامعتبر است.", show_alert=True)
        return

    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        admin_user = await identity_service.find_by_platform(
            session, platform, str(callback.from_user.id)
        )
        settings = get_settings()
        admin_ids = {v.strip() for v in settings.super_admin_telegram_chat_ids.split(",") if v.strip()}
        is_allowed = str(callback.from_user.id) in admin_ids or (admin_user is not None and admin_user.role == UserRole.SUPER_ADMIN)
        if not is_allowed:
            await safe_answer_callback(callback, "شما دسترسی مدیریت ندارید.", show_alert=True)
            return

        if admin_user is None:
            admin_user = await identity_service.resolve_or_provision_user(
                session, platform, callback.from_user.id
            )
            admin_user.role = UserRole.SUPER_ADMIN
            await session.flush()

        claim = await wallet_service.get_receipt_claim(session, claim_id)
        if claim is None or claim.status != ReceiptClaimStatus.PENDING.value:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return

        try:
            updated_claim = await wallet_service.reject_receipt_claim(
                session,
                claim_id=claim.id,
                admin_user_id=admin_user.id,
            )
        except ValueError:
            await safe_answer_callback(callback, "این فیش قبلاً تعیین وضعیت شده است.", show_alert=True)
            return
        target_identities = await identity_service.list_identities_for_user(session, claim.user_id)

    admin_name = callback.from_user.full_name or "مدیر"
    new_caption = (callback.message.caption or callback.message.text or "")
    new_caption += f"\n\n❌ <b>رد شد:</b> فیش توسط {admin_name} رد شد."
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            await callback.message.edit_text(text=new_caption, reply_markup=None)
    except Exception:
        pass

    await safe_answer_callback(callback, "❌ فیش واریزی رد شد.", show_alert=True)

    user_notify_text = (
        "❌ <b>عدم تأیید فیش واریزی</b>\n\n"
        f"متأسفانه فیش واریزی ارسالی شما برای مبلغ <b>{claim.amount_toman:,} تومان</b> مورد تأیید قرار نگرفت.\n"
        "در صورت کسر وجه از حسابتان، لطفاً با پشتیبانی در ارتباط باشید."
    )
    from khatmsaz.bot.notify_adapter import get_notify_fn
    try:
        notify = get_notify_fn()
        for ident in target_identities:
            await notify(ident.platform.value, ident.subject, user_notify_text)
    except Exception:
        pass

