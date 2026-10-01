# DOMAIN_MODEL

This is the condensed product spec, distilled from a long requirements
conversation with the user (Persian). It is the source of truth for business
rules — if a rule needed here is missing, **ask the user, do not guess**
(see CLAUDE.md hard rules). Anything not yet built is marked accordingly;
this file describes the *target* behavior, not necessarily what exists in
code today (check PROJECT_STATE.md / ARCHITECTURE.md's status table for
that).

**The full, un-summarized original text (Persian) lives at
[`../ORIGINAL_SPEC_FA.md`](../ORIGINAL_SPEC_FA.md).** If a decision here
seems ambiguous or a rule needed for a task isn't covered below, grep that
file before asking the user to repeat themselves — summarizing here has
already caused at least one real feature (participant registration) to be
missed entirely once (see DECISIONS.md DEC-PY-0015).

## Vocabulary (Persian ↔ code)

| Persian | Meaning | Code concept |
|---|---|---|
| ختم (Khatm) | A collective recitation effort | `Khatm` |
| سازنده / مشتری (Creator/Customer) | Person who pays to create a Khatm | `User` with role in that khatm = creator |
| شرکت‌کننده (Participant) | Person who joins a Khatm | `Participation` |
| سهم (Portion/Share) | A unit of content assigned to a participant | `Assignment` / `KhatmPortion` |
| تعهدی (Commitment) | Participant is assigned a fixed portion + deadline | `khatm_type = COMMITMENT` |
| آزاد (Open/Free) | Participant contributes at their own pace/amount | `khatm_type = OPEN` |
| نیت (Niyyat) | The stated intention/purpose of the khatm | `Khatm.niyyat` |
| یار ذخیره (Backup Reader) | Volunteer who covers missed portions | `Participation.backup_reader_opt_in` |

## 1. Users

- **Anyone can register.** No approval gate to become a participant.
- **Creating a Khatm costs money** (some pricing model — see §7); joining one
  is always free.
- **Central identity = phone number.** One verified phone = one person, no
  matter how many platform accounts (Telegram, Bale) they use. See
  DECISIONS.md DEC-PY-0003.
- **Only Creators verify their phone (OTP).** Regular participants give a
  phone number as contact info only — **not verified**, trust-based (user's
  explicit choice: "مورد اول باشه اعتماد کنیم"). A participant who later
  becomes a Creator must then verify.
- **Creators outside Iran use one-time manual review instead of Iranian SMS.**
  They enter an E.164 number with country code; the request and full number go
  to an authorized admin. One approval creates the same persistent verified
  phone claim as OTP, so it is not requested again. Rejection leaves identity
  unchanged. Iranian numbers may not use this bypass. Payment behavior for
  foreign creators is intentionally undecided until the owner specifies it.
- **A user can be a participant in many different creators' khatms
  simultaneously**, and **a creator can run many khatms simultaneously.**
- **Account linking across platforms**: "قبلاً حساب دارم" flow — a user on a
  second platform enters their existing verified phone + OTP to link the new
  platform account to their existing User, rather than creating a duplicate.
  This is implemented as `/link_account`; automatic linking is allowed only
  while the newly provisioned source account is still empty, otherwise support
  must review the merge to protect wallet and participation history.
- **Changing a verified phone preserves identity and history**: `/change_phone`
  sends OTP to the replacement number, rejects a number owned by someone else,
  and swaps the verified claim without changing the canonical User. Platform
  links, wallet, created/joined khatms, portions and reports stay attached to
  that same User. Ordinary `/profile` edits cannot bypass this verification.
- **Registration fields** (participant, on first join): first + last name
  (real name, not anonymous — creator needs to see it in reports), phone,
  province, city (from a fixed list for Iran; free-text for non-Iran),
  gender (used later for demographic reports and targeted messaging — not
  cosmetic). No birthdate, no long form. Iran province/city picked from list,
  editable later from a "profile" menu.
- **Creator registration**: same fields + phone OTP verification. No age
  gate beyond "has a verified phone and enough wallet balance."
- **Display name per khatm**: a creator picks, per khatm, how their name
  shows to participants — full name / first name only / a pseudonym /
  anonymous ("a benefactor"). Not a single global setting.
- **Account status**: `ACTIVE → WARNED → SUSPENDED → BANNED`, moderation is
  manual (an admin decides, even if the system suggests it). A `BANNED` user
  should never just be silently deleted — retained for audit.
- **Account deletion**: user-initiated deletion must first resolve any active
  commitments (replace them in every COMMITMENT khatm they're in) before the
  account is actually removed/anonymized — never leave a khatm broken.
- **Language**: every user profile has a `language` field (`fa`/`ar`/`en`)
  from day one even though only `fa` ships first — so a Persian and an Arabic
  participant can be in the *same* khatm and each get bot text in their own
  language later.

## 2. Khatm creation

- **Two-level template picker in the bot**: pick a category (e.g. "ختم
  قرآن") → pick a sub-type (ختم کل / ختم جزء / ختم سوره). If what the
  creator wants isn't in the list, they submit a free-text "request a khatm
  type" which goes to an admin queue; once approved it's added to the
  library and the requester is notified it's now available.
- **Execution mode per khatm — three options, chosen at creation**:
  1. **آزاد (Open)** — every participant sets their own pace/amount.
  2. **تعهدی (Commitment)** — the system assigns a fixed portion + deadline;
     participant explicitly accepts a short commitment text before joining.
  3. **ترکیبی (Hybrid)** — some participants commitment, some open, in the
     *same* khatm (e.g. 301 committed Quran readers + any number of open
     extra participants reading along).
- **Capacity**: not a single fixed number like the old 301-person model.
  Creator picks per-khatm: fixed capacity, or unlimited — the right choice
  depends on the khatm type (e.g. a 1,000,000-salawat open goal may not need
  a participant cap at all). Engine must not hard-code any specific number.
- **Content division is generic**, not just "2 pages/day": for
  page/positional content the creator can choose division granularity (by
  page, by juz/half-juz, by surah/hizb — whatever the template supports);
  for quantity content (salawat, dhikr) the creator sets a target count and
  either (a) each participant free-picks their own sub-target that decrements
  a shared remaining pool, or (b) every participant is assigned the same
  fixed quantity (commitment). **Support both patterns** — this is one
  generic "target + division" engine, not hard-coded per template.
- **Personal Journey + Collective goal, simultaneously (Quran)**: a
  participant's assigned pages advance sequentially for *them* (so after
  ~roughly a year they've personally read the whole Quran too), while the
  group's plan collectively covers the whole book with no gaps/no
  duplicates. Both properties must hold at once.
- **Owner override (2026-09-28, DEC-PY-0094):** new Quran-page members are
  member-controlled even when the creator selected COMMITMENT: each member
  chooses pages/day and delivery hour. Do not assign/show a fixed first share,
  request commitment consent, or expose done/snooze actions. The personal
  cursor still advances sequentially; the older rotating fixed-allocation
  implementation remains legacy compatibility only.
- Quantity commitments (e.g. "1000 salawat") also carry a **frequency**:
  once / daily / weekly / custom, AND a fully free-form variant ("commit to
  100 total, no deadline, whenever you get to it" — participant-controlled
  timing, still counted as a commitment for reporting purposes but with no
  Miss/backup-reader mechanics since there's no deadline to miss).
- **Overflow / mazad (surplus)**: if a participant logs more than the
  remaining target, the system splits it: "N counted toward completing this
  khatm, M counted as your surplus contribution 🌱" — both numbers are kept
  in that participant's personal stats. Never reject an over-log.
- **Start date**: immediate, or a future scheduled date (participants can
  join before it starts; nothing is due until it starts).
- **End condition**: by date, by reaching the numeric goal, or both together
  (goal OR date, whichever comes first) — creator picks at creation.
- **Structural fields lock once the khatm is ACTIVE** (target size, division
  granularity, commitment type) — creator reviews a "double check" summary
  and confirms before it goes live; only cosmetic fields (title, cover image,
  description, welcome text) stay editable afterward. Rationale: changing
  the plan mid-flight breaks participants' already-assigned portions and
  stats.
- **Owner override (2026-09-30, DEC-PY-0099):** creators may increase (never
  decrease) an active repetition target because this preserves all recorded
  progress. Quran's fixed 604-page plan and division remain locked. Cosmetic,
  presentation, reminder and access settings remain editable by the creator.
- **Visibility**: public (discoverable), unlisted (link-only), or private
  (creator manually approves each join request) — creator picks per khatm.
- **Creator-authored content**: creator may set a custom personal welcome
  line shown to new joiners, in addition to the standard system template
  (which already shows the joiner's own name + the khatm's niyyat — "خوش
  آمدید آقای/خانم X، به نیت Y"). A fully custom khatm *template* (not just
  the welcome line) requires admin approval before it can be used, same as
  a fully custom khatm-type request.
- **Cover image**: three options — pick from system presets, upload own
  (goes through moderation before it's live), or none.
- **Cloning**: "duplicate this khatm" — copies all settings from a past
  khatm as a starting point for a new one (creator still edits title/niyyat/
  dates before activating).
- **Join entry points (temporary owner override, 2026-10-01):** generated
  links open the correct Telegram/Bale member bot directly. The external web
  landing is disabled and `/join/{token}` returns 404 until the owner explicitly
  re-enables it. Opening a bot link first shows creator/title/intention context
  and mode-specific acceptance; it never registers or joins silently.
- **Multiple invite links per khatm** (e.g. "Instagram", "family WhatsApp
  group", "mosque QR code") with per-link labels, so the creator can later
  see which channel brought how many members — this is an *advanced*
  setting shown only when the creator opts into "professional mode" for
  that khatm, not part of the simple default flow. QR code generation for
  a link is the same advanced-settings tier.

## 3. Execution — commitment engine

- **A participant in a hybrid khatm chooses, per khatm, commitment or open**
  — the creator does not force it after the fact, and the creator cannot
  silently convert one to the other; only the participant can change their
  own mode (if the khatm design allows it).
- **Before joining**, the participant explicitly accepts mode-specific copy.
  COMMITMENT explains the chosen share/schedule is a religious obligation and
  debt until performed; OPEN explains that a self-entered amount should be
  completed. Only then may registration/membership proceed.
- **Reminder schedule is per-participant, editable anytime** (e.g. "10:00
  for the first half of the month, 14:00 for the second half"); **deadline
  time is set by the khatm** (creator/system), not the participant — a
  participant can move *when they're reminded*, not *when it's due*.
  Timezone is stored per user (future-proofing for non-Iran participants).
- **Miss-handling escalation** (creator-configurable thresholds, default
  shown as an example, not hard-coded):
  1. Reminder 1 (friendly) → Reminder 2 (closer to deadline) → Final
     reminder → deadline passes.
  2. On miss: the portion is offered to a **Backup Reader** (a separate,
     opt-in role — someone who volunteered "I'm available to cover missed
     portions", not automatically the next Waiting List person) or, if none
     available, released to an **Emergency Pool** — anyone in the khatm can
     claim it ("an emergency portion just opened — who wants it?"), with a
     short claim-lock (e.g. 2 hours) so one claimer can't sit on it
     indefinitely without completing it.
  3. The original committed participant is **not silently removed**. After
     N misses (creator-configurable, default suggestion: 2 misses in a
     rolling 7-day window) the system asks the **creator** what to do:
     keep them / convert to open / replace via waiting list. The creator
     decides — the system never auto-removes a committed participant.
  4. **We never say a khatm is "broken."** If a portion is still incomplete
     at day's end, the internal state is `Incomplete Assignment`, and if a
     status message about it was ever sent, it gets deleted/replaced once
     resolved — never leave a negatively-worded message sitting visible.
- **"I won't make it today" button**: lets a committed participant
  proactively release today's portion to backup/emergency *before* the
  deadline, instead of silently missing it. **Per-khatm toggle** — the
  creator can disable this button for stricter khatms.
- **"Pause my commitment" (vacation mode)**: participant can pause for N
  days / until a date; during the pause their portions route to
  backup/emergency automatically; creator can disable this feature per
  khatm too.
- **Completion is single-tap, no confirmation dialog, with a short undo
  window (~5 minutes)**. No photo/audio/proof requirement ever — trust-based
  by design (this is a devotional product, not a compliance product).
- **No partial-progress UI for a single portion** (no "6/10 pages done"
  slider) — a portion is done or not done. (Exception: quantity khatms
  naturally support multi-step logging — see overflow/mazad above — because
  each log is its own quantity, not a fraction of one portion.)
- **Extra reading beyond one's assigned portion** is logged as personal
  surplus stats; it does **not** re-shuffle anyone else's assignment.
- **Global goal reached, some individual commitments still open**: keep
  both facts distinct — `khatm.status = COMPLETED` at the group level, but
  an individual with a still-open personal commitment is told "the khatm
  reached its goal — finishing your remaining commitment now counts as
  surplus," and their number is still tracked.
- **Leaving a khatm while committed**: never an instant, silent removal.
  Show "you're a committed member — to avoid breaking the khatm, we'll find
  your replacement first," then: try backup pool → try waiting list →
  reassign → only then release the original member and notify them "your
  commitment ended, you're free to leave" (and if they don't explicitly
  leave, they simply become a non-committed/open participant going
  forward, not removed).
- **Waiting list**: when a COMMITMENT khatm is at capacity, new joiners land
  in a waiting list and — critically — **can still participate without
  commitment while waiting** (read along casually), and are notified the
  moment they're promoted into a committed seat, from which point *forward*
  they carry a commitment (not retroactively backdated to when they joined
  the waiting list).
- **30-day inactivity**: never remove the user from the bot / their
  account, but any commitment they hold gets handed to someone else via the
  same replacement flow above (they're not penalized further; they can
  resume anytime as an open participant).

## 4. Notifications

- **Reply keyboard / menu kept intentionally shallow**: Home = "امروز" /
  "ختم‌های من" / "گزارش من" / "تنظیمات" (+ "مدیریت ختم‌ها" only if the user
  is a creator). Anything more advanced lives in the messenger Mini App,
  not stacked into bot menus.
- **One daily digest message**, not one message per khatm, when a user has
  multiple khatms due the same day ("امروز ۳ سهم دارید: ..." with one button
  per item) — except a khatm with its own distinct deadline time still gets
  its own separate reminder at that time.
- **System notifications are never mutable** (can't be muted): replaced
  by backup, khatm started, khatm ended, creator made a decision about your
  membership. Regular daily reminders **cannot be muted either** — the user
  explicitly said reminders must always reach a committed participant; only
  Snooze (delay by 30m/1h/3h/custom) is offered, not permanent mute, and a
  creator may disable snoozing per khatm for strict khatms.
- **Reminder copy has selectable "tone" presets** (friendly / formal /
  devotional / very short) picked by the creator at khatm creation, built
  from admin-managed message templates — the creator never free-types
  reminder copy themselves (keeps moderation simple; see admin section).
- **Monthly personal report, always framed positively**: highlights
  completed count / total pages / total salawat / khatms completed; misses
  are never shown in the celebratory summary, only inside the user's own
  detailed history if they dig in. No public leaderboard / no competitive
  ranking anywhere (explicit decision — avoids turning devotion into
  competition/riya).
  This is delivered automatically for the closed previous calendar month in
  each user's timezone, with Quran-page, Salawat, and completed-khatm totals.
  The schedule is configurable and a stored month key prevents duplicate sends.
- **Completion announcement**: reaching the goal or configured end records a
  completed khatm and, when the creator's one-tap setting is on, sends one
  positive summary with member/work totals across linked platforms. It waits
  through the five-minute final-Undo window and never emphasizes misses.
- **Large-text mode**: two sizes only (normal / large), a single toggle in
  the user's own settings, applies across every khatm for that user — not
  something the creator sets.

## 5. Content delivery (Quran / dua / ziyarat text & audio)

- Text is stored either as page images (for Quran, matching the source PDF
  the user already has scanned page-by-page) or as plain text (dua/ziyarat/
  dhikr) — whichever exists for that content item; the bot sends whichever
  is available and never fabricates a missing format.
- Translation and tafsir are **both optional, off by default**, toggled per
  user; tafsir only shows if it exists in the DB for that content — no
  placeholder text if it doesn't.
- **Reciter (qari) selection**: creator whitelists which reciters are
  available for a khatm at creation; a participant picks their preferred
  reciter (remembered across khatms) but falls back to "pick another
  reciter" if their favorite hasn't recorded that particular content
  (avoids a hard error).
- Audio: send the audio **segment matching exactly the participant's
  assigned pages** for Quran (not the whole surah/juz); for dua/ziyarat send
  the complete file (they're not meant to be split). Playback speed control
  (0.75x–1.5x) is a nice-to-have, not blocking.
- Content-serving format choice (send as photo, send as text, or open a
  clean reading view/web link) is itself a per-khatm creator setting — not
  one global behavior.

## 6. Creator reporting

- **In-bot summary is short**: active khatm count, total members, today's
  completion %, "N items need attention" — tapping expands to
  per-portion/per-member detail **only in the Mini App**; the admin and creator
  views are rendered inside the messenger surface. The bot stays simple by design.
- **Creator sees real per-member data** (full name, full phone number,
  province/city, gender, join date, commitment type, completion count, miss
  count, surplus) — the user was explicit that a paying creator should see
  granular data, not just aggregates. This is more permissive than typical
  privacy defaults — do not water it down without asking.
  The creator enters through the signed Telegram Mini App command
  `/creator_app`; its session is separate from admin access and every khatm
  route verifies ownership. The implemented
  report includes these identity fields plus join/type/Backup status,
  completion, misses, contribution, and persisted surplus.
- **"Needs attention" queue**: members who've missed repeatedly, pending
  private-khatm join requests, a cover image awaiting moderation, a waiting
  member ready for promotion, plan expiring soon — surfaced as one list so
  the creator doesn't have to hunt across screens (Mini App feature).
- Advanced analytics (funnels per invite link, geographic/gender
  breakdowns, Excel/CSV export, a shareable graphic completion card) are
  **premium, Mini-App-only features**, gated behind a paid tier —
  build the data model to support them now, but the UI can come later.

## 7. Monetization (build the model flexibly now; keep MVP pricing simple)

- **Creating a khatm costs money; joining is always free.**
- **Wallet-based**: users top up a Toman wallet; creation cost is deducted
  from it (or paid directly via gateway at creation time — both paths must
  work).
- **Two balances, never mixed**: `balance_toman` (real money, refundable to
  wallet only, never to a bank) and `credit_toman` (earned via the
  advertising-consent program below — spendable in-system only, no
  expiry for now). Spending prefers `credit_toman` first automatically.
- **Refund rule**: if a creator deletes a paid khatm *before anyone has
  joined it*, the fee returns to their wallet; once someone has joined,
  deletion needs manual admin/support handling — no automatic refund.
- **Advertising-consent program**: a creator can opt a specific khatm's
  audience into receiving a limited number of admin-authored promotional
  messages per month (the creator does not write the ad copy — only
  opts in/out per khatm); in exchange, the creator earns `credit_toman` per
  *active* member (someone who actually did at least one completion in the
  period) in that khatm, at a rate set by the admin and versioned over time
  (rate changes must not retroactively alter past accruals).
- **Plans/pricing are admin-configurable, not hard-coded**: build a
  flexible plan/add-on/pricing-rule model from day one (admin defines
  plans, one-off add-ons, and promotions/coupons through an admin screen),
  even though the MVP only needs one or two simple tiers. No participant
  cap ever gates pricing — more members is good for the product's growth,
  never penalized.
- **Payment gateway**: the implementation now starts with PayPing v3 because
  that merchant account was supplied after this model was written (ZarinPal
  and Saman remain candidate later adapters) — implemented behind a Provider
  interface so swapping/adding a
  gateway later doesn't touch billing core logic. **IDOR/replay must be
  prevented by design**: a payment's `user_id` is stored server-side at
  intent-creation time and never taken from client input at verification
  time; verification does an atomic compare-and-swap on a `used` flag (the
  original project's `PendingPayment` table pattern — ported as-is, see
  `wallet/models.py::PendingPayment`).
- **SMS credits** are a wallet-purchasable item (not a separate wallet) —
  either the creator buys SMS credits for their whole audience, or an
  individual participant buys their own SMS-reminder credits if the creator
  hasn't.

## 8. Admin

- Content/template library is admin-curated: creator requests are queued,
  admin approves/edits/rejects (with a reason, reusable canned reasons),
  and only then does a new khatm type appear in the picker for everyone.
- Every reminder/system-message template is admin-editable (see §4) through
  a template system with placeholders (e.g. `{{first_name}}`), versioned per
  locale key (`fa` now, `ar`/`en` later) from day one.
- Moderation queue covers: custom khatm-type requests, cover-image
  uploads, creator broadcast messages (a creator's message to their own
  audience needs admin approval before sending — spam prevention), and user
  reports/bans (ban is admin-confirmed, never fully automatic).
- Full audit log for admin actions (who changed what plan/price/ban/refund,
  when) — append-only, never edited. Sensitive-event history is displayed
  only in the Web App as a read-only Super Admin/Operations timeline, never
  as another bot menu.
- Nearly every numeric knob mentioned above (miss thresholds, reminder
  timing, claim-lock duration, ad reward rate, inactivity days) should be a
  configurable setting an admin can tune, not a hard-coded constant — but
  keep the *admin UI* itself uncluttered; not every knob needs its own
  visible control on day one, just a schema that doesn't block adding one.

## Deliberately out of scope for now (explicit user decisions)

- No public leaderboard / competitive ranking, ever (by design, not just
  "not yet").
- No proof-of-completion requirement (photo/audio/timer) — trust-based.
- The Web App is now in scope and its admin MVP is live locally; creator
  self-service and production HTTPS deployment remain incremental work. The
  bot must still keep only the short everyday actions described above.
- No cross-product shared identity — if a future "study bot" or "donation
  bot" is ever built, it gets its own identity space, not shared with
  KhatmSaz (ported from the original project's DEC-0047, still applies).
