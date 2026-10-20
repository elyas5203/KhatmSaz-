"""Delivery logic for approved broadcasts across Telegram, Bale, and SMS."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.notify_adapter import get_notify_fn, send_media
from khatmsaz.modules.broadcast import repository as broadcast_repo
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.broadcast.models import BroadcastReceiptStatus, KhatmBroadcast
from khatmsaz.modules.sms.provider import build_provider as build_sms_provider

logger = logging.getLogger("khatmsaz")


async def deliver_broadcast(session: AsyncSession, item: KhatmBroadcast) -> int:
    """Deliver an approved broadcast to all target audience members, create receipts, and notify creator."""
    destinations = await broadcast_service.audience_destinations(session, item)
    sender_name = await broadcast_service.sender_display_name(session, item)
    prefix = f"📢 پیام از طرف سازندهٔ ختم، {sender_name}:\n\n"
    body = getattr(item, "body", "") or ""
    body_with_sender = f"{prefix}{body}" if body else prefix.strip()
    channel = getattr(item, "channel", "TELEGRAM")
    media_type = getattr(item, "media_type", None)
    media_file_id = (
        getattr(item, "media_file_id_telegram", None) if channel == "TELEGRAM"
        else getattr(item, "media_file_id_bale", None)
    )

    receipts_to_create: list[dict] = []

    if channel == "SMS":
        provider = build_sms_provider()
        for destination in destinations:
            phone = getattr(destination, "subject", destination)
            try:
                await provider.send(phone=phone, text=body_with_sender)
            except Exception as exc:
                logger.warning("SMS broadcast deliver failed to %s: %s", phone, exc)
            user_id = getattr(destination, "user_id", None)
            if user_id:
                receipts_to_create.append({
                    "broadcast_id": item.id,
                    "recipient_user_id": user_id,
                    "channel": channel,
                    "status": BroadcastReceiptStatus.DELIVERED.value,
                })
    else:
        if media_type and media_file_id:
            for destination in destinations:
                try:
                    await send_media(
                        channel, destination.subject, media_type, media_file_id,
                        caption=body_with_sender, bot_instance_id=destination.bot_instance_id,
                    )
                except Exception as exc:
                    logger.warning("Media broadcast deliver failed to %s: %s", destination.subject, exc)
                user_id = getattr(destination, "user_id", None)
                if user_id:
                    receipts_to_create.append({
                        "broadcast_id": item.id,
                        "recipient_user_id": user_id,
                        "channel": channel,
                        "status": BroadcastReceiptStatus.DELIVERED.value,
                    })
        else:
            try:
                notify = get_notify_fn()
            except RuntimeError:
                logger.warning("notify_fn not initialized yet; skipping live notification")
                notify = None

            if notify:
                for destination in destinations:
                    try:
                        await notify(
                            channel, destination.subject, body_with_sender,
                            bot_instance_id=destination.bot_instance_id,
                        )
                    except Exception as exc:
                        logger.warning("Text broadcast deliver failed to %s: %s", destination.subject, exc)
                    user_id = getattr(destination, "user_id", None)
                    if user_id:
                        receipts_to_create.append({
                            "broadcast_id": item.id,
                            "recipient_user_id": user_id,
                            "channel": channel,
                            "status": BroadcastReceiptStatus.DELIVERED.value,
                        })

    if receipts_to_create:
        try:
            await broadcast_repo.create_receipts(session, receipts_to_create)
        except Exception as exc:
            logger.warning("Failed to bulk create broadcast receipts: %s", exc)

    await broadcast_service.mark_sent(session, item)

    # MASTER-60: Notify creator with interactive live stats card entry button
    try:
        await broadcast_service.notify_creator_broadcast_sent(session, item, len(destinations))
    except Exception as exc:
        logger.warning("Failed to notify creator of broadcast delivery: %s", exc)

    return len(destinations)
