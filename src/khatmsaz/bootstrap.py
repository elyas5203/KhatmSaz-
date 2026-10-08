"""Process entrypoint: `python -m khatmsaz.bootstrap`.

Starts both bots (whichever tokens are configured) on long polling, sharing
one Dispatcher / one set of handlers. Long polling — not a webhook — is a
deliberate choice: it needs no public domain, no reverse proxy, and no
tunnel, which removes the exact failure point the previous TypeScript
deployment got stuck on (see docs/ai/DECISIONS.md, DEC-PY-0001).

Multi-bot architecture (DEC-PY-0080): up to 26 bots share one process.
Two Dispatchers — dp_creator for management, dp_member for participation.
"""

import asyncio
import logging
import signal
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn

from khatmsaz.bot.bale.client import build_bale_bot
from khatmsaz.bot.handlers.admin import router as admin_router
from khatmsaz.bot.handlers.account import router as account_router
from khatmsaz.bot.handlers.account_link import router as account_link_router
from khatmsaz.bot.handlers.change_phone import router as change_phone_router
from khatmsaz.bot.handlers.broadcast import router as broadcast_router
from khatmsaz.bot.handlers.create_khatm import router as create_khatm_router
from khatmsaz.bot.handlers.devotional import router as devotional_router
from khatmsaz.bot.handlers.creator_decisions import router as creator_decisions_router
from khatmsaz.bot.handlers.language_settings import router as language_settings_router
from khatmsaz.bot.handlers.manual_phone_verification import router as manual_phone_verification_router
from khatmsaz.bot.handlers.creator_request import router as creator_request_router
from khatmsaz.bot.handlers.khatm_request import router as khatm_request_router
from khatmsaz.bot.handlers.manage_content import router as manage_content_router
from khatmsaz.bot.handlers.my_khatms import router as my_khatms_router
from khatmsaz.bot.handlers.portions import router as portions_router
from khatmsaz.bot.handlers.public_khatms import router as public_khatms_router
from khatmsaz.bot.handlers.registration import router as registration_router
from khatmsaz.bot.handlers.start import router as start_router
from khatmsaz.bot.handlers.wallet import router as wallet_router
from khatmsaz.bot.handlers.creator_broadcast import router as creator_broadcast_router
from khatmsaz.bot.middlewares import ModerationMiddleware
from khatmsaz.bot.commands import install_command_menu
from khatmsaz.bot.notify_adapter import build_notify_fn, build_send_quran_pages_fn
from khatmsaz.bot.telegram.client import build_telegram_bot
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.core import runtime_status
from khatmsaz.core.bot_registry import BotRegistry, set_registry
from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.modules.bot_registry import service as bot_registry_service
from khatmsaz.modules.reminder_engine import service as reminder_engine
from khatmsaz.modules.sms_subscription import service as sms_subscription_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.web.app import app as admin_web_app

logger = logging.getLogger("khatmsaz")


def _configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )


def _tag_bot(
    bot: Bot,
    *,
    role: str,
    instance_id=None,
    category=None,
    language=None,
) -> None:
    bot.khatmsaz_role = role  # type: ignore[attr-defined]
    bot.khatmsaz_category = category  # type: ignore[attr-defined]
    bot.khatmsaz_language = language  # type: ignore[attr-defined]
    bot.khatmsaz_instance_id = instance_id  # type: ignore[attr-defined]


async def _build_member_bots() -> list[Bot]:
    settings = get_settings()
    if not settings.bot_token_encryption_key:
        logger.info("BOT_TOKEN_ENCRYPTION_KEY not set — skipping member bot loading.")
        return []

    member_bots: list[Bot] = []
    async with session_scope() as session:
        instances = await bot_registry_service.list_configured_member_bots(session)
        for inst in instances:
            token = await bot_registry_service.get_decrypted_token(inst)
            if not token:
                logger.warning("Could not decrypt token for %s — skipping.", inst.display_name)
                continue
            if inst.platform == "TELEGRAM":
                bot = build_telegram_bot(token)
            elif inst.platform == "BALE":
                bot = build_bale_bot(token)
            else:
                logger.warning("Unknown platform %s for %s — skipping.", inst.platform, inst.display_name)
                continue
            try:
                # Validate the token before adding to the pool — a revoked
                # token would crash the entire polling gather otherwise.
                me = await bot.get_me()
            except Exception as exc:
                logger.warning(
                    "Member bot %s (%s) has an invalid token (%s) — skipping.",
                    inst.display_name, inst.platform, type(exc).__name__,
                )
                await bot.session.close()
                continue
            bot.khatmsaz_username = me.username  # type: ignore[attr-defined]
            _tag_bot(
                bot,
                role=BotRole.MEMBER,
                instance_id=inst.id,
                category=inst.category,
                language=inst.language,
            )
            member_bots.append(bot)
            logger.info("Member bot loaded: %s (%s/%s/%s)", inst.display_name, inst.platform, inst.category, inst.language)
    return member_bots


async def main() -> None:
    _configure_logging()
    settings = get_settings()

    # --- Creator bots (from .env, as before) ---
    creator_bots: list[Bot] = []

    if settings.telegram_bot_token:
        bot = build_telegram_bot()
        _tag_bot(bot, role=BotRole.CREATOR)
        creator_bots.append(bot)
        logger.info("Telegram creator bot configured.")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram creator bot disabled.")

    if settings.bale_bot_token:
        bot = build_bale_bot()
        _tag_bot(bot, role=BotRole.CREATOR)
        creator_bots.append(bot)
        logger.info("Bale creator bot configured.")
    else:
        logger.warning("BALE_BOT_TOKEN not set — Bale creator bot disabled.")

    if not creator_bots:
        raise SystemExit(
            "No bot tokens configured. Set TELEGRAM_BOT_TOKEN and/or BALE_BOT_TOKEN in .env"
        )

    # Sync creator tokens into bot_instances table
    if settings.bot_token_encryption_key:
        try:
            async with session_scope() as session:
                await bot_registry_service.sync_creator_from_env(session)
            logger.info("Creator bot tokens synced to bot_instances.")
        except Exception:
            logger.warning("Could not sync creator tokens to DB.", exc_info=True)

    # --- Member bots (from DB) ---
    member_bots = await _build_member_bots()

    # --- Build registry ---
    all_bots = creator_bots + member_bots
    registry = BotRegistry(all_bots)
    set_registry(registry)
    logger.info(
        "BotRegistry: %d creator(s), %d member(s).",
        len(creator_bots), len(member_bots),
    )

    # FSM state must survive service restarts. MemoryStorage left an old
    # question visible while forgetting which answer the bot was waiting for,
    # making a conversation appear frozen after a deploy/restart.
    creator_storage = RedisStorage.from_url(
        settings.redis_url,
        key_builder=DefaultKeyBuilder(prefix="khatmsaz_fsm_creator", with_bot_id=True),
    )
    member_storage = RedisStorage.from_url(
        settings.redis_url,
        key_builder=DefaultKeyBuilder(prefix="khatmsaz_fsm_member", with_bot_id=True),
    )

    # --- Creator Dispatcher ---
    dp_creator = Dispatcher(storage=creator_storage)
    dp_creator.message.outer_middleware(ModerationMiddleware())
    dp_creator.callback_query.outer_middleware(ModerationMiddleware())

    # --- Member Dispatcher ---
    dp_member = Dispatcher(storage=member_storage)
    dp_member.message.outer_middleware(ModerationMiddleware())
    dp_member.callback_query.outer_middleware(ModerationMiddleware())

    # --- Member-only routers ---
    from khatmsaz.bot.handlers.member_start import router as member_start_router
    from khatmsaz.bot.handlers.member_registration import router as member_registration_router
    from khatmsaz.bot.handlers.member_my_khatms import router as member_my_khatms_router
    
    dp_member.include_router(member_start_router)
    dp_member.include_router(member_registration_router)
    dp_member.include_router(member_my_khatms_router)
    dp_member.include_router(portions_router)
    dp_member.include_router(devotional_router)
    # public_khatms moved to the shared list below so /public_khatms works on
    # the creator bot too (owner live QA 2026-09-28: it produced no output
    # there because it was member-only).

    # --- Creator-only routers ---
    dp_creator.include_router(start_router)
    dp_creator.include_router(registration_router)
    dp_creator.include_router(create_khatm_router)
    dp_creator.include_router(my_khatms_router)
    dp_creator.include_router(admin_router)
    dp_creator.include_router(broadcast_router)
    dp_creator.include_router(wallet_router)
    dp_creator.include_router(creator_decisions_router)
    dp_creator.include_router(creator_request_router)
    dp_creator.include_router(creator_broadcast_router)
    dp_creator.include_router(manual_phone_verification_router)
    dp_creator.include_router(account_router)
    dp_creator.include_router(account_link_router)
    dp_creator.include_router(change_phone_router)
    dp_creator.include_router(language_settings_router)
    dp_creator.include_router(khatm_request_router)
    from khatmsaz.bot.handlers.panel import router as panel_router
    dp_creator.include_router(panel_router)

    # --- Shared routers ---
    # aiogram enforces a single-parent rule: a Router can only be included
    # in one Dispatcher. To share handlers across dp_creator and dp_member we
    # load each module fresh for each Dispatcher using importlib.util, which
    # produces a new Router object per call without touching sys.modules.
    import importlib.util

    def _fresh_router(module_path: str):
        spec = importlib.util.find_spec(module_path)
        fresh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fresh)
        return getattr(fresh, "router")

    _shared_module_paths = [
        "khatmsaz.bot.handlers.manage_content",
        "khatmsaz.bot.handlers.public_khatms",
        "khatmsaz.bot.handlers.leave",
        "khatmsaz.bot.handlers.join_flow",
        "khatmsaz.bot.handlers.join_requests",
        "khatmsaz.bot.handlers.member_commitment",
        "khatmsaz.bot.handlers.help",
        "khatmsaz.bot.handlers.settings_menu",
        "khatmsaz.bot.handlers.timezone_settings",
        "khatmsaz.bot.handlers.font_settings",
        "khatmsaz.bot.handlers.content_settings",
        "khatmsaz.bot.handlers.reciter_settings",
        "khatmsaz.bot.handlers.reminder_settings",
        "khatmsaz.bot.handlers.digest_settings",
        "khatmsaz.bot.handlers.sms_settings",
        "khatmsaz.bot.handlers.profile",
        "khatmsaz.bot.handlers.report",
        "khatmsaz.bot.handlers.suggestions",
    ]

    for _path in _shared_module_paths:
        dp_creator.include_router(_fresh_router(_path))
        dp_member.include_router(_fresh_router(_path))

    # Fetch and tag usernames for creator bots (member bots already tagged during token validation above).
    for bot in creator_bots:
        try:
            me = await bot.get_me()
            bot.khatmsaz_username = me.username  # type: ignore[attr-defined]
        except Exception:
            bot.khatmsaz_username = None  # type: ignore[attr-defined]

    # --- Clear stale webhooks ---
    # A single unreachable bot (e.g. Bale's tapi.bale.ai down, or a bad token)
    # must NOT crash the whole process — that took the service into a restart
    # loop and killed Telegram too (owner server log 2026-09-29). Wrap each
    # bot's startup calls so a failing one is logged and skipped; the reachable
    # bots keep working.
    for bot in all_bots:
        try:
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception as exc:
            logger.warning(
                "Could not clear webhook for %s (%s) — skipping this bot's startup calls; it may be unreachable.",
                getattr(bot, "khatmsaz_platform", "?"), type(exc).__name__,
            )
            continue
        try:
            if await install_command_menu(bot):
                logger.info("Command menu installed for %s.", getattr(bot, "khatmsaz_platform", "?"))
        except Exception as exc:
            logger.warning("Could not install bot command menu: %s", type(exc).__name__)

    bots_by_platform = {bot.khatmsaz_platform: bot for bot in creator_bots}  # type: ignore[attr-defined]
    notify = build_notify_fn(bots_by_platform)
    send_quran_pages = build_send_quran_pages_fn(bots_by_platform)

    # Self-heal Quran channel map on every startup
    try:
        from khatmsaz.modules.content import service as content_service
        async with session_scope() as session:
            seed_result = await content_service.seed_verified_quran_channel_map(session)
        logger.info("Quran channel map self-heal check: %s", seed_result)
    except Exception:
        logger.warning("Quran channel map self-heal check failed — will retry next restart.", exc_info=True)

    # Seed admin-curated devotional texts (Ziyarat Ashura, Al-Yasin, Faraj,
    # Ahd) on every startup — idempotent upsert keyed on slug.
    try:
        from khatmsaz.modules.content.devotional_seed import seed_devotional_texts
        async with session_scope() as session:
            devotional_result = await seed_devotional_texts(session)
        logger.info("Devotional text seed: %s", devotional_result)
    except Exception:
        logger.warning("Devotional text seed failed — will retry next restart.", exc_info=True)

    # Self-heal database enums on every startup (e.g. KHUTBAH in khatmcategorygroup)
    try:
        from sqlalchemy import text
        from khatmsaz.core.db import get_engine
        async with get_engine().connect() as conn:
            await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.execute(text("ALTER TYPE khatmcategorygroup ADD VALUE IF NOT EXISTS 'KHUTBAH'"))
    except Exception as exc:
        logger.debug("Database enum self-heal check: %s", exc)

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
            async with session_scope() as session:
                await wallet_service.cleanup_expired_pending_payments(session)
        except Exception as exc:
            runtime_status.mark_scan_failed(exc)
            raise
        else:
            runtime_status.mark_scan_succeeded()

    scheduler = AsyncIOScheduler(timezone=settings.app_timezone)
    scheduler.add_job(
        _run_reminder_scan,
        "cron",
        minute="*",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    runtime_status.mark_scheduler_started()
    logger.info("Reminder scan scheduled every minute (coalesced, single instance).")

    # --- Shutdown coordination ---
    shutdown_event = asyncio.Event()

    def _trigger_shutdown(*_args: object) -> None:
        if not shutdown_event.is_set():
            logger.info("Termination signal received — stopping KhatmSaz...")
            shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _trigger_shutdown)
        except (NotImplementedError, AttributeError):
            pass

    for sig in (signal.SIGINT, getattr(signal, "SIGTERM", None), getattr(signal, "SIGBREAK", None)):
        if sig is not None:
            try:
                signal.signal(sig, lambda s, f: _trigger_shutdown())
            except (ValueError, OSError):
                pass

    async def _safe_stop_polling(dp: Dispatcher) -> None:
        try:
            await dp.stop_polling()
        except RuntimeError:
            pass
        except Exception as exc:
            logger.warning("Error stopping polling for dispatcher: %s", exc)

    # --- Polling supervisor ---
    async def _run_polling_supervised(dp: Dispatcher, bots: list[Bot], name: str) -> None:
        if not bots:
            return
        backoff_seconds = 2.0
        while not shutdown_event.is_set():
            try:
                logger.info("Starting polling for %s (%d bot(s))...", name, len(bots))
                await dp.start_polling(
                    *bots,
                    handle_signals=False,
                    close_bot_session=False,
                )
                break
            except asyncio.CancelledError:
                break
            except Exception as exc:
                if shutdown_event.is_set():
                    break
                logger.error(
                    "Polling error in %s (%s: %s). Reconnecting in %.1fs...",
                    name, type(exc).__name__, exc, backoff_seconds,
                )
                try:
                    await asyncio.wait_for(shutdown_event.wait(), timeout=backoff_seconds)
                    break
                except asyncio.TimeoutError:
                    backoff_seconds = min(backoff_seconds * 1.5, 30.0)

    web_server: uvicorn.Server | None = None
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

    async def _handle_shutdown() -> None:
        await shutdown_event.wait()
        logger.info("Shutdown initiated — stopping scheduler, web server, and bot polling...")
        try:
            if scheduler.running:
                scheduler.shutdown(wait=False)
                logger.info("Scheduler stopped.")
        except Exception as exc:
            logger.warning("Error stopping scheduler: %s", exc)

        if web_server is not None:
            web_server.should_exit = True
            logger.info("Admin web server requested to exit.")

        stop_coros = [_safe_stop_polling(dp_creator)]
        if member_bots:
            stop_coros.append(_safe_stop_polling(dp_member))
        await asyncio.gather(*stop_coros, return_exceptions=True)
        logger.info("Dispatcher stop signals sent.")

    tasks: list[asyncio.Task] = [
        asyncio.create_task(_run_polling_supervised(dp_creator, creator_bots, "creator")),
    ]
    if member_bots:
        tasks.append(asyncio.create_task(_run_polling_supervised(dp_member, member_bots, "member")))

    if web_server is not None:
        tasks.append(asyncio.create_task(web_server.serve()))
        logger.info(
            "Admin web app listening on %s:%d.",
            settings.admin_web_host,
            settings.admin_web_port,
        )

    shutdown_task = asyncio.create_task(_handle_shutdown())

    try:
        await asyncio.gather(*tasks)
    except (asyncio.CancelledError, KeyboardInterrupt):
        _trigger_shutdown()
        await shutdown_task
    finally:
        if not shutdown_event.is_set():
            _trigger_shutdown()
        try:
            await shutdown_task
        except Exception:
            pass
        if scheduler.running:
            try:
                scheduler.shutdown(wait=False)
            except Exception:
                pass
        logger.info("Closing bot HTTP sessions...")
        await asyncio.gather(*(bot.session.close() for bot in all_bots), return_exceptions=True)
        logger.info("KhatmSaz shutdown complete.")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
