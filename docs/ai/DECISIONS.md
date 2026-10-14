# DECISIONS

Append-only. Never edit or delete an old decision — if it's superseded, add a
new entry that says so and link back.

### DEC-PY-0129 — Telegram Local Bot API & Heavy Media Mirroring up to 2GB (MASTER-21)

**Date:** 2026-10-14
**Owner confirmation:** To eliminate the cloud Telegram Bot API 20MB download restriction on media (`Bad Request: file is too big`), KhatmSaz natively integrates with a local Telegram Bot API server (`aiogram/telegram-bot-api --local`). The local server raises the file download and upload limit to 2000 MB (2 GB). KhatmSaz uses `TelegramAPIServer.from_base(settings.telegram_api_server_url, is_local=True)` and streams files to Bale using `FSInputFile` directly from the local disk filesystem (`/var/lib/telegram-bot-api`), ensuring zero RAM spikes and automated dual-platform content registration for heavy videos and audio files. See `docs/ai/masters/MASTER_21_LARGE_FILE_TELEGRAM_LOCAL_BOT_API_SUPPORT.md`.

---

### DEC-PY-0128 — Real-Time Background Cross-Platform Media Mirroring for Telegram and Bale (MASTER-20)

**Date:** 2026-10-14
**Owner confirmation:** When an authorized administrator uploads or sets any media (videos via `/set_video`, PDFs via `/set_pdf`, audios via `/set_audio`, or devotional assets via `/manage_content`) on Telegram, the system immediately registers the asset for the source platform, and asynchronously streams the file bytes in the background to Bale (using `BaleAiohttpSession` direct multipart serialization). The resulting Bale `file_id` is registered in `devotional_media` with `asset_platform="BALE"`, and the temporary storage message is removed. The operation is completely non-blocking, fault-tolerant, and delivers seamless zero-bandwidth dual-platform content availability. See `docs/ai/masters/MASTER_20_REALTIME_DUAL_PLATFORM_MEDIA_MIRRORING.md`.

---

### DEC-PY-0127 — Automated cross-platform Telegram-to-Bale media migration pipeline

**Date:** 2026-10-13
**Owner confirmation:** An automated, memory-efficient migration pipeline streams Quran pages (604 images + Parhizgar audio) and devotional assets (Dua, Ziyarat, Khutbah) from Telegram to a dedicated Bale storage chat. Captured Bale `file_id` values are registered in `quran_page_assets` and `devotional_media` with `asset_platform="BALE"`. Delivery on Bale uses these pre-registered `file_id`s for zero-bandwidth instant delivery. The process is strictly idempotent, throttled for rate-limits, and manageable via CLI (`scripts/migrate_telegram_to_bale.py`) and admin command (`/admin_bale_media_status`, `/admin_sync_bale`). See `docs/ai/TELEGRAM_TO_BALE_MIGRATION_MASTER.md`.

---
### DEC-PY-0126 — Live Continuous File Logging, Error Crash Alert System & Telegram Real-Time Error Dispatch (MASTER-12)

**Date:** 2026-10-13
**Owner confirmation:**
1. **Continuous Moment-by-Moment File Logging:** Added rotating file logger writing to `logs/khatmsaz.log` (level INFO) and `logs/errors.log` (level ERROR/CRITICAL with full tracebacks).
2. **Real-Time Telegram Crash Alerting:** Implemented `TelegramErrorAlertHandler` that hooks into the logging engine. Whenever an unhandled exception, critical error, or dangerous bug occurs, an alert is formatted with module name, line number, exception type, error message, and stack trace, and immediately sent to the Super Admin via `@khatmsaz_admin_bot`. Includes debounce rate-limiting (max 1 alert per unique error type/module per 60s) to prevent flood.
3. **Asyncio & Sys Exception Hooks:** Integrated `sys.excepthook` and `asyncio.get_running_loop().set_exception_handler` so silent background task failures are surfaced and dispatched to the admin.
4. **Interactive In-Bot Log Commands:** Super Admins can query `/logs`, `/errors`, and download log files directly in `@khatmsaz_admin_bot`.

---

### DEC-PY-0125 — Dedicated Admin Bot (@khatmsaz_admin_bot) and Complete Isolation of Admin Functions from Creator Bot (MASTER-12)

**Date:** 2026-10-13
**Owner confirmation:**
1. **Dedicated Admin Bot:** Token `8804225228:AAHPfsV4E8oSxjoGSqpD4S3GgkPJxuZKEH4`, username `@khatmsaz_admin_bot`. All administrative operations, settings, stats, and moderation workflows are hosted exclusively on this bot.
2. **Creator Bot (`Khatm_Saz_bot`) Isolation:** `Khatm_Saz_bot` is strictly and exclusively dedicated to creating and managing khatms for creators. Even the Super Admin using `Khatm_Saz_bot` sees only the creator menus. All admin push notifications, receipt moderation, La'n khatm reviews, and crash alerts are diverted to `@khatmsaz_admin_bot`. (Supersedes the admin dispatch channel in `DEC-PY-0124`).
3. **Strict Role-Gating:** Access to `@khatmsaz_admin_bot` is restricted to Super Admins (`5490508090` and `UserRole.SUPER_ADMIN`). Non-admins receive an explicit unauthorized notice.

---

### DEC-PY-0124 — Direct PayPing link (ppng.ir/d/VFBD), removal of card numbers, 8-digit numeric tracking code (MASTER-11, partially superseded by DEC-PY-0125 for dispatch bot)

**Date:** 2026-10-13
**Owner confirmation:**
1. **Elimination of Card Numbers:** Bank card number and holder name are completely removed from the wallet recharge screen.
2. **Dedicated PayPing Direct Link:** The wallet top-up message provides the dedicated open-amount Shaparak link `https://ppng.ir/d/VFBD`.
3. **Clean 8-Digit Numeric Tracking Code:** Replaced the hexadecimal UUID slice (e.g. `01a134f0`) with an 8-digit numeric tracking code (e.g. `83491205`) for clear display in Persian RTL chat and clean banking reconciliation.
4. **Centralized Admin Dispatch via `Khatm_Saz_bot`:** All admin push notifications (receipt approval requests, custom La'an moderation) are dispatched exclusively through the creator bot `@Khatm_Saz_bot`. Super admin chat IDs are resolved both from `.env` and by querying `role == 'SUPER_ADMIN'` in the database. Media uploaded to member bots is cross-downloaded and re-uploaded via `Khatm_Saz_bot` to prevent Telegram file_id authorization errors.

---

### DEC-PY-0123 — La'an Khatm Wizard Redesign: Elimination of preset options, custom title & dhikr prompt, moderation queue, and automated invite delivery (MASTER-11)

**Date:** 2026-10-13
**Owner confirmation:**
1. **Elimination of Preset La'an Categories:** Removed all preset buttons («لعن عمر», «لعن ابوبکر», «لعن عایشه», «لعن هشت‌گانه امام رضا») from the wizard and deleted them from `khatm_categories` and admin panel.
2. **Interactive Wizard Prompts:** Selecting "لعن" immediately asks:
   - Question 1: «عنوان ختم لعنتون چیه؟» (Creator enters custom title)
   - Question 2: «متن ذکر لعن را وارد کنید:» (Creator enters custom dhikr / recitation text)
   - Followed by the regular wizard steps (Commitment vs Free, count/goal, schedule, deadline hour, niyyat).
3. **Pending Moderation Queue:** Upon completion, the khatm is created in `status = DRAFT` / `pending_lan_approval = True`. The creator is informed that member recruitment is inactive until admin approval.
4. **Super Admin Dispatch & Inline Review:** The request is dispatched to `@Khatm_Saz_bot` for super admins with `[✅ تأیید و فعال‌سازی]` and `[❌ رد کردن]` buttons.
5. **Automated Invite Card Delivery upon Approval:** Upon admin approval, the khatm status becomes `ACTIVE` and the invitation card along with member invite links is immediately sent to the creator in `@Khatm_Saz_bot`.

---

### DEC-PY-0122 — 30-day PRO Plan duration, additive renewal, pre-lapse warnings (7-day and 24-hour), and automatic downgrade

**Date:** 2026-10-13
**Owner confirmation:**
1. **30-Day PRO Plan Duration:** The PRO plan duration is strictly 30 days (1 month).
2. **Additive Renewal:** Renewing an active PRO plan adds 30 days additively to the current expiration date (`current_expires_at + 30 days`), preserving remaining time. If renewed when expired, it starts 30 days from now.
3. **Pre-Lapse Automated Warnings:**
   - **7 days before expiration:** Bot sends a friendly reminder highlighting remaining days and prompt to renew without interruption.
   - **24 hours before expiration:** Bot sends a final alert that only 24 hours remain before returning to standard tier.
4. **Automatic Downgrade & Notification upon Lapse:** If not renewed by `expires_at`, the user automatically lapses out of PRO (to BASIC if active members exceed cap, else FREE), and receives an expiration notification.
5. **Periodic Scheduler & Lazy Check:** Checked every minute by `plan_service.process_plan_expirations_and_reminders` via AsyncIOScheduler, with lazy expiration fallback in `get_plan`.

---

### DEC-PY-0121 — Broadcast 1,000-recipient tier pricing, removal of free messages, bank receipt upload / PayPing direct link top-up, and admin-only creator panel guard (MASTER-10)

**Date:** 2026-10-13
**Owner confirmation:**
1. **Broadcast 1000-Recipient Tier Pricing:** Pro plan does not include unlimited broadcasts. Every broadcast charges `ceil(audience_count / 1000) * price_per_1000` from the user's wallet. Even for an audience of 1 to 1000, 1 package fee is charged. For 6000 recipients, 6 package units are charged. Free broadcast quotas (e.g. 2 free messages) are completely abolished.
2. **Basic Plan Broadcast Exclusion:** Basic plan users do not have broadcast messaging entitlements.
3. **Creator Panel Restricted to Admin Only:** Until fully refined and approved, access to the Creator Panel (`/creator/*`, `/mini/creator/*`, and in-bot button `creator:web_login`) is strictly restricted to `SUPER_ADMIN` users. Regular users receive a friendly Persian upgrade notice.
4. **Bank Receipt Upload Flow & PayPing Direct Link:** Automated redirect/callback payment is bypassed. Users recharge via card-to-card or PayPing direct open-amount link (`payping.ir/d/...` or `payping.ir/@Username`), upload a receipt screenshot in the bot, which is dispatched to super admins with inline approve/reject buttons. Approving credits the user's wallet immediately and issues an invoice.

---

### DEC-PY-0120 — Post-completion two-message flow (Confirmation + Invite Link, then separate Progress Report), removal of 'read another portion' button, and removal of 14:00 member broadcast

**Date:** 2026-10-11
**Owner confirmation:**
1. **Separate Confirmation & Progress Report Messages:** Upon clicking the share completion button (`share_done:`, `regular_done:`, `regular_early_done:`, `done:`), the bot must send **two separate messages** in sequence:
   - **Message 1 (Confirmation + Invite Link):** Thanks the member, confirms the portion is logged in the khatm and niyyat, and includes the direct member-bot invitation link (`_invite_friends_line`) encouraging the member to invite friends to share in the reward.
   - **Message 2 (Progress Report):** Sent immediately after Message 1 as a standalone message displaying overall khatm progress (`build_motivational_progress_snippet`: before today, today's recitations, total completed, and percentage).
2. **Remove "Read Another Portion" Button:** The inline button `[📖 خواندن یک سهم دیگر]` (`today_pick:{part.id}`) is completely removed from post-completion messages.
3. **No 14:00 Scheduled Broadcast to Members:** The automatic 14:00 daily digest broadcast to members (`deliver_member_daily_digests`) is disconnected from `reminder_engine/service.py:run_once`. Members receive the progress report on-demand immediately upon completing their portion rather than at 14:00.

---

### DEC-PY-0119 — Creator Web Panel ground-up redesign, Mobile-First navigation, bot invite link generation, and zero-confusion UX

**Date:** 2026-10-11
**Context & Scope:** Comprehensive ground-up rebuild of the Creator / Organizer Web Panel (`/creator`) across all 7 views in `src/khatmsaz/web/templates/` (`creator_base.html`, `creator_dashboard.html`, `creator_khatms.html`, `creator_khatm_detail.html`, `creator_khatm_new.html`, `creator_wallet.html`, `creator_broadcasts.html`, `creator_login.html`).
**Decisions:**
1. **Mobile-First Architecture for Mini-Apps:** Implemented responsive Estedad 5.3.0 layout with a fixed bottom dock (home, khatms, new, wallet, broadcasts) optimized for Telegram and Bale in-bot WebApps.
2. **First-Class Invite Links:** The web panel resolves the khatm's domain/bot category and renders 1-click copyable Telegram (`t.me/...`) and Bale (`ble.ir/...`) deep invite links directly on the detail page, with Web Share API native sharing.
3. **Dynamic Visual Progress Bars:** Dashboards and khatm cards calculate `progress_pct` against completed portions or repetition targets.
4. **Organizer Lifecycle Actions:** Direct status toggle (pause/resume) and member removal from the web interface.
5. **Niyyat Persistence:** Form field `niyyat` parsed and passed to `workflow_service.create_and_launch_khatm`.

---

### DEC-PY-0118 — Ground-up Admin Panel redesign, custom La'an moderation, web media upload, and fixed PRO plan

**Date:** 2026-10-10
**Owner confirmation:**
1. **Custom La'an moderation (`pending_lan_approval`):** Custom La'an khatms can be approved, edited, or rejected both in the Web Admin Panel (`/moderation` and `/categories`) and via inline buttons in the Telegram admin bot. Until approved by an admin, the khatm must not be joinable/active, and the invite link is sent to the creator upon approval.
2. **Devotional & Khutbah media management in Web Admin Panel:** Support both direct file upload from computer/mobile in the web panel (which sends the file via the creator bot to obtain and store `file_id` in `devotional_media`) AND direct entry of `file_id` or URL for large files (>50MB).
3. **PRO plan model:** Fixed-price `PRO` plan (paid from wallet at the admin-configured `PRO` price to disable ads completely) plus manual admin override to set any user's plan (`FREE` / `BASIC` / `PRO`) from the Web Admin Panel.
4. **Admin Panel routing & UI:** Rebuild the Admin Panel across the 10 modules with `[؟]` simple-language popup guides and step-by-step instructions while preserving/aliasing legacy URL paths (`/categories`, `/devotionals`, `/bots`, `/operations`, `/broadcasts`, etc.) so existing links and tests continue to work seamlessly.
>>>>>>> update_khatm_wizard_flow

---

### DEC-PY-0117 — Quran numeric and scheduled shares

**Date:** 2026-10-05
**Owner confirmation:** Quran has both numeric and regular modes. Numeric mode delivers a specified page range immediately; an OPEN reservation lasts 168 hours with the agreed day-six local-noon warning. COMMITMENT pages remain owed until completed. Regular Quran supports a page amount and selected weekdays. Preserve the existing personal page order; creator-fixed quantities remain immutable. This supersedes the earlier UI restriction to a daily-only Quran plan.

---

### DEC-PY-0116 — Fixed daily amounts and outage recovery

**Date:** 2026-10-03
**Owner decisions:** Members cannot override a creator-fixed daily quantity. Amount changes are available for OPEN and member-selected commitment schedules. After a multi-day outage, issue only the current day's occurrence; retain all previously delivered unfinished shares and do not fabricate obligations for unsent outage days.

---

### DEC-PY-0115 — Goal exhaustion, open reservation clock and editable reading settings

**Date:** 2026-10-03
**Owner decisions:** Stop issuing new shares once the total goal is met, retain previously issued commitments, and record additional completions as surplus. An OPEN numeric reservation lasts exactly 168 hours, with its warning at member-local noon six calendar days after the reservation day. Preserve existing members' amounts/schedules without inventing reservation expiry dates. The owner reports mainly test data, but no destructive cleanup is authorized. Members must be able to adjust Quran page counts and audio from their khatm settings; the interaction with creator-fixed daily quantities still needs clarification. No request to change Quran page order was given.

---

### DEC-PY-0114 — Owner authorizes staged execution and clarifies retained commitments

**Date:** 2026-10-03
**Owner approval:** Proceed step by step from `REMINDER_REDESIGN_MASTER.md`; mark ownership and in-progress/completed state so another assistant can continue without overlapping edits. This satisfies DEC-PY-0113's implementation gate, not the production deployment gate.
**Rules:** Seven-day reservation release applies only to OPEN khatms. Committed shares remain owed until performed. Undone scheduled shares remain available while new daily occurrences are delivered. Both creator-fixed and member-selected commitment schedules receive one follow-up two hours after delivery and one reminder an hour before the creator's daily deadline while undone. The owner requests the open reservation's day-six reminder around noon; exact calendar/timezone interpretation remains to be settled before boundary tests. Use plain, warm Persian copy without implying that debt disappears at the deadline.

---

### DEC-PY-0113 — Audit first; owner approval before reminder redesign implementation

**Date:** 2026-10-03
**Owner instruction:** Inspect the project and graphs, create a new handoff master, report its name, then wait for approval before implementing the redesign step by step.
**Decision:** `REMINDER_REDESIGN_MASTER.md` is the pending execution reference for this request. Creator-selected OPEN/COMMITMENT and member-selected numeric/regular flows, fixed daily creator commitments, reminder reliability and message cleanup must be assessed together. This records the approval boundary, not authorization to migrate or deploy.
**Unresolved:** Seven-day expiry versus commitment debt, Quran allocation, goal exhaustion, old membership migration and follow-up scope remain explicit questions in the master. Existing domain rules are not silently superseded by proposed schema or ambiguous examples.

---

### DEC-PY-0112 — A share is consumable only after its content is delivered

**Date:** 2026-10-02
**Decision:** Manual Today actions, per-khatm actions and scheduled reminders use
the same content-first contract. A completion/logging button and a daily sent
stamp may appear only after the Quran or devotional content was successfully
delivered through the member bot. Legacy participations with no stored bot
instance may be attached only when their khatm family matches the current
member bot; an explicit different instance is never overridden.

**Why:** A generic prompt without the actual reading content lets users record
work they could not perform and can permanently consume that day's share.

---

### DEC-PY-0111 — Member-facing follow-ups stay inside the member bot

**Date:** 2026-10-01
**Decision:** A private join decision and an approved creator broadcast are
delivered through the same category/language member bot in which that member
joined or requested access, never through the creator KhatmSaz bot. Private
approval records that bot instance on the new participation. A broadcast to
several khatms is deduplicated per `(recipient, member bot)`, so one person may
receive it once in each genuinely different member bot where they participate.

**Why:** Mixing creator operations with member conversations is confusing and
breaks the multi-bot boundary visible to users. Bot-scoped media file IDs are
re-uploaded through the member bot when necessary to preserve this boundary.

---

### DEC-PY-0110 — Private approvals work in the creator bot and identify the requester

**Date:** 2026-10-01
**Decision:** Private-khatm approve/reject callbacks are shared by creator and
member dispatchers because the notification may reach any linked creator
identity. The creator-facing request includes the requester's display name,
profile phone and platform numeric identity. Profile/wizard validation notices
are transient and are deleted after a corrected answer.

Salawat commitment creation stores the creator-selected total target in the
live repetition target. Preview mode and consent mode must both derive from the
same enum-safe commitment check; a missing legacy target cannot make a
commitment khatm appear open.

**Why:** Production updates were unhandled on the creator bot, creators could
not recognize private applicants, and inconsistent target persistence caused
the preview and responsibility warning to contradict each other.

---

### DEC-PY-0109 — Member share copy is family-aware and links back to the same khatm

**Date:** 2026-10-01
**Decision:** Share reminders and completion acknowledgements identify the
actual content family (Quran, Salawat, Dua, Ziyarat or La'an), the concrete
share, khatm title and intention. Commitment reminders state the khatm's daily
deadline and use the action «قرائت بخش فوق انجام شد». A completion message
includes a direct invitation to the same khatm through the current member bot
while that flow can issue an invitation.

**Why:** Short generic acknowledgements felt mechanical and did not give the
member enough context or an easy way to invite others into the same reward.

---

### DEC-PY-0108 — Wizard prompts are ephemeral; every commitment has a daily deadline

**Date:** 2026-10-01
**Decision:** Creator/profile questions and their typed answers are transient and
are removed as each step completes. The creator wizard keeps at most one progress
card and one current question; an unchanged Telegram message is not recreated.
Every commitment khatm, including Dua/Ziyarat/Salawat/La'an, asks for and stores a
daily deadline hour. Open khatms explicitly create no religious debt for a chosen
amount, while encouraging the member to complete it out of respect for the group.

**Why:** Accumulating and duplicated questions made the flow unreadable, and
non-Quran commitment khatms were missing a deadline required by the owner.

---

### DEC-PY-0107 — Admin-action queues push alerts; creator wizard uses two messages

**Date:** 2026-10-01
**Decision:** Creator-wizard context/progress and the current question are two
separate bot messages. The progress card may be updated as choices accumulate;
the question card alone owns the current input controls.

Manual review for an Iranian phone is not offered while its OTP remains valid.
The action is revealed on the existing prompt after five minutes. Requests that
require admin action push a best-effort Telegram alert containing enough context
and an identifier, while the persisted moderation queue remains authoritative.
This applies to phone review, creator broadcasts, cover review, requested khatm
types and requested dua categories.

Approved creator broadcasts identify themselves using the display mode chosen
for the targeted khatm. PUBLIC creation copy explicitly states that the khatm is
listed in the public directory.

**Why:** Premature controls confused users, combined wizard text was hard to
scan, and admins should not need to repeatedly open the panel to discover new
work. Persisting first and notifying second preserves requests during temporary
messaging failures.

---

### DEC-PY-0106 — Creator finance is a menu; PayPing credit requires the verified return

**Date:** 2026-10-01
**Decision:** The creator reply button «گزارش و مالی» opens a submenu containing
the creator-khatm report and wallet top-up. An account with no active created
khatm receives an explicit empty creator report; it never falls back to the
member participation report.

Changing or disabling a user's VPN after a payment intent is created does not
change the wallet owner because ownership is bound server-side. Credit is still
applied only after the PayPing browser callback reaches KhatmSaz and the server
successfully verifies it. The payment page therefore tells the user not to close
the flow before seeing the KhatmSaz success result.

**Why:** The old navigation hid the existing top-up flow and displayed a
semantically wrong participation report. Iranian users also need an accurate,
non-alarming instruction for moving from Telegram access to a domestic gateway.

---

### DEC-PY-0105 — Join requires mode-specific acceptance and uses two bot messages

**Date:** 2026-10-01
**Decision:** Before registration or membership, every invite shows the khatm's
creator, title and intention and requires an explicit confirmation. For a
COMMITMENT khatm, the copy states that the member's chosen share or schedule is
a religious obligation and remains a debt until completed. For an OPEN khatm,
the copy states that the amount the member personally enters should be completed
so none of that chosen amount remains outstanding.

After acceptance, the welcome/context card is a fixed standalone message. A
second message owns the current question and is the only message edited as setup
advances. This supersedes the earlier D5 implementation that repeatedly included
the welcome summary inside the updating question message.

Public web landing pages are temporarily disabled. Generated and post-completion
share links go directly to the correct Telegram/Bale member bot; `/join/{token}`
returns 404 until the owner re-enables the web surface.

**Why:** The owner found the combined message hard to read, requires informed
acceptance before a religious commitment is created, and wants sharing to open
the relevant bot directly rather than detouring through a web page.

---

### DEC-PY-0104 — Daily reminders are mandatory and configured per khatm

**Date:** 2026-10-01
**Decision:** A participant's reminder time belongs to one active participation,
not to their whole account. Settings first list the active khatms reachable
through the current member bot and show each saved time; the participant then
changes exactly one khatm using a preset or any valid HH:MM time. There is no
reminder-off action in either the button flow or the legacy typed command.

The public invitation page exposes only Persian member bots until Arabic and
English experiences are complete. It uses the shared admin-configured KhatmSaz
logo rather than maintaining a separate public-page logo.

**Why:** The owner may participate in several khatms in one bot and explicitly
requires different reminder times for them. The owner also stated that reminders
are a core part of the system, not an optional notification, and temporarily
disabled non-Persian public entry points.

---

### DEC-PY-0103 — Conversation state is Redis-persistent; expired OTP may escalate to an admin

**Date:** 2026-10-01
**Decision:** Creator and member FSM data is stored in Redis with keys scoped by
dispatcher and bot ID, without a short idle TTL. A visible conversation must
remain answerable across a service restart until the user completes, cancels or
starts a new flow.

An Iranian SMS OTP remains the first verification method and is valid for the
actual service TTL of five minutes. Manual verification cannot be requested
before the persisted challenge expires. After expiry, the user may create one
normal audited manual-phone request. Admin approval verifies the same number,
notifies the user with a Continue action, and resumes any preserved khatm
creation state; rejection keeps the number unverified.

**Why:** `MemoryStorage` lost state on deploy/restart while leaving the old bot
question visible, which looked like a frozen bot. SMS delivery can also fail;
the owner explicitly requested a secure human fallback after the code window,
not an immediate bypass of OTP.

---

### DEC-PY-0102 — Member setup is self-cleaning and scheduled reminders include reading content

**Date:** 2026-10-01
**Decision:** First-time profile collection and creator phone verification keep
only their current prompt and remove their own typed answers; after successful
completion no registration/OTP exchange remains. Questions are visually marked,
and validation errors must retain the question being answered. The member home
keyboard uses four compact rows.

For regular Salawat/Dua/Ziyarat/La'an commitments, the configured readable
content is sent immediately before the reminder/action message: image pages and
PDF take priority, then text is the fallback. This supersedes the temporary
text-only scheduled-delivery limitation while leaving on-demand delivery intact.

**Why:** The owner observed first-time members being confused by accumulated
questions, a hidden/scrolled menu, and reminders that named a share without
delivering its registered PDF. The conversation should leave only the current
actionable item and the reading material it refers to.

---

### DEC-PY-0101 — Short devotional images may be server files identified by filename

**Date:** 2026-10-01
**Decision:** The category image and the one fixed Salawat image accept either a
full HTTP(S) URL or a single safe filename. A filename refers only to
`src/khatmsaz/web/static/devotional-images/`; nested paths and executable/vector
formats are rejected. It is resolved at delivery time through
`ADMIN_WEB_BASE_URL`, falling back to `PUBLIC_WEB_BASE_URL`.

**Why:** The owner keeps short, single-image La'an/Salawat assets on the VPS and
wants to select them from the Mini App without registering media through a bot.
This extends DEC-PY-0096 without changing chat-registered devotional PDF/image
media. Runtime image files remain outside Git and require no database seed.

---

### DEC-PY-0100 — The two free digital broadcasts are one shared lifetime allowance

**Date:** 2026-09-30
**Decision:** OWNER_SPEC_MASTER C4's phrase «کلاً دو پیام» is implemented as
two lifetime broadcasts total across Telegram and Bale, not two per channel and
not a rolling weekly allowance. Each free send must resolve to fewer than 1000
distinct members. Pending requests reserve a slot, approved/sent requests consume
it, and rejected requests release it. A non-PRO creator needs PRO for a third
digital send or an audience of 1000 or more. SMS is excluded and paid from its
first request at the admin-configured price.

**Why:** This is the literal shared-total interpretation of the owner's wording,
prevents parallel pending requests from exceeding the allowance, and keeps SMS's
explicit paid-from-first rule independent.

---

### DEC-PY-0099 — Active-khatm editing permits safe goal increases, never destructive restructuring

**Decision:** Owner spec B8 requires creators to edit their khatm whenever needed,
including schedule and count where possible. Cosmetic and presentation settings
(title, welcome, visibility, allowed platforms, reminder tone and deadline hour)
remain editable by the owner. A repetition target may only stay equal or increase;
it may never decrease, and Quran's fixed 604-page structure remains immutable.

**Why:** Increasing a repetition goal preserves every recorded contribution while
meeting the owner's editing requirement. Decreasing a goal or changing Quran's
division can contradict already-issued portions and completion history.

**Implementation:** `khatm.service.update_creator_runtime_settings`, creator bot
settings and `/creator/khatms/{id}/settings`. This decision narrows the older
blanket structural lock in `DOMAIN_MODEL.md` without permitting destructive edits.

### DEC-PY-0098 — PRO is an automatic wallet-balance state, not a purchase
**Date:** 2026-09-29
**Decision:** This supersedes DEC-PY-0097. The only active/user-facing tiers
are FREE and PRO. PRO becomes active whenever cash balance plus earned credit
is at least the enabled PRO `PlanDefinition.price_toman`; that admin-managed
value is a threshold and is never deducted. Falling below the threshold makes
the effective tier FREE again. PRO creation has no per-khatm charge. Historical
BASIC/UserPlan rows remain in storage for compatibility but cannot be selected,
configured, displayed, or used to determine the effective tier.

---

### DEC-PY-0097 — Creator-paid PRO upgrade is permanent and database-priced
**Date:** 2026-09-29
**Decision:** The creator UI presents only FREE and PRO. Historical BASIC rows
remain valid in the backend and are displayed as the paid/unlimited state; no
data is migrated or deleted. A FREE creator can buy PRO from wallet funds only
when the enabled PRO `PlanDefinition.price_toman` is positive. The price is
never hard-coded. The purchase uses an append-only PURCHASE invoice, changes
only `UserPlan`, and is serialized per user so repeat/concurrent submissions do
not charge twice. With the current schema PRO has no expiry and is permanent;
adding subscriptions or renewal requires a later owner decision and schema.

---

### DEC-PY-0096 — Salawat is one fixed, category-free recitation
**Date:** 2026-09-29
**Decision:** Salawat never has subcategories. Selecting «ختم صلوات» always
continues directly to the commitment/open mode step with
`content_category_id=None`, even if historical SALAWAT category rows remain in
the database. Those legacy rows are hidden from the category-management panel.

The canonical recitation text is exactly:
«الّلهُمَّ صَلِّ عَلَی مُحَمَّدٍ وَآلِ مُحَمَّدٍ وَعَجِّلْ فَرَجَهُمْ وَالْعَنْ أعْداءَهُم أجْمَعِینَ».
The admin may optionally save one public HTTP(S) image URL in the content
panel. With an image, the bot sends the image with this fixed text as its
caption; without one, it sends the text alone. Dua/Ziyarat and La'an retain
their category flows.

---

### DEC-PY-0095 — First Quran pages wait for the chosen hour; titles are automatic; OTP is deduplicated
**Date:** 2026-09-29
**Decision:** Choosing a Quran delivery hour configures the schedule only. No
pages are reserved or sent during setup; the first batch, like every later
batch, is sent by the reminder engine when that hour arrives. This refines
DEC-PY-0094, whose phrase “delivers ... immediately” is superseded.

Creators are not asked to type a khatm title. The application generates a
localized standard title from the Quran/Salawat template or selected devotional
category. An OTP is valid for five minutes, and repeated or concurrent requests
for the same user, phone and purpose reuse that active challenge without
sending another SMS.

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
