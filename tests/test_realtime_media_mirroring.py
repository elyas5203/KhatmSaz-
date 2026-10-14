"""Unit tests for Real-time Cross-Platform Media Mirroring (MASTER-16 / WP-01..WP-04)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import (
    Audio,
    BufferedInputFile,
    Chat,
    Document,
    Message,
    PhotoSize,
    Video,
)

from khatmsaz.bot.bale.client import BaleAiohttpSession
from khatmsaz.bot.filters import AdminFilter
from khatmsaz.core.ids import new_id
from khatmsaz.modules.content.migrator import (
    TelegramToBaleMigrator,
    mirror_devotional_media_to_bale,
)
from khatmsaz.modules.content.models import DevotionalAsset, DevotionalMedia
from khatmsaz.modules.content.service import AppendMediaResult
from khatmsaz.modules.identity.models import Platform, UserRole


class FakeResult:
    def __init__(self, items):
        self._items = list(items)

    def scalars(self):
        return self

    def scalar(self):
        return self._items[0] if self._items else None

    def all(self):
        return list(self._items)

    def __iter__(self):
        return iter(self._items)


class FakeSession:
    def __init__(self, devotional_assets=None, devotional_media=None):
        self.devotional_assets: list[DevotionalAsset] = list(devotional_assets or [])
        self.devotional_media: list[DevotionalMedia] = list(devotional_media or [])
        self.added = []

    def add(self, obj):
        self.added.append(obj)
        if isinstance(obj, DevotionalAsset):
            self.devotional_assets.append(obj)
        elif isinstance(obj, DevotionalMedia):
            self.devotional_media.append(obj)

    async def flush(self):
        pass

    async def commit(self):
        pass

    async def execute(self, statement):
        try:
            params = statement.compile().params
        except Exception:
            params = {}

        stmt_str = str(statement).lower()
        if "devotional_assets" in stmt_str:
            slug = params.get("slug_1")
            matching = [a for a in self.devotional_assets if not slug or a.slug == slug]
            return FakeResult(matching)

        if "devotional_media" in stmt_str:
            matching = list(self.devotional_media)
            for k, val in params.items():
                if "asset_platform" in k:
                    matching = [m for m in matching if m.asset_platform == val]
                elif "kind" in k:
                    matching = [m for m in matching if m.kind == val]
                elif "page_number" in k:
                    matching = [m for m in matching if m.page_number == val]
            return FakeResult(matching)

        return FakeResult([])

    async def scalar(self, statement):
        res = await self.execute(statement)
        return res.scalar()


@pytest.mark.asyncio
async def test_bale_aiohttp_session_supports_video_mime():
    """Verify BaleAiohttpSession detects video/mp4 for video uploads."""
    session = BaleAiohttpSession()
    bot = MagicMock()
    method = MagicMock()
    method.model_dump.return_value = {
        "video": BufferedInputFile(b"test_video_bytes", filename="lecture_part1.mp4"),
        "caption": "Part 1 video",
    }
    form = session.build_form_data(bot, method)
    # Form fields are fields added
    found_video_field = False
    for field in form._fields:
        # field is a tuple/dict depending on aiohttp FormData internals
        headers = field[0]
        if "video" in str(headers):
            found_video_field = True
            assert "video/mp4" in str(headers) or "video/mp4" in str(field[1])
    assert found_video_field


@pytest.mark.asyncio
async def test_admin_filter_checks_super_admin_env_ids():
    """Verify AdminFilter validates against configured super_admin_telegram_chat_ids."""
    with patch("khatmsaz.bot.filters.get_settings") as mock_settings:
        mock_settings.return_value.super_admin_telegram_chat_ids = "5490508090,123456"
        mock_settings.return_value.super_admin_bale_chat_ids = "987654"

        admin_filter = AdminFilter()

        # Authorized Telegram admin
        msg_auth = MagicMock()
        msg_auth.chat.id = 5490508090
        bot_tg = MagicMock()
        bot_tg.khatmsaz_platform = Platform.TELEGRAM

        assert await admin_filter(msg_auth, bot_tg) is True

        # Authorized Bale admin
        msg_bale = MagicMock()
        msg_bale.chat.id = 987654
        bot_bale = MagicMock()
        bot_bale.khatmsaz_platform = Platform.BALE

        assert await admin_filter(msg_bale, bot_bale) is True

        # Unauthorized chat id not in config or DB
        msg_unauth = MagicMock()
        msg_unauth.chat.id = 999999
        with patch("khatmsaz.bot.filters.session_scope") as mock_scope:
            mock_session = AsyncMock()
            mock_scope.return_value.__aenter__.return_value = mock_session
            with patch("khatmsaz.modules.identity.service.find_by_platform", return_value=None):
                assert await admin_filter(msg_unauth, bot_tg) is False


@pytest.mark.asyncio
async def test_upload_to_bale_handles_video():
    """Verify TelegramToBaleMigrator sends video via send_video and extracts file_id."""
    bale_bot = AsyncMock()
    mock_msg = MagicMock()
    mock_video = MagicMock(spec=Video)
    mock_video.file_id = "bale_video_file_id_777"
    mock_msg.video = mock_video
    mock_msg.message_id = 101
    bale_bot.send_video.return_value = mock_msg
    bale_bot.delete_message.return_value = True

    migrator = TelegramToBaleMigrator(
        tg_bot=None,
        bale_bot=bale_bot,
        bale_storage_chat_id=1499052236,
        delay_seconds=0,
    )

    file_id = await migrator.upload_to_bale(
        file_bytes=b"video_content",
        kind="VIDEO",
        filename="clip_1.mp4",
        caption="Video 1",
    )

    assert file_id == "bale_video_file_id_777"
    bale_bot.send_video.assert_awaited_once()
    bale_bot.delete_message.assert_awaited_once_with(chat_id=1499052236, message_id=101)


@pytest.mark.asyncio
async def test_download_asset_bytes_handles_channel_forward():
    """Verify download_asset_bytes properly forwards and cleans up channel messages."""
    tg_bot = AsyncMock()
    fwd_msg = MagicMock()
    mock_vid = MagicMock(spec=Video)
    mock_vid.file_id = "tg_video_fid_44"
    mock_vid.file_name = "part1.mp4"
    fwd_msg.photo = None
    fwd_msg.video = mock_vid
    fwd_msg.audio = None
    fwd_msg.voice = None
    fwd_msg.document = None
    fwd_msg.message_id = 999
    tg_bot.forward_message.return_value = fwd_msg
    tg_bot.delete_message.return_value = True

    async def fake_download(file_id, destination):
        destination.write(b"channel_video_payload")

    tg_bot.download.side_effect = fake_download

    migrator = TelegramToBaleMigrator(
        tg_bot=tg_bot,
        bale_bot=None,
        bale_storage_chat_id=1499052236,
        tg_scratch_chat_id=5490508090,
    )

    bytes_out, kind, filename = await migrator.download_asset_bytes(
        "tg_forward:@khedmatgozaran_group:25286", fallback_kind="VIDEO"
    )

    assert bytes_out == b"channel_video_payload"
    assert kind == "VIDEO"
    assert filename == "part1.mp4"
    tg_bot.forward_message.assert_awaited_once_with(
        chat_id=5490508090, from_chat_id="@khedmatgozaran_group", message_id=25286
    )
    tg_bot.delete_message.assert_awaited_once_with(chat_id=5490508090, message_id=999)


@pytest.mark.asyncio
async def test_mirror_devotional_media_to_bale_success():
    """Verify mirror_devotional_media_to_bale completes download, upload, and DB persistence."""
    fake_asset = DevotionalAsset(
        id=new_id(), content_type="DUA", slug="khutbah-fadakiah", title="خطبه فدکیه", text_body=""
    )
    fake_db = FakeSession(devotional_assets=[fake_asset])

    with patch("khatmsaz.modules.content.migrator.get_settings") as mock_settings:
        mock_settings.return_value.bale_bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"
        mock_settings.return_value.bale_media_storage_chat_id = 1499052236

        with patch("khatmsaz.bot.bale.client.build_bale_bot") as mock_build_bale:
            mock_build_bale.return_value = AsyncMock()

            with patch("khatmsaz.modules.content.migrator.session_scope") as mock_scope:
                mock_scope.return_value.__aenter__.return_value = fake_db

                with patch("khatmsaz.modules.content.migrator.TelegramToBaleMigrator") as mock_migrator_cls:
                    instance = MagicMock()
                    instance.download_asset_bytes = AsyncMock(
                        return_value=(b"raw_bytes", "VIDEO", "part1.mp4")
                    )
                    instance.upload_to_bale = AsyncMock(return_value="bale_mirrored_file_id_999")
                    mock_migrator_cls.return_value = instance

                    bot = AsyncMock()
                    bale_fid = await mirror_devotional_media_to_bale(
                        slug="khutbah-fadakiah",
                        kind="VIDEO",
                        page_number=1,
                        asset_ref="tg_raw_file_id_1",
                        caption="بخش ۱",
                        notify_chat_id=5490508090,
                        bot=bot,
                    )

                    assert bale_fid == "bale_mirrored_file_id_999"
                    # Check that DevotionalMedia with asset_platform='BALE' was created in DB
                    bale_records = [
                        m for m in fake_db.devotional_media if m.asset_platform == "BALE"
                    ]
                    assert len(bale_records) == 1
                    assert bale_records[0].asset_ref == "bale_mirrored_file_id_999"
                    assert bale_records[0].page_number == 1
                    assert bale_records[0].kind == "VIDEO"

                    # Check admin was notified
                    bot.send_message.assert_awaited_once()
                    call_args = bot.send_message.call_args[1]
                    assert call_args["chat_id"] == 5490508090
                    assert "بله" in call_args["text"]


@pytest.mark.asyncio
async def test_mirror_devotional_media_to_bale_graceful_degradation():
    """Verify mirror_devotional_media_to_bale does not raise on error and informs admin."""
    with patch("khatmsaz.modules.content.migrator.get_settings") as mock_settings:
        mock_settings.return_value.bale_bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"
        mock_settings.return_value.bale_media_storage_chat_id = 1499052236

        with patch("khatmsaz.bot.bale.client.build_bale_bot") as mock_build_bale:
            mock_build_bale.return_value = AsyncMock()

            with patch("khatmsaz.modules.content.migrator.TelegramToBaleMigrator") as mock_migrator_cls:
                instance = MagicMock()
                instance.download_asset_bytes = AsyncMock(side_effect=RuntimeError("Telegram timeout"))
                mock_migrator_cls.return_value = instance

                bot = AsyncMock()
                result = await mirror_devotional_media_to_bale(
                    slug="ziyarat-ashura",
                    kind="AUDIO",
                    page_number=1,
                    asset_ref="tg_audio_id",
                    notify_chat_id=5490508090,
                    bot=bot,
                )

                assert result is None
                bot.send_message.assert_awaited_once()
                call_text = bot.send_message.call_args[1]["text"]
                assert "خطا" in call_text


def test_append_media_result_subclasses_str():
    """Verify AppendMediaResult behaves as a string and carries media metadata."""
    dummy_media = DevotionalMedia(
        id=new_id(),
        devotional_asset_id="asset_1",
        kind="VIDEO",
        asset_ref="vid_123",
        asset_platform="TELEGRAM",
        page_number=3,
    )
    result = AppendMediaResult("VIDEO (بخش 3)", dummy_media)

    assert isinstance(result, str)
    assert result == "VIDEO (بخش 3)"
    assert f"Status: {result}" == "Status: VIDEO (بخش 3)"
    assert bool(result) is True
    assert result.media is dummy_media
    assert result.media.page_number == 3


@pytest.mark.asyncio
async def test_set_video_direct_triggers_mirroring_on_telegram():
    """Verify /set_video triggers mirror_devotional_media_to_bale on Telegram."""
    from khatmsaz.bot.handlers.manage_content import set_video_direct

    msg = MagicMock()
    msg.reply_to_message = MagicMock()
    msg.reply_to_message.video = MagicMock(file_id="vid_tg_111")
    msg.reply_to_message.caption = "جلسه اول"
    msg.bot = AsyncMock()
    msg.bot.khatmsaz_platform = Platform.TELEGRAM
    msg.chat.id = 5490508090
    msg.answer = AsyncMock()

    cmd = MagicMock()
    cmd.args = "khutbah-fadakiah 1"

    fake_db = FakeSession()
    with patch("khatmsaz.bot.handlers.manage_content.session_scope") as mock_scope:
        mock_scope.return_value.__aenter__.return_value = fake_db
        with patch("khatmsaz.bot.handlers.manage_content.mirror_devotional_media_to_bale") as mock_mirror:
            mock_mirror.return_value = "bale_fid_test"
            await set_video_direct(msg, cmd)

            # Give event loop a micro-tick for background task
            await asyncio.sleep(0.01)
            mock_mirror.assert_called_once()
            call_kw = mock_mirror.call_args[1]
            assert call_kw["slug"] == "khutbah-fadakiah"
            assert call_kw["kind"] == "VIDEO"
            assert call_kw["page_number"] == 1
            assert call_kw["asset_ref"] == "vid_tg_111"
            assert call_kw["notify_chat_id"] == 5490508090

