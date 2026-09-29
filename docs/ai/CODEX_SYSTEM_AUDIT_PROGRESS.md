# Codex system audit progress — 2026-09-29

Resumable implementation ledger for the owner's reminder/settings/plan/join/
broadcast review. `TODO`, `IN-PROGRESS`, `DONE` are evidence-based only.

## Requirements

1. **Automatic scheduled delivery for every khatm mode — DONE (code/tests)**
   - Audit all reminder-engine branches (committed Quran, open Quran,
     recurring quantity commitments, open scheduled devotionals).
   - Every actionable share message must carry an identity-bound completion
     button and produce a clear confirmation.
   - Verify exact local time, restart catch-up, and once-per-period dedupe.

2. **Member settings reflect real member choices — DONE (home menu)**
   - Remove global audio/reciter and other creator-owned content policy from
     the member settings home.
   - Keep only choices that truly belong to the member/account.

3. **Canonical Quran edition — DONE**
   - New Quran creation always uses Madina/Hafs, 604 pages, without asking.
   - Historical editions remain readable only for compatibility.

4. **Exactly FREE and PRO, balance-threshold PRO — DONE**
   - Remove BASIC from active domain/UI/admin choices, with safe migration of
     historical BASIC rows.
   - PRO is derived/activated when wallet balance reaches the admin-configured
     threshold; Persian UI must contain no leaked i18n keys.

5. **Plain Persian validation and stable contact identity — DONE**
   - Custom wallet minimum/maximum errors use Persian digits/wording.
   - Contact-to-creator preserves the sender's platform username/identifier;
     profile editing cannot erase the routing identity.

6. **No skip-today behavior anywhere — DONE**
   - Remove buttons, callbacks, commands, creator settings and active service
     behavior for skipping a required share. Preserve old DB columns only when
     removal would create avoidable migration risk; they must become inert.

7. **Creator broadcast center — TODO**
   - Creator web panel supports one khatm or all distinct active members.
   - Delivery channels: Telegram, Bale, SMS.
   - Admin controls allowance/count and free/paid pricing per channel; every
     creator broadcast requires admin approval before delivery.

8. **Family-specific onboarding and intro media — TODO**
   - Four admin-configured intro images: Quran, Salawat, Dua/Ziyarat, La'an;
     shared across language/platform bots, with text-only fallback.
   - Commitment/count wording and units are family-specific.
   - Join setup maintains one editable summary message and removes/edits only
     messages created by that join flow, never unrelated history.

## Evidence gathered

- Graphify graph at audit start: 3776 nodes / 13559 edges / 238 communities.
- Reminder call graph identifies four delivery branches under
  `reminder_engine.run_once`.
- Creator broadcast already has bot-only one-khatm/all-member targeting, but
  pricing is hard-coded (3 free/week, then fixed prices), paid sending is
  disabled, there is no SMS/Bale cross-channel selection, and no creator web
  page/admin policy model.
- Quran creation registry already exposes only `madina-hafs`, but bot and web
  still render a redundant edition question/select.
- Skip-today UI is partly removed from buttons, but active model/service/web
  settings and workflow functions remain.
- Current plan enum/schema still contains BASIC and current PRO purchase spends
  wallet funds; this contradicts the newly stated balance-threshold rule.

## Delivery log

- Baseline commit: `df83fd9` on `main`, clean working tree.
- Reminder/settings/canonical-edition batch: scheduler scans every minute;
  member-bot/platform routing is strict; committed Quran, open Quran, open
  scheduled khatms and regular quantity commitments receive a khatm- or
  participation-bound completion button; delivery logs are written only after
  a real keyboard-message success. Regular completion is ownership-checked,
  deduplicated per sent occurrence and produces a confirmation.
- Removed audio/reciter/digest from the member settings home. New Quran khatms
  silently use Madina/Hafs (604 pages). Wallet custom-amount validation uses
  localized digits. Web welcome-text edits preserve the creator contact line.
- Evidence: non-integration suite **189 passed, 86 deselected** before the last
  keyboard regression assertion; no migration added in this batch.
- Plan batch: effective tier is derived from total wallet funds against the
  enabled admin-set PRO threshold. No purchase/deduction route remains, PRO
  creation is free, BASIC is excluded from active admin/UI choices, and the
  missing «نامحدود» translation no longer leaks its key. Evidence:
  **192 passed, 86 deselected**; DEC-PY-0098; no migration.
- No-skip batch: the legacy database column remains compatibility-only and
  defaults false; setter/workflow APIs and every call-site parameter are gone.
  Pausing reminders no longer releases the current owed portion. Evidence:
  **193 passed, 85 deselected**; no migration.
