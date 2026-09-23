# PROJECT_STATE

> Newest entry is always at the top. Read this file first in every session.

## Current state — 2026-09-23 — scheduler cron fix + minute-level reminder + post-reg redirect + deploy docs [Claude Code]

**مشکل ۱ — یادآور سر ساعت ارسال نمی‌شد:**
ریشه احتمالی: scheduler با `interval` اجرا می‌شد؛ اگه بات در لحظه اشتباهی start می‌شد،
ممکن بود ساعت هدف کاملاً skip بشه. بعلاوه چک `current_hour == reminder_hour` اگه scanner
دیر/زود می‌رسید مشکل داشت.

**تغییرات:**
- `bootstrap.py` — scheduler از `interval(30min)` به `cron(minute="0,15,30,45")` تغییر کرد؛
  حالا بدون توجه به زمان start بات، هر ۱۵ دقیقه دقیقاً اجرا می‌شه
- `reminder_engine/service.py` — تابع `_is_reminder_due()` اضافه شد؛ به‌جای `current_hour == reminder_hour`
  (نقطه‌ای)، از پنجره ۱۵ دقیقه‌ای استفاده می‌کنه — اگه scanner کمی دیر برسد باز درست کار می‌کند؛
  logging برای debug اضافه شد
- `notification/models.py` — ستون `reminder_minute` (INT default=0) به `notification_preferences` اضافه شد
- `notification/repository.py` + `notification/service.py` — `upsert_preference` و `set_reminder_preference`
  پارامتر `reminder_minute` گرفتند
- `migrations/versions/a1b2c3d4e5f6_add_reminder_minute.py` — migration جدید

**مشکل ۲ — پشتیبانی از زمان دقیق (مثل ۷:۴۵):**
- `bot/handlers/start.py` — تابع `_parse_delivery_time()` اضافه شد؛ فرمت‌های `7`، `07`، `7:45`،
  `19:30` همه قبول می‌شن؛ دقیقه هم ذخیره می‌شه

**مشکل ۳ — بعد از احراز هویت هدایت خودکار به ساخت ختم:**
- `bot/handlers/registration.py` — وقتی کاربر بدون `pending_token` ثبت‌نام می‌کنه،
  بلافاصله ویزارد ساخت ختم باز می‌شه

**مستندات جدید:**
- `docs/ai/DEPLOY.md` — راهنمای کامل push + deploy روی سرور + rollback
- `docs/ai/ANTIGRAVITY_PROMPT.md` — متاپرامپت برای Antigravity (مالک می‌تونه مستقیم بده)
- `docs/ai/AI_HANDOFF_PROTOCOL.md` — هشدار production اضافه شد

**اجرای migration روی سرور لازم است:**
```bash
python -m alembic upgrade head   # migration: a1b2c3d4e5f6
```

**تست: ۶۹ unit test پاس (integration tests نیاز به DB دارن)**

---

## Current state — 2026-09-22 — miss notice: consecutive days + phone number; skip_today confirmed removed [Claude Code]

**تصمیم مالک:** دکمهٔ «امروز نمی‌رسم» حذف شد (قبلاً از UI حذف شده بود، کد مرده هم
پاک‌سازی منطقی شد). بعد از ۲ روز متوالی غیبت، سازنده اطلاع می‌گیرد با:
- نام عضو + شماره تماس
- متن «چیکارش کنیم؟ حذف یا نگه داریم؟»

**تغییرات:**
- `reminder_engine/service.py` — window_days پیش‌فرض ۷→۳؛ شماره تماس همیشه اضافه می‌شود
- `khatm/models.py` + `khatm/repository.py` + `khatm_workflow/service.py` — default به ۳ روز
- `migrations/78e35fca4f39` — default DB و آپدیت همهٔ ردیف‌های موجود
- `tests/test_creator_miss_notice_integration.py` — تست جدید phone + 150 تست پاس

---

## Previous state — 2026-09-22 — BACKLOG item 8: today-vs-yesterday for committed quantity khatms [Claude Code]

**تغییرات:**
- `src/khatmsaz/modules/allocation/models.py` — مدل جدید `CommittedQuantityLog`
- `src/khatmsaz/modules/allocation/repository.py` — `log_committed_quantity` و `committed_quantity_total_between`
- `src/khatmsaz/modules/allocation/service.py` — لاگ خودکار در `record_quantity_commitment_progress`؛ تابع جدید `today_vs_yesterday_committed`
- `src/khatmsaz/bot/handlers/portions.py` — مقایسه امروز/دیروز به پاسخ تعهدی اضافه شد
- `migrations/versions/c8e057163033_add_committed_quantity_logs.py` — جدول و ایندکس جدید
- `tests/test_committed_today_vs_yesterday_integration.py` — تست جدید

**نتیجه: migration اجرا شد، 149 تست پاس.**

---

## Previous state — 2026-09-22 — delivery-hour question extended to ALL khatm types [Claude Code]

**درخواست مالک:** وقتی اعضا به هر ختم تعهدی می‌پیوندند (نه فقط قرآن)، باید
از ساعت تحویل یادآوری پرسیده بشه.

**تغییر:** یک شرط در `start.py::resume_join_after_registration` حذف شد:
`and first_portion.unit_kind == PortionUnitKind.POSITIONAL` — حالا برای هر
`first_portion is not None` (چه POSITIONAL چه QUANTITY) پرسش پرسیده می‌شه.
ختم‌های آزاد که سهم از پیش ندارند (`first_portion is None`) همچنان بدون
پرسش ثبت می‌شوند.

**تست جدید:** `test_fresh_committed_salawat_join_asks_delivery_hour` در
`tests/test_join_delivery_hour_ask_integration.py` اضافه شد.

**نتیجه: ۱۴۸ تست پاس (unit + integration).**

---

## Previous state — 2026-09-22 — start.py join-flow i18n + test isolation fix + creator_web_login DB early-return bug [Claude Code]

دو چیز در این پاس انجام شد:

**۱) باگ test isolation (سوئیت unit):** تست
`test_creator_mini_app_rejects_local_http_origin_before_database_access` در سوئیت
کامل fail می‌شد چون `creator_web_login` پیش از چک HTTPS به DB وصل می‌شد
(`_lang_for` → `session_scope` → asyncpg)؛ connection در event loop قبلی باقی
می‌موند. راه‌حل: چک HTTPS را پیش از هر DB call آوردیم — اگه URL معتبر نبود
مستقیماً با `"fa"` پیام می‌ده و برمی‌گرده. **تمام ۶۸ unit test + ۱۴۷
integration test پاس شدن.**

**۲) ادامهٔ i18n — start.py کامل شد:** همهٔ رشته‌های هاردکد فارسی در
`start.py` که هنوز نشده بودن ترجمه شدن:
- خطاهای لینک دعوت: نامعتبر، منقضی
- ختم: حذف‌شده/غیرفعال، تموم‌شده، عضو قبلی
- کپشن کاور ختم
- متن تعهد (commitment consent)
- لغو عضویت تعهدی / انجام‌نشد
- درخواست عضویت به ختم خصوصی
- ۱۱ کلید جدید زیر `join.*` به `i18n/__init__.py` اضافه شد

`I18N_MIGRATION.md` به‌روز شد: `start.py` و `my_khatms.py` هر دو `[x]` شدن
(my_khatms در پاس قبلی ۲۰۲۶-۰۹-۲۱ کامل شده بود، فقط در چک‌لیست تیک نخورده بود).

**وضعیت i18n:** تنها بخش باقی‌مانده در `I18N_MIGRATION.md` که هنوز `[x]` نشده،
تمپلیت‌های ادمین پنل وب (`web/templates/admin_*.html`) است که طبق تصمیم مالک
«همیشه فارسی بمونه» — یعنی i18n عملاً کامله.

## Current state — 2026-09-22 (overnight autonomous pass) — Bale bot live; critical create-khatm-abandons-on-verification bug fixed; system-settings admin feature added [Claude Code]

Owner gave standing instruction to continue working autonomously overnight
without waiting for approval between steps, testing and fixing as it goes.
This entry covers everything done in that pass — see CHANGELOG.md for full
technical detail on each item, this is the orientation summary.

**Bale bot is now live** — real token + username set in `.env`, confirmed
polling successfully in logs alongside Telegram. Super-admin bootstrap
(previously Telegram-only) now also works on Bale via a new
`SUPER_ADMIN_BALE_CHAT_IDS` setting.

**The most important fix in this pass:** creating a khatm used to
completely restart from scratch if the creator's phone wasn't verified
(or their profile wasn't complete) at the confirmation step — the wizard
just said "run /verify_phone, then start over" and threw away every
answer. This is now fixed end-to-end (verified with a real test that
actually creates a khatm through the unverified-phone path, extracts the
dev-mode OTP code, submits it, and confirms the khatm gets created with
the original data) — see `create_khatm.py::resume_khatm_creation_if_pending`.
**This same mechanism now also applies wherever else a mid-flow
profile/phone verification interrupts something** — the resume hook lives
in one place and both `change_phone.py` and `profile.py` call into it, so
if a similar "wizard gets abandoned" bug is found elsewhere, check whether
it should also call this hook rather than writing a bespoke fix.

**New reusable capability:** a generic `system_settings` key/value table
+ `/admin_settings`/`/admin_setting_set` commands, so small system-wide
numeric defaults don't need a migration each time going forward. Only
`default_reminder_hour` and `inactivity_days` are wired to it so far —
this is the foundation, not a finished "everything is dynamic" project
(see BACKLOG.md's admin-panel audit for what's still genuinely hardcoded:
the reciter whitelist, Quran edition list, and the SALAWAT/LAAN/DUA
category-group enum, the last of which needs a real schema migration to
extend, not just an admin toggle).

**Flagged, not guessed at:** the owner also described a Telegram
phone-share reply-keyboard UX issue in dictation-style Persian that was
ambiguous enough to risk fixing the wrong thing — needs a screenshot or
clearer restatement before `registration.py`'s `_phone_keyboard` gets
touched.

**Verified:** full `pytest` (72) + real-Postgres integration (144 total)
pass; migrations applied cleanly; both bots (Telegram + Bale) restarted
and confirmed polling; `/health` OK.

## Current state — 2026-09-21 (late night) — Join-time delivery-hour ask + auto content push for committed Quran; Postgres crash recovered; bot now runs under a watchdog [Claude Code]

Owner asked for two more things before going offline for the night, plus
one operational question:

1. **"تویه همه مدل ختم‌ها از کاربر بپرسه چه ساعتی برات ارسال بشه"** — every
   committed member should be asked their delivery hour at join time, not
   left to silently default to hour 9. Done: new `AskDeliveryHour` FSM in
   `start.py`, fires once right after a fresh committed Quran join.
2. **"سهم امروز باید اتومات باشه و اصلا دکمه نداشته باشه"** — real page
   content (not just reminder text) should be pushed automatically every
   day, reusing the same mechanism already built for open-Quran readers.
   Done: `reminder_engine.service._push_portion_content`, wired into both
   the first-portion daily digest and `deliver_due_next_portions`.
3. Along the way, found and fixed two more leftover mentions of the
   removed backup-reader wording in `reminder_engine.service`'s default
   reminder text (a third and fourth spot beyond the two fixed earlier
   tonight — this phrase was copy-pasted in several places across the
   codebase, not just one).

**Real infra incident during this work (not caused by these code
changes):** the local Postgres test cluster crashed (OS-level client
backend termination — Windows exception, not a query error) and the bot
process died with it around 19:31. Both were down for roughly 45 minutes
before being noticed and fixed: `pg_ctl start` recovered Postgres cleanly
(WAL replay, zero data loss), and the bot was restarted. **Because the
owner said they were going to sleep and wanted things to keep running
unattended, the bot is now launched via a small shell watchdog
(`/tmp/khatmsaz_watchdog.sh`, logging to `bot-watchdog.log`) that
restarts it automatically on any crash** — this is a *local dev-machine*
mitigation only; the real production fix once deployed to the VPS is the
`systemd` service already documented in `Rahnama.VPS.txt` §13, which has
its own crash-restart policy.

**Deployment question answered:** the owner asked whether they could push
this code to their own GitHub and have the server pull from there instead
of transferring files by hand. Answered yes, with a plain-language
explanation of the tradeoffs (`.env` must never be committed — already
correctly excluded via `.gitignore`), and added a documented alternative
path in `Rahnama.VPS.txt` (new §8-ب) alongside the existing SCP-based
method, so their support team has a written runbook for either approach.

**Verified:** full `pytest` (65) + real-Postgres integration (137 total)
pass; `alembic upgrade head` no-op; bot restarted under the watchdog,
`/health` returns `{"status":"ok","database":"ok"}`.

## Current state — 2026-09-21 — Fixed 3 real UX bugs from owner screenshots (language-leaking button, wrong post-completion keyboard, stale consent wording); flagged one contradiction with a prior decision for owner clarification [Claude Code]

Owner sent two screenshots from real Telegram testing:
1. An English-language user got an all-English confirmation message but
   the button below it still said "ثبت مشارکت" in Persian.
2. After tapping "✅ انجام دادم" (done), the confirmation still showed
   "📖 نمایش محتوای سهم"/"✅ انجام دادم" buttons — for a portion that was
   already just marked done.

**Both are real, now fixed** — see CHANGELOG.md for the exact code
locations (`contribute_keyboard`/`commitment_quantity_keyboard` needed a
`lang` param; `portion_done_keyboard` was wrongly reused post-completion,
split into a separate `post_completion_keyboard`). Also fixed, found while
reading the owner's exact quoted phrase: `start.py`'s commitment
join-consent prompt still said "اگر نتوانم، زودتر اطلاع می‌دهم" — leftover
wording from the removed backup-reader mechanism (BACKLOG.md §15) — missed
in the earlier stale-copy sweep; reworded to the responsibility framing
from BACKLOG.md §14.

**Contradiction flagged, owner confirmed the reversal — implemented.** The
owner was asked directly (AskUserQuestion) whether they wanted to keep
"nobody gets notified on a miss" (today's earlier decision) or reverse it
so the creator learns about a member who's been missing their portion.
They chose: **notify the creator.** Implemented narrowly — only the
creator-facing half is restored, nothing else:
- `reminder_engine.service._maybe_record_miss_and_notify_creator` — once
  a day, if a portion is still incomplete past `daily_deadline_hour`,
  records a miss (reusing the pre-existing `NotificationKind.FOLLOW_UP` +
  `Khatm.miss_notice_threshold`/`miss_notice_window_days`, both already in
  the schema, no migration needed) and, once the threshold is reached,
  sends the **creator only** a message naming the member and the miss
  count.
- **Explicitly still removed, not brought back:** the participant is
  never notified of their own miss; their portion is never released to
  anyone else (no `release_portion` call); no emergency-pool/backup-reader
  claim UI; `/khatm_decision` remains a stub (the creator is only
  informed, not offered an automatic reassignment action — they're pointed
  at "👥 اعضا" in ختم management or contacting the member directly).
- `/khatm_attention` (my_khatms.py) — already existed, previously always
  reported empty since nothing logged `FOLLOW_UP` anymore — now correctly
  shows real data again, with no code changes needed there.
- New real-Postgres test `tests/test_creator_miss_notice_integration.py`:
  confirms the creator is *not* notified below threshold, *is* notified
  once threshold is reached, and the member is never in the notified set.

**Still not built (asked about, not yet scoped):** asking every committed
participant their delivery hour at join time (mirroring the open-Quran
wizard so nobody has to know about the hidden `/reminder` command), and
auto-pushing portion content alongside the daily reminder instead of
requiring a manual "show content" tap.

**Verified:** full `pytest` (63) + real-Postgres integration (134 total)
pass; bot restarted, `/health` OK. Also confirmed (no code change): the
support team's reverse-proxy setup is a server-side/DNS matter outside
this codebase — nothing in the bot needs updating on this side for it;
once the domain resolves to the server and files are uploaded, the
existing `PAYPING_CALLBACK_URL`/`admin_web_base_url` env vars just need to
be set to the real HTTPS domain (already documented in an earlier
session's support-ticket guidance).

## Current state — 2026-09-21 — Open/waitlisted Quran readers now actually receive real page content (BACKLOG.md §24) [Claude Code]

Owner reported: for OPEN Quran khatms (and waitlisted, non-committed
members of a COMMITMENT Quran khatm — DEC-PY-0010), logging a contribution
never actually sent any Quran page content — it was purely a bare number
counter, identical to how Salawat open logging works. Owner wants: on
first use, ask how many pages/day the reader wants and what hour to send
them, then auto-send that many real pages every day; manual "extra"
logging should also actually deliver the corresponding pages.

**Root cause confirmed via investigation before coding:** `open_contribution`
module only ever stored a plain `amount` — no page range, no schedule.
Real Quran page delivery (`content_service.resolve_current_quran_delivery`)
only ever ran off an assigned `KhatmPortion`, which only exists for
COMMITMENT participants. An OPEN/waitlisted participant has no portion, so
they never got content — confirmed with a full trace, no guessing.

**Built:**
- 3 new columns on `Participation` (migration `r9s0t1u2v3w4`):
  `open_reading_pages_per_day`, `open_reading_next_page` (1-based cursor,
  default 1), `open_reading_last_sent_at`.
- New repository/service functions in `modules/participation/` to set the
  plan, advance the cursor by N pages (returning the reserved range), and
  mark "sent now".
- New `content_service.get_quran_total_pages(khatm)` — OPEN Quran khatms
  already store the edition's total in `repetition_target` at creation;
  COMMITMENT ones don't, so this falls back to the edition's own page
  count (`QURAN_EDITIONS`).
- `bot/handlers/portions.py`: the first time a non-committed Quran
  participant taps "➕ ثبت مشارکت", a new 2-step FSM
  (`SetupOpenQuranReading`) asks pages/day then delivery hour (stored via
  the existing `NotificationPreference.reminder_hour`, same mechanism as
  `/reminder` — but `/reminder` itself explicitly filters to committed
  participants only, so this needed its own ask rather than reusing that
  command), then immediately delivers the first day's real pages. Once
  set up, subsequent manual "ثبت مشارکت" logging (`receive_contribution_amount`)
  also now actually delivers the corresponding page range (capped to what's
  left in the edition) via the new shared `_deliver_quran_pages` helper,
  instead of only logging a number.
- New `reminder_engine.service.deliver_due_open_quran_reading`, wired into
  the existing 30-minute scan: for each configured reader, once a full
  local day has passed since their last send **and** the local clock
  matches their chosen hour, delivers that day's page batch and advances
  the cursor. Stops cleanly once the reader reaches the edition's last
  page.
- New `bot/notify_adapter.py::build_send_quran_pages_fn` — the reminder
  engine is deliberately platform-agnostic and has no `Bot` instance
  access (see its own docstring), so actual photo/audio sending for the
  auto-send path is built in `notify_adapter.py` (which already owns the
  real `Bot` instances) and passed in as a callback, mirroring the
  existing `notify` pattern.
- New real-Postgres integration test
  `tests/test_open_quran_reading_integration.py`: proves the auto-send
  fires exactly once per local day at the chosen hour, not twice on the
  same day, delivers the next batch correctly the following day, and
  stops once the reader reaches the edition's page limit.

**Verified:** full `pytest` (63) + real-Postgres integration
(`RUN_INTEGRATION_TESTS=1`, 134 total, including the new test) pass;
`alembic upgrade head` applied the new migration cleanly against the real
local Postgres; import smoke-test passes; bot restarted cleanly, `/health`
returns `{"status":"ok","database":"ok"}`.

**Also answered (no code change):** a status question about whether the
local admin web panel is reachable — yes, `http://localhost:8000` serves
it, but logging in requires a real signed Telegram Mini App request over
HTTPS, which isn't wired up in this local/pre-deployment environment yet
(expected, not a bug — see `admin_web_login`'s existing HTTPS guard).

## Current state — 2026-09-21 — "ختم‌های من" made hierarchical (BACKLOG.md §18); my_khatms.py creator commands fully translated + tone-guide pass (§19/§3 leftover); a real NameError bug fixed [Claude Code]

Owner asked for two things: (1) BACKLOG.md §18 — the hierarchical redesign
of "my khatms" — and (2) translating `my_khatms.py`'s creator typed
commands (`/khatm_members`, `/khatm_stats`, ...) and the advanced `cs:*`
settings tree, which had been the one explicitly-flagged leftover from the
earlier full-bot i18n pass (BACKLOG.md §3). Also answered a status
question about the local admin panel (it's running on :8000, but its
login requires a real Telegram Mini App signature over HTTPS, which isn't
wired up locally — expected, not a bug).

**"ختم‌های من" hierarchical redesign, done and tested.** Three levels,
exactly as requested: (1) top branches — created / joined / finished, each
with a count; (2) inside each branch, content-type categories — Quran /
Salawat / Dua / La'an (only categories that actually have something show
up); (3) the individual khatms with their existing action buttons
(manage/contribute/pause/resume/leave). No FSM state is kept — every
navigation tap (`mk:root`/`mk:b:<branch>`/`mk:c:<branch>:<category>`)
re-reads fresh from the DB and edits the same message in place, so the
view never goes stale and doesn't spam new messages. New functions in
`bot/handlers/my_khatms.py`: `_content_group` (categorizes a khatm using
`template_type`/`KhatmCategory.group`), `_build_my_khatms_tree`, and three
`_render_my_khatms_*` functions. New real-Postgres test
`tests/test_my_khatms_hierarchy_integration.py` — creates a Quran khatm, a
plain Salawat khatm, and a Dua khatm (via a real `KhatmCategory` row),
joins a second user to two of them, and checks every item lands in the
right branch/category for both the creator and the member.

**`my_khatms.py`'s creator-facing surface fully translated (fa/ar/en) and
tone-guide-reviewed.** ~90 new `my_khatms.creator.*` i18n keys cover every
typed command (`/khatm_members`, `/khatm_member`, `/khatm_attention`,
`/khatm_export`, `/khatm_stats`, `/khatm_qr`, `/khatm_content_mode`,
`/khatm_pause`, `/khatm_snooze`, `/khatm_end_at`, `/khatm_schedule`,
`/khatm_edit_title`, `/khatm_edit_welcome`, `/khatm_cover`,
`/creator_app`) and the entire `cs:*` inline settings tree (menu, content
mode, schedule, cosmetic edits, pause/snooze toggles) plus khatm
cancellation. Applied `docs/ai/TONE_GUIDE_80YO_PERSONA.md`'s 9-point
checklist while writing these: shorter sentences, no unexplained jargon,
no blame in error text ("این مقدار قابل ذخیره نیست" framed around the
problem, not the user).

**Two real, pre-existing bugs found and fixed while doing this translation
pass (not part of the ask, found by necessity while touching every line):**
1. `khatm_stats` referenced an undefined `callback` variable in its
   phone-not-verified branch — this handler only ever receives a
   `Message` (both as a direct `/khatm_stats` command and via
   `creator_report_callback`'s forwarding, which passes `callback.message`
   as the `message` argument, never a real callback). Any creator with an
   unverified phone hitting `/khatm_stats` would have gotten a raw
   `NameError` instead of the intended guidance message. Fixed by using
   `message.answer` directly.
2. `/khatm_skip_today` and `/khatm_miss_policy` — two typed commands that
   configured the "امروز نمی‌رسم" button and the miss-notice threshold,
   both removed from the UI entirely in the emergency-portion-removal pass
   earlier today — were still present as reachable typed commands that
   silently did nothing useful anymore. Removed outright rather than
   translated, since translating a command that can no longer have any
   visible effect would be actively misleading. (Their underlying
   `khatm_service.set_allow_skip_today`/`set_miss_notice_policy` functions
   and `bot/keyboards.py::creator_miss_policy_keyboard` were left alone —
   still exercised directly by `tests/test_skip_today_setting_integration.py`
   and `tests/test_miss_notice_policy_integration.py`, harmless as unused
   library code.)

**BACKLOG.md §19 (persona tone rewrite) — genuinely started, not claimed
as finished.** Beyond `my_khatms.py` above, also reviewed and fixed
`welcome.text` (already compliant) and the two stale
emergency-portion-era strings from earlier today
(`create_khatm.mode_explanation.quran`, `join.preview.mode_commitment_quran`).
Explicitly **not** done: a full line-by-line pass over the remaining
~1500 i18n keys (registration/profile/help/create_khatm wizard/settings/
reminders) that already got an earlier "super-simple tone" pass
(BACKLOG.md §3, 2026-09-19/20) — that overlaps significantly with this
checklist but isn't identical, and doing a wholesale rewrite of already-
tested, already-shipped strings without a specific complaint risks
introducing regressions for no concrete benefit. Recommended approach
going forward: apply the checklist to any string as it's touched anyway
(as done here), plus fix on report rather than rewrite everything
speculatively.

**Verified:** full `pytest` (63, one test updated for the new
tone-compliant creator-login copy) + real-Postgres integration
(`RUN_INTEGRATION_TESTS=1`, 133 total) all pass; `alembic upgrade head` is
a no-op; two duplicate-process incidents (both from earlier restarts
today) were found and cleaned up again, bot restarted cleanly each time,
`/health` returns `{"status":"ok","database":"ok"}`.

## Current state — 2026-09-21 — Emergency-portion/backup-reader system fully removed; one-Quran-portion-per-day implemented; stale contradictory copy and dead code cleaned up [Claude Code]

Owner explicitly said (after being asked two clarifying questions):
**"اصلا کلا سهم اضطراری رو وردار اگر کسی نخونه نمیخواد کسی باخبر بشه کلا
قضیه سهم اختیاری رو وردار و چیزای مرتبطش چون باعث گیج شد مخاطبام میشه"** —
remove the entire emergency-portion/backup-reader concept, no one should be
notified if someone misses their portion. Next-portion delivery timing
reuses the existing `/reminder` hour.

**Emergency-portion / backup-reader feature removed end-to-end:**
- `reminder_engine/service.py::_maybe_send_miss_notice` (auto-released a
  missed portion back to a shared pool, notified the participant, and
  conditionally notified the creator with a `/khatm_decision` prompt) —
  deleted entirely, along with its call site.
- `bot/handlers/portions.py`: removed `claim_emergency_portion`
  (`emergency:` callback), `toggle_backup_reader` (`backup_toggle:`
  callback), and `skip_today` (`skip_today:` callback, the "امروز نمی‌رسم"
  button) — all three were different doors into the same now-removed
  shared-pool concept.
- `bot/handlers/my_khatms.py`: removed the `needs_claim`/`backup_targets`
  button rows from `list_my_khatms`.
- `bot/keyboards.py`: removed `emergency_claim_keyboard`,
  `backup_reader_keyboard`, the "امروز نمی‌رسم" row from
  `portion_done_keyboard`, and the skip/miss-threshold rows from
  `creator_settings_keyboard`.
- `bot/handlers/creator_decisions.py::resolve_creator_decision`
  (`/khatm_decision`) reduced to a short "no longer available" stub — the
  whole missed-commitment-decision workflow it managed no longer applies.
- Left untouched (own judgment call, not explicitly confirmed with owner):
  `/khatm_attention` (will now always report empty, since nothing logs
  `NotificationKind.FOLLOW_UP` anymore — harmless-if-inert) and
  `reminder_engine.service.delegate_inactive_portions` (a separate,
  30-day-inactivity fallback, not part of the daily-miss confusion the
  owner flagged).
- Removed ~15 now-dead i18n keys this left behind (`portions.backup_*`,
  `portions.emergency_*`, `portions.no_emergency_portion`,
  `portions.today_skipped`/`no_active_portion_today`,
  `my_khatms.button.claim`/`backup_*`, `my_khatms.backup_status_line` +
  `backup_on`/`backup_off`, `creator_decisions.usage` and 7 other now-
  unreachable `creator_decisions.*` keys) — verified dead via grep before
  removing each.

**One-Quran-portion-per-day implemented:**
- `allocation/service.py::complete_current_portion_and_advance` no longer
  auto-assigns the next portion in the same call — it only completes the
  current one now.
- New `allocation/repository.py::list_latest_completed_without_current_assignment`
  + `allocation/service.py::list_awaiting_next_portion` find participants
  who finished today's portion and have no portion assigned yet.
- New `allocation/service.py::peek_next_open_portion` — read-only pool
  check (does not assign) used only to phrase the completion message
  correctly ("next one arrives tomorrow" vs. "that was your last one").
- New `reminder_engine/service.py::deliver_due_next_portions`, wired into
  the existing 30-minute `run_once()` scan: for each such participant,
  resolves their own timezone + their own `/reminder` hour (same
  resolution pattern as the existing daily-reminder loop, default hour 9),
  and only once a full calendar day has passed *in their own timezone*
  since their last completion **and** the local clock matches their
  reminder hour, assigns the next portion via the existing
  `allocate_next_portion_to` and notifies them.
- `bot/handlers/portions.py::mark_portion_done` updated: since the next
  portion is never available immediately anymore, it now peeks the pool
  (via `peek_next_open_portion`, without assigning) right after completion
  to decide which message to show — "✅ done, next one arrives tomorrow at
  your reminder time" (new key `portions.page_done_next_tomorrow`) if the
  pool still has portions left for this khatm, or the existing "🎉 your
  personal portion is fully complete" message if not.
- New real-Postgres integration test
  `tests/test_one_portion_per_day_integration.py` — proves: completing a
  portion does not immediately hand out the next one; calling the new
  delivery function on the same day delivers nothing; simulating a full
  day passed + local reminder hour reached delivers exactly the next
  portion in sequence.

**Stale/contradictory copy fixed (found while removing the above):** two
existing strings still described the just-removed mechanism as if it were
reassuring ("اگه نتونید، سهمتون به یکی دیگه می‌رسه" — don't worry, someone
else will cover it) — `create_khatm.mode_explanation.quran` (shown in the
creation wizard) and `join.preview.mode_commitment_quran` (shown in the
invite-preview message, BACKLOG.md §13/§14). Since the mechanism they
described no longer exists, and the owner separately asked (§14) for this
kind of copy to convey responsibility instead of false reassurance, both
were rewritten in the same tone-direction: "if you miss a day, the khatm
waits on you and the whole group's progress slows down" — factually
accurate now, and responsibility-framed as requested. All three languages
updated in both keys.

**Duplicate live bot process fixed.** Found two independent
`python -m khatmsaz.bootstrap` processes both polling Telegram
(`@Khatm_Saz_bot`) at once — a real, pre-existing operational bug (every
update would be raced/double-handled), unrelated to this session's code
changes. Both killed and replaced with one clean instance; confirmed via
`Get-CimInstance Win32_Process` that only one logical instance runs now
(a parent/child pair from the Python launcher itself, not two independent
bots — same pattern seen on the previous clean start).

**Verified:** full `pytest` (62) + real-Postgres integration (`RUN_INTEGRATION_TESTS=1`,
70 incl. the new test) all pass, `alembic upgrade head` is a no-op (no
schema changes), import smoke-test passes, bot restarted cleanly and
`/health` returns `{"status":"ok","database":"ok"}`.

**Explicitly NOT done in this pass (flagged, not silently skipped) —**
raised by the owner's "همه چیز آماده اجرا باشه، همه بخش‌ها، بجز درگاه
پرداخت/پلن‌های پولی/پیامک" request for one big pre-launch pass:
- BACKLOG.md §18 (hierarchical "ختم‌های من" redesign) and §19 (persona-
  driven tone rewrite of ~1500+ i18n keys) are each large, separate efforts
  the backlog itself already flagged as needing their own dedicated
  session/design pass, not a rushed pass under launch time pressure.
- `my_khatms.py`'s creator-facing typed commands (`/khatm_members`,
  `/khatm_stats`, `/khatm_export`, ...) and the `cs:*` advanced-settings
  inline tree are still Persian-only (I18N_MIGRATION.md §2 already flagged
  this as needing an explicit owner decision before translating, since
  creators are likely Persian-speaking anyway).
- The web admin panel beyond the creator Mini App panel (i.e.
  `src/khatmsaz/web/templates/*.html` outside `creator_*.html`) is still
  Persian-only/untouched.

## Current state — 2026-09-21 — Quran portion/audio boundary bug fixed (real, wide-reaching); devotional-audio no-code path confirmed already working [Claude Code]

Owner asked whether yesterday's requested changes were done, reported a
real bug (page 7-8 portions getting two audio messages), and asked for a
channel-based no-code content pipeline.

**Real bug found and fixed — much wider than reported.** The Quran
allocation engine chunked pages uniformly as [1-2],[3-4],[5-6],[7-8]...
(`DEFAULT_PAGES_PER_PORTION=2`, starting at page 1), but the real,
verified reciter audio is segmented differently: pages 1-3 in one
recording, then 2-page segments from page 4 onward ([4-5],[6-7],[8-9]...).
Every portion boundary from page 3 onward was offset by one page relative
to the real audio segments, so almost every portion (300 of 302) straddled
two different audio files and sent both — not just the pages-7-8 case the
owner happened to notice. Fixed by adding
`allocation_service.generate_quran_page_plan_from_boundaries` +
`repository.bulk_create_positional_portions_from_boundaries`, and using
them (only for the canonical 604-page `madina-hafs` edition) with
boundaries taken directly from `AUDIO_MESSAGE_RANGES` — portion 1 is now
pages 1-3 (matching the owner's "pages 1&2 count as one" framing), and
every later portion aligns exactly with one audio file. Legacy/no-longer-
creatable editions are untouched.

**Verified thoroughly, both ways:** a real-Postgres script checked all 301
new portion boundaries and confirmed zero portions have more than one
distinct audio file; the same check re-run with the *old* uniform logic
confirmed 300 of 302 portions would have had two different audio refs —
proving this was a real, systemic bug, not a one-off. Also created a real
Quran khatm end-to-end and confirmed a freshly joined member's first
portion is exactly pages 1-3.

**Unrelated incident found and fixed along the way:** `quran_page_assets`
was completely empty (likely the local dev Postgres recovery cluster
loaded an older snapshot after an earlier restart this session) — re-ran
the idempotent seed, fully restored (604 images + 604 audio).

**Two integration tests broken by an earlier change in this session, now
fixed.** `test_creator_web_integration.py` and
`test_creator_pagination_integration.py` failed on teardown ordering
because `_creator()` (changed earlier today to resolve the creator's
language for Mini App i18n) now creates a `UserSettings` row as a side
effect that the tests' manual cleanup didn't anticipate. Fixed both
tests' cleanup order rather than the app code, since the new side effect
is correct/intended.

**Channel-based no-code content pipeline — investigated, already exists.**
Owner wants to add new dua/ziyarat audio (e.g. "Ziyarat Ashura, reciter
so-and-so") without any code deploy. Found this capability already built:
`/admin_devotional_text` registers a new slug's text; forwarding/sending
an audio file with caption `/admin_devotional_audio <slug>` attaches audio
to it — no code needed for either step. (Briefly added a duplicate,
incompatible `register_devotional_audio` function while investigating,
caught and removed immediately in the same pass — the real, working
function was untouched.) Verified with a real-Postgres call that audio
attaches correctly to the `ziyarat-ashura` slug registered earlier today.

**Not done — needs an owner decision, flagged rather than guessed:**
"only one Quran portion per day" (owner wants completing today's portion
to NOT immediately reveal/assign tomorrow's). Confirmed current behavior:
`complete_current_portion_and_advance` still assigns and shows the next
portion immediately, unchanged since Phase 1's "Personal Journey" design.
This is a significant behavioral change to a core, heavily-used subsystem
— asked the owner four precise clarifying questions (see
`docs/ai/BACKLOG.md` §23) before touching it, since guessing wrong could
break the experience for every current committed Quran participant.

Verified throughout: full `pytest` (62 passed, 69 skipped) and full
real-Postgres integration suite (69 passed) after every change, multiple
real-Postgres one-off scripts, import smoke-tests, and a bot restart +
`/health` check after each meaningful change.

Docs updated: `docs/ai/BACKLOG.md` (§21 fixed, §22 investigated/confirmed
existing, §23 new — needs decision), this entry.

## Current state — 2026-09-21 — Devotional content delivery built for Salawat/Dua/La'an khatms; suggestions inbox added [Claude Code]

Owner supplied the full, verbatim Ziyarat Ashura text (Arabic + Persian
translation, "با خط درشت و ترجمه") and asked for real content delivery
during Salawat/Dua/La'an khatms, plus letting creators write their own
La'an/dua text, plus a user-suggestions inbox to admins. All three built:

**1) Ziyarat Ashura + Salawat registered as real devotional content.**
`scripts/register_devotional_content.py` (new, one-off, not part of the
app) transcribes the owner's exact text — every couplet as
`<b>arabic</b>\npersian`, chunked with `\x1e` boundaries between groups of
5 couplets so each stays under Telegram's message limit — and calls
`content_service.register_devotional_text` directly against real Postgres.
Excluded one stray line ("دوره عدل مقدماتی دکتر قلیان") from the owner's
paste that was clearly a website artifact, not part of the ziyarat.
Registered slugs: `ziyarat-ashura` (10,752 chars → 15 messages) and
`salawat` (96 chars → 1 message).

**2) `devotional.py` fixed to actually render bold text.** It was calling
`html.escape()` on `text_body` before sending, which silently defeated any
`<b>` tags even though both bots already run in HTML parse mode — bold
formatting could never have worked before this. Now splits on `\x1e` and
sends each chunk as its own trusted-HTML message (content is admin-curated
via the script, not user input, so escaping is correctly skipped here).

**3) Creator-authored custom recitation text for Salawat-family khatms.**
New optional wizard step (`create_khatm.py`, `entering_recitation_text`,
SALAWAT-template only) lets a creator type up to 3500 characters of their
own dua/la'an text — directly answering "کسی که داره لعن می‌سازه بتونه
متن لعنش رو بنویسه". Stored in the pre-existing, previously-unused
`Khatm.description` column — zero new migration. Threaded through
`workflow_service.create_and_launch_khatm`'s new `description` parameter
(the underlying `khatm_service.create_draft_khatm`/`repository.create`
already supported it).

**4) Delivery wired into the actual portion/contribution flow.**
`portions.py`'s `_send_recitation_content()` runs after every commitment
or open-pool contribution logged on a SALAWAT-template khatm: if the
khatm has creator-authored `description`, send it verbatim (HTML-escaped,
since it's untrusted creator input); otherwise, if the linked category's
title contains "عاشورا", auto-deliver the `ziyarat-ashura` devotional
asset; a category-less plain Salawat khatm gets the `salawat` asset.
**Known limitation, flagged for a proper fix:** matching "عاشورا" by
category title text is a stopgap, not a real link — the correct long-term
design is a `devotional_slug` column on `khatm_categories` (needs a
migration), tracked in `docs/ai/BACKLOG.md` §14.

**5) Suggestions/bug-report inbox.** New `bot/handlers/suggestions.py`:
a "💡 پیشنهاد یا گزارش مشکل" button added to the Help menu
(`help_keyboard`) starts a short FSM that records the text in the
existing `audit_logs` table (action `USER_SUGGESTION`, no new table) and
pushes it live to every `super_admin_telegram_chat_ids` chat via the same
broadcast pattern `manual_phone_verification.py` uses. Registered in
`bootstrap.py`. Updated `tests/test_help.py`'s exact-callback-set
assertion to include the new `suggest:start` button.

Verified throughout: full `pytest` suite (62 passed, 69 skipped) after
every change, a real-Postgres script confirming both the custom-text and
library-fallback delivery paths on real khatms (with cleanup), a real
audit-log write/read check for the suggestions flow, chunk-size
verification for the Ziyarat Ashura content (all 15 chunks ≤ 4000 chars),
import smoke-tests, and a bot restart + `/health` check after each
meaningful change.

Docs updated: `docs/ai/BACKLOG.md` (§14 devotional-content update, new
known-limitation note about `devotional_slug`), this entry.

## Current state — 2026-09-21 — Creator Mini App panel localized; go-live readiness confirmed without payment/SMS [Claude Code]

Two threads this session:

**1) Creator-facing web panel (Telegram Mini App content) localized.**
Owner clarified there is no separate "web app" — `src/khatmsaz/web/` is
exactly the content rendered inside the Telegram Mini App. Scoped the i18n
work the same way `admin.py` was scoped (DEC-PY-0075): only the
**creator**-facing pages (`creator_base.html`, `creator_dashboard.html`,
`creator_khatm_detail.html`, `creator_login.html`) were translated, since
creators are regular end users; the Super-Admin-only pages stay Persian.
Added ~60 new `web.*`/`web.creator.*`/`web.label.*` keys to
`i18n/__init__.py`. Wired `t()` into Jinja2 (`templates.env.globals`,
default `lang="fa"` for unauthenticated pages like the login screen);
`_creator()` now also resolves and returns the creator's `UserSettings.language`,
threaded through `_creator_ctx()`. Added a `_web_label()`/`label()` template
helper for enum-value labels (status, template type, gender, etc.) that is
separate from the untouched Persian-only `_fa_label()` used by admin pages.
Verified by rendering both templates directly (not just importing) for all
three languages via a real Jinja2 render against the actual FastAPI app
router (so `url_for` resolves) — no raw untranslated keys leaked into the
output for fa/ar/en.

**2) Go-live readiness check (owner wants to deploy today).** Owner asked
whether the bot can go live before PayPing/Kavenegar are configured, i.e.
whether people can already create/join khatms. Checked `.env`:
`KHATM_CREATION_PRICE_TOMAN=0` (no wallet charge on creation — payment
code path isn't even invoked), `DEV_OTP=1` (phone verification bypasses
real SMS delivery and shows the code directly in chat), `SMS_PROVIDER=noop`
(safe no-op, no crash on missing Kavenegar key). Confirmed with a real
end-to-end script against Postgres: register → complete profile → verify
phone via dev-OTP → create a free SALAWAT khatm → second user joins via
token → logs a contribution — all succeeded with zero payment/SMS
involvement. **Conclusion: the core flows already work without a real
payment gateway or SMS provider; nothing new needed to be built for this.**

**Operational note:** found the local dev Postgres recovery cluster (port
55433) and the bot process both stopped (this Claude Code session/app was
interrupted mid-task). Restarted Postgres (`pg_ctl start`), ran
`alembic upgrade head` (no pending migrations), and restarted the bot
process (`python -m khatmsaz.bootstrap` in the background); confirmed
`/health` → `{"status":"ok","database":"ok"}` and live Telegram polling
in the log. This is purely local-dev-environment upkeep — unrelated to
the production server the owner is provisioning separately.

**Not done, deliberately, given the "no invented content" rule:** the
owner asked for Salawat text+image and Ziyarat Ashura text+image to be
sent during those khatms. Investigated and found **no delivery pipeline
exists at all for non-Quran content** — `devotional_assets`/`/devotional
<slug>` is a manually-invoked standalone lookup command, not wired into
any khatm/portion flow. Building that wiring is a real feature, not a
same-day fix, and Ziyarat Ashura's exact canonical wording must come from
the owner or a verified source — it will not be reproduced from memory
given how sensitive an exact-text error would be. Flagged to owner
directly in chat as a fast-follow, not a launch blocker (existing
quantity-only behavior for Salawat/Dua/Laan khatms is unaffected and
still fully functional for launch).

Verified: full `pytest` suite (62 passed, 69 skipped) after all changes,
a real-Postgres end-to-end smoke script (with full cleanup), a direct
Jinja2 render check for the creator templates in fa/ar/en, bot restart,
and `/health` check.

Docs updated: `i18n/__init__.py` (`web.*` block), this entry. `docs/ai/I18N_MIGRATION.md`
still needs a short "§4 web panel" checklist entry noting creator pages
done / admin pages intentionally skipped — pending next doc pass.

## Current state — 2026-09-20 — Two real bugs fixed (language menu, reciter list); Quran-content bug investigated and found to be stale test data [Claude Code]

Owner asked to fix "the bugs" from the backlog and gave a standing
instruction to do web research for future requests. Fixed the two items
that were genuine, unambiguous bugs (not product decisions):

**§16 — language change didn't update the bottom Reply Keyboard.**
`settings_menu.py::set_language` now sends one extra short confirmation
message with `reply_markup=main_menu_keyboard(new_lang)` right after
editing the inline settings screen, so the persistent bottom menu updates
immediately instead of waiting for some unrelated later action.

**§17 — reciter picker offered 4 reciters but only Parhizgar has real
audio.** Added `RECITERS_WITH_REGISTERED_AUDIO = ("parhizgar",)` to
`content/service.py`; `list_reciters()` (the only function that builds the
user-facing picker) now reads from that instead of the full
`SYSTEM_RECITERS` dict. Deliberately left `SYSTEM_RECITERS` itself
untouched — it's still the full technical whitelist, and the existing
integration tests (`test_reciter_policy_integration.py`,
`test_quran_delivery_integration.py`) that exercise husary/minshawi/
abdulbasit fallback logic still pass unchanged. Adding a reciter later
is a one-line change once its audio is actually imported.

**§20 — investigated, found to be stale test data, not a code bug.** A
real-Postgres script confirmed all 604 pages (image + audio) are correctly
seeded under `edition_id='madina-hafs'`, and `resolve_complete_quran_page_assets`
correctly resolves pages 1-2 and 5-6 for that edition. The actual cause:
most existing test khatms in the database were created with the old
`iran-pocket` edition (286 pages) from before the creation wizard was
restricted to only the 604-page `madina-hafs` edition — and the page-asset
library was only ever seeded for `madina-hafs`. Those old khatms
structurally cannot have content; this isn't fixable in code. Recommended
the owner retest with a freshly created khatm (which now always uses
`madina-hafs`) rather than an old `iran-pocket` test khatm; flagged that
"fixing" the old khatms would itself require a real product decision
(re-seed a second library for `iran-pocket`, or reassign `quran_edition_id`
on active khatms — risky since page counts differ and portions are already
assigned).

Verified: full `pytest` suite (62 passed, 69 skipped) **and** the full
integration suite against real Postgres (`RUN_INTEGRATION_TESTS=1` — 69
passed, 62 deselected, ~2.5 minutes), an import smoke-test, a one-off
script confirming `list_reciters()` now returns only Parhizgar, a bot
restart, and `/health` → `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/BACKLOG.md` (§16, §17 marked done; §20 updated
with investigation findings and a recommendation, not marked done since
it needs an owner confirmation), this entry.

**Standing instruction recorded:** the owner asked to be given web
research for future requests where relevant (in addition to code work) —
see the `TONE_GUIDE_80YO_PERSONA.md` research from the prior entry as the
first example of this pattern.

## Current state — 2026-09-20 — Owner requested a status report + 6 new backlog items (no code changed this entry) [Claude Code]

Owner explicitly asked for a project status report (not more code) plus
six new items added to the backlog. No source files were touched in this
entry — only `docs/ai/BACKLOG.md` (§14–§18 added).

New backlog items, each requiring an owner decision before implementation
(per CLAUDE.md — no guessing product rules):
- §14: khatm/invite descriptions should show the actual goal/target and
  use a motivating, "your inaction can hurt the group" tone instead of
  reassuring users their portion is safely handed to someone else —
  conflicts with the existing DEC-PY-0009 mechanic, needs resolution.
- §15: "امروز نمی‌رسم" (skip today) should stop freely releasing the
  portion and instead push it to some "makeup list" — a significant
  behavioral change in direct tension with DEC-PY-0009's backup-reader
  pool design; flagged, not touched.
- §16: real bug found (diagnosed only, not fixed) — changing language via
  the settings menu updates the inline settings message but not the
  persistent bottom Reply Keyboard, because that keyboard only refreshes
  when a *new* message is sent with `reply_markup=main_menu_keyboard(lang)`.
  Fix is well-understood, just needs a go-ahead.
- §17: `SYSTEM_RECITERS` in `content/service.py` lists 4 reciters but only
  Parhizgar has real registered audio; needs an owner decision on whether
  to delete the other three or grey them out as "coming soon".
- §18: `list_my_khatms` needs a full UX redesign into a drill-down menu
  (created/joined/completed → content family → khatm list), not a long
  text dump — a substantial, separate piece of work.

Gave the owner a plain-language project status report covering ROADMAP.md
phase-by-phase completion and an overall percentage estimate (see chat —
not duplicated here since PROJECT_STATE.md tracks changes, not
conversation summaries).

Added a 7th item (§19) right after: a comprehensive literary/psychology
tone-research task, framed as "put yourself in the shoes of an 80-year-old
first-time bot user" and review every user-facing string (welcome message,
button labels, portion-completion messages, errors, help text — i.e. the
whole `src/khatmsaz/i18n/__init__.py` registry built up this session)
through that lens. Explicitly a separate, content-focused research task,
not a code task — recommended to produce a written tone-guide before
touching any actual strings, so changes are judged against a documented
standard rather than one-off taste. Not started; no strings changed.

## Current state — 2026-09-20 — Three owner-reported UX bugs fixed: message burst, province keyboard, join-invite text [Claude Code]

Owner reported three concrete UX problems directly (not part of the i18n
work) and asked them added to the task list and fixed. All three done:

**1. "ختم‌های من" message burst.** `list_my_khatms` in
`src/khatmsaz/bot/handlers/my_khatms.py` used to send one separate
message per khatm/action (creator management, contribute, emergency
claim, pause/resume, backup-reader toggle) — annoying with several
khatms. Now everything is combined into **one** inline keyboard attached
to the single summary message; creator management (which has too many
sub-actions — members, attention, CSV, stats, QR, completion toggle,
settings, cancel — to fit one row) gets a single "🛠 Manage «title»"
opener button that sends the existing full settings keyboard as one
follow-up message only when actually tapped, via a new
`my_khatms:manage:<khatm_id>` callback. Verified with a real-Postgres
script creating 2 khatms for one user: before the fix this would have
sent 3 messages, after the fix exactly 1 message with a combined
2-button keyboard.

**2. Province picker too tall.** The 31-province + "outside Iran"
selection keyboard (duplicated in `registration.py` and `profile.py`)
put one button per row (32 rows). Changed both to pair two provinces per
row (16 paired rows + 1 single row), roughly halving the scroll height.
City remains free text per DEC-PY-0015 — unaffected. Verified: both
keyboards produce paired rows via a direct check.

**3. Join-invite preview text didn't explain the khatm.**
`build_join_preview_message` in `src/khatmsaz/bot/handlers/start.py` —
shown when someone opens an invite link, before joining — only showed
title/creator/niyyat/member-count; it never said what *kind* of khatm it
is or what committing to it means. Added two new lines: a **content-type
line** (Quran page-by-page / Salawat / Dua-or-Ziyarat with the real
category title / La'an with the real category title — resolved from
`content_category_id`, never guessed) and a **mode line with a concrete
explanation** (Quran commitment explains the daily-portion mechanic;
Salawat/Dua/La'an commitment states the *actual* pledged quantity from
`khatm.repetition_target`, e.g. "you pledge to complete 100 Salawat";
open mode gets its own explanation). Both new lines are fully localized
(fa/ar/en) using the viewer's own stored language. No existing test
broke (`test_welcome_text.py`'s exact-substring assertions still pass
since `title`/`creator`/`member_count`/CTA wording was preserved).

Added 3 new numbered items to `docs/ai/BACKLOG.md` (§11, §12, §13) per
the owner's explicit request to record these, each marked done with
implementation notes.

Verified across all three: full `pytest` suite (62 passed, 69 skipped),
real-Postgres one-off scripts (burst test with actual khatm creation +
cleanup; province-keyboard row-pairing check; join-preview text for 3
real (template×mode) combinations across all 3 languages), an import
smoke-test, a bot restart, and `/health` → `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/BACKLOG.md` (§11–13), this entry.

## Current state — 2026-09-20 — Owner resolved 3 remaining i18n scope questions; legacy settings commands fully localized [Claude Code]

Asked the project owner the three open i18n-scope questions left after
finishing every normal-priority bot-handler file. Answers (recorded as
`DEC-PY-0075`):
1. `admin.py` / `/admin_*` commands: **stay Persian-only forever** — no
   translation needed, admins always work in Persian.
2. Admin web panel (`src/khatmsaz/web/templates/*.html`): **needs
   multi-language support** — not started yet, flagged as a separate,
   architecturally distinct task (needs a Jinja2-side `t()` equivalent and
   a decision on where admin-web language preference is stored — cookie?
   querystring? — before any template gets touched).
3. Legacy typed-command settings files: **owner wants them fully
   translated too**, despite being lower priority than the button-driven
   `settings_menu.py` flows that replaced them.

Acted on decision 3 immediately: converted all seven legacy files —
`digest_settings.py`, `font_settings.py`, `language_settings.py`,
`reciter_settings.py`, `reminder_settings.py`, `sms_settings.py`,
`timezone_settings.py` — to `t(key, lang)`. Added 28 new keys total across
all seven. Each file resolves the user's language via
`settings_service.get_or_create` (no FSM state needed — these are all
single-message typed commands).

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off script checking all 28 keys across fa/ar/en plus an import
smoke-test for all seven modules, bot restart, `/health` →
`{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/DECISIONS.md` (`DEC-PY-0075`), `docs/ai/I18N_MIGRATION.md`
(all seven legacy files + `admin.py` now `[x]`; added §3 with the admin-web
architecture questions for whoever starts that task), this entry.

**This closes the bot-side i18n rollout entirely** — the last remaining
i18n work is the admin web panel, a distinct, not-yet-started task.

## Current state — 2026-09-20 — devotional.py localized; normal-priority i18n checklist complete [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/devotional.py`
(`/devotional <slug>` dua/ziyarat library delivery) to `t(key, lang)`;
added 4 new keys.

Also reviewed `broadcast.py` (next item on the checklist) and made a
deliberate no-change decision: the entire file is either creator/admin
typed commands, or the actual broadcast text itself — which is free-form
content written by the khatm's creator and therefore cannot be
auto-translated (there's no way to guess what a human wrote). No
templated system message to a third party exists there needing a
translation key, so it's marked `[x]` reviewed with a note rather than
`[ ]` left dangling.

**This closes every file in `I18N_MIGRATION.md`'s "normal priority"
checklist** (`start.py` welcome/join-success parts, `registration.py`,
`profile.py`, `help.py`, `create_khatm.py`, `settings_menu.py`,
`my_khatms.py` [partial, by design], `portions.py`, `report.py`,
`leave.py`, `join_requests.py`, `wallet.py`, `change_phone.py`,
`account_link.py`, `account.py`, `creator_decisions.py`,
`khatm_request.py`, `public_khatms.py`, `manual_phone_verification.py`,
`broadcast.py`, `devotional.py`).

Remaining in `I18N_MIGRATION.md`: the low-priority legacy typed-command
settings files (`digest_settings.py`, `font_settings.py`,
`language_settings.py`, `reciter_settings.py`, `reminder_settings.py`,
`sms_settings.py`, `timezone_settings.py` — all superseded by
`settings_menu.py`'s button tree), `admin.py` (needs an owner decision on
whether admin tooling needs translation at all), and the admin web panel
HTML templates (needs an owner decision on whether that surface needs
translation too — not yet asked).

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key check plus an import smoke-test, bot restart, `/health` →
`{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`devotional.py` and
`broadcast.py` now `[x]`), this entry.

Next: the low-priority legacy settings command files, or ask the owner
about `admin.py` / the web panel before spending more effort there.

## Current state — 2026-09-20 — manual_phone_verification.py: requester notification localized [Claude Code]

Continuing the i18n rollout. `src/khatmsaz/bot/handlers/manual_phone_verification.py`
is almost entirely an admin review UI (list pending foreign-number
requests, approve/reject buttons) — kept Persian, same treatment as
`admin.py`. Localized only the 2 messages that actually reach the
end-user requester after a decision (`manual_phone_verification.approved_notice`
/ `.rejected_notice`), resolved in the requester's own stored language.

Verified: full `pytest` suite (62 passed, 69 skipped), an import
smoke-test plus direct key checks for both new strings on all three
languages, bot restart, `/health` → `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`manual_phone_verification.py`
now `[x]`, with the admin-UI-stays-Persian note), this entry.

Next unchecked file: `broadcast.py`.

## Current state — 2026-09-20 — public_khatms.py fully localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/public_khatms.py`
(`/public_khatms` discovery list + join flow) to `t(key, lang)`; added 4
new keys. Small, single-recipient file.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key check plus an import smoke-test, bot restart, `/health` →
`{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`public_khatms.py` now `[x]`),
this entry.

Next unchecked file: `manual_phone_verification.py`.

## Current state — 2026-09-20 — khatm_request.py localized (submitter side + notifications) [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/khatm_request.py`
to `t(key, lang)`; added 11 new keys. Split treatment, consistent with the
project's pattern for admin-adjacent files: the submitter-facing part
(`/request_khatm`, the description/attachment FSM flow) is fully
localized with `lang` carried via `state.update_data`; the admin-only
typed commands (`/admin_requests`, `/admin_approve_request`,
`/admin_reject_request`) keep their Persian text, same as `admin.py` —
but the approve/reject notification sent back to the requester is always
built in *the requester's own* stored language, resolved separately from
the admin's.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check plus an import smoke-test, bot restart, `/health`
→ `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`khatm_request.py` now `[x]`),
this entry.

Next unchecked file: `public_khatms.py`.

## Current state — 2026-09-20 — creator_decisions.py fully localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/creator_decisions.py`
(`/khatm_decision` — creator resolution for repeated missed Quran
commitments) to `t(key, lang)`; added 11 new keys. Even though the typed
command itself is creator-only tooling (similar in spirit to the commands
left untranslated in `my_khatms.py`), this file also notifies a *third
party* — the waitlisted member who gets promoted — so it was fully
localized rather than skipped, per the same reasoning applied to
`leave.py` and `join_requests.py`.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check plus an import smoke-test, bot restart, `/health`
→ `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`creator_decisions.py` now
`[x]`), this entry.

Next unchecked file: `khatm_request.py`.

## Current state — 2026-09-20 — account.py fully localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/account.py`
(the `/delete_account` confirm/cancel flow and its blocked-deletion
explanation) to `t(key, lang)`; added 11 new `account.*` keys. Small,
single-recipient file, no FSM state.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check plus an import smoke-test, bot restart, `/health`
→ `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`account.py` now `[x]`), this
entry.

Next unchecked file: `creator_decisions.py`.

## Current state — 2026-09-20 — account_link.py fully localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/account_link.py`
(self-service OTP flow for linking a new chat/platform to an existing
account) to `t(key, lang)`; added 11 new `account_link.*` keys including
the real OTP SMS text. Language is resolved from the *source* account (the
chat currently running `/link_account`), not the target account being
linked to, and carried via `state.update_data(lang=...)` through the flow.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check plus an import smoke-test, bot restart, `/health`
→ `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`account_link.py` now `[x]`),
this entry.

Next unchecked file: `account.py`.

## Current state — 2026-09-20 — change_phone.py fully localized (incl. OTP SMS text) [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/change_phone.py`
— creator phone verification and self-service phone change, both flows
sharing the OTP-code state machine — to `t(key, lang)`. Added 22 new
`change_phone.*` keys. Notably, this includes the **actual SMS text sent
to the user's phone** via Kavenegar (`change_phone.otp_sms_text` /
`change_phone.otp_sms_text_change`), not just in-bot chat messages — the
first file this session where a real outbound SMS payload is localized.

Language carried via `state.update_data(lang=...)` across the multi-step
OTP flow (phone entry → code entry), same pattern as `create_khatm.py`.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check plus an import smoke-test, bot restart, `/health`
→ `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`change_phone.py` now `[x]`),
this entry.

Next unchecked file: `account_link.py`.

## Current state — 2026-09-20 — wallet.py fully localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/wallet.py`
(balance overview, invoice history, PayPing top-up flow) to `t(key, lang)`;
added 21 new `wallet.*` keys. Straightforward single-recipient file, no FSM
state, language resolved once per handler.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check plus an import smoke-test, bot restart, `/health`
→ `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`wallet.py` now `[x]`), this
entry.

Next unchecked file: `change_phone.py`.

## Current state — 2026-09-20 — join_requests.py localized + shared join-success message localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/join_requests.py`
(private-khatm membership approve/reject) to `t(key, lang)`, using the same
per-recipient pattern introduced for `leave.py` (creator and requester each
see their own language). Added 10 new `join_requests.*` keys.

Also localized `build_join_success_message()` in
`src/khatmsaz/bot/handlers/start.py` — the shared function that builds the
"🌱 welcome, you joined «title»" message, used both by the direct
`/start join_<token>` flow and by this file's approval flow. Added a `lang`
parameter (default `"fa"`) and 9 new `join.*` keys, since this function is
called directly by `join_requests.py` and needed to be in the requester's
language for the approval-notification path to be correct. Updated its one
other call site in `start.py::resume_join_after_registration` to resolve
and pass the joining user's own language.

**Scope note:** only `build_join_success_message` and its call site were
converted in `start.py` — the rest of that file (invalid/expired invite
link errors, "already a member", "khatm no longer active", the initial
welcome-message wizard) is still Persian-only and remains a separate,
larger task on the checklist.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off script confirming all 19 new keys (`join.*` + `join_requests.*`)
format cleanly on all three languages plus an import smoke-test of both
modified files, bot restart, `/health` → `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`join_requests.py` now `[x]`,
with the `start.py` scope note), this entry.

Next unchecked file: `wallet.py`.

## Current state — 2026-09-20 — leave.py fully localized (per-recipient language) [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/leave.py`
to `t(key, lang)`; added 14 new `leave.*` keys. This file is the first one
this session where a single flow sends messages to **multiple different
people** — the requester, the khatm creator, and (on promotion) the next
waitlisted member — and they can each have a different stored language.
Previous conversions this session only ever needed one `lang` per flow;
here each recipient's message is built with their own language via a new
`_lang_for_user(session, user_id)` helper, called separately for the
requester, the creator, and the promoted participant.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check, bot restart, `/health` → `{"status":"ok",...}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`leave.py` now `[x]`, with a note
about the per-recipient pattern for future files that also fan out
notifications — `join_requests.py` is next and will need the same
treatment), this entry.

Next unchecked file: `join_requests.py`.

## Current state — 2026-09-20 — report.py fully localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/report.py`
(the "📅 امروز" today-overview and "📊 گزارش من" personal report) to
`t(key, lang)`; added 11 new `report.*` keys. Small, straightforward file —
no FSM state, language resolved once per handler via `settings_service`.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off key/format check, bot restart, `/health` → `{"status":"ok",...}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`report.py` now `[x]`), this
entry.

Next unchecked file: `leave.py`.

## Current state — 2026-09-20 — portions.py fully localized [Claude Code]

Continuing the i18n rollout. Converted `src/khatmsaz/bot/handlers/portions.py`
— the daily portion-completion flow, open/commitment contribution logging,
today-vs-yesterday, pause/resume/snooze, emergency-portion claiming, and the
friend-invite line — to `t(key, lang)`. Added 60 new keys under
`portions.*`. This is one of the most frequently seen surfaces in the whole
bot (every "✅ page read" / "✅ N Salawat logged" message goes through here),
so it was a high-priority conversion.

Two lang-resolution patterns used depending on handler shape: plain
callback handlers with no multi-step state use a `_lang_for(chat_id, bot)`
helper (same pattern as `settings_menu.py`); the three FSM flows that span
multiple messages (`LogContribution`, `PauseCommitment`, `CustomSnooze`)
resolve the user's language once when the flow starts and store it in
`state.update_data(lang=...)`, so the follow-up message handler doesn't
re-query the database (same pattern as `create_khatm.py`).

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off script confirming all 60 new keys have fa/ar/en entries and that
every format string used in the handler (page ranges, pledge progress,
today/yesterday totals, pause days, invite URLs) formats cleanly on all
three languages, bot restart, `/health` → `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`portions.py` now `[x]`), this
entry.

Next unchecked file: `report.py`.

## Current state — 2026-09-20 — my_khatms.py member-facing entry localized + real bug fixed [Claude Code]

Continuing the i18n rollout. `src/khatmsaz/bot/handlers/my_khatms.py` is a
huge (1300+ line) file mixing member-facing UI with dozens of creator-only
typed power commands (`/khatm_stats`, `/khatm_export`, `/khatm_qr`, etc.)
and an inline creator-settings tree (`cs:*`). Localized only the
member-facing entry point — `list_my_khatms` (the "🕋 ختم‌های من" button)
and its immediate follow-up messages (group progress, open-contribution
invite, emergency-portion claim, pause/resume commitment, backup-reader
status) — 21 new `my_khatms.*` keys. Left the creator typed commands and
`cs:*` inline tree in Persian, same reasoning as `admin.py`: these are
power-user/creator tooling that likely doesn't need translation, and
should get an explicit owner decision before spending effort on it.
Marked `[~]` (partial) rather than `[x]` in the checklist to be honest
about scope.

**Found and fixed a real, pre-existing bug while doing this:** a block of
message-sending loops (open-contribution invites, emergency-claim prompts,
pause/resume buttons, backup-reader status) was misplaced inside
`confirm_cancel_khatm` (the khatm-cancellation confirmation handler),
referencing undefined names (`message`, `open_targets`, `needs_claim`,
`pause_targets`, `backup_targets`) that don't exist in that function's
scope — every time a creator confirmed cancelling a khatm, this would have
raised `NameError` after the cancellation and refund message. The correct
logic already existed properly inside `list_my_khatms`; this was dead,
broken duplicate code. Removed it.

Verified: full `pytest` suite (62 passed, 69 skipped — the removed
dead-code block wasn't covered by any test, which is why it went
unnoticed), a real-Postgres one-off key/format check for all 21 new keys,
bot restart, `/health` → `{"status":"ok","database":"ok"}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`my_khatms.py` marked `[~]` with
scope notes), this entry.

Next unchecked file: `portions.py`.

## Current state — 2026-09-20 — Settings menu fully localized [Claude Code]

Continuing the i18n rollout (Codex has stopped this session). Converted
`src/khatmsaz/bot/handlers/settings_menu.py` — the button-driven settings
tree — to `t(key, lang)`. Added 49 new `settings.*` keys to
`src/khatmsaz/i18n/__init__.py` covering the home screen, language/font/
reciter/content/reminder/digest/SMS/timezone submenus, and every inline
button label used by their keyboards.

Unlike `create_khatm.py`, this router has no FSM state to carry `lang`
across steps (each screen is a fresh callback), so language is read fresh
from `UserSettings.language` on every screen via a small `_lang_for(chat_id,
bot)` helper — one extra DB read per settings tap, acceptable since this
isn't a hot path. Updated the corresponding keyboard builders in
`bot/keyboards.py` (`settings_home_keyboard`, `settings_language_keyboard`,
`settings_font_keyboard`, `settings_reciter_keyboard`,
`settings_content_keyboard`, `settings_reminder_keyboard`,
`settings_on_off_keyboard`, `sms_subscription_keyboard`,
`settings_timezone_keyboard`, `settings_back_row`) to accept an optional
`lang: str = "fa"` parameter — the `"fa"` default keeps
`tests/test_help.py`'s existing `settings_home_keyboard(audio_enabled=False)`
call (no `lang` arg) passing unchanged.

Verified: full `pytest` suite (62 passed, 69 skipped), a real-Postgres
one-off script confirming all 49 new keys have fa/ar/en entries and that
kwargs-based formats (e.g. SMS subscription date/price interpolation) work
on all three languages, bot restart, and `/health` → `{"status":"ok",...}`.

Docs updated: `docs/ai/I18N_MIGRATION.md` (`settings_menu.py` now `[x]`),
this entry.

Next unchecked file: `my_khatms.py`.

## Current state — 2026-09-20 — Khatm-creation wizard fully localized [Claude Code]

Codex has stopped for this session; per the owner's instruction ("کدکس
استپ شده... برو بقیشو انجام بده") Claude Code is continuing the i18n
rollout alone. Converted `src/khatmsaz/bot/handlers/create_khatm.py` — the
entire khatm-creation wizard, the largest remaining item on the checklist —
to `t(key, lang, **kwargs)`. Added 105 new keys to `src/khatmsaz/i18n/__init__.py`
under the `create_khatm.*` prefix: template/category prompts, the four
per-(template×category) commitment-vs-open explanations, title/niyyat/
welcome/creator-display/pseudonym/start-schedule prompts, open-target and
commitment-quantity prompts (with unit/title interpolation), edition/
content-delivery/deadline-hour/capacity prompts, reminder-tone/advertising/
visibility prompts, every label used in the final confirmation summary
(mode, visibility, display, tone, content-mode, group, capacity), coupon
flow messages, cancellation/error messages, and the final success message
with its invite-link/landing-page lines.

Language is resolved once at wizard start (`start_wizard`, via
`_resolve_lang`) and stored in FSM state as `lang`; every other handler in
the file reads it back with a small `_lang(state)` helper instead of
re-querying the database on each step — this avoids a DB round-trip per
wizard message while staying correct if the user changes their language
mid-flow in a different chat (unlikely, but the next `start_wizard` call
re-resolves).

Verified: full `pytest` suite passes (62 passed, 69 skipped — skips are the
Postgres-integration tests when the DB isn't reachable in that shell), plus
a real-Postgres one-off script (`/tmp/verify_i18n_create_khatm.py`) that
confirmed all 105 new keys have fa/ar/en entries and that every format
string used in the handler formats cleanly with real kwargs on all three
languages. Restarted the running bot process and confirmed `/health` →
`{"status":"ok","database":"ok"}` after the restart.

Docs updated: `docs/ai/I18N_MIGRATION.md` checklist (`create_khatm.py` now
`[x]`), this entry.

Next unchecked file in `docs/ai/I18N_MIGRATION.md`'s priority order:
`settings_menu.py`.

## Current state — 2026-09-20 — Profile editor fully localized [Codex]

Completed the profile-editor i18n checklist item. `/profile` and the same
flow opened from Settings now load the persisted user language and localize
all name/phone/province/city/gender prompts, errors, verified-phone security
warning, success message, contact keyboard, province labels and final main
menu in Persian, Arabic or English. Canonical profile storage is unchanged.

The PostgreSQL-backed Arabic/English flow regression passes, and the full
suite passes **131 tests in 154.73s**.

## Current state — 2026-09-20 — Registration fully localized [Codex]

Completed the next i18n checklist item: first-join registration now loads
the user's stored language from PostgreSQL and renders the name, phone,
province, city and gender flow in Persian, Arabic or English, including
validation errors, contact-sharing button, completion message and localized
labels for all 31 provinces. Province callbacks still persist one canonical
Persian value, preventing language-dependent duplicates in reporting.

Added real-PostgreSQL integration coverage for Arabic and English users and
keyboard rendering. Focused suite: 7 passed. The complete suite after the
handler conversion passed **131 tests in 153.06s**; the final province-label
addition then passed its focused regression suite again.

## Current state — 2026-09-20 — Plan controls added to Admin Mini App [Codex]

The Finance area of the Telegram Admin Mini App now exposes graphical,
CSRF-protected controls for both product plan definitions and paid SMS
subscription options. A Finance Admin can edit plan title, pricing mode,
price, creation permission, enabled state, devotional-family member cap and
Quran member cap; an empty cap remains unlimited. SMS duration, price and
availability are likewise editable without typed bot commands. Existing
unknown entitlement keys are preserved when the known cap fields are edited,
and every mutation is audit-logged.

Added a real-PostgreSQL ASGI integration test covering both forms, persisted
values, validation and audit events. Focused suite: 5 passed. Full suite:
**129 passed in 151.22s**. Runtime restart is required after this entry so
the already-running process loads these routes and templates.

## Current state — 2026-09-20 — Concurrent-change safety review and clean restart [Codex]

Reviewed the new SMS-subscription, plan-cap, i18n-foundation and wizard
changes before continuing. Fixed two data-integrity/entitlement defects:
SMS purchase now checks for a contact phone before charging the wallet (and
malformed `sms_buy:` callbacks fail safely), and a repair migration
`d0e1f2a3b4c5` restores the missing FREE plan definition without overwriting
an administrator's existing entitlement values. The free devotional-member
cap now aggregates the full devotional family, including legacy DUA and
ZIYARAT rows, instead of comparing one exact template enum.

Added persistent PostgreSQL integration coverage for the SMS no-charge
guarantee and devotional-family aggregation. Full real-PostgreSQL suite:
**128 passed in 148.84s**. The Telegram bot was restarted from the tested
tree at 16:08 Asia/Tehran; polling for `@Khatm_Saz_bot` and the web service
both started cleanly, and `/health` returned
`{"status":"ok","database":"ok"}`. Bale remains disabled because
`BALE_BOT_TOKEN` is not configured. PayPing remains deliberately disabled
because its dedicated API token and a live public callback test are still
missing.

## Current state — 2026-09-20 — help.py fully localized [Claude Code]

Continued `I18N_MIGRATION.md`'s checklist. Codex had already (in parallel)
added every translation key this needed to `src/khatmsaz/i18n/` and given
every `help_*_keyboard()` function a `lang` parameter — but `help.py`
itself was still calling them with no `lang` argument and still building
its home/topic text from hardcoded Persian constants, so none of that
translation work was actually reachable yet. Wired it up: `help.py` now
resolves the requesting user's real `UserSettings.language` (via a new
`_resolve_lang` helper) before rendering the home screen or any of the 6
topics, and passes it through to every keyboard call.  Kept a `HELP_TOPICS`
dict (Persian-only) for backward compatibility with `tests/test_help.py`,
which asserts structural properties (button-only, minimum length, correct
callback sets) against the Persian baseline — no need to rewrite that test
just because the underlying strings moved into the i18n registry.

Verified against real Postgres: created a user, set their language to
`en`, confirmed `t("help.home", "en")` and `help_keyboard("en")` both
actually reflect the English strings/button labels — i.e. the full path
from a real user's stored preference through to rendered UI text works,
not just the i18n registry in isolation. Fast suite: 62 passed, 69
skipped (some previously-`ss`-skipped tests are now real passes/skips
reshuffled by Codex's parallel work — not a regression, just more test
files existing than in the last entry). Bot restarted clean; `/health` is
`{"status":"ok","database":"ok"}`.

## Current state — 2026-09-20 — Multi-language (fa/ar/en) foundation started [Claude Code]

Started backlog item 1 (full multi-language UI) — a genuinely
multi-session task, deliberately scoped and documented so any of the three
AI tools (Codex, Claude Code, Antigravity) can continue without
re-deriving the architecture. **Full continuation checklist, the exact
pattern to follow, and one non-obvious architectural constraint discovered
while building this are all in the new `docs/ai/I18N_MIGRATION.md` — read
that file, not just this entry, before touching any more translation
work.**

Built this session: `src/khatmsaz/i18n/` (central `t(key, lang)` /
`variants(key)` registry — `variants()` exists specifically because
aiogram's `F.text == X` message filters run before a handler can look up
the user's language, so a language-dependent reply-keyboard button must be
matched against the set of all its language variants instead of a single
string); `UserSettings.language_prompted` (migration `c9d0e1f2a3b4`) so a
brand-new user is asked their language exactly once, right after the
welcome message (owner's explicit requirement), never re-asked afterward;
`start.py`'s `/start` flow now shows the welcome message then a
fa/ar/en picker (`first_lang:` callback) for first-time users, and uses
the stored `language` for returning ones; the 6 main-menu reply-keyboard
buttons (Today/My Khatms/Report/Settings/Create/Help) and their matching
filters across 6 handler files were converted to the new
variant-matching pattern as the worked example for the rest.

**Explicitly not done — the large majority of the bot's user-facing text**
(the entire creation wizard, help topics, settings menus, portion
completion messages, error messages, etc.) is still Persian-only. This was
never going to fit in one session; `I18N_MIGRATION.md` has a file-by-file
checklist ordered by user-facing priority for whoever continues it. Also
still open: whether the admin web panel needs the same treatment — not
asked, not assumed.

Verified against real Postgres: `t()`/`variants()` return correct
per-language text with graceful Persian fallback for unknown
keys/languages; `main_menu_keyboard("en")` actually renders English button
labels; `language_prompted`/`set_language` persist and update correctly.
Fast suite: 62 passed, 64 skipped. Bot restarted clean; `/health` is
`{"status":"ok","database":"ok"}`.

## Current state — 2026-09-20 — Time-limited SMS reminder subscriptions [Claude Code]

Owner's backlog item 5: SMS reminders now require a paid, time-limited
subscription instead of a free on/off toggle. New module
`modules/sms_subscription/` (migration `b8c9d0e1f2a3`): `SmsPlanOption`
(admin-editable, months → price_toman, seeded with the owner's two
examples — 3 months/50,000 toman, 6 months/87,000 toman — but editable via
the new `/admin_sms_plan_set <months> <price> on|off` command, mirroring
`/admin_plan_set`'s pattern) and `SmsSubscription` (one row per user,
`expires_at` + an `expiry_notified` flag so the periodic scan never
double-notifies the same lapse).

`sms_subscription.service.purchase` charges the wallet via the existing
`wallet_service.purchase` (same mechanism as khatm-creation charges,
`InvoiceKind.PURCHASE`), extends from whichever is later — now, or the
current expiry if still active, so renewing early never wastes paid time —
and turns `UserSettings.sms_enabled` on. `process_expired` (wired into the
existing periodic scan in `bootstrap.py`, right after
`reminder_engine.run_once`, no new scheduler job needed) finds newly-lapsed
subscriptions, turns SMS off, and notifies the user through the existing
`notify` fan-out — satisfying the owner's explicit "must turn off and tell
the user" requirement.

Bot UX: `settings_menu.py`'s "📩 پیامک یادآوری" screen replaced the plain
on/off toggle with plan-purchase buttons (`sms_subscription_keyboard` in
`keyboards.py`) showing subscription status and expiry date; turning off
stays free and immediate. The typed `/sms on` command no longer silently
enables SMS for free — it now points to the button flow; `/sms off` still
works directly as a compatibility path.

Verified end-to-end against real Postgres: seeded plan options confirmed
present with the owner's exact prices; purchased a 3-month plan and
confirmed it both set a real expiry ~90 days out and flipped
`sms_enabled` to true; force-expired the subscription and confirmed
`process_expired` flipped `sms_enabled` back to false and fired exactly
one notification; ran it a second time and confirmed zero further
notifications (no double-notify on repeated scans). Fast suite: 62 passed,
64 skipped. Bot restarted clean; `/health` is
`{"status":"ok","database":"ok"}`.

## Current state — 2026-09-20 — Plain-language pass on remaining wizard prompts + local DB recovery [Claude Code]

Finished the leftover part of backlog item 3: rewrote the remaining terse
wizard prompts in `bot/handlers/create_khatm.py` — welcome-message prompt
(now says when/who sees it), creator-display-name prompt (clarifies it's
display-only, real identity stays with the bot), start-schedule prompt
(explains a future-dated start still makes the invite link work
immediately, only content delivery/reminders wait — verified against
`khatm.service.has_started` before writing this claim), reminder-tone
prompt (clarifies it only changes wording, not khatm content), and the
advertising-opt-in prompt, which previously said "نمایش تبلیغات" (a
confusing description of what's actually a per-member one-time wallet
credit). While writing that last one, checked
`advertising.service.accrue_first_completed_action` before claiming who
pays for the reward — confirmed it's funded from `AdvertisingRewardRate`
via `wallet_repository.add_credit`, never debited from the creator's own
wallet, so the new copy says exactly that instead of guessing.

**Incidental infrastructure recovery, unrelated to the wording change:**
found the bot down (`/health` connection-refused) and the supervised-loop
script (`start_bot.ps1`) not running in any active terminal. Root cause:
the `khatmsaz-py-postgres` Docker container has no published port
(`docker inspect` showed `"5432/tcp": []`), so it was never actually
reachable — the real, working database this whole session has been the
local PostgreSQL 18 recovery cluster documented in the 2026-09-20
"Database-aware health" entry (own data directory under `%TEMP%\khatmsaz-pg18-test`,
listening on 127.0.0.1:55433), which had stopped. Started it directly with
the same `pg_ctl` invocation `start_bot.ps1` uses, confirmed
`alembic upgrade head` had nothing pending, and restarted the bot process
manually. **The owner should keep a `start_bot.ps1` terminal window open**
for the auto-restart supervision to actually apply — a manually
`nohup`-launched process (as this session and prior ones have been doing)
has no supervisor and silently stays down if it ever exits.

Verified: fast suite 62 passed, 64 skipped; bot restarted clean; `/health`
returns `{"status":"ok","database":"ok"}`.

## Current state — 2026-09-20 — Today-vs-yesterday progress on countable khatms [Claude Code]

Owner's backlog item 8: after logging a contribution to a countable
("شمارشی") khatm — Salawat/Dua/Ziyarat/La'an open-pool logging — show the
whole group's running total *today so far* next to *yesterday's* full-day
total, so a member who logs early in the day (say noon) still sees the
number keep growing rather than a single frozen snapshot, since other
members log throughout the day up to local midnight.

Scoped deliberately to **open contribution logging only** (`OpenContribution.recorded_at`
already has a real per-log timestamp). The SALAWAT+COMMITMENT quantity path
(`KhatmPortion.completed_quantity`) has no per-increment timestamp today —
only one running total per participant — so building the same per-day
split there would require a new logging table, a materially bigger
feature than "add a comparison line." Not built; flagged rather than
silently skipped.

New: `open_contribution.repository.total_for_khatm_between` (date-range
sum) and `open_contribution.service.today_vs_yesterday` (Tehran-local — or
whichever `app_timezone` is configured — midnight-to-now for today, full
previous calendar day for yesterday). Wired into
`bot/handlers/portions.py::receive_contribution_amount`'s open-logging
branch, right after the existing group-progress line, only when the khatm
hasn't just been fully completed.

Verified end-to-end against real Postgres: logged one contribution "now"
and a second one, then directly backdated the second row's `recorded_at`
to exactly 24+ hours earlier and confirmed `today_vs_yesterday` correctly
split them (50 today / 30 yesterday) rather than summing both into either
bucket. Fast suite: 62 passed, 64 skipped. Bot supervisor relaunched
cleanly; `/health` is `{"status":"ok","database":"ok"}`.

## Current state — 2026-09-20 — Reordered creation wizard: content first, then commitment/free [Claude Code]

Owner's backlog item 2: the wizard used to ask تعهدی/آزاد (commitment vs.
free) before the content family, with one generic explanation for both
modes. Reordered `bot/handlers/create_khatm.py` so the flow is now content
family (Quran / Salawat / Dua-Ziyarat / La'an) → subcategory (for the three
devotional families) → **then** commitment/free, and the commitment/free
question now shows a distinct, concrete example per (template, category
group) combination — e.g. "در ختم صلواتِ تعهدی، هر عضو متعهد می‌شه یک
تعداد مشخص صلوات ... رو تا آخر بفرسته" vs. the Quran-specific "هر عضو یک
بخش مشخص از قرآن رو می‌گیره و متعهد می‌شه تا مهلت روزانه بخونتش". New
`_ask_mode` helper + `_MODE_EXPLANATION` dict keyed by
`(template_type, category_group)`; the old top-level `ck:mode:` handler
(fired before template choice) was removed and replaced by one gated on a
new `CreateKhatm.choosing_mode` state that fires after content selection.
Everything downstream (title → niyyat → ... → confirmation → creation) is
unchanged — only *when* `khatm_type` gets set moved, not what happens with
it afterward.

Verified: a functional test drove `_ask_mode` directly (bypassing Telegram)
for all four combinations (Quran, Salawat, Dua, La'an) and asserted each
produces its own distinct explanation text and correctly transitions FSM
state. Fast suite: 62 passed, 64 skipped (unchanged — no existing test
exercised the old click order, so nothing broke). Bot supervisor
relaunched cleanly; `/health` is `{"status":"ok","database":"ok"}`.

**Not done as part of this:** item 3 in the backlog (full plain-language
pass over the rest of the wizard's remaining prompts — niyyat, welcome
text, deadline hour, capacity, reminder tone, visibility) — those prompts
are unchanged from before and still assume some baseline familiarity;
flagged, not silently claimed complete.

## Current state — 2026-09-20 — Free-tier plan member caps (DEC-PY-0074) [Claude Code]

Implemented the plan-cap rule the owner specified after two rounds of
clarification (recorded as DEC-PY-0074): a FREE-tier creator gets up to
`max_devotional_members` total members summed across all their own
SALAWAT-family khatms (صلوات/دعا/زیارت/لعن all share `template_type ==
SALAWAT`), and a separate, independently configurable
`max_quran_members` for QURAN_PAGE. Reused the existing admin-editable
`PlanDefinition.entitlements` JSON column (module `plan`, already built,
previously only holding boolean feature flags) rather than adding a new
table — both caps are just new keys in that same dict, so the existing
plan-admin machinery (`plan_service.set_definition`) needed no schema
change, only richer parsing.

New: `khatm_workflow.service._enforce_creation_cap` (called at the very
start of `create_and_launch_khatm`, before any wallet charge) counts a
creator's active members via a `Participation ⋈ Khatm` query scoped to
their own khatms of the relevant template type, and raises the new
`PlanCapExceededError` if the FREE-tier cap (when one is configured) is
met or exceeded. Per the owner's explicit answer: existing khatms and their
members are never touched — only *new* khatm creation is blocked, with a
clear Persian message telling the creator to buy a plan. A missing/absent
cap key, or any plan tier above FREE, means unlimited — so this ships with
zero behavior change until a Super Admin actually sets a cap.

Extended the existing typed admin command `/admin_plan_set` to accept
`key=value` entitlement pairs (previously only boolean flags), e.g.
`/admin_plan_set FREE fixed 0 khatm.create,max_devotional_members=100,max_quran_members=302`.
No dedicated admin-panel web UI for this yet — flagged, not built, since
the owner didn't ask for one specifically and the typed command is
consistent with how `PlanDefinition` was already administered.

Verified end-to-end against real Postgres: set a FREE-plan cap of 1
devotional member, created a khatm, joined one member, confirmed a second
khatm's creation raised `PlanCapExceededError` with the right message,
then confirmed the *existing* khatm still accepted a brand-new member
despite the cap (i.e. only creation is blocked, not membership) — then
cleaned up all test rows including the plan definition itself. Fast suite:
62 passed, 64 skipped. Bot supervisor relaunched cleanly; `/health` is
`{"status":"ok","database":"ok"}`.

**Not done as part of this:** the QURAN "one free full read-through" framing
the owner used in conversation (as opposed to a flat member-count cap) — the
owner's actual answer resolved this ambiguity in favor of the same
member-count mechanism (`max_quran_members`, e.g. 302, or unset for
unlimited), so no separate "one free cycle" concept was built; if that
framing turns out to still be wanted literally as "one free completed khatm,
regardless of member count," that would be a different mechanism and needs
saying explicitly.

## Current state — 2026-09-20 — Post-completion invite links + docs archiving [Claude Code]

Two owner requests: (1) every "your portion/contribution was logged"
message now ends with an invite link to that same khatm, matching a real
sample the owner sent from a comparable bot ("با ارسال این لینک برای
دوستان خود می‌توانید آنان را دعوت کنید"). Implemented in
`bot/handlers/portions.py` via a new `_invite_friends_line` helper (same
URL-building rule as the existing QR-invite feature in `my_khatms.py`),
wired into `mark_portion_done` (Quran page completion, both the
"more pages left" and "your personal portion is done" branches) and
`receive_contribution_amount` (Salawat/open contribution and Salawat
commitment logging) — skipped only when the message already means the
whole khatm just finished, since that has its own separate
completion-announcement flow. Verified end-to-end against real Postgres: a
real invitation token was created and a real `https://t.me/<bot>?start=join_<token>`
URL was asserted present in the returned text.

(2) `PROJECT_STATE.md`, `CHANGELOG.md`, and `DECISIONS.md` had grown to
1673/1303/1098 lines respectively — append-only history files that never
shrink. Split each at a clean boundary (2026-09-18 for the first two,
DEC-PY-0064 for decisions) into `docs/ai/archive/*.md`, verbatim, with a
one-line pointer left at the bottom of each trimmed file. Entry counts were
counted before and after to confirm nothing was lost (75/128/73 headers
split cleanly across main+archive with no gaps). Documented the convention
itself in `docs/ai/AI_HANDOFF_PROTOCOL.md` so future sessions (any of the
three AI tools) repeat this pattern once a file crosses roughly 500 lines,
instead of always fully re-reading a monotonically growing file.

Also resolved three owner clarifications recorded in `docs/ai/BACKLOG.md`:
the "100 members" free-tier cap is per-creator (summed across all their
Salawat/Dua/Ziyarat khatms, not per-khatm); the SMS-plan sample prices were
in thousands of toman (۵۰,۰۰۰ and ۸۷,۰۰۰ تومان, not ۵۰/۸۷); the
post-completion "link" is the invite link (built above). Two real open
product questions remain in `BACKLOG.md` (Quran free-tier scope; what
exactly happens when a creator's 100-member cap is hit) — not guessed at.

Fast suite: 62 passed, 64 skipped. Bot supervisor (`start_bot.ps1`)
relaunched cleanly; `/health` returns `{"status":"ok","database":"ok"}`.

## Current state — 2026-09-20 — Telegram Mini App authentication and independent devotional parents

The dashboard is no longer entered through a shareable browser URL. Telegram
now receives HTTPS `web_app` buttons at `/mini/admin` and `/mini/creator`;
the backend validates Telegram's HMAC, rejects stale/duplicate/forged launch
fields, resolves the signed Telegram user, rechecks the requested role, and
issues an HttpOnly Secure scoped session. Query-string login tokens have been
disabled. Visible commands are `/admin_app` and `/creator_app`, while the old
names remain compatibility aliases. Bale fails closed until an official signed
Mini App authentication contract and a real token are available.

The creation wizard now presents Salawat, Dua/Ziyarat, and La'an as independent
top-level families and filters their children at the service boundary. Custom
requests appear only under Dua. Migration `ab8c9d0e1f2a` seeds the requested
La'an children without inventing religious body text. Focused PostgreSQL tests
prove family filtering and signed Mini App session issuance. Fast validation:
**60 passed, 61 skipped**. The complete PostgreSQL-enabled regression is
**121 passed in 136.33s**. The bot was restarted on this release; Telegram
polling, scheduler and the HTTP service are live, and `/health` returns HTTP
200 with `database=ok`. Public DNS now resolves `khatmsaz.com` through the two
assigned Cloudflare nameservers; HTTPS subdomain records/deployment remain the
external prerequisite for an actual phone Mini App launch.

The bot entry handlers now also reject empty or local HTTP origins before
attempting to send Telegram's `web_app` button, with a plain Persian message
pointing to `app.khatmsaz.com`. This prevents Telegram API errors while the
current `.env` still points at a LAN address. Two focused tests pass, and the
bot was restarted with this guard active.

Admin khatm search is now implemented in the Mini App: title, creator display
name and khatm UUID can be combined with the existing status selector. The
query is bounded and executed in PostgreSQL without changing active-member
counts. A real PostgreSQL + ASGI test covers all three keys and no-result UX;
focused integration is 2/2 and the fast suite is **62 passed, 62 skipped**.

The admin Mini App now paginates both khatm and user-search results at 25 rows
per page. Previous/next forms retain the query and khatm status filter, inputs
are bounded, and mobile styles keep the controls readable. A PostgreSQL/ASGI
test creates 26 matching rows in each list and proves the 25+1 split and filter
retention. Focused PostgreSQL validation is 3/3; fast regression is **62
passed, 63 skipped**.

Creator Mini App lists now use the same bounded 25-row pattern: the creator's
own khatms and each searchable member report paginate independently, preserve
the member query, and keep every ownership check. Active-member aggregation is
limited to the 25 visible khatms instead of scanning unrelated data. During
verification, the XLSX endpoint was found to call `strftime` on an already
formatted Tehran-time string; this 500-risk is fixed and a real workbook is
now downloaded, opened and checked in the PostgreSQL integration test.
Focused creator integration: **3 passed**; fast suite: **62 passed, 64 skipped**.

Creator-facing report values are now fully Persian: membership state, gender,
template/type labels and the previous technical `Miss` label no longer leak
enum or implementation wording. Salawat is again labelled only «صلوات» in the
shared label map; Dua/Ziyarat and La'an have independent labels. The focused
PostgreSQL/render suite passes 4/4.

## Current state — 2026-09-20 — One-command local startup now checks PostgreSQL

`start_bot.ps1` no longer starts a doomed restart loop when PostgreSQL is
offline. It probes the actual app-facing TCP endpoint on 127.0.0.1:55433,
tries the known Docker container, falls back to the restored local PostgreSQL
18 cluster when present, fails clearly if neither becomes reachable, applies
pending Alembic migrations, and only then launches the bot. `start_bot.bat`
remains the double-click wrapper.

Live verification passed: the script found PostgreSQL, confirmed Alembic head,
started Telegram polling and the admin web, and the database-aware `/health`
returned HTTP 200 with `database=ok`.

## Current state — 2026-09-20 — Database-aware health and stable PostgreSQL verification

`GET /health` now executes `SELECT 1`: it returns HTTP 200 with
`{"status":"ok","database":"ok"}` only when PostgreSQL is reachable, and
returns a detail-free HTTP 503 when it is not. Two unit tests cover both the
healthy and fail-closed paths; the fast suite is `50 passed, 59 skipped`.

Docker Desktop repeatedly lost the configured `55433:5432` host-port mapping
after engine restarts. To avoid treating this infrastructure fault as an
application failure, a separate PostgreSQL 18 cluster was initialized under
the Windows temporary directory on `127.0.0.1:55433`. All migrations applied
cleanly through `aa7b8c9d0e1f`, and the complete integration-enabled suite
passed against it: **109 passed in 131.80s**.

The live Docker database was then dumped in PostgreSQL custom format and
restored into the local cluster without modifying the source volume. Restore
verification found migration head `aa7b8c9d0e1f`, 32 users, and 22 khatms.
The Telegram bot/admin web are running against that restored data; `/health`
returns HTTP 200 with `database=ok`. The configured Telegram Super Admin
already has an active VERIFIED phone claim, so local khatm creation no longer
needs another OTP step. Bale still lacks a real token.

## Current state — 2026-09-19 — Recovered PostgreSQL and verified live Quran delivery

Docker became responsive again and the existing `khatmsaz-py-postgres`
container was restarted on port 55433. The previously pending private-join
authorization integration test now passes against real PostgreSQL (`1 passed`).
The Telegram bot and admin web were restarted after database recovery.

Live Telegram history provides end-to-end evidence that the private Quran
source is no longer blocked: `/admin_quran_source_status` reports live access,
the 604-page seed reports 604/604 image and audio coverage, and delivery
forwarded the pages 1–2 image plus the Parhizgar audio post spanning pages
1–3. The current local creation blocker is creator OTP; `.env` already has
development OTP enabled, so the next live `/verify_phone` attempt should show
the local test code without requiring Kavenegar.

## Current state — 2026-09-19 — Private-join callback authorization hardening

Reviewed the files updated by Cloud Code after the previous bot launch. The
new cross-platform join/promotion notifications and shared-contact profile UX
compile and pass the default suite. During review, a forged private-join
approve/reject callback was found to lack a fresh creator-ownership check.
Ownership is now enforced both in the handler and at the workflow service
boundary. Independent unit and PostgreSQL regression tests were added.

Validation: compileall passed; the focused authorization unit test passed and
the default suite passed (`48 passed, 59 skipped`). The focused PostgreSQL test
subsequently passed after the existing database container was recovered (see
the newer entry above). Runtime health is `{"status":"ok"}`.

## Current state — 2026-09-19 — Optional attachments for custom requests

Custom khatm requests now accept an optional Telegram document or photo after
the description. The request stores only the platform file ID and safe
metadata (name, MIME type, platform); admins see an attachment marker in the
pending queue. Migration `aa7b8c9d0e1f` upgrades existing databases.

Validation: Alembic upgrade succeeded; focused tests passed 7/7. A PostgreSQL
integration test covers persistence of the attachment metadata.

When a permitted content admin runs `/admin_requests`, attached files are
replayed directly from Telegram's file ID to that admin; the server still does
not download or permanently store the media bytes.

Full PostgreSQL integration suite after this feature: `105 passed`.

## Current state — 2026-09-19 — Regression test audit

The full non-integration test suite passes (`47 passed, 57 skipped`); the
skips are the explicitly opt-in PostgreSQL integration tests. The running bot
and admin web health endpoint both remain healthy.

## Current state — 2026-09-19 — PayPing secret hygiene audit

Searched the project (excluding the virtual environment and generated caches):
the supplied PayPing panel username/password are not present anywhere. `.env`
is ignored by Git, and only the empty `PAYPING_API_TOKEN` placeholder plus the
HTTPS callback URL remain. Runtime health is `{"status":"ok"}`.

## Current state — 2026-09-19 — Complete button-first open scheduling presets

Extended the open-khatm schedule menu with workdays, weekend, and a specific
date. The specific-date flow uses the same guarded Tehran-local FSM and the
existing service validation; command compatibility remains intact.

Validation: compileall passed; focused menu/command tests passed 7/7.

The creator settings screen now also displays the active open-khatm schedule
in plain Persian, so the selected option is visible without reopening the
schedule menu.

The schedule service now rejects fixed dates before the configured application
timezone's current date, so legacy command callers cannot save a date that the
UI promises to reject and the midnight boundary matches Tehran-local UX.

## Current state — 2026-09-19 — Button-first ending and open scheduling

Creator settings now expose historical ending controls for every owned draft
or active khatm: enter a Tehran-local date/time through a guarded FSM or clear
the existing end date with one tap. Open khatms additionally expose safe
schedule presets (off, daily, every three days), routed through the existing
service validation. Structural rules and ownership checks remain server-side;
the old commands remain compatible.

Validation: compileall passed; focused menu tests passed 3/3; the full real-
PostgreSQL suite passed 103/103.

## Current state — 2026-09-19 — Recoverable local bot launcher

Added `start_bot.ps1` and double-clickable `start_bot.bat` at the project root.
They set the project directory/PYTHONPATH, start the existing bootstrap, and
restart it after an unexpected nonzero exit. A normal stop or Ctrl+C exits the
runner. This is a local-development convenience, not a production service;
production should use the systemd unit described in `Rahnama.VPS.txt`.

## Current state — 2026-09-19 — Button-first miss-notice policy

Commitment-khatm settings now show the current creator alert threshold and a
plain-language preset picker: sensitive (1/7), balanced (2/7), or relaxed
(3/14). Selection rechecks ownership/applicability, persists through the
existing configurable miss-policy service, and explains that this is a private
management alert—not automatic removal or public negative reporting. The
arbitrary numeric legacy command remains compatible.

Validation: compileall passed; focused menu tests passed 3/3; the full real-
PostgreSQL suite passed 103/103.

## Current state — 2026-09-19 — Button-first safe cosmetic edits

The per-khatm settings screen now lets creators edit the two post-start fields
the domain explicitly permits: title and welcome text. Buttons enter a guarded
FSM, recheck ownership and ACTIVE status at save time, enforce the existing
200/500-character service limits, support deleting the welcome text with the
plain Persian phrase `پاک کردن`, and provide an inline cancel/back action.
Structural settings remain locked.

Validation: compileall passed; focused menu tests passed 3/3; the full real-
PostgreSQL suite passed 103/103.

## Current state — 2026-09-19 — Button-first creator policy settings

Every owned-khatm management card now exposes `تنظیمات ختم`. The scoped
submenu only shows policies meaningful for that khatm: Quran content delivery
mode, Skip Today for committed Quran, and Pause/Snooze for commitment khatms.
Each toggle revalidates ownership and service-level applicability, persists
through the existing domain service, and refreshes its ✅/🚫 state in place.
Legacy creator commands remain compatible.

Validation: compileall passed; focused keyboard tests passed 3/3; the full
real-PostgreSQL suite passed 103/103.

## Current state — 2026-09-19 — First-run help and profile are command-free

The persistent Home keyboard now includes `راهنمای کامل`, and the welcome
copy points to that visible button instead of `/help`. Starting creation with
an incomplete creator profile now enters the existing guarded profile FSM
immediately rather than instructing the user to type `/profile`; after profile
completion the user returns to the visible Create button as before.

Validation: compileall and focused help tests passed; the full real-PostgreSQL
suite passed 102/102. The existing menu-shape test was updated to assert the
new Help action explicitly.

## Current state — 2026-09-19 — Button-first create/manage help

The create and creator-management help topics no longer instruct normal users
to type slash commands. Create help now directly starts the verified creation
wizard or a guarded free-text custom-khatm request. Manage help directly opens
My Khatms, issues a scoped creator-dashboard link, or (for authorized users)
issues an admin-dashboard link. Legacy command entry points remain available.

Validation: compileall passed; focused help tests passed 5/5; the full real-
PostgreSQL suite passed 102/102.

## Current state — 2026-09-19 — Live Quran-source access diagnostic

The verified source map still covers all 604 image and audio pages. A direct
live Telegram forward attempt from source message 10 returned `chat not
found`, proving that `@Khatm_Saz_bot` is not yet a member of the private
source channel. `/admin_quran_source_status` now reports database coverage and
live bot-to-channel access as two separate checks, with a plain Persian remedy
when access is absent. This avoids claiming that media delivery is ready merely
because its persisted map is complete.

## Current state — 2026-09-19 — Button-first creation coupon flow

Paid-khatm confirmation now exposes a `کد تخفیف دارم` button. Tapping it
opens a guarded text step where the user sends only the coupon itself; an
explicit `ادامه بدون کد` button returns to confirmation. Invalid and expired
coupon guidance no longer requires typing a slash command. The legacy
`/coupon CODE` path remains backward-compatible.

Validation: compileall passed; focused keyboard/help tests passed 4/4; the
full real-PostgreSQL suite passed 101/101.

## Current state — 2026-09-19 — Button-first wallet and account settings help

Removed the remaining typed-command dependency from the two most common help
topics. Wallet help now has direct buttons for balance/top-up and invoice
history. Personal settings now exposes profile editing, verified phone change,
and prior-account linking as direct inline actions; those actions enter the
existing guarded FSM flows, so their OTP/manual-review security boundaries are
unchanged. The post-payment copy now tells users to tap the balance button
instead of typing `/wallet`. Slash commands remain backward-compatible but are
no longer required for these journeys.

Validation: compileall passed; the full real-PostgreSQL suite passed 98/98;
three focused help/keyboard tests passed and assert that wallet/settings help
contains no slash-command instructions. The live Telegram bot restarted and
confirmed polling as `@Khatm_Saz_bot`; admin web health returned HTTP 200.

## Current state — 2026-09-19 — Two-VPS PayPing reverse-proxy runbook

Added the owner-facing `Rahnama.VPS.txt` at the project root. It documents a
two-server production topology where the tax/PayPing-registered service domain
remains unchanged, an exact Nginx or Apache reverse-proxy route forwards the
v3 callback POST to the separate KhatmSaz VPS, and the application performs
the normal PayPing Verify before crediting a wallet. The guide covers Ubuntu,
SSH, least-privilege deployment, PostgreSQL/Redis, `.env`, Alembic/tests,
systemd, Nginx/Certbot, both source-server web servers, shared-host escalation,
firewall, callback tests, live low-value validation, troubleshooting, backups,
rollback, and final readiness checks. It explicitly distinguishes the product
page's browser referral URL from the API callback.

## Current state — 2026-09-19 — Health/Operations dashboard

Added the specification's read-only operations surface at `/operations`,
visible only to Super Admin and delegated Operations admins. It reports live
PostgreSQL connectivity; Telegram/Bale sender readiness; PayPing HTTPS
callback/API-token readiness; Kavenegar provider readiness; pending broadcast,
cover, foreign-phone and category-request queue depths; and the in-process
reminder scheduler heartbeat with last success/failure metadata. The reminder
worker now records start/success/failure without exposing exception messages or
secrets. Navigation includes a Persian «سلامت» item for authorized admins.

Validation against real PostgreSQL: admin integration suite 4/4 passed,
including both Super Admin and delegated Operations access; full suite 98/98
passed. No migration was required. Runtime restart found the configured local
Telegram proxy `127.0.0.1:12334` offline; direct Telegram access also timed
out. The admin web app was therefore restored independently on
`0.0.0.0:8000` (health 200), while bot polling awaits the owner's VPN/proxy.

## Current state — 2026-09-19 — Category moderation hardening + full admin regression

Reviewed the category/admin changes against the live PostgreSQL schema and
fixed two integrity gaps. `khatm_category` models are now imported by the
central model registry, so Alembic/`Base.metadata` sees the tables referenced
by `Khatm.content_category_id`. Category requests can only move out of
`PENDING` once; replaying a crafted fulfill/decline POST now returns 409
instead of creating duplicate permanent categories. Create, update, toggle,
fulfill and decline actions now write immutable audit events with category or
request identifiers. The settings profile button was also connected directly
to the profile wizard instead of telling non-technical users to type
`/profile`.

Added PostgreSQL + ASGI regression coverage for every current Super Admin
navigation route and the complete request-to-permanent-category lifecycle,
including replay rejection and audit evidence. Validation: Alembic database
is at `a7f8b9c0d1e2 (head)`; targeted admin suite 4/4 passed; full real-
PostgreSQL suite 98/98 passed. The Telegram bot and admin web app were running
cleanly on `0.0.0.0:8000`; restart is required after these latest code edits.
PayPing's login page was opened for the owner to create the required dedicated
API token manually. No panel password was stored or copied into project files.

## Current state — 2026-09-20 — Cross-AI handoff protocol + owner backlog [Claude Code]

Owner is now also running Antigravity locally (in addition to Codex and
Claude Code) and asked for a shared convention so any of the three doesn't
lose or duplicate another's work, plus a running list of everything they've
asked for that isn't built yet. Two new files:

- `docs/ai/AI_HANDOFF_PROTOCOL.md` — the shared rule: every meaningful change
  gets a dated `PROJECT_STATE.md` entry tagged with which agent made it
  (`[Codex]` / `[Claude Code]` / `[Antigravity]`), don't blindly revert a
  file that changed on disk since you last read it, log real product
  decisions in `DECISIONS.md` not just chat memory, and read `PROJECT_STATE.md`
  → `BACKLOG.md` → `ROADMAP.md` → `DECISIONS.md` in that order before
  starting work. `CLAUDE.md`'s "start every task" list now points here.
- `docs/ai/BACKLOG.md` — every item from the owner's latest message,
  written out precisely with current-state context (what already exists vs.
  what's actually missing) so nobody re-derives it from scratch, and with
  explicit "⚠️ نیاز به تصمیم" markers on the ones that have a real open
  product question (full multi-language UI trigger point, plan/capacity
  semantics, SMS subscription pricing — the owner's example numbers ۵۰/۸۷
  تومان look like placeholders, flagged rather than used). One item (the
  "one portion per day, surplus doesn't shrink tomorrow's share" ask)
  appears to already be built — flagged as "looks done, tell us the exact
  scenario if it isn't" instead of guessing at a fix for an unreproduced bug.

Not started yet: full i18n, wizard reordering (content family before
free/committed), the per-content-type wizard copy, plan/capacity limits,
SMS subscription billing, the post-completion thank-you message's invite
link (blocked on what "link" means), and the daily today-vs-yesterday
comparison message. These are tracked in `BACKLOG.md`, not silently
implied here.

## Current state — 2026-09-20 — SALAWAT+COMMITMENT waiting list

Closed the one remaining non-token-blocked ROADMAP.md gap (Phase 4): asked
the owner the exact blocking product question the roadmap had flagged —
"what does a waiting SALAWAT participant do casually while capacity is
full" — and got a direct answer: same as QURAN_PAGE+COMMITMENT, free casual
participation through the open contribution pool (DEC-PY-0010 now covers
both templates, not just Quran).

Changes: creation wizard asks for capacity after the per-participant
SALAWAT commitment quantity (previously this question only existed for
QURAN_PAGE); `khatm_workflow.service.create_and_launch_khatm` now stores
`capacity` for SALAWAT+COMMITMENT; `_complete_join`'s capacity gate and
`leave_khatm`'s promotion path were extended from
`template_type == QURAN_PAGE` to also cover SALAWAT (promotion now calls
`allocation_service.assign_quantity_commitment` for SALAWAT instead of
`allocate_next_portion_to`). While implementing this, found the "read along
while waiting" UI itself was incomplete for **both** templates — a
waitlisted participant's join-success message and later `my_khatms.py`
visits never actually offered a contribute button — so `build_join_success_message`'s
waitlisted branch now returns `contribute_keyboard` instead of the plain
main menu, and `my_khatms.py` now offers the same `contribute_keyboard` to
any non-committed (waitlisted) participant in a COMMITMENT khatm, not only
`OPEN`-type ones. This is a real, if small, UX fix that also benefits
existing QURAN_PAGE waitlisted users, not just the new SALAWAT case.

Verified against real Postgres end-to-end (not just unit tests): created a
SALAWAT+COMMITMENT khatm with capacity 1, joined two users, confirmed the
second was waitlisted with no portion, had the first leave, and confirmed
the second was promoted with a real 100-unit quantity portion — then
cleaned up all rows. Fast suite: 62 passed, 64 skipped. Bot supervisor
(`start_bot.ps1`) picked up the change on its next auto-restart; `/health`
returns `{"status":"ok","database":"ok"}`.

**Not done as part of this**: no admin-panel or wizard-summary display
changes beyond showing the new capacity line in the confirmation text — a
full audit of every SALAWAT-related report/label for capacity/waiting-list
wording was not performed.

## Current state — 2026-09-19 — Warmer bot copy pass + local dev fixes

Owner shared two real message samples from a comparable bot (a polite,
detailed nightly-reminder message with a deadline and a "delegate to a
friend if busy" line, and a warm per-page completion confirmation with a
sawab framing and a shareable invite link) and asked for every bot message
to read this way. Did a first, real pass rather than a superficial one:

- **DB-backed reminder templates** (`message_templates` table, rendered via
  `message_template.service.render`, consumed by
  `reminder_engine/service.py`) — added new versions for `reminder.first`,
  `reminder.second`, `reminder.final`, `reminder.missed` (fa/FRIENDLY tone)
  matching the sample's tone: explicit Tehran-time deadline, "give it to a
  friend if you're busy" line, closing blessing. `reminder.first` didn't
  previously receive a `deadline` value at all — added it at both call
  sites in `_send_daily_digest`, using `getattr(khatm, "daily_deadline_hour",
  None)` so the existing unit test's `SimpleNamespace` fake khatm (which
  has no such attribute) doesn't break.
- Per-page completion message in `bot/handlers/portions.py::mark_portion_done`
  now names the exact pages read and frames it as sawab, matching the
  sample; did **not** add an auto-generated invite link to this message —
  that's a new feature (reusable invite token per completion), not a
  wording fix, and wasn't asked for explicitly enough to build without
  checking first.
- Touched up terse/unclear strings across `start.py` (invalid/expired
  invite links, unavailable khatm — now say what to do next),
  `registration.py` + `profile.py` (province/city/gender prompts explained,
  final "ثبت‌نام کامل شد" now tells them what to do next),
  `leave.py`/`join_requests.py`/`khatm_request.py` (creator/admin-facing
  approve/reject confirmations were one-word terse, now say what actually
  happened). Left `help.py` untouched — it was already a thorough,
  step-by-step reference from an earlier session; no changes needed there.
  Left admin-only `/admin_warn` etc. command-format hints and defensive
  "should never happen" guards (invalid callback ids, account-not-found)
  mostly as-is — those aren't normal-user-facing copy.
- **Not done**: a full pass of every remaining string in every handler
  (`admin.py`, `broadcast.py`, `creator_decisions.py`, `devotional.py`,
  `manual_phone_verification.py`, `public_khatms.py`, the standalone
  `*_settings.py` command handlers now superseded by `settings_menu.py`,
  and all admin-web-panel HTML). This is a large, genuinely multi-session
  task; flagged honestly rather than claimed complete. Also explained the
  `/khatm_decision <id> <continue|open|replace>` command's cryptic options
  in plain Persian in `creator_decisions.py` (still a typed command, not
  buttons — converting it would be a UX change beyond wording, not done
  here without checking first).

**Local-dev-only fix, unrelated to copy:** owner's admin account couldn't
create a khatm because SMS is not live yet (`SMS_PROVIDER=noop`, no
Kavenegar token set). Set `DEV_OTP=1` in `.env` — an existing, intentional
dev-only bypass (`change_phone.py` already prints the OTP code in the chat
when this flag is on) — so testing isn't blocked while waiting on the real
Kavenegar key. **Must be set back to `0` before any real deployment** — the
`.env` comment already says so.

**Quran channel ingestion completed by the owner**: ran
`/admin_quran_source_seed` against the pre-verified 604-page map in
`quran_channel_seed.py` (built by an earlier session for the owner's exact
channel, chat id `-1001127138974`, including the page-1+2-share-one-image
exception the owner asked about — already correctly encoded, no code
change needed) after adding the bot as a channel admin. Confirmed 604/604
images and 604/604 audio registered.

Verified: fast unit suite 47 passed/58 skipped; bot + admin web restarted
clean with no exceptions after every batch of changes.

## Current state — 2026-09-19 — Admin-manageable khatm categories + QA handoff doc

Built the content-category system the owner asked for: صلوات/لعن/ادعیه items
are now rows in a new `khatm_categories` table (module
`src/khatmsaz/modules/khatm_category/`), manageable from `/categories` in the
admin panel (add/edit/activate-deactivate) with **no code deploy needed** to
add a new item. Migration `a7f8b9c0d1e2` adds `khatm_categories`,
`khatm_category_requests`, and `khatms.content_category_id` (nullable FK).
Owner explicitly confirmed the completion rule before this was built: a
دعا/لعن khatm finishes exactly like a صلوات khatm — a plain repetition
counter — so this only adds *content* (title/text) riding on the existing
SALAWAT execution engine; no new business rule was invented, no allocation
logic changed. The creation wizard's SALAWAT branch now shows a live list of
active categories fetched from the DB (`create_khatm.py`
`choosing_category` state) plus an "➕ دعای دیگر (درخواستی)" button that
files a `KhatmCategoryRequest`; the admin panel's pending-requests queue on
`/categories` lets an admin turn a request into a permanent category with one
form, which notifies the requester. Seeded: صلوات ساده، لعن دشمنان اهل بیت،
زیارت عاشورا، دعای مشمول، دعای عهد، زیارت آل‌یاسین — all with `body_text =
NULL` (owner will paste the actual text from khedmatgozaran.com through the
admin panel later; this is intentional, not a bug).

Verified against real Postgres: single alembic head confirmed
(`alembic heads` — there had been a latent unrelated multi-head situation
from an earlier branch point; this migration's `down_revision` was pointed at
the actual current head `q7r8s9t0`, not blindly at the last file in the
directory), migration applied cleanly, categories seeded, and an end-to-end
script created a real SALAWAT khatm with a LAAN category id and asserted
`Khatm.content_category_id` round-tripped correctly, then cleaned up its own
rows (including the `khatm_invitations` child row). Fast unit suite: 41
passed, 56 skipped. Bot + admin web app restarted cleanly.

Also wrote `docs/ai/QA_HANDOFF_TELEGRAM_TESTING.md` — a full Persian
scenario-by-scenario test script (settings menu, copy-khatm removal, creator
Excel export, admin-panel broadcast moderation, the new category system, and
a general admin-panel Persian/access sweep) for a second AI session (Codex,
which has live Telegram access) to execute end-to-end and self-fix bugs it
finds, per the owner's request. It explicitly tells Codex not to invent
product decisions it's unsure of — report them instead.

Still open: the owner's "سیستم تبلیغ" (advertising system) mention is still
unexplained — no scoping possible until they describe it. Live browser-driven
testing by this assistant was blocked twice (Claude in Chrome extension not
connected, then a fresh un-logged-in tab requiring a QR scan the owner
couldn't complete) — handed off to Codex instead per the owner's instruction.


---

## Older history

Entries from 2026-09-18 and earlier were moved to keep this file
readable: [docs/ai/archive/PROJECT_STATE_until_2026-09-18.md](archive/PROJECT_STATE_until_2026-09-18.md).
Nothing was deleted — read that file if you need context older than
the entries above.
