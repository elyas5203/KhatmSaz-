"""FastAPI administration dashboard, authenticated by bot-issued sessions."""

import hashlib
import json
import secrets
from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import String, case, func, or_, select, text
from sqlalchemy.orm import aliased

from khatmsaz.core.db import session_scope
from khatmsaz.core import runtime_status
from khatmsaz.modules.bot_registry import service as bot_registry_service
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.authorization.models import AdminPermission, AdminRole, AdminRoleGrant
from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, User
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.invitation.service import InvitationExpiredError, InvitationNotFoundError
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import CreatorDisplayMode, Khatm, KhatmStatus
from khatmsaz.bot import invite_links
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_category.models import KhatmCategoryRequest, KhatmCategoryRequestStatus
from khatmsaz.modules.manual_phone_verification.models import ManualPhoneVerification
from khatmsaz.modules.khatm_request.models import KhatmRequest, KhatmRequestStatus
from khatmsaz.modules.message_template import repository as template_repository
from khatmsaz.modules.message_template.models import MessageTemplate
from khatmsaz.modules.manual_phone_verification import repository as manual_phone_repository
from khatmsaz.modules.manual_phone_verification import service as manual_phone_service
from khatmsaz.modules.allocation.models import KhatmPortion, PortionStatus
from khatmsaz.modules.notification.models import NotificationKind, NotificationLog
from khatmsaz.modules.open_contribution.models import OpenContribution
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.reporting import service as reporting_service
from khatmsaz.modules.session import service as session_service
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.i18n import t as web_t
from khatmsaz.config import get_settings
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.gateway import GatewayError
from khatmsaz.modules.wallet.payping import PayPingGateway
from khatmsaz.modules.wallet.models import CouponDiscountType, WalletInvoice
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanDefinition, PlanTier, PricingMode
from khatmsaz.modules.sms_subscription import service as sms_subscription_service
from khatmsaz.modules.sms_subscription.models import SmsPlanOption
from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.web.telegram_mini_app import InvalidTelegramInitData, validate_telegram_init_data

COOKIE_NAME = "khatmsaz_admin_session"
CREATOR_COOKIE_NAME = "khatmsaz_creator_session"
CATEGORY_GROUP_LABELS = {"SALAWAT": "صلوات", "LAAN": "لعن", "DUA": "دعا / زیارت"}
FA_LABELS = {
    "ACTIVE": "فعال",
    "DRAFT": "پیش‌نویس",
    "COMPLETED": "تمام‌شده",
    "CANCELLED": "لغوشده",
    "PENDING": "در انتظار",
    "QURAN_PAGE": "صفحات قرآن",
    "SALAWAT": "صلوات",
    "DUA": "ادعیه و زیارات",
    "ZIYARAT": "زیارت",
    "LAAN": "لعن",
    "COMMITMENT": "تعهدی",
    "OPEN": "آزاد",
    "LEFT": "خارج‌شده",
    "REMOVED": "حذف‌شده",
    "MALE": "آقا",
    "FEMALE": "خانم",
    "POSITIONAL": "صفحه‌ای",
    "QUANTITY": "تعدادی",
    "TOPUP": "افزایش موجودی",
    "KHATM_CREATION": "ساخت ختم",
    "PURCHASE": "خرید",
    "PAID": "پرداخت‌شده",
    "REFUNDED": "بازپرداخت‌شده",
    "PERCENT": "درصدی",
    "FIXED": "مبلغ ثابت",
    "CONTENT_ADMIN": "مدیر محتوا",
    "FINANCE_ADMIN": "مدیر مالی",
    "SUPPORT_ADMIN": "مدیر پشتیبانی",
    "MODERATION_ADMIN": "مدیر نظارت",
    "MARKETING_ADMIN": "مدیر بازاریابی",
    "OPERATIONS_ADMIN": "مدیر عملیات",
    "fa": "فارسی",
    "ar": "عربی",
    "en": "انگلیسی",
}
ROOT = Path(__file__).resolve().parent

app = FastAPI(title="پنل مدیریت ختم‌ساز", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")
_INLINE_CSS = (ROOT / "static" / "app.css").read_text(encoding="utf-8") + "\n" + (ROOT / "static" / "finance.css").read_text(encoding="utf-8")
templates.env.globals["inline_css"] = _INLINE_CSS
# "fa" default so unauthenticated pages (e.g. creator_login.html, hit
# before any session/user is resolved) still render correctly; any
# authenticated context that passes its own `lang` (see _creator_ctx)
# overrides this global.
templates.env.globals["t"] = web_t
templates.env.globals["lang"] = "fa"

AUDIT_ACTION_LABELS = {
    "USER_WARN": "اخطار به کاربر",
    "USER_SUSPEND": "تعلیق کاربر",
    "USER_BAN": "مسدودسازی نهایی کاربر",
    "USER_REACTIVATE": "فعال‌سازی دوبارهٔ کاربر",
    "WEB_ADMIN_WARN": "اخطار به کاربر از پنل",
    "WEB_ADMIN_SUSPEND": "تعلیق کاربر از پنل",
    "WEB_ADMIN_BAN": "مسدودسازی نهایی کاربر از پنل",
    "WEB_ADMIN_REACTIVATE": "فعال‌سازی دوبارهٔ کاربر از پنل",
    "CREDIT_GRANT": "افزایش دستی اعتبار",
    "KHATM_CANCEL_REFUND": "بازپرداخت لغو ختم",
    "WEB_COUPON_SET": "ساخت یا ویرایش کد تخفیف",
    "WEB_COUPON_TOGGLE": "تغییر وضعیت کد تخفیف",
    "COUPON_SET": "ساخت یا ویرایش کد تخفیف در بات",
    "COUPON_TOGGLE": "تغییر وضعیت کد تخفیف در بات",
    "WEB_ADMIN_ROLE_GRANTED": "اعطای نقش مدیریتی",
    "WEB_ADMIN_ROLE_REVOKED": "لغو نقش مدیریتی",
    "KHATM_COVER_SUBMIT": "ارسال کاور ختم برای بررسی",
    "KHATM_COVER_REVIEW": "بررسی کاور ختم",
    "KHATM_BROADCAST_APPROVE": "تأیید پیام گروهی",
    "KHATM_BROADCAST_REJECT": "رد پیام گروهی",
    "KHATM_REQUEST_APPROVE": "تأیید درخواست نوع ختم",
    "KHATM_REQUEST_REJECT": "رد درخواست نوع ختم",
    "MESSAGE_TEMPLATE_UPDATE": "ثبت نسخهٔ پیام",
    "MESSAGE_TEMPLATE_TOGGLE": "تغییر وضعیت نسخهٔ پیام",
    "WEB_MESSAGE_TEMPLATE_TOGGLE": "تغییر وضعیت نسخهٔ پیام از پنل",
    "QURAN_ASSET_REGISTER": "ثبت فایل صفحهٔ قرآن",
    "QURAN_CHANNEL_SEED": "بارگذاری نقشهٔ کانال قرآن",
    "QURAN_CHANNEL_POST_REGISTER": "ثبت پست کانال قرآن",
    "DEVOTIONAL_TEXT_UPSERT": "ثبت متن دعا یا زیارت",
    "DEVOTIONAL_AUDIO_REGISTER": "ثبت صوت دعا یا زیارت",
    "AD_REWARD_RATE_UPDATE": "تغییر نرخ پاداش تبلیغاتی",
    "PLAN_DEFINITION_UPDATE": "تغییر تعریف پلن",
    "SMS_PLAN_OPTION_UPDATE": "تغییر گزینهٔ اشتراک پیامک",
    "CREATOR_MISSED_COMMITMENT_DECISION": "تصمیم سازنده برای تعهد انجام‌نشده",
    "PHONE_CHANGE": "تغییر شمارهٔ تأییدشده",
    "PHONE_VERIFY": "تأیید شمارهٔ سازنده",
    "MANUAL_PHONE_VERIFY_APPROVE": "تأیید دستی شمارهٔ خارجی",
    "MANUAL_PHONE_VERIFY_REJECT": "رد تأیید دستی شمارهٔ خارجی",
}

AUDIT_DETAIL_LABELS = {
    "new_phone_last4": "چهار رقم آخر شمارهٔ جدید",
    "phone_last4": "چهار رقم آخر شماره",
    "purpose": "هدف درخواست",
    "replaced_previous": "جایگزین شمارهٔ قبلی شد",
    "amount": "مبلغ",
    "amount_toman": "مبلغ (تومان)",
    "reason": "دلیل",
    "note": "یادداشت",
    "role": "نقش",
    "code": "کد",
    "type": "نوع",
    "value": "مقدار",
    "enabled": "فعال",
    "months": "مدت (ماه)",
    "price_toman": "قیمت (تومان)",
    "plan": "پلن",
    "pricing_mode": "روش قیمت‌گذاری",
    "approved": "تأیید شد",
    "platform": "پیام‌رسان",
    "request_id": "شناسه درخواست",
    "key": "کلید پیام",
    "locale": "زبان",
    "version": "نسخه",
}


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


def _csrf(raw_token: str) -> str:
    return hashlib.sha256(("khatmsaz-csrf:" + raw_token).encode()).hexdigest()


def _valid_csrf(raw_token: str, supplied: str) -> bool:
    return bool(raw_token and supplied) and secrets.compare_digest(_csrf(raw_token), supplied)


async def _admin(request: Request, *required: AdminPermission):
    raw = request.cookies.get(COOKIE_NAME, "")
    async with session_scope() as session:
        user = await session_service.authenticate_admin(session, raw)
        if user is not None:
            permissions = await authorization_service.permissions_for(session, user)
            if required and not any(permission in permissions for permission in required):
                user = None
            else:
                user._admin_permissions = {permission.value for permission in permissions}
    return user, raw


async def _creator(request: Request):
    raw = request.cookies.get(CREATOR_COOKIE_NAME, "")
    async with session_scope() as session:
        user = await session_service.authenticate_creator(session, raw)
        lang = "fa"
        if user is not None:
            settings = await settings_service.get_or_create(session, user.id)
            lang = settings.language
    return user, raw, lang


def _login_redirect() -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)


def _ctx(request: Request, admin, raw_token: str, **extra):
    return {
        "request": request,
        "admin": admin,
        "csrf": _csrf(raw_token),
        "fa_label": _fa_label,
        **extra,
    }


def _creator_ctx(request: Request, creator, raw_token: str, *, lang: str = "fa", **extra):
    return {
        "request": request,
        "creator": creator,
        "csrf": _csrf(raw_token),
        "fa_label": _fa_label,
        "lang": lang,
        "t": web_t,
        "label": lambda value: _web_label(value, lang),
        **extra,
    }


def _fa_label(value) -> str:
    raw = getattr(value, "value", value)
    return FA_LABELS.get(str(raw), str(raw).replace("_", " "))


# Owner scope decision, this session: the web panel IS the Telegram Mini
# App's content, and only the creator-facing pages (not Super-Admin pages)
# need translation — see the "web.*" block in i18n/__init__.py for why.
WEB_LABEL_KEYS = {
    "ACTIVE": "web.label.ACTIVE", "DRAFT": "web.label.DRAFT", "COMPLETED": "web.label.COMPLETED",
    "CANCELLED": "web.label.CANCELLED", "QURAN_PAGE": "web.label.QURAN_PAGE", "SALAWAT": "web.label.SALAWAT",
    "DUA": "web.label.DUA", "ZIYARAT": "web.label.ZIYARAT", "LAAN": "web.label.LAAN",
    "COMMITMENT": "web.label.COMMITMENT", "OPEN": "web.label.OPEN", "MALE": "web.label.MALE",
    "FEMALE": "web.label.FEMALE",
}


def _web_label(value, lang: str = "fa") -> str:
    raw = getattr(value, "value", value)
    key = WEB_LABEL_KEYS.get(str(raw))
    if key:
        return web_t(key, lang)
    return _fa_label(value)


def _payment_gateway() -> PayPingGateway:
    return PayPingGateway(get_settings().payping_api_token)


def _audit_label(action: str) -> str:
    return AUDIT_ACTION_LABELS.get(action, action.replace("_", " "))


def _audit_details(details: dict) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for key, value in (details or {}).items():
        label = AUDIT_DETAIL_LABELS.get(key, key.replace("_", " "))
        if isinstance(value, bool):
            rendered = "بله" if value else "خیر"
        elif isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        else:
            rendered = str(value)
        rows.append((label, rendered))
    return rows


def _tehran_time(value: datetime) -> str:
    return value.astimezone(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d · %H:%M")


def _public_creator_name(khatm: Khatm, creator: User | None) -> str:
    mode = khatm.creator_display_mode
    if mode == CreatorDisplayMode.ANONYMOUS.value:
        return "یک نیکوکار"
    if mode == CreatorDisplayMode.PSEUDONYM.value:
        return khatm.creator_pseudonym or "یک نیکوکار"
    name = creator.display_name if creator and creator.display_name else "یک نیکوکار"
    return name.split()[0] if mode == CreatorDisplayMode.FIRST_NAME.value else name


def _payment_result_page(title: str, message: str, *, success: bool, status_code: int = 200) -> HTMLResponse:
    color = "#16794c" if success else "#a02c2c"
    icon = "✅" if success else "⚠️"
    html = f"""<!doctype html>
<html lang=\"fa\" dir=\"rtl\"><head><meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{title}</title><style>
body{{font-family:Tahoma,Arial,sans-serif;background:#f4f7f5;margin:0;padding:24px;color:#17352a}}
main{{max-width:520px;margin:8vh auto;background:#fff;border-radius:20px;padding:28px;box-shadow:0 12px 40px #17352a18}}
h1{{color:{color};font-size:1.45rem}}p{{line-height:2}}.icon{{font-size:2.5rem}}
</style></head><body><main><div class=\"icon\">{icon}</div><h1>{title}</h1><p>{message}</p>
<p>حالا می‌توانید این صفحه را ببندید و به گفت‌وگوی بات برگردید.</p></main></body></html>"""
    return HTMLResponse(html, status_code=status_code)


@app.get("/health")
async def health():
    """Readiness probe: the HTTP process is useful only while PostgreSQL works."""
    try:
        async with session_scope() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        # Do not expose driver, host, credentials, or schema details publicly.
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unavailable"},
        )
    return {"status": "ok", "database": "ok"}


@app.get("/operations", response_class=HTMLResponse)
async def operations_page(request: Request):
    """Read-only service readiness and queue depth for Operations admins."""
    admin, raw = await _admin(request, AdminPermission.OPERATIONS_VIEW)
    if admin is None:
        return _login_redirect()
    settings = get_settings()
    database_ok = True
    queue_counts = {"broadcasts": 0, "covers": 0, "phones": 0, "categories": 0}
    try:
        async with session_scope() as session:
            await session.execute(text("SELECT 1"))
            queue_counts = {
                "broadcasts": int(await session.scalar(select(func.count()).select_from(KhatmBroadcast).where(KhatmBroadcast.status == BroadcastStatus.PENDING)) or 0),
                "covers": int(await session.scalar(select(func.count()).select_from(Khatm).where(Khatm.cover_status == "PENDING")) or 0),
                "phones": int(await session.scalar(select(func.count()).select_from(ManualPhoneVerification).where(ManualPhoneVerification.status == "PENDING")) or 0),
                "categories": int(await session.scalar(select(func.count()).select_from(KhatmCategoryRequest).where(KhatmCategoryRequest.status == KhatmCategoryRequestStatus.PENDING)) or 0),
            }
    except Exception:
        database_ok = False

    try:
        get_notify_fn()
        messaging_running = True
    except RuntimeError:
        messaging_running = False
    callback_ready = settings.payping_callback_url.lower().startswith("https://")
    services = [
        {"name": "پایگاه داده", "ready": database_ok, "detail": "اتصال PostgreSQL"},
        {"name": "بات تلگرام", "ready": bool(settings.telegram_bot_token) and messaging_running, "detail": "توکن و فرستندهٔ زنده"},
        {"name": "بات بله", "ready": bool(settings.bale_bot_token) and messaging_running, "detail": "توکن و فرستندهٔ زنده"},
        {"name": "پرداخت پی‌پینگ", "ready": bool(settings.payping_api_token) and callback_ready, "detail": "API Token و Callback امن"},
        {"name": "پیامک کاوه‌نگار", "ready": settings.sms_provider.lower() == "kavenegar" and bool(settings.sms_api_key), "detail": "Provider و API Key"},
    ]
    return templates.TemplateResponse(
        request=request,
        name="operations.html",
        context=_ctx(
            request, admin, raw, services=services, queues=queue_counts,
            worker=runtime_status.snapshot(), scan_interval=settings.reminder_scan_interval_minutes,
        ),
    )


@app.get("/join/{token}", response_class=HTMLResponse)
async def public_join_landing(request: Request, token: str):
    unavailable = False
    khatm = creator = None
    member_count = 0
    khatm_bot_cat = None
    try:
        async with session_scope() as session:
            khatm_id = await invitation_service.resolve_khatm_id(session, token)
            khatm = await session.get(Khatm, khatm_id)
            if khatm is None or khatm.status != KhatmStatus.ACTIVE:
                unavailable = True
            else:
                creator = await identity_service.find_by_id(session, khatm.creator_user_id)
                member_count = int(
                    await session.scalar(
                        select(func.count()).select_from(Participation).where(
                            Participation.khatm_id == khatm.id,
                            Participation.status == ParticipationStatus.ACTIVE,
                        )
                    )
                    or 0
                )
                khatm_bot_cat = await invite_links.resolve_khatm_category_value(session, khatm)
    except (InvitationNotFoundError, InvitationExpiredError):
        unavailable = True

    # Build one button per configured member bot (category + language), so a
    # visitor lands directly in the correct member bot. Falls back to the
    # creator bot only if no member bot is configured for this category.
    links: list[dict] = []
    if not unavailable:
        lang_names = {"fa": "فارسی", "ar": "عربی", "en": "English"}
        try:
            by_lang = invite_links.build_member_invite_links(khatm_bot_cat, token)
        except Exception:
            by_lang = {}
        for lang_code, urls in by_lang.items():
            label = lang_names.get(lang_code, lang_code)
            if urls.get("telegram"):
                links.append({"name": f"تلگرام · {label}", "url": urls["telegram"], "is_telegram": True})
            if urls.get("bale"):
                links.append({"name": f"بله · {label}", "url": urls["bale"], "is_telegram": False})
        if not links:
            settings = get_settings()
            if settings.telegram_bot_username:
                links.append({"name": "ورود با تلگرام", "url": f"https://t.me/{settings.telegram_bot_username}?start=join_{token}", "is_telegram": True})
            if settings.bale_bot_username:
                links.append({"name": "ورود با بله", "url": f"https://ble.ir/{settings.bale_bot_username}?start=join_{token}", "is_telegram": False})

    return templates.TemplateResponse(
        request=request,
        name="join.html",
        context={
            "request": request,
            "unavailable": unavailable,
            "khatm": khatm,
            "creator_name": _public_creator_name(khatm, creator) if khatm else "",
            "member_count": member_count,
            "links": links,
            "no_bots": not links,
        },
        status_code=404 if unavailable else 200,
    )


@app.post("/payments/payping/callback", response_class=HTMLResponse)
async def payping_callback(request: Request):
    """Receive PayPing's form POST and credit the bound wallet exactly once."""
    try:
        form = await request.form()
        status = int(str(form.get("status", "0")))
        if status != 1:
            return _payment_result_page(
                "پرداخت کامل نشد",
                "بانک پرداخت را موفق اعلام نکرد. هیچ مبلغی به کیف پول اضافه نشده است.",
                success=False,
                status_code=400,
            )

        raw_data = form.get("data", "")
        data = json.loads(str(raw_data))
        if not isinstance(data, dict):
            raise ValueError("callback data is not an object")
        client_ref_id = str(data.get("clientRefId") or "")
        authority = str(data.get("paymentCode") or "")
        transaction_ref = str(data.get("paymentRefId") or "")
        amount_toman = int(data.get("amount"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return _payment_result_page(
            "پاسخ پرداخت نامعتبر است",
            "اطلاعات برگشتی بانک کامل یا معتبر نبود. کیف پول تغییر نکرد.",
            success=False,
            status_code=400,
        )

    try:
        gateway = _payment_gateway()
    except ValueError:
        return _payment_result_page(
            "درگاه هنوز فعال نیست",
            "توکن اختصاصی پی‌پینگ روی سرور تنظیم نشده است. کیف پول تغییر نکرد.",
            success=False,
            status_code=503,
        )

    try:
        async with session_scope() as session:
            await wallet_service.verify_payping_callback_and_credit(
                session,
                gateway,
                client_ref_id=client_ref_id,
                authority=authority,
                amount_toman=amount_toman,
                transaction_ref=transaction_ref,
            )
    except wallet_service.PaymentAlreadyProcessedError:
        return _payment_result_page(
            "پرداخت قبلاً ثبت شده است",
            "این تراکنش قبلاً با موفقیت به کیف پول اضافه شده و دوباره شارژ نشد.",
            success=True,
        )
    except wallet_service.InvalidPaymentError:
        return _payment_result_page(
            "پرداخت قابل تأیید نیست",
            "اطلاعات پرداخت با درخواست ذخیره‌شده تطبیق نداشت یا زمان آن گذشته است. کیف پول تغییر نکرد.",
            success=False,
            status_code=400,
        )
    except GatewayError:
        return _payment_result_page(
            "تأیید پرداخت در حال بررسی است",
            "پی‌پینگ فعلاً نتیجهٔ قطعی نداد. برای جلوگیری از شارژ اشتباه، کیف پول هنوز تغییر نکرده است.",
            success=False,
            status_code=502,
        )

    return _payment_result_page(
        "کیف پول شارژ شد",
        f"پرداخت {amount_toman:,} تومان با موفقیت تأیید و فقط یک بار به کیف پول شما اضافه شد.",
        success=True,
    )


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request, token: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "invalid": bool(token)},
        status_code=401 if token else 200,
    )


def _mini_app_page(request: Request, *, purpose: str, error: str = "", status_code: int = 200):
    return templates.TemplateResponse(
        request=request,
        name="mini_app_login.html",
        context={
            "request": request,
            "title": "مدیریت ختم‌ساز" if purpose == "admin" else "پنل سازندهٔ ختم",
            "auth_path": f"/mini/{purpose}/auth",
            "error": error,
        },
        status_code=status_code,
    )


@app.get("/mini/admin", response_class=HTMLResponse)
async def telegram_admin_mini_app(request: Request):
    return _mini_app_page(request, purpose="admin")


@app.get("/mini/creator", response_class=HTMLResponse)
async def telegram_creator_mini_app(request: Request):
    return _mini_app_page(request, purpose="creator")


async def _authenticate_telegram_mini_app(request: Request, init_data: str, *, purpose: str):
    try:
        signed_user = validate_telegram_init_data(init_data, get_settings().telegram_bot_token)
    except InvalidTelegramInitData:
        return _mini_app_page(
            request, purpose=purpose,
            error="ورود معتبر نیست یا زمان آن گذشته است. پنجره را ببندید و دوباره از داخل بات باز کنید.",
            status_code=401,
        )
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, Platform.TELEGRAM, str(signed_user.id))
        if user is None:
            return _mini_app_page(
                request, purpose=purpose,
                error="ابتدا در بات دکمهٔ شروع را بزنید و ثبت‌نام را کامل کنید.", status_code=403,
            )
        try:
            if purpose == "admin":
                raw_token = await session_service.issue_admin_session(session, user)
                destination, cookie_name, cookie_path = "/", COOKIE_NAME, "/"
            else:
                if not await khatm_service.list_my_created(session, user.id):
                    raise PermissionError
                raw_token = await session_service.issue_creator_session(session, user)
                destination, cookie_name, cookie_path = "/creator", CREATOR_COOKIE_NAME, "/creator"
        except PermissionError:
            return _mini_app_page(
                request, purpose=purpose, error="این بخش برای حساب شما فعال نیست.", status_code=403
            )
    response = RedirectResponse(destination, status_code=303)
    response.set_cookie(
        cookie_name, raw_token, max_age=8 * 60 * 60, httponly=True,
        samesite="lax", secure=True, path=cookie_path,
    )
    return response


@app.post("/mini/admin/auth")
async def telegram_admin_mini_app_auth(request: Request, init_data: str = Form(...)):
    return await _authenticate_telegram_mini_app(request, init_data, purpose="admin")


@app.post("/mini/creator/auth")
async def telegram_creator_mini_app_auth(request: Request, init_data: str = Form(...)):
    return await _authenticate_telegram_mini_app(request, init_data, purpose="creator")


@app.post("/logout")
async def logout(request: Request, csrf: str = Form("")):
    admin, raw = await _admin(request)
    if admin is not None and _valid_csrf(raw, csrf):
        async with session_scope() as session:
            await session_service.revoke_admin_session(session, raw)
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(COOKIE_NAME, path="/")
    return response


@app.get("/creator/login", response_class=HTMLResponse)
async def creator_login(request: Request, token: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="creator_login.html",
        context={"request": request, "invalid": bool(token)},
        status_code=401 if token else 200,
    )


@app.post("/creator/logout")
async def creator_logout(request: Request, csrf: str = Form("")):
    creator, raw, _lang = await _creator(request)
    if creator is not None and _valid_csrf(raw, csrf):
        async with session_scope() as session:
            await session_service.revoke_web_session(session, raw, purpose="CREATOR")
    response = RedirectResponse("/creator/login", status_code=303)
    response.delete_cookie(CREATOR_COOKIE_NAME, path="/creator")
    return response


@app.get("/creator", response_class=HTMLResponse)
async def creator_dashboard(request: Request, page: int = 1):
    creator, raw, lang = await _creator(request)
    if creator is None:
        return RedirectResponse("/creator/login", status_code=303)
    page = max(1, min(page, 10_000))
    page_size = 25
    async with session_scope() as session:
        khatms = list((await session.execute(
            select(Khatm)
            .where(Khatm.creator_user_id == creator.id)
            .order_by(Khatm.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size + 1)
        )).scalars())
        has_next = len(khatms) > page_size
        khatms = khatms[:page_size]
        khatm_ids = [item.id for item in khatms]
        member_counts = dict(
            (
                await session.execute(
                    select(Participation.khatm_id, func.count())
                    .where(
                        Participation.status == ParticipationStatus.ACTIVE,
                        Participation.khatm_id.in_(khatm_ids),
                    )
                    .group_by(Participation.khatm_id)
                )
            ).all()
        ) if khatm_ids else {}
    return templates.TemplateResponse(
        request=request,
        name="creator_dashboard.html",
        context=_creator_ctx(
            request, creator, raw, lang=lang, khatms=khatms, member_counts=member_counts,
            page=page, has_next=has_next,
        ),
    )


async def _load_creator_member_rows(
    session, khatm_id: UUID, *, query: str = "", limit: int = 250, offset: int = 0
) -> list[dict]:
    member_stmt = (
        select(Participation, User, UserSettings)
        .join(User, User.id == Participation.user_id)
        .outerjoin(UserSettings, UserSettings.user_id == User.id)
        .where(Participation.khatm_id == khatm_id)
        .order_by(Participation.joined_at.desc())
        .offset(max(0, offset))
        .limit(limit)
    )
    query = query.strip()
    if query:
        pattern = f"%{query}%"
        member_stmt = member_stmt.where(
            or_(
                User.display_name.ilike(pattern),
                UserSettings.contact_phone.ilike(pattern),
                UserSettings.province.ilike(pattern),
                UserSettings.city.ilike(pattern),
            )
        )
    member_records = list((await session.execute(member_stmt)).all())
    participation_ids = [membership.id for membership, _, _ in member_records]
    completed_by_participation = {}
    misses_by_participation = {}
    contributions_by_participation = {}
    if participation_ids:
        completed_by_participation = dict(
            (
                await session.execute(
                    select(KhatmPortion.participation_id, func.count())
                    .where(
                        KhatmPortion.participation_id.in_(participation_ids),
                        KhatmPortion.status == PortionStatus.COMPLETED,
                    )
                    .group_by(KhatmPortion.participation_id)
                )
            ).all()
        )
        misses_by_participation = dict(
            (
                await session.execute(
                    select(NotificationLog.participation_id, func.count())
                    .where(
                        NotificationLog.participation_id.in_(participation_ids),
                        NotificationLog.kind == NotificationKind.FOLLOW_UP,
                    )
                    .group_by(NotificationLog.participation_id)
                )
            ).all()
        )
        contributions_by_participation = {
            participation_id: (float(total or 0), float(surplus or 0))
            for participation_id, total, surplus in (
                await session.execute(
                    select(
                        OpenContribution.participation_id,
                        func.sum(OpenContribution.amount),
                        func.sum(OpenContribution.surplus_amount),
                    )
                    .where(OpenContribution.participation_id.in_(participation_ids))
                    .group_by(OpenContribution.participation_id)
                )
            ).all()
        }
    return [
        {
            "membership": membership,
            "user": user,
            "settings": settings,
            "joined_at": _tehran_time(membership.joined_at),
            "completed": int(completed_by_participation.get(membership.id, 0)),
            "misses": int(misses_by_participation.get(membership.id, 0)),
            "contribution": contributions_by_participation.get(membership.id, (0.0, 0.0))[0],
            "surplus": contributions_by_participation.get(membership.id, (0.0, 0.0))[1],
        }
        for membership, user, settings in member_records
    ]


@app.get("/creator/khatms/{khatm_id}", response_class=HTMLResponse)
async def creator_khatm_detail(
    request: Request, khatm_id: UUID, q: str = "", page: int = 1
):
    creator, raw, lang = await _creator(request)
    if creator is None:
        return RedirectResponse("/creator/login", status_code=303)
    page = max(1, min(page, 10_000))
    page_size = 25
    query = q.strip()[:100]
    async with session_scope() as session:
        khatm = await session.get(Khatm, khatm_id)
        if khatm is None or khatm.creator_user_id != creator.id:
            return HTMLResponse(web_t("web.creator.khatm_not_found", lang), status_code=404)
        stats = await reporting_service.get_khatm_stats(session, khatm.id)
        rows = await _load_creator_member_rows(
            session, khatm.id, query=query, limit=page_size + 1,
            offset=(page - 1) * page_size,
        )
        has_next = len(rows) > page_size
        rows = rows[:page_size]
    return templates.TemplateResponse(
        request=request,
        name="creator_khatm_detail.html",
        context=_creator_ctx(
            request, creator, raw, lang=lang, khatm=khatm, stats=stats, rows=rows,
            query=query, page=page, has_next=has_next,
        ),
    )


@app.get("/creator/khatms/{khatm_id}/export.xlsx")
async def creator_khatm_export(request: Request, khatm_id: UUID):
    """Full member info export for a khatm's own creator (owner request,
    2026-09-18): one row per member with every field a creator would need
    to reach them, no info held back since it's their own khatm."""
    creator, _raw, _lang = await _creator(request)
    if creator is None:
        return RedirectResponse("/creator/login", status_code=303)
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter

    async with session_scope() as session:
        khatm = await session.get(Khatm, khatm_id)
        if khatm is None or khatm.creator_user_id != creator.id:
            return HTMLResponse("این ختم در پنل شما وجود ندارد.", status_code=404)
        rows = await _load_creator_member_rows(session, khatm.id, limit=100000)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "اعضا"
    sheet.sheet_view.rightToLeft = True
    headers = [
        "نام نمایشی",
        "شماره تماس",
        "استان",
        "شهر",
        "جنسیت",
        "تاریخ عضویت (تهران)",
        "سهم‌های تکمیل‌شده",
        "یادآوری‌های ازدست‌رفته",
        "مبلغ مشارکت",
        "مازاد مشارکت",
    ]
    sheet.append(headers)
    for row in rows:
        user = row["user"]
        settings = row["settings"]
        gender = "" if settings is None or settings.gender is None else (
            "آقا" if settings.gender.value == "MALE" else "خانم"
        )
        sheet.append(
            [
                user.display_name or "",
                (settings.contact_phone if settings else "") or "",
                (settings.province if settings else "") or "",
                (settings.city if settings else "") or "",
                gender,
                row["joined_at"] or "",
                row["completed"],
                row["misses"],
                row["contribution"],
                row["surplus"],
            ]
        )
    for index in range(1, len(headers) + 1):
        sheet.column_dimensions[get_column_letter(index)].width = 20

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    filename = f"khatm-members-{khatm_id}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    admin, raw = await _admin(request)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        users = await session.scalar(select(func.count()).select_from(User))
        active_khatms = await session.scalar(
            select(func.count()).select_from(Khatm).where(Khatm.status == KhatmStatus.ACTIVE)
        )
        active_members = await session.scalar(
            select(func.count()).select_from(Participation).where(
                Participation.status == ParticipationStatus.ACTIVE
            )
        )
        pending_covers = await session.scalar(
            select(func.count()).select_from(Khatm).where(Khatm.cover_status == "PENDING")
        )
        pending_broadcasts = await session.scalar(
            select(func.count()).select_from(KhatmBroadcast).where(
                KhatmBroadcast.status == BroadcastStatus.PENDING
            )
        )
        pending_requests = await session.scalar(
            select(func.count()).select_from(KhatmRequest).where(
                KhatmRequest.status == KhatmRequestStatus.PENDING
            )
        )
        recent = list(
            (await session.execute(select(Khatm).order_by(Khatm.created_at.desc()).limit(8))).scalars()
        )
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=_ctx(
            request,
            admin,
            raw,
            counts={
                "users": int(users or 0),
                "active_khatms": int(active_khatms or 0),
                "active_members": int(active_members or 0),
                "pending": int(pending_covers or 0) + int(pending_broadcasts or 0) + int(pending_requests or 0),
            },
            pending={
                "covers": int(pending_covers or 0),
                "broadcasts": int(pending_broadcasts or 0),
                "requests": int(pending_requests or 0),
            },
            recent=recent,
        ),
    )


@app.get("/khatms", response_class=HTMLResponse)
async def khatms(request: Request, status: str = "", q: str = "", page: int = 1):
    admin, raw = await _admin(
        request, AdminPermission.SUPPORT_USERS, AdminPermission.MODERATION_MANAGE
    )
    if admin is None:
        return _login_redirect()
    creator = aliased(User)
    page = max(1, min(page, 10_000))
    page_size = 25
    stmt = (
        select(
            Khatm,
            func.count(case((Participation.status == ParticipationStatus.ACTIVE, 1))).label("members"),
        )
        .outerjoin(creator, creator.id == Khatm.creator_user_id)
        .outerjoin(Participation, Participation.khatm_id == Khatm.id)
        .group_by(Khatm.id)
        .order_by(Khatm.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size + 1)
    )
    if status in {item.value for item in KhatmStatus}:
        stmt = stmt.where(Khatm.status == KhatmStatus(status))
    query = q.strip()[:100]
    if query:
        pattern = f"%{query}%"
        stmt = stmt.where(
            or_(
                Khatm.title.ilike(pattern),
                creator.display_name.ilike(pattern),
                Khatm.id.cast(String).ilike(pattern),
            )
        )
    async with session_scope() as session:
        rows = list((await session.execute(stmt)).all())
    has_next = len(rows) > page_size
    rows = rows[:page_size]
    return templates.TemplateResponse(
        request=request,
        name="khatms.html",
        context=_ctx(
            request, admin, raw, rows=rows, selected_status=status, query=query,
            page=page, has_next=has_next,
        ),
    )


@app.get("/khatms/{khatm_id}", response_class=HTMLResponse)
async def khatm_detail(request: Request, khatm_id: UUID):
    admin, raw = await _admin(
        request, AdminPermission.SUPPORT_USERS, AdminPermission.MODERATION_MANAGE
    )
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        khatm = await session.get(Khatm, khatm_id)
        if khatm is None:
            return RedirectResponse("/khatms", status_code=303)
        stats = await reporting_service.get_khatm_stats(session, khatm.id)
        members = list(
            (
                await session.execute(
                    select(Participation, User)
                    .join(User, User.id == Participation.user_id)
                    .where(Participation.khatm_id == khatm.id)
                    .order_by(Participation.joined_at.desc())
                    .limit(100)
                )
            ).all()
        )
    return templates.TemplateResponse(
        request=request,
        name="khatm_detail.html",
        context=_ctx(request, admin, raw, khatm=khatm, stats=stats, members=members),
    )


@app.get("/users", response_class=HTMLResponse)
async def users(request: Request, q: str = "", page: int = 1):
    admin, raw = await _admin(
        request, AdminPermission.SUPPORT_USERS, AdminPermission.MODERATION_MANAGE
    )
    if admin is None:
        return _login_redirect()
    page = max(1, min(page, 10_000))
    page_size = 25
    query = q.strip()[:100]
    async with session_scope() as session:
        found = await identity_service.search_users(
            session, query, limit=page_size + 1, offset=(page - 1) * page_size
        )
    has_next = len(found) > page_size
    found = found[:page_size]
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context=_ctx(
            request, admin, raw, users=found, query=query, page=page, has_next=has_next
        ),
    )


@app.get("/phone-verifications", response_class=HTMLResponse)
async def phone_verifications(request: Request):
    admin, raw = await _admin(request, AdminPermission.SUPPORT_USERS)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        pending = await manual_phone_repository.list_pending(session)
        rows = []
        for item in pending:
            user = await identity_service.find_by_id(session, item.user_id)
            profile = await session.get(UserSettings, item.user_id)
            rows.append(
                {
                    "item": item,
                    "user": user,
                    "profile": profile,
                    "time": _tehran_time(item.created_at),
                    "purpose": "تغییر شماره" if item.purpose == "PHONE_CHANGE" else "فعال‌سازی سازنده",
                }
            )
    return templates.TemplateResponse(
        request=request,
        name="phone_verifications.html",
        context=_ctx(
            request,
            admin,
            raw,
            rows=rows,
            saved=request.query_params.get("saved", ""),
        ),
    )


@app.post("/phone-verifications/{request_id}/decide")
async def decide_phone_verification(
    request: Request,
    request_id: UUID,
    decision: str = Form(...),
    csrf: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.SUPPORT_USERS)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    if decision not in {"approve", "reject"}:
        return HTMLResponse("تصمیم نامعتبر است.", status_code=400)
    try:
        async with session_scope() as session:
            actor = await identity_service.find_by_id(session, admin.id)
            if decision == "approve":
                item, _ = await manual_phone_service.approve(
                    session, request_id=request_id, admin_user_id=actor.id
                )
            else:
                item = await manual_phone_service.reject(
                    session,
                    request_id=request_id,
                    admin_user_id=actor.id,
                    note="رد از پنل ادمین",
                )
            identities = await identity_service.list_identities_for_user(
                session, item.user_id
            )
    except manual_phone_service.ManualVerificationError as exc:
        return HTMLResponse(f"درخواست قابل انجام نیست: {exc}", status_code=409)

    approved = decision == "approve"
    notification = (
        "شمارهٔ خارج از کشور شما توسط مدیریت تأیید شد ✅\n"
        "این تأیید دائمی است و حالا می‌توانید ختم بسازید."
        if approved
        else "درخواست تأیید شمارهٔ شما رد شد. لطفاً شماره و مشخصات پروفایل را بررسی کنید."
    )
    try:
        notify = get_notify_fn()
    except RuntimeError:
        notify = None
    if notify is not None:
        for identity in identities:
            await notify(identity.platform.value, identity.subject, notification)
    return RedirectResponse(
        f"/phone-verifications?saved={'approved' if approved else 'rejected'}",
        status_code=303,
    )


@app.get("/broadcasts", response_class=HTMLResponse)
async def broadcasts_page(request: Request):
    """Group-message moderation queue, reachable from the admin panel
    (owner request, 2026-09-18): a creator's `/khatm_message` submission
    lands here for one-click approve/reject instead of typed bot commands."""
    admin, raw = await _admin(request, AdminPermission.MODERATION_MANAGE)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        pending = await broadcast_service.list_pending(session)
        rows = []
        for item in pending:
            khatm = await session.get(Khatm, item.khatm_id)
            creator = await identity_service.find_by_id(session, item.creator_user_id)
            rows.append(
                {
                    "item": item,
                    "khatm": khatm,
                    "creator": creator,
                    "time": _tehran_time(item.created_at),
                }
            )
    return templates.TemplateResponse(
        request=request,
        name="broadcasts.html",
        context=_ctx(request, admin, raw, rows=rows, saved=request.query_params.get("saved", "")),
    )


@app.post("/broadcasts/{broadcast_id}/decide")
async def decide_broadcast(
    request: Request,
    broadcast_id: UUID,
    decision: str = Form(...),
    csrf: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.MODERATION_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    if decision not in {"approve", "reject"}:
        return HTMLResponse("تصمیم نامعتبر است.", status_code=400)
    async with session_scope() as session:
        try:
            item = await (broadcast_service.approve if decision == "approve" else broadcast_service.reject)(
                session, broadcast_id, "تأیید از پنل ادمین" if decision == "approve" else "رد از پنل ادمین"
            )
        except ValueError:
            return HTMLResponse("این پیام پیدا نشد یا دیگر در انتظار بررسی نیست.", status_code=409)
        actor = await identity_service.find_by_id(session, admin.id)
        await audit_service.record(
            session,
            actor_user_id=actor.id,
            target_khatm_id=item.khatm_id,
            action="KHATM_BROADCAST_APPROVE" if decision == "approve" else "KHATM_BROADCAST_REJECT",
            details={"broadcast_id": str(item.id)},
        )
        if decision == "approve":
            participants = await participation_service.list_active_for_khatm(session, item.khatm_id)
            identities = []
            for participant in participants:
                identities.extend(await identity_service.list_identities_for_user(session, participant.user_id))
            notify = get_notify_fn()
            for identity in identities:
                await notify(identity.platform.value, identity.subject, item.body)
            await broadcast_service.mark_sent(session, item)
    return RedirectResponse(
        f"/broadcasts?saved={'approved' if decision == 'approve' else 'rejected'}", status_code=303
    )


@app.get("/admins", response_class=HTMLResponse)
async def admins(request: Request, q: str = ""):
    admin, raw = await _admin(request, AdminPermission.ADMIN_ROLES_MANAGE)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        active_grants = list(
            (
                await session.execute(
                    select(AdminRoleGrant, User)
                    .join(User, User.id == AdminRoleGrant.user_id)
                    .where(AdminRoleGrant.revoked_at.is_(None))
                    .order_by(User.display_name.asc(), AdminRoleGrant.role.asc())
                )
            ).all()
        )
        found = (
            await identity_service.search_users(session, q.strip(), limit=30)
            if q.strip()
            else []
        )
    return templates.TemplateResponse(
        request=request,
        name="admins.html",
        context=_ctx(
            request,
            admin,
            raw,
            active_grants=active_grants,
            users=found,
            query=q,
            roles=list(AdminRole),
            saved=request.query_params.get("saved", ""),
        ),
    )


@app.get("/audit", response_class=HTMLResponse)
async def audit_timeline(request: Request, q: str = ""):
    admin, raw = await _admin(request, AdminPermission.OPERATIONS_VIEW)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        entries = await audit_service.list_recent(session, action_query=q, limit=100)
        user_ids = {
            user_id
            for entry in entries
            for user_id in (entry.actor_user_id, entry.target_user_id)
            if user_id is not None
        }
        khatm_ids = {entry.target_khatm_id for entry in entries if entry.target_khatm_id is not None}
        users_by_id = {
            user.id: user
            for user in (
                list((await session.execute(select(User).where(User.id.in_(user_ids)))).scalars())
                if user_ids
                else []
            )
        }
        khatms_by_id = {
            khatm.id: khatm
            for khatm in (
                list((await session.execute(select(Khatm).where(Khatm.id.in_(khatm_ids)))).scalars())
                if khatm_ids
                else []
            )
        }
        rows = [
            {
                "entry": entry,
                "label": _audit_label(entry.action),
                "time": _tehran_time(entry.created_at),
                "actor": users_by_id.get(entry.actor_user_id),
                "target_user": users_by_id.get(entry.target_user_id),
                "target_khatm": khatms_by_id.get(entry.target_khatm_id),
                "details": _audit_details(entry.details),
            }
            for entry in entries
        ]
    return templates.TemplateResponse(
        request=request,
        name="audit.html",
        context=_ctx(request, admin, raw, rows=rows, query=q),
    )


@app.post("/admins/{user_id}/roles")
async def change_admin_role(
    request: Request,
    user_id: UUID,
    csrf: str = Form(...),
    role: str = Form(...),
    action: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.ADMIN_ROLES_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    try:
        role_value = AdminRole(role.upper())
    except ValueError:
        return HTMLResponse("نقش انتخاب‌شده معتبر نیست.", status_code=400)
    if action not in {"grant", "revoke"}:
        return HTMLResponse("عملیات نقش معتبر نیست.", status_code=400)
    async with session_scope() as session:
        actor = await identity_service.find_by_id(session, admin.id)
        target = await identity_service.find_by_id(session, user_id)
        if target is None:
            return HTMLResponse("کاربر پیدا نشد.", status_code=404)
        if action == "grant":
            await authorization_service.grant_role(
                session, actor=actor, target=target, role=role_value
            )
            changed = True
        else:
            changed = await authorization_service.revoke_role(
                session, actor=actor, target=target, role=role_value
            )
        if changed:
            await audit_service.record(
                session,
                actor_user_id=actor.id,
                target_user_id=target.id,
                action="WEB_ADMIN_ROLE_GRANTED" if action == "grant" else "WEB_ADMIN_ROLE_REVOKED",
                details={"role": role_value.value},
            )
    return RedirectResponse("/admins?saved=1", status_code=303)


@app.post("/users/{user_id}/moderate")
async def moderate_user(
    request: Request,
    user_id: UUID,
    action: str = Form(...),
    csrf: str = Form(...),
    q: str = Form(""),
):
    admin, raw = await _admin(request, AdminPermission.MODERATION_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    actions = {
        "warn": identity_service.warn,
        "suspend": identity_service.suspend,
        "ban": identity_service.ban,
        "reactivate": identity_service.reactivate,
        "promote": identity_service.promote_creator,
        "demote": identity_service.demote_creator,
    }
    if action not in actions or user_id == admin.id:
        return HTMLResponse("عملیات مجاز نیست.", status_code=400)
    async with session_scope() as session:
        target = await identity_service.find_by_id(session, user_id)
        if target is None:
            return HTMLResponse("کاربر پیدا نشد.", status_code=404)
        await actions[action](session, user_id)
        if action in ("promote", "demote"):
            from khatmsaz.bot.keyboards import main_menu_keyboard
            from khatmsaz.modules.settings import service as settings_service
            user_settings = await settings_service.get_or_create(session, target.id)
            if target.platform_identities:
                pi = target.platform_identities[0]
                if action == "promote":
                    msg = "🎉 تبریک! حساب شما به **سازنده ختم** ارتقا یافت.\n\nهم‌اکنون منوی اختصاصی مدیریت ختم‌ها برای شما فعال شد. می‌توانید از دکمه‌های پایین صفحه استفاده کنید."
                    kb = main_menu_keyboard(user_settings.language, is_creator=True)
                else:
                    msg = "حساب شما از سطح سازنده به **کاربر عادی** تغییر یافت."
                    kb = main_menu_keyboard(user_settings.language, is_creator=False)
                from khatmsaz.bot.notify_adapter import send_with_keyboard
                import asyncio
                asyncio.create_task(
                    send_with_keyboard(pi.platform.value, pi.subject, msg, kb)
                )
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            target_user_id=user_id,
            action=f"WEB_ADMIN_{action.upper()}",
        )
    return RedirectResponse(f"/users?q={q}", status_code=303)


@app.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request):
    """Admin CRUD for صلوات/لعن/ادعیه content items (owner request,
    2026-09-18): new khatm categories must be addable without a code
    deploy — see `khatm_category` module."""
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        items = await category_service.list_all(session)
        devotional_assets = await content_service.list_all_devotional_assets(session)
        requests = await category_service.list_pending_requests(session)
        request_rows = []
        for item in requests:
            requester = await identity_service.find_by_id(session, item.requested_by_user_id)
            request_rows.append({"item": item, "requester": requester})
    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context=_ctx(
            request, admin, raw, items=items, requests=request_rows,
            devotional_assets=devotional_assets,
            group_labels=CATEGORY_GROUP_LABELS,
            saved=request.query_params.get("saved", ""),
        ),
    )


@app.post("/categories/create")
async def create_category(
    request: Request,
    group: str = Form(...),
    title: str = Form(...),
    body_text: str = Form(""),
    source_note: str = Form(""),
    devotional_slug: str = Form(""),
    image_url: str = Form(""),
    csrf: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        try:
            category = await category_service.create(
                session, group=group, title=title, body_text=body_text, source_note=source_note,
                devotional_slug=devotional_slug, image_url=image_url,
            )
        except ValueError as exc:
            return HTMLResponse(f"ورودی نامعتبر: {exc}", status_code=400)
        await audit_service.record(
            session, actor_user_id=admin.id, action="KHATM_CATEGORY_CREATE",
            details={"category_id": str(category.id), "group": category.group.value, "title": category.title},
        )
    return RedirectResponse("/categories?saved=created", status_code=303)


@app.post("/categories/{category_id}/update")
async def update_category(
    request: Request,
    category_id: UUID,
    title: str = Form(...),
    body_text: str = Form(""),
    source_note: str = Form(""),
    devotional_slug: str = Form(""),
    image_url: str = Form(""),
    csrf: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        try:
            category = await category_service.update(
                session, category_id, title=title, body_text=body_text, source_note=source_note,
                devotional_slug=devotional_slug, image_url=image_url,
            )
        except ValueError as exc:
            return HTMLResponse(f"ورودی نامعتبر: {exc}", status_code=400)
        await audit_service.record(
            session, actor_user_id=admin.id, action="KHATM_CATEGORY_UPDATE",
            details={"category_id": str(category.id), "title": category.title},
        )
    return RedirectResponse("/categories?saved=updated", status_code=303)


@app.post("/categories/{category_id}/toggle")
async def toggle_category(request: Request, category_id: UUID, csrf: str = Form(...)):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        category = await category_service.get(session, category_id)
        if category is None:
            return HTMLResponse("پیدا نشد.", status_code=404)
        category = await category_service.set_active(session, category_id, not category.is_active)
        await audit_service.record(
            session, actor_user_id=admin.id, action="KHATM_CATEGORY_TOGGLE",
            details={"category_id": str(category.id), "enabled": category.is_active},
        )
    return RedirectResponse("/categories?saved=toggled", status_code=303)


@app.post("/categories/requests/{request_id}/decline")
async def decline_category_request(request: Request, request_id: UUID, csrf: str = Form(...)):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        try:
            item = await category_service.decline_request(session, request_id)
        except ValueError as exc:
            return HTMLResponse(f"درخواست قابل پردازش نیست: {exc}", status_code=409)
        await audit_service.record(
            session, actor_user_id=admin.id, action="KHATM_CATEGORY_REQUEST_DECLINE",
            target_user_id=item.requested_by_user_id, details={"request_id": str(item.id)},
        )
    return RedirectResponse("/categories?saved=declined", status_code=303)


@app.post("/categories/requests/{request_id}/fulfill")
async def fulfill_category_request(
    request: Request,
    request_id: UUID,
    group: str = Form(...),
    title: str = Form(...),
    body_text: str = Form(""),
    source_note: str = Form(""),
    image_url: str = Form(""),
    devotional_slug: str = Form(""),
    csrf: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        try:
            req, category = await category_service.fulfill_request(
                session, request_id, group=group, title=title, body_text=body_text, source_note=source_note,
                image_url=image_url, devotional_slug=devotional_slug,
            )
        except ValueError as exc:
            return HTMLResponse(f"درخواست قابل پردازش نیست: {exc}", status_code=409)
        await audit_service.record(
            session, actor_user_id=admin.id, action="KHATM_CATEGORY_REQUEST_FULFILL",
            target_user_id=req.requested_by_user_id,
            details={"request_id": str(req.id), "category_id": str(category.id), "title": category.title},
        )
        identities = await identity_service.list_identities_for_user(session, req.requested_by_user_id)
    try:
        notify = get_notify_fn()
    except RuntimeError:
        notify = None
    if notify is not None:
        for identity in identities:
            await notify(
                identity.platform.value, identity.subject,
                f"درخواست شما «{category.title}» به لیست دعاها اضافه شد ✅\nحالا می‌تونید ختمش رو بسازید.",
            )
    return RedirectResponse("/categories?saved=fulfilled", status_code=303)


# --- Devotional texts (dua / ziyarat) library ---------------------------------
# Owner request (2026-09-27): add/edit dua & ziyarat texts from a graphical
# admin page instead of code + git pull. Text is stored in `devotional_assets`
# (same rows the startup seed writes and the member bots deliver). The long
# body is chunked into <=~3500-char pieces joined by \x1e at save time, the
# same delimiter `portions._send_recitation_content` splits on.
_DEVOTIONAL_TYPE_LABELS = {"DUA": "دعا", "ZIYARAT": "زیارت"}
_DEVOTIONAL_CHUNK_LIMIT = 3500
_DEVOTIONAL_SEP = "\x1e"


def _chunk_devotional(text: str) -> str:
    paragraphs = [p.strip() for p in text.strip().replace("\r\n", "\n").split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > _DEVOTIONAL_CHUNK_LIMIT and current:
            chunks.append(current)
            current = para
        else:
            current = candidate
    if current:
        chunks.append(current)
    return _DEVOTIONAL_SEP.join(chunks)


@app.get("/devotionals", response_class=HTMLResponse)
async def devotionals_page(request: Request):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        assets = await content_service.list_all_devotional_assets(session)
    rows = []
    for a in assets:
        # Re-join chunks with blank lines for editing; the separator is a
        # storage detail the admin never needs to see.
        display_text = (a.text_body or "").replace(_DEVOTIONAL_SEP, "\n\n")
        rows.append({
            "slug": a.slug,
            "title": a.title,
            "content_type": a.content_type,
            "type_label": _DEVOTIONAL_TYPE_LABELS.get(a.content_type, a.content_type),
            "enabled": a.enabled,
            "text": display_text,
            "char_count": len(a.text_body or ""),
            "has_image": bool(a.image_ref),
            "has_audio": bool(a.audio_ref),
        })
    return templates.TemplateResponse(
        request=request,
        name="devotionals.html",
        context=_ctx(
            request, admin, raw, items=rows,
            type_labels=_DEVOTIONAL_TYPE_LABELS,
            saved=request.query_params.get("saved", ""),
        ),
    )


@app.post("/devotionals/save")
async def save_devotional(
    request: Request,
    slug: str = Form(...),
    title: str = Form(...),
    content_type: str = Form(...),
    text_body: str = Form(...),
    csrf: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        try:
            asset = await content_service.register_devotional_text(
                session,
                content_type=content_type,
                slug=slug,
                title=title,
                text_body=_chunk_devotional(text_body),
            )
        except ValueError as exc:
            return HTMLResponse(f"ورودی نامعتبر: {exc}", status_code=400)
        await audit_service.record(
            session, actor_user_id=admin.id, action="DEVOTIONAL_TEXT_SAVE",
            details={"slug": asset.slug, "title": asset.title, "content_type": asset.content_type},
        )
    return RedirectResponse("/devotionals?saved=saved", status_code=303)


@app.post("/devotionals/{slug}/toggle")
async def toggle_devotional(request: Request, slug: str, csrf: str = Form(...)):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        current = await session.scalar(
            select(content_service.DevotionalAsset).where(
                content_service.DevotionalAsset.slug == slug.strip().lower()
            )
        )
        if current is None:
            return HTMLResponse("پیدا نشد.", status_code=404)
        asset = await content_service.set_devotional_enabled(session, slug, not current.enabled)
        await audit_service.record(
            session, actor_user_id=admin.id, action="DEVOTIONAL_TEXT_TOGGLE",
            details={"slug": asset.slug, "enabled": asset.enabled},
        )
    return RedirectResponse("/devotionals?saved=toggled", status_code=303)


@app.get("/templates", response_class=HTMLResponse)
async def message_templates(request: Request):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        items = list(
            (
                await session.execute(
                    select(MessageTemplate)
                    .order_by(
                        MessageTemplate.key.asc(),
                        MessageTemplate.locale.asc(),
                        MessageTemplate.version.desc(),
                    )
                    .limit(250)
                )
            ).scalars()
        )
    return templates.TemplateResponse(
        request=request,
        name="templates.html",
        context=_ctx(request, admin, raw, items=items),
    )


@app.get("/finance", response_class=HTMLResponse)
async def finance(request: Request):
    admin, raw = await _admin(request, AdminPermission.FINANCE_MANAGE)
    if admin is None:
        return _login_redirect()
    async with session_scope() as session:
        coupons = await wallet_service.list_coupons(session)
        invoice_rows = list(
            (
                await session.execute(
                    select(WalletInvoice, User)
                    .join(User, User.id == WalletInvoice.user_id)
                    .order_by(WalletInvoice.issued_at.desc())
                    .limit(30)
                )
            ).all()
        )
        paid_total = await session.scalar(
            select(func.coalesce(func.sum(WalletInvoice.net_amount_toman), 0)).where(
                WalletInvoice.status == "PAID"
            )
        )
        refunded_total = await session.scalar(
            select(func.coalesce(func.sum(WalletInvoice.net_amount_toman), 0)).where(
                WalletInvoice.status == "REFUNDED"
            )
        )
        plan_definitions = list(
            (await session.execute(select(PlanDefinition).order_by(PlanDefinition.plan))).scalars()
        )
        sms_plan_options = list(
            (await session.execute(select(SmsPlanOption).order_by(SmsPlanOption.months))).scalars()
        )
    return templates.TemplateResponse(
        request=request,
        name="finance.html",
        context=_ctx(
            request,
            admin,
            raw,
            coupons=coupons,
            invoice_rows=invoice_rows,
            paid_total=int(paid_total or 0),
            refunded_total=int(refunded_total or 0),
            plan_definitions=plan_definitions,
            sms_plan_options=sms_plan_options,
            saved=request.query_params.get("saved", ""),
        ),
    )


@app.post("/finance/plans/{plan_name}")
async def update_plan_definition(
    request: Request,
    plan_name: str,
    csrf: str = Form(...),
    title: str = Form(...),
    pricing_mode: str = Form(...),
    price_toman: int = Form(0),
    max_devotional_members: str = Form(""),
    max_quran_members: str = Form(""),
    khatm_create: str = Form(""),
    enabled: str = Form(""),
):
    admin, raw = await _admin(request, AdminPermission.FINANCE_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    try:
        plan = PlanTier(plan_name.upper())
        mode = PricingMode(pricing_mode.upper())
        clean_title = title.strip()
        if not clean_title or price_toman < 0:
            raise ValueError
        limits: dict[str, int] = {}
        for key, raw_value in (
            ("max_devotional_members", max_devotional_members),
            ("max_quran_members", max_quran_members),
        ):
            if raw_value.strip():
                value = int(raw_value)
                if value <= 0:
                    raise ValueError
                limits[key] = value
    except (TypeError, ValueError):
        return HTMLResponse("اطلاعات پلن معتبر نیست.", status_code=400)

    async with session_scope() as session:
        current = await plan_service.get_definition(session, plan)
        entitlements = dict(current.entitlements) if current else {}
        entitlements.pop("max_devotional_members", None)
        entitlements.pop("max_quran_members", None)
        entitlements.update(limits)
        entitlements["khatm.create"] = khatm_create == "on"
        definition = await plan_service.set_definition(
            session,
            plan=plan,
            title=clean_title,
            pricing_mode=mode,
            price_toman=price_toman if mode == PricingMode.FIXED else 0,
            unit_price_toman=price_toman if mode == PricingMode.USAGE_BASED else 0,
            entitlements=entitlements,
        )
        definition.enabled = enabled == "on"
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="PLAN_DEFINITION_UPDATE",
            details={
                "plan": plan.value,
                "pricing_mode": mode.value,
                "price_toman": price_toman,
                "enabled": definition.enabled,
                "entitlements": entitlements,
            },
        )
    return RedirectResponse("/finance?saved=plan", status_code=303)


@app.post("/finance/sms-plans")
async def update_sms_plan_option(
    request: Request,
    csrf: str = Form(...),
    months: int = Form(...),
    price_toman: int = Form(...),
    enabled: str = Form(""),
):
    admin, raw = await _admin(request, AdminPermission.FINANCE_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    try:
        option = None
        async with session_scope() as session:
            option = await sms_subscription_service.set_option(
                session,
                months=months,
                price_toman=price_toman,
                enabled=enabled == "on",
            )
            await audit_service.record(
                session,
                actor_user_id=admin.id,
                action="SMS_PLAN_OPTION_UPDATE",
                details={
                    "months": option.months,
                    "price_toman": option.price_toman,
                    "enabled": option.enabled,
                },
            )
    except ValueError:
        return HTMLResponse("مدت یا قیمت اشتراک پیامک معتبر نیست.", status_code=400)
    return RedirectResponse("/finance?saved=sms", status_code=303)


@app.post("/finance/coupons")
async def create_coupon(
    request: Request,
    csrf: str = Form(...),
    code: str = Form(...),
    discount_type: str = Form(...),
    value: int = Form(...),
    min_purchase_toman: int = Form(0),
    total_redemption_limit: str = Form(""),
    per_user_limit: int = Form(1),
    max_discount_toman: str = Form(""),
):
    admin, raw = await _admin(request, AdminPermission.FINANCE_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    try:
        kind = CouponDiscountType(discount_type.upper())
        total_limit = int(total_redemption_limit) if total_redemption_limit.strip() else None
        max_discount = int(max_discount_toman) if max_discount_toman.strip() else None
        async with session_scope() as session:
            coupon = await wallet_service.set_coupon(
                session,
                code=code,
                discount_type=kind,
                value=value,
                min_purchase_toman=min_purchase_toman,
                max_discount_toman=max_discount,
                total_redemption_limit=total_limit,
                per_user_limit=per_user_limit,
                created_by_user_id=admin.id,
            )
            await audit_service.record(
                session,
                actor_user_id=admin.id,
                action="WEB_COUPON_SET",
                details={"code": coupon.code, "type": coupon.discount_type, "value": coupon.value},
            )
    except (ValueError, TypeError):
        return HTMLResponse("اطلاعات کد تخفیف معتبر نیست.", status_code=400)
    return RedirectResponse("/finance?saved=1", status_code=303)


@app.post("/finance/coupons/{code}/toggle")
async def toggle_coupon(request: Request, code: str, csrf: str = Form(...)):
    admin, raw = await _admin(request, AdminPermission.FINANCE_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        coupons = await wallet_service.list_coupons(session)
        current = next((item for item in coupons if item.code == code.upper()), None)
        if current is None:
            return HTMLResponse("کد پیدا نشد.", status_code=404)
        updated = await wallet_service.set_coupon_enabled(session, current.code, not current.enabled)
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="WEB_COUPON_TOGGLE",
            details={"code": updated.code, "enabled": updated.enabled},
        )
    return RedirectResponse("/finance", status_code=303)


@app.post("/templates/{template_id}/toggle")
async def toggle_template(
    request: Request, template_id: UUID, csrf: str = Form(...)
):
    admin, raw = await _admin(request, AdminPermission.CONTENT_MANAGE)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)
    async with session_scope() as session:
        item = await session.get(MessageTemplate, template_id)
        if item is None:
            return HTMLResponse("قالب پیدا نشد.", status_code=404)
        item = await template_repository.set_enabled(
            session, item.key, item.locale, item.version, not item.enabled
        )
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="WEB_MESSAGE_TEMPLATE_TOGGLE",
            details={
                "key": item.key,
                "locale": item.locale,
                "version": item.version,
                "enabled": item.enabled,
            },
        )
    return RedirectResponse("/templates", status_code=303)


# ---------------------------------------------------------------------------
# Bot token management
# ---------------------------------------------------------------------------

@app.get("/bots", response_class=HTMLResponse)
async def bots_page(request: Request, platform: str = "TELEGRAM"):
    admin, raw = await _admin(request, AdminPermission.OPERATIONS_VIEW)
    if admin is None:
        return _login_redirect()
    if platform not in ("TELEGRAM", "BALE"):
        platform = "TELEGRAM"
    async with session_scope() as session:
        all_bots = await bot_registry_service.list_all_instances(session)
    filtered = [b for b in all_bots if b.platform == platform]
    needs_restart = any(
        b.updated_at and b.updated_at > runtime_status.process_started_at()
        for b in all_bots
        if b.bot_role == "MEMBER"
    )
    return templates.TemplateResponse(
        request=request,
        name="bot_tokens.html",
        context=_ctx(
            request,
            admin,
            raw,
            bots=filtered,
            platform=platform,
            needs_restart=needs_restart,
            saved=request.query_params.get("saved", ""),
            error=request.query_params.get("error", ""),
        ),
    )


@app.post("/bots/{instance_id}/token")
async def save_bot_token(
    request: Request,
    instance_id: UUID,
    csrf: str = Form(...),
    token: str = Form(""),
    username: str = Form(""),
    confirm_name: str = Form(""),
):
    admin, raw = await _admin(request, AdminPermission.OPERATIONS_VIEW)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)

    async with session_scope() as session:
        instance = await bot_registry_service.get_instance(session, instance_id)
        if instance is None:
            return HTMLResponse("بات پیدا نشد.", status_code=404)
        if instance.bot_role == "CREATOR":
            return RedirectResponse(
                f"/bots?platform={instance.platform}&error=توکن+بات+سازنده+از+env.+بارگذاری+می‌شود",
                status_code=303,
            )
        if confirm_name.strip() != instance.display_name.strip():
            return RedirectResponse(
                f"/bots?platform={instance.platform}&error=نام+تایید+با+نام+نمایشی+بات+مطابقت+ندارد",
                status_code=303,
            )
        await bot_registry_service.set_bot_token(
            session, instance_id, token.strip(), username.strip(),
        )
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="BOT_TOKEN_CHANGED",
            details={"instance_id": str(instance_id), "display_name": instance.display_name},
        )
    return RedirectResponse(
        f"/bots?platform={instance.platform}&saved=1", status_code=303,
    )


@app.post("/bots/{instance_id}/toggle")
async def toggle_bot(
    request: Request,
    instance_id: UUID,
    csrf: str = Form(...),
):
    admin, raw = await _admin(request, AdminPermission.OPERATIONS_VIEW)
    if admin is None:
        return _login_redirect()
    if not _valid_csrf(raw, csrf):
        return HTMLResponse("درخواست امنیتی نامعتبر است.", status_code=403)

    async with session_scope() as session:
        instance = await bot_registry_service.get_instance(session, instance_id)
        if instance is None:
            return HTMLResponse("بات پیدا نشد.", status_code=404)
        await bot_registry_service.toggle_bot_active(
            session, instance_id, not instance.is_active,
        )
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="BOT_ACTIVE_TOGGLED",
            details={
                "instance_id": str(instance_id),
                "display_name": instance.display_name,
                "is_active": not instance.is_active,
            },
        )
    return RedirectResponse(
        f"/bots?platform={instance.platform}&saved=1", status_code=303,
    )
