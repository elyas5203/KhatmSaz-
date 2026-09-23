"""Process entrypoint: `python -m khatmsaz.bootstrap`.

Starts both bots (whichever tokens are configured) on long polling, sharing
one Dispatcher / one set of handlers. Long polling — not a webhook — is a
deliberate choice: it needs no public domain, no reverse proxy, and no
tunnel, which removes the exact failure point the previous TypeScript
deployment got stuck on (see docs/ai/DECISIONS.md, DEC-PY-0001).
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn

from khatmsaz.bot.bale.client import build_bale_bot
from khatmsaz.bot.handlers.admin import router as admin_router
from khatmsaz.bot.handlers.account import router as account_router
from khatmsaz.bot.handlers.account_link import router as account_link_router
from khatmsaz.bot.handlers.change_phone import router as change_phone_router
from khatmsaz.bot.handlers.broadcast import router as broadcast_router
from khatmsaz.bot.handlers.create_khatm import router as create_khatm_router
from khatmsaz.bot.handlers.digest_settings import router as digest_settings_router
from khatmsaz.bot.handlers.devotional import router as devotional_router
from khatmsaz.bot.handlers.creator_decisions import router as creator_decisions_router
from khatmsaz.bot.handlers.join_requests import router as join_requests_router
from khatmsaz.bot.handlers.language_settings import router as language_settings_router
from khatmsaz.bot.handlers.manual_phone_verification import router as manual_phone_verification_router
from khatmsaz.bot.handlers.khatm_request import router as khatm_request_router
from khatmsaz.bot.handlers.leave import router as leave_router
from khatmsaz.bot.handlers.manage_content import router as manage_content_router
from khatmsaz.bot.handlers.my_khatms import router as my_khatms_router
from khatmsaz.bot.handlers.portions import router as portions_router
from khatmsaz.bot.handlers.profile import router as profile_router
from khatmsaz.bot.handlers.font_settings import router as font_settings_router
from khatmsaz.bot.handlers.help import router as help_router
from khatmsaz.bot.handlers.suggestions import router as suggestions_router
from khatmsaz.bot.handlers.content_settings import router as content_settings_router
from khatmsaz.bot.handlers.public_khatms import router as public_khatms_router
from khatmsaz.bot.handlers.reminder_settings import router as reminder_settings_router
from khatmsaz.bot.handlers.registration import router as registration_router
from khatmsaz.bot.handlers.report import router as report_router
from khatmsaz.bot.handlers.settings_menu import router as settings_menu_router
from khatmsaz.bot.handlers.reciter_settings import router as reciter_settings_router
from khatmsaz.bot.handlers.start import router as start_router
from khatmsaz.bot.handlers.sms_settings import router as sms_settings_router
from khatmsaz.bot.handlers.timezone_settings import router as timezone_settings_router
from khatmsaz.bot.handlers.wallet import router as wallet_router
from khatmsaz.bot.middlewares import ModerationMiddleware
from khatmsaz.bot.commands import install_command_menu
from khatmsaz.bot.notify_adapter import build_notify_fn, build_send_quran_pages_fn
from khatmsaz.bot.telegram.client import build_telegram_bot
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.core import runtime_status
from khatmsaz.modules.reminder_engine import service as reminder_engine
from khatmsaz.modules.sms_subscription import service as sms_subscription_service
from khatmsaz.web.app import app as admin_web_app

logger = logging.getLogger("khatmsaz")


def _configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )


async def main() -> None:
    _configure_logging()
    settings = get_settings()

    bots: list[Bot] = []

    if settings.telegram_bot_token:
        bots.append(build_telegram_bot())
        logger.info("Telegram bot configured.")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")

    if settings.bale_bot_token:
        bots.append(build_bale_bot())
        logger.info("Bale bot configured.")
    else:
        logger.warning("BALE_BOT_TOKEN not set — Bale bot disabled.")

    if not bots:
        raise SystemExit(
            "No bot tokens configured. Set TELEGRAM_BOT_TOKEN and/or BALE_BOT_TOKEN in .env"
        )

    # MemoryStorage: conversation state (creation wizard, contribution log)
    # lives in process memory and is lost on restart. Fine for a single-
    # process MVP; move to Redis-backed storage (see .env REDIS_URL) once
    # that stops being acceptable — see ROADMAP.md.
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.outer_middleware(ModerationMiddleware())
    dp.callback_query.outer_middleware(ModerationMiddleware())
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(suggestions_router)
    dp.include_router(account_router)
    dp.include_router(account_link_router)
    dp.include_router(change_phone_router)
    dp.include_router(manual_phone_verification_router)
    dp.include_router(sms_settings_router)
    dp.include_router(timezone_settings_router)
    dp.include_router(language_settings_router)
    dp.include_router(registration_router)
    dp.include_router(report_router)
    dp.include_router(settings_menu_router)
    dp.include_router(reciter_settings_router)
    dp.include_router(create_khatm_router)
    dp.include_router(digest_settings_router)
    dp.include_router(creator_decisions_router)
    dp.include_router(portions_router)
    dp.include_router(profile_router)
    dp.include_router(font_settings_router)
    dp.include_router(content_settings_router)
    dp.include_router(devotional_router)
    dp.include_router(public_khatms_router)
    dp.include_router(reminder_settings_router)
    dp.include_router(my_khatms_router)
    dp.include_router(leave_router)
    dp.include_router(wallet_router)
    dp.include_router(admin_router)
    dp.include_router(broadcast_router)
    dp.include_router(khatm_request_router)
    dp.include_router(join_requests_router)
    dp.include_router(manage_content_router)

    for bot in bots:
        # Long polling requires no webhook to be set; clear any stale one so
        # Telegram/Bale actually deliver updates to getUpdates.
        await bot.delete_webhook(drop_pending_updates=False)
        try:
            if await install_command_menu(bot):
                logger.info("Telegram command menu installed.")
        except Exception as exc:
            logger.warning("Could not install bot command menu: %s", type(exc).__name__)

    bots_by_platform = {bot.khatmsaz_platform: bot for bot in bots}  # type: ignore[attr-defined]
    notify = build_notify_fn(bots_by_platform)  # also registers the get_notify_fn() singleton
    send_quran_pages = build_send_quran_pages_fn(bots_by_platform)

    # Self-heal on every startup (2026-09-21): the canonical Quran channel
    # map (`quran_page_assets`) has now gone empty twice this session after
    # unrelated local-dev Postgres crashes/WAL recovery, silently breaking
    # all Quran page/audio delivery until someone happened to notice and
    # re-ran the seed by hand. `seed_verified_quran_channel_map` is
    # idempotent (safe to re-run, never creates duplicates), so just always
    # run it here — a real failure (e.g. DB genuinely down) only logs a
    # warning, it must never block the bot from starting.
    try:
        from khatmsaz.modules.content import service as content_service
        async with session_scope() as session:
            seed_result = await content_service.seed_verified_quran_channel_map(session)
        logger.info("Quran channel map self-heal check: %s", seed_result)
    except Exception:
        logger.warning("Quran channel map self-heal check failed — will retry next restart.", exc_info=True)

    async def _run_reminder_scan() -> None:
        runtime_status.mark_scan_started()
        try:
            async with session_scope() as session:
                await reminder_engine.run_once(
                    session,
                    notify,
                    tz_name=settings.app_timezone,
                    monthly_report_day=settings.monthly_report_day,
                    monthly_report_hour=settings.monthly_report_hour,
                    send_quran_pages=send_quran_pages,
                )
            async with session_scope() as session:
                await sms_subscription_service.process_expired(session, notify)
        except Exception as exc:
            runtime_status.mark_scan_failed(exc)
            raise
        else:
            runtime_status.mark_scan_succeeded()

    # Cron trigger at :00, :15, :30, :45 (every 15 min) so reminder delivery
    # is predictable regardless of when the bot starts. The 15-minute
    # granularity also supports per-minute delivery times (e.g. 7:45) that
    # users can now set. `reminder_scan_interval_minutes` is kept in config
    # for backward compatibility but the cron overrides it.
    scheduler = AsyncIOScheduler(timezone=settings.app_timezone)
    scheduler.add_job(
        _run_reminder_scan,
        "cron",
        minute="0,15,30,45",
    )
    scheduler.start()
    runtime_status.mark_scheduler_started()
    logger.info("Reminder scan scheduled at :00, :15, :30, :45 of every hour.")

    logger.info("Starting polling for %d bot(s)...", len(bots))
    polling = asyncio.create_task(dp.start_polling(*bots))
    tasks = [polling]
    if settings.admin_web_enabled:
        web_server = uvicorn.Server(
            uvicorn.Config(
                admin_web_app,
                host=settings.admin_web_host,
                port=settings.admin_web_port,
                log_level=settings.log_level.lower(),
                access_log=False,
            )
        )
        tasks.append(asyncio.create_task(web_server.serve()))
        logger.info(
            "Admin web app listening on %s:%d.",
            settings.admin_web_host,
            settings.admin_web_port,
        )
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    if sys.platform == "win32":
        # asyncio's default ProactorEventLoop has a known bug with TLS
        # negotiated over an already-open connection (e.g. HTTPS through an
        # HTTP CONNECT proxy) — it hangs instead of completing the
        # handshake. The SelectorEventLoop doesn't have this bug. See
        # DEBUGGING.md "Bot can't reach Telegram on Windows".
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
