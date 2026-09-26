"""In-process operational heartbeat exposed read-only to Operations admins."""

from datetime import datetime, timezone


_process_started_at = datetime.now(timezone.utc)

_state = {
    "scheduler_started_at": None,
    "last_scan_started_at": None,
    "last_scan_succeeded_at": None,
    "last_scan_failed_at": None,
    "last_scan_error": None,
}


def process_started_at() -> datetime:
    return _process_started_at


def mark_scheduler_started() -> None:
    _state["scheduler_started_at"] = datetime.now(timezone.utc)


def mark_scan_started() -> None:
    _state["last_scan_started_at"] = datetime.now(timezone.utc)


def mark_scan_succeeded() -> None:
    _state["last_scan_succeeded_at"] = datetime.now(timezone.utc)
    _state["last_scan_error"] = None


def mark_scan_failed(exc: Exception) -> None:
    _state["last_scan_failed_at"] = datetime.now(timezone.utc)
    _state["last_scan_error"] = type(exc).__name__


def snapshot() -> dict:
    return dict(_state)
