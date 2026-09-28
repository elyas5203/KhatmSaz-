"""R11 (owner 2026-09-28, revised): unit tests for the pure member-commitment
logic — count logging (incl. re-pledge), exact HH:MM parsing, and the
period-based "is a regular reminder due now?" decision."""
from datetime import date, datetime

from khatmsaz.modules.participation.commitment import (
    CommitmentMode,
    ScheduleFreq,
    is_regular_due,
    log_count,
    parse_hhmm,
)


def test_log_count_accumulates_and_caps_at_target():
    assert log_count(0, 10, 3) == (3, False)
    assert log_count(6, 10, 3) == (9, False)
    assert log_count(9, 10, 5) == (10, True)  # overshoot capped + completed


def test_log_count_exact_completion_and_no_target():
    assert log_count(9, 10, 1) == (10, True)
    assert log_count(5, None, 100) == (105, False)
    assert log_count(4, 10, -3) == (4, False)  # negative ignored


def test_parse_hhmm_variants():
    assert parse_hhmm("13:25") == (13, 25)
    assert parse_hhmm("9") == (9, 0)
    assert parse_hhmm("۱۳:۲۵") == (13, 25)   # Persian digits
    assert parse_hhmm("08.30") == (8, 30)    # dot separator
    assert parse_hhmm("24:00") is None
    assert parse_hhmm("12:60") is None
    assert parse_hhmm("abc") is None


def test_daily_due_once_per_day_after_time():
    now = datetime(2026, 9, 28, 18, 5)
    assert not is_regular_due(now, ScheduleFreq.DAILY.value, 19, 0, None)  # before time
    assert is_regular_due(now, ScheduleFreq.DAILY.value, 18, 0, None)      # after, never sent
    assert not is_regular_due(now, ScheduleFreq.DAILY.value, 18, 0, date(2026, 9, 28))  # sent today
    assert is_regular_due(now, ScheduleFreq.DAILY.value, 18, 0, date(2026, 9, 27))      # sent yesterday


def test_exact_minute_respected():
    now = datetime(2026, 9, 28, 13, 24)
    assert not is_regular_due(now, ScheduleFreq.DAILY.value, 13, 25, None)  # 13:24 < 13:25
    now2 = datetime(2026, 9, 28, 13, 25)
    assert is_regular_due(now2, ScheduleFreq.DAILY.value, 13, 25, None)


def test_weekly_due_every_seven_days():
    now = datetime(2026, 9, 28, 10, 0)
    assert is_regular_due(now, ScheduleFreq.WEEKLY.value, 9, 0, date(2026, 9, 21))       # 7 days
    assert not is_regular_due(now, ScheduleFreq.WEEKLY.value, 9, 0, date(2026, 9, 24))   # 4 days


def test_monthly_due_once_per_calendar_month():
    now = datetime(2026, 9, 28, 10, 0)
    assert is_regular_due(now, ScheduleFreq.MONTHLY.value, 9, 0, date(2026, 8, 28))
    assert not is_regular_due(now, ScheduleFreq.MONTHLY.value, 9, 0, date(2026, 9, 1))


def test_modes_enum_values():
    assert CommitmentMode.REGULAR.value == "REGULAR"
    assert CommitmentMode.COUNT.value == "COUNT"
