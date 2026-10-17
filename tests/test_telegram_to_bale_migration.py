"""Unit tests for Telegram-to-Bale media migration service and CLI."""

from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Audio, Message, PhotoSize

from khatmsaz.core.ids import new_id
from khatmsaz.modules.content.migrator import (
    MigrationStats,
    TelegramToBaleMigrator,
    get_bale_devotional_coverage,
    get_bale_quran_coverage,
)
from khatmsaz.modules.content.models import (
    DevotionalMedia,
    QuranAssetKind,
    QuranPageAsset,
)
from khatmsaz.modules.khatm.quran_editions import CANONICAL_QURAN_EDITION_ID


class FakeResult:
    def __init__(self, items):
        self._items = list(items)

    def scalars(self):
        return self

    def all(self):
        return list(self._items)

    def __iter__(self):
        return iter(self._items)


class FakeSession:
    """In-memory mock SQLAlchemy AsyncSession for migration unit tests."""

    def __init__(self, quran_assets=None, devotional_media=None):
        self.quran_assets: list[QuranPageAsset] = list(quran_assets or [])
        self.devotional_media: list[DevotionalMedia] = list(devotional_media or [])
        self.added = []

    def add(self, obj):
        self.added.append(obj)
        if isinstance(obj, QuranPageAsset):
            self.quran_assets.append(obj)
        elif isinstance(obj, DevotionalMedia):
            self.devotional_media.append(obj)

    async def flush(self):
        pass

    async def execute(self, statement):
        try:
            params = statement.compile().params
        except Exception:
            params = {}

        platform_filter = None
        for val in params.values():
            if val in ("BALE", "TELEGRAM"):
                platform_filter = val
                break

        page_filter = None
        page_between = None
        for k, val in params.items():
            if "page_number" in k and isinstance(val, int):
                page_filter = val

        if "page_number_1" in params and "page_number_2" in params:
            page_between = (params["page_number_1"], params["page_number_2"])

        kind_filter = None
        for val in params.values():
            if isinstance(val, QuranAssetKind):
                kind_filter = val.value
            elif str(val) in ("IMAGE", "AUDIO", "PDF", "DOCUMENT"):
                kind_filter = str(val)

        stmt_str = str(statement).lower()
        if "quran_page_assets" in stmt_str:
            matching = list(self.quran_assets)
            if platform_filter:
                matching = [a for a in matching if a.asset_platform == platform_filter]
            if page_between:
                matching = [a for a in matching if page_between[0] <= a.page_number <= page_between[1]]
            elif page_filter is not None:
                matching = [a for a in matching if a.page_number == page_filter]
            if kind_filter:
                matching = [a for a in matching if (getattr(a.kind, "value", a.kind) == kind_filter)]
            return FakeResult(matching)

        if "devotional_media" in stmt_str:
            matching = list(self.devotional_media)
            if platform_filter:
                matching = [m for m in matching if m.asset_platform == platform_filter]
            if kind_filter:
                matching = [m for m in matching if m.kind == kind_filter]
            return FakeResult(matching)

        return FakeResult([])

    async def scalar(self, statement):
        res = await self.execute(statement)
        items = res.all()
        return items[0] if items else None


@pytest.mark.asyncio
async def test_bale_quran_coverage_empty_and_filled():
    session = FakeSession()
    cov = await get_bale_quran_coverage(session)
    assert cov["image_count"] == 0
    assert cov["audio_count"] == 0
    assert cov["ready"] is False
    assert len(cov["missing_images"]) == 604

    # Seed 1 image and 1 audio for BALE
    session.add(
        QuranPageAsset(
            id=new_id(),
            edition_id=CANONICAL_QURAN_EDITION_ID,
            page_number=1,
            kind=QuranAssetKind.IMAGE,
            reciter_id="",
            asset_ref="bale_fid_p1_img",
            asset_platform="BALE",
        )
    )
    session.add(
        QuranPageAsset(
            id=new_id(),
            edition_id=CANONICAL_QURAN_EDITION_ID,
            page_number=1,
            kind=QuranAssetKind.AUDIO,
            reciter_id="parhizgar",
            asset_ref="bale_fid_p1_audio",
            asset_platform="BALE",
        )
    )

    cov_updated = await get_bale_quran_coverage(session)
    assert cov_updated["image_count"] == 1
    assert cov_updated["audio_count"] == 1
    assert 1 not in cov_updated["missing_images"]
    assert 1 not in cov_updated["missing_audio"]


@pytest.mark.asyncio
async def test_bale_devotional_coverage():
    session = FakeSession()
    session.add(
        DevotionalMedia(
            id=new_id(),
            devotional_asset_id=new_id(),
            kind="AUDIO",
            reciter_id="reciter_1",
            page_number=0,
            asset_ref="tg_audio_ref",
            asset_platform="TELEGRAM",
        )
    )
    cov1 = await get_bale_devotional_coverage(session)
    assert cov1["telegram_media_count"] == 1
    assert cov1["bale_media_count"] == 0

    session.add(
        DevotionalMedia(
            id=new_id(),
            devotional_asset_id=new_id(),
            kind="AUDIO",
            reciter_id="reciter_1",
            page_number=0,
            asset_ref="bale_audio_ref",
            asset_platform="BALE",
        )
    )
    cov2 = await get_bale_devotional_coverage(session)
    assert cov2["bale_media_count"] == 1


@pytest.mark.asyncio
async def test_migrator_dry_run():
    session = FakeSession()
    migrator = TelegramToBaleMigrator(
        tg_bot=None,
        bale_bot=None,
        bale_storage_chat_id=-100999,
        dry_run=True,
        delay_seconds=0.0,
    )

    stats_img = await migrator.migrate_quran_images(session, limit=3)
    assert stats_img.total == 3
    assert stats_img.migrated == 3
    assert stats_img.failed == 0

    stats_audio = await migrator.migrate_quran_audio(session, limit=2)
    assert stats_audio.total == 2
    assert stats_audio.migrated > 0
    assert stats_audio.failed == 0


@pytest.mark.asyncio
async def test_migrator_mocked_upload_and_idempotency():
    mock_tg_bot = MagicMock()
    mock_bale_bot = MagicMock()

    async def fake_download(file_id, destination):
        destination.write(b"fake_file_content_12345")

    mock_tg_bot.download = AsyncMock(side_effect=fake_download)

    mock_fwd_msg = MagicMock(spec=Message)
    mock_fwd_msg.message_id = 9999
    mock_photo = MagicMock(spec=PhotoSize)
    mock_photo.file_id = "tg_photo_fid_1"
    mock_fwd_msg.photo = [mock_photo]
    mock_fwd_msg.audio = None
    mock_fwd_msg.voice = None
    mock_fwd_msg.document = None

    mock_tg_bot.forward_message = AsyncMock(return_value=mock_fwd_msg)
    mock_tg_bot.delete_message = AsyncMock()

    mock_bale_sent_msg = MagicMock(spec=Message)
    mock_bale_photo = MagicMock(spec=PhotoSize)
    mock_bale_photo.file_id = "bale_photo_fid_abc_123"
    mock_bale_sent_msg.photo = [mock_bale_photo]
    mock_bale_bot.send_photo = AsyncMock(return_value=mock_bale_sent_msg)

    session = FakeSession()
    migrator = TelegramToBaleMigrator(
        tg_bot=mock_tg_bot,
        bale_bot=mock_bale_bot,
        bale_storage_chat_id=-10012345,
        tg_scratch_chat_id=-1009999,
        delay_seconds=0.0,
        dry_run=False,
    )

    # 1. Run migration for page 1
    stats = await migrator.migrate_quran_images(session, limit=1)
    assert stats.migrated == 1
    assert stats.failed == 0

    # Verify registered in session
    saved = [a for a in session.quran_assets if a.page_number == 1 and a.asset_platform == "BALE"]
    assert len(saved) == 1
    assert saved[0].asset_ref == "bale_photo_fid_abc_123"

    # 2. Idempotency test: Run again
    mock_bale_bot.send_photo.reset_mock()
    stats2 = await migrator.migrate_quran_images(session, limit=1)
    assert stats2.migrated == 0
    assert stats2.skipped == 1
    mock_bale_bot.send_photo.assert_not_called()


@pytest.mark.asyncio
async def test_migrator_devotional_media_mocked():
    session = FakeSession()
    dev_id = new_id()
    tg_item = DevotionalMedia(
        id=new_id(),
        devotional_asset_id=dev_id,
        kind="AUDIO",
        reciter_id="reciter_1",
        reciter_label="استاد تستی",
        page_number=0,
        asset_ref="tg_audio_ref_999",
        asset_platform="TELEGRAM",
    )
    session.add(tg_item)

    mock_tg_bot = MagicMock()
    async def fake_download(file_id, destination):
        destination.write(b"fake_audio_bytes")
    mock_tg_bot.download = AsyncMock(side_effect=fake_download)

    mock_bale_bot = MagicMock()
    mock_bale_msg = MagicMock(spec=Message)
    mock_bale_audio = MagicMock(spec=Audio)
    mock_bale_audio.file_id = "bale_audio_fid_777"
    mock_bale_msg.audio = mock_bale_audio
    mock_bale_bot.send_audio = AsyncMock(return_value=mock_bale_msg)

    migrator = TelegramToBaleMigrator(
        tg_bot=mock_tg_bot,
        bale_bot=mock_bale_bot,
        bale_storage_chat_id=-1008888,
        delay_seconds=0.0,
        dry_run=False,
    )

    stats = await migrator.migrate_devotional_media(session)
    assert stats.migrated == 1
    assert stats.failed == 0

    bale_saved = [m for m in session.devotional_media if m.asset_platform == "BALE"]
    assert len(bale_saved) == 1
    assert bale_saved[0].asset_ref == "bale_audio_fid_777"


@pytest.mark.asyncio
async def test_migrator_handles_errors_gracefully():
    session = FakeSession()
    mock_tg_bot = MagicMock()
    mock_tg_bot.forward_message = AsyncMock(side_effect=RuntimeError("Network error"))

    migrator = TelegramToBaleMigrator(
        tg_bot=mock_tg_bot,
        bale_bot=MagicMock(),
        bale_storage_chat_id=-100111,
        tg_scratch_chat_id=-100222,
        delay_seconds=0.0,
        dry_run=False,
    )

    stats = await migrator.migrate_quran_images(session, limit=2)
    assert stats.failed == 2
    assert len(stats.errors) == 2
    assert "Network error" in stats.errors[0]


def test_migration_stats_summary():
    stats = MigrationStats(total=10, migrated=7, skipped=2, failed=1)
    summary = stats.summary()
    assert "Total: 10" in summary
    assert "Migrated: 7" in summary
    assert "Skipped (already exists): 2" in summary
    assert "Failed: 1" in summary
