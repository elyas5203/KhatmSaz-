# F2: Cancel / Join Concurrency & Refund Reliability

## Problem
1. **Join vs Cancel Concurrency (Race Condition):** Concurrent requests to `join_via_token` (or `approve_join_request`) and `cancel_khatm` could interleave such that `cancel_khatm` sees `count_for_khatm == 0`, while `_complete_join` simultaneously inserts a new participation. This leaves an active member inside a cancelled khatm.
2. **Double Refund Vulnerability:** `refund_purchase_invoice` incorrectly interpreted a missing `PAID` invoice as "never existed", falling back to `refund_cash`. Since `mark_invoice_refunded` sets the status to `REFUNDED`, a subsequent concurrent (or repeated) `cancel_khatm` call would find no `PAID` invoice, assume it was a legacy khatm, and incorrectly grant another `refund_cash`!

## Resolution
- Added `get_by_id_for_update` in `khatm/repository.py` and `get_khatm_for_update` in `khatm/service.py` to acquire row-level locks on `Khatm`.
- Changed `join_via_token`, `approve_join_request`, and `cancel_khatm` to use `get_khatm_for_update`, completely serializing join and cancel operations for the same khatm.
- Added `get_invoice_by_resource` to `wallet/repository.py` which retrieves the invoice ignoring `status`.
- Updated `refund_purchase_invoice` to use `get_invoice_by_resource`. If an invoice exists but is not `PAID`, it immediately raises `InvalidPaymentError`, preventing the `refund_cash` fallback for already refunded invoices.

## Testing
- Wrote a new unit test in `tests/test_audit_c01.py` capturing the `refund_purchase_invoice` double refund logic using `pytest` and `monkeypatch`.
- Tested the original code (test failed due to fallback `refund_cash`).
- Tested the new code (test passed by correctly raising `InvalidPaymentError`).
- Verified full suite stability (`11 failed, 299 passed`, matching the baseline failures).

## Files Changed
- `src/khatmsaz/modules/khatm/repository.py`
- `src/khatmsaz/modules/khatm/service.py`
- `src/khatmsaz/modules/khatm_workflow/service.py`
- `src/khatmsaz/modules/wallet/repository.py`
- `src/khatmsaz/modules/wallet/service.py`
- `tests/test_audit_c01.py`
