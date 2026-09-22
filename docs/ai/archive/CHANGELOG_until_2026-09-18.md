# CHANGELOG archive — up to 2026-09-18

> Older entries moved out of `CHANGELOG.md` on 2026-09-20 to keep that
> file readable without burning tokens on ancient history. Nothing here
> was deleted or edited — verbatim continuation, newest still at top.

## 2026-09-18 — Removed "copy khatm"

- Owner asked to remove the "🔁 کپی این ختم" feature entirely. Deleted the
  keyboard buttons/keyboards, the three bot callback handlers (preview,
  cancel, confirm), and `khatm_workflow.service.copy_khatm`. Removed its now-
  dead integration test and the resulting unused imports.
- Fast unit suite: 41 passed, 56 skipped (integration tests need
  `RUN_INTEGRATION_TESTS=1` + real Postgres). Live bot restarted cleanly.

## 2026-09-18 — Creator Excel export + admin-panel broadcast moderation

- Added `/creator/khatms/{id}/export.xlsx`: full member info (name, phone,
  province, city, gender, join date, completed portions, missed reminders,
  contribution/surplus) as a downloadable Excel file for the khatm's own
  creator. Added `openpyxl` dependency.
- Added `/broadcasts` admin-panel page (gated on `MODERATION_MANAGE`) so
  creator group-message requests can be approved/rejected with one click
  instead of only via bot commands; reuses the existing `broadcast_service`.

## 2026-09-18 — Button-only settings menu

- Replaced the text-heavy ⚙️ تنظیمات screen (which told users to type
  `/language`, `/timezone`, `/font`, `/reminder`, `/digest`, `/sms`,
  `/content`) with a full inline-keyboard tree in a new
  `bot/handlers/settings_menu.py`, registered in `bootstrap.py`.
- Every preference (language, font size, reciter, translation/tafsir,
  reminder hour, daily digest, SMS reminders, timezone) is now reachable by
  tapping only, per the project's standing "click, don't type" rule. Reuses
  existing service-layer functions with no new business logic.
- Verified via clean module import and a live bot restart against real
  Postgres with clean startup logs and no exceptions.

## 2026-09-18 — Fixed live Telegram creator-card callback overflow

- Reproduced `BUTTON_DATA_INVALID` in the real bot when opening My Khatms.
- Replaced the over-64-byte completion-announcement callback with compact
  `cat:<uuid>` data and removed a duplicate registered handler.
- Added a regression assertion over every creator-card button's UTF-8 byte
  length. Full suite: **98 passed**.

## 2026-09-18 — Foreign-verification queue in the admin web app

- Added a mobile-first `/phone-verifications` page showing each pending
  foreign number with user, location, purpose and local request time.
- Added CSRF-protected approve/reject actions that reuse the domain service;
  there is no weaker web-only identity path.
- Restricted view and mutation to Super Admin/Support permission and added a
  conditional navigation entry. Real PostgreSQL + ASGI tests cover rendering,
  CSRF rejection, approval, persistent claim, empty state and denial to the
  Finance role. Full suite: **98 passed**.

## 2026-09-18 — Admin-reviewed verification for users outside Iran

- Added migration `q7r8s9t0` and a persistent pending/approved/rejected manual
  phone-verification lifecycle for non-`+98` numbers.
- Creator verification and phone replacement now route foreign numbers to
  manual review instead of attempting Kavenegar. Configured Super Admins get
  inline approve/reject controls; Support admins can list pending work with
  `/admin_phone_requests`.
- Approval creates the normal permanent verified phone claim, safely replaces
  an old claim when applicable, synchronizes the profile and notifies all
  linked platforms. Iranian bypass, duplicate/race behavior, takeover, reject,
  and replay are protected. PostgreSQL and full suites pass: **96 passed**.
- Payment rules for foreign creators remain intentionally unchanged pending a
  later explicit decision from the project owner.

## 2026-09-18 — Native Telegram command picker

- Added a short Persian Telegram command menu covering only functional,
  high-frequency user journeys; users no longer need to memorize command
  names from help text.
- Added `/new_khatm` and `/my_khatms` aliases over the existing button flows.
- Startup installs both the default and `fa` menu, fails non-fatally if the
  platform API is unavailable, and leaves Bale untouched until live parity is
  known. Unit and full regression suites pass: **93 passed**.

## 2026-09-18 — Kavenegar production SMS adapter

- Implemented `KavenegarSmsProvider` against the official REST send endpoint
  and registered it under `SMS_PROVIDER=kavenegar`.
- Added Iranian E.164 receptor conversion, HTTP/provider-status validation,
  message-id capture, safe timeout/invalid-response handling, and errors that
  do not expose the path-embedded API key.
- Documented `SMS_API_KEY`, `SMS_SENDER`, and optional `SMS_API_BASE_URL` in
  the environment and Persian deployment guide. Mock-transport tests cover
  successful send, provider rejection, missing config and factory selection;
  full suite: **90 passed**.

## 2026-09-18 — Verified creator gate before every khatm creation

- The main create button now requires a complete short profile and verifies
  its saved number by OTP when the account has no verified phone claim.
  `/verify_phone` is also available as a direct, documented entry point.
- Ordinary creation and copy-khatm both recheck verification at confirmation,
  before charging or writing anything. A failed/disabled SMS provider leaves
  the wallet and khatm list untouched; a number owned elsewhere points the
  user to the safe account-link flow.
- Added a distinct masked `PHONE_VERIFY` audit event and PostgreSQL coverage
  for first-time creator verification. Full suite: **86 passed**.

## 2026-09-18 — Secure phone change with history preservation

- Added `/change_phone`, with clear Persian guidance and OTP delivery to the
  replacement number through the configured SMS provider.
- Kept the canonical User unchanged while atomically revoking the previous
  verified claim, creating the new claim, and synchronizing the profile phone;
  wallet, khatms, memberships, platform links and history therefore remain
  attached to the same account.
- Rejected numbers owned by another account, serialized same-number ownership
  changes in PostgreSQL, prevented `/profile` from bypassing OTP, and recorded
  a masked `PHONE_CHANGE` audit event. PostgreSQL tests cover preservation and
  takeover rejection; full suite: **86 passed**.

## 2026-09-17 — Timezone-aware automatic monthly report

- Added a scheduler-backed previous-month report with Quran-page, Salawat and
  completed-khatm totals, using each user's timezone and fa/ar/en positive
  copy. Misses and competitive ranking are deliberately absent.
- Added configurable `MONTHLY_REPORT_DAY`/`MONTHLY_REPORT_HOUR`; a scan after
  downtime catches up once instead of permanently missing the month.
- Added per-user `YYYY-MM` deduplication in migration `p6q7r8s9`. Empty months
  are processed silently to avoid spam. Real PostgreSQL aggregation and
  delivery tests pass; full suite: **83 passed**.

## 2026-09-17 — Scoped creator web dashboard and granular member report

- Added `/creator_web_login` and a separate eight-hour `CREATOR` web session;
  regular creators do not receive any admin permission and can access only
  khatms whose `creator_user_id` is their own.
- Added the mobile `/creator` dashboard and private member detail/search page
  with full phone, location, gender, join time, membership/Backup status,
  completion count, misses, contributions, and surplus.
- Added immutable counted/surplus snapshots to each new open contribution so
  per-member reporting remains correct after the global goal is exceeded.
- Migration `o5p6q7r8` is applied. PostgreSQL + ASGI tests cover session scope,
  cross-owner denial, sensitive fields, search and surplus; full suite:
  **82 passed**.

## 2026-09-17 — Safe automatic completion messages

- Added migration `n4o5p6q7` with completion time, creator announcement choice,
  and an idempotent announcement timestamp.
- Added a positive fa/ar/en completion summary for creator and active members,
  delivered on every linked Telegram/Bale identity after a five-minute undo
  grace period. An atomic claim prevents duplicate broadcasts.
- Added a one-tap `پیام پایان: روشن/خاموش` creator control. Final Quran-page
  completion now retains its five-minute Undo action and reopens the khatm if
  used before announcement.
- Fixed an undefined callback in the free-contribution inactive-khatm path and
  fixed copy-khatm support for pause/snooze/miss/schedule/completion settings.
  Real PostgreSQL completion, grace, idempotency, cross-platform recipient, and
  copy tests pass; full suite: **80 passed**.

## 2026-09-17 — Web-only sensitive activity timeline

- Added `/audit`, a mobile-first, read-only timeline for the append-only audit
  trail required by SPEC Q104.
- Each row resolves actor and target names, Tehran-local time, a Persian action
  label, stable event code, target khatm, and structured details; event-code
  filtering and a clear empty state keep the page simple.
- Restricted the page and navigation to Super Admin/Operations access. No
  mutation or deletion endpoint exists. PostgreSQL + ASGI tests cover delegated
  access, denied finance access, filtering, details, and empty state; full
  suite: **77 passed**.

## 2026-09-17 — Self-service OTP account linking

- Added `/link_account` for linking a newly provisioned Telegram/Bale identity
  to an existing phone-verified account, including same-platform account
  replacement required by the original specification.
- Normalized common Iranian phone forms to E.164 and kept OTP delivery behind
  the `SmsProvider`; production never reveals codes in chat or logs.
- Added a fail-closed merge policy: only a pristine provisional account may be
  absorbed automatically; profiles, khatms, participations, or wallet activity
  require support review. Successful links preserve an `AccountMerge` audit
  record and mark the source account merged.
- Added PostgreSQL integration coverage for successful reassignment and unsafe
  merge rejection. Full suite: **76 passed**.

## 2026-09-17 — Public cross-platform invitation page

- Added `/join/{token}` as a no-index, mobile-first public preview with title,
  creator privacy policy, niyyat, welcome text, membership type, and live
  active-member count.
- Added Telegram/Bale continuation choices and clear copy that previewing does
  not itself join the khatm.
- Cancelled invitation tokens now resolve as invalid; inactive khatms and bad
  tokens fail closed with a safe Persian page.
- Added `PUBLIC_WEB_BASE_URL`; when production HTTPS is configured, new invite
  messages and QR codes point to the cross-platform page. PostgreSQL + ASGI
  regression coverage passes; full suite: **73 passed**.

## 2026-09-17 — Delegated admin RBAC

- Added migration `m3n4o5p6` and revocable grants for content, finance,
  support, moderation, marketing, and operations administrators.
- Added a single role-to-permission policy shared by Telegram/Bale handlers,
  dashboard sessions, routes, and navigation; Super Admin implicitly retains
  every permission.
- Added `/admins` for user search, one-tap role assignment/revocation, and a
  list of active delegated roles, plus matching bot commands.
- Every role change is audited; revoked users lose delegated session access on
  the next request. PostgreSQL and authenticated ASGI tests cover scope and
  revocation; full suite: **72 passed**.

## 2026-09-17 — Guided in-bot help for inexperienced users

- Added `/help` with six button-driven, step-by-step Persian topics: joining,
  portions, creation, wallet, settings, and creator management.
- Linked the full guide from Settings and the welcome message while preserving
  the intentionally shallow five-action home menu.
- Added structural coverage for every help topic and callback; full suite:
  **69 passed**.

## 2026-09-17 — Coupon engine and finance administration

- Added migration `l2m3n4o5`, percentage/fixed coupons, validity and minimum
  purchase checks, total/per-user limits, and an optional maximum discount.
- Coupon validation and redemption lock the coupon row; invoice gross,
  discount, and net snapshots remain auditable under concurrent use.
- Added `/coupon CODE`, `/admin_coupons`, `/admin_coupon_set`, and
  `/admin_coupon_toggle`, plus an RTL mobile `/finance` page for coupon
  management, totals, and recent invoices.
- Kept coupon entry optional in the paid creation confirmation so users without
  a code see no extra mandatory step; invalidated codes fall back safely to the
  same confirmation screen.
- Added PostgreSQL and authenticated ASGI coverage; the current full suite is
  **69 passed**.

## 2026-09-17 — Internal invoices and paid-khatm receipt lifecycle

- Added migration `k1l2m3n4` and append-only amount snapshots for wallet
  top-ups and paid khatm creation.
- Bound paid-creation invoices to the khatm UUID; eligible cancellation now
  marks that invoice refunded and credits Cash Balance exactly once.
- Added `/invoices` for a short Persian list of the user's latest receipts.
- Added a real PostgreSQL paid-create/refund scenario and invoice assertions
  to PayPing callback tests.
- Fixed khatm creation persistence for the already-existing reminder-tone and
  content-delivery-mode wizard values; full suite: **67 passed**.

## 2026-09-17 — PayPing v3 top-up flow

- Added the official PayPing v3 create/verify adapter with Bearer auth,
  Toman amounts, safe error normalization, and strict response matching.
- Added `/wallet` and `/topup` one-tap amounts and a Persian guided redirect
  flow.
- Added the public form callback with locally bound `clientRefId`, amount and
  payment-code checks, PSP verification, and atomic replay protection.
- Added unit plus real PostgreSQL/ASGI tests for success, replay, forged
  amounts, secure URLs, and secret-safe errors; full suite: **66 passed**.
- Live payment remains disabled until a dedicated API token and production
  HTTPS callback are configured and tested.

## 2026-09-17 — Private-channel Quran delivery and opt-in audio

- Added a verified, versioned map of all 604 image pages and 301 audio posts
  covering all 604 pages, plus idempotent seed/import of forwarded posts from
  the configured private Quran channel.
- Added source-message forwarding with de-duplication, Parhizgar as the source
  reciter, and exact 604-page coverage reporting.
- Added a default-off Quran audio preference, one-tap settings controls, and a
  plain-language four-step participant guide.
- Added migration `j0k1l2m3`, unit/integration coverage, and production-safe
  domain/PayPing configuration placeholders; full suite: **61 passed**.
- Live source access remains pending because the bot is not yet a member of the
  private channel.

## 2026-09-16 — Mobile-first admin web dashboard

- Added a FastAPI/Jinja administration dashboard that runs alongside bot
  polling and is reachable from phones on the same local network.
- Added role-gated, opaque eight-hour sessions issued by
  `/admin_web_login`, HttpOnly cookies, CSRF checks, no-store/security headers,
  logout revocation, and audit logging for state-changing admin actions.
- Added responsive Persian RTL views for system metrics and pending queues,
  khatm list/detail analytics, user search/moderation, and message templates.
- Verified the UI at a 390×844 viewport with no browser console errors and
  added a real PostgreSQL + ASGI route test; full suite: **55 passed**.

## 2026-09-16 — Message-template lifecycle controls

- Added immutable template history listing and exact-version enable/disable
  controls in both Telegram admin commands and the web dashboard.
- Disabled latest versions now fall back to the newest enabled version; all
  toggles are audited.
- Added PostgreSQL integration coverage and verified history live in Telegram.

## 2026-09-16 — Tracked invitation QR

- Added `/khatm_qr` and the inline `🔳 QR دعوت` creator action.
- Each QR creates a tracked reusable invitation and encodes its platform deep
  link into an in-memory PNG; creator ownership and active status are checked.
- Added `qrcode[pil]`, unit coverage, and live Telegram verification; full
  suite: **52 passed**.

## 2026-09-16 — Creator analytics and invite funnel

- Added `/khatm_stats` and an inline `📈 آمار ختم` button for creator-owned
  khatms.
- Added member, portion, contribution, and invitation conversion metrics;
  successful invitation acceptance is now persisted.
- Added real PostgreSQL coverage and verified the command live in Telegram;
  full suite: **50 passed**.

## 2026-09-16 — Safe account deletion

- Added migration `i9j0k1l2`, soft-deletion state, and `/delete_account` with
  explicit confirmation.
- Active commitments and active creator-owned khatms block deletion; open
  memberships are closed and personal profile fields are cleared.
- Added real PostgreSQL coverage; verification: **49 passed**.
- Live Telegram test correctly blocked the test account with unresolved
  obligations, without deleting it.

## 2026-09-16 — Live verification of open-khatm schedule

- Verified `/khatm_schedule <id> daily` in the live Telegram bot and received
  the success response.
- Restored the same owned test khatm with `/khatm_schedule <id> off`; no
  temporary schedule remains.

## 2026-09-16 — Inactivity-safe Quran delegation

- Added `users.last_activity_at` with migration `h8i9j0k1` and middleware
  activity tracking.
- Assigned Quran portions are delegated after 30 days of inactivity to an
  available opted-in Backup Reader, without recording a miss for the original
  participant.
- Added a real PostgreSQL integration scenario; verification: `48 passed`.

## 2026-09-16 — Creator member detail

- Added `/khatm_member <khatm_id> <participation_id>` for a guarded,
  creator-only detail view of an active participant.
- The view reports assignment/progress, rolling-window misses, reminder and
  pause state, and commitment/backup-reader flags.
- Verification: integration suite `47 passed`.

## 2026-09-16 — Creator report buttons

- Added inline management buttons for member view, needs-attention queue, and
  CSV export alongside the existing copy/cancel actions.
- Callback routes reuse the guarded command handlers and creator ownership
  checks.
- Verification: integration suite `47 passed`.

## 2026-09-16 — Creator CSV export

- Added `/khatm_export <khatm_id>` to download the creator's active-member
  report as UTF-8 CSV.
- Export includes display name, commitment/backup flags, progress, and
  rolling-window miss count; data is generated in memory and not persisted.
- Verification: integration suite `47 passed`.

## 2026-09-16 — Creator needs-attention queue

- Added `/khatm_attention <khatm_id>` to report active members with recorded
  missed-deadline follow-ups in the khatm's configured rolling window.
- Enforced creator-only access and an explicit empty-state response.
- Verification: integration suite `47 passed`.

## 2026-09-16 — Creator member progress view

- Added `/khatm_members <khatm_id>` for a creator-only active-member and
  progress summary, including committed and backup-reader flags.
- Fixed Telegram HTML parsing in the command's format-error response.
- Verification: integration suite `47 passed`.

## 2026-09-16 — Message-template placeholder validation

- Added shared validation for template placeholder syntax and supported names.
- `/admin_template_set` now rejects unknown or malformed placeholders before
  saving a new template version.
- Verification: integration suite `47 passed`.

## 2026-09-16 — Open schedules and moderated covers

- Added creator-configurable open-khatm schedules: daily, selected weekdays,
  fixed intervals, one date, or off; the reminder worker sends deduplicated
  prompts at each member's reminder hour.
- Added moderated per-platform covers: creator submission, Super Admin review
  queue, approve/reject audit events, and approved-cover invite previews.
- Added creator controls for pause/snooze, custom pause/snooze end times,
  configurable miss thresholds, date-based khatm ending, completion guards,
  and My Khatms status buckets.
- Verification: migrations applied to real PostgreSQL; integration suite
  `43 passed`. Telegram smoke tests covered live admin routing and status UI.

## 2026-09-16 — Reminder tone presets

- Added per-khatm `friendly`, `formal`, `devotional`, and `short` reminder
  tones, selected in the creation wizard and preserved when copying a khatm.
- Non-default tones use seeded locale-aware template keys with a friendly
  fallback.
- Verification: migration applied and full PostgreSQL integration suite
  `26 passed`.

## 2026-09-16 — Safe cosmetic edits after activation

- Added creator-only `/khatm_edit_title` and `/khatm_edit_welcome` commands.
- Only active khatms may be edited, and structural settings are not exposed;
  `clear` removes an existing welcome message.

## 2026-09-16 — Per-khatm creator identity display

- Added creator display choices for full name, first name, pseudonym, and
  anonymous benefactor; the selected identity is shown on join messages.
- Pseudonyms are bounded to 64 characters and HTML-escaped; cloning preserves
  the setting. Migration and rendering tests pass.

## 2026-09-16 — Shallow home navigation

- Added «امروز», «گزارش من», and «تنظیمات» to the home reply keyboard.
- Today lists active assigned portions and reuses the existing completion and
  content actions; Settings documents the available preference commands.

## 2026-09-16 — Khatm-request approval runtime fix

- Fixed `/admin_approve_request` and `/admin_reject_request` so they resolve
  the active Telegram/Bale platform before looking up the administrator.
- The request queue now reaches its audit and cross-platform notification path
  instead of failing on an undefined local variable.

## 2026-09-16 — Invite landing preview

- Deep-link invites now show the khatm title, niyyat, creator identity, member
  count, and welcome text before any membership action occurs.
- Registration and commitment consent start only after explicit confirmation;
  invalid and canceled previews leave the user unjoined.

## 2026-09-16 — Public visibility wizard option

- Added the public visibility choice to khatm creation and its confirmation
  labels, completing the public/unlisted/private selector.

## 2026-09-16 — Creator skip-today toggle

- Added `/khatm_skip_today <khatm_id> on|off` for owners of committed Quran
  khatms; the service rejects other owners and khatm types.

## 2026-09-16 — Moderated creator messages

- Added `/khatm_message <khatm_id> <text>` to submit a creator message for
  moderation instead of sending it directly.
- Added Super Admin listing and approve/reject commands; approved messages are
  delivered to active members across linked Telegram/Bale identities and
  recorded in the audit log.
- Verification: migration applied after enum-creation hardening and full
  PostgreSQL integration suite `32 passed`.

## 2026-09-16 — Canonical Quran page asset registry

- Added a 604-page-only registry for image, audio, and text asset references.
- Range resolution is exact and contiguous; incomplete ranges return no result.
- Verification: migration applied and full PostgreSQL integration suite `22 passed`.

## 2026-09-16 — Assigned Quran content delivery

- Added a content action to assigned Quran portions.
- It sends only complete exact-range image/audio/text assets and falls back
  clearly when the library has no matching asset.
- Verification: real PostgreSQL delivery-policy test; full integration suite `23 passed`;
  bot polling restarted successfully.

## 2026-09-16 — Per-khatm content delivery mode

- Added creator-selectable `AUTO`, `PHOTO`, and `TEXT` delivery modes.
- Added `/khatm_content_mode <khatm_id> <auto|photo|text>` with ownership and
  input validation; live invalid-input smoke test passed.
- The same choice is now presented during the Quran creation wizard and is
  preserved when a khatm is copied.

## 2026-09-16 — Admin Quran media ingestion

- Added `/admin_quran_asset` guidance and media-caption handling for page images
  and reciter-specific audio.
- Telegram and Bale file references are stored separately; invalid page/kind/
  reciter inputs and duplicate identities are rejected.
- Verification: migration applied, platform-isolation integration test passed,
  and live Telegram help response passed.

## 2026-09-16 — Dua and ziyarat library

- Added complete text/audio records for admin-curated `DUA` and `ZIYARAT` items.
- Added `/admin_devotional_text`, `/admin_devotional_audio`, and
  `/devotional <slug>`; audio remains platform-scoped.
- Verification: migration applied, integration suite `24 passed`, and live
  Telegram missing-slug fallback passed.

## 2026-09-16 — Creator welcome message

- Added an optional 500-character welcome line to khatm creation and join
  messages; cloning preserves it and user-authored HTML is escaped.
- Verification: migration applied and full suite `25 passed`.

## 2026-09-16 — Translation and tafsir preferences

- Added independent per-user `/content translation on|off` and
  `/content tafsir on|off` settings.
- Preferences are advisory and only affect delivery when the corresponding
  library asset exists; live Telegram verification passed and was restored off.
- Verification: real PostgreSQL settings test; full integration suite `22 passed`.

## 2026-09-16 — Reading font-size preference

- Added `/font normal|large` backed by the per-user settings record.
- Verification: real PostgreSQL settings test and live Telegram toggle test
  passed; the test account was restored to normal size.

## 2026-09-16 — Reciter policy and favorite fallback

- Added per-khatm reciter whitelist storage and priority ordering.
- Added per-user `/reciter` favorite selection with whitelist-first fallback
  resolution; media delivery remains separate from this policy layer.
- Verification: real PostgreSQL reciter-policy integration test passed and live
  Telegram listing test passed.

## 2026-09-16 — Public khatm discovery

- Added `/public_khatms` for active `PUBLIC` khatms.
- Added direct join buttons; unregistered users enter the existing registration
  flow and committed khatms retain the pledge-consent gate.
- Verification: real PostgreSQL listing test passed and live Telegram smoke test
  correctly handled an empty public list.

## 2026-09-16 — Advertising reward credit MVP

- Added per-khatm advertising opt-in and append-only reward-rate history.
- Added `/admin_ad_rate` with audit logging.
- Eligible active members receive at most one Reward Credit after their first
  completed assigned action or first open contribution; the wallet transaction
  reference is idempotent.
- Verification: real PostgreSQL advertising integration test passed; live
  Telegram argument-validation smoke test passed.

## 2026-09-16 — Vendor-neutral SMS boundary

- Added the async `SmsProvider` contract and normalized `SmsSendResult`.
- Added a safe `noop` provider and factory rejection for unknown vendors;
  external SMS remains disabled until credentials and an adapter exist.
- Added `/sms on|off`; enabling requires a saved phone and clearly reports the
  current noop-provider limitation. Live Telegram toggle verification passed.
- Verification: default suite `9 passed, 6 skipped`; integration-enabled suite
  `15 passed`.

## 2026-09-16 — Plan pricing wired into khatm creation

- Creation and copy flows now resolve the authoritative charge from the active
  plan definition: fixed plans use `price_toman`, usage-based plans use
  `unit_price_toman`.
- Disabled plans or plans without `khatm.create` are rejected before creation.
- Verification: integration-enabled suite `12 passed`; bot restarted and
  polling successfully.

## 2026-09-16 — Plan definitions and feature entitlements

- Added persistent FREE/BASIC/PRO plan definitions with fixed/usage pricing
  fields and JSON feature entitlements.
- Added Super Admin commands `/admin_plans` and `/admin_plan_set`.
- Added feature-key checks that do not branch on plan names.
- Applied migration `o4c5d6e7f8a9`; integration-enabled suite `11 passed`.

## 2026-09-16 — Reminder locale selection

- Added `/language fa|ar|en` with validation and persistence in `user_settings`.
- Reminder, staged reminder, missed-deadline, and creator-miss messages now
  render in each recipient's saved locale, with Persian fallback.
- Seeded Arabic and English reminder templates in migration `k0e1f2a3b4c5`.
- Live Telegram smoke test passed for `/language en` and `/language fa`; the
  test account was restored to Persian afterward.
- Verification: unit suite `3 passed, 1 skipped`; integration-enabled suite
  `4 passed`.

## 2026-09-16 — Personal progress report

- Added `/report` with a positive summary of active/completed khatms, completed
  portions, and current-month open contributions.
- Added a reporting service with month-boundary aggregation and PostgreSQL
  integration coverage.
- Live Telegram verification passed; the real test account received its active
  khatm and completed-portion summary.
- Verification: integration-enabled suite `8 passed`.

## 2026-09-16 — Daily Digest

- Daily reminders for multiple active khatms are now combined into one message
  per user; second/final deadline reminders remain per khatm.
- Each included participation is still independently deduplicated and logged.
- Verification: digest unit coverage passed; full integration-enabled suite
  `9 passed`.

## 2026-09-16 — Daily Digest preference

- Added `/digest on|off` and persisted `daily_digest_enabled` per user.
- Disabled digest mode sends daily reminders separately while preserving all
  deadline/system notification behavior.
- Live Telegram test passed for `/digest off` and `/digest on`; the test account
  was restored to Digest enabled.
- Applied migration `n3b4c5d6e7f8`; integration-enabled suite `10 passed`.

## 2026-09-16 — Refund before first join

- Persisted the exact creation charge on each khatm.
- Added creator-only, two-step cancellation for active khatms with no members;
  the amount returns to the internal Cash Balance, never to a bank account.
- Added `KHATM_CANCEL_REFUND` audit records and PostgreSQL integration coverage.
- Verification: integration-enabled suite `10 passed`.

## 2026-09-16 — Admin user search

- Added bounded `/admin_user_search <query>` lookup by display name, phone,
  platform subject, or canonical UUID.
- Results include status, role, saved contact, and linked platform identities;
  access remains `SUPER_ADMIN`-only.
- Verification: real PostgreSQL search integration test passed.

## 2026-09-16 — Reminder Snooze

- Added per-participation snooze state and inline choices for ۳۰ دقیقه، ۱ ساعت،
  or ۳ ساعت.
- Snooze suppresses reminder-stage sends only; deadline and system notices are
  intentionally still eligible.
- Applied migration `l1f2a3b4c5d6`; full suite verification: 8 passed with
  integration enabled.

## 2026-09-16 — Automated backend test suite

- Added pytest and pytest-asyncio configuration with Windows-compatible async
  event-loop handling.
- Added unit coverage for safe message-template rendering and locale fallback.
- Added an opt-in real-PostgreSQL test covering payment ownership, exact amount
  binding, atomic single-use consumption, and replay rejection.
- Verification: default suite `2 passed, 1 skipped`; integration-enabled suite
  `3 passed`.

## 2026-09-16 — Versioned message templates

- Added the `message_templates` table with locale, version, enabled state, and
  stable message keys.
- Reminder, escalation, missed-deadline, and creator-miss messages now use
  safe `{{placeholder}}` rendering with Persian fallback defaults.
- `SUPER_ADMIN` can list templates or create a new locale/version through
  `/admin_templates` and `/admin_template_set`; changes are audited.
- Applied migration `i9d0e1f2a3b4`; admin editing and tone presets remain future
  work.

## 2026-09-16 — Gateway-neutral payment intents

- Added a `PaymentGateway` protocol and wallet intent creation/verification
  services.
- Verification binds the gateway authority to the owner and exact amount,
  checks expiry, and atomically consumes `PendingPayment` to prevent IDOR and
  replay before crediting the cash balance.
- Verified the full intent/verify/ledger path and replay rejection against the
  persistent PostgreSQL container with a fake gateway adapter.
- A real ZarinPal adapter remains pending because no merchant credential is
  configured.

## 2026-09-16 — Interactive creator resolution for missed commitments

- Added `creator_resolution` state to participations and the
  `/khatm_decision` creator-only command.
- `continue`, `open`, and `replace` are validated in the workflow service;
  replacement reuses the existing waiting-list promotion path.
- Applied migration `j0e1f2a3b4c5`; live Telegram and PostgreSQL verification
  passed for the continue path, with an audit record.

## 2026-09-16 — Open-membership contribution action

- Converted/open Quran memberships now receive a visible «ثبت مشارکت» action
  in `🕋 ختم‌های من`, so the creator's `open` resolution is usable immediately.

## 2026-09-16 — Per-user reminder timezone

- Added `/timezone <Area/City>` with IANA validation and display of the active
  timezone.
- Reminder and escalation hour checks now use each member's saved timezone,
  falling back to the application timezone for legacy/invalid data.

## 2026-09-16 — Chunked commitments and Backup Reader opt-in

- Added partial SALAWAT commitment logging with personal progress and surplus
  accounting; verified against real Postgres and live Telegram.
- Added explicit Backup Reader opt-in for committed Quran participants, with a
  toggle in «ختم‌های من» and enforcement on emergency claims.
- Applied migration `e5f6a7b8c9d0` and live-tested the opt-in toggle successfully.

## 2026-09-16 — Emergency claim expiry

- Emergency claims now reserve a Quran portion for two hours and automatically
  return expired reservations to the OPEN pool.
- Added migration `f6a7b8c9d0e1`; verified expiry and release against real PostgreSQL.

## 2026-09-16 — Per-member reminder preference

- Added `/reminder 0..23` and `/reminder off` for committed memberships.
- The reminder engine now uses each participation's preference, with the
  configured default when no preference exists; live Telegram test passed.

## 2026-09-16 — Graduated reminder escalation

- Added distinct second and final reminder stages before the daily deadline.
- Each stage has its own notification kind and daily deduplication.
- Added migration `g7b8c9d0e1f2` for the PostgreSQL enum values; real-DB
  verification passed after applying it.

## 2026-09-16 — Commitment consent gate

- Added a pledge message and explicit «تعهد را می‌پذیرم» action before committed
  deep-link joins allocate a participation or portion.
- The callback carries the invite token for reliability across transient FSM
  state; live Telegram verification passed.

## 2026-09-16 — Copy previous khatm

- Added «کپی این ختم» to creator khatm listings with a preview and explicit
  confirmation step.
- Copying creates a fresh active khatm and invitation; members, progress,
  portions, and old invitations are never copied. Quran copies use 604 pages.
- Real PostgreSQL verification passed.

## 2026-09-16 — Administrative audit trail

- Added the isolated `audit_log` module and `audit_logs` table.
- Moderation, credit grants, and khatm-request decisions now record actor,
  target, action, JSON details, and timestamp.
- Applied migration `h8c9d0e1f2a3`; real PostgreSQL persistence test passed.

## 2026-09-16 — Quran completion undo

- Added a five-minute Undo action for Quran-page completion.
- Undo restores the completed portion and releases only the untouched next
  auto-assigned portion; ownership and age are checked server-side.

## 2026-09-16 — Live four-combination Telegram sweep and admin copy fix

- Verified live creation of all four independent combinations: committed/open Quran
  and committed/open Salawat, including confirmation and invite-link output.
- Verified `🕋 ختم‌های من` lists the newly-created ACTIVE khatms.
- Fixed the empty `/admin_requests` message typo from «درخواست بازی وجود نداره.» to
  the correct «درخواستی وجود نداره.»
- A second Telegram account is still needed for real invite joining and registration.

## 2026-09-16 — Quran creation restricted to 604-page edition

- The creation wizard now shows only «مدینه (حفص) — ۶۰۴ صفحه».
- Existing khatms using older edition IDs remain readable for backwards compatibility.

## 2026-09-16 — Profile editing flow

- Added `/profile` to update name, phone, province, city, and gender after registration.
- The flow uses the same trust-based phone collection policy as first registration.

## 2026-09-16 — Partial progress for committed Salawat

- SALAWAT+COMMITMENT participants can now record progress in multiple steps.
- Personal completion and surplus are stored and reported separately.
- Added a hand-written migration for `KhatmPortion.completed_quantity`.

## 2026-09-16 — Khatm visibility: public/unlisted/private, private needs creator approval

- New `Khatm.visibility` enum (`PUBLIC`/`UNLISTED`/`PRIVATE`), asked in the creation
  wizard right before final confirmation (UNLISTED = today's behavior, default;
  PRIVATE = new). PUBLIC exists in the schema but has no discovery UI yet.
- `khatm_workflow.join_via_token` refactored: shared `_complete_join` helper now backs
  both the normal path and the new `approve_join_request` (used once a creator approves
  a PRIVATE join). Raises `JoinRequiresApprovalError` for a first-time PRIVATE join
  attempt instead of creating anything.
- New `bot/handlers/join_requests.py`: creator gets ✅/❌ buttons via
  `notify_adapter.send_with_keyboard`; approval runs the exact same join logic as a
  normal join (capacity/waiting-list/portion-assignment all identical).
- Verified against real Postgres: PRIVATE join creates no participation until approved;
  approval creates it correctly; re-joining afterward correctly raises
  `AlreadyParticipatingError`. Live button delivery not yet verified (needs two accounts).
- Hit and documented a new migration gotcha: a brand-new Postgres enum type needs an
  explicit `CREATE TYPE` before `add_column` — autogenerate's raw output doesn't include
  it. See DATABASE.md.
- See DECISIONS.md DEC-PY-0017.

## 2026-09-16 — Leaving a committed khatm now needs creator approval

- User decided (asked to choose between 3 options): a committed participant's leave
  request goes to the creator with ✅/❌ buttons instead of leaving immediately.
  Non-committed participants still leave right away.
- New `bot/notify_adapter.py::send_with_keyboard` — cross-platform notify with an inline
  keyboard, needed because the creator may be on a different platform than the requester.
- Verified against real Postgres: participation stays ACTIVE until approval actually
  happens; status/reason update correctly once it does. Button delivery not yet verified
  live (needs two real accounts).
- See DECISIONS.md DEC-PY-0016.

## 2026-09-16 — "امروز نمی‌رسم", pause/resume commitment, leave reason

- New `Khatm.allow_skip_today` (default True, no wizard question added — see DECISIONS.md),
  `Participation.paused_until`, `Participation.leave_reason` columns.
- `khatm_workflow.skip_today` / `pause_commitment` / `resume_commitment`: release the
  current portion without counting a miss; `participation.service.is_paused` gates the
  emergency-claim handler and (implicitly, since the portion is already released)
  `reminder_engine`.
- Leave flow now asks a quick-pick reason first (`leave_ask:` → `leave_reason:`) before
  actually leaving — stored for later churn analysis, never shown to the creator.
- New buttons: "⏭ امروز نمی‌رسم" (next to "✅ انجام دادم", only when
  `allow_skip_today`), "⏸ توقف موقت تعهد" / "▶️ ادامه تعهد" in "🕋 ختم‌های من".
- Also added Telegram's native "share contact" button as an alternative to typing the
  phone number during registration (user request); Bale falls back to typing only.
- Verified against real Postgres: skip-today releases without a miss, pause/resume
  toggles correctly and blocks reclaiming while paused, leave stores the reason.
- Recovered from an overnight interruption this session: the `khatmsaz-py-postgres`
  Docker container had exited (machine sleep/restart) and two backgrounded bot processes
  were orphaned — restarted both cleanly, and applied the skip/pause/leave-reason
  migration (generated in the interrupted prior turn) after fixing a missing
  `server_default` on a `NOT NULL` boolean column (would have failed against the
  non-empty `khatms` table otherwise).
- User confirmed their SMS provider: Kavenegar (کاوه‌نگار) — a legitimate, well-documented
  Iranian SMS gateway. Not yet integrated (still needs an API key + the premium/opt-in
  reminder-SMS design from DOMAIN_MODEL.md, which the user reconfirmed: SMS reminders are
  a paid add-on, not sent to everyone by default).

## 2026-09-15 — Participant registration (a real gap found on a full spec sweep)

- Found: DOMAIN_MODEL.md §1's first-join registration (name/phone/province/city/gender)
  was never actually built — the bot only ever used Telegram's own display name.
- New `bot/handlers/registration.py`: short FSM wizard triggered from `start.py`'s join
  flow the first time an unregistered user taps a join link (not at bare `/start`).
- New `bot/iran_provinces.py`: the 31 official provinces as a picklist; city is free text
  (documented scoping decision — DECISIONS.md DEC-PY-0015 — a full province→city dataset
  would be too error-prone to hand-write).
- New `settings.service` (`get_or_create`, `is_registered`, `save_profile`) — this module
  previously had only `models.py`. New `contact_phone` column on `user_settings`.
- New `identity.service.set_display_name`.
- Verified against real Postgres: registration gate correctly flips from unregistered to
  registered; display name and profile fields persist. Not yet exercised through an
  actual live Telegram join (needs a second real account).

## 2026-09-15 — Admin verified live; khatm-request queue built

- User's real Telegram chat id added to `SUPER_ADMIN_TELEGRAM_CHAT_IDS`; confirmed
  promoted to `SUPER_ADMIN` in the live database after `/start`.
- New `modules/khatm_request`: `/request_khatm` (submit), `/admin_requests` (list
  pending), `/admin_approve_request` / `/admin_reject_request` (decide + notify
  requester cross-platform). Verified against real Postgres.
- Approving a request does not auto-activate the khatm type in the wizard — see
  DECISIONS.md DEC-PY-0014 for why that needs a separate template-registry refactor.

## 2026-09-15 — Admin moderation + super-admin bootstrap

- New `identity.service` moderation functions: `warn`/`suspend`/`ban`/`reactivate`/
  `is_blocked`, plus `_bootstrap_super_admin_if_configured` (auto-promotes a configured
  `SUPER_ADMIN_TELEGRAM_CHAT_IDS` chat id to `SUPER_ADMIN` on first contact — no admin
  panel exists yet, this is how the first admin gets in at all).
- New `bot/handlers/admin.py`: `/admin_warn`, `/admin_suspend`, `/admin_ban`,
  `/admin_activate`, `/admin_grant_credit`, gated on `SUPER_ADMIN` role, targeting a user
  by platform chat id.
- New `bot/middlewares.py::ModerationMiddleware`: outer middleware blocking
  SUSPENDED/BANNED users before any handler/wizard state runs.
- Verified against real Postgres: admin bootstrap, all status transitions, and
  `is_blocked`'s WARNED-vs-BANNED distinction all correct. Not yet verified live (needs
  the user's real Telegram chat id in `.env`).
- See DECISIONS.md DEC-PY-0013.

## 2026-09-15 — Wallet + plan structure; khatm-creation charge wired (price=0 for now)

- New `wallet.service`: credit-first spending, real-cash top-up, reward-credit grant,
  refund — every mutation paired with an append-only `WalletTransaction`.
- New `plan.service`: lazy FREE default, `set_plan`.
- `khatm_workflow.create_and_launch_khatm` now charges `khatm_creation_price_toman`
  (config, defaults to 0 — no live payment gateway yet) before creating anything;
  verified zero orphan khatm rows on a failed charge, correct deduction on success.
- New `/wallet` command (balance/credit/plan) — not a Home-menu button, since top-up
  isn't live yet.
- Decided against hybrid khatms (user's call) — see DECISIONS.md DEC-PY-0011.
- See DECISIONS.md DEC-PY-0012 for the full reasoning and what's still blocked
  (real ZarinPal/Saman integration, pricing tiers, coupons, ad-credit program).

## 2026-09-15 — Capacity, waiting list, and leave/promotion

- New `Khatm.capacity` and `Participation.is_committed` columns (migration `fc2337bfe5d5`).
- Wizard now asks for capacity (limited/unlimited) when creating a QURAN_PAGE+COMMITMENT
  khatm. Joining past capacity waitlists the participant (still ACTIVE, no portion) instead
  of rejecting them.
- New `waiting_list.service` (FIFO join/promote) and `khatm_workflow.leave_khatm`
  (leaving a committed slot promotes the next waiting person, with a portion assigned and
  a cross-platform notification via `notify_adapter.get_notify_fn()`).
- New "🚪 خروج از «title»" buttons attached to the "🕋 ختم‌های من" summary message.
- Verified against real Postgres: capacity gate, waitlisting, and promotion-on-leave all
  behave correctly (scripted scenario, then deleted).
- See DECISIONS.md DEC-PY-0010 for why this is scoped to QURAN_PAGE+COMMITMENT only.

## 2026-09-15 — Emergency pool: missed portions become claimable, not stuck

- `allocation.service.release_portion` — a missed deadline now returns the portion to the
  OPEN pool (`reminder_engine` calls this instead of just notifying).
- `allocation.service.claim_next_open_portion` + `repository.try_claim_portion` — race-safe
  self-service claim via an atomic conditional UPDATE, not check-then-insert.
- New "📖 برداشتن سهم بعدی" button in "🕋 ختم‌های من" for any joined COMMITMENT+QURAN_PAGE
  khatm where the participant currently holds no portion.
- Verified against real Postgres: release → claim reclaims the same portion; a
  concurrently-joining second participant never collides with it.
- See DECISIONS.md DEC-PY-0009 for why this is a shared pool, not a dedicated
  opt-in "Backup Reader" role (that's a real, separate, still-deferred feature).

## 2026-09-15 — Reminder + deadline-miss engine (Phase 2, first slice)

- New `khatms.daily_deadline_hour` column (migration `435027907255`) — creator sets it
  during the wizard for QURAN_PAGE + COMMITMENT khatms only.
- New `modules/reminder_engine/service.py`: platform-agnostic periodic scan — morning
  reminder + same-day deadline-miss notice to the participant, informational
  miss-threshold notice to the creator. Deduplicated per day via `NotificationLog`.
- New `modules/notification/repository.py` + `service.py`: dedup-check and miss-count
  helpers backing the engine above.
- New `bot/notify_adapter.py`: the one place a scheduled job (not a live update) touches
  an aiogram `Bot` instance, keeping `reminder_engine` itself free of any bot-framework
  import.
- `bootstrap.py` now starts an `AsyncIOScheduler` job alongside bot polling
  (`REMINDER_SCAN_INTERVAL_MINUTES` in `.env`, default 30).
- Verified against real Postgres with a scripted scenario: reminder/miss dedup within a
  day, and a backdated second miss correctly triggering the creator-threshold notice.
- Explicitly not built: backup reader, emergency pool, portion reassignment, "I won't
  make it today" / "pause commitment" buttons, per-participant reminder hour — see
  DECISIONS.md DEC-PY-0008 for the honest list of what's still missing.
- Bot restarted live with the scheduler active; not yet observed firing for real (would
  need a live khatm sitting past its deadline hour during a real scan).

## 2026-09-15 — Commitment mode is now an explicit, independent creator choice

- Wizard now asks "تعهدی یا آزاد؟" before content template (was previously hard-wired per
  template as an MVP shortcut — DEC-PY-0004, superseded by DEC-PY-0007).
- New `allocation.service.assign_quantity_commitment`: fixed per-participant quantity
  commitment portions (e.g. "everyone commits to 100 salawat"), single-tap completion.
- QURAN_PAGE + OPEN combination now works (free page logging, no portion assignment,
  reuses `open_contribution`'s overflow/mazad accounting).
- All four (template × mode) combinations verified against real Postgres via a scripted
  scenario (created, then deleted — not a permanent test file).
- Bot restarted live with the new wizard; not yet manually walked through by the user in
  the real Telegram app with the new commitment-mode question.

## 2026-09-15 — Bot live-tested against real Telegram; 3 bugs found and fixed

- Set up a dedicated persistent Postgres container (`khatmsaz-py-postgres`, port 55433)
  separate from the legacy project's own `khatmsaz-postgres`; migrated it; started the
  bot with a real `@Khatm_Saz_bot` Telegram token.
- Diagnosed and fixed two Windows-only connectivity issues (DNS fake-IP requiring a local
  proxy; a Windows asyncio event-loop TLS-over-proxy hang) — new `BOT_HTTP_PROXY_URL`
  setting, `WindowsSelectorEventLoopPolicy` on Windows. See DEBUGGING.md.
- Fixed a check-then-insert race in `identity.resolve_or_provision_user` (SAVEPOINT +
  catch-and-retry).
- Fixed the identical race shape in `participation.service.join`.
- Fixed a wizard bug where pressing a menu button mid-conversation got swallowed as the
  wizard's text answer (`bot.keyboards.bail_if_menu_button`, applied to every free-text
  FSM step).
- Bot confirmed stable and polling cleanly after all four fixes; full manual user
  walkthrough in the real Telegram app is the next step (not yet done).

## 2026-09-15 — Phase 1: first real khatm end-to-end

- Built `khatm`, `participation`, `allocation`, `open_contribution`, `invitation`
  services/repositories, plus a new orchestration-only `khatm_workflow` module.
- Built the full bot conversation: creation wizard, `/start join_<token>` deep-link join,
  portion-completion and contribution-logging handlers, a shared keyboards module.
- Verified end-to-end against real (throwaway Docker) Postgres: Salawat overflow/mazad
  split, and Quran-page sequential non-overlapping personal-journey allocation across two
  simultaneous readers.
- Not yet run against real Telegram/Bale bot tokens.

## 2026-09-15 — Phase 0: project bootstrap

- Created the Python project at `C:\xampp\htdocs\Khatm`.
- Ported the full Prisma schema (23 tables, 14 modules) to SQLAlchemy 2.0
  async models, isolated one-folder-per-module.
- Wired Alembic; generated + verified (against real throwaway-Docker
  Postgres 17) the initial schema migration and a second migration adding
  6 hand-written partial unique indexes.
- Built the identity module (`resolve_or_provision_user`) and verified it
  end-to-end against real Postgres, including the platform-isolation
  property (same numeric chat id on Telegram vs Bale = two different users).
- Found + fixed a UUID type-mismatch bug in `core/ids.py` (see
  DEBUGGING.md).
- Built the aiogram bot skeleton (shared Dispatcher, Telegram + Bale client
  factories, `/start` handler, long-polling entrypoint) — import/config
  smoke-tested, not yet run against real bot tokens.
- Wrote the full `docs/ai/` memory system (this file, PROJECT_STATE,
  ARCHITECTURE, DOMAIN_MODEL, DATABASE, DECISIONS, ROADMAP, INTEGRATIONS,
  DEBUGGING, LEGACY_REFERENCE) and root `CLAUDE.md`.
- Wrote `docs/DEPLOY-GUIDE-FA.md`, a from-scratch, no-programming-background
  deployment walkthrough (not yet executed against a real VPS).
