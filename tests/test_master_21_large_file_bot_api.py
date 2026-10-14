"""Unit tests for Master 21: Large File Telegram Local Bot API & Heavy Media Mirroring (MASTER-21)."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import FSInputFile, File, Message

from khatmsaz.bot.telegram.client import build_telegram_bot
from khatmsaz.modules.content.migrator import TelegramToBaleMigrator


@pytest.mark.asyncio
async def test_build_telegram_bot_with_custom_local_api_server():
    """Verify build_telegram_bot sets TelegramAPIServer when telegram_api_server_url is configured."""
    with patch("khatmsaz.bot.telegram.client.get_settings") as mock_settings:
        mock_settings.return_value.telegram_bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"
        mock_settings.return_value.telegram_api_server_url = "http://127.0.0.1:8081"
        mock_settings.return_value.telegram_api_server_is_local = True
        mock_settings.return_value.bot_http_proxy_url = ""

        bot = build_telegram_bot()
        assert bot.session.api.is_local is True
        assert "http://127.0.0.1:8081" in bot.session.api.base


@pytest.mark.asyncio
async def test_migrator_get_telegram_file_local_path():
    """Verify get_telegram_file returns local file path without buffering bytes when file exists on disk."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(b"local video chunk data" * 100)
        local_path = tf.name

    try:
        mock_tg_bot = AsyncMock()
        mock_file = MagicMock(spec=File)
        mock_file.file_path = local_path
        mock_tg_bot.get_file = AsyncMock(return_value=mock_file)

        migrator = TelegramToBaleMigrator(
            tg_bot=mock_tg_bot,
            bale_bot=AsyncMock(),
            bale_storage_chat_id=12345,
        )

        file_bytes, file_path = await migrator.get_telegram_file("sample_large_file_id")

        assert file_bytes is None
        assert file_path == local_path
        mock_tg_bot.get_file.assert_awaited_once_with("sample_large_file_id")
        # Ensure bot.download was NOT called since file is already on local disk
        mock_tg_bot.download.assert_not_called()
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


@pytest.mark.asyncio
async def test_migrator_upload_to_bale_with_file_path():
    """Verify upload_to_bale uses FSInputFile and streams video to Bale without RAM pressure."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(b"mock video data" * 100)
        local_path = tf.name

    try:
        mock_bale_bot = AsyncMock()
        mock_msg = MagicMock(spec=Message)
        mock_video = MagicMock()
        mock_video.file_id = "bale_uploaded_video_file_id_777"
        mock_msg.video = mock_video
        mock_msg.message_id = 42
        mock_bale_bot.send_video = AsyncMock(return_value=mock_msg)
        mock_bale_bot.delete_message = AsyncMock()

        migrator = TelegramToBaleMigrator(
            tg_bot=AsyncMock(),
            bale_bot=mock_bale_bot,
            bale_storage_chat_id=987654321,
            delay_seconds=0,
        )

        bale_file_id = await migrator.upload_to_bale(
            file_path=local_path,
            kind="VIDEO",
            filename="khutbah_part1.mp4",
            caption="بخش ۱",
        )

        assert bale_file_id == "bale_uploaded_video_file_id_777"
        mock_bale_bot.send_video.assert_awaited_once()
        call_kwargs = mock_bale_bot.send_video.call_args.kwargs
        assert call_kwargs["chat_id"] == 987654321
        assert isinstance(call_kwargs["video"], FSInputFile)
        assert call_kwargs["caption"] == "بخش ۱"
        # Temporary storage chat message should be deleted
        mock_bale_bot.delete_message.assert_awaited_once_with(chat_id=987654321, message_id=42)
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


@pytest.mark.asyncio
async def test_migrator_get_asset_file_direct_and_channel():
    """Verify get_asset_file correctly handles direct file_ids and tg_forward references."""
    mock_tg_bot = AsyncMock()
    mock_file = MagicMock(spec=File)
    mock_file.file_path = "/var/lib/telegram-bot-api/videos/test.mp4"
    mock_tg_bot.get_file = AsyncMock(return_value=mock_file)

    migrator = TelegramToBaleMigrator(
        tg_bot=mock_tg_bot,
        bale_bot=AsyncMock(),
        bale_storage_chat_id=123,
        tg_scratch_chat_id=5490508090,
    )

    with patch("os.path.exists", return_value=True):
        file_bytes, file_path, kind, filename = await migrator.get_asset_file(
            "direct_video_fid", fallback_kind="VIDEO"
        )
        assert file_bytes is None
        assert file_path == "/var/lib/telegram-bot-api/videos/test.mp4"
        assert kind == "VIDEO"
        assert filename == "media.mp4"
