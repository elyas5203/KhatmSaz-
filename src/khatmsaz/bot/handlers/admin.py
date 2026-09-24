"""Permission-gated admin commands and secure dashboard entry.

The first Super Admin is bootstrapped from configuration (DEC-PY-0013), then
may delegate narrowly scoped roles. A non-admin typing these commands sees
the same "unknown command" experience as anyone else — the existence of
admin commands isn't hidden, but they silently no-op for non-admins rather
than leaking who's an admin via a different error message.

Targeting a user for moderation is still by platform chat id, but
`/admin_user_search` can now locate a canonical user by name, phone, platform
subject, or UUID. A full web admin panel and cross-platform moderation UX remain
future work.
"""

from html import escape
from uuid import UUID

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, MessageOriginChannel, WebAppInfo
from sqlalchemy.exc import IntegrityError

from khatmsaz.core.db import session_scope
from khatmsaz.config import get_settings
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.authorization.models import AdminPermission, AdminRole
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.message_template import repository as template_repository
from khatmsaz.modules.message_template import service as template_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import CouponDiscountType
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanTier, PricingMode
from khatmsaz.modules.sms_subscription import service as sms_subscription_service
from khatmsaz.modules.advertising import service as advertising_service
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import QuranAssetKind
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.system_settings import service as system_settings_service

router = Router(name="admin")


@router.message(Command("admin_app", "admin_web_login"))
async def admin_web_login(message: Message) -> None:
    """Open the signed Telegram Mini App for an authorized administrator."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform):
        return
    base_url = get_settings().admin_web_base_url.rstrip("/")
    if not base_url.lower().startswith("https://"):
        await message.answer(
            "مینی‌اپ هنوز روی آدرس امن HTTPS فعال نشده است. بعد از اتصال "
            "app.khatmsaz.com به سرور، دوباره همین دستور را بفرستید."
        )
        return
    if platform != Platform.TELEGRAM:
        await message.answer("مینی‌اپ بله پس از تأیید رسمی روش احراز هویت بله فعال می‌شود؛ ورود ناامن ارائه نمی‌شود.")
        return
    login_url = f"{base_url}/mini/admin"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="باز کردن مینی‌اپ مدیریت", web_app=WebAppInfo(url=login_url))]]
    )
    await message.answer(
        "برای ورود امن، مینی‌اپ مدیریت را از همین دکمه باز کنید.",
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "admin:web_login")
async def admin_web_login_button(callback) -> None:
    await admin_web_login(callback.message)
    await callback.answer()


@router.message(Command("admin_covers"))
async def admin_covers(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MODERATION_MANAGE):
        return
    async with session_scope() as session:
        covers = await khatm_service.list_pending_covers(session)
    if not covers:
        await message.answer("کاور در انتظار بررسی وجود ندارد.")
        return
    lines = ["کاورهای در انتظار بررسی:"]
    for khatm in covers:
        lines.append(f"— {khatm.title} | {khatm.id} | {khatm.cover_platform}")
    await message.answer("\n".join(lines))


@router.message(Command("admin_review_cover"))
async def admin_review_cover(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MODERATION_MANAGE):
        return
    parts = (command.args or "").strip().split(maxsplit=2)
    if len(parts) < 2 or parts[1].lower() not in {"approve", "reject"}:
        await message.answer("فرمت درست: /admin_review_cover <khatm_id> <approve|reject> [یادداشت]")
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer("شناسه ختم معتبر نیست.")
        return
    approved = parts[1].lower() == "approve"
    note = parts[2] if len(parts) == 3 else None
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        try:
            khatm = await khatm_service.review_cover(session, khatm_id=khatm_id, approved=approved, note=note)
        except ValueError:
            await message.answer("کاور پیدا نشد یا در صف بررسی نیست.")
            return
        await audit_service.record(
            session, actor_user_id=admin.id, target_khatm_id=khatm.id,
            action="KHATM_COVER_REVIEW", details={"approved": approved, "note": note},
        )
    await message.answer(f"کاور «{escape(khatm.title)}» {'تأیید' if approved else 'رد'} شد ✅")


async def _require_admin(
    message: Message,
    platform: Platform,
    permission: AdminPermission = AdminPermission.DASHBOARD_ACCESS,
) -> bool:
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        return await authorization_service.has_permission(session, user, permission)


@router.message(Command("admin_quran_asset"))
async def admin_quran_asset_help(message: Message, command: CommandObject) -> None:
    """Explain the media-upload caption format when no media is attached."""
    if (command.args or "").strip():
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    await message.answer(
        "برای ثبت رسانه، عکس یا فایل صوتی را با caption زیر بفرستید:\n"
        "/admin_quran_asset IMAGE ‹page›\n"
        "/admin_quran_asset AUDIO ‹page› ‹reciter›\n"
        "قاری‌ها: minshawi، abdulbasit، husary"
    )


@router.message(F.caption.startswith("/admin_quran_asset"))
async def admin_quran_asset_upload(message: Message) -> None:
    """Register a Telegram/Bale file id as a canonical Quran page asset."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    parts = (message.caption or "").strip().split()
    if len(parts) not in (3, 4):
        await message.answer("فرمت caption درست نیست. برای راهنما /admin_quran_asset را بفرستید.")
        return
    try:
        kind = QuranAssetKind(parts[1].upper())
        page = int(parts[2])
    except (TypeError, ValueError):
        await message.answer("نوع asset باید IMAGE یا AUDIO و شماره صفحه باید عدد ۱ تا ۶۰۴ باشد.")
        return
    reciter = parts[3] if len(parts) == 4 else ""
    if kind == QuranAssetKind.AUDIO and len(parts) != 4:
        await message.answer("برای AUDIO باید قاری را هم بنویسید: AUDIO <page> <reciter>")
        return
    if kind != QuranAssetKind.AUDIO and len(parts) == 4:
        await message.answer("برای IMAGE فقط نوع و شماره صفحه را بنویسید.")
        return
    asset_ref = None
    if kind == QuranAssetKind.IMAGE and message.photo:
        asset_ref = message.photo[-1].file_id
    elif kind == QuranAssetKind.AUDIO and message.audio:
        asset_ref = message.audio.file_id
    elif message.document:
        asset_ref = message.document.file_id
    if not asset_ref:
        await message.answer("برای این دستور باید عکس، صوت یا فایل ضمیمه کنید.")
        return
    try:
        async with session_scope() as session:
            admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
            asset = await content_service.register_quran_page_asset(
                session, edition_id=content_service.CANONICAL_EDITION_ID,
                page_number=page, kind=kind, reciter_id=reciter,
                asset_ref=asset_ref, asset_platform=platform.value,
            )
            await audit_service.record(
                session, actor_user_id=admin.id, action="QURAN_ASSET_REGISTER",
                details={"page": page, "kind": kind.value, "platform": platform.value,
                         "asset_id": str(asset.id), "reciter_id": asset.reciter_id},
            )
    except ValueError as exc:
        await message.answer(str(exc))
        return
    except IntegrityError:
        await message.answer("این asset برای همین صفحه، نوع، قاری و پلتفرم قبلاً ثبت شده است.")
        return
    await message.answer(f"asset {kind.value} صفحه {page} برای {platform.value} ثبت شد ✅")


def _short_missing(pages: list[int]) -> str:
    if not pages:
        return "هیچ‌کدام"
    shown = "، ".join(str(page) for page in pages[:20])
    return shown + (f" و {len(pages) - 20} صفحهٔ دیگر" if len(pages) > 20 else "")


@router.message(Command("admin_quran_source_status"))
async def admin_quran_source_status(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    async with session_scope() as session:
        coverage = await content_service.quran_channel_coverage(session)
    live_access = False
    if platform == Platform.TELEGRAM:
        try:
            await message.bot.get_chat(get_settings().quran_source_telegram_chat_id)
            live_access = True
        except TelegramAPIError:
            # A private channel is reported as "chat not found" until the bot
            # has been added. Keep the provider detail out of user-facing copy.
            live_access = False
    await message.answer(
        "وضعیت کتابخانهٔ کانال قرآن (نسخهٔ ۶۰۴ صفحه‌ای)\n\n"
        f"تصویر: {coverage['image_count']} از ۶۰۴ صفحه\n"
        f"صوت پرهیزگار: {coverage['audio_count']} از ۶۰۴ صفحه\n"
        f"تصویرهای ثبت‌نشده: {_short_missing(coverage['missing_images'])}\n"
        f"صوت‌های ثبت‌نشده: {_short_missing(coverage['missing_audio'])}\n\n"
        + ("✅ نگاشت همهٔ صفحه‌ها آماده است.\n" if coverage["ready"] else "⏳ هنوز نگاشت کتابخانه کامل نشده است.\n")
        + (
            "✅ دسترسی زندهٔ بات به کانال برقرار است؛ ارسال واقعی ممکن است."
            if live_access
            else "❌ بات هنوز به کانال خصوصی دسترسی ندارد. بات @Khatm_Saz_bot را به کانال اضافه کنید، "
                 "سپس همین گزارش را دوباره بگیرید."
        )
    )


@router.message(Command("admin_quran_source_seed"))
async def admin_quran_source_seed(message: Message) -> None:
    """Load the audited 604-page map bundled with this release."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        coverage = await content_service.seed_verified_quran_channel_map(session)
        await audit_service.record(
            session, actor_user_id=admin.id, action="QURAN_CHANNEL_SEED",
            details={"image_count": coverage["image_count"], "audio_count": coverage["audio_count"]},
        )
    await message.answer(
        "✅ نگاشت تأییدشدهٔ کانال بارگذاری شد.\n"
        f"تصویر: {coverage['image_count']} از ۶۰۴\n"
        f"صوت: {coverage['audio_count']} از ۶۰۴"
    )


@router.message(F.forward_origin)
async def admin_quran_source_forward(message: Message) -> None:
    """Import a forwarded canonical-channel post by reading its Persian caption."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if platform != Platform.TELEGRAM or not await _require_admin(
        message, platform, AdminPermission.CONTENT_MANAGE
    ):
        return
    origin = message.forward_origin
    if not isinstance(origin, MessageOriginChannel):
        return
    expected_chat_id = get_settings().quran_source_telegram_chat_id
    if expected_chat_id and origin.chat.id != expected_chat_id:
        await message.answer("این پیام از کانال قرآن تعیین‌شده نیامده و ثبت نشد.")
        return
    parsed = content_service.parse_quran_channel_caption(message.caption or message.text)
    if parsed is None:
        await message.answer("این پیام عنوان صفحه/صوت قابل تشخیص ندارد؛ احتمالاً عنوان جزء یا پیام توضیحی است و ثبت نشد.")
        return
    kind, page_start, page_end = parsed
    if kind == QuranAssetKind.IMAGE and not (message.photo or message.document):
        await message.answer("عنوان صفحه پیدا شد، اما خود پیام تصویر ندارد؛ ثبت نشد.")
        return
    if kind == QuranAssetKind.AUDIO and not (message.audio or message.voice or message.document):
        await message.answer("عنوان صوت پیدا شد، اما خود پیام فایل صوتی ندارد؛ ثبت نشد.")
        return
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        rows = await content_service.register_telegram_channel_asset_range(
            session, source_chat_id=origin.chat.id, source_message_id=origin.message_id,
            page_start=page_start, page_end=page_end, kind=kind, reciter_id="parhizgar",
        )
        await audit_service.record(
            session, actor_user_id=admin.id, action="QURAN_CHANNEL_POST_REGISTER",
            details={
                "source_chat_id": origin.chat.id, "source_message_id": origin.message_id,
                "page_start": page_start, "page_end": page_end, "kind": kind.value,
                "asset_ids": [str(row.id) for row in rows],
            },
        )
    label = "تصویر" if kind == QuranAssetKind.IMAGE else "صوت پرهیزگار"
    await message.answer(f"✅ {label} صفحه‌های {page_start} تا {page_end} ثبت شد.")


@router.message(Command("admin_devotional_text"))
async def admin_devotional_text(message: Message, command: CommandObject) -> None:
    """Upsert complete dua/ziyarat text: TYPE SLUG TITLE | BODY."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    raw = (command.args or "").strip()
    if "|" not in raw:
        await message.answer("فرمت درست: /admin_devotional_text DUA slug عنوان | متن کامل")
        return
    header, body = [part.strip() for part in raw.split("|", 1)]
    parts = header.split(maxsplit=2)
    if len(parts) != 3 or not body:
        await message.answer("فرمت درست: /admin_devotional_text DUA slug عنوان | متن کامل")
        return
    try:
        async with session_scope() as session:
            admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
            asset = await content_service.register_devotional_text(
                session, content_type=parts[0], slug=parts[1], title=parts[2], text_body=body,
            )
            await audit_service.record(
                session, actor_user_id=admin.id, action="DEVOTIONAL_TEXT_UPSERT",
                details={"asset_id": str(asset.id), "slug": asset.slug, "type": asset.content_type},
            )
    except ValueError as exc:
        await message.answer(str(exc))
        return
    await message.answer(f"متن کامل «{escape(asset.title)}» در کتابخانه ذخیره شد ✅\nslug: {asset.slug}")


@router.message(F.caption.startswith("/admin_devotional_audio"))
async def admin_devotional_audio_upload(message: Message) -> None:
    """Attach an audio file to a devotional asset by slug — a slug can
    now have MULTIPLE reciters (owner request, 2026-09-22): add an
    optional third caption word naming the reciter/variant; omit it for
    the plain "only reciter" slot. Accepts a voice note, an audio file,
    or a document (a Telegram "voice message", `message.voice`, is a
    different field from `message.audio` — previously only the latter
    two were accepted, so recording a quick voice note silently failed)."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    parts = (message.caption or "").strip().split(maxsplit=2)
    if len(parts) not in (2, 3):
        await message.answer("فرمت caption درست: /admin_devotional_audio slug [نام قاری]\nمثال: /admin_devotional_audio ziyarat-ashura محمودی")
        return
    reciter_label = parts[2] if len(parts) == 3 else None
    reciter_id = reciter_label.strip().lower() if reciter_label else ""
    asset_ref = (
        message.voice.file_id if message.voice
        else message.audio.file_id if message.audio
        else message.document.file_id if message.document
        else None
    )
    if not asset_ref:
        await message.answer("باید یک ویس، فایل صوتی، یا document ضمیمه کنید.")
        return
    try:
        async with session_scope() as session:
            admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
            media = await content_service.add_devotional_audio_variant(
                session, slug=parts[1], asset_ref=asset_ref, asset_platform=platform.value,
                reciter_id=reciter_id, reciter_label=reciter_label,
            )
            await audit_service.record(
                session, actor_user_id=admin.id, action="DEVOTIONAL_AUDIO_REGISTER",
                details={"media_id": str(media.id), "slug": parts[1], "reciter_id": reciter_id, "platform": platform.value},
            )
    except ValueError as exc:
        await message.answer(str(exc))
        return
    label = f" (قاری: {escape(reciter_label)})" if reciter_label else ""
    await message.answer(f"صوت «{escape(parts[1])}»{label} برای {platform.value} ثبت شد ✅")


@router.message(F.caption.startswith("/admin_devotional_image"))
async def admin_devotional_image_upload(message: Message) -> None:
    """Attach an image (e.g. a photo of the Ziyarat Ashura text) to a
    devotional asset by slug. Owner request (2026-09-22): a dua's text
    can span more than one page — add an optional third caption word
    with the page number (1, 2, 3, ...); omit it to auto-append after
    the last page already registered."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    parts = (message.caption or "").strip().split(maxsplit=2)
    if len(parts) not in (2, 3) or (len(parts) == 3 and not parts[2].isdigit()):
        await message.answer("فرمت caption درست: /admin_devotional_image slug [شماره صفحه]\nمثال: /admin_devotional_image dua-ahd 2")
        return
    page_number = int(parts[2]) if len(parts) == 3 else None
    asset_ref = (
        message.photo[-1].file_id if message.photo
        else message.document.file_id if message.document
        else None
    )
    if not asset_ref:
        await message.answer("باید یک عکس یا document ضمیمه کنید.")
        return
    try:
        async with session_scope() as session:
            admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
            media = await content_service.add_devotional_image_page(
                session, slug=parts[1], asset_ref=asset_ref, asset_platform=platform.value, page_number=page_number,
            )
            await audit_service.record(
                session, actor_user_id=admin.id, action="DEVOTIONAL_IMAGE_REGISTER",
                details={"media_id": str(media.id), "slug": parts[1], "page": media.page_number, "platform": platform.value},
            )
    except ValueError as exc:
        await message.answer(str(exc))
        return
    await message.answer(f"تصویر «{escape(parts[1])}» — صفحهٔ {media.page_number} — برای {platform.value} ثبت شد ✅")


@router.message(F.caption.startswith("/admin_devotional_pdf"))
async def admin_devotional_pdf_upload(message: Message) -> None:
    """Attach a PDF of the full dua text to a devotional asset by slug.
    Owner request (2026-09-22)."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    parts = (message.caption or "").strip().split()
    if len(parts) != 2:
        await message.answer("فرمت caption درست: /admin_devotional_pdf slug")
        return
    asset_ref = message.document.file_id if message.document else None
    if not asset_ref:
        await message.answer("باید یک فایل PDF (به‌صورت document) ضمیمه کنید.")
        return
    try:
        async with session_scope() as session:
            admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
            media = await content_service.set_devotional_pdf(
                session, slug=parts[1], asset_ref=asset_ref, asset_platform=platform.value,
            )
            await audit_service.record(
                session, actor_user_id=admin.id, action="DEVOTIONAL_PDF_REGISTER",
                details={"media_id": str(media.id), "slug": parts[1], "platform": platform.value},
            )
    except ValueError as exc:
        await message.answer(str(exc))
        return
    await message.answer(f"PDF «{escape(parts[1])}» برای {platform.value} ثبت شد ✅")


def _parse_target_and_rest(command: CommandObject) -> tuple[str, str] | None:
    """Splits "<chat_id> <rest...>" — returns (chat_id, rest) or None if the
    chat id isn't a plain integer."""
    args = (command.args or "").strip()
    if not args:
        return None
    parts = args.split(maxsplit=1)
    target_chat_id = parts[0]
    if not target_chat_id.lstrip("-").isdigit():
        return None
    rest = parts[1] if len(parts) > 1 else ""
    return target_chat_id, rest


@router.message(Command("admin_warn"))
async def admin_warn(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MODERATION_MANAGE):
        return

    parsed = _parse_target_and_rest(command)
    if parsed is None:
        await message.answer("فرمت درست: /admin_warn <chat_id>")
        return
    target_chat_id, _ = parsed

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        target = await identity_service.find_by_platform(session, platform, target_chat_id)
        if target is None:
            await message.answer("این کاربر پیدا نشد.")
            return
        await identity_service.warn(session, target.id)
        await audit_service.record(session, actor_user_id=admin.id, action="USER_WARN", target_user_id=target.id, details={"platform": platform.value})
    await message.answer(f"کاربر {target_chat_id} اخطار گرفت.")


@router.message(Command("admin_suspend"))
async def admin_suspend(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MODERATION_MANAGE):
        return

    parsed = _parse_target_and_rest(command)
    if parsed is None:
        await message.answer("فرمت درست: /admin_suspend <chat_id>")
        return
    target_chat_id, _ = parsed

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        target = await identity_service.find_by_platform(session, platform, target_chat_id)
        if target is None:
            await message.answer("این کاربر پیدا نشد.")
            return
        await identity_service.suspend(session, target.id)
        await audit_service.record(session, actor_user_id=admin.id, action="USER_SUSPEND", target_user_id=target.id, details={"platform": platform.value})
    await message.answer(f"کاربر {target_chat_id} موقتاً مسدود شد.")


@router.message(Command("admin_ban"))
async def admin_ban(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MODERATION_MANAGE):
        return

    parsed = _parse_target_and_rest(command)
    if parsed is None:
        await message.answer("فرمت درست: /admin_ban <chat_id>")
        return
    target_chat_id, _ = parsed

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        target = await identity_service.find_by_platform(session, platform, target_chat_id)
        if target is None:
            await message.answer("این کاربر پیدا نشد.")
            return
        await identity_service.ban(session, target.id)
        await audit_service.record(session, actor_user_id=admin.id, action="USER_BAN", target_user_id=target.id, details={"platform": platform.value})
    await message.answer(f"کاربر {target_chat_id} مسدود شد.")


@router.message(Command("admin_activate"))
async def admin_activate(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MODERATION_MANAGE):
        return

    parsed = _parse_target_and_rest(command)
    if parsed is None:
        await message.answer("فرمت درست: /admin_activate <chat_id>")
        return
    target_chat_id, _ = parsed

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        target = await identity_service.find_by_platform(session, platform, target_chat_id)
        if target is None:
            await message.answer("این کاربر پیدا نشد.")
            return
        await identity_service.reactivate(session, target.id)
        await audit_service.record(session, actor_user_id=admin.id, action="USER_REACTIVATE", target_user_id=target.id, details={"platform": platform.value})
    await message.answer(f"وضعیت کاربر {target_chat_id} به فعال برگشت.")


@router.message(Command("admin_grant_credit"))
async def admin_grant_credit(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.FINANCE_MANAGE):
        return

    parsed = _parse_target_and_rest(command)
    if parsed is None:
        await message.answer("فرمت درست: /admin_grant_credit <chat_id> <مبلغ> <دلیل>")
        return
    target_chat_id, rest = parsed
    rest_parts = rest.split(maxsplit=1)
    if not rest_parts or not rest_parts[0].isdigit():
        await message.answer("فرمت درست: /admin_grant_credit <chat_id> <مبلغ> <دلیل>")
        return
    amount = int(rest_parts[0])
    reason = rest_parts[1] if len(rest_parts) > 1 else "اعتبار اهدایی ادمین"

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        target = await identity_service.find_by_platform(session, platform, target_chat_id)
        if target is None:
            await message.answer("این کاربر پیدا نشد.")
            return
        await wallet_service.grant_reward_credit(session, target.id, amount, description=reason)
        await audit_service.record(session, actor_user_id=admin.id, action="CREDIT_GRANT", target_user_id=target.id, details={"amount": amount, "reason": reason})
    await message.answer(f"{amount:,} تومان اعتبار به کاربر {target_chat_id} اضافه شد.")


@router.message(Command("admin_user_search"))
async def admin_user_search(message: Message, command: CommandObject) -> None:
    """Search users by display name, phone, platform subject, or UUID."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.SUPPORT_USERS):
        return
    query = (command.args or "").strip()
    if not query:
        await message.answer("فرمت درست: /admin_user_search <نام، شماره، chat_id یا user_id>")
        return

    async with session_scope() as session:
        users = await identity_service.search_users(session, query, limit=10)
        if not users:
            await message.answer("کاربری با این مشخصات پیدا نشد.")
            return
        lines = [f"نتیجه جست‌وجو برای «{query}» ({len(users)} مورد):"]
        for user in users:
            settings = await settings_service.get_or_create(session, user.id)
            identities = await identity_service.list_identities_for_user(session, user.id)
            subjects = ", ".join(f"{item.platform.value}:{item.subject}" for item in identities)
            lines.append(
                f"\n👤 {user.display_name or 'بدون نام'}\n"
                f"شناسه: {user.id}\nوضعیت: {user.status.value} | نقش: {user.role.value}\n"
                f"تماس: {settings.contact_phone or 'ثبت نشده'}\n"
                f"حساب‌ها: {subjects or 'ثبت نشده'}"
            )
    await message.answer("\n".join(lines))


@router.message(Command("admin_plans"))
async def admin_plans(message: Message) -> None:
    """List admin-managed plan definitions."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.FINANCE_MANAGE):
        return
    async with session_scope() as session:
        lines = ["پلن‌ها:"]
        for plan in PlanTier:
            definition = await plan_service.get_definition(session, plan)
            if definition is None:
                lines.append(f"— {plan.value}: تعریف نشده")
                continue
            enabled = ", ".join(k for k, value in definition.entitlements.items() if value) or "بدون قابلیت"
            price = definition.price_toman if definition.pricing_mode == PricingMode.FIXED.value else definition.unit_price_toman
            lines.append(f"— {plan.value} | {definition.title} | {definition.pricing_mode} | {price:,} | {enabled}")
    await message.answer("\n".join(lines))


@router.message(Command("admin_ad_rate"))
async def admin_ad_rate(message: Message, command: CommandObject) -> None:
    """Append a new reward-credit rate for eligible advertising members."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MARKETING_MANAGE):
        return
    raw = (command.args or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer("فرمت درست: /admin_ad_rate [مبلغ مثبت به تومان]")
        return
    amount = int(raw)
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        rate = await advertising_service.set_reward_rate(session, amount)
        await audit_service.record(
            session, actor_user_id=admin.id, action="AD_REWARD_RATE_UPDATE",
            details={"amount_toman": amount, "rate_id": str(rate.id)},
        )
    await message.answer(f"نرخ پاداش تبلیغات روی {amount:,} تومان تنظیم شد ✅")


@router.message(Command("admin_settings"))
async def admin_settings_list(message: Message) -> None:
    """List all admin-editable system-wide numeric defaults (owner
    request, 2026-09-21: "همه چیز داینامیک باشه") — see
    `system_settings/service.py::KNOWN_SETTINGS`."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.ADMIN_ROLES_MANAGE):
        return
    async with session_scope() as session:
        current = await system_settings_service.list_current(session)
    lines = ["⚙️ تنظیمات سراسری فعلی:"]
    for key, value in current.items():
        label = system_settings_service.KNOWN_SETTINGS[key]["label_fa"]
        lines.append(f"— {key} = {value}\n  {label}")
    lines.append("\nبرای تغییر: /admin_setting_set <کلید> <عدد>")
    await message.answer("\n".join(lines))


@router.message(Command("admin_setting_set"))
async def admin_setting_set(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.ADMIN_ROLES_MANAGE):
        return
    parts = (command.args or "").strip().split()
    if len(parts) != 2 or not parts[1].lstrip("-").isdigit():
        keys = "، ".join(system_settings_service.KNOWN_SETTINGS.keys())
        await message.answer(f"فرمت درست: /admin_setting_set <کلید> <عدد>\nکلیدهای معتبر: {keys}")
        return
    key, raw_value = parts
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        try:
            await system_settings_service.set_int(session, key, int(raw_value))
        except ValueError as exc:
            await message.answer(f"مقدار قابل ذخیره نیست: {exc}")
            return
        await audit_service.record(
            session, actor_user_id=admin.id, action="SYSTEM_SETTING_UPDATE",
            details={"key": key, "value": raw_value},
        )
    await message.answer(f"«{key}» روی {raw_value} تنظیم شد ✅")


@router.message(Command("admin_coupons"))
async def admin_coupons(message: Message) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.FINANCE_MANAGE):
        return
    async with session_scope() as session:
        coupons = await wallet_service.list_coupons(session)
    if not coupons:
        await message.answer("هنوز کد تخفیفی ساخته نشده است.")
        return
    lines = ["کدهای تخفیف:"]
    for coupon in coupons:
        value = (
            f"{coupon.value}%"
            if coupon.discount_type == CouponDiscountType.PERCENT.value
            else f"{coupon.value:,} تومان"
        )
        lines.append(
            f"— {coupon.code} | {value} | حداقل {coupon.min_purchase_toman:,} | "
            f"هر کاربر {coupon.per_user_limit} بار | {'فعال' if coupon.enabled else 'غیرفعال'}"
        )
    await message.answer("\n".join(lines))


@router.message(Command("admin_coupon_set"))
async def admin_coupon_set(message: Message, command: CommandObject) -> None:
    """Create/update: CODE percent|fixed VALUE MIN TOTAL|none USER [MAX|none]."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.FINANCE_MANAGE):
        return
    parts = (command.args or "").strip().split()
    if len(parts) not in {6, 7}:
        await message.answer(
            "فرمت: /admin_coupon_set CODE percent|fixed مقدار حداقل_خرید سقف_کل|none سقف_هرکاربر [حداکثر_تخفیف|none]"
        )
        return
    code, kind_text, value_text, minimum_text, total_text, per_user_text = parts[:6]
    max_text = parts[6] if len(parts) == 7 else "none"
    try:
        kind = {
            "percent": CouponDiscountType.PERCENT,
            "fixed": CouponDiscountType.FIXED,
        }[kind_text.lower()]
        value = int(value_text)
        minimum = int(minimum_text)
        total_limit = None if total_text.lower() == "none" else int(total_text)
        per_user = int(per_user_text)
        max_discount = None if max_text.lower() == "none" else int(max_text)
    except (KeyError, ValueError):
        await message.answer("نوع یا عددهای کد تخفیف معتبر نیستند.")
        return
    try:
        async with session_scope() as session:
            admin = await identity_service.find_by_platform(
                session, platform, str(message.chat.id)
            )
            coupon = await wallet_service.set_coupon(
                session,
                code=code,
                discount_type=kind,
                value=value,
                min_purchase_toman=minimum,
                max_discount_toman=max_discount,
                total_redemption_limit=total_limit,
                per_user_limit=per_user,
                created_by_user_id=admin.id,
            )
            await audit_service.record(
                session,
                actor_user_id=admin.id,
                action="COUPON_SET",
                details={
                    "code": coupon.code,
                    "type": coupon.discount_type,
                    "value": coupon.value,
                },
            )
    except ValueError as exc:
        await message.answer(f"کد تخفیف ساخته نشد: {exc}")
        return
    await message.answer(f"کد {coupon.code} ذخیره و فعال شد ✅")


@router.message(Command("admin_coupon_toggle"))
async def admin_coupon_toggle(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.FINANCE_MANAGE):
        return
    parts = (command.args or "").strip().split()
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        await message.answer("فرمت: /admin_coupon_toggle CODE on|off")
        return
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        coupon = await wallet_service.set_coupon_enabled(
            session, parts[0], parts[1].lower() == "on"
        )
        if coupon is None:
            await message.answer("این کد پیدا نشد.")
            return
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="COUPON_TOGGLE",
            details={"code": coupon.code, "enabled": coupon.enabled},
        )
    await message.answer(f"کد {coupon.code} {'فعال' if coupon.enabled else 'غیرفعال'} شد.")


@router.message(Command("admin_plan_set"))
async def admin_plan_set(message: Message, command: CommandObject) -> None:
    """Set a plan's pricing mode, price, and comma-separated entitlements."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.FINANCE_MANAGE):
        return
    parts = (command.args or "").strip().split(maxsplit=3)
    if len(parts) != 4:
        await message.answer(
            "فرمت درست: /admin_plan_set <FREE|BASIC|PRO> <fixed|usage> <مبلغ> <feature1,feature2,key=value>\n\n"
            "برای سقف عضو (DEC-PY-0074) از این کلیدها استفاده کن:\n"
            "max_devotional_members=100 (سقف مجموع صلوات/دعا/زیارت/لعن)\n"
            "max_quran_members=302 (سقف قرآن؛ برای نامحدود این کلید رو کلاً ننویس)\n"
            "مثال کامل:\n"
            "/admin_plan_set FREE fixed 0 khatm.create,max_devotional_members=100,max_quran_members=302"
        )
        return
    plan_name, mode_name, price_text, feature_text = parts
    try:
        plan = PlanTier(plan_name.upper())
        mode = {"fixed": PricingMode.FIXED, "usage": PricingMode.USAGE_BASED}[mode_name.lower()]
        price = int(price_text)
        if price < 0:
            raise ValueError
    except (KeyError, ValueError):
        await message.answer("پلن، حالت یا مبلغ معتبر نیست.")
        return
    features: dict = {}
    for raw in feature_text.split(","):
        item = raw.strip()
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            key, value = key.strip(), value.strip()
            if not value.isdigit():
                await message.answer(f"مقدار «{key}» باید یک عدد باشه.")
                return
            features[key] = int(value)
        else:
            features[item] = True
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        definition = await plan_service.set_definition(
            session, plan=plan, title=plan.value, pricing_mode=mode,
            price_toman=price if mode == PricingMode.FIXED else 0,
            unit_price_toman=price if mode == PricingMode.USAGE_BASED else 0,
            entitlements=features,
        )
        await audit_service.record(
            session, actor_user_id=admin.id, action="PLAN_DEFINITION_UPDATE",
            details={"plan": plan.value, "pricing_mode": mode.value, "price": price, "features": list(features)},
        )
    await message.answer(f"پلن {definition.plan} ذخیره شد ✅")


@router.message(Command("admin_sms_plan_set"))
async def admin_sms_plan_set(message: Message, command: CommandObject) -> None:
    """Set/edit one admin-managed SMS subscription option (DEC: owner
    request 2026-09-20, plans must stay admin-editable, never hardcoded)."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.FINANCE_MANAGE):
        return
    parts = (command.args or "").strip().split()
    if len(parts) != 3:
        await message.answer(
            "فرمت درست: /admin_sms_plan_set <ماه> <قیمت تومان> <on|off>\n\n"
            "مثال: /admin_sms_plan_set 3 50000 on"
        )
        return
    try:
        months = int(parts[0])
        price = int(parts[1])
        enabled = {"on": True, "off": False}[parts[2].lower()]
        if months <= 0 or price < 0:
            raise ValueError
    except (KeyError, ValueError):
        await message.answer("ماه، قیمت یا وضعیت معتبر نیست.")
        return
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        option = await sms_subscription_service.set_option(
            session, months=months, price_toman=price, enabled=enabled
        )
        await audit_service.record(
            session, actor_user_id=admin.id, action="SMS_PLAN_OPTION_UPDATE",
            details={"months": option.months, "price_toman": option.price_toman, "enabled": option.enabled},
        )
    await message.answer(
        f"گزینهٔ {option.months} ماهه با قیمت {option.price_toman:,} تومان "
        f"{'فعال' if option.enabled else 'غیرفعال'} شد ✅"
    )


@router.message(Command("admin_templates"))
async def admin_templates(message: Message, command: CommandObject) -> None:
    """List the active latest Persian templates for a privileged admin."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return

    locale = (command.args or "fa").strip() or "fa"
    async with session_scope() as session:
        templates = await template_repository.list_latest(session, locale)
    if not templates:
        await message.answer(f"قالب فعالی برای زبان {locale} ثبت نشده است.")
        return
    lines = [f"قالب‌های فعال ({locale}):"]
    for template in templates:
        preview = template.body.replace("\n", " ")
        if len(preview) > 120:
            preview = preview[:117] + "..."
        lines.append(f"— {template.key} (نسخه {template.version}): {preview}")
    await message.answer("\n".join(lines))


@router.message(Command("admin_template_set"))
async def admin_template_set(message: Message, command: CommandObject) -> None:
    """Create a new immutable version of a locale-keyed template.

    Format: /admin_template_set <key> <locale> <body>
    """
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return

    parts = (command.args or "").strip().split(maxsplit=2)
    if len(parts) != 3 or len(parts[0]) > 120 or len(parts[1]) > 10 or not parts[2].strip():
        await message.answer("فرمت درست: /admin_template_set <key> <locale> <body>")
        return
    key, locale, body = parts
    try:
        template_service.validate_body(body)
    except ValueError as exc:
        detail = str(exc)
        if detail.startswith("unsupported placeholders:"):
            names = detail.split(":", 1)[1].strip()
            await message.answer(f"placeholder نامعتبر است: {names}\nمجاز: title, start, end, deadline, misses")
        else:
            await message.answer("placeholder قالب ناقص یا نامعتبر است؛ از فرم {{title}} استفاده کنید.")
        return

    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        version = await template_repository.next_version(session, key, locale)
        template = await template_repository.create(
            session, key=key, locale=locale, body=body, version=version
        )
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="MESSAGE_TEMPLATE_UPDATE",
            details={"key": key, "locale": locale, "version": version},
        )
    await message.answer(f"قالب {template.key} برای زبان {template.locale} با نسخه {version} ذخیره شد.")


@router.message(Command("admin_template_history"))
async def admin_template_history(message: Message, command: CommandObject) -> None:
    """List every immutable version and its enabled state."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    parts = (command.args or "").strip().split()
    if len(parts) not in (1, 2):
        await message.answer("فرمت درست: /admin_template_history <key> [locale]")
        return
    key, locale = parts[0], parts[1] if len(parts) == 2 else "fa"
    async with session_scope() as session:
        versions = await template_repository.list_versions(session, key, locale)
    if not versions:
        await message.answer(f"نسخه‌ای برای {key} ({locale}) پیدا نشد.")
        return
    lines = [f"تاریخچهٔ {key} ({locale}):"]
    for item in versions:
        preview = item.body.replace("\n", " ")
        if len(preview) > 100:
            preview = preview[:97] + "..."
        lines.append(
            f"— نسخه {item.version} | {'فعال' if item.enabled else 'غیرفعال'} | {preview}"
        )
    await message.answer("\n".join(lines))


@router.message(Command("admin_template_toggle"))
async def admin_template_toggle(message: Message, command: CommandObject) -> None:
    """Enable or disable one exact immutable template version."""
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.CONTENT_MANAGE):
        return
    parts = (command.args or "").strip().split()
    if len(parts) != 4 or parts[3].lower() not in {"on", "off"}:
        await message.answer(
            "فرمت درست: /admin_template_toggle <key> <locale> <version> <on|off>"
        )
        return
    key, locale, raw_version, raw_state = parts
    try:
        version = int(raw_version)
        if version < 1:
            raise ValueError
    except ValueError:
        await message.answer("شماره نسخه باید عدد مثبت باشد.")
        return
    enabled = raw_state.lower() == "on"
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        template = await template_repository.set_enabled(
            session, key, locale, version, enabled
        )
        if template is None:
            await message.answer("این نسخهٔ قالب پیدا نشد.")
            return
        await audit_service.record(
            session,
            actor_user_id=admin.id,
            action="MESSAGE_TEMPLATE_TOGGLE",
            details={
                "key": key,
                "locale": locale,
                "version": version,
                "enabled": enabled,
            },
        )
    await message.answer(
        f"نسخه {version} قالب {key} ({locale}) {'فعال' if enabled else 'غیرفعال'} شد ✅"
    )


def _admin_role_help() -> str:
    values = " | ".join(role.value for role in AdminRole)
    return (
        "نقش‌های معتبر:\n"
        f"{values}\n\n"
        "اعطا: /admin_role_grant <user_uuid> <role>\n"
        "لغو: /admin_role_revoke <user_uuid> <role>\n"
        "نمایش: /admin_role_list <user_uuid>"
    )


@router.message(Command("admin_role_list"))
async def admin_role_list(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.ADMIN_ROLES_MANAGE):
        return
    try:
        target_id = UUID((command.args or "").strip())
    except ValueError:
        await message.answer(_admin_role_help())
        return
    async with session_scope() as session:
        target = await identity_service.find_by_id(session, target_id)
        if target is None:
            await message.answer("کاربر پیدا نشد.")
            return
        roles = await authorization_service.list_roles(session, target.id)
    role_text = "، ".join(role.value for role in roles) if roles else "بدون نقش واگذارشده"
    await message.answer(f"نقش‌های {escape(target.display_name or str(target.id))}:\n{role_text}")


async def _change_admin_role(
    message: Message, command: CommandObject, *, revoke: bool
) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.ADMIN_ROLES_MANAGE):
        return
    parts = (command.args or "").strip().split()
    if len(parts) != 2:
        await message.answer(_admin_role_help())
        return
    try:
        target_id = UUID(parts[0])
        role = AdminRole(parts[1].upper())
    except ValueError:
        await message.answer(_admin_role_help())
        return
    async with session_scope() as session:
        actor = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        target = await identity_service.find_by_id(session, target_id)
        if target is None:
            await message.answer("کاربر پیدا نشد.")
            return
        if revoke:
            changed = await authorization_service.revoke_role(
                session, actor=actor, target=target, role=role
            )
            action = "ADMIN_ROLE_REVOKED"
        else:
            await authorization_service.grant_role(
                session, actor=actor, target=target, role=role
            )
            changed = True
            action = "ADMIN_ROLE_GRANTED"
        if changed:
            await audit_service.record(
                session,
                actor_user_id=actor.id,
                target_user_id=target.id,
                action=action,
                details={"role": role.value},
            )
    if revoke and not changed:
        await message.answer("این نقش از قبل برای کاربر فعال نبود.")
    else:
        await message.answer(
            f"نقش {role.value} برای {escape(target.display_name or str(target.id))} "
            f"{'لغو' if revoke else 'فعال'} شد ✅"
        )


@router.message(Command("admin_role_grant"))
async def admin_role_grant(message: Message, command: CommandObject) -> None:
    await _change_admin_role(message, command, revoke=False)


@router.message(Command("admin_role_revoke"))
async def admin_role_revoke(message: Message, command: CommandObject) -> None:
    await _change_admin_role(message, command, revoke=True)

@router.message(Command("admin_promote"))
async def admin_promote(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if not await _require_admin(message, platform, AdminPermission.MODERATION_MANAGE):
        return

    args = (command.args or "").split()
    if not args:
        await message.answer("فرمت درست: /admin_promote <chat_id>")
        return
    
    target_id = args[0]
    async with session_scope() as session:
        from khatmsaz.modules.identity.models import UserRole
        from khatmsaz.modules.identity import service as identity_service
        
        user = await identity_service.find_by_platform_id(session, Platform.TELEGRAM, target_id)
        if not user:
            user = await identity_service.find_by_platform_id(session, Platform.BALE, target_id)
        if not user:
            try:
                user = await identity_service.find_by_id(session, target_id)
            except:
                pass
                
        if not user:
            await message.answer(f"کاربری با شناسه {target_id} یافت نشد.")
            return
            
        user.role = UserRole.CREATOR
        await message.answer(f"✅ کاربر {user.display_name or user.id} با موفقیت به سازنده ارتقا یافت.")
