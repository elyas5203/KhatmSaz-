# DECISIONS archive — DEC-PY-0064 and earlier

> Older decisions moved out of `DECISIONS.md` on 2026-09-20 to keep
> that file readable. Nothing was deleted or edited — verbatim
> continuation. Append-only rule still applies: never edit these.

### DEC-PY-0064 — Creator web sessions are purpose-scoped and ownership-checked
**Date:** 2026-09-17
**Decision:** Issue a separate `CREATOR` session from
`/creator_web_login`, store it in its own path-scoped HttpOnly cookie, and
never infer admin permission from it. Every creator detail route must match
the requested khatm's `creator_user_id` to the authenticated User. Show the
full member data explicitly requested by the owner only inside this private
web surface. Persist counted and surplus amounts on every new open
contribution so per-member reports remain historically accurate.
**Why:** The original specification intentionally keeps granular personal
data out of the bot but requires paying creators to see it. A separate session
purpose and ownership check prevent both privilege confusion with the admin
dashboard and horizontal access to another creator's audience.

### DEC-PY-0063 — Completion announcements wait through the final Undo window
**Date:** 2026-09-17
**Decision:** Record `completed_at` when a khatm reaches its goal/date, but do
not broadcast immediately. Wait five minutes, atomically claim the still
completed and creator-enabled announcement, then send one positive localized
summary to the creator and active members on every linked platform. A final
Quran completion retains Undo; using it before the claim reopens the khatm.
Store `completion_announced_at` so scheduler retries cannot duplicate a sent
summary. The management card provides a plain on/off creator choice.
**Why:** SPEC Q87-88 guarantees a five-minute Undo and Q95-96 asks for an
automatic completion message controlled by the creator. Broadcasting at the
final tap would tell everyone a khatm ended even when that tap was immediately
reversed. The grace period preserves both requirements while keeping the bot
interaction one-tap and positive.

### DEC-PY-0062 — Sensitive audit events are web-only and operations-scoped
**Date:** 2026-09-17
**Decision:** Render the append-only `audit_logs` stream at `/audit` with no
mutation or deletion endpoint. Show actor, target, Tehran-local time,
structured details, and a stable machine event code beside its Persian label.
Grant visibility only to Super Admin and the delegated Operations role; other
delegated roles retain access only to their own working areas.
**Why:** The original specification requires sensitive activity timelines in
the Web App and explicitly keeps the bot simple. A read-only operations scope
preserves accountability without leaking unrelated financial, moderation, or
role-management history to every staff member.

### DEC-PY-0061 — Self-service linking only absorbs pristine provisional accounts
**Date:** 2026-09-17
**Decision:** `/link_account` may reassign the current Telegram or Bale
identity to the unique existing User found by a verified phone claim after a
valid one-time OTP. It may do so only when the newly provisioned source User
has no saved profile, created khatm, participation, or wallet activity. Record
the operation in `AccountMerge`, mark the source `MERGED`, and require support
review for any non-pristine source. Permit another identity from the same
platform because the original requirements explicitly include replacing a
Telegram/Bale account, not only crossing between platforms. In production the
OTP is sent only through `SmsProvider`; showing the code is restricted to
`DEV_OTP`.
**Why:** Moving one empty identity is deterministic, but silently combining
two used accounts could duplicate balances, lose ownership, or corrupt active
commitments. This boundary gives ordinary users the simple recovery flow they
asked for while keeping ambiguous financial and participation merges under
human control.

### DEC-PY-0060 — Public invite pages preview first and join only inside a bot
**Date:** 2026-09-17
**Decision:** Resolve the existing hashed invitation token at
`/join/{token}` and show a read-only, no-index preview. Continue into Telegram
or Bale with the same payload; do not create a participation from the web
request. Only emit this public URL in bot messages/QR codes when the explicitly
configured `PUBLIC_WEB_BASE_URL` is available over production HTTPS.
**Why:** The original requirements call for an external introduction page and
three entry paths, but registration, consent, private approval, and platform
identity already have one authoritative implementation inside the bots. A
preview-only landing page provides a clear, cross-platform UX without creating
a second unauthenticated joining path or changing the meaning of opening a
link.

### DEC-PY-0059 — Delegated administrators use revocable role grants
**Date:** 2026-09-17
**Decision:** Keep the bootstrapped `SUPER_ADMIN` as the root authority, but
store every delegated admin assignment in `admin_role_grants`. Derive concrete
permissions from six named roles and enforce the same policy in bot handlers,
web sessions, routes, and navigation. Never copy Super Admin onto ordinary
staff accounts. Revoke a grant in place so its history remains inspectable;
existing sessions are re-authorized on every request and therefore stop
working outside the user's remaining roles immediately.
**Why:** The original specification requires separate content, finance,
support, moderation, and marketing responsibilities with per-person access.
A shared least-privilege policy prevents bot and dashboard behavior from
drifting while preserving a simple no-code UI for the project owner.

### DEC-PY-0058 — Coupon entry stays optional and redemption is invoice-bound
**Date:** 2026-09-17
**Decision:** Do not add a mandatory coupon question to the khatm wizard.
During a paid confirmation, a user who has a code may send `/coupon CODE` and
receive the exact gross/discount/net quote. Revalidate and redeem under a row
lock in the same transaction that charges the wallet and creates the invoice;
store the coupon redemption against that invoice. If the code becomes invalid
before confirmation, remove it and keep the user on the same confirmation
screen at full price.
**Why:** Most users do not have a coupon, so an extra required question would
make the primary flow harder. Transactional revalidation prevents overselling
limited coupons, while invoice-bound immutable snapshots make support and
refund accounting unambiguous.

### DEC-PY-0057 — Implemented purchases always write an internal invoice
**Date:** 2026-09-17
**Decision:** Store an immutable gross/discount/net amount snapshot for every
implemented purchase category (`TOPUP`, `KHATM_CREATION`, future generic
`PURCHASE`). Bind a paid khatm invoice to its khatm UUID. A permitted
pre-first-member cancellation changes that exact invoice from `PAID` to
`REFUNDED` and records the internal-wallet refund; it does not erase or rewrite
the invoice. Keep a compatibility fallback only for khatms created before the
invoice migration.
**Why:** The original specification requires an internal invoice from day one
and an auditable wallet-only refund. Keeping the receipt lifecycle next to the
wallet ledger makes both requirements transactional and prevents a separate,
mutable receipt system from drifting away from actual balance movements.

### DEC-PY-0056 — PayPing v3 is the first live PSP adapter
**Date:** 2026-09-17
**Decision:** Keep the gateway-neutral wallet boundary, but implement PayPing
v3 as the first concrete adapter because the project owner supplied a PayPing
merchant account. Use a locally generated pending-payment UUID as
`clientRefId`, accept only PayPing's documented form POST, compare callback
status/client reference/payment code/amount against the stored intent, then
call `/v3/pay/verify` and compare the verified amount, payment code,
`clientRefId`, and payment reference before atomically crediting Cash Balance.
Never treat the browser redirect alone as payment success, and never store
panel login credentials in application configuration.
**Consequence:** `/wallet` and `/topup` can expose simple fixed amounts once
`PAYPING_API_TOKEN` and a public HTTPS callback are configured. Creation stays
free until one real low-value top-up passes end to end; the old ZarinPal
placeholder remains inert and can later be another adapter rather than a
rewrite.

### DEC-PY-0055 — Post-activation edits stay cosmetic
**Date:** 2026-09-16
**Decision:** Allow only the creator of an ACTIVE khatm to change its title or
welcome text through validated commands; support explicit `clear` for the
welcome text. Do not expose target, commitment, allocation, capacity, or other
structural mutations after activation.
**Why:** The specification locks structural settings once members can depend
on them, while title and welcome copy are low-risk presentation fields.

### DEC-PY-0047 — Reminder tone is a per-khatm pre-activation choice
**Date:** 2026-09-16
**Decision:** Store one of `FRIENDLY`, `FORMAL`, `DEVOTIONAL`, or `SHORT` on
each khatm. Ask for it before activation, resolve non-default reminder and
miss messages through locale-aware tone keys, and fall back to the friendly
template when a localized tone version is unavailable. Preserve the setting
when copying a khatm.
**Why:** Reminder style belongs to the khatm's communication contract rather
than to an individual recipient; bounded presets keep messages consistent,
reviewable, and safe while retaining the existing template fallback behavior.

### DEC-PY-0048 — Creator identity display is per-khatm and bounded
**Date:** 2026-09-16
**Decision:** Let the creator choose `FULL_NAME`, `FIRST_NAME`, `PSEUDONYM`,
or `ANONYMOUS` for each khatm. Store a pseudonym only for the pseudonym mode,
limit it to 64 characters, escape it at delivery, and preserve the setting
when cloning.
**Why:** The original specification makes creator visibility a per-khatm
choice; bounding and escaping the optional pseudonym keeps the simple bot flow
safe without changing the canonical user identity.

### DEC-PY-0049 — Home navigation stays shallow and action-oriented
**Date:** 2026-09-16
**Decision:** Keep the reply keyboard limited to Today, My Khatms, Personal
Report, Settings, and Create Khatm. Today is a read-only overview that links
back to the existing portion action keyboards; Settings documents the command
surfaces instead of adding a deep nested menu.
**Why:** The specification explicitly keeps the bot home simple while making
the four primary participant surfaces directly reachable.

### DEC-PY-0050 — Request moderation resolves the invoking platform
**Date:** 2026-09-16
**Decision:** Admin approval/rejection of a custom khatm request must derive
the platform from the invoking bot instance before loading the admin identity;
the same resolved platform is used for authorization and audit context.
**Why:** Telegram and Bale share request data but have distinct platform
identities. A command handler must never rely on an undefined or guessed
platform when performing a privileged state transition.

### DEC-PY-0051 — Invite opening is separate from joining
**Date:** 2026-09-16
**Decision:** Resolve an invite token and show a sanitized preview first. Only
the explicit preview callback may enter registration, commitment consent, or
the join operation; opening a deep link alone never creates membership.
**Why:** The specification requires a landing view across entry points and
prevents accidental registration/participation from a link preview.

### DEC-PY-0052 — All visibility modes are creator-selectable
**Date:** 2026-09-16
**Decision:** The creation wizard offers `PUBLIC`, `UNLISTED`, and `PRIVATE`
with explicit labels. Public khatms are discoverable through the existing
bounded `/public_khatms` list; unlisted and private retain their link and
approval semantics.
**Why:** The domain already models all three modes and the specification
requires creator choice per khatm; hiding public mode made the discovery path
unreachable from normal creation.

### DEC-PY-0053 — Skip-today is a creator-controlled Quran commitment option
**Date:** 2026-09-16
**Decision:** Keep `allow_skip_today` scoped to committed Quran khatms and let
only the owner change it through `/khatm_skip_today <id> on|off`. The portion
release remains proactive and miss-free when enabled.
**Why:** The specification makes this action optional per khatm; a server-side
ownership/type check prevents an unrelated user from changing commitment
behavior.

### DEC-PY-0054 — Creator messages require moderation before delivery
**Date:** 2026-09-16
**Decision:** Store creator-to-member messages as pending `KhatmBroadcast`
records. Only a Super Admin may approve or reject them; approval sends the
message once to each active member's linked platform identities and records an
audit event. A message is never sent at creator submission time.
**Why:** The original specification explicitly requires admin approval before
customer messages reach members, preventing unreviewed broadcasts while
retaining cross-platform delivery.

### DEC-PY-0040 — Quran assets are canonical-page and contiguous-range gated
**Date:** 2026-09-16
**Decision:** Store addressable `IMAGE`, `AUDIO`, and `TEXT` references only for
the canonical 604-page `madina-hafs` edition. A requested range is deliverable
only when every page in that range exists; audio is additionally keyed by a
known reciter ID.
**Why:** SPEC requires one fixed Quran edition and exact participant page
delivery; a fail-closed registry prevents mixed editions and partial media.

### DEC-PY-0041 — Assigned content delivery is asset-first and fail-closed
**Date:** 2026-09-16
**Decision:** The bot exposes a content action on an assigned Quran portion and
sends only complete exact-range assets; when none are registered it explains
the missing library content instead of sending placeholders or partial pages.
**Why:** SPEC Q107 and Q119–122 require the user's exact pages and support
Telegram media, while the project does not yet ship the real Quran asset files.

### DEC-PY-0042 — Content format is a per-khatm creator choice
**Date:** 2026-09-16
**Decision:** Store the creator's preferred `AUTO`, `PHOTO`, or `TEXT` delivery
mode on each khatm. Audio remains available independently when its exact asset
exists, and missing content still falls back safely.
**Why:** DOMAIN_MODEL §5 makes format choice a per-khatm setting while keeping
the bot's default behavior simple and preserving exact-range delivery.

### DEC-PY-0044 — Media file references are platform-scoped
**Date:** 2026-09-16
**Decision:** Admin-uploaded Quran image/audio file IDs carry a `TELEGRAM` or
`BALE` platform key and are resolved only for the requesting bot platform.
**Why:** Bot file IDs are platform-specific; sharing one reference across both
connectors would make delivery fail or silently select the wrong asset.

### DEC-PY-0045 — Dua and ziyarat assets are complete-item deliveries
**Date:** 2026-09-16
**Decision:** Store admin-curated dua/ziyarat text as a complete body and audio
as one complete file per platform; retrieve by a stable slug and never split
these items into Quran-style page ranges.
**Why:** SPEC Q120–122 distinguishes complete dua/ziyarat delivery from exact
Quran page segments, while a slug keeps the first bot surface simple.

### DEC-PY-0046 — Creator welcome text is optional and bounded
**Date:** 2026-09-16
**Decision:** Allow a creator-authored welcome line up to 500 characters,
collected before activation, copied when cloning, and escaped before it is
shown to joiners alongside the standard system welcome.
**Why:** DOMAIN_MODEL §2 permits cosmetic welcome customization without letting
creators replace the moderated system template or inject markup.

### DEC-PY-0043 — Choose content format before activation
**Date:** 2026-09-16
**Decision:** Ask for `AUTO`, `PHOTO`, or `TEXT` in the Quran creation wizard
before the final confirmation; retain the same setting when cloning a khatm.
**Why:** The format is structural content behavior and should be reviewed with
the other pre-activation settings, while the post-creation command supports
legitimate later correction by the creator.

### DEC-PY-0039 — Optional content layers are per-user and asset-gated
**Date:** 2026-09-16
**Decision:** Store translation and tafsir visibility independently per user;
delivery may include either only when a matching library asset exists. A missing
asset is a normal fallback, not an error or a fabricated translation.
**Why:** SPEC Q112–114 makes these layers optional and conditional on database
availability while keeping the minimal reading message intact.

---

### DEC-PY-0038 — Reading font size is per-user
**Date:** 2026-09-16
**Decision:** Keep reading font size in `UserSettings`, with the current bot
surface accepting `normal` and `large` through `/font`; it must not alter the
stored content or affect another member's rendering.
**Why:** SPEC Q108–110 makes presentation a personal preference and the simple
MVP needs a low-friction setting before richer adaptive UX.

---

### DEC-PY-0037 — Reciter preference is policy-resolved
**Date:** 2026-09-16
**Decision:** A user's favorite reciter is honored only if the khatm whitelist
allows it; otherwise choose the first whitelisted reciter by priority, then the
system default. Stable reciter IDs are stored instead of vendor/media URLs.
**Why:** The creator controls available content per khatm while each member can
choose a preference, and future asset providers must not leak into domain logic.

---

### DEC-PY-0036 — Public discovery joins through the existing invite path
**Date:** 2026-09-16
**Decision:** `/public_khatms` lists only active `PUBLIC` khatms. A selected item
gets a normal reusable invitation token internally, then uses the existing
registration and commitment-consent gates before joining.
**Why:** This adds discovery without creating a second membership path or
bypassing identity and pledge safeguards.

---

### DEC-PY-0035 — Advertising reward is opt-in and first-action idempotent
**Date:** 2026-09-16
**Decision:** Store advertising consent on each khatm, keep reward rates as
append-only effective-dated rows, and grant one non-cash credit only after an
active member completes their first assigned action. Use a deterministic wallet
transaction reference as the retry/idempotency key.
**Why:** This follows SPEC Q191–Q210: creator-controlled consent, admin-owned
rate history, active-member eligibility, and no duplicate reward on callback or
worker retry.

---

### DEC-PY-0034 — SMS is an explicit provider boundary
**Date:** 2026-09-16
**Decision:** Application code depends on an async vendor-neutral `SmsProvider`
and normalized send result. The default is `noop`; unknown provider names fail
fast instead of silently pretending delivery succeeded.
**Why:** SMS is optional and paid, and the specification requires a swappable
provider without coupling reminder/account logic to a vendor before credentials
and commercial selection exist.

---

### DEC-PY-0033 — Active plan owns the khatm creation charge
**Date:** 2026-09-16
**Decision:** Resolve one khatm creation charge from the creator's active plan:
`price_toman` for `FIXED`, or `unit_price_toman` for `USAGE_BASED`. Require the
`khatm.create` entitlement before charging; retain the legacy configuration
value only when no plan-definition row exists.
**Why:** It makes the admin-managed plan layer authoritative while preserving a
safe compatibility path for pre-migration deployments.

---

### DEC-PY-0032 — Entitlements are feature-key based
**Date:** 2026-09-16
**Decision:** Store plan definitions with fixed/usage pricing fields and a JSON
feature-key map; application services ask `has_feature(...)` rather than
branching on `FREE/BASIC/PRO`. Seed all three tiers at zero price until the
purchase UI and real gateway are wired.
**Why:** SPEC Q67 and Q181–210 require a replaceable entitlement/pricing layer,
while no live PSP credentials exist yet.

---

### DEC-PY-0025 — Locale at notification delivery time
**Date:** 2026-09-16
**Decision:** Store the user's locale in `user_settings` and resolve scheduled
reminder templates per recipient immediately before sending. Missing translations
fall back to Persian.
**Why:** A single khatm may have members with different languages; locale belongs
to the recipient, not to the khatm or shared notification record.

---

### DEC-PY-0026 — Bounded canonical-user search for admins
**Date:** 2026-09-16
**Decision:** Provide a `SUPER_ADMIN` bot command that searches canonical users
by name, phone, platform subject, or UUID, capped at ten results (and never
expose it to regular users).
**Why:** It closes the immediate operational gap without coupling moderation to
an unbounded query or pretending the web admin panel already exists.

---

### DEC-PY-0027 — Snooze reminders without muting safety notices
**Date:** 2026-09-16
**Decision:** Store `snoozed_until` per participation and suppress only daily,
second, and final reminder stages while it is active. Deadline-miss and other
system notifications remain unaffected.
**Why:** SPEC Q123–124 asks for a temporary deferral, while Q136–138 requires
critical deadline/system notifications to remain reliable.

---

### DEC-PY-0028 — Positive personal report in the bot
**Date:** 2026-09-16
**Decision:** `/report` exposes a compact, positive personal summary and does
not highlight misses or create a public ranking. Monthly contribution totals
use the current UTC month boundary for the MVP.
**Why:** SPEC Q143 requires encouraging personal reporting, while Q144–145
explicitly rejects competitive public leaderboards.

---

### DEC-PY-0029 — Combine daily reminders, preserve staged alerts
**Date:** 2026-09-16
**Decision:** Group same-hour daily reminders by recipient and send one digest;
keep second/final deadline reminders separate and record daily delivery once per
included participation.
**Why:** SPEC Q131–133 asks for less notification noise without hiding a
khatm-specific deadline or weakening per-membership deduplication.

---

### DEC-PY-0030 — Refund unjoined paid khatms to Cash Balance
**Date:** 2026-09-16
**Decision:** Record the creation price on the khatm, permit only its creator
to cancel before any participation exists, and refund the amount internally as
Cash Balance with an audit event.
**Why:** SPEC Q68 and Q181–210 require refund-before-first-join, internal wallet
refunds, and traceable financial operations.

---

### DEC-PY-0031 — Daily Digest is user-configurable
**Date:** 2026-09-16
**Decision:** Default `daily_digest_enabled` to true and let each user switch
between combined and separate daily reminders with `/digest on|off`; critical
deadline/system notices are unaffected.
**Why:** SPEC Q131–133 requires a digest but also requires user control over
notification shape without allowing committed-member safety notices to be muted.

---

### DEC-PY-0024 — Opt-in real-PostgreSQL pytest coverage
**Date:** 2026-09-16
**Decision:** Keep unit tests runnable without external services and gate tests
that require the persistent PostgreSQL container behind
`RUN_INTEGRATION_TESTS=1`.
**Why:** Contributors get fast default feedback, while payment ownership and
replay guarantees are still checked against the real database before release.

---

### DEC-PY-0023 — IANA timezone per member
**Date:** 2026-09-16
**Decision:** Store each user's IANA timezone in the existing `user_settings`
row and expose it through `/timezone`. Reminder and escalation hour checks
convert the current instant per member; invalid legacy values fall back to
the application timezone.
**Why:** SPEC Q85 requires reminders to follow the user's local day without
duplicating timezone state per participation.

---

### DEC-PY-0022 — Creator resolution is explicit and auditable
**Date:** 2026-09-16
**Decision:** After repeated missed Quran commitments, the creator can issue
`continue`, `open`, or `replace` through `/khatm_decision`. The command is
accepted only when the sender owns the target khatm and the target is an
active committed Quran membership. `open` removes the commitment flag,
`replace` uses the existing leave/waiting-list promotion flow, and every
decision is recorded in `audit_logs`.
**Why:** This implements SPEC Q77 while keeping the bot simple and avoiding
silent membership changes by a creator or another user.

---

### DEC-PY-0021 — Gateway-neutral payment callback boundary
**Date:** 2026-09-16
**Decision:** Payment intents are stored against the exact user, amount, and
expiry before a callback can credit the wallet. A gateway must verify the
authority and amount, then an atomic compare-and-swap marks the intent used;
only after that does the wallet ledger receive the cash credit. PSP-specific
requests stay behind `PaymentGateway`.
**Why:** This prevents IDOR and callback replay while keeping ZarinPal/Saman
replaceable. No real PSP adapter is enabled without merchant credentials.

---

### DEC-PY-0020 — Copy only khatm creation settings
**Date:** 2026-09-16
**Decision:** «کپی این ختم» creates a fresh active khatm after an explicit
preview and confirmation. It copies creator-facing creation settings only;
members, portions, progress, and old invitations are never copied. Quran
copies always use the canonical 604-page Madina/Hafs edition.
**Why:** This provides a safe repeat workflow without leaking runtime state or
reusing completed allocations, while preserving the single Quran edition
policy for new khatms.

---

### DEC-PY-0019 — Explicit consent before committed joins
**Date:** 2026-09-16
**Decision:** A deep-link join to a COMMITMENT khatm first shows a short pledge
and requires an explicit «تعهد را می‌پذیرم» action. Only after acceptance does
the workflow create the participation and allocate its first portion; OPEN joins
remain direct. The invite token is carried in the callback to survive transient
FSM-state loss.
**Why:** This is explicitly required by ORIGINAL_SPEC_FA.md Q72 and prevents
an involuntary commitment while preserving the quick path for free participation.

### DEC-PY-0018 — New Quran khatms use only the 604-page edition
**Date:** 2026-09-16
**Decision:** The Quran edition picker in the creation wizard exposes only the
604-page Madina/Hafs edition, as explicitly requested by the user. Existing
database records using the previously available 560- or 286-page IDs remain
readable and are not migrated or deleted.
**Why:** The user wants one canonical Quran edition for new khatms while
preserving existing live data.
**Consequence:** New Quran khatms cannot be created from the older editions;
content assets and page delivery for the 604-page edition remain a separate
Phase 6 task.

### DEC-PY-0000 — Rewrite from scratch in Python; keep the TS project as reference
**Date:** 2026-09-15
**Decision:** Build a new Python project at `C:\xampp\htdocs\Khatm` rather than
continuing the existing TypeScript/NestJS project at
`\\wsl.localhost\Ubuntu-24.04\home\elyas\KhatmSaz`. The old project is left
untouched on disk and used as a reference for domain logic (10 sprints of
already-worked-out rules), not ported line-by-line.
**Why:** User's explicit choice, for performance/preference reasons, after
being told the TS project was much closer to done (397+ tests passing, bot
webhook receiving messages, only one bug away from working) than a rewrite.
**Consequence accepted:** significant duplicate effort; the Python project
starts at zero tests/zero deployment and must re-earn everything the TS
project already had working.

---

### DEC-PY-0001 — Long polling, not webhooks
**Date:** 2026-09-15
**Decision:** `bootstrap.py` starts both bots with `dp.start_polling(*bots)`
(aiogram long polling), not a webhook + HTTP server.
**Why:** The TS deployment got stuck specifically in the webhook path
(Cloudflare Tunnel + `TelegramSender.sendMessage` failing in a way that took
a long, careful debugging session to even localize — see the deployment
report the user provided). Long polling needs only outbound HTTPS from the
server to `api.telegram.org` / `tapi.bale.ai` — no public domain, no reverse
proxy, no tunnel, no webhook secret to manage. Given the user has no
programming background and will operate the server themselves, removing an
entire class of infrastructure (and its failure modes) is worth the small
latency cost of polling.
**Revisit when:** if/when a web dashboard needs its own public HTTP endpoint
anyway, webhooks become a much smaller incremental addition and could be
reconsidered — not before.

---

### DEC-PY-0002 — Module isolation: one folder per domain concept
**Date:** 2026-09-15
**Decision:** `src/khatmsaz/modules/<name>/{models,repository,service}.py`,
with the import rules in `ARCHITECTURE.md` (repositories never call across
modules; only services do; models reference other tables by bare FK column,
not cross-module ORM relationships).
**Why:** User explicitly asked that finished, working parts not be put at
risk when a new feature is added — "قسمت‌های مخصوص به خودش، ایزوله باشه".

---

### DEC-PY-0003 — Identity: canonical User keyed by internal UUID, platforms are links
**Date:** 2026-09-15
**Decision:** Ported unchanged from the original project (its DEC-0010/0032).
A `User` is never a phone number, Telegram id, or Bale id. A
`PlatformIdentity` row links `(platform, subject)` to a `User`; the pair is
globally unique so one external account belongs to at most one user. Phone
number is the cross-platform merge key once phone auth is built (matches
user's answer in the requirements chat: "شماره موبایل یعنی هر فرد یک نفره").
**Why:** Confirmed unchanged — this is exactly the model needed for "someone
active in both Telegram and Bale should count as one person" without forcing
verification on every participant.

---

### DEC-PY-0004 — MVP scoping: template hard-wires khatm_type, for now
**Status: SUPERSEDED by DEC-PY-0007 (2026-09-15, same day).**
**Date:** 2026-09-15
**Decision:** In Phase 1, `khatm/service.py::create_draft_khatm` maps
`QURAN_PAGE → COMMITMENT` and `SALAWAT → OPEN` automatically, instead of
letting the creator choose (and instead of the hybrid mode DOMAIN_MODEL.md
§2 describes as real target scope).
**Why:** Getting one complete, correct, join-to-completion path working end
to end first was more valuable than building the full creator-choice/hybrid
UI before anything worked at all. The underlying data model
(`Khatm.khatm_type`) already supports the real behavior — only the wizard
and `create_draft_khatm`'s defaulting are simplified.
**Why superseded:** the user flagged, right after the first live test, that
the legacy project always asked commitment-mode *before* content type as two
independent questions — this was supposed to be real scope from day one
(DOMAIN_MODEL.md §2), not a later-phase nice-to-have. Fixed the same day; no
reason to wait for Phase 4 once flagged.

---

### DEC-PY-0007 — Commitment mode is an explicit creator choice, independent of content
**Date:** 2026-09-15
**Decision:** The creation wizard now asks "تعهدی یا آزاد؟" (commitment or
open) as its *first* question, before content template. `khatm_type` is
passed explicitly into `create_draft_khatm`/`create_and_launch_khatm` — no
more per-template default. All four combinations are supported and verified
against real Postgres:
  - QURAN_PAGE + COMMITMENT — sequential personal-journey page assignment
    (unchanged from Phase 1).
  - QURAN_PAGE + OPEN — **new**: no page assignment; free-form page logging
    against the chosen edition's total page count, reusing the
    `open_contribution` engine and its overflow/mazad accounting.
  - SALAWAT + COMMITMENT — **new**: every participant is assigned the same
    fixed quantity the creator set at creation
    (`allocation.service.assign_quantity_commitment`), single-tap
    completion. `Khatm.repetition_target` is reused to mean "per-participant
    fixed amount" in this mode (vs. "shared pool target" in OPEN mode) —
    documented inline in `khatm_workflow/service.py`, not a new column.
  - SALAWAT + OPEN — unchanged from Phase 1.
**Why not a new column instead of reusing `repetition_target`:** avoids a
migration for a value that's already unambiguous given `(template_type,
khatm_type)` — the meaning is documented at every call site that reads it.
Chunked/partial logging for a SALAWAT commitment portion (DOMAIN_MODEL.md §3's
"option C" — log 300, then 200, then 500 against one commitment) now supports
both one-tap completion and incremental progress. Also not built: hybrid
khatms where *some* participants are
committed and others open in the *same* khatm (still real scope, still
Phase 4).

---

### DEC-PY-0008 — Reminder/deadline-miss engine: first slice only, no backup reader yet
**Date:** 2026-09-15
**Decision:** Built `daily_deadline_hour` on `Khatm` (creator-set, only for
QURAN_PAGE + COMMITMENT — a one-shot SALAWAT commitment has no "day"
concept) and `modules/reminder_engine/service.py`, run periodically via
APScheduler (`bootstrap.py`, interval configurable via
`REMINDER_SCAN_INTERVAL_MINUTES`). It sends: a morning reminder at a fixed
hour (`DEFAULT_REMINDER_HOUR = 9`, not yet per-participant-configurable even
though `NotificationPreference.reminder_hour` exists in the schema for
exactly that), and a same-day "the deadline passed" notice to the
participant once `daily_deadline_hour` is reached — deduplicated via
`NotificationLog` so neither fires twice in the same day. After
`MISS_NOTICE_THRESHOLD = 2` total misses, the **creator** gets an
informational notice (not an interactive decision — see below).
**Explicitly NOT built in this pass** (real gaps, not oversights — each
needs its own data model before it can exist):
  - **Backup Reader** (a participant opting in to "cover missed portions").
    No such opt-in flag/table exists yet.
  - **Emergency Pool** with claim-lock (anyone can claim a stuck portion for
    a time-boxed window). Needs the same backup-reader-style opt-in data
    plus a lock/expiry mechanism.
  - **A missed portion is never reassigned or released** in this pass — it
    stays `ASSIGNED` to the original participant forever, they just get
    reminded. This matches DOMAIN_MODEL.md's "never silently drop a
    committed member" principle, but stops short of the "creator decides:
    keep / convert to open / replace via waiting list" interactive flow the
    domain describes — today's creator notice is read-only information.
  - **"I won't make it today" and "pause my commitment"** buttons — not
    built; there's nothing yet for them to *do* (no reassignment/backup
    mechanism exists to hand a released portion to).
  - **Per-participant reminder hour** — the field exists
    (`NotificationPreference`) but nothing reads or writes it yet; everyone
    gets `DEFAULT_REMINDER_HOUR`.
**Why ship this slice anyway:** a real, working reminder + miss-visibility
loop is valuable on its own even before the reassignment mechanics exist —
a creator finding out "so-and-so missed twice" via a plain message is
already useful, and doesn't require getting backup-reader/emergency-pool
data modeling right on the first attempt.
**Verified:** scripted scenario against real Postgres — reminder text sent
once, deduplicated on a second scan the same day; a backdated second miss
correctly triggers the creator-threshold notice with the right count.

---

### DEC-PY-0009 — Missed portions go to a shared "emergency pool," not a dedicated backup-reader role
**Date:** 2026-09-15
**Decision:** When `reminder_engine` detects a missed deadline, it releases
the portion back to `OPEN` status (`allocation.service.release_portion`) —
the same pool every not-yet-assigned page already lives in. **Any**
participant in the khatm (not just an opted-in "backup reader") can claim
the next open portion via a new "📖 برداشتن سهم بعدی" button
(`bot/handlers/portions.py`'s `emergency:` callback →
`allocation.service.claim_next_open_portion`), which appears in "🕋
ختم‌های من" whenever a joined COMMITMENT+QURAN_PAGE participation currently
holds no portion (finished their queue, or lost one to a miss).
**Why not build the dedicated Backup Reader opt-in role first:** it needs
its own data (a flag or table recording who volunteered, per khatm) and
its own UI to set it, and the *outcome* for the reader would be identical
either way — "claim the next open page." Shipping the claim mechanism first
means the feature works today; a Backup Reader flag can layer a
*preference order* on top later (try opted-in volunteers before opening
it to everyone) without changing how claiming itself works.
**Race safety:** `claim_next_open_portion` uses an atomic conditional
`UPDATE ... WHERE status = 'OPEN'` (`repository.try_claim_portion`), not a
check-then-insert — two participants tapping the claim button at the same
moment cannot both win the same portion. Verified with a scripted scenario:
release → claim → a concurrently-joining second participant gets a
different, non-colliding portion.
**Historical limitation (superseded 2026-09-16):** the first slice had no
claim time-lock and no dedicated Backup Reader role. Those two gaps are now
closed by `Participation.backup_reader_opt_in` and `KhatmPortion.claim_expires_at`;
emergency reservations expire after two hours and return to `OPEN`.

---

### DEC-PY-0010 — Capacity + waiting list scoped to QURAN_PAGE + COMMITMENT only
**Date:** 2026-09-15
**Decision:** Added `Khatm.capacity` (nullable — unlimited by default) and
`Participation.is_committed` (new column; previously commitment was purely
khatm-level). The wizard asks for capacity only when creating a
QURAN_PAGE + COMMITMENT khatm. Joining past capacity creates the
participation with `is_committed=False` and a `waiting_list` row instead of
rejecting the join — the waiting participant is still ACTIVE and can read
along casually (no assigned portion), matching DOMAIN_MODEL.md §3 exactly.
Leaving a committed participation (`khatm_workflow.leave_khatm`) promotes
the next waiting-list entry: `is_committed` flips to `True` and they get a
real portion assigned, with a cross-platform notification (via
`notify_adapter.get_notify_fn()`, since the promoted person might be on a
different platform than whoever just left).
**Why not extend this to SALAWAT + COMMITMENT too:** a waiting SALAWAT
participant has no natural "read along casually" fallback the way a Quran
waiting participant does (there's no shared page pool to read from without
committing) — building a coherent waiting experience for it needs its own
product answer, not a copy-paste of the Quran behavior. Left uncapped for
now rather than guessing.
**Known limitation (accepted, documented, not silently ignored):** the
capacity check in `participation.service.join` is check-then-insert, not
fully atomic — two joins landing at the exact capacity boundary in the same
instant could both read "under capacity." This is a soft product limit
(a creator's stated capacity might overshoot by one or two in a true race),
not a security or data-integrity invariant, so the added complexity of a
fully serialized check wasn't judged worth it yet. Revisit if it's ever
observed happening in practice.
**Verified:** scripted scenario against real Postgres — 2 joiners fill a
capacity-2 khatm and get portions immediately; a 3rd joiner is correctly
waitlisted with no portion; when the 1st joiner leaves, the 3rd is promoted
and receives a real portion.

---

### DEC-PY-0011 — Hybrid khatms: not building this
**Date:** 2026-09-15
**Decision:** A khatm is COMMITMENT or OPEN for everyone in it — never a mix
of both within one khatm. DOMAIN_MODEL.md §2/§3 originally described a
hybrid mode as target scope; asked the user the specific blocking design
question this raised (a hybrid SALAWAT khatm's `repetition_target` field
would need to mean both "shared pool target" and "fixed per-participant
amount" simultaneously — DEC-PY-0007 already reuses that one field for
those two mutually-exclusive meanings). User's answer: **"we don't have
hybrid khatms, drop it."**
**Consequence:** `Participation.is_committed` (added for DEC-PY-0010's
waiting-list mechanics) remains useful on its own — it still distinguishes
a waitlisted, not-yet-promoted participant from a committed one within a
COMMITMENT khatm — but no wizard path will ever let a creator mix
COMMITMENT and OPEN participants by choice in the same khatm.
**If this ever comes back:** re-read DEC-PY-0007 first — the field-reuse
conflict above is exactly what would need a real answer before building it.

---

### DEC-PY-0012 — Wallet/plan built now; khatm-creation price defaults to 0 until a gateway exists
**Date:** 2026-09-15
**Decision:** Built `wallet.service` (credit-first spending, real-cash
top-up, reward-credit grant, refund — all append-only via
`WalletTransaction`) and `plan.service` (lazy FREE default) fully, and wired
a creation charge into `khatm_workflow.create_and_launch_khatm` via a new
`khatm_creation_price_toman` setting. That setting **defaults to 0**.
**Why 0 and not a real price:** DOMAIN_MODEL.md §7 is unambiguous that
creating a khatm costs money — but there is no live payment gateway
(`ZARINPAL_MERCHANT_ID` is blank, no merchant account provided yet), so
nobody could top up their wallet to pay a nonzero price. Shipping the full
charge/insufficient-funds logic now (verified against real Postgres: a
charge fails cleanly with zero orphan khatm rows when funds are
insufficient; a funded user is charged correctly and the khatm is created)
means turning pricing on later is a one-line config change, not new code.
**`/wallet` command, not a Home-menu button:** wallet top-up isn't
functional yet, so it doesn't earn a permanent slot in the intentionally
shallow menu (DOMAIN_MODEL.md §4) — reachable by typing `/wallet` instead.
**Still blocked on the user:** the actual ZarinPal (or Saman) integration,
real pricing tiers, coupons/promotions, and the advertising-consent credit
program — all real DOMAIN_MODEL.md §7 scope, none buildable without a
payment gateway account or further product decisions on exact tier pricing.

---

### DEC-PY-0013 — Admin bootstrap via a config allowlist; moderation via typed commands, not a panel
**Date:** 2026-09-15
**Decision:** No admin panel exists yet (that's real, deferred scope —
DOMAIN_MODEL.md §8, ROADMAP.md). To have *any* way to reach admin
capability, `SUPER_ADMIN_TELEGRAM_CHAT_IDS` (`.env`, comma-separated numeric
chat ids) auto-promotes whoever's id is listed to `UserRole.SUPER_ADMIN` the
next time they message the bot (`identity.service._bootstrap_super_admin_if_configured`,
called on every `resolve_or_provision_user`). Admin actions
(`/admin_warn`, `/admin_suspend`, `/admin_ban`, `/admin_activate`,
`/admin_grant_credit`) are typed commands gated on that role, targeting a
user by their platform chat id (which the admin has to already know — no
user search exists yet, a real gap).
**Why not build a nicer admin UI first:** the underlying moderation logic
(status transitions, credit grants) is exactly what a future panel would
call anyway — building the commands first means that logic exists and is
tested now, and a panel can be a thin layer over the same `identity.service`
/`wallet.service` functions later.
**Enforcement:** `bot/middlewares.py::ModerationMiddleware`, registered as
an *outer* middleware on both `dp.message` and `dp.callback_query` — runs
before any router/state matching, so a SUSPENDED/BANNED user can't reach any
handler (including mid-wizard) rather than each handler needing to
remember to check. WARNED is intentionally not blocking (matches
DOMAIN_MODEL.md's escalation ladder — a warning is a signal, not a lockout).
**Verified:** scripted scenario against real Postgres — the configured chat
id gets promoted to SUPER_ADMIN on first contact, a plain user doesn't;
warn/suspend/ban/reactivate all transition status correctly; `is_blocked`
correctly treats WARNED as not-blocking and BANNED/SUSPENDED as blocking.
**Verified live, 2026-09-15**: user's real chat id (`5490508090`) added to
`SUPER_ADMIN_TELEGRAM_CHAT_IDS`, confirmed promoted to `SUPER_ADMIN` in the
database after their next `/start`.

---

### DEC-PY-0014 — Khatm-request queue built; wizard integration deliberately NOT built
**Date:** 2026-09-15
**Decision:** `modules/khatm_request` (submit/list-pending/approve/reject)
and `/request_khatm`, `/admin_requests`, `/admin_approve_request`,
`/admin_reject_request` are fully built and verified against real Postgres.
Approving a request does **not** make the requested khatm type usable —
it's recorded as approved and the requester is notified, full stop.
**Why not wire it into the wizard too:** the wizard's template list
(`KhatmTemplateType.SALAWAT`/`QURAN_PAGE`) is hardcoded Python, not
data-driven — there's no registry table mapping a template to its
allocation strategy, wizard questions, and engine behavior. Making a new
"approved" request actually appear as a real, working option in the
creation wizard needs that registry to exist first (a real, sizeable
refactor — DOMAIN_MODEL.md §2/§8 always described this as admin-curated
content, which implies exactly this kind of data-driven registry). Shipping
a request queue that just logs and notifies, without pretending to
auto-activate anything, was judged more honest than half-wiring it.
**What actually happens today when a request is approved:** nothing
automatic — a human (the admin, i.e. the user) still has to manually extend
the wizard code (add a new `KhatmTemplateType` value, wire its allocation
strategy, add its wizard questions) the same way `SALAWAT`/`QURAN_PAGE` were
built. The queue's value today is purely "collect and track what people are
asking for," not "auto-provision it."

---

### DEC-PY-0015 — Participant registration built; city is free text, not a picklist
**Date:** 2026-09-15
**Decision:** A genuine gap from the original spec, only noticed when the
user asked to sweep for anything still missing: DOMAIN_MODEL.md §1's first-
join registration (name, phone, province, city, gender) was never actually
built — the bot was using Telegram's own display name and nothing else.
Fixed: `bot/handlers/registration.py`, triggered from `start.py`'s join flow
the *first* time an unregistered user taps a join link (never at bare
`/start` — matches the spec's "show khatm info, then register only after
they choose to join" order). Province is a picklist of the 31 official
Iranian provinces (`bot/iran_provinces.py`) plus "خارج از ایران"; city is
free text for everyone.
**Why city isn't a province-scoped picklist** (the spec's stated
preference): a full province→city dataset for Iran has hundreds of entries;
reconstructing it from memory risks silent errors or omissions — exactly
the kind of unverifiable fact CLAUDE.md's "no business rule may be invented"
rule warns about. The 31 provinces are official, stable, and low-risk to
hard-code; a city list is not. Free text is an honest, documented
compromise, not a silent shortcut.
**Data model:** `display_name` stays on `User` (identity module);
phone/province/city/gender went onto the already-existing (but
previously-unused) `UserSettings` columns, plus one new column
(`contact_phone` — unverified, trust-based, matching the "مورد اول باشه
اعتماد کنیم" answer from the requirements conversation). New
`settings.service` (`get_or_create`, `is_registered`, `save_profile`) — this
module previously had only `models.py`.
**Verified:** scripted scenario against real Postgres — a brand-new user is
correctly `is_registered() == False`; after `save_profile` +
`set_display_name`, both persist and `is_registered()` flips to `True`.
Not yet exercised through an actual live join in Telegram (needs a second
real account to test the join-triggers-registration path end to end).
**Superseded in part, 2026-09-16 (DEC-PY-0016):** leaving while committed no
longer happens immediately for anyone — see DEC-PY-0016.

**Update, same day:** added Telegram's native "share contact" button
(`request_contact=True`) as an alternative to typing the phone number —
user request. Bale's Bot API doesn't document `request_contact` support, so
Bale users always see the typing path; the handler accepts either
(`F.contact` vs plain text) regardless of platform. Two messages are sent
when a phone is provided (one to clear the reply-keyboard button, one with
the next inline keyboard) — Telegram doesn't allow attaching both a
`ReplyKeyboardRemove` and an `InlineKeyboardMarkup` to a single message.

---

### DEC-PY-0005 — FSM conversation state in memory, not Redis, for now
**Date:** 2026-09-15
**Decision:** `bootstrap.py` uses aiogram's `MemoryStorage` for wizard/
conversation state (creation wizard, contribution-amount prompt), not a
Redis-backed store.
**Why:** `REDIS_URL` is reserved and the module isn't wired yet (see
INTEGRATIONS.md). Getting the conversation flows working correctly first
was the priority; swapping the storage backend later is a one-line change
in `bootstrap.py` (aiogram's `RedisStorage`) with no handler changes needed.
**Consequence accepted:** a bot restart mid-conversation drops the user's
in-progress wizard state (they'd need to start over — not data loss, since
nothing is committed to the DB until the wizard's final "confirm" step).
**Revisit when:** before running more than one bot process, or once losing
in-progress wizard state on deploy/restart becomes annoying in practice.

---

### DEC-PY-0016 — Leaving a committed khatm needs creator approval
**Date:** 2026-09-16
**Decision:** A non-committed participant (OPEN khatm, or still waitlisted)
leaves immediately, same as before. A **committed** participant's "خروج"
request no longer leaves them right away — it sends the creator a message
with ✅/❌ buttons (`bot/handlers/leave.py`: `leave_reason_chosen` →
`approve_leave`/`reject_leave`). Only on approval does
`khatm_workflow.leave_khatm` actually run (status → LEFT, waiting-list
promotion, notifications) — on rejection, the participation is untouched
and the requester is told they're still committed.
**Why:** explicit user decision after being asked to choose between three
options (auto-leave as before, always-require-approval, or drop the leave
feature entirely if it's too complex). Chosen: always require approval for
a committed participant. This also matches the *spirit* of the original
requirements conversation's concern about a committed khatm "breaking" if
people can walk out unchecked — approval is a stronger guarantee than the
automatic-replacement-then-leave flow this superseded.
**No new DB state:** the pending request isn't persisted — the
participation id and leave-reason code are carried through the
`approve_leave:{id}:{reason}` / `reject_leave:{id}` callback data itself.
If the creator never responds, the participant simply stays committed
indefinitely (no timeout/reminder to the creator yet — a real gap, not
addressed in this pass).
**New infra needed:** `bot/notify_adapter.py::send_with_keyboard` — the
existing `NotifyFn` singleton only sends plain text, and a creator on a
different platform than the requester needed an inline keyboard delivered
correctly regardless of which bot instance that is. Added as a second
function rather than widening `NotifyFn` everywhere else.
**Verified:** scripted scenario against real Postgres confirms a
participation stays ACTIVE until `leave_khatm` is actually invoked (i.e.
until "approval" happens), and status/reason update correctly once it is.
The Telegram-side approve/reject button delivery itself is not yet verified
live (needs a real creator + real committed participant in two chats).

---

### DEC-PY-0017 — Khatm visibility (public/unlisted/private); private khatms need creator approval to join
**Date:** 2026-09-16
**Decision:** `Khatm.visibility` (`PUBLIC`/`UNLISTED`/`PRIVATE`, default
`UNLISTED`) — DOMAIN_MODEL.md §2 Q65-66. Only `UNLISTED` (today's existing
behavior: anyone with the invite link joins directly) and `PRIVATE` are
reachable from the wizard; `PUBLIC` exists in the schema but has no
discovery/browse UI to make it meaningful yet (real gap, not a decision to
never build it).
**PRIVATE mechanics:** `join_via_token` raises `JoinRequiresApprovalError`
instead of creating a participation; `bot/handlers/start.py` catches it and
sends the creator (via `notify_adapter.send_with_keyboard` — the same new
cross-platform-keyboard infra DEC-PY-0016 added) a message with ✅/❌
buttons. `khatm_workflow.approve_join_request` runs the *same* join logic
`join_via_token` would have (refactored into a shared `_complete_join`) —
so waiting-list/capacity/portion-assignment behavior is identical whether a
khatm is UNLISTED or PRIVATE; only the timing (immediate vs. after
approval) differs. No pending-request table: khatm id + requester's user id
travel through the `approve_join:{khatm_id}:{user_id}` callback data,
same pattern as the leave-approval flow.
**Verified:** scripted scenario against real Postgres — joining a PRIVATE
khatm raises `JoinRequiresApprovalError` and creates no participation;
`approve_join_request` then creates it correctly; re-joining after approval
correctly raises `AlreadyParticipatingError`. Live Telegram button delivery
not yet verified (needs two real accounts, one as creator one as requester).
**Gotcha hit while migrating:** a brand-new Postgres enum type isn't
auto-created by `op.add_column(..., sa.Enum(...))` in a hand-edited
migration — needs an explicit `CREATE TYPE` first. See DATABASE.md.
