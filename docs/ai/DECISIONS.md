# DECISIONS

Append-only. Never edit or delete an old decision — if it's superseded, add a
new entry that says so and link back.

---

### DEC-PY-0094 — Quran reading pace is chosen by each member
**Date:** 2026-09-28
**Decision:** For every new Quran-page participation, including a khatm the
creator labelled COMMITMENT, the member chooses how many pages to receive per
day and the local delivery hour. Joining must not assign or announce a fixed
page range, ask for commitment consent, or show the fixed-portion actions
«انجام دادم» and snooze. The existing open-Quran cursor delivers the selected
pages immediately and advances that reader's sequence thereafter.

This supersedes DEC-PY-0092 for new member-facing behavior. Its rotating
allocation schema/code remains only for compatibility with historical rows;
it is not used for new Quran joins. This owner instruction intentionally also
overrides DOMAIN_MODEL §2's older fixed-portion commitment wording for Quran.

---

### DEC-PY-0093 — Creator bot has one fixed creator menu and starts creation directly
**Date:** 2026-09-28
**Decision:** The dedicated KhatmSaz creator bot always shows the creator menu
to every account, including a new user and the SUPER_ADMIN; language and formal
role must never switch it to a participant menu. After the first language choice
and on a normal `/start`, the bot immediately enters the create-khatm flow.
Choosing to create promotes an ordinary account to `CREATOR`; phone verification,
wallet/plan checks and the normal wizard remain the actual gates. Admin UI is
still available only through the permission-gated `/admin_app`. This supersedes
the creator-bot menu/approval parts of DEC-PY-0076; participant menus live only
in category-specific member bots.

The Iran province keyboard remains two columns: Telegram reply markup has no
responsive breakpoint, and three columns can truncate long labels on narrow
clients. The owner's condition was to use three only if full labels remain safe.

---

### DEC-PY-0092 — Rotating Quran allocation (personal-sequential + collective)
**Date:** 2026-09-28
**Decision:** Owner confirmed: committed Quran readers must advance their OWN
pages sequentially (4,5 → 6,7 → 8,9 …) from a distinct staggered start, wrapping
around the book — the DOMAIN_MODEL §2 rotating model — instead of the current
shared-pool "next open portion" which made each reader's pages jump by the
member count (4,5 → 8,9 → 12,13). Pure math lives in
`allocation.service.positional_range_for_step` (unit-tested,
`tests/test_positional_rotation.py`). **Wiring is a follow-up that needs a
migration** (a per-participation committed offset, analogous to the OPEN mode's
`open_reading_next_page` cursor) + a rewrite of `allocate_next_portion_to`; **Technical blocker for the follow-up:** the current shared-pool model has a partial UNIQUE(plan_id, unit_start) WHERE POSITIONAL constraint (`allocation/models.py`) — the rotating model reads the SAME page ranges repeatedly (per reader, per cycle), which violates that constraint. So the follow-up must also change the portion identity model (portions become per-participation, keyed by (plan, participation, sequence) instead of unique per page range) and needs a real test Postgres to validate the migration — the owner has none, so this row is BLOCKED on a test DB + owner review.
must be reviewed by the owner before applying to production (affects live
khatms — structural, so only NEW khatms should adopt it; existing ACTIVE khatms
keep their assigned portions per the lock-on-active rule).

---

### DEC-PY-0091 — Creation wizard no longer asks the content format
**Date:** 2026-09-27
**Decision:** Owner: remove the «فرمت ارسال محتوا» step (خودکار/فقط تصویر/فقط متن)
from the khatm-creation wizard. The bot should just send whatever content it
has for each page (`ContentDeliveryMode.AUTO`). `create_khatm.choose_edition`
now sets AUTO and skips straight to the next step. The per-khatm content-mode
override still exists in khatm management (`cs:modes`) for anyone who needs it.

### DEC-PY-0090 — Fixed niyyat + optional نیابت (dedication)
**Date:** 2026-09-27
**Decision:** Owner: the niyyat is FIXED for every khatm —
«به نیت ظهور امام زمان علیه السلام». The creator may **not** write a free
niyyat. They may only optionally dedicate the khatm on someone's behalf
(نیابت), typed as a name, which is appended as a suffix
(«… — به نیابت از {name}»). Implemented in `create_khatm._compose_niyyat`;
the former free-text niyyat step is repurposed as the optional نیابت prompt.

---

### DEC-PY-0080 — Multi-bot split: 1 creator + 12 member bots per platform
**Date:** 2026-09-26
**Decision:** Split the single KhatmSaz bot into 26 bots:
- 1 creator bot (ختم‌ساز) per platform — handles creation, management, admin.
  Supports all 3 languages (fa/ar/en) internally.
- 12 member bots per platform — 4 categories (QURAN, SALAWAT, DUA_ZIYARAT,
  LAAN) × 3 languages. Each member bot is single-language.
- Total: 13 Telegram + 13 Bale = 26 bot tokens.
- All run in one Python process, one PostgreSQL database, one event loop.
- Two `Dispatcher` instances: `dp_creator` (creator routers) + `dp_member`
  (member routers). Shared routers on both.
- Bot tokens stored encrypted in `bot_instances` table, managed via admin
  web panel with 2-step confirmation. Creator tokens also in `.env` for
  bootstrapping.
- Invite links point to the correct member bot based on khatm category +
  chosen language. Same token across all language variants.
- Participations track `joined_via_bot_instance_id` so notifications are
  sent from the correct bot.
**Why:** Owner request — better UX (members only see relevant content),
language isolation per bot, separation of creator and member responsibilities,
cleaner menus. The existing single-bot UX had too many buttons and features
visible to users who couldn't use them.
**Full docs:** `docs/ai/multibot/OVERVIEW.md`

---

### DEC-PY-0076 — Separate participant and creator menus
**Date:** 2026-09-24
**Decision:** Introduce a new `CREATOR` UserRole and separate the main menu keyboard based on this role.
1. Regular users (Participants) see a shallow menu with "Today", "My Khatms", "Public Khatms", "Settings", "Contact Support", and "Request Creator Access".
2. Users with the `CREATOR` role see the original menu which includes "Create New Khatm" and "My Report".
3. The `/start` command no longer forces new users immediately into the khatm creation wizard; instead it shows the onboarding info and appropriate menu.
**Why:** To reduce confusion for normal participants who just want to join a khatm and don't need to see creator-specific options. Only users explicitly approved by admins (via the new `creator_requests` table) get to create khatms.

### DEC-PY-0075 — i18n scope: admin bot commands stay Persian-only; admin web panel gets translated; legacy typed settings commands get translated
**Date:** 2026-09-20
**Decision:** Three open i18n-scope questions resolved directly by the
project owner:
1. `admin.py` and all `/admin_*` typed bot commands are **not** translated —
   they remain Persian-only permanently (owner: "همیشه فارسی بمونه
   (توصیه می‌شود)"). Admins are assumed to always work in Persian.
2. The admin web panel (`src/khatmsaz/web/templates/*.html`) **does** need
   multi-language support (owner: "بله، چندزبانه بشه"). Not yet started —
   see `docs/ai/I18N_MIGRATION.md` §3 for the architecture questions the
   next session needs to resolve before starting (where admin-web language
   preference lives, how to expose `t()`-equivalent to Jinja2 templates).
3. The legacy typed-command settings files (`digest_settings.py`,
   `font_settings.py`, `language_settings.py`, `reciter_settings.py`,
   `reminder_settings.py`, `sms_settings.py`, `timezone_settings.py`) —
   superseded by `settings_menu.py`'s button tree but kept for
   power-user/backward compatibility — **do** get full translation (owner:
   "بله، اونا رو هم کامل کن"), despite being lower priority than the
   button-driven flows.
**Why:** Asked directly to unblock the remaining items on the i18n
migration checklist after all "normal priority" bot-handler files were
converted; the owner made a clear scope call for each of the three
categories rather than leaving them as open questions.
**Applies to:** `docs/ai/I18N_MIGRATION.md`, `src/khatmsaz/bot/handlers/admin.py`,
`src/khatmsaz/web/templates/`, the seven legacy settings command files.

### DEC-PY-0074 — Free-tier plan caps are per-creator, admin-editable, and lock new creation (not existing membership)
**Date:** 2026-09-20
**Decision:** A creator gets a free tier: up to 100 members summed across all
their own SALAWAT/DUA/LAAN khatms combined (not per-khatm), and for QURAN_PAGE
a separate, admin-configurable cap that may be a number (owner's example: 302)
or unlimited. When a creator's applicable free-tier cap is reached, existing
khatms and their current members are unaffected — new members may still join
an already-active khatm. What locks is the creator's ability to **create a new
khatm**: they see a clear message that a plan/subscription purchase is
required to create another one. All of these numbers (100, 302, or no cap)
must be admin-editable from the panel, not hardcoded — mirrors the general
"plans must be editable" requirement for the whole plan system.
**Why:** Owner's direct answer when asked to resolve the two open questions
left in `docs/ai/BACKLOG.md` section 4. Not yet implemented — this decision
records the rule so implementation doesn't have to re-derive it.

### DEC-PY-0073 — Dashboard surfaces are messenger Mini Apps, not standalone sites
**Date:** 2026-09-20
**Decision:** Admin and creator dashboards may reuse the existing FastAPI HTML
views, but their supported product entry is a Telegram or Bale Mini App. For
Telegram, launch only through an HTTPS `web_app` button, validate the signed
`Telegram.WebApp.initData` HMAC and a five-minute `auth_date` window on the
server, resolve the Telegram identity, recheck admin/creator authorization,
then issue the existing scoped HttpOnly Secure session. Disable login tokens
in query strings. Keep the old command names only as compatibility aliases;
the visible commands are `/admin_app` and `/creator_app`. Do not invent Bale
authentication parity: keep Bale Mini App entry unavailable until its official
signed-init-data contract and a real token can be verified.
**Why:** The owner explicitly rejected a standalone web product. Signed
messenger identity removes shareable login URLs and binds dashboard access to
the person who opened the button in the chat, while retaining the tested
authorization and dashboard code behind the Mini App shell.

### DEC-PY-0072 — Devotional families are independent top-level choices
**Date:** 2026-09-20
**Decision:** Present Quran, Salawat, Dua/Ziyarat, and La'an as separate parent
choices. Filter children by `KhatmCategoryGroup`; permit custom requests only
inside Dua/Ziyarat. La'an owns children such as La'an Umar, Abu Bakr, Aisha,
and the eightfold Imam Reza item. Reusing the quantity counter internally is
an implementation detail and must never place Dua or La'an under Salawat in
the UI or explanatory copy.
**Why:** The owner explicitly defined this religious/content hierarchy. A
shared counter does not make distinct content families parent and child.

### DEC-PY-0071 — Web and bot review share one foreign-identity service
**Date:** 2026-09-18
**Decision:** Expose pending foreign phone reviews at the mobile
`/phone-verifications` page only to `SUPPORT_USERS` (and implicit Super Admin),
with CSRF-protected approve/reject actions. Show the full submitted number and
profile location because the reviewer must actually verify ownership. Both web
and bot entry points must call the same transaction-safe domain decision
service and produce the same permanent claim, audit event and user result.
**Why:** The owner wants an admin decision and primarily uses a phone. A web
queue is easier to recover and scan than old chat messages, but duplicating
the approval logic in a route would create inconsistent security. Shared
authorization and mutation rules keep the convenience without widening access
to finance/content/marketing staff.

### DEC-PY-0070 — Foreign phone verification is a durable admin decision
**Date:** 2026-09-18
**Decision:** Route non-Iranian E.164 creator-verification and phone-change
requests to a persistent manual-review queue instead of Kavenegar. Notify the
configured Telegram Super Admins with the full submitted number and inline
approve/reject controls; allow Support admins to recover pending requests with
`/admin_phone_requests`. Approval creates the ordinary verified `PhoneClaim`
and therefore remains valid permanently, while rejection changes no identity.
Serialize submission by User and phone, reject already-owned numbers, audit
both outcomes, and notify every linked platform. Never allow `+98` numbers to
choose manual review. Do not invent a foreign-payment policy yet.
**Why:** Kavenegar serves Iranian delivery and cannot be assumed to reach an
international number. The owner explicitly chose one-time human approval as
the equivalent trust decision for foreign creators. Reusing the same verified
claim keeps every downstream creation rule simple and avoids a second class of
partially verified accounts; deferring payment honors the owner's instruction
that this will be specified only after the rest of the project is complete.

### DEC-PY-0069 — Telegram commands mirror the shallow guided menu
**Date:** 2026-09-18
**Decision:** Install a short default and Persian Telegram command list at
startup, containing only implemented primary journeys. Add command aliases for
new-khatm and my-khatms that invoke the existing button handlers rather than
creating parallel flows. Treat command-menu installation failure as non-fatal.
Do not call Bale's equivalent endpoint until a real token confirms parity.
**Why:** The target audience should not have to remember syntax, but hiding all
commands also makes recovery and discovery harder. Telegram's native picker is
a familiar second entrance to the same simple flows and introduces no deeper
home-menu hierarchy or duplicated business logic.

### DEC-PY-0068 — Kavenegar is the first production SMS adapter
**Date:** 2026-09-18
**Decision:** Keep the vendor-neutral `SmsProvider` boundary and safe `noop`
default, but implement Kavenegar as the first real adapter because the original
requirements identify that provider. Use its HTTPS REST `sms/send.json`
contract, form parameters, approved sender and API key. Convert Iranian E.164
numbers to `09...`, require both HTTP success and embedded provider status
200, and normalize errors without logging the key embedded in the URL. Keep
`DEV_OTP` strictly local.
**Why:** All creator/account security flows are already OTP-backed but were
operationally blocked by a placeholder sender. Implementing the confirmed
vendor now leaves credentials and one live delivery test as the only external
dependency while preserving the option to add another provider later.

### DEC-PY-0067 — Creator eligibility is rechecked before every creation charge
**Date:** 2026-09-18
**Decision:** A user may start or copy a khatm only after completing the short
profile and owning one verified `PhoneClaim`. If no claim exists, verify the
saved contact number through the purpose-bound OTP flow; also expose
`/verify_phone` directly. Recheck the claim inside the final create/copy
transaction path before invoking pricing, wallet purchase, or khatm creation.
Failed SMS delivery must fail closed and must not charge or create anything.
Log first verification as `PHONE_VERIFY`, distinct from `PHONE_CHANGE`.
**Why:** SPEC Q7/Q9/Q40 says ordinary participants are trust-based but every
creator is phone-verified. Checking only when the wizard opens leaves a stale
callback window, while checking after purchase could charge an ineligible
account. Two inexpensive checks keep the simple guided UX and put the security
boundary before all financial and creation mutations.

### DEC-PY-0066 — A phone change replaces the claim, never the User
**Date:** 2026-09-18
**Decision:** `/change_phone` verifies the replacement number with a
purpose-bound OTP sent to that number. On success, keep the canonical User
and every dependent record unchanged, revoke the previous verified
`PhoneClaim`, create the replacement claim, and synchronize the profile
contact number in one transaction. Reject a number already verified for
another User and serialize each E.164 ownership change with a PostgreSQL
transaction advisory lock. Once an account has a verified claim, `/profile`
may retain that same number but cannot replace it. Record `PHONE_CHANGE` in
the audit log with only the new number's last four digits.
**Why:** SPEC Q38 requires all history to survive a number change. Replacing
the User would orphan or move wallet and khatm records, while allowing the
ordinary trust-based participant profile editor to change a creator's
verified identity would bypass OTP. The atomic claim swap and per-number lock
close both takeover and concurrency windows without storing another copy of
the full number in the audit details.

### DEC-PY-0065 — Monthly reports summarize a closed local month exactly once
**Date:** 2026-09-17
**Decision:** On or after the configurable local report day/hour, aggregate
the previous calendar month in each user's IANA timezone. Include Quran pages,
Salawat, and completed khatms only; never include misses or rankings. Save the
processed `YYYY-MM` even for an empty month, silently skip empty reports, and
use that key to make the scheduler idempotent. If the process was offline at
the preferred time, the next scan catches up.
**Why:** A current partial month changes underneath the user and can be sent
twice by the recurring worker. Closed local-month boundaries make the summary
stable, while a persistent period key and catch-up behavior avoid both spam
and lost reports. Positive-only copy preserves the non-competitive devotional
tone required by SPEC Q105/Q143.


---

## Older history

Decisions DEC-PY-0064 and earlier were moved to keep this file
readable: [docs/ai/archive/DECISIONS_until_DEC-PY-0064.md](archive/DECISIONS_until_DEC-PY-0064.md).

## DEC-PY-0077: Daily Portions Stack Up
- **Date**: 2026-09-26
- **Context**: The user explicitly requested that positional portions must stack up daily, even if the user misses them.
- **Decision**: Implemented stacked_portion processing by querying the oldest uncompleted assigned portion, rather than enforcing a strict one-portion-per-day completion lock.
- **Consequences**: Overrides the prior owner decision to lock users to a single portion per day. Allows successive completion of stacked portions.
