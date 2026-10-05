# Redesign verification checkpoint — 2026-10-05 [Codex]

Status: LOCAL PASS. Production migration/restart/live QA are not included.

Environment: Codex-created PostgreSQL 18, loopback port 55439, database khatm_redesign_20261004. Messenger calls in redesign integration scenarios are fakes. No production server, database, deployment, commit or push.

## Executed checks

1. Final RUN_INTEGRATION_TESTS=1; python -m pytest -q --tb=short: **564 passed in 39.63s**. No skips or failures.
2. Subsequent routing-language/audio-only and retained-debt cases: python -m pytest -q tests/test_redesign_delivery_integration.py tests/test_reminder_redesign_p2.py tests/test_today_early_delivery.py tests/test_quran_delivery_integration.py --tb=short: **33 passed in 6.15s**.
3. Reviewed migration; python -m alembic upgrade head: PASS on local disposable database (already upgraded). python -m alembic heads: share2026100501, one head.
4. python -m compileall -q src/khatmsaz: PASS. git diff --check: PASS.
5. mypy: NOT RUN; not installed/configured as a required checker in the inspected environment.

Earlier full failures were retained in the conversation: 421 passed/16 failed, then a run interrupted by loss of disposable PostgreSQL availability (405 passed/32 failed), then 434 passed/3 failed. Repairs included real fixture setup, strict audit assertions, scoped legacy scans and cleanup of test-owned foreign-key records. No test was skipped to get a passing result.

## Remaining production acceptance work

- Apply the reviewed additive migration on VPS, restart services, and perform one real Persian delivery/completion QA on Telegram and Bale.
- Confirm production scheduler health and rollback readiness according to DEPLOY.md.

## Raw full-suite output and current code hashes

The hashes are of the current checkpoint; the full-suite output above precedes the explicitly listed subsequent small edits.

```text
........................................................................ [ 16%]
........................................................................ [ 32%]
........................................................................ [ 49%]
........................................................................ [ 65%]
........................................................................ [ 82%]
........................................................................ [ 98%]
.....                                                                    [100%]
437 passed in 23.28s

EBBB8876105FBEB8D88F2EC65FE4BAD215AB6957711E3620CF73BCDDAC4627C4  C:\xampp\htdocs\Khatm\src\khatmsaz\modules\share_occurrence\delivery.py
78BC03DD4FA584213951C6E0003BBA2B946E23D0BDAF64002221795544DD4DA0  C:\xampp\htdocs\Khatm\src\khatmsaz\bot\occurrence_adapter.py
F23A186C80A12F26CE405C735732ABAA4F3557C9DE9D9C1CBAE57CD6CC3EEBD2  C:\xampp\htdocs\Khatm\src\khatmsaz\bot\handlers\report.py
20D71FEDEB91AD4B68506C5AA4AE12AD137697F63E2C01E79BAED66C5BD8E2F5  C:\xampp\htdocs\Khatm\tests\test_redesign_delivery_integration.py
`
