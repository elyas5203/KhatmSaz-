# F5: Quran and Creator's Fixed Rules

## Problem
Based on `RUN-20261004-CODEX-002.md` and `DEC-PY-0116`, for a Quran Khatm with a `FIXED_DAILY` policy, the amount is fixed by the creator and should determine the daily page goal for the member without using the general numeric counting approach.
1. The static analysis found that `join_flow._save_delivery_time` incorrectly assigned a `REGULAR` schedule mode to `FIXED_DAILY` Quran khatms (via `set_commitment_schedule`). Because Quran uses `KhatmPortion` or `open_reading_pages_per_day`, not a scalar `CommitmentDelivery`, it broke the delivery engine (the `report` function skips `REGULAR` early before Quran allocation).
2. The user could trigger `regular_done` button clicks for a Quran khatm, which would write numeric values to `open_contribution_service.log_contribution` incorrectly, without actually reading Quran pages or valid portions.
3. The discrepancy between the manual `_send_recitation_content` (for Salawat) and the automated `send_devotional_content` raised alarms. The manual path isn't used for Quran, but the concern was valid regarding misusing numeric logs.

## Resolution
1. **Join Flow Correction:** Modified `src/khatmsaz/bot/handlers/join_flow.py` inside `_save_delivery_time`. If the khatm is `FIXED_DAILY`, it now checks `khatm.template_type`. If it's a `QURAN_PAGE` khatm, it correctly sets `open_reading_pages_per_day` to `khatm.daily_commitment_amount` instead of applying a `REGULAR` schedule.
2. **Preventing Erroneous Button Clicks:** In `src/khatmsaz/bot/handlers/member_commitment.py`, inside `confirm_regular_occurrence`, added an explicit check. If `khatm.template_type == KhatmTemplateType.QURAN_PAGE`, it immediately answers the callback with an invalid alert and `return`s. This fully mitigates any legacy corrupted data where a Quran participant might have received a REGULAR done button.

## Testing
- Verified that all unit tests still pass (retaining the exact same 11 baseline failures).
- No new regressions were introduced by fixing the `join_flow` and `member_commitment` behavior.

## Files Changed
- `src/khatmsaz/bot/handlers/join_flow.py`
- `src/khatmsaz/bot/handlers/member_commitment.py`
