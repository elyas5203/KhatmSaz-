"""DEC-PY-0092 rotating Quran allocation — proves each committed reader's own
pages advance sequentially (4,5 → 6,7 → 8,9 …) instead of jumping by N members
(the reported 4,5 → 8,9 → 12,13 bug), while distinct offsets keep same-day
assignments collision-free and cover the whole book over a full cycle."""
from khatmsaz.modules.allocation.service import positional_range_for_step


def test_personal_journey_is_sequential():
    # One reader, offset 0, reading 2 pages/portion → 1-2, 3-4, 5-6, ...
    ranges = [positional_range_for_step(offset=0, step=s, total_units=604, units_per_portion=2) for s in range(4)]
    assert ranges == [(1, 2), (3, 4), (5, 6), (7, 8)]


def test_second_reader_also_sequential_not_jumping():
    # Reader B starts at offset 2 (3rd portion). Their OWN pages must still be
    # sequential: 5,6 → 7,8 → 9,10 — NOT jumping by the member count.
    b = [positional_range_for_step(offset=2, step=s, total_units=604, units_per_portion=2) for s in range(3)]
    assert b == [(5, 6), (7, 8), (9, 10)]


def test_no_same_day_duplicate_across_members():
    # 3 members with distinct offsets on the same day (same step) read
    # different, non-overlapping pages.
    day0 = {positional_range_for_step(offset=o, step=0, total_units=604, units_per_portion=2) for o in (0, 1, 2)}
    assert day0 == {(1, 2), (3, 4), (5, 6)}


def test_wraps_around_the_book():
    total_portions = 302  # 604 / 2
    # After a full cycle a reader returns to their start (personal khatm done).
    first = positional_range_for_step(offset=5, step=0, total_units=604, units_per_portion=2)
    wrapped = positional_range_for_step(offset=5, step=total_portions, total_units=604, units_per_portion=2)
    assert first == wrapped


def test_last_portion_clamps_to_total():
    # 5 pages, 2 per portion → portions 1-2, 3-4, 5-5 (clamped).
    assert positional_range_for_step(offset=2, step=0, total_units=5, units_per_portion=2) == (5, 5)
