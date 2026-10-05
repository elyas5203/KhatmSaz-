# دفتر باگ‌های ممیزی

در آغاز هیچ باگی با اجرای این مستر بازتولید نشده است. سرنخ‌های زیر از اجرای پیشین آمده‌اند و وضعیتشان `UNVERIFIED_LEAD` است:

- `tests/test_i18n_coverage.py::test_no_literal_t_key_is_missing`
- `tests/test_join_records_bot_instance.py::test_join_via_token_threads_bot_instance_id`
- `tests/test_join_records_bot_instance.py::test_quran_join_is_member_controlled_without_auto_allocation`
- `tests/test_member_bot_fixes.py::test_next_portion_delivery_records_daily_reminder_to_prevent_duplicate`
- `tests/test_migration_graph.py::test_bot_instance_migrations_are_ordered_before_intro_image`
- چهار پارامتر `tests/test_reminder_redesign_p2.py::test_accept_removes_only_consent_after_join_or_registration`
- `tests/test_reminder_redesign_p2.py::test_consent_delete_failure_does_not_fail_join`
- `tests/test_reminder_redesign_p2.py::test_failed_join_does_not_remove_consent_card`
- چند head در Alembic؛ `upgrade head` در اجرای پیشین شکست خورده. بدون بازبینی تاریخچه، migration حذف/renumber یا stamp نشود.

## الگوی هر باگ — کپی کنید، نمونه را نتیجه تلقی نکنید

```text
ID / title:
Status: OPEN / REPRODUCED / FIX_IN_PROGRESS / FIXED_UNVERIFIED / VERIFIED / REOPENED
Severity: P0 (تخریب/افشای گسترده)، P1 (مسیر اصلی مسدود/اثر مالی یا بدهی غلط)، P2 (خطای محدود)، P3 (کیفیت)
Owner / discovered_at / package / item IDs / run IDs:
HEAD / file:line / function / graph callers and callees:
Authoritative rule: DEC/domain/user instruction + exact section
Environment and synthetic seed:
Steps to reproduce:
Expected:
Actual:
Evidence path / failing test node:
Root cause: verified / hypothesis (تفکیک شود)
Proposed minimal fix / allowed files / files not to change:
Data or migration impact / external side effects:
Regression tests and boundary cases:
Before result:
Fix commit or diff:
After result / full suite result:
Independent recheck of original symptom:
Residual risk / blockers / next step:
Status history (append-only):
```

باگ fixture یا تست منسوخ را از باگ محصول جدا کنید. برای تغییر انتظار تست، مرجع تصمیم لازم است؛ سبزکردن عددی suite کافی نیست.

## BUG-20261004-001
- **Status**: OPEN
- **Description**: Missing i18n key `portions.no_capacity_left`
- **Impact**: Translation errors
- **Proposed Fix**: Add to _STRINGS in `i18n/__init__.py`

## BUG-20261004-002
- **Status**: OPEN
- **Description**: Outdated tests in `test_join_records_bot_instance.py` regarding `force_open` for OPEN/COMMITMENT khatms
- **Impact**: Test failures
- **Proposed Fix**: Update assertions to expect `force_open = True` for OPEN and `False` for COMMITMENT

## BUG-20261004-003
- **Status**: OPEN
- **Description**: Mock `UserSettings` in `test_member_bot_fixes.py` lacks `quran_audio_enabled` attribute
- **Impact**: Test failure during settings retrieval
- **Proposed Fix**: Add `quran_audio_enabled=True` to the mock `SimpleNamespace`

## BUG-20261004-004
- **Status**: OPEN
- **Description**: Multiple Alembic heads (`res20261003120539`, `res20261003123135`)
- **Impact**: Migration failure
- **Proposed Fix**: Merge heads or correct `down_revision`

## BUG-20261004-005
- **Status**: OPEN
- **Description**: Outdated tests in `test_reminder_redesign_p2.py` for consent deletion
- **Impact**: Test failures
- **Proposed Fix**: Update tests to expect immediate and repeated deletion calls to match the new behavior

## 2026-10-04 — Codex direct audit: AUD-C01 to AUD-C05

See [static evidence](evidence/RUN-20261004-CODEX-001.md). Status: OPEN; static findings, no experimental reproduction or VPS verification. C01/C02 high priority; C05 requires middleware/reachability review. Fixes are not authorized in this analysis pass.
