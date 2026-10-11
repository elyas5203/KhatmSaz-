"""Simple wallet balance and PayPing top-up flow."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.gateway import GatewayError
from khatmsaz.modules.wallet.payping import PayPingGateway

router = Router(name="wallet")

_PLAN_LABEL_KEYS = {"FREE": "wallet.plan_label.FREE", "BASIC": "wallet.plan_label.BASIC", "PRO": "wallet.plan_label.PRO"}
_TOPUP_AMOUNTS = (50_000, 100_000, 200_000, 500_000)
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


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


def _topup_keyboard(lang: str, *, pro_price: int | None = None) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=t("wallet.topup_button", lang, amount=f"{amount // 1000:,}"),
                callback_data=f"wallet_topup:{amount}",
            )
            for amount in _TOPUP_AMOUNTS[:2]
        ],
        [
            InlineKeyboardButton(
                text=t("wallet.topup_button", lang, amount=f"{amount // 1000:,}"),
                callback_data=f"wallet_topup:{amount}",
            )
            for amount in _TOPUP_AMOUNTS[2:]
        ],
        [InlineKeyboardButton(text=t("wallet.topup_custom_button", lang), callback_data="wallet_topup_custom")],
    ]
    if pro_price is not None and pro_price > 0:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"⭐ ارتقا به پلن ویژه و حذف تبلیغات ({pro_price:,} تومان)",
                    callback_data="wallet:buy_pro",
                )
            ]
        )
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
        plan = await plan_service.get_plan(session, user.id)
        if plan.value != "PRO":
            pro_price = await plan_service.get_pro_plan_price(session)

    plan_label = t(_PLAN_LABEL_KEYS.get(plan.value, ""), lang) if plan.value in _PLAN_LABEL_KEYS else plan.value
    await message.answer(
        t("wallet.overview", lang, balance=f"{balance:,}", credit=f"{credit:,}", plan=plan_label),
        reply_markup=_topup_keyboard(lang, pro_price=pro_price),
    )


@router.callback_query(F.data == "wallet:buy_pro")
async def buy_pro_from_wallet(callback: CallbackQuery) -> None:
    platform: Platform = getattr(callback.bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(
                session, platform, callback.message.chat.id
            )
            await plan_service.purchase_pro_plan(session, user.id)
    except wallet_service.InsufficientFundsError:
        await callback.answer(
            "موجودی کیف پول شما برای خرید پلن ویژه کافی نیست. ابتدا کیف پول خود را شارژ کنید.",
            show_alert=True,
        )
        return
    except Exception as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    await callback.answer("🎉 پلن شما با موفقیت به ویژه (PRO) ارتقا یافت!", show_alert=True)
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
    if not invoices:
        await message.answer(t("wallet.no_invoices", lang))
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
    await message.answer("\n".join(lines))


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

