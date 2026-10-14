"""Direct Telegram MTProto downloading for large media files (>20MB up to 2GB).

Bypasses the standard Telegram Bot API 20MB get_file limit using Telethon
with bot token authentication. Based on the proven implementation from
MohtavaTelBot (DEC-PY-0129 / MASTER-23).
"""

import asyncio
import logging
import os
from typing import Any, Callable

from telethon import TelegramClient
from telethon.sessions import MemorySession

from khatmsaz.config import get_settings

logger = logging.getLogger(__name__)

# Default official Telegram Desktop API credentials (from MohtavaTelBot reference)
DEFAULT_TELEGRAM_API_ID = 2040
DEFAULT_TELEGRAM_API_HASH = "b18441a1ff607e10a989891a5462e627"


def get_telegram_api_credentials() -> tuple[int, str]:
    """Retrieve Telegram api_id and api_hash, falling back to official Desktop credentials."""
    settings = get_settings()
    api_id = settings.telegram_api_id or DEFAULT_TELEGRAM_API_ID
    api_hash = settings.telegram_api_hash or DEFAULT_TELEGRAM_API_HASH
    return int(api_id), str(api_hash)


async def download_telegram_media_by_message(
    bot_token: str,
    chat_id: int | str,
    message_id: int,
    dest_path: str,
    api_id: int | None = None,
    api_hash: str | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> str:
    """Download media from a Telegram message directly via MTProto.

    Supports files up to 2GB without hitting the 20MB Bot API download limit.
    """
    default_id, default_hash = get_telegram_api_credentials()
    chosen_id = api_id or default_id
    chosen_hash = api_hash or default_hash

    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)

    client = TelegramClient(MemorySession(), chosen_id, chosen_hash)
    await client.start(bot_token=bot_token)
    try:
        target_chat: int | str = (
            int(chat_id)
            if (
                isinstance(chat_id, str)
                and (chat_id.isdigit() or (chat_id.startswith("-") and chat_id[1:].isdigit()))
            )
            else chat_id
        )
        msg = await client.get_messages(target_chat, ids=int(message_id))
        if not msg or not getattr(msg, "media", None):
            raise RuntimeError(f"Message {message_id} in chat {chat_id} contains no media")

        downloaded = await client.download_media(
            msg,
            file=dest_path,
            progress_callback=progress_callback,
        )
        if not downloaded or not os.path.exists(dest_path):
            raise RuntimeError(f"Telethon failed to download media to {dest_path}")
        return dest_path
    finally:
        await client.disconnect()


async def download_telegram_media_by_file_id(
    tg_bot: Any,
    scratch_chat_id: int | str,
    file_id: str,
    kind: str,
    dest_path: str,
    api_id: int | None = None,
    api_hash: str | None = None,
) -> str:
    """Download media given a Telegram file_id by sending to scratch chat then downloading via MTProto.

    Telegram allows bots to send files up to 2GB using existing file_ids.
    This method sends the file to scratch_chat_id, downloads it via MTProto,
    and removes the temporary scratch message.
    """
    kind_upper = kind.upper()
    if kind_upper == "VIDEO":
        temp_msg = await tg_bot.send_video(chat_id=scratch_chat_id, video=file_id, caption="[temp_sync]")
    elif kind_upper == "AUDIO":
        temp_msg = await tg_bot.send_audio(chat_id=scratch_chat_id, audio=file_id, caption="[temp_sync]")
    elif kind_upper == "IMAGE":
        temp_msg = await tg_bot.send_photo(chat_id=scratch_chat_id, photo=file_id, caption="[temp_sync]")
    else:
        temp_msg = await tg_bot.send_document(chat_id=scratch_chat_id, document=file_id, caption="[temp_sync]")

    try:
        bot_token = getattr(tg_bot, "token", "")
        return await download_telegram_media_by_message(
            bot_token=bot_token,
            chat_id=temp_msg.chat.id,
            message_id=temp_msg.message_id,
            dest_path=dest_path,
            api_id=api_id,
            api_hash=api_hash,
        )
    finally:
        try:
            await tg_bot.delete_message(chat_id=temp_msg.chat.id, message_id=temp_msg.message_id)
        except Exception:
            pass
