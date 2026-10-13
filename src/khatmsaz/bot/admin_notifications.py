"""Centralized push notifications for queues that require admin action.
Dispatches directly via the main creator bot (Khatm_Saz_bot) to all Super Admins.
"""

import logging
from io import BytesIO

from aiogram import Bot
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.config import get_settings
from khatmsaz.core.bot_registry import get_registry
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole

logger = logging.getLogger("khatmsaz")


async def get_super_admin_telegram_chat_ids(session: AsyncSession | None = None) -> list[int]:
    """Retrieve super admin numeric Telegram chat IDs from settings and database."""
    admin_ids: set[int] = set()
    # 1. From settings (.env)
    for value in get_settings().super_admin_telegram_chat_ids.split(","):
        value = value.strip()
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            admin_ids.add(int(value))

    # 2. From database (users with SUPER_ADMIN role)
    async def _fetch_from_db(s: AsyncSession) -> None:
        stmt = (
            select(PlatformIdentity.subject)
            .join(User, User.id == PlatformIdentity.user_id)
            .where(
                User.role == UserRole.SUPER_ADMIN,
                PlatformIdentity.platform == Platform.TELEGRAM,
            )
        )
        for sid in (await s.execute(stmt)).scalars().all():
            sid_clean = str(sid).strip()
            if sid_clean.isdigit():
                admin_ids.add(int(sid_clean))

    try:
        if session is not None:
            await _fetch_from_db(session)
        else:
            async with session_scope() as s:
                await _fetch_from_db(s)
    except Exception as exc:
        logger.warning("Failed to query super admin chat IDs from DB: %s", exc)

    return sorted(admin_ids)


async def notify_super_admins(
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    session: AsyncSession | None = None,
) -> None:
    """Send text (and optional inline buttons) to all Super Admins via Khatm_Saz_bot."""
    admin_ids = await get_super_admin_telegram_chat_ids(session)
    if not admin_ids:
        logger.warning("No super admin Telegram chat IDs found to notify.")
        return

    registry = get_registry()
    target_bot = registry.get_admin_bot(Platform.TELEGRAM) or registry.get_creator_bot(Platform.TELEGRAM)
    if not target_bot:
        logger.warning("Neither Admin bot nor Creator bot available in registry for admin notification.")
        return

    for chat_id in admin_ids:
        try:
            await target_bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
            )
            logger.info("Admin notification sent to %s via @%s", chat_id, getattr(target_bot, "khatmsaz_username", "admin_bot"))
        except Exception as exc:
            logger.warning("Failed to deliver admin notification to %s: %s", chat_id, exc)


async def notify_super_admins_photo(
    caption: str,
    *,
    photo_file_id: str | None = None,
    photo_bytes: bytes | None = None,
    source_bot: Bot | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
    session: AsyncSession | None = None,
) -> None:
    """Send a photo with caption and inline buttons to all Super Admins via @khatmsaz_admin_bot.
    If the photo was uploaded to another bot, downloads it first to avoid cross-bot file_id errors.
    """
    admin_ids = await get_super_admin_telegram_chat_ids(session)
    if not admin_ids:
        logger.warning("No super admin Telegram chat IDs found for photo notification.")
        return

    registry = get_registry()
    target_bot = registry.get_admin_bot(Platform.TELEGRAM) or registry.get_creator_bot(Platform.TELEGRAM)
    if not target_bot:
        logger.warning("Neither Admin bot nor Creator bot available in registry for admin photo notification.")
        return

    upload = None
    if photo_bytes is not None:
        upload = BufferedInputFile(photo_bytes, filename="receipt.jpg")
    elif photo_file_id and source_bot:
        try:
            buffer = BytesIO()
            await source_bot.download(photo_file_id, destination=buffer)
            upload = BufferedInputFile(buffer.getvalue(), filename="receipt.jpg")
        except Exception as exc:
            logger.warning("Failed to download photo from source bot: %s", exc)

    for chat_id in admin_ids:
        try:
            if upload is not None:
                await target_bot.send_photo(
                    chat_id=chat_id,
                    photo=upload,
                    caption=caption,
                    reply_markup=reply_markup,
                )
            elif photo_file_id and (source_bot is None or source_bot == target_bot):
                await target_bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file_id,
                    caption=caption,
                    reply_markup=reply_markup,
                )
            else:
                await target_bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    reply_markup=reply_markup,
                )
            logger.info("Admin photo notification sent to %s via @%s", chat_id, getattr(target_bot, "khatmsaz_username", "admin_bot"))
        except Exception as exc:
            logger.warning("Failed to deliver admin photo notification to %s: %s", chat_id, exc)
