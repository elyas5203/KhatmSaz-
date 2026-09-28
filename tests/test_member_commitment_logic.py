"""R11 (owner 2026-09-28): unit tests for the pure member-commitment logic —
count logging (incl. R12 re-pledge) and the "is a regular occurrence due now?"
decision the reminder engine relies on. No DB / no bot needed."""
from datetime import date, datetime

from khatmsaz.modules.participation.commitment import (
    CommitmentMode,
    ScheduleFreq,
    is_regular_due,
    is_regular_occurrence_today,
    log_count,
    persian_dow,
)


def test_log_count_accumulates_and_caps_at_target():
    assert log_count(0, 10, 3) == (3, False)
    assert log_count(3, 10, 3) == (6, False)
    assert log_count(6, 10, 3) == (9, False)
    # overshoot is capped and marks completed
    assert log_count(9, 10, 5) == (10, True)


def test_log_count_exact_completion():
    assert log_count(9, 10, 1) == (10, True)


def test_log_count_no_target_never_completes():
    assert log_count(5, None, 100) == (105, False)


def test_log_count_ignores_negative():
    assert log_count(4, 10, -3) == (4, False)


def test_persian_dow_saturday_is_zero():
    # 2026-09-26 is a Saturday
    assert persian_dow(datetime(2026, 9, 26, 12, 0)) == 0
    # 2026-09-25 is a Friday
    assert persian_dow(datetime(2026, 9, 25, 12, 0)) == 6


def test_daily_always_today():
    now = datetime(2026, 9, 28, 8, 0)
    assert is_regular_occurrence_today(now, ScheduleFreq.DAILY.value, None)


def test_weekly_only_on_anchor_day():
    sat = datetime(2026, 9, 26, 8, 0)  # Persian dow 0
    sun = datetime(2026, 9, 27, 8, 0)  # Persian dow 1
    assert is_regular_occurrence_today(sat, ScheduleFreq.WEEKLY.value, 0)
    assert not is_regular_occurrence_today(sun, ScheduleFreq.WEEKLY.value, 0)


def test_monthly_on_anchor_and_clamped_last_day():
    assert is_regular_occurrence_today(datetime(2026, 9, 15, 8, 0), ScheduleFreq.MONTHLY.value, 15)
    assert not is_regular_occurrence_today(datetime(2026, 9, 14, 8, 0), ScheduleFreq.MONTHLY.value, 15)
    # anchor 31 in a 30-day month (September) fires on the 30th
    assert is_regular_occurrence_today(datetime(2026, 9, 30, 8, 0), ScheduleFreq.MONTHLY.value, 31)


def test_is_regular_due_respects_hour_and_dedup():
    now = datetime(2026, 9, 28, 8, 30)
    # before the chosen hour → not due
    assert not is_regular_due(now, ScheduleFreq.DAILY.value, None, 9, 0, None)
    # at/after the chosen time → due when never sent
    assert is_regular_due(now, ScheduleFreq.DAILY.value, None, 8, 0, None)
    # already sent today → not due again
    assert not is_regular_due(now, ScheduleFreq.DAILY.value, None, 8, 0, date(2026, 9, 28))
    # sent yesterday → due today
    assert is_regular_due(now, ScheduleFreq.DAILY.value, None, 8, 0, date(2026, 9, 27))


def test_modes_enum_values():
    assert CommitmentMode.REGULAR.value == "REGULAR"
    assert CommitmentMode.COUNT.value == "COUNT"
