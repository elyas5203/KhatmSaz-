# ROADMAP

Phased so each phase produces something runnable/demoable, not a pile of
unintegrated code. Mark items `[x]` when done, add a dated note — never
delete a completed phase.

## 2026-10-01 — Ephemeral prompts and commitment-flow QA repair (DONE)
- [x] Keep one creator summary and one current question without duplicate resends.
- [x] Delete completed profile prompts and typed answers.
- [x] Ask/persist a daily deadline for all commitment khatm families.
- [x] Compact the creator menu and correct member creator/open/commitment copy.

## 2026-10-01 — Admin alerts and creator-flow copy repair (DONE)
- [x] Reveal manual phone review only after OTP expiry.
- [x] Separate creator-wizard context from its current question.
- [x] Remove abbreviated Imam Mahdi salutations and correct the dedication example.
- [x] Make PUBLIC visibility explicitly mean listing in public khatms.
- [x] Push actionable alerts for the main admin moderation queues.
- [x] Add broadcast-ID search and creator-labelled recipient messages.
- [x] Repair the production member-start missing import.

## 2026-10-01 — Creator finance navigation repair (DONE)
- [x] Open a report/wallet submenu from «گزارش و مالی».
- [x] Keep creator reports distinct from member participation reports when no active khatm exists.
- [x] Explain the VPN-to-Iranian-gateway handoff and successful callback requirement in the payment message.

## 2026-10-01 — Explicit join acceptance and direct member-bot invitations (DONE)
- [x] Show creator/intention context and mode-specific responsibility before joining.
- [x] Require confirmation for both committed and open khatms before registration/membership.
- [x] Preserve a fixed welcome card above one updating question message.
- [x] Share direct Telegram/Bale member-bot links and temporarily disable the web landing page.

## 2026-10-01 — Production repair for invite styling and Salawat image (DONE)
- [x] Make the public invite layout independent of reverse-proxy static URL generation.
- [x] Permit the fixed Salawat content asset in the database check constraint.
- [x] Add migration-head and rendered-page regression coverage.

## 2026-10-01 — Per-khatm reminder settings and public invite refresh (DONE)
- [x] List the member's active khatms with each current reminder time.
- [x] Change one khatm at a time with presets or a custom HH:MM value.
- [x] Keep core reminders mandatory by removing reminder-off actions.
- [x] Show the configured logo and only Persian bot entries on the redesigned responsive join page.
- [x] Make Redis-backed member join and scheduled-start FSM data JSON-safe.

## 2026-10-01 — Restart-safe conversation and OTP fallback (DONE)
- [x] Creator/member FSM state persists in Redis and is isolated per bot.
- [x] Five-minute OTP expiry is represented accurately in user copy.
- [x] Expired undelivered OTP can be escalated to audited admin review.
- [x] Approval notifies the requester and resumes pending khatm creation.

## 2026-10-01 — Member onboarding/reminder UX QA batch (DONE)
- [x] Registration and successful OTP exchanges clean up their own prompts and answers.
- [x] Questions are distinct; invalid answers retain context; weekly counts are unambiguous.
- [x] Creator intro image disappears on Continue and member menu fits in four rows.
- [x] Scheduled devotional reminders include image/PDF or fallback text before the action.

## 2026-10-01 — Server-managed short devotional images (DONE)
- [x] Category and fixed-Salawat image fields accept safe filenames or public URLs.
- [x] Local files are served from a fixed Git-ignored folder and validated on save.
- [x] Telegram/Bale delivery resolves filenames through the configured public web origin.

## 2026-09-30 — Owner creation/editing UX B6–B10 (DONE)
- [x] Trust copy explains isolated invite audiences and required contact purpose.
- [x] Creation and join setup use one updating message with visible progress/back navigation.
- [x] Creator bot/web edit every safely mutable khatm setting; numeric goals are increase-only.
- [x] Welcome examples and commitment questions are specific to each content family.

## 2026-09-30 — Owner creation UX B1–B5 (DONE)
- [x] Creation prompts clean up only their own previous prompt/input messages.
- [x] Quran family is labelled «ختم قرآن».
- [x] Every active creation step has a stateful previous-step action.
- [x] Final confirmation describes available later edits without the old absolute warning.
- [x] Numeric-goal prompts explain completion and future increases without mentioning payment.

## 2026-09-28 — Rotating committed-Quran allocation (DONE)
- [x] Each committed reader advances through their own sequential Quran ranges
      from a distinct staggered offset and wraps at the end (DEC-PY-0092).
- [x] Existing shared-pool plans remain compatible; new plans store exact audio
      boundaries and use per-participant portion identity.
- [x] PostgreSQL migration apply/downgrade/re-apply and integration coverage.

## Phase 1.5 — Scheduled starts (DONE — 2026-09-16)
- [x] Creator chooses immediate or future Tehran-local start time during creation;
      invite links can be distributed before the start.
- [x] Reminder and Today delivery are gated by the scheduled start instant.
- [x] PostgreSQL migration and integration test coverage added.

## Phase 0.5 — Participant registration (DONE — 2026-09-15, found on a full spec sweep)
- [x] Name/phone/province/city/gender collected on first join
      (DOMAIN_MODEL.md §1) — this had been missed entirely until the user
      asked for a full sweep against the original spec. See DECISIONS.md
      DEC-PY-0015 for why city is free text, not a province-scoped picklist.
- [ ] Not yet exercised through an actual live Telegram join — needs a
      second real account.
- [x] Editing profile after the fact (DOMAIN_MODEL.md §1: "بله باید بشه") —
      `/profile` updates name, phone, province, city, and gender (2026-09-16).
- [x] Secure verified-phone replacement (SPEC Q38): `/change_phone` verifies
      the new number by OTP, preserves the same User and all wallet/khatm/
      membership history, rejects an already-owned number, and prevents the
      regular profile editor from bypassing verification (2026-09-18).
- [x] Creator verification gate (SPEC Q7/Q9/Q40): the create and copy flows
      require a complete short profile plus a verified phone, start the OTP
      flow when needed, and recheck before any khatm write or wallet charge;
      `/verify_phone` is the direct entry point (2026-09-18).
- [x] Foreign-number creator verification: non-Iranian E.164 numbers create a
      persistent admin-review request instead of using Kavenegar; Super Admin
      buttons and `/admin_phone_requests` approve/reject it once, with approval
      producing the normal durable phone claim (2026-09-18). Foreign payment
      policy is intentionally pending the owner's later instruction.
- [x] Mobile admin review for foreign verification at `/phone-verifications`,
      scoped to Super Admin/Support, with full submitted number, location,
      purpose, CSRF-protected approve/reject and the shared audited decision
      service (2026-09-18).
- [x] Safe account deletion (SPEC Q39): `/delete_account` requires active
      commitments and creator-owned active khatms to be resolved first, then
      closes open memberships and clears personal fields (2026-09-16).

## Phase 0 — Bootstrap (DONE — 2026-09-15)
- [x] Project skeleton, module folders, config, DB session helper.
- [x] Full schema ported from Prisma to SQLAlchemy (23 tables, all modules).
- [x] Alembic wired; initial migration + partial-index migration verified
      against real Postgres (throwaway Docker container).
- [x] Identity module: resolve-or-provision a User from (platform, chat_id).
- [x] Bot skeleton: shared aiogram Dispatcher, Telegram + Bale client
      factories, `/start` handler, long-polling bootstrap.
- [x] Pytest suite added: unit tests run by default; opt-in payment integration
      test runs against persistent PostgreSQL (2026-09-16).
- [ ] Running against real bot tokens beyond the completed Telegram walkthrough,
      and any deployment, remain pending.

## Phase 1 — First real khatm, single platform, single template (DONE — 2026-09-15)
Goal: a Telegram user can create a small SALAWAT (quantity) khatm, another
user can join and complete it, end to end, for real.
- [x] `khatm` module service: create khatm (DRAFT), activate.
- [x] `allocation` module service: POSITIONAL plan (Quran pages, sequential
      personal-journey assignment, non-overlap enforced). QUANTITY plan for
      OPEN khatms done differently — via `open_contribution`, not a
      pre-generated plan (simpler, matches original project's OPEN-khatm
      design); QUANTITY commitment portions use fixed per-participant targets
      with chunked progress logging.
- [x] `participation` module service: join, leave (simple path — no
      commitment engine yet).
- [x] Bot conversation: creation wizard (template → title → niyyat → target/
      edition → confirm), join via `/start join_<token>` deep link,
      "✅ انجام دادم" / "➕ ثبت مشارکت" flows, `my_khatms` progress view.
- [x] `invitation` module: token-based invite link, works from Telegram
      (deep link) and gives a raw `/start join_<token>` command for Bale
      when a Bale username is unavailable. A mobile-first external landing
      page now previews the khatm and offers Telegram/Bale continuation at
      `/join/{token}`; new invites and QR codes use it when
      `PUBLIC_WEB_BASE_URL` is configured (2026-09-17).
- [x] Active public-khatm discovery via `/public_khatms`, with direct joining
      and the existing registration/commitment-consent gates (2026-09-16).
- [x] Public visibility is selectable in the creation wizard, alongside
      unlisted and private modes (2026-09-16).
- [x] Invite deep links show a landing preview before registration or joining;
      the explicit join button then enters the existing flow (2026-09-16).
- [x] Automated pytest coverage added for message-template rendering and the
      gateway-neutral payment path; `RUN_INTEGRATION_TESTS=1` enables the real
      PostgreSQL test (2026-09-16).
- [ ] Bale still needs a real token; Telegram has been exercised live through
      creation, joining, consent, reminder settings, and commitment progress.

## Phase 1.5 — Commitment mode as an explicit choice (DONE — 2026-09-15)
Flagged by the user right after the first live Telegram test: commitment
mode must be asked independently of content type, not derived from it.
- [x] Wizard now asks "تعهدی یا آزاد؟" first, then content template — see
      DECISIONS.md DEC-PY-0007 (supersedes DEC-PY-0004).
- [x] New `allocation.service.assign_quantity_commitment` — fixed
      per-participant quantity portions (SALAWAT + COMMITMENT), verified
      against real Postgres: two participants each get their own portion,
      completing one doesn't affect the other, single-tap completion.
- [x] QURAN_PAGE + OPEN now works too — free page logging against the
      edition's total, reusing `open_contribution`'s overflow accounting.
- [x] Chunked/partial logging for a SALAWAT commitment (DOMAIN_MODEL.md §3
      "option C") — implemented 2026-09-16 with personal progress and surplus.
- [x] Commitment consent gate — before any committed join, the bot displays
      the short pledge and requires «تعهد را می‌پذیرم» (2026-09-16).
- [x] Copy/repeat a previously-created khatm — «کپی این ختم» shows a preview
      and confirmation, then creates a fresh active khatm without runtime state
      (2026-09-16).
- [x] Per-khatm creator display name (full name, first name, pseudonym, or
      anonymous) is selected before activation and preserved on copies
      (2026-09-16).
- [x] ~~Hybrid khatms~~ — explicitly removed from scope by the project owner;
      mixed committed/open participants will not be built (DEC-PY-0011).

## Phase 2 — Commitment engine + Quran page template (PARTIAL — reminders done 2026-09-15)
- [x] `allocation` service: POSITIONAL (page-range) plan generation,
      non-overlap enforced via the DB partial unique index. (Phase 1.)
- [x] Khatm-level deadline: `daily_deadline_hour`, creator-set at khatm
      creation (QURAN_PAGE + COMMITMENT only — see DECISIONS.md DEC-PY-0008).
- [x] APScheduler wired (`bootstrap.py`, `AsyncIOScheduler`): a periodic scan
      (`reminder_engine.run_once`) sends a morning reminder and a same-day
      deadline-miss notice, deduplicated via `NotificationLog`. Verified
      against real Postgres with a scripted scenario, including the
      creator-threshold notice after repeated misses.
- [x] Per-participant reminder time — `/reminder 0..23` and `/reminder off`
      update committed memberships; the reminder engine reads the preference
      (2026-09-16).
- [x] Full escalation (reminder 1 → reminder 2 → final reminder, distinct
      messages) — first at the member's selected hour, second four hours
      before deadline, final one hour before deadline (2026-09-16). PostgreSQL
      enum values and daily deduplication are covered by migration
      `g7b8c9d0e1f2`.
- [x] Per-user IANA timezone preference via `/timezone`; scheduled reminder
      hour checks now use each member's timezone (2026-09-16).
- [x] Reminder Snooze for ۳۰ دقیقه، ۱ ساعت یا ۳ ساعت; it suppresses only
      reminder-stage sends and leaves deadline/system notices active
      (2026-09-16).
- [x] Daily Digest combines same-hour daily reminders for a user with multiple
      active khatms into one message; staged deadline reminders stay separate
      (2026-09-16).
- [x] Users can enable/disable Daily Digest with `/digest on|off`; disabling
      restores separate daily messages without muting deadline alerts
      (2026-09-16).
- [x] Missed-portion handling: a missed deadline releases the portion to a
      shared "emergency pool" (== the normal OPEN pool); any participant can
      self-serve the next available one via "📖 برداشتن سهم بعدی" in "🕋
      ختم‌های من". Race-safe (atomic conditional UPDATE). See DEC-PY-0009.
      Verified against real Postgres (release → claim → no collision with a
      concurrently-joining second participant).
- [x] Dedicated Backup Reader opt-in role — committed Quran participants can
      opt in/out from «ختم‌های من»; emergency claims require this explicit role
      (2026-09-16).
- [x] Claim time-lock/expiry — emergency reservations expire after two hours
      and return atomically to the pool (2026-09-16).
- [x] Interactive creator decision ("keep / convert to open / replace") —
      after the miss threshold the creator can use
      `/khatm_decision <participation_id> continue|open|replace`; ownership,
      applicability, and the resulting action are checked and audited
      (2026-09-16).
- [x] "I won't make it today" + "pause my commitment" buttons — release the
      current portion without recording a miss; pause also suppresses reminders
      until resumed (implemented and available in the bot).
- [x] Creator toggle for the proactive skip-today action via
      `/khatm_skip_today <khatm_id> <on|off>` (2026-09-16).
- [x] Undo the latest Quran-page completion for up to five minutes; the prior
      portion is restored and only an untouched auto-assigned next portion is
      released (2026-09-16).
- [x] `/report` provides a positive personal progress summary: active and
      completed khatms, completed portions, and this month's open contributions
      (2026-09-16). 
- [x] Automatic previous-month report: timezone-aware configurable schedule,
      Quran/Salawat/completed-khatm totals, fa/ar/en positive copy, downtime
      catch-up, and per-period idempotency with no misses/ranking
      (2026-09-17; SPEC Q105/Q143).
- [x] Per-user reading font-size preference is controllable with
      `/font normal|large` (2026-09-16).
- [x] Shallow home menu now exposes Today, My Khatms, Personal Report, and
      Settings; Today lists current portions with their action keyboard
      (2026-09-16).
- [x] `/help` provides complete, plain-Persian, button-driven guidance for the
      main user and creator journeys without making the home menu deeper
      (2026-09-17).
- [x] Telegram's native command picker exposes the main functional journeys,
      with `/new_khatm` and `/my_khatms` aliases over the same guided button
      flows; Bale command-menu parity awaits its real token (2026-09-18).
- [x] My Khatms now groups owned/joined entries as active, future, or completed
      and suppresses work actions for non-active entries (2026-09-16; live
      Telegram verified).
- [x] Active-khatm cosmetic edits for title and welcome text are available to
      the creator; structural edits remain locked (2026-09-16).
- [x] Open-khatm scheduling supports daily, selected weekdays, fixed-day
      intervals, one specific date, and off; the reminder worker executes it
      with per-user reminder hours. Button-first presets, visible schedule
      summaries, and Tehran-local rejection of past fixed dates are included
      (2026-09-19).
- [x] Creator-controlled pause policy via `/khatm_pause <id> <on|off>`;
      disabled pause actions are enforced server-side (2026-09-16).
- [x] Member pause supports a custom end date in addition to fixed durations;
      local Tehran input is normalized to UTC (2026-09-16).
- [x] Reminder Snooze supports a custom end time in addition to the fixed
      presets; past values are rejected (2026-09-16).
- [x] Creator can disable Snooze per active commitment khatm with
      `/khatm_snooze <id> <on|off>`; all snooze entry points enforce the policy
      (2026-09-16).
- [x] Goal-based completion persists `COMPLETED` for open contributions and
      fully completed positional Quran plans; transition is idempotent
      (2026-09-16). Closed khatms also reject stale joins and contribution
      callbacks.
- [x] Creator-controlled automatic completion summary with positive stats,
      fa/ar/en text, cross-platform delivery, five-minute final-Undo grace,
      reopen-on-Undo, and atomic single-send claim (2026-09-17; SPEC Q95-96).
- [x] Creator-configurable miss-notice threshold and rolling window via
      `/khatm_miss_policy`; defaults are 2 in 7 days (2026-09-16).
- [x] Optional date-based ending via `/khatm_end_at`; the scheduled worker
      closes due active khatms idempotently (2026-09-16).

## Phase 3 — Bale as a real second platform
- [ ] Real Bale bot token tested end-to-end (not just import smoke-tested).
- [ ] Verify a khatm with members split across Telegram and Bale behaves
      identically (shared identity via phone, shared reminders/scheduling).
- [x] Secure self-service phone/OTP linking via `/link_account`: E.164
      normalization, one-time HMAC challenge, same-platform/new-platform
      identity reassignment, `AccountMerge` audit record, and pristine-source
      safety gate (2026-09-17). Live Bale/SMS verification still needs
      credentials.
- [x] Thirty-day inactivity handling: retain the account, delegate assigned
      Quran work to an available opted-in Backup Reader, and avoid a miss for
      the inactive participant (2026-09-16).

## Phase 4 — Waiting list + hybrid khatms (PARTIAL — waiting list done 2026-09-15)
- [x] Capacity + waiting list; promotion flow; "read along while waiting" —
      scoped to QURAN_PAGE+COMMITMENT only, see DECISIONS.md DEC-PY-0010.
      Verified against real Postgres.
- [x] Same for SALAWAT+COMMITMENT (2026-09-20) — owner answered: same as
      QURAN_PAGE, free casual participation via the open pool while waiting.
- [x] ~~Hybrid khatm~~ — **decided against, 2026-09-15.** Asked the user the
      blocking design question (what a hybrid SALAWAT khatm's reported goal
      should mean when it's simultaneously a shared pool and fixed
      per-participant amounts); user's answer: "we don't have hybrid khatms,
      drop it." Not building this. See DECISIONS.md DEC-PY-0011.

## Phase 5 — Money
- [ ] Wallet + PayPing top-up and khatm-creation charge. The PayPing v3
      adapter, one-tap bot UI, public callback, PSP verify, locally bound
      `clientRefId`, amount/code comparison, and atomic replay protection are
      implemented and verified with persistent PostgreSQL/ASGI tests
      (2026-09-17). Remaining before checking this complete: create and store
      a dedicated API token, deploy the callback behind `khatmsaz.com` HTTPS,
      run one live low-value payment, then set a nonzero production creation
      price if desired.
- [x] Internal invoice/receipt lifecycle for every implemented purchase:
      verified top-ups and paid khatm creation store immutable amount
      snapshots; eligible cancellation marks the bound invoice refunded.
      Users can view recent receipts with `/invoices` (2026-09-17).
- [x] Coupon MVP: percentage/fixed discounts with validity, minimum purchase,
      total/per-user usage limits, optional maximum discount, transactional
      redemption, invoice snapshots, `/coupon CODE`, and Super Admin controls
      in both the bot and `/finance` web page (2026-09-17).
- [x] Plan Definition/Entitlement MVP: admin-managed FREE/BASIC/PRO definitions
      with fixed or usage-based price fields and feature keys, via
      `/admin_plans` and `/admin_plan_set` (2026-09-16). Creation and copy flows
      now resolve their authoritative charge from the active plan definition.
- [x] Refund-before-first-join: creator cancellation is confirmed in the bot,
      allowed only with zero memberships, and returns the recorded creation
      charge to Cash Balance with an audit event (2026-09-16).

## Phase 6 — Content library, reciters, translation/tafsir
- [x] Canonical `madina-hafs` exact-page asset registry for `IMAGE`, `AUDIO`, and
      `TEXT` references, with contiguous-range validation (2026-09-16). Actual
      media can now be imported from the selected private Telegram channel by
      forwarding its posts to the bot. Persian page/audio captions are parsed,
      multi-page source posts are de-duplicated during delivery, and coverage is
      reported by `/admin_quran_source_status` (2026-09-17). The verified map
      covers all 604 image pages and all 604 audio pages and is reproducibly
      loaded by `/admin_quran_source_seed`. Live Telegram delivery was verified
      on 2026-09-19: the bot forwarded the source image for pages 1–2 and the
      deduplicated Parhizgar audio post covering pages 1–3. Creator-selectable `AUTO`/`PHOTO`/
      `TEXT` mode is available through `/khatm_content_mode` (2026-09-16).
      Admin can register uploaded page media with `/admin_quran_asset`; asset
      references are platform-scoped for Telegram/Bale (2026-09-16).
- [x] Reciter whitelist per khatm, per-user favorite with fallback; users can
      set their favorite with `/reciter` (2026-09-16). Parhizgar is the default
      source reciter; Quran audio is opt-in with a one-tap settings control
      (2026-09-17).
- [x] Per-user translation/tafsir display toggles with `/content`; delivery
      remains conditional on library assets (2026-09-16).
- [x] Dua/ziyarat complete text/audio library with admin registration and
      `/devotional <slug>` delivery; platform-scoped audio (2026-09-16).

## Phase 7 — Admin (PARTIAL — 2026-09-15)
- [x] Least-privilege delegated administration: content, finance, support,
      moderation, marketing, and operations roles; shared permission checks in
      bot/web, revocable grants, audited changes, and no-code `/admins` role
      management (2026-09-17).
- [x] User moderation (warn/suspend/ban/reactivate), gated on `SUPER_ADMIN` role,
      bootstrapped via a config allowlist and exposed in the secured web panel
      (DEC-PY-0013). Verified
      live: user's real Telegram account confirmed promoted in the database.
- [x] Custom khatm-type request queue → submit/list/approve/reject, with cross-platform
      notification to the requester. Verified against real Postgres. **Approval does
      NOT auto-activate the type in the wizard** — see DEC-PY-0014; that needs a
      template-registry refactor, a separate, real, not-yet-attempted piece.
      Optional Telegram document/photo attachments are now stored as platform
      file metadata and replayed to permitted content admins (2026-09-19).
- [x] Message-template system (placeholders, tone presets, locale keys) — reminder/miss
      text now resolves through versioned locale-keyed templates with safe
      placeholders and Persian defaults (2026-09-16). Per-khatm friendly,
      formal, devotional, and short tone presets are now seeded and selected
      before activation. `SUPER_ADMIN` can list/create versions, inspect
      history, and toggle an exact version from the bot; the web dashboard
      exposes the version history and lifecycle controls (2026-09-16).
- [x] Moderation queue for cover images: creator upload, pending status,
      Super Admin approve/reject commands, audit trail, and approved-cover
      preview display (2026-09-16).
- [x] Creator broadcast moderation for active khatms: pending message queue,
      Super Admin approval/rejection, audit trail, and cross-platform delivery
      to active members (2026-09-16). Cover-image moderation remains pending.
- [x] Audit log — moderation, credit grants, and request decisions are recorded
      in append-only `audit_logs` with actor, target, action, details, and time
      (2026-09-16).
- [x] Read-only Health/Operations dashboard at `/operations`: live database and
      messaging readiness, PayPing/Kavenegar/Bale configuration readiness,
      moderation queue depths, and in-process reminder-worker heartbeat;
      restricted to Super Admin/Operations (2026-09-19).
- [x] Admin user search by display name, phone, platform subject, or UUID via
      `/admin_user_search` (2026-09-16). The Mini App khatm list also searches
      title, creator display name or khatm UUID while combining the existing
      status filter. Both khatm and user search results have 25-row mobile
      pagination that preserves the active query/filter (2026-09-20).

## Phase 8 — SMS + advertising-consent credit program
- [x] SMS provider boundary: vendor-neutral async `SmsProvider`, normalized
      result, factory, safe `noop`, and production Kavenegar REST adapter with
      non-leaking errors (2026-09-18). User opt-in is available through
      `/sms on|off` and requires a saved phone number. Live OTP sending now
      needs only the Kavenegar API key and approved service sender.
- [x] Advertising opt-in per khatm, append-only admin reward-rate history, and
      idempotent Reward Credit after the first completed active-member action
      (assigned portion or open contribution);
      Super Admin rate control is `/admin_ad_rate` (2026-09-16). Ad delivery
      content/count controls and a real campaign provider remain future work.

## Phase 9 — Arabic / English
- [x] Locale-keyed reminder templates filled for `ar`/`en`; Persian remains
      the fallback (2026-09-16).
- [x] Each member's reminder and creator-miss notification uses their saved
      language; `/language fa|ar|en` validates and updates the preference
      (2026-09-16). Full mixed-language UI coverage remains future work.

## Phase 10 — Messenger Mini Apps (Telegram implemented; Bale pending)

- [x] Telegram admin and creator entry uses an HTTPS `web_app` button and
      signed `Telegram.WebApp.initData`; server-side HMAC/freshness/identity/
      role checks issue scoped Secure HttpOnly sessions. Query-string login
      tokens are disabled (2026-09-20).
- [x] Existing mobile dashboard views are reused only as the content rendered
      inside the Telegram Mini App; they are not a standalone product.
- [ ] Bale Mini App launch and signed identity validation: blocked on official
      Bale protocol confirmation and a real Bale token. Do not emulate
      Telegram's signature contract without evidence.
- [x] Creator-authenticated mobile dashboard with signed Telegram Mini App login,
      owned-khatm isolation, and searchable granular member report (full phone,
      location, gender, join/type/Backup status, completion, misses,
      contribution and persisted surplus) (2026-09-17). Creator khatms and
      filtered member reports now paginate at 25 rows while retaining search;
      XLSX export remains complete and was regression-tested (2026-09-20).
- [x] Bot-side creator member overview with per-member progress and role flags
      via `/khatm_members`; dashboard-only exports/analytics remain future work
      (2026-09-16).
- [x] Bot-side "needs attention" queue via `/khatm_attention`, based on
      recorded follow-ups and each khatm's rolling miss window (2026-09-16).
- [x] Bot-side UTF-8 CSV export via `/khatm_export` for member progress and
      miss counts (2026-09-16).
- [x] Inline creator report buttons route to the same guarded views and export
      handler (2026-09-16).
- [x] Creator per-member detail via `/khatm_member`, with ownership and
      participation-scope checks (2026-09-16).
- [x] Bot-side creator analytics and invitation-funnel counts via
      `/khatm_stats`; accepted invitations are persisted for conversion
      reporting (2026-09-16).
- [x] Tracked invitation QR images via `/khatm_qr` and creator management
      button, generated in memory and live-verified in Telegram (2026-09-16).
- [x] Mobile-first admin dashboard MVP rendered inside the Mini App: operational metrics,
      pending queues, khatm list/detail analytics, user moderation, and message
      template lifecycle controls (2026-09-16). Admin khatm/user pagination
      was added 2026-09-20, followed by creator khatm/member pagination;
      production HTTPS deployment remains future work.
- [x] Finance dashboard: aggregate paid/refunded/net totals, recent invoice
      inspection, and CSRF-protected coupon creation/toggling (2026-09-17).
- [x] Sensitive activity timeline: read-only `/audit` with actor/target,
      Tehran-local time, structured details, event-code filtering, and
      Super Admin/Operations-only access (2026-09-17; SPEC Q104).
- [x] `session` module is load-bearing: opaque, hashed, expiring admin sessions
      authenticate the dashboard and are revoked on logout (2026-09-16).

## Explicitly not scheduled
- Public leaderboards / competitive ranking — will not be built (see
  DOMAIN_MODEL "deliberately out of scope").
- Proof-of-completion (photo/audio) — will not be built.
## Completed — 2026-09-30 — Owner spec Section C

- C1–C2: secure member↔creator and creator↔Super Admin ticket/reply paths.
- C3–C6: positive content moderation, shared two-message digital allowance,
  composable audience filters, and moderated text/photo/video/voice delivery.
- Creation wizard: removed its visible cancel action at the owner's request.
