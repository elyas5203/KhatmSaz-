"""CLI runner for automated media migration from Telegram to Bale.

Usage:
    # Dry-run test (no real uploads):
    python scripts/migrate_telegram_to_bale.py --dry-run --target all

    # Live migration with specified Bale storage chat:
    python scripts/migrate_telegram_to_bale.py --storage-chat-id -1001234567890 --target quran

    # Limit migration to first 5 items per category for testing:
    python scripts/migrate_telegram_to_bale.py --limit 5 --target all
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from khatmsaz.bot.bale.client import build_bale_bot
from khatmsaz.bot.telegram.client import build_telegram_bot
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.modules.content.migrator import TelegramToBaleMigrator, get_bale_quran_coverage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("telegram_to_bale_migrator")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate Quran and devotional assets from Telegram to Bale."
    )
    parser.add_argument(
        "--target",
        choices=["all", "quran", "quran-images", "quran-audio", "devotionals"],
        default="all",
        help="Target content category to migrate (default: all).",
    )
    parser.add_argument(
        "--storage-chat-id",
        type=int,
        default=None,
        help="Bale storage channel/chat ID where media is uploaded to generate file_ids.",
    )
    parser.add_argument(
        "--scratch-chat-id",
        type=int,
        default=None,
        help="Telegram scratch chat/channel ID used to forward and inspect channel posts.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between Bale upload requests to respect rate limits (default: 0.5s).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of items to migrate per category (useful for testing).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without downloading from Telegram or uploading to Bale.",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    settings = get_settings()

    storage_chat_id = args.storage_chat_id or settings.bale_media_storage_chat_id or 1499052236
    scratch_chat_id = args.scratch_chat_id or settings.telegram_scratch_chat_id

    logger.info("Initializing bot clients...")
    tg_bot = None
    bale_bot = None

    if not args.dry_run:
        try:
            tg_bot = build_telegram_bot()
            bale_bot = build_bale_bot()
        except Exception as exc:
            logger.error("Failed to construct bot clients: %s", exc)
            return 1

    def progress_printer(stage: str, current: int, total: int) -> None:
        pct = (current / total * 100) if total else 0
        sys.stdout.write(f"\r[{stage}] {current}/{total} ({pct:.1f}%)")
        sys.stdout.flush()
        if current >= total:
            sys.stdout.write("\n")

    migrator = TelegramToBaleMigrator(
        tg_bot=tg_bot,
        bale_bot=bale_bot,
        bale_storage_chat_id=storage_chat_id or 0,
        tg_scratch_chat_id=scratch_chat_id,
        delay_seconds=args.delay,
        dry_run=args.dry_run,
        progress_callback=progress_printer,
    )

    logger.info("Starting migration (target=%s, dry_run=%s)...", args.target, args.dry_run)

    try:
        async with session_scope() as session:
            if args.target in ("all", "quran", "quran-images"):
                logger.info("Migrating Quran images (604 pages)...")
                stats_images = await migrator.migrate_quran_images(session, limit=args.limit)
                logger.info("Quran Images: %s", stats_images.summary())

            if args.target in ("all", "quran", "quran-audio"):
                logger.info("Migrating Quran audio (Parhizgar)...")
                stats_audio = await migrator.migrate_quran_audio(session, limit=args.limit)
                logger.info("Quran Audio: %s", stats_audio.summary())

            if args.target in ("all", "devotionals"):
                logger.info("Migrating Devotionals, Ziyarat and Khutbahs...")
                stats_dev = await migrator.migrate_devotional_media(session, limit=args.limit)
                logger.info("Devotionals: %s", stats_dev.summary())

            # Print final coverage summary
            cov = await get_bale_quran_coverage(session)
            logger.info(
                "Final Bale Quran Coverage: %d/604 images, %d/604 audio. Ready: %s",
                cov["image_count"],
                cov["audio_count"],
                cov["ready"],
            )

        logger.info("Migration finished successfully.")
        return 0
    finally:
        if tg_bot and tg_bot.session:
            await tg_bot.session.close()
        if bale_bot and bale_bot.session:
            await bale_bot.session.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
