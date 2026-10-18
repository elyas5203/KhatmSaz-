"""Admin alert synchronization across multiple administrators.

When an action item (e.g. support ticket reply, manual phone verification review)
is handled by any administrator, this module updates the database record and
edits other administrators' Telegram messages to remove action buttons and display
who took action and at what time, preventing race conditions and duplicate work.
"""

from datetime import datetime, timezone
import logging
from zoneinfo import ZoneInfo
import uuid

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.notify_adapter import send_with_keyboard_msg
from khatmsaz.config import get_settings
from khatmsaz.core.bot_registry import get_registry
from khatmsaz.modules.authorization.models import AdminAlertMessage, AdminRole, AdminRoleGrant
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole

logger = logging.getLogger("khatmsaz.admin_sync")


async def record_admin_alert_message(
    session: AsyncSession,
    *,
    alert_type: str,
    reference_id: str,
    chat_id: str,
    message_id: int,
    original_text: str | None = None,
) -> AdminAlertMessage:
    """Record an alert message sent to an admin for later cross-admin synchronization."""
    alert = AdminAlertMessage(
        id=uuid.uuid4(),
        alert_type=alert_type,
        reference_id=str(reference_id),
        chat_id=str(chat_id),
        message_id=int(message_id),
        original_text=original_text,
        handled=False,
    )
    session.add(alert)
    await session.flush()
    return alert


async def is_admin_alert_handled(
    session: AsyncSession,
    alert_type: str,
    reference_id: str,
) -> tuple[bool, str | None, str | None]:
    """Check if an alert has already been acted on.

    Returns:
        (is_handled, handled_by_name, action_taken)
    """
    stmt = (
        select(AdminAlertMessage)
        .where(
            AdminAlertMessage.alert_type == alert_type,
            AdminAlertMessage.reference_id == str(reference_id),
            AdminAlertMessage.handled.is_(True),
        )
        .limit(1)
    )
    row = (await session.execute(stmt)).scalar_one_or_none()
    if row is not None:
        return True, row.handled_by_name, row.action_taken
    return False, None, None


async def mark_admin_alert_handled(
    session: AsyncSession,
    bot: Bot | None,
    *,
    alert_type: str,
    reference_id: str,
    actor_name: str,
    action_label: str,
    tz_name: str = "Asia/Tehran",
) -> int:
    """Mark all copies of an alert handled in DB and edit Telegram messages across all admins."""
    stmt = select(AdminAlertMessage).where(
        AdminAlertMessage.alert_type == alert_type,
        AdminAlertMessage.reference_id == str(reference_id),
    )
    alerts = list((await session.execute(stmt)).scalars().all())
    now_utc = datetime.now(timezone.utc)
    for alert in alerts:
        alert.handled = True
        alert.handled_by_name = actor_name
        alert.action_taken = action_label
        alert.handled_at = now_utc
    await session.flush()

    if not alerts:
        return 0

    if bot is None:
        try:
            bot = get_registry().get_creator_bot(Platform.TELEGRAM)
        except Exception:
            bot = None

    if bot is None:
        logger.warning("No bot available to edit admin alert messages.")
        return len(alerts)

    try:
        local_tz = ZoneInfo(tz_name)
    except Exception:
        local_tz = ZoneInfo("Asia/Tehran")
    time_str = now_utc.astimezone(local_tz).strftime("%H:%M")

    for alert in alerts:
        try:
            chat_id = int(alert.chat_id)
        except (ValueError, TypeError):
            continue

        if alert.original_text:
            new_text = f"{alert.original_text}\n\n✅ توسط «{actor_name}» در ساعت {time_str} {action_label} شد."
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=alert.message_id,
                    text=new_text,
                    reply_markup=None,
                )
                continue
            except Exception as exc:
                logger.debug("edit_message_text failed for admin %s (%s), falling back to markup edit", chat_id, exc)

        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=alert.message_id,
                reply_markup=None,
            )
        except Exception as exc:
            logger.debug("edit_message_reply_markup failed for admin %s: %s", chat_id, exc)

    return len(alerts)


async def get_all_admin_telegram_chat_ids(session: AsyncSession | None = None) -> list[str]:
    """Retrieve all Telegram chat IDs for both Super Admins and non-Super Admin Admins.

    Aggregates configured IDs (.env) and active database-delegated admin roles.
    """
    settings = get_settings()
    configured_ids: set[str] = set()

    for raw in (settings.super_admin_telegram_chat_ids, settings.admin_telegram_chat_ids):
        for item in raw.split(","):
            val = item.strip()
            if val:
                configured_ids.add(val)

    if session is not None:
        stmt = (
            select(PlatformIdentity.subject)
            .select_from(PlatformIdentity)
            .join(User, User.id == PlatformIdentity.user_id)
            .outerjoin(AdminRoleGrant, AdminRoleGrant.user_id == User.id)
            .where(
                PlatformIdentity.platform == Platform.TELEGRAM,
                (
                    (User.role == UserRole.SUPER_ADMIN)
                    | (
                        (AdminRoleGrant.role.in_([AdminRole.SUPER_ADMIN.value, AdminRole.ADMIN.value]))
                        & (AdminRoleGrant.revoked_at.is_(None))
                    )
                ),
            )
        )
        db_chat_ids = (await session.execute(stmt)).scalars().all()
        for cid in db_chat_ids:
            if cid and str(cid).strip():
                configured_ids.add(str(cid).strip())

    return sorted(list(configured_ids))


async def send_alert_to_all_admins(
    session: AsyncSession,
    *,
    alert_type: str,
    reference_id: str,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    bot: Bot | None = None,
) -> list[AdminAlertMessage]:
    """Broadcast an actionable alert to all admins and record each sent message for synchronization."""
    admin_chat_ids = await get_all_admin_telegram_chat_ids(session)
    recorded_alerts: list[AdminAlertMessage] = []

    for chat_id in admin_chat_ids:
        msg = None
        if bot is not None:
            try:
                msg = await bot.send_message(
                    chat_id=int(chat_id),
                    text=text,
                    reply_markup=reply_markup,
                )
            except Exception as exc:
                logger.warning("Failed to deliver alert to admin %s: %s", chat_id, exc)
        else:
            msg = await send_with_keyboard_msg(
                Platform.TELEGRAM.value,
                chat_id,
                text,
                reply_markup,
            )

        if msg is not None:
            alert = await record_admin_alert_message(
                session,
                alert_type=alert_type,
                reference_id=reference_id,
                chat_id=chat_id,
                message_id=msg.message_id,
                original_text=text,
            )
            recorded_alerts.append(alert)

    return recorded_alerts


async def notify_new_admin_appointed(
    session: AsyncSession,
    user_id: uuid.UUID,
    bot: Bot | None = None,
) -> bool:
    """Send warm instant notification to newly appointed Admin."""
    from khatmsaz.modules.identity import service as identity_service
    from khatmsaz.bot.notify_adapter import get_notify_fn
    identities = await identity_service.list_identities_for_user(session, user_id)
    if not identities:
        return False

    welcome_text = (
        "🎉 با سلام و خداقوت؛\n"
        "حساب کاربری شما به عنوان «مدیر (ادمین)» در سامانه ختم‌ساز فعال شد.\n\n"
        "از این پس می‌توانید به امکانات مدیریتی دسترسی داشته باشید و گزارش‌های روزانه و پیام‌های پشتیبانی برای شما ارسال خواهد شد."
    )

    if bot is None:
        try:
            bot = get_registry().get_creator_bot(Platform.TELEGRAM)
        except Exception:
            bot = None

    sent = False
    for pi in identities:
        try:
            if bot is not None and pi.platform == Platform.TELEGRAM:
                await bot.send_message(chat_id=int(pi.subject), text=welcome_text)
                sent = True
            else:
                try:
                    notify = get_notify_fn()
                    await notify(pi.platform.value, pi.subject, welcome_text)
                    sent = True
                except Exception:
                    pass
        except Exception as exc:
            logger.warning("Failed to send welcome message to new admin %s: %s", pi.subject, exc)
    return sent

