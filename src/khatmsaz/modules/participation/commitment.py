"""R11 (owner 2026-09-28, revised after live QA): member-side commitment logic.

Pure, side-effect-free (no DB, no aiogram) so it is unit-testable.

A commitment khatm's TOTAL is fixed by the creator. Each MEMBER picks how they
personally commit:

  • COUNT   — "I'll read this N times." They read on their own and tap a button
    to log progress; when done they may pledge a fresh count.
  • REGULAR — "I'll read <times_per_period> times per day / week / month, remind
    me at <hour>:<minute>." The reminder engine notifies at that exact local
    time, once per period.

Field mapping on `Participation` (reused columns, no extra migration):
  schedule_freq              -> "DAILY" | "WEEKLY" | "MONTHLY"
  commitment_per_occurrence  -> times_per_period (e.g. «۳ بار در هفته»)
  schedule_hour              -> reminder hour (0..23)
  schedule_anchor            -> reminder minute (0..59) — supports exact HH:MM
"""
from __future__ import annotations

import enum
from datetime import datetime


class CommitmentMode(str, enum.Enum):
    REGULAR = "REGULAR"
    COUNT = "COUNT"


class ScheduleFreq(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


def log_count(done: int, target: int | None, amount: int) -> tuple[int, bool]:
    """Add ``amount`` to a COUNT-mode member's logged total.

    Returns ``(new_done, completed)``. ``new_done`` never exceeds ``target``
    (when set); ``completed`` is True once the target is reached. A NULL target
    means "no cap yet" — accumulate and never complete."""
    if amount < 0:
        amount = 0
    new_done = done + amount
    if target is not None:
        new_done = min(new_done, target)
        return new_done, new_done >= target
    return new_done, False


def parse_hhmm(raw: str) -> tuple[int, int] | None:
    """Parse a typed exact time like «13:25» / «۱۳:۲۵» / «9» into (hour, minute),
    or None if invalid. Supports Persian/Arabic digits and an optional minute."""
    s = raw.strip()
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    s = s.translate(trans)
    s = s.replace(".", ":").replace("،", ":").strip()
    if ":" in s:
        parts = s.split(":", 1)
        if not (parts[0].isdigit() and parts[1].isdigit()):
            return None
        hour, minute = int(parts[0]), int(parts[1])
    elif s.isdigit():
        hour, minute = int(s), 0
    else:
        return None
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return hour, minute
    return None


def _minutes(hour: int, minute: int) -> int:
    return hour * 60 + minute


def _persian_weekdays_to_py(weekdays: str | None) -> set[int]:
    """Parse «0,1,4» (Persian index 0=Sat..6=Fri) → Python weekday()s (Mon=0..Sun=6).
    Mapping: py = (persian + 5) % 7 (Sat→5, Sun→6, Mon→0, …)."""
    out: set[int] = set()
    for part in (weekdays or "").split(","):
        part = part.strip()
        if part.isdigit() and 0 <= int(part) <= 6:
            out.add((int(part) + 5) % 7)
    return out


def is_regular_due(
    now_local: datetime,
    freq: str,
    hour: int,
    minute: int,
    last_sent_local_date,
    weekdays: str | None = None,
) -> bool:
    """Decision for the reminder engine: the exact time has been reached and this
    period's reminder hasn't been sent yet.

    ``last_sent_local_date`` is the local calendar date of the last delivery (or
    None). Period gating:
      • DAILY   — once per calendar day.
      • WEEKLY  — owner L4 (2026-09-30): fires on each chosen weekday (``weekdays``,
        Persian 0=Sat..6=Fri), once per that day. Legacy weekly without ``weekdays``
        falls back to once-every-7-days.
      • MONTHLY — (removed from the UI) once per calendar month, kept for old rows.
    """
    if _minutes(now_local.hour, now_local.minute) < _minutes(hour, minute):
        return False
    today = now_local.date()
    if freq == ScheduleFreq.WEEKLY.value and weekdays:
        py_days = _persian_weekdays_to_py(weekdays)
        if now_local.weekday() not in py_days:
            return False
        return last_sent_local_date is None or today > last_sent_local_date
    if last_sent_local_date is None:
        return True
    if freq == ScheduleFreq.DAILY.value:
        return today > last_sent_local_date
    if freq == ScheduleFreq.WEEKLY.value:
        return (today - last_sent_local_date).days >= 7
    if freq == ScheduleFreq.MONTHLY.value:
        return (today.year, today.month) != (last_sent_local_date.year, last_sent_local_date.month)
    return today > last_sent_local_date
