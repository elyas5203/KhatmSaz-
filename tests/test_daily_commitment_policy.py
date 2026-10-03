from types import SimpleNamespace

import pytest

from khatmsaz.modules.khatm.commitment_policy import validate_policy, validate_member_amount


@pytest.mark.parametrize("mode", ["OPEN", "COMMITMENT"])
def test_member_choice_does_not_impose_daily_amount(mode):
    validate_policy(mode)
    with pytest.raises(ValueError):
        validate_policy(mode, "MEMBER_CHOICE", 10)


@pytest.mark.parametrize("amount", [None, 0, -1, True, 1.5])
def test_fixed_requires_a_positive_integer(amount):
    with pytest.raises(ValueError):
        validate_policy("COMMITMENT", "FIXED_DAILY", amount)


def test_open_cannot_impose_commitment():
    with pytest.raises(ValueError):
        validate_policy("OPEN", "FIXED_DAILY", 10)


def test_member_may_change_own_amount_but_not_creator_fixed_amount():
    validate_policy("COMMITMENT", "FIXED_DAILY", 10)
    fixed = SimpleNamespace(commitment_policy="FIXED_DAILY", daily_commitment_amount=10)
    assert validate_member_amount(fixed, 10) == 10
    with pytest.raises(ValueError):
        validate_member_amount(fixed, 20)
    assert validate_member_amount(SimpleNamespace(commitment_policy="MEMBER_CHOICE"), 20) == 20
