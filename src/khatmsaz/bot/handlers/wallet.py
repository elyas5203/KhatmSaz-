"""Simple wallet balance and PayPing top-up flow."""

from aiogram import F, Router
from aiogram.filters import Command
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


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


def _topup_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
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
        ]
    )


async def _show_wallet(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
        balance, credit = await wallet_service.get_balances(session, user.id)
        plan = await plan_service.get_plan(session, user.id)

    plan_label = t(_PLAN_LABEL_KEYS.get(plan.value, ""), lang) if plan.value in _PLAN_LABEL_KEYS else plan.value
    await message.answer(
        t("wallet.overview", lang, balance=f"{balance:,}", credit=f"{credit:,}", plan=plan_label),
        reply_markup=_topup_keyboard(lang),
    )


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
            _, request = await wallet_service.create_payment_intent(
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
            [InlineKeyboardButton(text=t("wallet.pay_button", lang, amount=f"{amount:,}"), url=request.payment_url)]
        ]
    )
    await callback.message.answer(
        t("wallet.final_topup_step", lang, amount=f"{amount:,}"),
        reply_markup=keyboard,
    )
    await callback.answer(t("wallet.link_created", lang))
