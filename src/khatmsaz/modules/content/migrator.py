"""Automated cross-platform media migration service (Telegram -> Bale).

Reads canonical Quran pages/audio and registered devotional/khutbah assets from
Telegram, uploads them to a dedicated Bale storage chat/channel, extracts the
resulting Bale file_id, and registers the assets with asset_platform="BALE".
"""

from __future__ import annotations

import asyncio
import io
import logging
from dataclasses import dataclass, field
from typing import Callable

from aiogram import Bot
from aiogram.types import BufferedInputFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.content.models import (
    DevotionalAsset,
    DevotionalMedia,
    QuranAssetKind,
    QuranPageAsset,
)
from khatmsaz.modules.content.quran_channel_seed import (
    AUDIO_MESSAGE_RANGES,
    IMAGE_MESSAGE_IDS,
    SOURCE_CHAT_ID,
)
from khatmsaz.modules.khatm.quran_editions import CANONICAL_QURAN_EDITION_ID

logger = logging.getLogger(__name__)


@dataclass
class MigrationStats:
    total: int = 0
    migrated: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Total: {self.total} | Migrated: {self.migrated} | "
            f"Skipped (already exists): {self.skipped} | Failed: {self.failed}"
        )


async def get_bale_quran_coverage(session: AsyncSession) -> dict[str, object]:
    """Return exact 604-page coverage and missing pages for Bale Quran assets."""
    result = await session.execute(
        select(QuranPageAsset).where(
            QuranPageAsset.edition_id == CANONICAL_QURAN_EDITION_ID,
            QuranPageAsset.asset_platform == "BALE",
        )
    )
    image_pages: set[int] = set()
    audio_pages: set[int] = set()
    for row in result.scalars():
        if row.kind == QuranAssetKind.IMAGE:
            image_pages.add(row.page_number)
        elif row.kind == QuranAssetKind.AUDIO:
            audio_pages.add(row.page_number)
    all_pages = set(range(1, 605))
    return {
        "image_count": len(image_pages),
        "audio_count": len(audio_pages),
        "missing_images": sorted(all_pages - image_pages),
        "missing_audio": sorted(all_pages - audio_pages),
        "ready": (image_pages == all_pages and audio_pages == all_pages),
    }


async def get_bale_devotional_coverage(session: AsyncSession) -> dict[str, int]:
    """Return counts of devotional media registered on Telegram vs Bale."""
    tg_count = await session.scalar(
        select(DevotionalMedia.id).where(DevotionalMedia.asset_platform == "TELEGRAM")
    )
    bale_count = await session.scalar(
        select(DevotionalMedia.id).where(DevotionalMedia.asset_platform == "BALE")
    )
    return {
        "telegram_media_count": len(
            (
                await session.execute(
                    select(DevotionalMedia).where(DevotionalMedia.asset_platform == "TELEGRAM")
                )
            ).scalars().all()
        ),
        "bale_media_count": len(
            (
                await session.execute(
                    select(DevotionalMedia).where(DevotionalMedia.asset_platform == "BALE")
                )
            ).scalars().all()
        ),
    }


class TelegramToBaleMigrator:
    """Core engine for streaming media from Telegram and registering on Bale."""

    def __init__(
        self,
        tg_bot: Bot | None,
        bale_bot: Bot | None,
        bale_storage_chat_id: int,
        tg_scratch_chat_id: int | None = None,
        delay_seconds: float = 0.5,
        dry_run: bool = False,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> None:
        self.tg_bot = tg_bot
        self.bale_bot = bale_bot
        self.bale_storage_chat_id = bale_storage_chat_id
        self.tg_scratch_chat_id = tg_scratch_chat_id
        if not self.tg_scratch_chat_id:
            settings = get_settings()
            if settings.telegram_scratch_chat_id:
                self.tg_scratch_chat_id = settings.telegram_scratch_chat_id
            else:
                for x in settings.super_admin_telegram_chat_ids.split(","):
                    if x.strip().isdigit() or (x.strip().startswith("-") and x.strip()[1:].isdigit()):
                        self.tg_scratch_chat_id = int(x.strip())
                        break
        self.delay_seconds = delay_seconds
        self.dry_run = dry_run
        self.progress_callback = progress_callback

    def _notify_progress(self, stage: str, current: int, total: int) -> None:
        if self.progress_callback:
            try:
                self.progress_callback(stage, current, total)
            except Exception:
                logger.warning("Progress callback raised an exception", exc_info=True)

    async def download_telegram_file_bytes(self, file_id: str) -> bytes:
        """Download raw file bytes from Telegram given a file_id."""
        if not self.tg_bot:
            raise RuntimeError("Telegram bot instance is required for downloading")
        buffer = io.BytesIO()
        await self.tg_bot.download(file_id, destination=buffer)
        return buffer.getvalue()

    async def fetch_channel_message_bytes(
        self, source_chat_id: int | str, source_message_id: int
    ) -> tuple[bytes, str, str]:
        """Forward a channel post to scratch chat to obtain file bytes and kind.

        Returns (file_bytes, kind, filename).
        """
        if not self.tg_bot:
            raise RuntimeError("Telegram bot instance is required for downloading")
        if not self.tg_scratch_chat_id:
            raise RuntimeError("Telegram scratch chat id is required to inspect channel posts")

        # Forward message to scratch chat where the bot can read its file_id
        fwd = await self.tg_bot.forward_message(
            chat_id=self.tg_scratch_chat_id,
            from_chat_id=source_chat_id,
            message_id=source_message_id,
        )

        kind = "DOCUMENT"
        file_id = ""
        filename = f"media_{source_message_id}"

        try:
            if fwd.photo:
                kind = "IMAGE"
                file_id = fwd.photo[-1].file_id
                filename = f"page_{source_message_id}.jpg"
            elif fwd.video:
                kind = "VIDEO"
                file_id = fwd.video.file_id
                filename = fwd.video.file_name or f"video_{source_message_id}.mp4"
            elif fwd.audio:
                kind = "AUDIO"
                file_id = fwd.audio.file_id
                filename = fwd.audio.file_name or f"audio_{source_message_id}.mp3"
            elif fwd.voice:
                kind = "AUDIO"
                file_id = fwd.voice.file_id
                filename = f"voice_{source_message_id}.ogg"
            elif fwd.document:
                kind = "PDF" if fwd.document.mime_type == "application/pdf" else "DOCUMENT"
                file_id = fwd.document.file_id
                filename = fwd.document.file_name or f"doc_{source_message_id}.pdf"
            else:
                raise ValueError(f"Message {source_message_id} contains no recognizable media")

            file_bytes = await self.download_telegram_file_bytes(file_id)
            return file_bytes, kind, filename
        finally:
            # Clean up the scratch chat message
            try:
                await self.tg_bot.delete_message(
                    chat_id=self.tg_scratch_chat_id, message_id=fwd.message_id
                )
            except Exception:
                pass

    async def download_asset_bytes(
        self, asset_ref: str, fallback_kind: str = "DOCUMENT"
    ) -> tuple[bytes, str, str]:
        """Download bytes for an asset_ref, supporting both direct file_id and tg_forward:@channel:id.

        Returns (file_bytes, kind, filename).
        """
        if asset_ref.startswith("tg_forward:"):
            parts = asset_ref.split(":")
            if len(parts) >= 3:
                channel = parts[1]
                mid = int(parts[2])
                ch_id: int | str = (
                    int(channel)
                    if (channel.isdigit() or (channel.startswith("-") and channel[1:].isdigit()))
                    else channel
                )
                return await self.fetch_channel_message_bytes(ch_id, mid)
            raise ValueError(f"Malformed tg_forward reference: {asset_ref}")

        file_bytes = await self.download_telegram_file_bytes(asset_ref)
        ext = (
            "mp4"
            if fallback_kind.upper() == "VIDEO"
            else (
                "jpg"
                if fallback_kind.upper() == "IMAGE"
                else ("mp3" if fallback_kind.upper() == "AUDIO" else "pdf")
            )
        )
        filename = f"media.{ext}"
        return file_bytes, fallback_kind, filename

    async def upload_to_bale(
        self,
        file_bytes: bytes,
        kind: str,
        filename: str,
        caption: str | None = None,
    ) -> str:
        """Upload raw file bytes to Bale storage chat and extract the Bale file_id."""
        if self.dry_run:
            return f"mock_bale_file_id_{filename}"
        if not self.bale_bot:
            raise RuntimeError("Bale bot instance is required for uploading")

        input_file = BufferedInputFile(file_bytes, filename=filename)
        kind_upper = kind.upper()

        if kind_upper == "IMAGE":
            msg = await self.bale_bot.send_photo(
                chat_id=self.bale_storage_chat_id,
                photo=input_file,
                caption=caption,
            )
            if not msg.photo:
                raise RuntimeError("Bale send_photo returned message without photo attribute")
            file_id = msg.photo[-1].file_id
        elif kind_upper == "AUDIO":
            msg = await self.bale_bot.send_audio(
                chat_id=self.bale_storage_chat_id,
                audio=input_file,
                caption=caption,
            )
            if not msg.audio:
                raise RuntimeError("Bale send_audio returned message without audio attribute")
            file_id = msg.audio.file_id
        elif kind_upper == "VIDEO":
            msg = await self.bale_bot.send_video(
                chat_id=self.bale_storage_chat_id,
                video=input_file,
                caption=caption,
            )
            if msg.video:
                file_id = msg.video.file_id
            elif msg.document:
                file_id = msg.document.file_id
            else:
                raise RuntimeError("Bale send_video returned message without video or document attribute")
        else:  # PDF or generic document
            msg = await self.bale_bot.send_document(
                chat_id=self.bale_storage_chat_id,
                document=input_file,
                caption=caption,
            )
            if not msg.document:
                raise RuntimeError("Bale send_document returned message without document attribute")
            file_id = msg.document.file_id

        # Delete temporary upload message in Bale to keep storage chat clean
        try:
            await self.bale_bot.delete_message(
                chat_id=self.bale_storage_chat_id,
                message_id=msg.message_id,
            )
        except Exception:
            pass

        if self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)

        return file_id

    async def migrate_quran_images(
        self,
        session: AsyncSession,
        limit: int | None = None,
    ) -> MigrationStats:
        """Migrate all 604 Quran page images from Telegram channel to Bale."""
        stats = MigrationStats(total=len(IMAGE_MESSAGE_IDS))
        pages_to_process = list(enumerate(IMAGE_MESSAGE_IDS, start=1))
        if limit:
            pages_to_process = pages_to_process[:limit]
            stats.total = len(pages_to_process)

        for page, msg_id in pages_to_process:
            self._notify_progress("quran_images", page, stats.total)
            # 1. Check idempotency: does this page image already exist for BALE?
            existing = await session.scalar(
                select(QuranPageAsset).where(
                    QuranPageAsset.edition_id == CANONICAL_QURAN_EDITION_ID,
                    QuranPageAsset.page_number == page,
                    QuranPageAsset.kind == QuranAssetKind.IMAGE,
                    QuranPageAsset.asset_platform == "BALE",
                )
            )
            if existing and existing.asset_ref.strip():
                stats.skipped += 1
                continue

            if self.dry_run:
                stats.migrated += 1
                continue

            try:
                # 2. Download from Telegram
                file_bytes, _, filename = await self.fetch_channel_message_bytes(
                    SOURCE_CHAT_ID, msg_id
                )
                # 3. Upload to Bale
                bale_file_id = await self.upload_to_bale(
                    file_bytes,
                    kind="IMAGE",
                    filename=filename or f"quran_page_{page}.jpg",
                    caption=f"صفحه {page} قرآن کریم",
                )

                # 4. Save into database
                if existing:
                    existing.asset_ref = bale_file_id
                else:
                    await content_service.register_quran_page_asset(
                        session,
                        edition_id=CANONICAL_QURAN_EDITION_ID,
                        page_number=page,
                        kind=QuranAssetKind.IMAGE,
                        asset_ref=bale_file_id,
                        asset_platform="BALE",
                    )
                await session.flush()
                stats.migrated += 1
            except Exception as exc:
                err = f"Failed migrating Quran image page {page} (msg {msg_id}): {exc}"
                logger.error(err, exc_info=True)
                stats.failed += 1
                stats.errors.append(err)

        return stats

    async def migrate_quran_audio(
        self,
        session: AsyncSession,
        reciter_id: str = "parhizgar",
        limit: int | None = None,
    ) -> MigrationStats:
        """Migrate Quran audio ranges from Telegram channel to Bale."""
        stats = MigrationStats(total=len(AUDIO_MESSAGE_RANGES))
        ranges_to_process = list(AUDIO_MESSAGE_RANGES)
        if limit:
            ranges_to_process = ranges_to_process[:limit]
            stats.total = len(ranges_to_process)

        for idx, (page_start, page_end, msg_id) in enumerate(ranges_to_process, start=1):
            self._notify_progress("quran_audio", idx, stats.total)
            # Check idempotency: do all pages in this range have BALE audio?
            existing_rows = (
                await session.execute(
                    select(QuranPageAsset).where(
                        QuranPageAsset.edition_id == CANONICAL_QURAN_EDITION_ID,
                        QuranPageAsset.page_number.between(page_start, page_end),
                        QuranPageAsset.kind == QuranAssetKind.AUDIO,
                        QuranPageAsset.reciter_id == reciter_id,
                        QuranPageAsset.asset_platform == "BALE",
                    )
                )
            ).scalars().all()

            covered_pages = {row.page_number for row in existing_rows if row.asset_ref.strip()}
            required_pages = set(range(page_start, page_end + 1))
            if covered_pages == required_pages:
                stats.skipped += 1
                continue

            if self.dry_run:
                stats.migrated += len(range(page_start, page_end + 1))
                continue

            try:
                file_bytes, _, filename = await self.fetch_channel_message_bytes(
                    SOURCE_CHAT_ID, msg_id
                )
                caption = (
                    f"صوت صفحه {page_start} قرآن کریم"
                    if page_start == page_end
                    else f"صوت صفحات {page_start} تا {page_end} قرآن کریم"
                )
                bale_file_id = await self.upload_to_bale(
                    file_bytes,
                    kind="AUDIO",
                    filename=filename or f"quran_audio_{page_start}_{page_end}.mp3",
                    caption=caption,
                )

                # Persist for every page in this audio range
                for page in range(page_start, page_end + 1):
                    row = await session.scalar(
                        select(QuranPageAsset).where(
                            QuranPageAsset.edition_id == CANONICAL_QURAN_EDITION_ID,
                            QuranPageAsset.page_number == page,
                            QuranPageAsset.kind == QuranAssetKind.AUDIO,
                            QuranPageAsset.reciter_id == reciter_id,
                            QuranPageAsset.asset_platform == "BALE",
                        )
                    )
                    if row is None:
                        await content_service.register_quran_page_asset(
                            session,
                            edition_id=CANONICAL_QURAN_EDITION_ID,
                            page_number=page,
                            kind=QuranAssetKind.AUDIO,
                            reciter_id=reciter_id,
                            asset_ref=bale_file_id,
                            asset_platform="BALE",
                        )
                    else:
                        row.asset_ref = bale_file_id

                await session.flush()
                stats.migrated += 1
            except Exception as exc:
                err = f"Failed migrating Quran audio range {page_start}-{page_end} (msg {msg_id}): {exc}"
                logger.error(err, exc_info=True)
                stats.failed += 1
                stats.errors.append(err)

        return stats

    async def migrate_devotional_media(
        self,
        session: AsyncSession,
        limit: int | None = None,
    ) -> MigrationStats:
        """Migrate all registered DevotionalMedia and legacy DevotionalAssets to Bale."""
        tg_items = (
            await session.execute(
                select(DevotionalMedia)
                .where(DevotionalMedia.asset_platform == "TELEGRAM")
                .order_by(DevotionalMedia.created_at)
            )
        ).scalars().all()

        stats = MigrationStats(total=len(tg_items))
        items_to_process = list(tg_items)
        if limit:
            items_to_process = items_to_process[:limit]
            stats.total = len(items_to_process)

        for idx, item in enumerate(items_to_process, start=1):
            self._notify_progress("devotionals", idx, stats.total)
            # 1. Check if corresponding Bale record already exists
            existing_bale = await session.scalar(
                select(DevotionalMedia).where(
                    DevotionalMedia.devotional_asset_id == item.devotional_asset_id,
                    DevotionalMedia.kind == item.kind,
                    DevotionalMedia.reciter_id == item.reciter_id,
                    DevotionalMedia.page_number == item.page_number,
                    DevotionalMedia.asset_platform == "BALE",
                )
            )
            if existing_bale and existing_bale.asset_ref.strip():
                stats.skipped += 1
                continue

            if self.dry_run:
                stats.migrated += 1
                continue

            try:
                # 2. Download from Telegram (supporting file_id and tg_forward)
                file_bytes, _, _ = await self.download_asset_bytes(
                    item.asset_ref, fallback_kind=item.kind
                )
                ext = (
                    "mp4"
                    if item.kind == "VIDEO"
                    else ("jpg" if item.kind == "IMAGE" else ("mp3" if item.kind == "AUDIO" else "pdf"))
                )
                filename = f"devotional_{item.devotional_asset_id}_{item.page_number}.{ext}"
                caption = f"{item.kind} {item.reciter_label or ''}".strip()
                # 3. Upload to Bale
                bale_file_id = await self.upload_to_bale(
                    file_bytes,
                    kind=item.kind,
                    filename=filename,
                    caption=caption or None,
                )

                # 4. Save into database
                if existing_bale:
                    existing_bale.asset_ref = bale_file_id
                else:
                    new_media = DevotionalMedia(
                        id=new_id(),
                        devotional_asset_id=item.devotional_asset_id,
                        kind=item.kind,
                        reciter_id=item.reciter_id,
                        reciter_label=item.reciter_label,
                        page_number=item.page_number,
                        asset_ref=bale_file_id,
                        asset_platform="BALE",
                    )
                    session.add(new_media)
                await session.flush()
                stats.migrated += 1
            except Exception as exc:
                err = f"Failed migrating devotional media {item.id} ({item.kind}): {exc}"
                logger.error(err, exc_info=True)
                stats.failed += 1
                stats.errors.append(err)

        return stats

    async def migrate_all(
        self,
        session: AsyncSession,
        limit_per_category: int | None = None,
    ) -> dict[str, MigrationStats]:
        """Run complete migration pipeline across Quran images, Quran audio, and devotionals."""
        quran_images_stats = await self.migrate_quran_images(session, limit=limit_per_category)
        quran_audio_stats = await self.migrate_quran_audio(session, limit=limit_per_category)
        devotional_stats = await self.migrate_devotional_media(session, limit=limit_per_category)

        return {
            "quran_images": quran_images_stats,
            "quran_audio": quran_audio_stats,
            "devotionals": devotional_stats,
        }


async def mirror_devotional_media_to_bale(
    slug: str,
    kind: str,
    page_number: int | None,
    asset_ref: str,
    caption: str | None = None,
    reciter_id: str | None = None,
    reciter_label: str | None = None,
    notify_chat_id: int | None = None,
    bot: Bot | None = None,
) -> str | None:
    """Real-time background mirroring of newly registered Telegram media to Bale (MASTER-16).

    1. Checks if Bale bot and Bale storage chat are configured.
    2. Downloads media bytes from Telegram (file_id or tg_forward channel link).
    3. Uploads to Bale storage chat and extracts the Bale file_id.
    4. Deletes the temporary message in Bale storage chat.
    5. Saves or updates record in DevotionalMedia with asset_platform='BALE'.
    6. Gracefully logs and informs admin without disrupting Telegram flow.
    """
    settings = get_settings()
    if not settings.bale_bot_token or not settings.bale_media_storage_chat_id:
        logger.info(
            "Skipping Bale mirroring for %s (%s): Bale bot token or storage chat ID not configured",
            slug,
            kind,
        )
        return None

    try:
        from khatmsaz.bot.bale.client import build_bale_bot
        from khatmsaz.bot.telegram.client import build_telegram_bot
        from khatmsaz.core.bot_registry import get_registry

        try:
            reg = get_registry()
        except RuntimeError:
            reg = None
        tg_bot = (reg.get_creator_bot(Platform.TELEGRAM) if reg else None) or bot
        if not tg_bot:
            tg_bot = build_telegram_bot()

        bale_bot = reg.get_creator_bot(Platform.BALE) if reg else None
        if not bale_bot:
            bale_bot = build_bale_bot()

        migrator = TelegramToBaleMigrator(
            tg_bot=tg_bot,
            bale_bot=bale_bot,
            bale_storage_chat_id=settings.bale_media_storage_chat_id,
        )

        file_bytes, _, _ = await migrator.download_asset_bytes(asset_ref, fallback_kind=kind)
        ext = (
            "mp4"
            if kind.upper() == "VIDEO"
            else (
                "jpg"
                if kind.upper() == "IMAGE"
                else ("mp3" if kind.upper() == "AUDIO" else "pdf")
            )
        )
        filename = f"devotional_{slug}_{page_number or 1}.{ext}"

        bale_file_id = await migrator.upload_to_bale(
            file_bytes=file_bytes,
            kind=kind,
            filename=filename,
            caption=caption or reciter_label,
        )

        async with session_scope() as session:
            asset = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug))
            if not asset:
                title = (
                    "خطبه فدکیه حضرت زهرا (س)"
                    if "fadak" in slug
                    else ("خطبه غدیر پیامبر اکرم (ص)" if "ghadir" in slug else slug)
                )
                asset = DevotionalAsset(
                    id=new_id(),
                    content_type="DUA",
                    slug=slug,
                    title=title,
                    text_body="",
                    enabled=True,
                )
                session.add(asset)
                await session.flush()

            existing_bale = await session.scalar(
                select(DevotionalMedia).where(
                    DevotionalMedia.devotional_asset_id == asset.id,
                    DevotionalMedia.kind == kind.upper(),
                    DevotionalMedia.reciter_id == (reciter_id or ""),
                    DevotionalMedia.page_number == (page_number or 0),
                    DevotionalMedia.asset_platform == "BALE",
                )
            )
            if existing_bale:
                existing_bale.asset_ref = bale_file_id
                if caption or reciter_label:
                    existing_bale.reciter_label = caption or reciter_label
            else:
                new_media = DevotionalMedia(
                    id=new_id(),
                    devotional_asset_id=asset.id,
                    kind=kind.upper(),
                    reciter_id=reciter_id or "",
                    reciter_label=caption or reciter_label,
                    page_number=page_number or 0,
                    asset_ref=bale_file_id,
                    asset_platform="BALE",
                )
                session.add(new_media)
            await session.commit()

        logger.info(
            "Successfully mirrored %s %s (part %s) to Bale: file_id=%s",
            slug,
            kind,
            page_number,
            bale_file_id,
        )

        if notify_chat_id and bot:
            try:
                kind_fa = (
                    "ویدیو"
                    if kind.upper() == "VIDEO"
                    else ("فایل PDF" if kind.upper() == "PDF" else "صوت")
                )
                part_text = f" بخش {page_number}" if page_number else ""
                await bot.send_message(
                    chat_id=notify_chat_id,
                    text=f"🟢 {kind_fa}{part_text} به صورت خودکار در پیام‌رسان بله نیز همگام‌سازی و بارگذاری شد.",
                )
            except Exception:
                pass

        return bale_file_id
    except Exception as exc:
        logger.error(
            "Failed mirroring devotional media %s (%s, part %s) to Bale: %s",
            slug,
            kind,
            page_number,
            exc,
            exc_info=True,
        )
        if notify_chat_id and bot:
            try:
                err_text = str(exc)
                if "file is too big" in err_text.lower():
                    friendly_msg = (
                        "⚠️ <b>عدم امکان همگام‌سازی خودکار در بله به‌دلیل محدودیت حجم تلگرام:</b>\n\n"
                        "سرورهای تلگرام به ربات‌ها اجازه دانلود فایل‌های بالای <b>۲۰ مگابایت</b> را نمی‌دهند.\n\n"
                        "✅ این ویدیو با موفقیت کامل در <b>تلگرام</b> ذخیره شده و برای اعضا فعال است.\n"
                        "🟢 برای پیام‌رسان <b>بله</b>، کافیست همین ویدیو را یک‌بار در بله برای بات ارسال کرده و روی آن دستور زیر را ریپلای فرمایید:\n"
                        f"<code>/set_video {slug} {page_number or 1}</code>"
                    )
                else:
                    friendly_msg = (
                        f"⚠️ همگام‌سازی خودکار در بله با خطا مواجه شد:\n"
                        f"<code>{exc}</code>\n"
                        "محتوا در تلگرام ثبت است و بعداً نیز قابل همگام‌سازی است."
                    )
                await bot.send_message(
                    chat_id=notify_chat_id,
                    text=friendly_msg,
                )
            except Exception:
                pass
        return None

