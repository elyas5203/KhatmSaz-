"""Creator message requests with mandatory admin moderation."""

from html import escape
from uuid import UUID

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from khatmsaz.bot.notify_adapter import get_notify_fn, send_media
from khatmsaz.core.db import session_scope
from khatmsaz.modules.audit_log import service as audit_service
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.broadcast.models import BroadcastStatus
from khatmsaz.modules.authorization import service as authorization_service
from khatmsaz.modules.authorization.models import AdminPermission
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.service import InsufficientFundsError
from khatmsaz.modules.sms.provider import build_provider as build_sms_provider
from datetime import datetime, timezone

router = Router(name="broadcast")


@router.message(Command("khatm_message"))
async def submit_khatm_message(message: Message, command: CommandObject) -> None:
    parts = (command.args or "").strip().split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("فرمت درست: /khatm_message <khatm_id> <پیام برای اعضا>")
        return
    try:
        khatm_id = UUID(parts[0])
    except ValueError:
        await message.answer("شناسه ختم معتبر نیست.")
        return
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if user is None:
            await message.answer("حساب شما پیدا نشد.")
            return
        try:
            item = await broadcast_service.submit(
                session, khatm_id=khatm_id, creator_user_id=user.id, body=parts[1], channel=platform.value,
            )
        except broadcast_service.plan_service.PlanFeatureUnavailableError:
            await message.answer("دو پیام رایگان شما مصرف شده یا مخاطبان ۱۰۰۰ نفر و بیشترند؛ برای ادامه پلن حرفه‌ای لازم است.")
            return
        except ValueError:
            await message.answer("ختم پیدا نشد، فعال نیست، یا متعلق به شما نیست؛ پیام حداکثر ۱۰۰۰ کاراکتر است.")
            return
    await message.answer(f"پیام شما برای تأیید محتوا ثبت شد ✅\nشناسه درخواست: {item.id}")


async def _is_admin(message: Message) -> tuple[Platform, object] | None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        if not await authorization_service.has_permission(
            session, admin, AdminPermission.MODERATION_MANAGE
        ):
            return None
    return platform, admin


@router.message(Command("admin_broadcasts"))
async def admin_broadcasts(message: Message) -> None:
    if await _is_admin(message) is None:
        return
    async with session_scope() as session:
        items = await broadcast_service.list_pending(session)
    if not items:
        await message.answer("پیام عمومیِ در انتظار بررسی وجود ندارد.")
        return
    lines = ["پیام‌های در انتظار بررسی:"]
    for item in items:
        lines.append(f"\n#{item.id}\nختم: {item.khatm_id}\n{escape(item.body)}")
    lines.append("\nتأیید: /admin_approve_broadcast <id> <یادداشت اختیاری>\nرد: /admin_reject_broadcast <id> <دلیل>")
    await message.answer("\n".join(lines))


async def _moderate(message: Message, command: CommandObject, *, approve: bool) -> None:
    auth = await _is_admin(message)
    if auth is None:
        return
    platform, _admin = auth
    parts = (command.args or "").strip().split(maxsplit=1)
    if not parts:
        await message.answer("فرمت درست: /admin_approve_broadcast <id> <یادداشت اختیاری>")
        return
    try:
        broadcast_id = UUID(parts[0])
    except ValueError:
        await message.answer("شناسه درخواست معتبر نیست.")
        return
    note = parts[1] if len(parts) == 2 else None
    async with session_scope() as session:
        admin = await identity_service.find_by_platform(session, platform, str(message.chat.id))
        try:
            item = await (broadcast_service.approve if approve else broadcast_service.reject)(
                session, broadcast_id, note
            )
        except ValueError:
            await message.answer("این پیام پیدا نشد یا دیگر در انتظار بررسی نیست.")
            return
        await audit_service.record(
            session, actor_user_id=admin.id,
            target_khatm_id=item.khatm_id,
            action="KHATM_BROADCAST_APPROVE" if approve else "KHATM_BROADCAST_REJECT",
            details={"broadcast_id": str(item.id), "note": note},
        )
        if approve:
            if item.cost_toman > 0 and item.paid_at is None:
                try:
                    invoice = await wallet_service.purchase(
                        session, user_id=item.creator_user_id, gross_amount_toman=item.cost_toman,
                        description=f"ارسال گروهی {item.channel}",
                    )
                except InsufficientFundsError:
                    item.status = BroadcastStatus.PENDING
                    item.reviewed_at = None
                    item.admin_note = "موجودی کیف پول سازنده کافی نیست"
                    await session.flush()
                    await message.answer("موجودی کیف پول سازنده برای این ارسال کافی نیست.")
                    return
                item.invoice_id = invoice.id
                item.paid_at = datetime.now(timezone.utc)
            destinations = await broadcast_service.audience_destinations(session, item)
            if item.channel == "SMS":
                provider = build_sms_provider()
                for phone in destinations:
                    await provider.send(phone=phone, text=item.body)
            else:
                media_file_id = item.media_file_id_telegram if item.channel == "TELEGRAM" else item.media_file_id_bale
                if item.media_type and media_file_id:
                    for subject in destinations:
                        await send_media(item.channel, subject, item.media_type, media_file_id, caption=item.body or None)
                else:
                    notify = get_notify_fn()
                    for subject in destinations:
                        await notify(item.channel, subject, item.body)
            await broadcast_service.mark_sent(session, item)
    await message.answer("پیام تأیید و برای اعضای فعال ارسال شد ✅" if approve else "پیام رد شد.")


@router.message(Command("admin_approve_broadcast"))
async def admin_approve_broadcast(message: Message, command: CommandObject) -> None:
    await _moderate(message, command, approve=True)


@router.message(Command("admin_reject_broadcast"))
async def admin_reject_broadcast(message: Message, command: CommandObject) -> None:
    await _moderate(message, command, approve=False)
