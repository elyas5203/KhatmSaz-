"""Owner-defined daily quantity policy, independent of Quran/devotional units."""

MEMBER_CHOICE = "MEMBER_CHOICE"
FIXED_DAILY = "FIXED_DAILY"


def validate_policy(khatm_type, policy=MEMBER_CHOICE, daily_amount=None):
    if policy not in {MEMBER_CHOICE, FIXED_DAILY}:
        raise ValueError("Unknown commitment policy")
    if policy == FIXED_DAILY:
        if khatm_type != "COMMITMENT":
            raise ValueError("Only committed khatms may require a fixed daily amount")
        if not isinstance(daily_amount, int) or isinstance(daily_amount, bool) or daily_amount <= 0:
            raise ValueError("A positive fixed daily amount is required")
    elif daily_amount is not None:
        raise ValueError("Member-choice khatms cannot impose a fixed daily amount")


def validate_member_amount(khatm, amount):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("A positive reading amount is required")
    if getattr(khatm, "commitment_policy", MEMBER_CHOICE) == FIXED_DAILY:
        if amount != khatm.daily_commitment_amount:
            raise ValueError("The creator's fixed daily amount cannot be changed by a member")
    return amount
