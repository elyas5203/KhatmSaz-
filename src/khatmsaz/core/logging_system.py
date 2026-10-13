"""Real-time logging, persistent rotation, and instant crash alerting engine.

Captures all moments into `logs/khatmsaz.log` and `logs/errors.log`.
Instantly dispatches any ERROR or CRITICAL log records (and unhandled crashes)
to the Super Admin via the dedicated Admin Bot (@khatmsaz_admin_bot).
See DEC-PY-0126 and MASTER-12.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from html import escape
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import time
import traceback
from typing import Any

from khatmsaz.config import get_settings

logger = logging.getLogger("khatmsaz")

_LOG_DIR = Path("logs")
_MAIN_LOG_FILE = _LOG_DIR / "khatmsaz.log"
_ERROR_LOG_FILE = _LOG_DIR / "errors.log"

_ALERT_COOLDOWN_SECONDS = 60.0
_last_alerts: dict[str, float] = {}


class TelegramErrorAlertHandler(logging.Handler):
    """Logging handler that forwards ERROR and CRITICAL records to Super Admins via @khatmsaz_admin_bot."""

    def __init__(self, level: int = logging.ERROR) -> None:
        super().__init__(level=level)
        self._loop: asyncio.AbstractEventLoop | None = None

    def emit(self, record: logging.LogRecord) -> None:
        if sys.is_finalizing():
            return
        # Avoid recursion if logging within the handler fails
        if record.name.startswith("khatmsaz.core.logging_system") or record.name.startswith("aiogram"):
            return

        try:
            # Debounce to prevent flooding admin in tight loops
            err_key = f"{record.name}:{record.lineno}:{getattr(record, 'exc_info', None) and record.exc_info[0] or record.getMessage()[:50]}"
            now = time.time()
            last_sent = _last_alerts.get(err_key, 0.0)
            if now - last_sent < _ALERT_COOLDOWN_SECONDS:
                return
            _last_alerts[err_key] = now

            # Format alert payload
            time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            msg_text = record.getMessage()

            tb_text = ""
            if record.exc_info and record.exc_info[1]:
                lines = traceback.format_exception(*record.exc_info)
                # Take last 12 lines of traceback to fit comfortably in Telegram message
                tb_text = "".join(lines[-12:])
            elif record.stack_info:
                tb_text = str(record.stack_info)[-600:]

            alert_message = (
                "🚨 <b>هشدار خطای سیستمی در ختم‌ساز</b>\n\n"
                f"📍 <b>محل وقوع:</b> <code>{escape(record.name)}:{record.lineno}</code>\n"
                f"⚠️ <b>سطح خطا:</b> <b>{escape(record.levelname)}</b>\n"
                f"⏰ <b>زمان:</b> <code>{time_str}</code>\n\n"
                f"📝 <b>پیام:</b>\n<code>{escape(msg_text[:400])}</code>"
            )
            if tb_text:
                alert_message += f"\n\n📋 <b>تریس خطا (خلاصه):</b>\n<pre>{escape(tb_text[:900])}</pre>"

            # Dispatch asynchronously via running loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = self._loop

            if loop and loop.is_running():
                loop.create_task(self._send_alert_safe(alert_message))
        except Exception:
            pass

    async def _send_alert_safe(self, text: str) -> None:
        try:
            from khatmsaz.bot.admin_notifications import notify_super_admins
            await notify_super_admins(text)
        except Exception:
            # Never raise inside logging handler
            pass


def configure_system_logging() -> None:
    """Initialize continuous rotating file logging and Telegram alert handler."""
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    settings = get_settings()

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())

    # Formatter
    detailed_fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s [%(name)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # 1. Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level.upper())
    console_handler.setFormatter(console_fmt)
    root_logger.addHandler(console_handler)

    # 2. Main rotating file handler (10MB, 5 backups)
    main_file_handler = RotatingFileHandler(
        _MAIN_LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    main_file_handler.setLevel(logging.INFO)
    main_file_handler.setFormatter(detailed_fmt)
    root_logger.addHandler(main_file_handler)

    # 3. Error rotating file handler (10MB, 5 backups)
    error_file_handler = RotatingFileHandler(
        _ERROR_LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_fmt)
    root_logger.addHandler(error_file_handler)

    # 4. Telegram alert handler
    alert_handler = TelegramErrorAlertHandler(level=logging.ERROR)
    root_logger.addHandler(alert_handler)

    logger.info("Continuous logging initialized: %s and %s", _MAIN_LOG_FILE, _ERROR_LOG_FILE)


def install_exception_hooks(loop: asyncio.AbstractEventLoop | None = None) -> None:
    """Catch unhandled exceptions in both synchronous threads and asynchronous event loop."""
    # Synchronous hook
    def _sys_hook(exc_type: type[BaseException], exc_value: BaseException, exc_tb: Any) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical(
            "Unhandled top-level exception: %s",
            exc_value,
            exc_info=(exc_type, exc_value, exc_tb),
        )

    sys.excepthook = _sys_hook

    # Asyncio loop hook
    if loop is not None:
        def _asyncio_hook(_loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
            if sys.is_finalizing():
                return
            exc = context.get("exception")
            msg = context.get("message", "Unhandled exception in asyncio loop")
            if msg == "Unclosed client session":
                return
            if exc is not None:
                logger.critical("Asyncio task crashed: %s (%s)", msg, exc, exc_info=exc)
            else:
                logger.critical("Asyncio error: %s", msg)

        loop.set_exception_handler(_asyncio_hook)


def get_recent_logs(lines: int = 35) -> str:
    """Read the tail of the main system log file."""
    if not _MAIN_LOG_FILE.exists():
        return "فایل لاگ اصلی هنوز ایجاد نشده است."
    try:
        with open(_MAIN_LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return "".join(tail).strip()
    except Exception as exc:
        return f"خطا در خواندن فایل لاگ: {exc}"


def get_recent_errors(lines: int = 35) -> str:
    """Read the tail of the error log file."""
    if not _ERROR_LOG_FILE.exists():
        return "هیچ خطای ثبت‌شده‌ای در فایل خطاها یافت نشد."
    try:
        with open(_ERROR_LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return "".join(tail).strip() or "فایل خطاها خالی است (سیستم پایدار است)."
    except Exception as exc:
        return f"خطا در خواندن فایل خطاها: {exc}"


def get_log_file_paths() -> tuple[Path, Path]:
    return _MAIN_LOG_FILE, _ERROR_LOG_FILE
