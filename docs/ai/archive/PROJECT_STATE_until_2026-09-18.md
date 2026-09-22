# PROJECT_STATE archive — up to 2026-09-18

> Older entries moved out of `PROJECT_STATE.md` on 2026-09-20 to keep
> that file readable without burning tokens on ancient history. Nothing
> here was deleted or edited — this is a verbatim continuation. Newest
> entry in this archive is still at the top, oldest at the bottom.

## Current state — 2026-09-18 — Creator Excel export + admin-panel broadcast moderation

Two owner requests: (1) a khatm creator can now click "⬇️ دریافت اکسل کامل
اعضا" on `/creator/khatms/{id}` to download every field they're entitled to
(display name, contact phone, province, city, gender, join date, completed
portions, missed reminders, contribution/surplus) as a real `.xlsx` via the
new `/creator/khatms/{id}/export.xlsx` route (`openpyxl`, added to
requirements.txt) — same query the existing member list already used,
factored into `_load_creator_member_rows`; (2) the existing
`khatm_message`/`admin_approve_broadcast` bot-command-only moderation flow
(module `broadcast`) is now also reachable from the admin web panel at
`/broadcasts`, gated on `MODERATION_MANAGE`, with one-click approve/reject
forms (CSRF-protected, same `broadcast_service` + notify-fan-out + audit
logging as the bot path — no duplicated business logic). Nav entry added to
`base.html`. Verified: both modules import cleanly, live bot + admin web app
restarted against real Postgres with a clean log and no exceptions. Full
pytest suite not re-run (no service-layer logic changed, only new thin
routes/templates over already-tested functions).

Still open from the same owner conversation, not yet built: (a) making khatm
categories (currently hardcoded `KhatmTemplateType`) admin-panel-manageable
so new categories (e.g. لعن, named duas) can be added without a code
deploy — this is a real architecture change, scoped but not started; (b) the
"درخواستی" dua flow (user types a dua title → admin reviews → permanently
added to the dua list); (c) an "advertising system" the owner mentioned
without yet explaining — needs their explanation before scoping; (d) full
outside-in scenario testing via Telegram Web — blocked because the browser
tool has no logged-in Telegram session (needs a QR scan on the owner's
phone, which cannot be done by the AI).

## Current state — 2026-09-18 — Button-only settings menu

The owner flagged a real UX violation of the project's standing "click, don't
type" rule: the ⚙️ تنظیمات screen (`bot/handlers/report.py::settings_overview`)
told the user to type `/language fa`, `/timezone Asia/Tehran`, `/font large`,
`/reminder 9`, `/digest on`, `/sms on`, `/content translation on` — eight
preferences reachable only via typed commands. Replaced it with a new
`bot/handlers/settings_menu.py` owning a full `settings:`/`set_*:`-namespaced
inline-keyboard tree: language, font size, reciter, translation/tafsir,
reminder hour (curated common hours + off), daily digest, SMS reminders, and
timezone (curated common zones) are now each one or two taps away, calling the
exact same `settings_service`/`content_service`/`notification_service`
functions the old typed commands used — no business logic duplicated. The old
per-command handlers (`/language`, `/font`, etc.) are left in place (harmless
for power users) but are no longer the only way in. The audio on/off toggle
reuses the existing `quran_audio:` callback from `content_settings.py`
unchanged. Verified: module imports cleanly, live bot restarted against the
real `khatmsaz-py-postgres` Postgres container and confirmed clean startup
with all routers (including the new one) registered, no exceptions. Full
automated re-run of the suite was not repeated for this change (no new
service-layer code was added — only keyboards/handlers wiring against
already-tested service functions); flagged in the report below as
NOT RUN with reason.

## Current state — 2026-09-18 — Live Telegram creator-card repair

Live polling exposed Telegram's `BUTTON_DATA_INVALID` while the owner opened
My Khatms: the completion-announcement callback prefix plus a UUID exceeded
Telegram's 64-byte callback-data limit. It is now the compact `cat:<uuid>`
form, the accidentally duplicated callback handler was removed, and a
regression test enforces the byte limit for every creator-card button. The
failure was observed against the real `@Khatm_Saz_bot`, not inferred from a
mock. Full suite: **98 passed**.

## Current state — 2026-09-18 — Mobile web review for foreign verification

Support admins and Super Admins can now open `/phone-verifications` in the
mobile admin dashboard, inspect the pending user's full international number,
name, location, request purpose and Tehran-local request time, then approve or
reject with one confirmed action. The POST is CSRF-protected and reuses the
same row locks, ownership checks, permanent claim creation, audit and user
notification as the bot review path. Finance and other unrelated delegated
roles cannot view or mutate the queue. The navigation exposes the page only to
`SUPPORT_USERS`. Real PostgreSQL + ASGI rendering, permission, CSRF, mutation
and empty-state coverage pass; full suite: **98 passed**.

## Current state — 2026-09-18 — Persistent manual verification for foreign numbers

Users whose E.164 phone is outside Iran no longer enter the Kavenegar OTP
path. `/verify_phone`, first creator setup, and `/change_phone` create one
persistent admin-review request instead. Configured Telegram Super Admins
receive the full number and approve/reject buttons; Support admins can recover
the queue with `/admin_phone_requests`. Approval atomically creates the same
durable verified `PhoneClaim` used by OTP (or swaps it for a phone change),
updates the profile, preserves all account history, audits the decision, and
notifies every linked platform. Rejection changes no identity. Iranian numbers
cannot use this path, duplicate requests are deduplicated/superseded, and user
plus phone transaction locks prevent races. Migration `q7r8s9t0` is applied
to real PostgreSQL; full suite: **96 passed**. Foreign-user payment behavior is
deliberately deferred until the project owner supplies that product rule.

## Current state — 2026-09-18 — Native Telegram command menu

On every Telegram startup the bot now installs a concise default and Persian
native command menu for the main journeys: start/help, new khatm, my khatms,
report, public khatms, wallet, profile, phone verification/replacement, and
creator dashboard login. `/new_khatm` and `/my_khatms` now map to the same
button-driven handlers, so every advertised command is functional. Bale is
intentionally skipped until its command-menu API parity can be verified with a
real token; its reply keyboard remains unchanged. A menu API failure is logged
without taking polling offline. Full suite: **93 passed**.

## Current state — 2026-09-18 — Production Kavenegar SMS adapter

The vendor-neutral SMS boundary now has a concrete Kavenegar REST adapter for
creator verification, account linking and phone replacement OTPs. It sends a
form POST to the official `sms/send.json` endpoint, converts Iranian E.164 to
the provider's local receptor form, validates HTTP plus Kavenegar's embedded
status, returns the provider message id, and normalizes failures without
leaking the API key. Configuration and Persian deployment instructions now
name only the API key and approved sender—not panel login credentials. Adapter
success/rejection/misconfiguration/factory tests pass; full suite: **90
passed**. Live sending awaits the merchant's Kavenegar API key and service
sender.

## Current state — 2026-09-18 — Creator phone-verification gate

Starting a new khatm now requires the short creator profile and one verified
phone claim, as required by SPEC Q7/Q9/Q40. The main create button starts OTP
verification of the saved contact number when needed; `/verify_phone` provides
the same explicit entry point. Both ordinary creation and copy-khatm recheck
the claim immediately before mutation, so a stale/direct callback cannot
create a khatm or charge the wallet after verification disappears. Numbers
owned by another account are directed to `/link_account`; failed SMS delivery
creates no khatm and charges nothing. First verification is audited separately
as `PHONE_VERIFY` with only four phone digits. PostgreSQL tests and the full
suite pass: **86 passed**. Live verification remains blocked on an SMS
provider configuration.

## Current state — 2026-09-18 — OTP-protected phone replacement

Users can now run `/change_phone`, enter a replacement mobile number, and
confirm the six-digit OTP sent to that new number. The operation keeps the
same canonical User, platform identities, wallet, khatms, memberships and
completion history; it atomically revokes the previous verified claim,
creates the replacement claim, and synchronizes the profile contact number.
A number already verified for another account is rejected, ownership changes
for the same E.164 number are serialized with a PostgreSQL transaction lock,
and ordinary `/profile` editing cannot bypass OTP for an already verified
user. The audit trail stores the action with only the new number's last four
digits. PostgreSQL security/preservation tests and the full suite pass:
**86 passed**. Live SMS remains dependent on provider credentials.

## Current state — 2026-09-17 — Automatic positive monthly reports

The scheduler now delivers each registered user's previous calendar-month
summary on a configurable local day/hour (`MONTHLY_REPORT_DAY/HOUR`). It uses
the user's IANA timezone, catches up after downtime, and stores the processed
`YYYY-MM` period so repeated 30-minute scans cannot resend it. The report
totals completed Quran pages, Salawat (committed plus open), and khatms that
ended during the month; users with no activity are quietly marked processed
without receiving noise. Copy is positive-only in fa/ar/en and contains no
miss count or ranking. Migration `p6q7r8s9` is applied to real PostgreSQL;
timezone, aggregation, localization and idempotency coverage pass. Full suite:
**83 passed**.

## Current state — 2026-09-17 — Creator-owned mobile web dashboard

Every khatm creator can now request `/creator_web_login` and open a separate,
eight-hour scoped dashboard at `/creator`; no admin role is required. Creator
sessions use a distinct cookie and `CREATOR` purpose, and every detail route
rechecks `khatm.creator_user_id`, so guessing another khatm UUID returns 404.
The mobile view lists only owned khatms and exposes the private member report
required by the original specification: full name/phone, province/city,
gender, join time, committed/open/Backup status, completed portions, misses,
total contribution, and surplus, with name/phone/location search. New
contributions now persist counted-versus-surplus snapshots instead of trying
to reconstruct them later. Migration `o5p6q7r8` is applied to real PostgreSQL;
scoped-auth, ownership, sensitive-field rendering, filtering, progress, miss,
and surplus tests pass. Full suite: **82 passed**.

## Current state — 2026-09-17 — Creator-controlled completion announcements

Goal/date completion now records `completed_at` and queues one positive summary
for the creator and every active member across Telegram/Bale. The message shows
member count plus completed portions or contribution total, never highlights
misses, and is localized for fa/ar/en. Delivery waits five minutes so the final
Quran completion can still be undone; an undo before announcement reopens the
khatm. The creator controls this behavior with a plain `پیام پایان:
روشن/خاموش` button in each management card. An atomic claim and
`completion_announced_at` prevent duplicate sends. Migration `n4o5p6q7` is
applied to real PostgreSQL. This work also fixed an undefined callback in the
open-contribution inactive-khatm path and repaired copy-khatm propagation for
new creator settings. Full suite: **80 passed**.

## Current state — 2026-09-17 — Read-only sensitive activity timeline

The admin dashboard now exposes `/audit` as the web-only timeline required by
SPEC Q104. It shows the newest 100 append-only audit events with a plain-Persian
action label, Tehran-local timestamp, actor, target user/khatm, and structured
details. Operators can filter by the stable event code; the page intentionally
contains no edit or delete controls. Access is limited to Super Admin and the
delegated Operations role, so finance/content/support staff do not gain broad
visibility into unrelated sensitive actions. PostgreSQL + ASGI permission,
filtering, empty-state, and rendering coverage pass; full suite: **77 passed**.

## Current state — 2026-09-17 — Self-service account linking

Users who enter through a new Telegram/Bale account can now run
`/link_account`, enter the phone stored on their earlier account, and confirm
the six-digit OTP to move the current platform identity onto that existing
User. Iranian local, `98...`, and `0098...` phone forms normalize to one E.164
value. The operation records an `AccountMerge` and only merges a pristine
provisional account: if the new account already has a profile, khatms,
participations, or wallet activity, it refuses automatic merging and directs
the user to support. Production never prints the code; delivery goes through
the configured `SmsProvider`, while `DEV_OTP=1` is explicitly development
only. Same-platform account replacement is supported as required by the
original specification. PostgreSQL integration and the full suite pass:
**76 passed**. Live Bale/SMS verification still requires their credentials.

## Current state — 2026-09-17 — Public invitation landing page

Every invitation token can now render a mobile-first public preview at
`/join/{token}` before opening Telegram or Bale. It shows the khatm title,
creator display policy, niyyat, welcome message, membership mode and active
member count, and explicitly says that merely opening the page does not join.
Invalid, expired, cancelled, completed, and cancelled-khatm links fail closed.
When `PUBLIC_WEB_BASE_URL` is configured after HTTPS deployment, creation and
QR flows use this cross-platform landing URL; local development keeps direct
bot links. Real PostgreSQL + ASGI coverage and the full suite pass:
**73 passed**.

## Current state — 2026-09-17 — Delegated admin roles and least privilege

Super Admin can now assign and revoke six narrowly scoped roles: content,
finance, support, moderation, marketing, and operations. Migration `m3n4o5p6`
adds revocable, historically retained grants. Bot commands, dashboard routes,
and navigation enforce role-derived permissions; revocation invalidates an
existing delegated dashboard session on its next request. Role changes are
available without code on the new `/admins` page and through
`/admin_role_grant`, `/admin_role_revoke`, and `/admin_role_list`, with every
change written to the audit log. PostgreSQL/session/ASGI and the full suite
pass: **72 passed**.

## Current state — 2026-09-17 — Button-driven user help

`/help` now opens a plain-Persian, button-driven guide for joining, completing
Quran/quantity portions, creating and managing a khatm, wallet/payment, and
personal settings. The same guide is one tap away from Settings, and the
welcome message points first-time users to it without adding another permanent
home-menu button. The current full suite is **72 passed**.

## Current state — 2026-09-17 — Coupons and admin finance dashboard

Paid khatm creation now accepts admin-managed percentage or fixed-amount
coupons with validity windows, minimum purchase, total-use, per-user, and
maximum-discount controls. Validation and redemption are serialized on the
coupon row, and every invoice preserves gross, discount, and net snapshots.
Users enter a code only when they actually have one with `/coupon CODE`, so
the normal creation flow stays one-tap. Super Admins can manage coupons from
bot commands or the new mobile-first `/finance` dashboard, which also shows
invoice totals and recent receipts. Migration `l2m3n4o5` is applied to real
PostgreSQL; coupon, finance-page, PayPing, invoice, and full regression tests
pass; the current full suite is **72 passed**.

## Current state — 2026-09-17 — Internal financial invoices

Every verified PayPing wallet top-up now creates a permanent `TOPUP` invoice,
and every paid khatm creation creates a `KHATM_CREATION` invoice bound to the
new khatm UUID. Cancellation before the first member marks that exact invoice
`REFUNDED` and credits Cash Balance once; pre-migration khatms retain the old
compatible refund path. Users can inspect their latest receipts with
`/invoices`. Migration `k1l2m3n4` is applied to real PostgreSQL. The new
end-to-end paid-create/refund test also exposed and fixed an older repository
bug that rejected the wizard's `reminder_tone` and `content_delivery_mode`
fields. The current full suite, including the coupon and help layers, is
**72 passed**.

## Current state — 2026-09-17 — PayPing v3 wallet top-up is code-complete

The wallet now has a PayPing v3 adapter using the official `POST /v3/pay`
and `POST /v3/pay/verify` contracts, fixed one-tap amounts in `/wallet` and
`/topup`, and a public form-POST callback at
`/payments/payping/callback`. A locally generated UUID is sent as
`clientRefId`; callback status, client reference, payment code, amount, and
payment reference must all match the stored intent and the verified PSP
response before an atomic single-use claim credits Cash Balance. Replays are
idempotent and forged amounts are rejected. Panel credentials remain outside
the project. Unit tests use `httpx.MockTransport`; PostgreSQL + ASGI tests
cover successful credit, replay, and tampering. Payment-specific verification
was extended by the invoice and coupon work above; the current full suite is
**72 passed**.
Live activation still needs a dedicated PayPing API token, public DNS/TLS for
`khatmsaz.com`, and one real low-value payment test. Setup is documented in
`docs/PAYPING-SETUP-FA.md`.

## Current state — 2026-09-17 — Private-channel Quran delivery and simple audio UX

The canonical 604-page Quran registry now accepts forwarded posts from the
configured private Telegram channel. It parses Persian captions such as
`صفحه ۳`, `صفحات ۱ و ۲`, and `صوت صفحات ...`, maps shared posts to every page
they cover, forwards each physical post once, and reports exact image/audio
coverage with `/admin_quran_source_status`. Parhizgar is the default source
reciter. Quran audio is opt-in and controlled by a one-tap settings button;
the user help explains the four-step read/complete flow in plain Persian.
The extracted, versioned source map contains all **604 image pages** and **301
audio posts covering all 604 pages**; `/admin_quran_source_seed` loads it
idempotently and the local database reports 604/604 for both media kinds. The
source typo on message 492 is documented and corrected to pages 254-255.
Migration `j0k1l2m3` adds the preference. Real PostgreSQL verification passes:
**61 passed**. Live Bot API access currently returns `chat not found`, so the
bot must still be added to the private channel before live forwarding can be
verified. The admin web login page is running at
`http://192.168.0.111:8000`; production DNS/TLS for `khatmsaz.com` is pending.

PayPing panel login credentials are deliberately not stored. The dedicated
API token and a deployed HTTPS callback are still required before live
payments can be enabled.

## Current state — 2026-09-16 — Mobile-first admin web dashboard

The bot process now runs a FastAPI admin dashboard beside polling. A
`SUPER_ADMIN` obtains an opaque eight-hour login from `/admin_web_login`; the
dashboard stores it in an HttpOnly SameSite cookie, removes it from the URL,
uses per-session CSRF protection for writes, and records moderation/template
changes in the audit log. The Persian RTL mobile UI includes system metrics,
pending queues, khatm list/detail and analytics, user search/moderation, and
message-template version controls. It was browser-tested at 390×844 across
all routes with no console errors. Real PostgreSQL + ASGI and the full suite
pass: **55 passed**. Local LAN health is reachable at the configured base URL;
adding a Windows inbound firewall rule still requires an elevated shell.

## Current state — 2026-09-16 — Message-template lifecycle controls

`SUPER_ADMIN` can inspect immutable version history with
`/admin_template_history <key> [locale]` and enable/disable an exact version
with `/admin_template_toggle <key> <locale> <version> <on|off>`. Resolution
automatically falls back to the newest enabled version. The same lifecycle
controls are available in the web dashboard and every change is audited.
PostgreSQL coverage and a read-only live Telegram history check passed.

## Current state — 2026-09-16 — Tracked invitation QR

Creators can issue a fresh tracked invitation as an in-memory PNG with
`/khatm_qr <khatm_id>` or the `🔳 QR دعوت` management button. Ownership and
ACTIVE status are enforced; no temporary image is written to disk. Added
`qrcode[pil]` and PNG validation tests. Live Telegram delivered both the QR
image and deep link for the owned test khatm. Full suite: **52 passed**.

## Current state — 2026-09-16 — Creator analytics and invite funnel

Added `KhatmStats` aggregation and `/khatm_stats`, with an inline management
button. The report includes member status, commitment count, portion progress,
open-contribution total, and issued/accepted invitation conversion. Successful
invitation acceptance now records `accepted_at` and the accepting user. Real
PostgreSQL and live Telegram verification passed; full suite: **50 passed**.

## Current state — 2026-09-16 — Safe account deletion

Implemented SPEC Q39 with migration `i9j0k1l2` and `/delete_account`.
Deletion requires resolving active committed memberships and active khatms
created by the user; otherwise it safely closes open memberships, clears
personal profile fields, marks the account unusable, and preserves historical
reports/ledger. Real PostgreSQL verification passed; full suite: **49 passed**.
Live Telegram verification reached the confirmation screen and correctly
blocked the current test account because it had 3 committed memberships and 8
active created khatms; no account was deleted.

## Current state — 2026-09-16 — Live verification of open-khatm schedule

Telegram live verification passed for `/khatm_schedule`: the creator set the
owned test khatm to `daily`, received the success response, then set it back to
`off` and received the success response again. No temporary schedule remains.

## Current state — 2026-09-16 — Inactivity-safe Quran delegation

User activity is now tracked in `users.last_activity_at` (migration
`h8i9j0k1`). Before reminder scanning, a 30-day inactive member's assigned
Quran portion is returned to the pool and atomically claimed by an opted-in,
available Backup Reader when one exists. The original member remains active,
receives no miss, and both sides receive system notification when platform
identities are linked. Integration result: **48 passed**.

## Current state — 2026-09-16 — Creator member detail

Creators can inspect one active participant with
`/khatm_member <khatm_id> <participation_id>`. The detail view includes
current assignment, aggregate progress, rolling-window misses, reminder
preference, pause state, and commitment/backup flags. It verifies both
creator ownership and that the participation belongs to the requested khatm.
Integration result: **47 passed**.

## Current state — 2026-09-16 — Creator report buttons

The creator management message now exposes inline buttons for members,
needs-attention, CSV export, and copy. Each button routes through the same
creator-ownership checks as its command, so the new reports are usable without
manually copying a khatm UUID. Integration result: **47 passed**.

## Current state — 2026-09-16 — Creator CSV export

Creators can download an in-memory UTF-8 CSV report with
`/khatm_export <khatm_id>`. It includes active member display names,
commitment and backup-reader flags, per-member progress, and miss counts in
the khatm's configured rolling window. Access remains creator-scoped and no
temporary report file is persisted. Integration result: **47 passed**.

## Current state — 2026-09-16 — Creator needs-attention queue

Creators can now run `/khatm_attention <khatm_id>` to see active members with
recorded missed-deadline follow-ups inside that khatm's configured rolling
window. The report is creator-scoped and returns an explicit empty-state when
there is no actionable member. Integration result: **47 passed**.

## Current state — 2026-09-16 — Creator member progress view

Creators can inspect active members of an owned khatm with
`/khatm_members <khatm_id>`. The private summary resolves canonical display
names, commitment/backup-reader flags, and per-member quantity or positional
progress without exposing members across khatms. Telegram smoke testing also
found and fixed an HTML-parse issue in the invalid-argument response.
Integration result: **47 passed**.

## Current state — 2026-09-16 — Message-template placeholder validation

Admin-created message templates now validate placeholder syntax and reject
unknown names before storing a new immutable version. The supported reminder
placeholders are `title`, `start`, `end`, `deadline`, and `misses`; rendering
behavior remains backward-compatible for templates already in the database.
Integration result: **47 passed**.

## Current state — 2026-09-16 — Open-khatm schedules

Open khatms now support real scheduled participation prompts via
`/khatm_schedule <khatm_id> <off|daily|weekly:0,2,4|every:3|date:YYYY-MM-DD>`.
The worker evaluates the schedule in the application timezone, sends at each
member's reminder hour, and uses existing per-day notification deduplication.
Schedules are limited to open khatms and validated in the khatm service.
Migration: `g7h8i9j0k1`. Integration result: **43 passed**.

## Current state — 2026-09-16 — Moderated khatm covers

Creators can submit an image/document cover with caption
`/khatm_cover <khatm_id>`. Covers enter a pending queue; Super Admins review
them with `/admin_covers` and `/admin_review_cover <khatm_id> <approve|reject>
[note]`. Only an approved cover uploaded for the current platform is shown
before the invite preview. Migration: `f2a3b4c5d6`. Integration result:
**42 passed**.

## Current state — 2026-09-16 — Creator Snooze policy

Creators can enable or disable member reminder snooze per active commitment
khatm with `/khatm_snooze <khatm_id> <on|off>`. The setting is stored by
migration `e1f2a3b4c5`; the normal, custom-time, and emergency-claim keyboards
respect it, and stale callbacks are rejected server-side. Integration result:
**41 passed**.

## Current state — 2026-09-16 — My Khatms status buckets

The `🕋 ختم‌های من` view now separates creator-owned khatms into فعال/آینده/
تمام‌شده and labels joined khatms with the same bucket. Future and completed
khatms remain visible for context but do not receive new work-operation
keyboards. Live Telegram verification showed the new `فعال:` section and
`[فعال]` member labels.

## Current state — 2026-09-16 — Configurable miss threshold

Creator miss alerts are now configurable per khatm with
`/khatm_miss_policy <khatm_id> <count> <days>`. Defaults remain two misses in
seven days; valid ranges are 1–20 misses and 1–90 days. The reminder engine
counts only follow-up notices inside that configured window. Migration:
`d0e1f2a3b4`. Integration result: **41 passed**.
Live Telegram smoke validation of malformed policy input (`bad 0 100`) also
returned the expected invalid-ID response without changing state.

## Current state — 2026-09-16 — Custom reminder snooze

The reminder snooze menu now includes a custom end time in addition to 30
minutes, one hour, and three hours. Members enter `YYYY-MM-DD HH:MM` in the
application timezone; the value is stored timezone-aware and past values are
rejected by the notification service. Test result: **40 passed**.

## Current state — 2026-09-16 — Date-based khatm ending

Khatm now supports an optional indexed `end_at` timestamp. The creator can set
or clear it with `/khatm_end_at <khatm_id> <YYYY-MM-DD HH:MM|clear>`; input is
interpreted in the app timezone and stored timezone-aware. The reminder worker
closes due active khatms as `COMPLETED`, and repeated scans do not repeat the
transition. Migration: `c9d0e1f2a3`. Integration result: **38 passed**.

## Current state — 2026-09-16 — Custom commitment pause end

The member pause flow now supports the specified fixed durations (3/7/14
days) plus a custom Tehran-local end date via `YYYY-MM-DD HH:MM`. Custom input
is converted to UTC, rejects malformed/past values, and rechecks khatm policy
and membership before applying. PostgreSQL integration result remains **37
passed**.

## Current state — 2026-09-16 — Creator pause policy

Creators can control temporary commitment pauses per active commitment khatm
with `/khatm_pause <khatm_id> <on|off>`. The setting is persisted in the
`b8c9d0e1f2` migration; the member UI hides the pause action when disabled and
stale pause callbacks are rejected server-side. Integration result: **37
passed**.

## Current state — 2026-09-16 — OTP identity-linking boundary (superseded by the 2026-09-17 self-service flow)

The phone module now has a production-safe OTP service for cross-platform
account linking: E.164 normalization, HMAC-hashed six-digit codes, ten-minute
expiry, five-attempt limit, superseding of older challenges, one-time consume,
and a verified phone claim before attaching a Bale identity. A conflicting
platform identity is rejected rather than merged implicitly. The raw code is
returned only for the configured development OTP mode; production delivery is
through the existing `SmsProvider` boundary. PostgreSQL integration result:
**36 passed**. A live Bale token and SMS vendor credentials remain external
deployment prerequisites.

Completed/cancelled khatms are also guarded at join and contribution entry
points, so stale invite links or old inline keyboards cannot create new
participation or progress after closure.

## Current state — 2026-09-16 — Goal completion state

Goal-based completion now changes the aggregate status to `COMPLETED` instead
of only displaying a success message: open contributions close the khatm when
their target is reached, and positional Quran khatms close when all planned
portions are completed. The transition is idempotent and covered by PostgreSQL
integration tests. Full integration result: **35 passed**.

## Current state — 2026-09-16 — Scheduled khatm start

Creators can choose immediate start or a future Tehran-local start time in the
creation wizard (`YYYY-MM-DD HH:MM`). The indexed `khatms.start_at` field is
added by migration `a7b8c9d0e1f2`; invite links may be shared ahead of time,
while reminder scans and the participant Today view do not deliver scheduled
work before the start instant. Integration coverage is **34 passed** against
the persistent PostgreSQL container.

## Current state — 2026-09-16 — Reminder tones and payment safety

Pytest is now configured in `pytest.ini` with asyncio support. The default suite
passes unit tests and skips database integration tests; setting
`RUN_INTEGRATION_TESTS=1` runs database integration tests against the persistent
PostgreSQL container. The current result is 34 passed with the integration flag
and 10 passed/13 skipped without it.

The SMS boundary is now vendor-neutral through `modules/sms.provider.SmsProvider`
with a normalized result and a safe `noop` provider/factory. No external SMS is
sent until a real vendor adapter and credentials are selected. Users can opt in
or out with `/sms on|off`; enabling requires a saved contact phone. Live Telegram
verification passed for both toggles, and the test account was restored to off.

Advertising consent is now stored per khatm. An append-only reward-rate history
and `/admin_ad_rate` let Super Admins control the credit amount; an active member
earns at most one Reward Credit grant after their first completed assigned action,
or first logged open contribution, with a transaction reference preventing
retries from duplicating credit.
The live Telegram smoke test for `/admin_ad_rate` (argument validation) passed.
Active public discovery is available through `/public_khatms`; the live smoke
test correctly reported that no active public khatm currently exists.

Users can set their reading text size with `/font normal|large`; the live test
covered both values and restored the test account to `normal`.

Per-user translation and tafsir display preferences are stored independently via
`/content translation on|off` and `/content tafsir on|off`. They are advisory:
the delivery layer must show each only when the corresponding library asset
exists. Live Telegram translation toggling passed and was restored to off.

The canonical `madina-hafs` 604-page edition now has an exact-page asset registry
for `IMAGE`, `AUDIO`, and `TEXT` references. Registration rejects other editions
and pages outside 1–604; range resolution returns nothing unless every requested
page is present. Actual Quran media files have not yet been supplied; delivery
is connected and uses the library fallback until they are registered.
The assigned-portion keyboard now has a content action that sends all complete
image/audio/text assets for that exact range when references are available;
without assets it reports the library fallback. Telegram bot startup was
reverified after this integration.
Each Quran khatm now also chooses `AUTO`, `PHOTO`, or `TEXT` during the creation
wizard; the creator-only `/khatm_content_mode` command remains available for
later changes, and the live wizard reached its initial mode-selection step.
Each khatm can now choose `AUTO`, `PHOTO`, or `TEXT` delivery through the
creator-only `/khatm_content_mode <khatm_id> <auto|photo|text>` command; invalid
mode handling was verified live in Telegram.
The content module now also contains an admin-curated complete dua/ziyarat
library. Admins can upsert text with `/admin_devotional_text` and attach full
audio with `/admin_devotional_audio`; users retrieve an item with
`/devotional <slug>`. Audio references remain platform-scoped. Live Telegram
missing-slug fallback passed.
Creators can also add an optional welcome line (maximum 500 characters) during
the creation wizard; it is persisted, copied with the khatm, and shown to new
joiners with HTML escaping. The behavior is covered by a unit test.

Each khatm now stores a reminder tone selected before activation: friendly,
formal, devotional, or short. Non-default tones resolve to seeded,
locale-aware template keys while preserving the friendly fallback. The wizard
shows the selected tone in its confirmation, and copying a khatm preserves it.
The tone renderer and PostgreSQL migration are covered by the integration suite.

Creator identity display is also a per-khatm choice: full name, first name,
pseudonym, or anonymous benefactor. Pseudonyms are bounded and escaped before
being shown on the join confirmation; cloning preserves the choice.

The shallow home menu now exposes «امروز», «ختم‌های من», «گزارش من», and
«تنظیمات» alongside creation. «امروز» lists current assigned portions and
opens their existing completion/content actions; «تنظیمات» gives the user the
available command-based preferences.

The custom khatm-request moderation commands were also runtime-checked and
fixed to resolve their active platform before approval/rejection, preserving
the audit and cross-platform notification path.

Invite deep links now show an informational landing preview (title, niyyat,
creator display, current member count, and optional welcome text). Membership
and registration begin only after the user presses «شرکت در این ختم»;
canceling the preview leaves the user unjoined.

The creation wizard now exposes all three visibility modes, including public
discovery through `/public_khatms`; the previous UI exposed only unlisted and
private even though the domain and discovery service already supported public.

Creators can now control the proactive «امروز نمی‌رسم» action for committed
Quran khatms with `/khatm_skip_today <khatm_id> on|off`; ownership and khatm
type are checked in the service layer.

Creator-to-member messages now go through a moderated `khatm_broadcasts` queue:
`/khatm_message` creates a pending request, Super Admin reviews it with
`/admin_broadcasts` and approve/reject commands, and approved messages are
sent to active members on all linked platforms with an audit record.

Creators can edit only low-risk cosmetic fields after activation through
`/khatm_edit_title <khatm_id> <title>` and
`/khatm_edit_welcome <khatm_id> <text|clear>`. Ownership and ACTIVE status are
enforced; structural settings remain unchanged.
Admin media ingestion is available by sending a photo or audio/document with
caption `/admin_quran_asset IMAGE ‹page›` or
`/admin_quran_asset AUDIO ‹page› ‹reciter›`; references are stored separately
for Telegram and Bale file IDs. The live Telegram help response passed.

Per-khatm reciter whitelists and per-user favorites are now resolved by the
content service. `/reciter` lists stable reciter IDs; a favorite is used only
when allowed by the khatm, otherwise the first allowed reciter or system
fallback is selected. The live Telegram `/reciter` listing test passed. Quran
delivery is connected to the registry, pending supplied media files.

Users can now select `fa`, `ar`, or `en` with `/language`; reminder-stage and
missed-deadline messages resolve using that member's locale, with Persian
fallback. Arabic and English reminder templates were seeded by migration
`k0e1f2a3b4c5`. The rest of the bot UI is still Persian-first.
The live Telegram smoke test for `/language en` and `/language fa` passed, and
the test account was restored to Persian.
Super-admins can locate canonical users with `/admin_user_search` using a name,
phone, platform subject, or UUID; the bounded query was verified against real
PostgreSQL.
Members can snooze reminder-stage notifications for ۳۰ minutes، ۱ hour، or ۳
hours from the assigned-portion action; deadline/system notices remain active.
Migration `l1f2a3b4c5d6` is applied.
`/report` now shows a positive personal summary of active/completed khatms,
completed portions, and current-month open contributions; its aggregation was
verified against real PostgreSQL.
Live Telegram verification also passed for the real test account.
The reminder engine now combines same-hour daily reminders across a user's
active khatms into one digest while keeping staged deadline reminders separate.
The digest is per-user configurable via `/digest on|off`; turning it off sends
the daily reminders separately and does not mute deadline/system notices.
Both settings were verified live on Telegram and the test account was restored
to Digest enabled.
Paid creation amounts are now persisted on each khatm. The creator can cancel
an active, unjoined khatm through a confirmation flow; the recorded amount is
refunded to the internal cash balance and the action is audited. Migration
`m2a3b4c5d6e7` is applied.
Plan definitions now persist admin-managed fixed/usage pricing fields and JSON
feature entitlements for FREE/BASIC/PRO; Super Admins can inspect/update them
with `/admin_plans` and `/admin_plan_set`. The entitlement service exposes
feature-key checks without plan-name branching, and creation/copy flows charge
the active plan's fixed price or one-use price. Migration `o4c5d6e7f8a9` is
applied.

## Previous current state — 2026-09-16 — Chunked commitments and Backup Reader opt-in

SALAWAT commitment portions support incremental progress with surplus accounting
(`completed_quantity`), verified against real Postgres and live Telegram. Committed
Quran participants can explicitly opt in/out as Backup Readers; emergency claims
require that opt-in. Migration `e5f6a7b8c9d0` is applied and the toggle was live-tested.
Emergency claims now also carry a two-hour lock and expired reservations return
to `OPEN`; this was verified against real PostgreSQL.
Members can set their committed reminder hour with `/reminder 0..23` or disable
it with `/reminder off`; live Telegram verification passed.
Committed deep-link joins now require explicit pledge acceptance before the
participation and first portion are created; live Telegram verification passed.
Creators can now copy a previous khatm from «ختم‌های من» through a preview and
confirmation; only creation settings are copied, and new Quran copies use the
canonical 604-page edition. Real PostgreSQL verification passed.
The reminder engine now has distinct first/second/final stages, each
deduplicated independently, with the latter two scheduled relative to the
creator's deadline.
The PostgreSQL enum migration `g7b8c9d0e1f2` is applied; a real-DB test verified
that a staged reminder is sent once and deduplicated on repeat scans.
Admin moderation, credit grants, and request decisions now write append-only
audit records; migration `h8c9d0e1f2a3` is applied and JSON persistence was
verified against real PostgreSQL.
Reminder and deadline texts now resolve through the versioned,
locale-keyed `message_templates` table with safe `{{placeholder}}` rendering
and Persian defaults; the admin editor and tone presets are still pending.
The bot exposes controlled `SUPER_ADMIN` commands
`/admin_templates [locale]` and `/admin_template_set <key> <locale> <body>`;
each update is versioned and audited.
Wallet now has a gateway-neutral Payment Adapter boundary plus intent creation
and callback verification with user/amount/expiry binding and atomic
single-use consumption; ZarinPal and top-up UI remain pending until merchant
credentials are available.
The intent/verify/ledger path, including replay rejection, was verified
against the persistent PostgreSQL container using a fake gateway adapter.
Quran-page completion now exposes a five-minute Undo action with server-side
ownership and age checks; real PostgreSQL verification passed.
Repeated missed Quran commitments now include a creator decision path:
continue, convert the member to open, or replace via the existing waiting-list
flow. The command is creator-only and audited; a live `continue` decision was
verified on Telegram and PostgreSQL.
Open memberships listed in `🕋 ختم‌های من` now include their contribution
button, including memberships converted from commitment mode.
Each user can set an IANA timezone with `/timezone <Area/City>`; the reminder
engine uses that timezone for the member's reminder and escalation hour.

## Current state — 2026-09-16 — Full live Telegram creation sweep completed

### What was done
- Bot restarted cleanly with exactly one polling instance (the two Windows Python
  records are the venv launcher plus its real interpreter), and the log showed polling
  and the reminder scheduler starting without a traceback.
- Live Telegram Web walkthrough completed for all four combinations:
  تعهدی+قرآن، آزاد+قرآن، تعهدی+صلوات، آزاد+صلوات. Each reached confirmation, activation,
  and a well-formed reusable invite link. Quran flows showed edition selection; the
  committed Quran flow also showed daily deadline and capacity.
- Live `🕋 ختم‌های من` showed all four newly-created test khatms as ACTIVE alongside
  existing created/joined khatms.
- Live `/admin_requests` correctly enforced admin access; an empty queue exposed a
  Persian copy typo, now fixed from «درخواست بازی وجود نداره.» to «درخواستی وجود نداره.»
- Live `/wallet` returned the expected zero balance/free-plan view, and live
  `/request_khatm ختم آزمایشی دعای کمیل` was accepted successfully. No traceback or
  exception appeared in the bot log during the sweep.
- Per the user's explicit product instruction, new Quran creation now exposes only
  the 604-page Madina/Hafs edition; older edition records remain readable.
- Added `/profile` so registered users can update their name, phone, province, city,
  and gender, matching the original specification.
- Added partial progress for SALAWAT+COMMITMENT portions: a participant can record
  multiple amounts against one personal target; completion and surplus are reported
  separately.

### Still missing / not tested
- A second Telegram account is still required for a genuine invite-link join and the
  first-join registration flow. No join success is claimed from this one-account test.

### Next step
Use a second Telegram account to verify invite joining and first-join registration
end-to-end; no further single-account admin checks are pending.

## Current state — 2026-09-15 — Admin verified live + participant registration (a real gap found on a full spec sweep)

### What was done
- **Admin access verified live**: user's real Telegram chat id (`5490508090`) added to
  `SUPER_ADMIN_TELEGRAM_CHAT_IDS`; confirmed promoted to `SUPER_ADMIN` in the live
  database after their next `/start`.
- **Khatm-request queue built** (DECISIONS.md DEC-PY-0014): `/request_khatm`,
  `/admin_requests`, `/admin_approve_request`, `/admin_reject_request` — verified against
  real Postgres. Approving does NOT auto-activate the type in the wizard (that needs a
  template-registry refactor, a separate real gap).
- **Participant registration built** (DECISIONS.md DEC-PY-0015) — asked to sweep the
  original spec for anything missed, and found a genuine one: DOMAIN_MODEL.md §1's
  first-join registration (name/phone/province/city/gender) had never been built at all.
  Now triggered from the join flow the first time an unregistered user taps an invite
  link. Province is a picklist of the 31 official Iranian provinces; city is free text
  (documented reasoning in DEC-PY-0015 — a full province→city dataset is too
  error-prone to hand-write from memory). Verified against real Postgres.
- Bot restarted live with everything above active.

### What's still genuinely missing
- Registration not yet exercised through an actual live Telegram join (needs a second
  real account).
- No way to edit profile fields after first registration (no `/profile` command yet).
- Everything else listed in the previous entry below (custom khatm-type wizard wiring,
  message-template system, audit log, user search, real payment/SMS/content, Bale).

### Next step
Either keep sweeping the original spec for more missed items like registration, or pause
for the user to do a full live walkthrough — a very large amount has shipped since the
last live end-to-end check.

---

## Previous state — 2026-09-15 — Wallet/plan structure + admin moderation (same-day, after capacity/waiting-list/emergency-pool/reminders)

### What was done
Continuing the same session, user asked to keep going through everything buildable
without external resources (payment gateway, SMS provider, content files). Since the
reminder-engine entry below, also shipped and verified against real Postgres:

- **Emergency pool** (see DECISIONS.md DEC-PY-0009): a missed deadline releases the
  portion back to the OPEN pool; any participant can self-serve the next one via "📖
  برداشتن سهم بعدی" — race-safe atomic claim, not check-then-insert.
- **Capacity + waiting list** (DECISIONS.md DEC-PY-0010): `Khatm.capacity` +
  `Participation.is_committed`, scoped to QURAN_PAGE+COMMITMENT. Joining past capacity
  waitlists instead of rejecting; leaving a committed slot promotes the next waiting
  person with a real portion and a cross-platform notification.
- **Hybrid khatms: decided against** (DECISIONS.md DEC-PY-0011) — asked the user the
  specific blocking design conflict, answer was "we don't have hybrid khatms, drop it."
  Closed, not deferred.
- **Wallet + plan** (DECISIONS.md DEC-PY-0012): credit-first spend, top-up, reward grant,
  refund, all append-only. Khatm creation now charges `khatm_creation_price_toman` before
  creating anything (defaults to 0 — no live payment gateway to top up with yet). New
  `/wallet` command.
- **Admin moderation + bootstrap** (DECISIONS.md DEC-PY-0013): warn/suspend/ban/reactivate,
  a config-based super-admin bootstrap (no panel exists to grant the role any other way),
  `/admin_*` commands, and a `ModerationMiddleware` blocking SUSPENDED/BANNED users before
  any handler runs.
- Every one of the above verified with a scripted scenario against real Postgres, then
  the scratch script deleted. Bot restarted live with all of it active.

### What's still genuinely missing (see ROADMAP.md)
- Custom khatm-type request queue — needs a new table + refactoring the wizard's
  hardcoded template list into something admin-extensible. Real, separate piece.
- Real payment gateway, SMS provider, actual Quran/dua content, Bale token — blocked on
  resources only the user has.
- User search / admin panel UI — moderation only works by already knowing someone's
  numeric chat id.
- Admin commands not yet verified live (needs the user's real Telegram chat id in
  `SUPER_ADMIN_TELEGRAM_CHAT_IDS`).

### Next step
Get the user's real numeric Telegram chat id to finish wiring admin access, verify it
live, then either build the custom-khatm-request queue or pause for a full manual
walkthrough — a great deal has shipped since the last live check.

---

## Previous state — 2026-09-15 — Reminder + deadline-miss engine (Phase 2, first slice)

### What was done
Approved next-phase work after the commitment-mode fix (previous entry below). Built the
first working slice of the commitment engine's reminder/miss side:
- `Khatm.daily_deadline_hour` — new column, creator sets it in the wizard, only asked for
  QURAN_PAGE + COMMITMENT (a one-shot SALAWAT commitment has no daily cadence to set a
  deadline against — deliberately not asked there).
- `modules/reminder_engine/service.py` — platform-agnostic (no aiogram import) periodic
  scan over every currently-ASSIGNED positional (Quran page) portion: sends a morning
  reminder once/day, and once the khatm's deadline hour passes, a same-day "deadline
  passed, no worries, complete it whenever" notice to the participant — never framed as
  a failure, per DOMAIN_MODEL.md's "never say a khatm is broken" rule. After 2 total
  misses, the **creator** gets a plain informational notice (not an interactive
  decision — see below).
- `modules/notification/{repository,service}.py` — built for the first time (only
  `models.py` existed before): dedup-check (`already_sent_today`) and miss-counting
  (`total_miss_count`) backing the engine above, using the existing `NotificationLog`
  table.
- `bot/notify_adapter.py` — keeps `reminder_engine` free of any bot-framework import;
  it's the one place a *scheduled* job (as opposed to a live incoming update) sends a
  message through a `Bot` instance.
- `bootstrap.py` now runs an `AsyncIOScheduler` job (`REMINDER_SCAN_INTERVAL_MINUTES` in
  `.env`, default 30) alongside bot polling, in the same asyncio event loop.
- **Verified against real Postgres** with a scripted scenario (created, then deleted):
  a missed-deadline khatm correctly sends exactly one miss notice, a second scan the
  same day sends nothing more (dedup working), and backdating that log by 2 days to
  simulate a second missed day correctly triggers the creator-threshold notice with the
  right count ("2اُمین بار").
- Bot restarted live with the scheduler active and confirmed starting cleanly
  (`apscheduler.scheduler: Scheduler started` in the log) — **not yet observed actually
  firing against a real, currently-overdue khatm in production**; that only happens
  once a real committed Quran khatm exists past its deadline hour during a scan.

### Honest gaps (real, not oversights — see DECISIONS.md DEC-PY-0008)
- No backup reader, no emergency pool, no portion reassignment — a missed portion just
  sits `ASSIGNED` to the original participant forever; they keep getting reminded.
- Creator's miss-threshold notice is read-only information, not an interactive
  "keep / convert to open / replace" decision.
- No per-participant reminder hour (schema field exists, nothing uses it yet) — every
  participant gets the same fixed morning hour.
- No "I won't make it today" / "pause my commitment" buttons yet (nothing for them to
  hand a released portion to without the backup/emergency mechanism above).
- SALAWAT + COMMITMENT khatms get NO reminder/miss tracking at all in this slice — only
  QURAN_PAGE + COMMITMENT does, since only that combination has a daily-cadence deadline
  concept right now.

### Next step
Either (a) build the backup-reader/emergency-pool data model + reassignment logic to
close the biggest remaining gap above, or (b) pause the engine work and let the user
manually test everything built so far in the real Telegram app first — recommend (b)
given how much has shipped without a live end-to-end check since the commitment-mode
change.

---

## Previous state — 2026-09-15 — Commitment mode made explicit (all 4 combinations working)

### What was done
Right after the first live Telegram test (previous entry below), the user flagged that
commitment-mode (تعهدی/آزاد) must be its own explicit question, asked *before* content
type, independently — matching the legacy project and DOMAIN_MODEL.md §2. This had been
temporarily hard-wired per template (DEC-PY-0004, an explicitly-flagged MVP shortcut) to
get one path working end-to-end first. Fixed the same day:
- Wizard restructured: **تعهدی/آزاد → قرآن/صلوات → عنوان → نیت → (config specific to the
  combination) → تایید**. See `bot/handlers/create_khatm.py`.
- New engine piece: `allocation.service.assign_quantity_commitment` — fixed
  per-participant quantity commitment (e.g. every SALAWAT+COMMITMENT participant gets
  their own 100-salawat portion the moment they join). This was a real, documented gap
  (ROADMAP.md previously listed "QUANTITY commitment portions... still pending") — now
  closed for both one-tap completion and chunked progress logging.
- QURAN_PAGE + OPEN now works too (previously only QURAN_PAGE + COMMITMENT existed): free
  page logging against the edition's total page count, reusing the exact same
  `open_contribution` overflow/mazad logic already built for Salawat.
- All four `(template_type, khatm_type)` combinations verified against real Postgres with
  a scripted scenario (two participants each getting independent quantity commitments;
  completing one doesn't touch the other; OPEN Quran logging with correct target).
- Bot restarted live with the new wizard (`@Khatm_Saz_bot`, same persistent DB). Full
  decision record: DECISIONS.md DEC-PY-0007 (supersedes DEC-PY-0004).

### Remaining from this change
- User has now manually exercised the live commitment flow, including the new
  "➕ ثبت بخشی از تعهد" action. A 300-entry submission against a 100-target
  test commitment correctly recorded 100 as personal progress and 200 as surplus.
- Hybrid khatms (mixing committed and open participants in the *same* khatm) are still
  unbuilt — that's a bigger, separate feature (Phase 4), not just "ask the question
  earlier," and deliberately not attempted in this pass.

### Next step
User re-tests in real Telegram: `/start` → "➕ ساخت ختم جدید" → should now ask تعهدی/آزاد
first → try all four combinations (تعهدی+قرآن، تعهدی+صلوات، آزاد+قرآن، آزاد+صلوات) at
least once each and report anything that looks wrong.

---

## Previous state — 2026-09-15 — Bot verified LIVE against real Telegram (@Khatm_Saz_bot)

### What was done
- **The bot is running for real**, right now, on the user's Windows laptop, polling with a
  real `TELEGRAM_BOT_TOKEN` (`@Khatm_Saz_bot`), against a dedicated persistent Postgres
  container (`khatmsaz-py-postgres`, port 55433, Docker volume `khatmsaz-py-pgdata` — kept
  running between sessions, NOT the throwaway kind used for schema verification). This is
  the first time any part of this project ran against real Telegram infrastructure.
- **Three real bugs found and fixed by watching live traffic** (not caught by the earlier
  scripted DB scenario, because that script never had concurrent/duplicate requests):
  1. **Windows can't reach Telegram** — two stacked causes: (a) this laptop's network
     resolves `api.telegram.org` to a DNS "fake IP" that only a local VPN/proxy client can
     route (Telegram is blocked without one), and `aiohttp` doesn't auto-use the Windows
     system proxy the way `curl` does; (b) even once proxied, Windows' default
     `ProactorEventLoop` hangs doing TLS over an HTTP CONNECT tunnel (a known asyncio bug).
     Fixed with a new `BOT_HTTP_PROXY_URL` setting (empty on a real server) plus
     `WindowsSelectorEventLoopPolicy` on Windows only. Full story: DEBUGGING.md.
  2. **Identity race condition**: `resolve_or_provision_user` did check-then-insert with no
     locking; Telegram delivering several queued `/start` presses at once made two
     coroutines both try to create the same (platform, subject) user, and the loser
     crashed instead of just returning the winner. Fixed with a SAVEPOINT + catch-and-
     retry pattern in `identity/repository.py` + `identity/service.py`.
  3. **Same race in `participation.service.join`**: identical shape, identical fix,
     found immediately after fixing #2 because a queued `/start join_<token>` hit the same
     class of bug in a different table (`uq_participation_active_khatm_user`).
  4. **Menu button swallowed by wizard**: pressing "🕋 ختم‌های من" while the creation
     wizard was mid-flow (waiting for a title) got treated as the title text instead of
     navigating — a real khatm got created titled literally `🕋 ختم‌های من`. Fixed with a
     new `bot.keyboards.bail_if_menu_button()` guard, now called first in every free-text
     wizard step (`create_khatm.py`'s title/niyyat/target entry, `portions.py`'s
     contribution-amount entry).
- **Also found**: two full bot processes were accidentally running at once at one point
  (a stale process from an earlier crashed attempt didn't fully exit), which is *why* the
  identity/participation races triggered so easily — see DEBUGGING.md "Two bot processes
  end up polling the same token at once" for how to detect this.
- **DEC-PY-0006 not yet written up as a decision** — the proxy/event-loop fix is
  documented as a DEBUGGING.md entry, not a DECISIONS.md entry, since it's a Windows-dev-
  environment workaround, not a product/architecture decision.

### Commands known to work (this session, live)
```bash
# Dedicated persistent Postgres for the bot (separate from the legacy project's own
# khatmsaz-postgres container, which has no host port published):
docker run -d --name khatmsaz-py-postgres -e POSTGRES_USER=khatmsaz \
  -e POSTGRES_PASSWORD=khatmsaz_local_dev -e POSTGRES_DB=khatmsaz \
  -p 55433:5432 -v khatmsaz-py-pgdata:/var/lib/postgresql/data postgres:17-alpine

PYTHONPATH=src ./.venv/Scripts/python.exe -m alembic upgrade head
PYTHONPATH=src ./.venv/Scripts/python.exe -m khatmsaz.bootstrap
```
`.env` on this laptop has `DATABASE_URL` pointed at `localhost:55433`, a real
`TELEGRAM_BOT_TOKEN`/`TELEGRAM_BOT_USERNAME`, and `BOT_HTTP_PROXY_URL=http://127.0.0.1:12334`
(this laptop's local VPN client's proxy port at the time — may change if that app is
restarted on a different port; see DEBUGGING.md).

### Remaining / deferred
- User has not yet manually walked through the full flow in the Telegram app themselves
  (create a khatm, join from a second account, log a contribution, complete a Quran
  portion) — the bot is up and confirmed not crashing, but a full manual walkthrough by
  the user is the immediate next step.
- Bale still untested against a real token (no `BALE_BOT_TOKEN` provided yet).
- Same "everything else" list as the previous Phase 1 entry below: commitment engine
  proper, waiting list, hybrid khatms, wallet/payments, SMS, admin, content library,
  Arabic/English, and no pytest suite yet.

### Next step
User manually tests in the real Telegram app: `/start`, create a Salawat khatm, create a
Quran-page khatm, share an invite link with a second Telegram account, join, log a
contribution, complete a portion, check "🕋 ختم‌های من". Report anything that looks wrong —
given how many real bugs surfaced in the first few minutes of live traffic, more are
likely waiting in flows not yet exercised (e.g. edition-selection callback, cancel button,
double-tapping "✅ انجام دادم").

---

## Previous state — 2026-09-15 — Phase 1: First real khatm end-to-end (SALAWAT + QURAN_PAGE)

### What was done
- **Full khatm creation → join → complete flow built and verified against real Postgres**
  (throwaway Docker container, migrated, exercised with a scripted scenario, then torn
  down — not just import-checked).
- **New modules with real logic** (all follow the `models.py`/`repository.py`/`service.py`
  isolation pattern — see ARCHITECTURE.md):
  - `khatm`: create draft, activate, list-by-creator. MVP simplification: template type
    hard-wires khatm_type for now (`QURAN_PAGE → COMMITMENT`, `SALAWAT → OPEN`) — see
    DECISIONS.md DEC-PY-0004. The full hybrid/creator-chooses model from DOMAIN_MODEL.md
    is real scope, deferred.
  - `participation`: join/leave, idempotency guard (`AlreadyParticipatingError`) backed by
    the DB partial unique index.
  - `allocation`: POSITIONAL plan generation (Quran pages → fixed-size portions),
    sequential **personal-journey** assignment — verified with two simultaneous readers
    that their portions never overlap (`uq_portion_positional_plan_unit_start` holds), and
    that completing a portion correctly advances *that* reader to the *next* open one, not
    colliding with the other reader's in-flight portion.
  - `open_contribution`: free-form quantity logging for OPEN khatms (Salawat), with the
    "mazad" overflow split (DOMAIN_MODEL.md §2/§3) — verified: logging past the remaining
    target correctly splits into counted-vs-surplus and never rejects the log.
  - `invitation`: opaque token issue/resolve (SHA-256 hashed, ~no practical expiry,
    reusable multi-join link — not single-use).
  - `khatm_workflow` (new, no DB table): the one module allowed to call multiple other
    modules' `service.py` in sequence — `create_and_launch_khatm()` and `join_via_token()`
    orchestrate khatm + allocation + invitation + participation so bot handlers stay
    one-call-per-handler.
- **Full bot conversation built** (aiogram FSM, `MemoryStorage` — process-local, lost on
  restart; Redis-backed storage is a later ROADMAP item once that limitation matters):
  - `bot/handlers/create_khatm.py` — creation wizard: template → title → niyyat (optional,
    skippable) → target (Salawat) or edition (Quran) → confirmation → creates, activates,
    and returns an invite link/command.
  - `bot/handlers/start.py` — extended to handle `/start join_<token>` deep links (join
    flow with friendly errors for not-found/expired/already-joined) in addition to plain
    `/start`.
  - `bot/handlers/portions.py` — "✅ انجام دادم" (Quran) and "➕ ثبت مشارکت" (Salawat)
    inline-button flows.
  - `bot/handlers/my_khatms.py` — lists created + joined khatms with live progress.
  - `bot/keyboards.py` — every keyboard in one place (Home menu stays intentionally
    shallow, per DOMAIN_MODEL.md §4); `safe_clear_inline_keyboard`/`safe_answer_callback`
    helpers swallow the harmless "message not modified"/double-tap edge cases.
- **All four routers wired into `bootstrap.py`**, `Dispatcher(storage=MemoryStorage())`.
- **Verified test scenario** (script run against real Postgres, then deleted — not a
  permanent file; pytest suite is still a ROADMAP item):
  1. Create SALAWAT khatm (target 1000) → join → log 700 (exact) → log 500 more (only 300
     remaining) → correctly counted=300/surplus=200/total=1200.
  2. Create QURAN_PAGE khatm (iran-pocket edition, 286 pages, default 2 pages/portion → 143
     portions) → two different readers join → each gets non-overlapping first portions
     (1–2 and 3–4) → reader 1 completes 1–2 → auto-advances to 5–6 (not 3–4, which reader 2
     already holds) → progress correctly shows 1/143.
- **Bot still not run against real Telegram/Bale tokens** — only imports + full DB-backed
  business logic verified. Next real step for the user: get bot tokens, fill `.env`, run
  `python -m khatmsaz.bootstrap` and test `/start` for real (see README.md quick-start).

### Commands known to work
```bash
PYTHONPATH=src ./.venv/Scripts/python.exe -m alembic upgrade head
PYTHONPATH=src ./.venv/Scripts/python.exe -m khatmsaz.bootstrap   # once tokens are set in .env
```

### Remaining / deferred
- Commitment engine proper: consent text, per-participant reminder time, deadline,
  miss-escalation, backup reader, emergency pool, "I won't make it today", pause — all of
  DOMAIN_MODEL.md §3 beyond the bare join+assign+complete built this phase.
- Waiting list, hybrid khatms (creator offers both commitment and open in one khatm).
- Bale tested only via import/config smoke test, never against a real Bale token yet.
- Wallet/payments, SMS, admin, content library (reciters/translation/tafsir), Arabic/
  English — all untouched, per ROADMAP.md's later phases.
- No pytest suite yet — verification so far is scripted scenarios run by hand against a
  throwaway DB, not an automated, repeatable test suite.

### Next step
Get real `TELEGRAM_BOT_TOKEN` (and `BALE_BOT_TOKEN` if available) into `.env`, run the bot
locally, and manually walk through: create a Salawat khatm → join from a second Telegram
account → log a contribution → create a Quran-page khatm → join → complete a portion. Once
that's confirmed working with real Telegram, decide whether to harden Phase 1 with pytest
or move straight into Phase 2 (commitment engine).

---

## Previous state — 2026-09-15 — Phase 0: Project bootstrap (DB schema + identity + /start)

### What was done
- **New Python project created** at `C:\xampp\htdocs\Khatm` (this repo), replacing the
  earlier plan to keep building the TypeScript project at
  `\\wsl.localhost\Ubuntu-24.04\home\elyas\KhatmSaz`. That project is NOT deleted — it
  stays as the domain-logic reference (see `LEGACY_REFERENCE.md`). Decision: DEC-PY-0000.
- **Stack chosen**: Python 3.13, aiogram 3 (one shared Dispatcher/handler set for both
  Telegram and Bale — Bale's Bot API is Telegram-compatible, just a different base URL),
  SQLAlchemy 2.0 async + asyncpg, Alembic, PostgreSQL, Redis (not wired yet). **Long
  polling, not webhooks** — DEC-PY-0001 (see DECISIONS.md for why).
- **Project skeleton**: `src/khatmsaz/` with `core/` (db session, id generation, model
  registry) and `modules/<name>/` — one isolated folder per domain concept, each with its
  own `models.py` (and `repository.py`/`service.py` where logic already exists). See
  ARCHITECTURE.md for the full module list.
- **Full database schema ported** from the original Prisma schema to SQLAlchemy models —
  23 tables across 14 modules (identity, phone, khatm, participation, allocation,
  invitation, waiting_list, wallet, notification, settings, session, authorization,
  account_merge, plan, open_contribution). Field names, types, and relationships mirror
  the original 1:1 (see DATABASE.md for the table-by-table mapping).
- **Alembic wired and verified against a real (throwaway Docker) PostgreSQL 17**:
  - `migrations/versions/585f0d556cb8_initial_schema.py` — autogenerated from the models,
    applied successfully (`alembic upgrade head`).
  - `migrations/versions/3b206b888ca5_partial_unique_indexes.py` — the 6 hand-written
    partial unique indexes SQLAlchemy can't express declaratively (one ACTIVE
    participation per khatm+user, one ACTIVE capability grant per user+type, no
    overlapping positional portions per plan, and the three phone-claim invariants).
    Upgrade/downgrade roundtrip verified.
- **Identity module fully working**: `resolve_or_provision_user()` — given a
  (platform, chat_id), finds the existing User or creates one + a PlatformIdentity row.
  Verified end-to-end against real Postgres: same chat → same user id (idempotent);
  same numeric chat id on a *different* platform → a *different* user (platforms don't
  collide). This is the exact identity model the original project used (DEC-0032).
- **Bug found and fixed during verification**: `core/ids.py` originally returned `str`
  from `new_id()` for columns typed `Mapped[uuid.UUID]`. A freshly-inserted row's `.id`
  was therefore a `str`, while the same row re-fetched from the DB came back as a
  `uuid.UUID` — they printed identically but `==` was `False`. Fixed by having
  `new_id()` return `uuid.UUID` directly. Caught by an ad-hoc equality check while
  smoke-testing identity provisioning — **this class of bug (id type mismatch) is worth
  re-checking whenever a new module's repository is first written.**
- **Bot skeleton working**: `src/khatmsaz/bootstrap.py` starts both bots (whichever
  tokens are configured in `.env`) on long polling, sharing one `Dispatcher` and one
  `/start` handler (`bot/handlers/start.py`) that provisions the user and sends a
  Persian welcome message. Not yet run against real Telegram/Bale tokens — imports and
  config loading verified only.
- **Dependencies installed and verified** in a local `.venv` (`requirements.txt`):
  aiogram, SQLAlchemy, asyncpg, alembic, pydantic-settings, redis, APScheduler.

### Commands known to work
```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
# with DATABASE_URL pointed at a real Postgres:
PYTHONPATH=src ./.venv/Scripts/python.exe -m alembic upgrade head
PYTHONPATH=src ./.venv/Scripts/python.exe -m khatmsaz.bootstrap   # once tokens are set
```

### Remaining / deferred (see ROADMAP.md for the full phased plan)
- Khatm creation wizard (bot conversation flow) — live and supports all four MVP combinations.
- Allocation engine (plan generation, page/quantity portions) — service live; emergency claim lock/expiry is live.
- Waiting list + Backup Reader opt-in — live for the scoped Quran commitment flow; full replacement policy remains.
- Wallet + ZarinPal payment flow — models exist, no service yet.
- Notification/reminder scheduler (APScheduler + Redis) — not started.
- Phone OTP auth and `/link_account` are implemented; a real SMS provider and
  live Bale credentials are still deployment prerequisites.
- Admin capabilities (ban/warn, moderation) — models exist, no service yet.
- No automated test suite yet (pytest not set up).
- Not deployed anywhere yet. `docs/DEPLOY-GUIDE-FA.md` written for when it's ready but
  not yet executed on the real VPS.

### Next step
Phase 1: khatm creation wizard for the two simplest templates (SALAWAT quantity-based,
QURAN_PAGE positional-based) end-to-end through the bot, COMMITMENT type only, single
platform (Telegram) first — see ROADMAP.md.
