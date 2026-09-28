"""R11 (owner 2026-09-28): member-side commitment logic — pure, side-effect-free.

A commitment khatm's TOTAL is fixed by the creator (R5). Each MEMBER then picks
*how* they personally commit:

  • COUNT   — "I'll read this N times." They read on their own and tap a button
    to log progress; when done they may pledge a fresh count (R12).
  • REGULAR — "Send me M each day / each week on day D / each month on day D, at
    hour H." The reminder engine delivers at that local time.

Keeping the math and the "is a regular occurrence due now?" decision here (no DB,
no aiogram) makes both unit-testable without a live bot or Postgres.
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
    (when a target is set); ``completed`` is True once the target is reached.
    A NULL target means "no cap yet" — we just accumulate and never complete.
    """
    if amount < 0:
        amount = 0
    new_done = done + amount
    if target is not None:
        new_done = min(new_done, target)
        return new_done, new_done >= target
    return new_done, False


# Python's weekday(): Mon=0..Sun=6. The bot models the week Persian-style with
# Saturday first, so schedule_anchor uses 0=Saturday..6=Friday. This maps a
# local datetime to that 0=Sat..6=Fri index.
def persian_dow(dt: datetime) -> int:
    """0=Saturday .. 6=Friday for the given datetime's weekday."""
    # weekday(): Mon=0,Tue=1,Wed=2,Thu=3,Fri=4,Sat=5,Sun=6
    # want:      Sat=0,Sun=1,Mon=2,Tue=3,Wed=4,Thu=5,Fri=6
    return (dt.weekday() + 2) % 7


def _minutes(dt_hour: int, dt_minute: int) -> int:
    return dt_hour * 60 + dt_minute


def is_regular_occurrence_today(
    now_local: datetime,
    freq: str,
    anchor: int | None,
) -> bool:
    """Is today the right *day* for a REGULAR occurrence (ignoring the hour)?

    - DAILY: always today.
    - WEEKLY: only when today's Persian weekday equals ``anchor`` (0=Sat..6=Fri).
    - MONTHLY: only when today's day-of-month equals ``anchor`` (1..31); if the
      month is shorter than ``anchor`` (e.g. anchor=31 in a 30-day month), the
      last day of the month counts so the occurrence is never silently skipped.
    """
    if freq == ScheduleFreq.DAILY.value:
        return True
    if freq == ScheduleFreq.WEEKLY.value:
        return anchor is not None and persian_dow(now_local) == anchor
    if freq == ScheduleFreq.MONTHLY.value:
        if anchor is None:
            return False
        if now_local.day == anchor:
            return True
        # clamp: last day of a short month satisfies a too-large anchor
        import calendar
        last_dom = calendar.monthrange(now_local.year, now_local.month)[1]
        return now_local.day == last_dom and anchor > last_dom
    return False


def is_regular_due(
    now_local: datetime,
    freq: str,
    anchor: int | None,
    hour: int,
    minute: int,
    last_sent_local_date,
) -> bool:
    """Full decision for the reminder engine: right day, at/after the chosen
    time, and not already sent for this occurrence.

    ``last_sent_local_date`` is the local calendar date of the last delivery (or
    None). We dedupe per calendar day, matching ``deliver_due_open_quran_reading``
    — for WEEKLY/MONTHLY the day gate already limits it to one occurrence.
    """
    if not is_regular_occurrence_today(now_local, freq, anchor):
        return False
    if _minutes(now_local.hour, now_local.minute) < _minutes(hour, minute):
        return False
    if last_sent_local_date is not None and now_local.date() <= last_sent_local_date:
        return False
    return True
