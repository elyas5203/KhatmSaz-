## 2026-10-08 — Antigravity — Auto-Provision Devotional Asset & Quran Forward Interception Fix
- **Auto-Provisioning Devotional Asset & Category:** Added automatic on-demand creation of `DevotionalAsset` and `KhatmCategory` in `content/service.py:add_devotional_video_page` if missing in DB when setting video clips via `/set_video`, preventing `ValueError: enabled devotional asset not found`.
- **Quran Forward Interception Fix:** Suppressed unwanted «این پیام از کانال قرآن تعیین‌شده نیامده و ثبت نشد.» error reply in `admin.py:275` for forwards from other channels by returning silently.
- **Admin Video Reply Enhancements:** Added support for extracting channel links from video captions (`caption` and `text`) and error trapping in `manage_content.py:set_video_direct`.
- **Validation:** 350 unit tests PASS.

## 2026-10-08 — Antigravity — Khutbah 5-Part Video Delivery & Dua-Ziyarat Bot Routing
- **Khutbah Routing to Dua & Ziyarat Bot:** Implemented directive «بات ارسال خطبه فدک بات دعا و زیارته». Khutbah category Khatms resolve to `BotCategory.DUA_ZIYARAT` in `bot_registry/service.py` and `create_khatm.py`.
- **Devotional Video Media Delivery:** Supported `VIDEO` kind in `content/service.py` and `devotional.py:deliver_devotional_media`. When videos are present, video clips are sent directly as requested («بجای متن و فایل و صوت همین ویدیو براشون ارسال بشه»), bypassing raw text and audio.
- **Admin In-Bot Video Upload & Reply Shortcut:** Added `/set_video <slug> [part] [optional_link]` and `/add_video` in `manage_content.py`, supporting replies to video messages and Telegram channel post links (`https://t.me/khedmatgozaran_group/25286`). Shared `manage_content` across creator and member dispatchers in `bootstrap.py`.
- **Khutbah Fadakiah 5 Parts:** Updated `scripts/register_khutbah_fadakiah.py` to seed the 5 canonical sections matching Khedmatgozaran video series (parts 1 to 5).
- **Validation:** 349 unit tests PASS (including `test_khutbah_routing_to_dua_ziyarat_bot` and `test_video_media_is_delivered_directly_instead_of_text_audio`).

## 2026-10-08 — Antigravity — Master Audit V3 Bugs Resolved & Khutbah Fadakiah Seeded
- **All 9 Audit Ledger Bugs Fully Resolved:**
  - **Bug 1:** Fixed navigation deadlock for «🔙 بازگشت به منوی اصلی» across all 3 creator submenus (`src/khatmsaz/bot/handlers/panel.py`).
  - **Bug 2:** Removed restrictive `user.role` gate in `panel.py` and `creator_broadcast.py`, giving new creators immediate menu access.
  - **Bug 3:** Registered `BotCategory.KHUTBAH` in `bot_registry/models.py`, `bot_registry/service.py`, and `keyboards.py`.
  - **Bug 4:** Fixed creator panel inline report button target callback to `creator_finance_report_entry`.
  - **Bug 5:** Cleaned up `_ask_reminder_tone` and `_show_visibility_step` in `create_khatm.py`; step-back from visibility now reliably returns to reminder tone selection.
  - **Bug 6:** Implemented `scripts/register_khutbah_fadakiah.py` seeding all 8 canonical parts of Khutbah Fadakiah, audio media slots, and category row. Enabled `KHUTBAH` in `content/service.py:DEVOTIONAL_TYPES`.
  - **Bug 7:** Added `KHUTBAH` label and `📜` icon mapping in `start.py:124-135` and `join.preview.type_khutbah` in `i18n/__init__.py`.
  - **Bug 8:** Added `"khutbah": "قرائت شد"` to `verbs` in `member_copy.py:186-193`.
  - **Bug 9:** Added `khutbah` field to web panel `/bots` in `web/app.py:2760, 2788` and `web/templates/bot_tokens.html`, with `intro.image_caption.KHUTBAH` in `i18n/__init__.py`.
- **Validation:** 347 unit tests PASS (including new regression tests in `tests/test_khutbah_integration.py`).

## 2026-10-08 — Antigravity — Master System Audit Report V3 Completed (No Code Changes)
- **Zero-Code Full-System Audit:** Performed exhaustive 0-100 audit of all bot menus, buttons, handlers, copy, and multi-bot taxonomy matching owner requirements. Documented full findings and solutions in `docs/ai/MASTER_SYSTEM_AUDIT_REPORT_V3.md`.
- **Identified Critical Defects:** Dead «بازگشت به منوی اصلی» button across 3 creator submenus, obsolete `UserRole.CREATOR` menu gating blocking new creators, and missing `KHUTBAH` bot category mapping.
- **Copy Verification:** Verified 100% eradication of «فلانی», «شرعی», and non-Persian languages temporarily hidden.
- **Validation:** 344 unit tests PASS.

## 2026-10-08 — Antigravity — Wizard Step-by-Step Back Navigation & Khutbah Family Activation
- **Fixed Wizard Back Navigation Bug (P1):** Fixed critical issue where tapping «مرحله قبل» (`ck:back`) jumped to the very first step (`choosing_template`). Implemented step-by-step reverse FSM routing across all states (`confirming` -> `choosing_visibility` -> `choosing_reminder_tone` -> target/policy/fixed daily -> `entering_creator_contact` -> `entering_welcome` -> `entering_niyyat` -> `choosing_mode` -> category -> template -> cancel).
- **Added Khutbah Family (P3):** Added «📜 ختم خطبه‌ها» (`ck:group:KHUTBAH`) to `template_choice_keyboard`. Added `KhatmCategoryGroup.KHUTBAH` in domain models, web admin panel, and `i18n` strings with support for sequential parts, audio files, and cycling.
- **Copy Cleaned (P2):** Removed the word «فلانی» completely from onboarding captions, examples, and documentation.
- **Validation:** Added comprehensive test suite `test_previous_wizard_step_comprehensive_flow` and `test_khutbah_button_in_template_keyboard` in `tests/test_v3_wizard_and_allocation.py`. All 344 tests PASS.

## 2026-10-08 — Antigravity — V3 Wizard Flow Completion, 2-Message Output & Sequential Allocation Priority
- **Wizard Editing Flow (`create_khatm.py`):** Fully connected `editing_from_confirm` flag across all wizard step handlers (`choose_category`, `choose_mode`, `enter_niyyat`, target, commitment policies, tones, visibility, and title). Changing template to `QURAN_PAGE` initializes canonical defaults (`quran_edition_id=CANONICAL_QURAN_EDITION_ID`, `content_delivery_mode="AUTO"`).
- **Split Invite Output (`create_khatm.py`):** Separated `finish_invite_links` output into 2 distinct messages: Message 1 provides creator greeting/management confirmation with persistent reply menu (`main_menu_keyboard(is_creator=True)`). Message 2 provides the ready-to-forward shareable invitation card for members without duplicate "ختم ختم", with proxy niyyat support, clear template and mode labels, and disabled link preview (`LinkPreviewOptions(is_disabled=True)`).
- **Sequential Allocation Priority (`delivery.candidate_ids` & `allocation.repository`):** Implemented time-based priority (Mode 1): earlier scheduled hour receives earlier portions/pages. Ties broken by `joined_at ASC`.
- **Validation:** Added `tests/test_v3_wizard_and_allocation.py`. 337 non-integration tests PASS cleanly.

## 2026-10-06 — Antigravity — V3 Wizard & Bot UX Overhaul
- **i18n & Wording:** Stripped all occurrences of "شرعی" and "دین شرعی" across commitment and open khatm copy. Removed obsolete "دوباره دکمه ساخت ختم را بزنید" phrases. Added family-specific done buttons (`portions.button.done.*`) and About Us strings (`@khedmatgozaran_khadem`).
- **Keyboards & Persistence:** Enforced `is_persistent=True` on reply keyboards across all menus. Replaced `ReplyKeyboardRemove` calls in phone handlers with home menu restoration. Redesigned member menu. Added edit menu for confirmation screen. Added `settings_reminder_saved_keyboard`.
- **Wizard Streamlining:** Dropped creator name, daily deadline hour (default 24:00), and platform selection (default BOTH) questions. Added inline field edit flow.
- **Settings & Delivery:** Prevented duplicate hour grid in reminder settings. Handled family-aware done buttons in occurrence delivery and reminder engine.

## 2026-10-06 — Antigravity — Taxonomy-Aware Copy, Dignified Tone & Role Separation
- **Fixed (La'an & Dua Unit Misattribution):** Resolved critical screenshot bug where category-backed Khatms (La'an, Dua) displayed "صلوات" in consent cards and wizards (`start.py`, `create_khatm.py`). Replaced with `category_group` checking (`LAAN` -> `مرتبه ذکر`, `DUA` -> `مرتبه قرائت`, `SALAWAT` -> `صلوات`). Replaced "قرائت" in fixed daily rule consent text with universal devotional verb "ادا نمایید".
- **Added (Dynamic Time & Family Vocabulary in `member_copy.py`):** Added `action_verb(family, lang)` and `done_button_label(family, lang)` supporting 5 families (Quran, Salawat, Dua, Ziyarat, La'an). Replaced hardcoded "امشب" and "(به وقت ایران)" with dynamic time-of-day deadline (`صبح امروز`, `ظهر امروز`, `بعدازظهر امروز`, `امشب`) and time-aware greetings (`سحرگاه‌تون پربرکت`, `صبح‌تون بخیر`, `ظهرتون بخیر`, `عصرتون بخیر`, `شب‌تون آرام و پربرکت`) while preserving backward compatibility.
- **Refined (Tone & Dignity):** Polished informal slang in `i18n/__init__.py` ("یکی خوندم" -> "۱ سهم انجام شد", "چند تا خوندی؟" -> "چه تعداد انجام دادید؟", "آفرین" -> "طاعت و همراهی‌تان قبول حق"). Polished creator miss notification in `reminder_engine/service.py` to dignified managerial phrasing.
- **Added (Creator vs Member Completion Separation in `completion/service.py`):** Differentiated creator congratulations from member celebration, surfaced dedication intention (`🤲 به نیت: ...`), and adapted portion icon (📖 for Quran, 📿 for devotional).
- **Added (Monthly Report Taxonomy Support):** Added `dua_count` and `laan_count` to `ClosedMonthReport` with localized Persian/Arabic/English labels in `monthly_report/service.py` and `reporting/service.py`.
- **Master Checklist Completed:** All 6 steps in `MASTER_MESSAGES_AND_COPY_AUDIT_REPORT.md` completed and ticked off.
- **Validation:** 31 targeted unit and integration tests PASS cleanly.

## 2026-10-05 — Antigravity — Systemd Stop Timeout, Polling Supervisor & Persian i18n Cleanup
- **Fixed (Stop Timeout & SIGKILL):** Fixed multi-dispatcher signal handler collision in `bootstrap.py` where `dp_member.start_polling` overwrote `dp_creator`'s SIGTERM handler. Unified process termination with `shutdown_event: asyncio.Event`, `handle_signals=False` on aiogram dispatchers, and explicit clean stop of scheduler, web server, and pollers within 1 second.
- **Fixed (Startup Crash Resilience):** Added supervisor loop with backoff retry around `Dispatcher.start_polling` so a transient 60s network timeout on startup does not crash the systemd service. Decoupled creator and member polling tasks.
- **Fixed (Corrupted Strings & Missing Buttons):** Cleaned corrupted `???` question mark strings in `i18n/__init__.py` (days of the week and wizard prompts) and `member_commitment.py`. Restored missing `settings:font` and `settings:content` buttons to `settings_home_keyboard`. Added missing key `portions.no_capacity_left`.
- **Protected (Delivery Isolation):** Isolated `deliver_due_regular_commitments` to skip Quran templates (`QURAN_PAGE`/`QURAN_SURAH`), preventing devotional reminders from touching Quran schedules. Guarded `quran_audio_enabled` access with safe fallback.
- **Validation:** 37 targeted unit tests PASS; 296 full non-integration suite tests PASS. Delivery logic from `REMINDER_REDESIGN_MASTER.md` strictly preserved.

## 2026-10-05 — Share redesign continuation [Codex]
- Final local suite: 564 PASS with PostgreSQL integration enabled, zero failures/skips. Local migration head is `share2026100501`; production migration and runtime QA were not run.
- Follow-up validation reached 437 passing PostgreSQL-enabled tests; retained debts are discoverable after leaving, Today supplies exact-share actions with cleanup receipts, and Quran text/audio-only fallbacks and member-bot language were corrected. Final requirement-by-requirement acceptance is still pending.
- Implemented numeric and regular Quran entry points according to DEC-PY-0117, exact page snapshots, member quantity changes for future shares, and nullable per-khatm audio override.
- Connected receipt-based share delivery, independent completion/reminders, and OPEN reservation deadlines; added reviewed additive migration share2026100501.
- Replaced temporary consent-registration flag with persisted card identity and success-only cleanup after transaction commit.
- Validation is PARTIAL: focused tests pass; full PostgreSQL run recorded 421 passed and 16 failed before the subsequent fixture repairs. Production untouched; not pushed.

## 2026-10-04 — Codex — Quran picker and corrupted text regression
- Restored Quran contribution routing, guarded stale repetition setup/delivery/completion, and corrected weekday translations/order and creator amount prompts.
- Added 18 regression cases. Diagnostic suite excluding pre-existing broken audit test: 328 passed, 94 skipped; full collection remains blocked. No deployment or production data changes.

## 2026-10-04 — Antigravity — Executed F0-F7 Local Fixes
- **Database**: Merged divergent Alembic heads into `a6289f6b73c2`.
- **Concurrency**: Added row-level locking (`with_for_update`) to waiting list promotion and open reservation commitments.
- **Bot/UX**: Fixed consent card deletion to wait until registration finishes, solving lost-path issues. Added missing translation keys.
- **Quran Policy**: Enforced `force_open=True` for `QURAN_PAGE` and separated `FIXED_DAILY` scheduling from `REGULAR` numeric metrics.
- **Tests**: Cleaned up all 11 test suite failures. Test suite now passes cleanly (310 passed).

## 2026-10-04 — Codex — Local repair execution master
- Added phased local repair instructions, authorization boundary and regression criteria; no runtime changes or deployment.

## 2026-10-04 — Codex — Direct A04/A05 audit
- Added source-backed reservation findings, append-only run records and ownership tracking. Analysis only; no fixes or production actions.

## 2026-10-04
- **Audit**: Executed full test suite in audit mode and logged 11 failures related to outdated tests and Alembic heads in `BUGS.md`. (Antigravity)

## 2026-10-04 — Codex — Audit is analysis-only
- Clarified owner boundary: report findings first; no code or test changes until a later explicit fix request.

## 2026-10-04 — Codex — Full-system audit playbook
- Added FULL_SYSTEM_AUDIT_MASTER.md and audit/ inventories, module map, work ownership, run evidence and bug records.
- Added repeatable AST inventory generator; documented historical graph limitations and explicit allowed/prohibited actions. No runtime changes or claim of completed system testing.

## 2026-10-03 — Codex — La'an reminder hotfix
- Return Persian reminder/completion text so delivery can send the Done button and record today's delivery instead of resending content every minute.
- Restore Quran audio hint and request persistent member keyboard.
- Related tests 12 passed; full suite 297 passed, 11 pre-existing failures, 94 skipped. PostgreSQL upgrade blocked by pre-existing multiple Alembic heads. Not deployed.

﻿- **2026-10-03:** Fixed Phase 4 UX bugs. Removed erroneous ✅ انجام سهم buttons from welcome cards and success messages. Deleted commitment warning upon acceptance. Added audio settings hint to daily reminders.
## [Unreleased] - 2026-10-03
### Fixed
- Fixed bug where users joining a commitment khatm via private link were not asked for their preferred reminder time (join_requests.py).
- Fixed bug where Quran Commitment khatms were erroneously treated as Open Khatms during join, resulting in missing portions (khatm_workflow/service.py).
- Quran audio is now enabled by default for new users, and a hint on how to disable it is attached to the reminder message.
- Removed extraneous inline action buttons (like "????? ???") that were accidentally appended beneath success messages.

# 2026-10-03 â€” Phase 6 Regular Commitment Schedules [Antigravity]
- **Added**: Updated setup UI (R09) for Member Choice commitment mode to display detailed text explicitly combining days of the week, delivery hour, occurrences per day, and weekly sum.
- **Fixed**: Verified that the schedule delivery engine properly dispatches content at the custom hour, pushes required devotional content correctly to the member, and waits for explicit logging via the inline keyboard (without advance reservation limits).

# 2026-10-03 â€” Phase 5 Open Reservations [Antigravity]
- **Added**: Open Reservations: Numeric contributions to OPEN khatms are now reserved for 7 days rather than being counted immediately.
- **Added**: Expiration System: A background task warns users on Day 6 and auto-expires incomplete numeric reservations on Day 7.
- **Fixed**: Capacity Limits: Open reservations now properly respect the remaining capacity (`repetition_target`) of the khatm.

# 2026-10-03 â€” Phase 4 Member Join Flow [Antigravity]
- **Added**: Implemented Member Join Flow logic for `FIXED_DAILY` khatms. Users joining these khatms are no longer prompted for commitment modes and default directly to schedule delivery hour.
- **Added**: i18n support for the new Fixed Daily commitment modes.
- **Fixed**: Proper schedule delivery mapping to user participation models.

# 2026-10-03 â€” Reminder redesign audit/master [Codex]
- Added `REMINDER_REDESIGN_MASTER.md` with requirements R01â€“R21, evidence F01â€“F15, pending product questions, P0â€“P9 gates, migration strategy and VPS checklist.
- Documentation only; implementation awaits the owner's explicit approval. Baseline: 285 passed, 1 failed (existing reciter-button expectation), 85 skipped; imports and Alembic head check passed.

### 2026-10-02
- **Fixed**: Manually logging completed pages in an Open Quran Khatm no longer automatically forwards the next block of pages (which double-advanced the cursor). The daily schedule handles delivering pages.

### 2026-10-02
- **Fixed**: NameError: name 'KhatmTypeEnum' is not defined crash in portions.py when tapping contribute.
- **Added**: Audio toggle and Reciter selection buttons in the member settings menu to allow users to configure and receive Quran audio.

### 2026-10-02
- **Fixed**: Leave notifications (approval, rejection, and waitlist promotion) are now routed through the correct member bot instead of defaulting to the Creator bot.

### 2026-10-02
- **Fixed**: 'Approve' or 'Reject' leave from a commitment Khatm now works correctly for Creators (leave_router added to shared routers).
- **Fixed**: Joining a 'Targeted/Commitment' Dua/Ziyarat Khatm no longer automatically forces the total Khatm goal as the user's portion.
- **Changed**: The 'Commitment Mode Picker' (Regular vs Count) is no longer forced immediately upon joining; instead, the member gets the '??? ??????' button first, which opens the picker.

## 2026-10-02 (today-share delivery integrity)
- Fixed open devotional Today actions that showed a generic share prompt without sending the Dua/Ziyarat content.
- Unified Â«Ù„ÛŒØ³Øª Ø®ØªÙ…â€ŒÙ‡Ø§ÛŒ Ù…Ù†Â» Today buttons with the canonical delivery flow and repaired legacy member-bot ownership metadata when it can be derived safely.
- Prevented manual/scheduled completion actions and daily-consumption stamps when content delivery fails, and stopped devotional content from being repeated after completion.

## 2026-10-01 (same-member-bot delivery routing)
- Routed private-join approval/rejection results back through the exact category/language member bot that received the request, and persisted that bot on approved participations.
- Routed approved creator broadcasts through each recipient's joined member bot instead of the creator bot.
- Added cross-bot media re-upload fallback for bot-scoped Telegram/Bale file IDs and backward handling for already-issued private approval buttons.

## 2026-10-01 (live QA cleanup and private-approval repair)
- Removed completed profile guidance and corrected validation-error cleanup.
- Made reminder-tone examples family-aware and removed the member-side preview heading.
- Fixed Salawat commitment target/mode consistency and enum-safe consent buttons.
- Registered private join approval handlers on the creator bot and added requester name, phone and platform ID to creator notices.

## 2026-10-01 (family-aware member share messages)
- Added polished Persian reminder and completion copy tailored to Quran, Salawat, Dua, Ziyarat and La'an.
- Included the exact share, deadline, khatm title, intention and direct same-khatm member-bot invitation where applicable.
- Renamed share completion actions to Â«Ù‚Ø±Ø§Ø¦Øª Ø¨Ø®Ø´ ÙÙˆÙ‚ Ø§Ù†Ø¬Ø§Ù… Ø´Ø¯Â» and unified scheduled/manual completion paths.

## 2026-10-01 (wizard/OTP copy and admin-action notifications)
- Hid manual phone review until the five-minute OTP window expires and rewrote both requester/admin copy.
- Split creator-wizard progress from the current question, renamed public visibility clearly, corrected the healing dedication example and removed runtime Â«(Ø¹Ø¬)Â» abbreviations.
- Added immediate admin alerts for all primary moderation queues and searchable broadcast request IDs in the admin panel.
- Made approved broadcasts identify the creator using that khatm's configured display name mode.
- Fixed the missing `KhatmTemplateType` import that crashed member-bot invite starts in production.

## 2026-10-01 (creator finance menu and payment handoff guidance)
- Changed Â«Ú¯Ø²Ø§Ø±Ø´ Ùˆ Ù…Ø§Ù„ÛŒÂ» into a real submenu with separate report and wallet/top-up actions.
- Removed the misleading fallback from an empty creator report to the member participation report.
- Clarified that users may switch off VPN for the Iranian gateway without losing payment ownership, and must wait for the successful KhatmSaz return page.

## 2026-10-01 (explicit join consent, separate question message, direct bot links)
- Added a mandatory mode-specific confirmation before membership: religious-obligation/debt copy for committed khatms and self-entered-amount completion copy for open khatms.
- Split member onboarding into one fixed welcome/context card and one separately updating question message.
- Changed post-completion sharing to direct links for the current Telegram/Bale member bot.
- Disabled `/join/{token}`, stopped generating landing-page URLs, and removed the public join template/styles.

## 2026-10-01 (production repair: join styling and Salawat image constraint)
- Inlined the public invite page's small stylesheet so proxy-generated mixed-content/static URLs cannot leave the page unstyled or the logo unconstrained.
- Added a reviewed migration expanding `ck_devotional_assets_type` to accept the fixed `SALAWAT` asset used by the Salawat image setting.
- Added render and migration-graph regression coverage.

## 2026-10-01 (per-khatm reminders, Persian invite redesign, Redis JSON safety)
- Changed account reminder settings from one bulk hour to a khatm picker showing each current time; added custom HH:MM entry and removed reminder-off controls.
- Displayed current values before editing the main personal settings.
- Rebuilt the public invite page as a responsive Persian-only entry experience and connected its logo to the operations setting.
- Made UUID and scheduled-start FSM values safe for Redis JSON serialization.
- Added reminder keyboard/FSM and join-template regressions; no migration was required.

## 2026-10-01 (restart-safe FSM and OTP admin fallback)
- Replaced process-memory FSM storage with Redis, namespaced by dispatcher and bot ID, so unanswered conversations survive restarts.
- Corrected creator/change-phone OTP wording from 10 minutes to the real 5-minute lifetime.
- Added an expiry-gated admin-verification request for undelivered SMS codes, including admin approve/reject notification and a requester Continue button that resumes pending khatm creation.
- Reused the existing manual-verification table and audit trail; no migration was required.

## 2026-10-01 (clean onboarding and complete scheduled devotional delivery)
- Converted creator registration and creator OTP verification to self-cleaning prompts; member registration already uses the same one-current-question model.
- Added clear numbered/question headings, retained questions after invalid input, clarified weekly per-selected-day counts, and compacted the member menu to four rows.
- Deleted the creator-family intro image after Continue.
- Changed regular reminders to send registered image/PDF/text immediately before the share reminder and completion action.
- Confirmed the admin-preserving development reset does not remove devotional library rows or registered devotional media.

## 2026-10-01 (local filenames for short devotional images)
- Allowed category and fixed-Salawat image fields to store one safe filename as an alternative to a full HTTP(S) URL.
- Added the Git-ignored `web/static/devotional-images` server folder and runtime URL resolution for Telegram/Bale delivery.
- Added panel-side existence/extension/path validation and plain-Persian filename guidance. No migration or seed is required.

## 2026-10-01 (hierarchical devotional pages and reorderable wizard categories)
- Grouped devotional library records and khatm categories into collapsible parent/child sections with compact closed summaries.
- Added exact 1-based wizard positioning for each dua/ziyarat or la'an category; moving one item automatically renumbers its siblings.
- Reused the existing `sort_order` column and authoritative wizard query, so no migration was required.
- Added service and rendered-template regressions; full suite passes.

## 2026-10-01 (visual-first devotional media across separate bots)
- Fixed Telegram devotional media registered by the creator bot failing in member bots because file IDs are bot-scoped; member delivery now downloads through the creator bot and re-uploads through the destination bot.
- Prioritized ordered images, then PDF, then audio; full text is now the fallback when no image/PDF exists.
- Applied the same behavior to direct `/devotional` lookup and khatm recitation delivery, with regression coverage. No migration.

## 2026-09-30 (owner spec D6 trust-first join message; Section D complete)
- Added creator-name and khatm-title invitation context before first-time member registration.
- Displayed who the khatm is from, plus its fixed intention and optional proxy/dedication, while preserving creator display-mode privacy.
- Reused the trust copy in join previews and kept it inside the one-message registration flow.
- Added regression coverage for HTML escaping, proxy text and duplicate Â«Ø¨Ù‡ Ù†ÛŒØªÂ» prevention. No migration.

## 2026-09-30 (owner spec D5 single-message join UX)
- Converted member registration to one owned, replaceable prompt and removed only typed replies belonging to that registration step.
- Added previous-step navigation throughout registration after the initial name step.
- Preserved the join welcome/selection summary when the reminder hour is confirmed.
- Added focused regression coverage. No migration.

## 2026-09-29 (Quran done action and niyyat cleanup)
- Removed duplicated Â«Ø¨Ù‡ Ù†ÛŒØªÂ» from the optional proxy/dedication suffix.
- Restored one-tap whole-share completion for committed Quran portions; numeric page reporting remains limited to open Quran.
- Limited automatic pages/day setup to open Quran.
- Clarified the religious-obligation difference between commitment and open modes in Persian creation copy.
- No migration.

## 2026-09-29 (today picker and early share delivery)
- Reworded all family intro captions to identify the member bot the audience enters and retain the shared Imam Mahdi intention.
- Removed the long commitment-consent warning from invite and public join paths; existing mode/setup choices continue in the tracked one-message wizard.
- Changed Â«Ø§Ù…Ø±ÙˆØ²Â» from dumping every share into a khatm-name picker, then delivering only the selected share.
- Early completion now shares scheduler dedupe state: completed early shares are not resent at their configured time, while merely viewing a regular share does not suppress its later reminder.
- Added focused regression coverage. No migration.

## 2026-09-29 (family intro images and compact join flow)
- Added four admin-configurable shared intro-image URLs for Quran, Salawat, Dua/Ziyarat and La'an, with per-bot and text-only fallback behavior.
- Added distinct localized intro captions for all four families.
- Consolidated Quran setup, repetition commitment selection and delivery-hour selection into the bot-owned join-summary message; only typed flow input and that tracked message are touched.
- Reconfirmed the category-free Salawat invite regression is fixed on `origin/main`; production must pull/restart to replace the older running behavior shown in the owner's screenshot.
- No migration.

## 2026-09-29 (moderated multi-channel creator broadcasts)
- Added a creator-panel broadcast center for one khatm or all distinct active members, with Telegram, Bale and SMS channel selection.
- Unified panel and bot submissions behind mandatory admin approval; removed the legacy direct-send module.
- Added per-channel admin-configurable seven-day free allowances and post-quota prices, wallet charging at approval, deduplicated audience resolution and SMS-provider delivery.
- Added migration `broadcast2026092901`. Validation: 196 non-integration tests passed, 85 deselected; 28 templates compiled; one Alembic head. Live migration apply could not connect to the configured PostgreSQL endpoint.

## 2026-09-29 (remove skip-today behavior)
- Removed skip-today service/repository/workflow APIs and all keyboard/caller parameters; new khatms force the legacy compatibility field off.
- Changed reminder pause so it never releases the member's current owed Quran share.
- Validation: 193 non-integration tests passed, 85 deselected. No migration.

## 2026-09-29 (automatic wallet-threshold FREE/PRO)
- Replaced the wallet-funded permanent PRO purchase with automatic FREE/PRO eligibility based on total wallet funds and the admin-configured PRO threshold; no balance is deducted.
- Removed the creator purchase endpoint/button and manual per-user plan assignment, excluded legacy BASIC from active configuration, and made PRO khatm creation free instead of misreading its threshold as a creation charge.
- Fixed the leaked `web.creator.plan_unlimited` key and clarified threshold copy in creator/admin panels.
- Validation: 192 non-integration tests passed, 86 deselected. No migration. DEC-PY-0098 supersedes DEC-PY-0097.

## 2026-09-29 (actionable exact-time delivery and owner-policy cleanup)
- Changed reminder polling from quarter-hour intervals to every minute with single-instance coalescing, preserving catch-up and dedupe behavior.
- Added correct completion actions to every scheduled member-share branch and a secure, duplicate-safe confirmation path for regular quantity commitments.
- Prevented cross-platform member-bot misrouting and stopped recording keyboard reminders as sent when delivery failed.
- Simplified member settings, fixed new Quran khatms to Madina/Hafs 604 pages, localized wallet amount validation, and made the creator contact line immutable through welcome-text edits.
- Validation: focused reminder suite 18 passed/1 skipped; non-integration suite 189 passed/86 deselected. No migration.

## 2026-09-29 (fix category-free Salawat invite admission)
- Fixed Salawat invite links being rejected inside the correct Salawat member bot when the khatm intentionally has no content category.
- Member-bot admission and invite generation now use the same shared bot-category resolver, preventing future classification drift.
- Added a focused regression test for the category-free Salawat case. No migration.

## 2026-09-29 (Estedad panel font)
- Replaced Vazirmatn with pinned Fontsource Estedad 5.3.0 in both shared admin and creator panel shells.
- Added `system-ui`, `Tahoma`, and generic sans-serif fallbacks; Fontsource CSS uses `font-display: swap`.
- Added regression coverage that keeps both panel shells on the same font source and fallback stack. No migration.
- Validation: 12 focused tests and 185 non-integration tests passed; 27 templates compiled; Alembic remains at one head (`rot2026092805`).

## 2026-09-29 (configurable panel logo)
- Added an operations-panel field for saving or clearing a public HTTP(S) panel logo URL in the existing system-settings store.
- Admin and creator headers now render the configured image, while preserving the current Â«Ø®Â» fallback.
- Added CSRF protection, an audit event, URL validation, and service/route/template regression tests. No migration.

## 2026-09-29 (real creator PRO purchase)
- Added a wallet-funded FREE â†’ PRO purchase action using the admin-configured positive PRO price; zero/unconfigured price keeps the button disabled.
- Purchase writes a normal PURCHASE invoice, changes only the user's plan, audits `PLAN_PURCHASED`, and uses a per-user transaction lock to prevent duplicate concurrent charges.
- Creator UI now shows only FREE/PRO; legacy BASIC remains backend-compatible and appears as paid/unlimited.
- PRO is permanent under the current no-expiry schema (DEC-PY-0097). No migration.

## 2026-09-29 (graphical creator Mini App khatm creation)
- Added a minimal card-based `/creator/khatms/new` form and `/creator/khatms/create` action for Quran, Salawat, Dua/Ziyarat and La'an, with OPEN/COMMITMENT, optional automatic title, relevant count and visibility.
- The web flow uses the existing workflow service, plan price, wallet purchase, FREE cap, phone verification and CSRF rules instead of duplicating business logic.
- Added clear localized fa/ar/en errors and direct wallet top-up navigation; linked the form from the creator dashboard and khatm list.
- Added route/template/i18n regression coverage. No migration.

## 2026-09-29 (fixed Salawat content + optional panel image)
- Salawat is now permanently category-free: choosing it always continues directly to mode selection, regardless of legacy SALAWAT category rows.
- Plain Salawat sends the owner-provided canonical text exactly.
- Added a fixed-Salawat card to `/devotionals` where an admin can save/remove a public image URL; the image is sent with the canonical text as its caption.
- Removed Salawat from category creation/fulfillment choices and hid historical Salawat categories from that panel; Dua/Ziyarat and La'an are unchanged.
- Added DEC-PY-0096 and regression tests. No migration. Full pytest: 173 passed, 86 skipped; imports/templates/Alembic-head checks passed.

## 2026-09-29 (Quran ranges + committed button + simple Salawat creation)
- Open Quran contribution logging accepts counts or localized ranges (`ØªØ§`, `-`, `â€“`, `to`; Persian/Arabic digits); inclusive range counting currently makes `20 ØªØ§ 31` equal 12.
- Added a Quran-specific fa/ar/en prompt that shows both count and range examples.
- Scheduled committed-Quran delivery now shows `âœ… Ø§Ù†Ø¬Ø§Ù… Ø¯Ø§Ø¯Ù…`; open Quran retains numeric `Ø«Ø¨Øª Ù…Ø´Ø§Ø±Ú©Øª`.
- Empty SALAWAT categories no longer block creation and instead continue with simple Salawat (`content_category_id=None`); LAAN and DUA empty-group behavior is unchanged.
- Confirmed the existing Dua/Ziyarat COUNT flow already supports one-tap and custom-amount logging with progress.
- No migration. `pytest -m "not integration"` â†’ 170 passed, 86 deselected; handler imports and Jinja template compilation passed.

## 2026-09-29 (Quran first-send timing + automatic title + OTP dedupe)
- Quran setup no longer sends the first pages immediately; the first and later batches are delivered only by the scheduler at the member's selected hour.
- Removed the create-khatm title question and generate a standard localized title from the selected content.
- OTP challenges now live for five minutes and repeated/concurrent requests reuse the active challenge without another SMS across creator verification, phone change and account linking.
- Added six regression assertions/tests; non-integration suite: 158 passed.

## 2026-09-29 (startup crash-proofing + member tickets + custom wallet + FREE/PRO)
- bootstrap: an unreachable bot (e.g. Bale down) at delete_webhook no longer crashes the whole process (restart loop). Per-bot try/except.
- /start: shows only the welcome + menu (removed auto create-wizard that fired OTP/phone messages).
- Fixed doubled Â«Ø¨Ù‡ Ù†ÛŒØªÂ» on join cards (_clean_niyyat).
- Member support redesigned to Â«Ø§Ø±ØªØ¨Ø§Ø· Ø¨Ø§ Ø³Ø§Ø²Ù†Ø¯Ù‡Ù” Ø®ØªÙ…Â»: members message their khatm's creator (picker if several), never the super-admin; creator replies now route back via the member's own member bot (previously undeliverable). Creators can still ticket the head admin.
- Wallet: custom top-up amount on the bot (ðŸ’° Ù…Ø¨Ù„Øº Ø¯Ù„Ø®ÙˆØ§Ù‡) and the creator web wallet.
- Creator wallet shows a FREE-vs-PRO comparison; removed the contact-support-to-upgrade note.
- No migration. pytest -m "not integration" â†’ 163 passed.

## 2026-09-29 (FIX: scheduled delivery stopped on member bots)
- `reminder_engine._is_reminder_due` widened from a strict 15-min window to "at or after the chosen time" (all callers already dedupe once/day). After DEC-PY-0095 removed the immediate first send, the tight window was the sole delivery path and any missed scan dropped the whole day â€” so members received nothing. Now delivery is reliable for Quran (open + commitment), positional daily reminders, and open-schedule reminders; regular Salawat/Dua schedule was already robust.
- No migration. pytest -m "not integration" â†’ 162 passed.

## 2026-09-29 (member-bot fixes)
- Open-Quran setup hour accepts exact time (14:27), stores minute, confirms HH:MM.
- Removed the stray Â«Ø«Ø¨Øª Ù…Ø´Ø§Ø±Ú©ØªÂ» button on the Quran join/setup cards (no pages sent yet); the log button now rides on the daily page delivery.
- Home menu now shown right after open-Quran setup.
- `/my_khatms` command now works on member bots (was button-only).
- Added Â«ÙˆØ±ÙˆØ¯ Ø¨Ù‡ Ù¾Ù†Ù„ Ø³Ø§Ø²Ù†Ø¯Ù‡Â» to Settings for creators/admins (callback creator:web_login).
- No migration. pytest -m "not integration" â†’ 162 passed (new tests/test_member_bot_fixes.py).

## 2026-10-01 â€” spec batch finished (L4/L11/L12/L13/M)
- L4: weekly multi-day commitment schedule (+migration schedweekdays2026100101); monthly removed. RUN alembic upgrade head.
- L11: automatic regular-commitment reminder now includes the zekr/dua text.
- L12: one devotional form sets text + image + audio (URL or file_id).
- L13/M: panels audited (29 templates compile, routes ok); added TEST_CHECKLIST.md + MANUAL_TEST_NOTES.md. 236 tests pass.

## 2026-09-30 (Ø´Ø¨) â€” live-fix batch L1â€“L11
- Join: no double Â«Ø®ØªÙ…Â»; removed wrong Â«Ù¾ÛŒØ§Ù… Ø³Ø§Ø²Ù†Ø¯Ù‡:Â» label; ðŸ”’ privacy note now the join intro-image caption (family image on top).
- Â«Ø§Ù†Ø¬Ø§Ù… Ù‚Ø±Ø§Ø¦Øª Ø§Ù…Ø±ÙˆØ²Â» delivers the zekr/dua content, then the done button last.
- Tickets include member name+id; broadcasts prefixed Â«Ø§Ø² Ø·Ø±Ù <Ø³Ø§Ø²Ù†Ø¯Ù‡>Â»; Â«Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ú¯Ø±ÙˆÙ‡ÛŒÂ» in creator main menu (text/photo/video/voice).
- 236 tests pass. Remaining (spec Â§L/Â§M): L4 weekly-multiday+migration, L11 engine content, L12 content mgmt, L13 panel audit, M test checklist.

## 2026-09-30 (Section A completed: promo media, paid SMS, servant ads)
- A2: creator promo broadcasts now carry media (photo/video/voice/document) end-to-end â€” submit stores it, `send_media` delivers it; media-only allowed.
- A3: SMS broadcast channel is paid from the first message (free_count=0), admin-reviewed, wallet-charged on approve.
- A4: new isolated `servant_ad` module + `/servant-ad` admin page â€” admin-initiated system ad to BASIC creators' deduped audiences.
- 210 tests pass (new tests/test_servant_ad.py). No migration.

## 2026-09-30 (Section A backbone: 3-tier plans + role removal)
- Plans are now a STORED tier again (FREE/BASIC/PRO); `get_plan` reads UserPlan (no wallet derivation).
- Admin-editable `free_total_member_cap` (default 1000) + `ads_enabled` per plan on /finance.
- FREE auto-upgrades to BASIC when total audience passes the cap, with a one-time creator notice; BASIC = Ø®Ø¯Ù…ØªÚ¯Ø²Ø§Ø±Ø§Ù† ads flag on, PRO = off. Old per-family creation block disabled when the new cap is set; creation no longer blocked by member count.
- Removed the "upgrade to creator" buttons (support inline, admin panel, sidebar) â€” everyone in the Ø®ØªÙ…â€ŒØ³Ø§Ø² bot is a creator.
- Creator wallet shows the real tier + total-audience vs cap + ads status + 3-tier comparison. 208 tests pass.
- Staged (own goals): A2 promo messaging, A3 paid SMS, A4 servant ads, PRO buy-member-blocks.

## 2026-09-30 (E2 verified, E3 range arithmetic aligned)
- E2: verified the "today" pickâ†’deliverâ†’doneâ†’no-resend flow (report.py) across all khatm types.
- E3: `parse_contribution_amount` now treats Â«Û²Û° ØªØ§ Û³Û±Â» as 11 pages (endâˆ’start, owner's rule) and rejects Â«Û²Û° ØªØ§ Û²Û°Â». Used in both open and committed-count logging. 205 tests pass.

## 2026-09-30 (E1 scheduling audit + duplicate-send fix)
- Audited reminder_engine: every-minute scan, at/after-time once-per-day due check, per-participation time, per-user timezone, correct per-bot delivery â€” all khatm families.
- Fixed a duplicate send: `deliver_due_next_portions` now records DAILY_REMINDER so the digest path doesn't re-send the freshly-allocated portion next scan.
- Added `docs/ai/OWNER_SPEC_MASTER.md` (living spec of all owner requirements). No migration. 204 tests pass.

## 2026-09-29 (plan panels aligned to real backend)
- Admin `/finance`: honest plan-card wording (enabled = Â«ÙØ¹Ø§Ù„ Ùˆ Ù‚Ø§Ø¨Ù„ Ø§Ø¹Ù…Ø§Ù„Â»), member caps shown only on FREE, BASIC/PRO note "no member limit", price titled Â«Ù‡Ø²ÛŒÙ†Ù‡Ù” Ø³Ø§Ø®Øª Ù‡Ø± Ø®ØªÙ…Â». New Â«Ù…Ø¯ÛŒØ±ÛŒØª Ù¾Ù„Ù† Ú©Ø§Ø±Ø¨Ø±Ø§Ù†Â» section + `POST /finance/user-plan` (search â†’ set FREE/BASIC/PRO, audit `USER_PLAN_CHANGED`).
- Creator `/creator/wallet`: read-only Â«Ù¾Ù„Ù† ÙØ¹Ù„ÛŒÂ» card (title from PlanDefinition, FREE usage vs cap for Quran & Salawat/Dua, cap-only-blocks-new-creation note, no buy button, contact-support-to-upgrade note). Top-up and SMS kept separate.
- No domain/pricing/DB change. `pytest -m "not integration"` â†’ 158 passed.

## 2026-09-29 (admin + creator panel redesign; creator wallet-charge button)
- Creator bot menu: new Â«ðŸ’³ Ø´Ø§Ø±Ú˜ Ú©ÛŒÙ Ù¾ÙˆÙ„Â» button (reply + inline panel) wired to the existing PayPing top-up flow; new i18n `menu.creator.wallet`.
- Creator web panel: redesigned nav (sidebar + dock), new KPI dashboard, parent/child Â«Ø®ØªÙ…â€ŒÙ‡Ø§ÛŒ Ù…Ù†Â» (status â†’ type â†’ khatm), and a wallet page (balance/credit/plan, top-up, invoices). ~35 new `web.creator.*` keys.
- Admin web panel: new Â«ØªØ£ÛŒÛŒØ¯ Ø³Ø§Ø²Ù†Ø¯Ú¯Ø§Ù†Â» page â€” approve/reject creator-role requests, upgrade role, notify user, audit event. Nav link added.
- Inline bot panel: admin dead-ends now point to the real web-panel sections.
- No migration. `pytest -m "not integration"` â†’ 153 passed (new `tests/test_panel_redesign.py`).

## 2026-09-28 (DEC-PY-0092 rotating committed-Quran allocation)
- New Quran commitment plans now allocate a distinct staggered start per reader and advance each reader's own ranges sequentially with wraparound.
- Added `rot2026092805`: strategy/boundary metadata, per-participant rotation offset, and partial uniqueness rules that support repeated page ranges safely.
- Preserved existing plans as `SHARED_POOL`; rotating released rows cannot leak into the legacy emergency/claim pool.
- PostgreSQL fresh apply + downgrade/re-upgrade and full 227-test suite pass.

## 2026-09-28 (integration-suite alignment after R11/live QA)
- Updated integration fixtures and expectations for multi-bot notification callbacks, member-bot invite links, current Persian copy, and the R11 member commitment picker.
- Corrected one-portion-per-day test setup to backdate `updated_at`, which is the production dedupe timestamp.
- Verified the complete opt-in suite on PostgreSQL 17: 226 passed.

## 2026-09-28 (fresh-database Alembic ordering fix)
- Repaired the migration graph so `bot_instances` is created before `joined_via_bot_instance_id` and the R2 intro-image column reference it.
- Preserved all revision IDs and added a migration-graph regression test.
- Verified the entire chain with `alembic upgrade head` on an empty disposable PostgreSQL 17 database.

## 2026-09-28 (R2 per-bot intro image + admin upload)
- **Schema**: `bot_instances.intro_image_url` (migration bii2026092803). **Admin**: `/bots` form per member bot + `POST /bots/{id}/intro_image`. **Wizard**: intro image + fixed Â«Ù‡Ù…Ù‡ Ø®ØªÙ…â€ŒÙ‡Ø§ Ø¨Ù‡ Ù†ÛŒØª ØµØ§Ø­Ø¨â€ŒØ§Ù„Ø²Ù…Ø§Ù†Â» caption shown right after commitment/free choice; text-only fallback. Tests +5. Suite 142.

## 2026-09-28 (R1 ephemeral wizard prompts)
- **Wizard**: `_wiz` helper deletes the previous bot prompt before sending the next; whole create-khatm question spine routed through it so the chat no longer piles up questions. Guarded (failed delete never blocks). Tests +3. Suite 137.

## 2026-09-28 (R11/N2 member commitment: regular schedule + count logging)
- **Member flow**: after joining a repetition COMMITMENT khatm, member picks COUNT (pledge+log+re-pledge R12) or REGULAR (freqâ†’dayâ†’per-occurrenceâ†’hour). Quran unchanged.
- **Engine**: `deliver_due_regular_commitments` sends the nudge at the chosen local time each occurrence (daily/weekly/monthly), deduped per day.
- **New**: `modules/participation/commitment.py` (pure logic), `bot/handlers/member_commitment.py`, participation repo/service setters, i18n `commit.*`/`weekday.*`/`reminder.regular_commitment`, keyboards. Tests +17. Suite 134 passed.

## 2026-09-28 (N1 i18n audit â€” removed dup + 31 dead keys)
- **i18n**: removed duplicate `menu.public_khatms` + 31 unreferenced keys (leftovers from removed capacity/ads/content-delivery/per-member-share/old-welcome/orphan-my_khatms features). 852â†’820 keys. All remaining keys verified fa/ar/en complete, non-empty, placeholder-consistent.
- **Guard**: `tests/test_i18n_audit.py` (no-dupes, all-langs, placeholder-match).

## 2026-09-28 (R4 creator-contact in welcome â€” migration-free)
- **Wizard (R4)**: new step asks the creator for a contact handle (Telegram/Bale ID / t.me link / phone) after the welcome step, with a one-tap "use my @username" button and skip. Folded into the existing `welcome_text` (ðŸ“¬ line) so every member sees how to reach the organizer â€” no migration.
- **Blocker**: Alembic has 3 heads (`a1b2c3d4e5f6`, `f4a5b6c7d8e9`, `zz9999`); `upgrade head` fails until merged. R2/R4 kept migration-free; R11-full + DEC-PY-0092 wiring wait on the merge + a test DB.
- **Tests**: +`tests/test_creator_contact.py` (7). Suite 114 passed / 85 skipped.

## 2026-09-28 (redesign plan + remove capacity wizard step)
- **Plan**: `docs/ai/REDESIGN_PLAN_2026-09-28.md` â€” minimal-interaction redesign of the create-khatm wizard + member join flow (R1â€“R13) with a Codex meta-prompt.
- **Wizard**: removed the capacity question (owner: unnecessary step) â€” `enter_commitment_quantity` and `enter_deadline_hour` now go straight to visibility with capacity=None; the old capacity handlers are unreachable.

## 2026-09-28 (allocation root-cause + warmer commitment messages + SMS answer)
- **Allocation (DEC-PY-0092)**: reproduced & root-caused the Quran page-jump bug (committed readers got the shared pool's next-open portion â†’ personal pages jumped by member count). Added the unit-tested rotating helper `positional_range_for_step` (5 tests). Wiring + migration is a documented follow-up BLOCKED on a test Postgres + owner review (the partial UNIQUE(plan_id,unit_start) constraint conflicts with rotating repeats â€” needs a portion-identity change).
- **Copy**: rewrote the quantity-commitment confirmation and completion messages to be warmer/devotional (owner called the old ones Â«Ù…Ø³Ø®Ø±Ù‡Â»), fa/ar/en, matching the project tone guide.

## 2026-09-28 (live Telegram QA â€” Chrome/Codex)
- Exercised the fa/ar/en member join links and creator/super-admin bot flows using the owner's development-only Telegram accounts.
- Verified member-bot language selection, exact `14:40` reminder parsing, `/public_khatms`, creator khatm management, QR links, stats, and reversible settings toggles.
- Recorded blockers/defects: Mini Apps refuse to connect in Telegram Web because `/mini/admin` and `/mini/creator` return `X-Frame-Options: SAMEORIGIN`; leaked `Welcome /admin_app`; English Quran source delivery failure; misleading generic cancel copy; mixed-language creator/admin controls; technical admin approval instructions.
- No production payment, broadcast, deletion, ban, deploy, restart, or database operation was performed.

## 2026-09-28 (live-QA: member-bot language, HH:MM reminder, /public_khatms on creator)
- **Fix (CRITICAL)**: member bot showed Persian commitment consent â€” `resume_join_after_registration` now uses the bot's language on member bots.
- **Fix**: per-khatm reminder accepts a typed exact time Â«14:40Â» (reuses AskDeliveryHour).
- **Fix**: `/public_khatms` produced no output on the creator bot (was member-only); moved to shared routers so it works on both dispatchers.
- **Docs**: recorded owner's large added goals (full admin panel redesign, creator web panel, mini-app entry buttons, finance simplification, payment/cert follow-up) in QA_MATRIX for dedicated sessions.

## 2026-09-27 (per-khatm broadcast targeting)
- **Feature**: Creator broadcast now starts with a khatm picker â€” Â«ðŸ“¢ Ø¨Ù‡ Ù‡Ù…Ù‡Ù” Ø®ØªÙ…â€ŒÙ‡Ø§Â» plus one row per active khatm â€” instead of blasting the whole audience with no choice (owner: Â«Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ú¯Ø±ÙˆÙ‡ÛŒ Ø¨Ù‡ Ù‡Ø± Ø®ØªÙ… Ù…Ø´Ú©Ù„ Ø¯Ø§Ø±Ù‡Â»). New FSM step `choosing_target` + handler `choose_broadcast_target`; `creator_broadcast.service.get_creator_audience_count` and `get_broadcast_audience` take an optional `khatm_id` scope; `confirm_broadcast` sends only to the chosen scope (de-duplicated). The creator inline-panel Â«Ø§Ø±Ø³Ø§Ù„ Ù¾ÛŒØ§Ù… Ú¯Ø±ÙˆÙ‡ÛŒÂ» button now opens this picker directly instead of a how-to text.

## 2026-09-27 (owner product rules: fixed niyyat + Ù†ÛŒØ§Ø¨Øª, drop content-format step, title example, live panel buttons)
- **DEC-PY-0090**: Niyyat is now FIXED for every khatm (Â«Ø¨Ù‡ Ù†ÛŒØª Ø¸Ù‡ÙˆØ± Ø§Ù…Ø§Ù… Ø²Ù…Ø§Ù† Ø¹Ù„ÛŒÙ‡ Ø§Ù„Ø³Ù„Ø§Ù…Â»); the creation wizard no longer accepts a free niyyat. The former niyyat step is repurposed as an optional Ù†ÛŒØ§Ø¨Øª (dedication) prompt â€” typing a name appends Â«â€¦ â€” Ø¨Ù‡ Ù†ÛŒØ§Ø¨Øª Ø§Ø² {name}Â». `create_khatm._compose_niyyat` + i18n `create_khatm.fixed_niyyat` / `niyyat_proxy_suffix`.
- **DEC-PY-0091**: Removed the Â«ÙØ±Ù…Øª Ø§Ø±Ø³Ø§Ù„ Ù…Ø­ØªÙˆØ§Â» step (auto/photo/text) from the creation wizard â€” `choose_edition` now sets `ContentDeliveryMode.AUTO` and skips it; the bot sends whatever content it has. Per-khatm override still available in khatm management.
- **Copy**: Title-prompt example updated to Â«Ø®ØªÙ… Ù‚Ø±Ø¢Ù† Ø¨Ø±Ø§ÛŒ Ø³Ù„Ø§Ù…ØªÛŒ Ø§Ù…Ø§Ù… Ø²Ù…Ø§Ù† Ø¹Ù„ÛŒÙ‡ Ø§Ù„Ø³Ù„Ø§Ù…Â» (fa/ar/en).
- **Panel**: Creator inline-panel Â«Ù…Ø§Ù„ÛŒÂ» and Â«ØªÙ†Ø¸ÛŒÙ…Ø§ØªÂ» buttons were "coming soon" dead-ends; now open the real personal report and settings menu.

## 2026-09-27 (admin dashboard â†’ real hub: quick-access tiles + clickable queue)
- **UX**: The admin dashboard (`/`) now shows a permission-gated Â«Ø¯Ø³ØªØ±Ø³ÛŒ Ø³Ø±ÛŒØ¹Â» grid of tiles linking to every section (Ø¯Ø¹Ø§Ù‡Ø§/Ø¯Ø³ØªÙ‡â€ŒÙ‡Ø§/Ù¾ÛŒØ§Ù…â€ŒÙ‡Ø§/Ø®ØªÙ…â€ŒÙ‡Ø§/Ú©Ø§Ø±Ø¨Ø±Ø§Ù†/Ø§Ø­Ø±Ø§Ø²/Ù¾ÛŒØ§Ù… Ú¯Ø±ÙˆÙ‡ÛŒ/Ù…Ø§Ù„ÛŒ/Ø¨Ø§ØªÙ‡Ø§/Ø³Ù„Ø§Ù…Øª/Ø±ÙˆÛŒØ¯Ø§Ø¯Ù‡Ø§/Ù…Ø¯ÛŒØ±Ø§Ù†), so a non-technical admin lands and reaches any capability in one tap without hunting the sidebar. The Â«Ù…ÙˆØ§Ø±Ø¯ Ø¯Ø± Ø§Ù†ØªØ¸Ø§Ø±Â» rows are now clickable links (coversâ†’/khatms, broadcastsâ†’/broadcasts, requestsâ†’/categories) and turn amber when non-zero. Verified by Jinja render (12 tiles, gated by `admin._admin_permissions`). Part of the owner's added panel-redesign goal.

## 2026-09-27 (member-facing hardcoded Persian â†’ i18n + i18n coverage guard)
- **Fix**: `member_start.py` sent two hardcoded Persian errors (Â«Ø§ÛŒÙ† Ø®ØªÙ… Ù…Ø±Ø¨ÙˆØ· Ø¨Ù‡ Ø¨Ø§Øª Ø¯ÛŒÚ¯Ø±ÛŒ Ø§Ø³ØªÂ»ØŒ Â«Ø§ÛŒÙ† Ø®ØªÙ… ÙÙ‚Ø· Ø¨Ø±Ø§ÛŒ Ú©Ø§Ø±Ø¨Ø±Ø§Ù† â€¦Â») even on the Arabic/English member bots. Moved to i18n keys `join.error.wrong_bot` and `join.error.platform_restricted` (fa/ar/en).
- **Guard**: New `tests/test_i18n_coverage.py` â€” asserts (1) every i18n key defines fa+ar+en, and (2) every literal `t()`/`web_t()` key referenced in code exists. This locks out the raw-slug / wrong-language bug class the owner hit in live QA (e.g. Â«button.confirmÂ»). Full audit result: 812 keys, 0 missing a language, 0 dangling references.

## 2026-09-27 (CRITICAL live-QA fixes: join crash, missing i18n keys, member menu, per-khatm reminder)
- **Fix (CRITICAL)**: `join_via_token()` crashed with `TypeError: got an unexpected keyword argument 'joined_via_bot_instance_id'` â€” every member-bot commitment join died at `accept_commitment` â†’ the bot froze after Â«ØªØ¹Ù‡Ø¯ Ø±Ø§ Ù…ÛŒâ€ŒÙ¾Ø°ÛŒØ±Ù…Â». Threaded `joined_via_bot_instance_id` through `join_via_token` â†’ `_complete_join` â†’ `participation_service.join` â†’ `repository.create` (the column already existed; the plumbing was missing). Regression test `tests/test_join_records_bot_instance.py`.
- **Fix**: Missing i18n keys rendered raw slugs to users: `button.confirm` (invite-language step showed literal Â«button.confirmÂ»), `my_khatms.button.leave` (member my-khatms leave button showed the raw key). Added both (fa/ar/en) + a friendlier confirm label Â«âœ… ØªØ£ÛŒÛŒØ¯ Ùˆ Ø³Ø§Ø®Øª Ù„ÛŒÙ†Ú©Â».
- **Fix**: After joining via a deep link the member's bottom menu never appeared (had to send /start manually). `resume_join_after_registration` now sends the home menu (`join.menu_hint`) when it doesn't ask the delivery hour; the hour handler already did.
- **Feature**: Per-khatm reminder time for members â€” Â«â° Ø³Ø§Ø¹Øª ÛŒØ§Ø¯Ø¢ÙˆØ±ÛŒÂ» button per khatm in member my-khatms (`mk_hourmenu`/`mk_sethour` handlers). Someone in 7 khatms can set 7 different times (`notification.set_reminder_preference` is per-participation).

## 2026-09-27 (create-khatm wizard keyboards i18n + cancel on every step)
- **Feature/Fix (BACKLOG #1 + goal option 2/3)**: All create-khatm wizard inline keyboards were hardcoded Persian, so a creator on the Arabic/English bot saw Persian buttons under an already-translated prompt. Every wizard keyboard (`commitment_mode`, `template_choice`, `category_choice`, `skip_niyyat`, `content_delivery_mode`, `reminder_tone`, `creator_display`, `start_schedule`, `capacity`, `visibility`, `advertising`, `confirm`, `coupon_entry`) now takes `lang` and uses new `ck.*` i18n keys (fa/ar/en). Callers in `create_khatm.py` pass the wizard language.
- Every wizard step now ends with a localized Â«Ø§Ù†ØµØ±Ø§ÙÂ» (cancel) row wired to the existing state-independent `ck:cancel` handler (goal: cancel available at every step). Back/previous-step navigation is deferred to a follow-up.
- Tests: `tests/test_wizard_keyboards_i18n.py` (every keyboard localized + cancellable in fa/ar/en); updated `test_home_menu` for the new cancel row.

## 2026-09-27 (fix cross-platform notification routing + callback scan)
- **Fix (correctness)**: `notify(..., bot_instance_id=...)` used the joined-through member bot for EVERY platform identity. A user with both a Telegram and a Bale identity who joined via a single-platform member bot had the other-platform reminder sent from the wrong-platform bot â€” which silently fails, so they got no reminder. `notify_adapter.build_notify_fn` now uses the member bot only when its platform matches the identity's platform; otherwise it falls back to that platform's creator bot. Regression test `tests/test_notify_routing.py`.
- **Scan**: Full inline-callback audit â€” every emitted `callback_data` prefix has a handler. `cs:miss:*` (miss-policy keyboard) is orphaned DEAD CODE (`creator_miss_policy_keyboard` is never called â€” leftover from the removed miss system, BACKLOG #15), not a reachable dead button; left in place, noted in QA_MATRIX.

## 2026-09-27 (more dead-button + member i18n fixes, Phase 2)
- **Fix**: Â«ðŸ•‹ Ø®ØªÙ…â€ŒÙ‡Ø§ÛŒ Ø¹Ù…ÙˆÙ…ÛŒÂ» (`menu.public_khatms`) reply button was only wired as the `/public_khatms` command, so tapping it in the participant/member menu did nothing. Added an `F.text.in_(PUBLIC_KHATMS_BUTTON_TEXTS)` handler; the empty-state reply keyboard now uses `home_keyboard_for_bot` so a member bot shows the member menu, not the participant one. Regression test `tests/test_public_khatms_button.py`.
- **Fix**: `snooze_keyboard` had hardcoded Persian labels (Â«Û³Û° Ø¯Ù‚ÛŒÙ‚Ù‡Â»â€¦), so a member on the Arabic/English bot saw Persian snooze buttons. Now takes `lang` and uses the existing `portions.snooze_label.*` i18n keys (+ new `portions.snooze_label.custom`).
- Note: broader wizard/khatm-management keyboards still hold hardcoded Persian â€” that is the tracked BACKLOG #1 i18n migration (creator bot only; those keyboards never render on member bots), not a regression.

## 2026-09-27 (fix dead creator reply-menu buttons + Phase-1 QA matrix)
- **Fix**: The creator reply-menu buttons Â«ðŸ“Š Ú¯Ø²Ø§Ø±Ø´ Ùˆ Ù…Ø§Ù„ÛŒÂ» (`menu.creator.finance`) and Â«â“ Ø±Ø§Ù‡Ù†Ù…Ø§ Ùˆ Ù¾Ø´ØªÛŒØ¨Ø§Ù†ÛŒÂ» (`menu.creator.support`) had NO handler anywhere â€” the old `creator_menu.py` was deleted (only a stale .pyc remained) and never re-registered, so tapping either did nothing (confirmed QA finding). Added `panel.handle_creator_finance` â†’ `report.personal_report` and `panel.handle_creator_support` â†’ `help.help_command`. Regression test `tests/test_creator_menu_buttons.py` feeds each button's fa/ar/en label through a real Dispatcher and asserts the handler fires.
- **Docs**: Added `docs/ai/QA_MATRIX.md` â€” the requirementâ†’codeâ†’testâ†’result matrix for Phase 1 of the stabilization goal, with honest status flags and the live/decision blockers.

## 2026-09-27 (member-bot i18n buttons + delivery-hour on every fresh join)
- **Fix (major)**: `join_preview_keyboard` and `commitment_consent_keyboard` were hardcoded Persian, so the Arabic/English member bots showed Persian buttons ("Ø´Ø±Ú©Øª Ø¯Ø± Ø§ÛŒÙ† Ø®ØªÙ…", "ØªØ¹Ù‡Ø¯ Ø±Ø§ Ù…ÛŒâ€ŒÙ¾Ø°ÛŒØ±Ù…") under a correctly-translated message. Both now take `lang` and use new i18n keys (`join.button.join`, `join.button.cancel`, `join.button.accept_commitment`, fa/ar/en). All 4 call sites (start.py x2, member_start.py, public_khatms.py) pass the bot/user language.
- **Fix**: The delivery-hour question was only asked when a first portion existed, so committing to a Quran-page khatm with no immediate portion silently skipped it. Now every fresh (non-waitlisted) COMMITMENT or OPEN join asks the delivery hour if no preference is set yet.

## 2026-09-27 (admin panel: devotional-texts CRUD page + grouped nav redesign)
- **Feature**: New admin page `/devotionals` â€” a graphical CRUD for dua/ziyarat **texts** (owner request: add/edit dua text without code + git pull). Add form (type, title, unique slug, full text) + per-item edit form + enable/disable toggle. Text is stored in `devotional_assets` (the same rows the startup seed writes and member bots deliver) and auto-chunked into <=3500-char pieces joined by `\x1e` at save time. Routes: `GET /devotionals`, `POST /devotionals/save` (upsert by slug), `POST /devotionals/{slug}/toggle`. All gated on `CONTENT_MANAGE`, CSRF-checked, audited (`DEVOTIONAL_TEXT_SAVE` / `DEVOTIONAL_TEXT_TOGGLE`). New service helpers `content.service.list_all_devotional_assets` and `set_devotional_enabled`.
- **Redesign**: `base.html` rebuilt with a proper desktop **sidebar** grouped into parent/child sections (Ù…Ø­ØªÙˆØ§ / Ú©Ø§Ø±Ø¨Ø±Ø§Ù† Ùˆ Ø®ØªÙ…â€ŒÙ‡Ø§ / Ù…Ø§Ù„ÛŒ / Ø³ÛŒØ³ØªÙ… / Ù…Ø¯ÛŒØ±ÛŒØª) with active-page highlighting via `request.url.path`; the flat bottom dock is now mobile-only (`lg:hidden`). Same glassmorphism tokens, but far easier to navigate. New "Ø¯Ø¹Ø§Ù‡Ø§ Ùˆ Ø²ÛŒØ§Ø±Ø§Øª" entry added to both the sidebar and the mobile dock.

## 2026-09-27 (member-side join button fixed + member welcome i18n)
- **Fix (major)**: On a member bot the "âœ… Ø´Ø±Ú©Øª Ø¯Ø± Ø§ÛŒÙ† Ø®ØªÙ…" button was filtered on the `JoinWorkflow.previewing` FSM state (`member_start.handle_member_join_callback`). MemoryStorage is wiped on every service restart, so after any restart the button hit no handler and the bot did nothing â€” the exact "Ø¨Ø§Øª Ù‡ÛŒÚ†ÛŒ Ù†Ù…ÛŒØ¯Ù‡" symptom. The token is already in the callback data, so the state was never needed. Removed the state filter to match the state-independent creator-side handler (`start.accept_join_preview`). This unblocks the whole member flow: first-time registration (share-number, no OTP) â†’ commitment consent â†’ join-success message â†’ ask delivery hour.
- **Fix**: `member_start.handle_member_start` sent a hardcoded Persian welcome even on the Arabic/English member bots. Now uses a new i18n key `member.welcome` (fa/ar/en) so each bot greets in its own language.

## 2026-09-27 (seed devotional texts: Ziyarat Ashura, Al-Yasin, Faraj, Ahd)
- **Feature**: Owner-provided devotional texts are now seeded into `devotional_assets` at startup (idempotent upsert keyed on slug), so a plain `git pull && systemctl restart` makes them live with no manual DB step or `/manage_content` upload. New files: `content/_devotional_texts.py` (raw Arabic+Persian texts) and `content/devotional_seed.py` (`seed_devotional_texts`, auto-chunks each text into <=3500-char pieces joined by `\x1e`, the delimiter `portions._send_recitation_content` splits on). Wired into `bootstrap.main` right after the Quran channel self-heal.
- **Slugs**: `ziyarat-ashura` (ZIYARAT), `dua-ale-yasin`, `dua-faraj`, `dua-ahd` (DUA). To deliver one in a khatm, set the `KhatmCategory.devotional_slug` to the slug (Ziyarat Ashura also auto-matches a category whose title contains Â«Ø¹Ø§Ø´ÙˆØ±Ø§Â» via the existing hint). Text-only for now; images/audio are added later via the admin channel/panel and live in separate columns, so this seed never overwrites them.

## 2026-09-26 (invite flow hardening after QA)
- **Fix**: `create_khatm.show_invite_platform_keyboard` and `show_invite_languages_keyboard` swallowed every `edit_text` failure with `except Exception: pass`, so if the edit failed (message too old/deleted, or a raced double-tap) the creator was left on a dead screen with no next step â€” matching a QA report that "selecting the invite messenger showed no new step". Both now fall back to sending the step as a fresh message so the flow always visibly advances.
- **Refactor**: `show_invite_languages_keyboard` dropped its duplicated inline category-resolution block and now uses `invite_links.resolve_khatm_category_value` (the canonical `resolve_bot_category`), matching `finish_invite_links` and the QR button.
- **QA note**: The multi-bot QR fix was confirmed working in live testing â€” the Persian deep link opened the correct member bot with the right khatm preview.

## 2026-09-26 (invite-link QR shows member-bot links)
- **Fix**: The "ðŸ”— QR Ø¯Ø¹ÙˆØª" button in khatm management (`my_khatms.khatm_qr`) generated a QR pointing only at the web landing page (`{public_web_base_url}/join/{token}`) â€” the creator got `api.khatmsaz.com/join/...` and no member-bot links, which was the whole point of the multi-bot split. Now it resolves the khatm's `BotCategory`, builds the per-language member-bot deep links (`t.me/<memberbot>?start=join_{token}` + `ble.ir/...`), lists them all in the caption, and encodes the creator's own language/platform link in the QR. Falls back to the web landing page (or a clear "set up member bots first" message) only when no member bot is configured for the category.
- **Refactor**: Extracted the member-bot link builder into a single shared module `bot/invite_links.py` (`resolve_khatm_category_value`, `build_member_invite_links`, `format_invite_lines`, `pick_primary_link`). Both the creation wizard (`create_khatm.finish_invite_links`) and the QR button now use it, so the two link generators can no longer drift apart. `finish_invite_links` lost its duplicated category-resolution/loop and now uses the canonical `resolve_bot_category`.

## 2026-09-26 (member & creator bot bug fixes)
- **Fix**: `str(BotRole.MEMBER) == "MEMBER"` is always False (a `str, Enum` stringifies to `"BotRole.MEMBER"`), so member bots silently fell through to creator/participant menus and DB-based language. Added `keyboards.is_member_bot(bot)` helper and replaced the broken check in `keyboards.home_keyboard_for_bot`, `navigation.resolve_home_navigation`, `settings_menu` (x2), and `portions._lang_for`.
- **Fix**: `create_khatm.py` invite-link generation called `category_service.get_category` which does not exist (only `get`) â€” AttributeError crashed link generation for every non-Quran (Salawat/Dua/La'an) khatm. Now calls `category_service.get`.
- **Fix**: `member_my_khatms.py` list buttons pointed at dead callbacks â€” `portions:{id}` had no handler, and `leave:{id}` used the wrong prefix and passed a khatm id where `leave_ask:` expects a participation id. Rewrote to `leave_ask:{participation.id}` and a new `mk_portion:{khatm.id}` handler that shows the current portion with the correct action keyboard (wiring back into the shared portions handlers).
- **Fix**: The commitment-consent (`commitment_consent:accept/cancel`) and delivery-hour (`join_hour:` + `AskDeliveryHour` message) handlers lived only in `start.py`, registered on `dp_creator`. On a member bot those callbacks hit no handler, so a member could never finish joining a commitment khatm or set a delivery hour. Extracted them into `bot/handlers/join_flow.py` and registered it on both dispatchers via bootstrap's shared-router list. Updated the two tests that imported these functions.

## 2026-09-26 (member bot UX fix)
- **Fix**: Invite links in khatm creation now use `bot.khatmsaz_username` (fetched at startup) and point to the correct member bots; no more fallback to creator bot.
- **Fix**: All shared handlers now return `member_menu_keyboard` on member bots via `home_keyboard_for_bot` helper â€” creator-only buttons no longer appear in member bot menus.
- **Fix**: `_lang_for` helpers in shared handlers use `bot.khatmsaz_language` instead of DB lookup for member bots.
- **Fix**: Language setting is blocked on member bots (language is fixed per bot).
- **Fix**: `help.py` hides creator/admin topics from member bot users; `create:start_from_help` callback rejects on member bots.
- **Fix**: `show_invite_platform_keyboard` skips platform selection and shows warning immediately when no member bots are configured.

## 2026-09-26 (audit pass)
- **Fix**: Replaced `reload_router`/`sys.modules` hack in `bootstrap.py` with clean `importlib.util` approach for sharing routers across two Dispatchers.
- **Fix**: Updated `test_daily_digest.py` mocks to include `joined_via_bot_instance_id` and accept the `bot_instance_id` kwarg.
- **Fix**: Added missing `@pytest.mark.integration` to `test_create_khatm_survives_phone_verification.py`.

## 2026-09-26
- **Architecture**: Multi-bot 26-bot split â€” `bot_registry` module, `bot_instances` table, Fernet token encryption.
- **Architecture**: `BotRegistry` singleton + dual Dispatchers (`dp_creator`/`dp_member`) in `bootstrap.py`.
- **Feature**: Admin panel `/bots` page for managing 26 bot tokens with 2-step name confirmation.
- **Docs**: Multi-bot architecture documentation in `docs/ai/multibot/` (10 files).

## 2026-09-24
- **Feature**: Creator Mass Broadcasts with media support and pricing logic (free under 3, 43k or 93k depending on audience size).
- **Feature**: Platform restriction (Telegram/Bale/Both) for joining Khatms.
- **Feature**: User support requests now dynamically route to their active Khatm creators.
- **UX**: Cleaned up the main menu and disabled unused settings buttons (font/content).

ï»¿# CHANGELOG

## 2026-10-03
- P9: Delivered final VPS deployment runbook (Runbook for P9). All phases of the new Reminder Redesign are now fully completed.

## 2026-10-03
- P8: Verified comprehensive integrity of portion delivery. The "Today" manual request and background scheduler correctly interlock to guarantee exactly one portion per calendar day per member. Tested concurrency and verified complete isolation of member notifications to member bots.

## 2026-10-03
- P7: Added 2-hour followup reminder for undone portions (Quran and Regular commitments).
- P7: Modified completion callbacks to delete the reminder message instead of just clearing its keyboard, cleaning up the chat while leaving the devotion media intact.

## 2026-09-24
- **UX**: Unified and redesigned the Creator and Admin management panels to use inline parent-child navigation (edit_message_text).
- **Feature**: Added bypass for SMS OTP if a foreign number is shared via Telegram contacts.
- **Feature**: Added instructions in the admin panel on how to manually approve a creator request.
- **Bugfix**: Fixed AttributeError for Khatm.creator_id in suggestions.py.
- **Feature**: Creator Mass Broadcasts with media support and pricing logic.
- **Feature**: Platform restriction (Telegram/Bale/Both) for joining Khatms.
- **Feature**: User support requests now dynamically route to their active Khatm creators.


## 2026-09-24

- **UX**: Auto-start khatm creation wizard on /start or immediately after language selection in src/khatmsaz/bot/handlers/start.py.

Newest entry at the top. One entry per meaningful task, dated.

---

## 2026-09-22 Ã¢â‚¬â€ SMS provider configured (Kavenegar Verify Lookup), PayPing token set, delivery-hour ask extended to OPEN khatms, advertising question removed from wizard

- **SMS: real Kavenegar credentials configured**, but kept as
  `SMS_PROVIDER=noop` in this local `.env` on purpose Ã¢â‚¬â€ flipping it here
  would send real, paid SMS to real numbers on every local test. The
  owner's given API key was hex-encoded; decoded to its real base64-like
  form before storing.
- **New: Kavenegar OTP goes through Verify Lookup, not plain SMS.**
  Iranian carriers require pre-approved patterns for OTP codes Ã¢â‚¬â€ sending
  a raw code as free-text SMS is routinely rejected for compliance. Added
  `SmsProvider.send(..., otp_code=...)` to the protocol; when both an OTP
  code and `SMS_KAVENEGAR_VERIFY_TEMPLATE` (set to the owner's registered
  "verify" pattern) are present, `KavenegarSmsProvider` calls
  `verify/lookup.json` (token + template) instead of `sms/send.json`
  (free text) Ã¢â‚¬â€ falls back to plain send if no template is configured.
  Wired into all 3 real OTP call sites (`change_phone.py` x2,
  `account_link.py`). New tests in `tests/test_sms_provider.py`.
- **PayPing token + callback URL set.** Callback URL corrected to
  `api.khatmsaz.com` (matching support ticket #3122), not `khatmsaz.com`.
- **Real bug fixed:** the "what hour should your daily nudge/portion
  arrive" question only fired for a fresh COMMITMENT portion Ã¢â‚¬â€ an OPEN
  khatm join (e.g. the owner's own new "Ã˜Â¯Ã˜Â¹Ã˜Â§Ã›Å’ Ã˜Â¹Ã™â€¡Ã˜Â¯" khatm) never asked at
  all, even though `_send_open_schedule_reminders` also reads each
  participant's own reminder hour. Now asks for both cases.
  **Still open, flagged rather than guessed:** the owner reported not
  being asked right after *creating* their own OPEN khatm Ã¢â‚¬â€ but creators
  don't automatically become a participant of their own khatm (confirmed
  in `khatm_workflow/service.py`), so this fix (which is join-flow-based)
  doesn't cover that exact moment. Whether creators should auto-join
  their own khatm is a real product decision, not something to guess.
- **Owner request, done:** removed the "Ã™ÂÃ˜Â¹Ã˜Â§Ã™â€ž Ã˜Â¨Ã˜Â´Ã™â€¡Ã˜Å¸" advertising/cash-gift
  question from the create-khatm wizard entirely (defaults to off) Ã¢â‚¬â€ "Ã™â€¦Ã™â€ Ã˜Â·Ã™â€š
  Ã˜Â§Ã˜Â±Ã˜Â³Ã˜Â§Ã™â€ž Ã™Â¾Ã›Å’Ã˜Â§Ã™â€¦ Ã˜ÂªÃ˜Â¨Ã™â€žÃ›Å’Ã˜ÂºÃ˜Â§Ã˜ÂªÃ›Å’ Ã˜Â±Ã™Ë† Ã˜Â§Ã˜Â´Ã˜ÂªÃ˜Â¨Ã˜Â§Ã™â€¡ Ã™ÂÃ™â€¡Ã™â€¦Ã›Å’Ã˜Â¯Ã›Å’Ã˜Å’ Ã˜Â¨Ã˜Â¹Ã˜Â¯Ã˜Â§Ã™â€¹ Ã˜ÂªÃ™Ë†Ã˜Â¶Ã›Å’Ã˜Â­ Ã™â€¦Ã›Å’Ã˜Â¯Ã™â€¦." Also removed
  its now-meaningless summary line from the confirmation screen.
- Full `pytest` (85) + real-Postgres integration (154 total) pass; both
  bots restarted, `/health` OK.

## 2026-09-22 Ã¢â‚¬â€ Multi-reciter audio, multi-page images, and PDF support for devotional content; **critical i18n corruption found and fixed** (381 entries had silently lost their Arabic/English translations)

- **Critical, wide-reaching bug found and fixed:** while adding a new
  translation key, noticed `devotional.audio_caption` had its "ar"/"en"
  values mashed into literal garbled text inside the "fa" string, using
  curly quotes (Ã¢â‚¬Å“ Ã¢â‚¬Â) instead of straight ones. Searched the whole file
  for the same corruption pattern and found **381 more entries** (249
  missing "ar", 132 also missing "en") Ã¢â‚¬â€ likely from a bulk edit earlier
  in this long session that used the wrong quote character. Every one of
  those keys had been silently serving Persian text (with garbage
  embedded) to Arabic and English users this entire time. Fixed with a
  targeted, verified string replacement (not a blind quote swap Ã¢â‚¬â€ only
  the exact corrupted separator sequences were touched, so legitimate
  curly quotes used as real punctuation elsewhere in English example
  text were left alone). Confirmed zero remaining occurrences, full
  `pytest` suite still green.
- **New: multiple reciters per dua/ziyarat.** Owner's original request:
  "Ã˜Â²Ã›Å’Ã˜Â§Ã˜Â±Ã˜Âª Ã˜Â¹Ã˜Â§Ã˜Â´Ã™Ë†Ã˜Â±Ã˜Â§ Ã™â€¦Ã™â€¦ÃšÂ©Ã™â€ Ã™â€¡ Ã˜Â¯Ã™Ë†Ã˜ÂªÃ˜Â§ Ã™â€šÃ˜Â§Ã˜Â±Ã›Å’ Ã™â€¦Ã˜Â®Ã˜ÂªÃ™â€žÃ™Â Ã˜Â¯Ã˜Â§Ã˜Â´Ã˜ÂªÃ™â€¡ Ã˜Â¨Ã˜Â§Ã˜Â´Ã™â€¡." New `devotional_media`
  table (migration `f4a5b6c7d8e9`) replaces the old single audio-slot
  design; `/admin_devotional_audio <slug> [Ã™â€ Ã˜Â§Ã™â€¦ Ã™â€šÃ˜Â§Ã˜Â±Ã›Å’]` now adds one more
  variant instead of overwriting. When a dua has 2+ registered reciters,
  `/devotional <slug>` (and the khatm-participation recitation flow) show
  a "ÃšÂ©Ã˜Â¯Ã™Ë†Ã™â€¦ Ã™â€šÃ˜Â§Ã˜Â±Ã›Å’Ã˜Å¸" picker instead of guessing; 1 reciter still auto-plays,
  0 falls back to the legacy single `audio_ref` column for content
  registered before this table existed.
- **New: multi-page images (pagination).** `/admin_devotional_image
  <slug> [Ã˜Â´Ã™â€¦Ã˜Â§Ã˜Â±Ã™â€¡ Ã˜ÂµÃ™ÂÃ˜Â­Ã™â€¡]` Ã¢â‚¬â€ omit the page number to auto-append after the
  last page, or give an explicit number to insert/replace one page.
- **New: PDF support.** `/admin_devotional_pdf <slug>` Ã¢â‚¬â€ send a PDF as a
  document with that caption; delivered via `answer_document`.
- New test `tests/test_devotional_multi_media.py`.
- Full `pytest` (78) + real-Postgres integration (152 total) pass;
  migration applied; both bots restarted, `/health` OK.

## 2026-09-22 Ã¢â‚¬â€ Devotional channel workflow: voice-note upload bug fixed, image support added; 3 new dua texts registered; local Postgres crash recovered

- **Real bug fixed:** `/admin_devotional_audio` only accepted
  `message.audio`/`message.document` Ã¢â‚¬â€ a Telegram *voice message*
  (`message.voice`, what recording directly in a chat produces) is a
  separate field and was silently rejected with "Ã˜Â¨Ã˜Â§Ã›Å’Ã˜Â¯ Ã™ÂÃ˜Â§Ã›Å’Ã™â€ž Ã˜ÂµÃ™Ë†Ã˜ÂªÃ›Å’ Ã›Å’Ã˜Â§
  document Ã˜Â¶Ã™â€¦Ã›Å’Ã™â€¦Ã™â€¡ ÃšÂ©Ã™â€ Ã›Å’Ã˜Â¯" even though a real audio file was attached. Now
  accepts voice notes too.
- **New: image support for devotional content**, previously entirely
  missing (only text + audio existed). New `image_ref`/`image_platform`
  columns on `devotional_assets` (migration `e3f4a5b6c7d8`), new
  `content_service.register_devotional_image`, new admin command
  `/admin_devotional_image <slug>` (send a photo with that caption), and
  delivery wired into both `/devotional <slug>` and the khatm-participation
  recitation flow (`portions.py::_send_recitation_content`).
- **Registered 3 new dua texts** the owner sent verbatim: Dua Ale-Yasin,
  Dua Ahd, Dua Moshkel Gosha (slugs `dua-ale-yasin`, `dua-ahd`,
  `dua-moshkel-gosha`) Ã¢â‚¬â€ same convention as Ziyarat Ashura (bold Arabic +
  Persian translation, chunked for Telegram's message-length limit).
  `scripts/register_devotional_content_batch2.py`.
- **Local Postgres crashed again overnight** (same recurring
  0x40010004 exception as before, coinciding with the local VPN proxy
  also dropping Ã¢â‚¬â€ likely a laptop sleep/network event, not an app bug) Ã¢â‚¬â€
  restarted the dev-test cluster on port 55433, ran the pending dua
  registration, verified full `pytest` (151) passes, both bots restarted,
  `/health` OK.
- **Not done, flagged for the owner:** true per-dua multiple-reciter
  browsing (e.g. Ziyarat Ashura having two different reciters to choose
  between) needs a real new data model (a devotional asset currently has
  exactly one audio slot, not a list) and a new hierarchical picker UI Ã¢â‚¬â€
  a genuinely separate feature, not attempted this pass to avoid a rushed
  half-implementation at the end of a long session.

## 2026-09-22 Ã¢â‚¬â€ "confused-user" persona pass: hour pickers replace raw 0-23 typing

Owner asked to actually put myself in the shoes of a non-technical user
and walk through the bot's flows to find real friction, not just review
text. Did an objective sweep of the whole `i18n/__init__.py` first
(banned jargon words, blame-toned phrases, over-long sentences) Ã¢â‚¬â€ result
was clean, no violations found (prior sessions' plain-language pass had
already covered this; see BACKLOG.md Ã‚Â§19 for the full method). The real
friction found was interaction-shaped, not text-shaped:

- Two places asked someone to type a raw hour (0Ã¢â‚¬â€œ23, 24-hour clock) with
  no other option: the join-time delivery-hour question (`start.py`) and
  the open-Quran-reading setup wizard (`portions.py`). Confusing/error-
  prone for anyone unsure of 24-hour notation. Added
  `keyboards.py::delivery_hour_keyboard` Ã¢â‚¬â€ six plain-language time-of-day
  buttons (Ã°Å¸Å’â€¦ Ã˜ÂµÃ˜Â¨Ã˜Â­ Ã˜Â²Ã™Ë†Ã˜Â¯ / Ã¢Ëœâ‚¬Ã¯Â¸Â Ã˜ÂµÃ˜Â¨Ã˜Â­ / Ã°Å¸Å’Å¾ Ã˜Â¸Ã™â€¡Ã˜Â± / Ã°Å¸Å’Â¤ Ã˜Â¨Ã˜Â¹Ã˜Â¯Ã˜Â§Ã˜Â²Ã˜Â¸Ã™â€¡Ã˜Â± / Ã°Å¸Å’â€¡ Ã˜ÂºÃ˜Â±Ã™Ë†Ã˜Â¨ / Ã°Å¸Å’â„¢ Ã˜Â´Ã˜Â¨) as
  the primary path in both flows; typing an exact hour still works as a
  fallback for anyone who wants precision. New test
  `tests/test_delivery_hour_button_picker.py`.
- Full `pytest` (77) + real-Postgres integration (151 total) pass; both
  bots restarted, `/health` OK.

## 2026-09-22 Ã¢â‚¬â€ miss notice: 2 consecutive days + phone number for creator; skip_today removed [Claude Code]

**Ã˜ÂªÃ˜ÂµÃ™â€¦Ã›Å’Ã™â€¦ Ã™â€¦Ã˜Â§Ã™â€žÃšÂ© (Ã˜Â¢Ã›Å’Ã˜ÂªÃ™â€¦ Ã›Â±Ã›Âµ BACKLOG):**
- Ã˜Â¯ÃšÂ©Ã™â€¦Ã™â€¡Ã™â€ Ã‚Â«Ã˜Â§Ã™â€¦Ã˜Â±Ã™Ë†Ã˜Â² Ã™â€ Ã™â€¦Ã›Å’Ã¢â‚¬Å’Ã˜Â±Ã˜Â³Ã™â€¦Ã‚Â» Ã˜Â§Ã˜Â² UI Ã˜Â­Ã˜Â°Ã™Â Ã˜Â´Ã˜Â¯ (Ã™â€šÃ˜Â¨Ã™â€žÃ˜Â§Ã™â€¹ no-op Ã˜Â¨Ã™Ë†Ã˜Â¯Ã˜Å’ Ã˜Â­Ã˜Â§Ã™â€žÃ˜Â§ ÃšÂ©Ã˜Â§Ã™â€¦Ã™â€žÃ˜Â§Ã™â€¹ Ã™Â¾Ã˜Â§ÃšÂ©Ã¢â‚¬Å’Ã˜Â³Ã˜Â§Ã˜Â²Ã›Å’ Ã˜Â´Ã˜Â¯)
- Ã˜ÂºÃ›Å’Ã˜Â¨Ã˜Âª Ã›Â² Ã˜Â±Ã™Ë†Ã˜Â² Ã™Â¾Ã˜Â´Ã˜ÂªÃ¢â‚¬Å’Ã˜Â³Ã˜Â±Ã™â€¡Ã™â€¦: Ã˜Â³Ã˜Â§Ã˜Â²Ã™â€ Ã˜Â¯Ã™â€¡ Ã™â€ Ã˜Â§Ã™â€¦ + Ã˜Â´Ã™â€¦Ã˜Â§Ã˜Â±Ã™â€¡ Ã˜ÂªÃ™â€¦Ã˜Â§Ã˜Â³ Ã˜Â¹Ã˜Â¶Ã™Ë† + Ã™Â¾Ã›Å’Ã˜Â§Ã™â€¦ Ã‚Â«Ãšâ€ Ã›Å’ÃšÂ©Ã˜Â§Ã˜Â±Ã˜Â´ ÃšÂ©Ã™â€ Ã›Å’Ã™â€¦Ã˜Å¸Ã‚Â» Ã™â€¦Ã›Å’Ã¢â‚¬Å’ÃšÂ¯Ã›Å’Ã˜Â±Ã˜Â¯

**Ã™ÂÃ˜Â§Ã›Å’Ã™â€žÃ¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã˜ÂªÃ˜ÂºÃ›Å’Ã›Å’Ã˜Â±ÃšÂ©Ã˜Â±Ã˜Â¯Ã™â€¡:**
- `src/khatmsaz/modules/reminder_engine/service.py`
- `src/khatmsaz/modules/khatm/models.py` + `repository.py`
- `src/khatmsaz/modules/khatm_workflow/service.py`
- `migrations/versions/78e35fca4f39_shorten_miss_notice_window.py`
- `tests/test_creator_miss_notice_integration.py`

**150 Ã˜ÂªÃ˜Â³Ã˜Âª Ã™Â¾Ã˜Â§Ã˜Â³Ã˜Å’ migration Ã˜Â§Ã˜Â¬Ã˜Â±Ã˜Â§ Ã˜Â´Ã˜Â¯.**

---

## 2026-09-22 Ã¢â‚¬â€ BACKLOG item 8: today-vs-yesterday for committed quantity khatms [Claude Code]

**Ã™ÂÃ˜Â§Ã›Å’Ã™â€žÃ¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã˜ÂªÃ˜ÂºÃ›Å’Ã›Å’Ã˜Â±ÃšÂ©Ã˜Â±Ã˜Â¯Ã™â€¡:**
- `src/khatmsaz/modules/allocation/models.py` Ã¢â‚¬â€ `CommittedQuantityLog` model
- `src/khatmsaz/modules/allocation/repository.py` Ã¢â‚¬â€ log insert + range query
- `src/khatmsaz/modules/allocation/service.py` Ã¢â‚¬â€ auto-log on progress record + `today_vs_yesterday_committed`
- `src/khatmsaz/bot/handlers/portions.py` Ã¢â‚¬â€ Ã™â€ Ã™â€¦Ã˜Â§Ã›Å’Ã˜Â´ Ã˜Â§Ã™â€¦Ã˜Â±Ã™Ë†Ã˜Â²/Ã˜Â¯Ã›Å’Ã˜Â±Ã™Ë†Ã˜Â² Ã˜Â¯Ã˜Â± Ã™Â¾Ã˜Â§Ã˜Â³Ã˜Â® Ã˜ÂªÃ˜Â¹Ã™â€¡Ã˜Â¯Ã›Å’
- `migrations/versions/c8e057163033_add_committed_quantity_logs.py` Ã¢â‚¬â€ migration
- `tests/test_committed_today_vs_yesterday_integration.py` Ã¢â‚¬â€ Ã˜ÂªÃ˜Â³Ã˜Âª

**149 Ã˜ÂªÃ˜Â³Ã˜Âª Ã™Â¾Ã˜Â§Ã˜Â³Ã˜Å’ migration Ã˜Â§Ã˜Â¬Ã˜Â±Ã˜Â§ Ã˜Â´Ã˜Â¯.**

---

## 2026-09-22 Ã¢â‚¬â€ delivery-hour question extended to ALL committed khatm types [Claude Code]

**Ã™ÂÃ˜Â§Ã›Å’Ã™â€žÃ¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã˜ÂªÃ˜ÂºÃ›Å’Ã›Å’Ã˜Â±ÃšÂ©Ã˜Â±Ã˜Â¯Ã™â€¡:**
- `src/khatmsaz/bot/handlers/start.py` Ã¢â‚¬â€ Ã˜Â´Ã˜Â±Ã˜Â· `unit_kind == POSITIONAL` Ã˜Â§Ã˜Â²
  trigger Ã™Â¾Ã˜Â±Ã˜Â³Ã˜Â´ Ã˜Â³Ã˜Â§Ã˜Â¹Ã˜Âª Ã˜ÂªÃ˜Â­Ã™Ë†Ã›Å’Ã™â€ž Ã˜Â­Ã˜Â°Ã™Â Ã˜Â´Ã˜Â¯Ã˜â€º Ã˜Â­Ã˜Â§Ã™â€žÃ˜Â§ Ã˜Â¨Ã˜Â±Ã˜Â§Ã›Å’ Ã™â€¡Ã™â€¦Ã™â€¡Ã™â€ Ã˜Â®Ã˜ÂªÃ™â€¦Ã¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã˜ÂªÃ˜Â¹Ã™â€¡Ã˜Â¯Ã›Å’ (Ã™â€šÃ˜Â±Ã˜Â¢Ã™â€  +
  Ã˜ÂµÃ™â€žÃ™Ë†Ã˜Â§Ã˜Âª + Ã˜Â¯Ã˜Â¹Ã˜Â§ + Ã™â€žÃ˜Â¹Ã™â€ ) Ã™Â¾Ã˜Â±Ã˜Â³Ã›Å’Ã˜Â¯Ã™â€¡ Ã™â€¦Ã›Å’Ã¢â‚¬Å’Ã˜Â´Ã™â€¡
- `tests/test_join_delivery_hour_ask_integration.py` Ã¢â‚¬â€ Ã˜ÂªÃ˜Â³Ã˜Âª Ã˜Â¬Ã˜Â¯Ã›Å’Ã˜Â¯ Ã˜Â¨Ã˜Â±Ã˜Â§Ã›Å’ Ã˜ÂµÃ™â€žÃ™Ë†Ã˜Â§Ã˜Âª

**148 Ã˜ÂªÃ˜Â³Ã˜Âª Ã™Â¾Ã˜Â§Ã˜Â³.**

---

## 2026-09-22 Ã¢â‚¬â€ start.py join-flow fully i18n'd; creator_web_login DB-before-HTTPS-check bug fixed; test isolation regression fixed [Claude Code]

**Ã™ÂÃ˜Â§Ã›Å’Ã™â€žÃ¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã˜ÂªÃ˜ÂºÃ›Å’Ã›Å’Ã˜Â±ÃšÂ©Ã˜Â±Ã˜Â¯Ã™â€¡:**
- `src/khatmsaz/bot/handlers/start.py` Ã¢â‚¬â€ Ã™â€¡Ã™â€¦Ã™â€¡Ã™â€ Ã˜Â±Ã˜Â´Ã˜ÂªÃ™â€¡Ã¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã™â€¡Ã˜Â§Ã˜Â±Ã˜Â¯ÃšÂ©Ã˜Â¯ join-flow (Ã˜Â®Ã˜Â·Ã˜Â§Ã™â€¡Ã˜Â§Ã›Å’
  Ã™â€žÃ›Å’Ã™â€ ÃšÂ© Ã˜Â¯Ã˜Â¹Ã™Ë†Ã˜ÂªÃ˜Å’ Ã˜Â®Ã˜ÂªÃ™â€¦ Ã˜Â­Ã˜Â°Ã™ÂÃ¢â‚¬Å’Ã˜Â´Ã˜Â¯Ã™â€¡/Ã˜ÂªÃ™â€¦Ã™Ë†Ã™â€¦Ã¢â‚¬Å’Ã˜Â´Ã˜Â¯Ã™â€¡/Ã˜Â¹Ã˜Â¶Ã™Ë†Ã™â€šÃ˜Â¨Ã™â€žÃ›Å’Ã˜Å’ Ã˜ÂªÃ˜Â¹Ã™â€¡Ã˜Â¯Ã˜Å’ ÃšÂ©Ã™Â¾Ã˜Â´Ã™â€  ÃšÂ©Ã˜Â§Ã™Ë†Ã˜Â±Ã˜Å’ Ã˜Â®Ã˜ÂµÃ™Ë†Ã˜ÂµÃ›Å’Ã˜Å’ Ã™â€žÃ˜ÂºÃ™Ë†)
  Ã˜Â¨Ã˜Â§ `t()` Ã™Ë† ÃšÂ©Ã™â€žÃ›Å’Ã˜Â¯Ã™â€¡Ã˜Â§Ã›Å’ Ã˜Â¬Ã˜Â¯Ã›Å’Ã˜Â¯ `join.*` Ã˜Â¬Ã˜Â§Ã›Å’ÃšÂ¯Ã˜Â²Ã›Å’Ã™â€  Ã˜Â´Ã˜Â¯Ã™â€ Ã˜â€º `_request_private_join`
  Ã™Â¾Ã˜Â§Ã˜Â±Ã˜Â§Ã™â€¦Ã˜ÂªÃ˜Â± `lang` ÃšÂ¯Ã˜Â±Ã™ÂÃ˜ÂªÃ˜â€º `cancel_commitment` Ã˜Â§Ã˜Â² DB Ã˜Â²Ã˜Â¨Ã˜Â§Ã™â€  Ã™â€¦Ã›Å’Ã¢â‚¬Å’ÃšÂ¯Ã›Å’Ã˜Â±Ã™â€¡
- `src/khatmsaz/bot/handlers/my_khatms.py` Ã¢â‚¬â€ Ãšâ€ ÃšÂ© HTTPS Ã˜Â¨Ã™â€¡ Ã™Â¾Ã›Å’Ã˜Â´ Ã˜Â§Ã˜Â² `_lang_for`
  Ã™â€¦Ã™â€ Ã˜ÂªÃ™â€šÃ™â€ž Ã˜Â´Ã˜Â¯ Ã˜ÂªÃ˜Â§ Ã˜Â¯Ã˜Â± Ã™â€¦Ã˜Â³Ã›Å’Ã˜Â± reject Ã˜Â¨Ã™â€¡ DB Ã™Ë†Ã˜ÂµÃ™â€ž Ã™â€ Ã˜Â´Ã™â€¡
- `src/khatmsaz/i18n/__init__.py` Ã¢â‚¬â€ Ã›Â±Ã›Â± ÃšÂ©Ã™â€žÃ›Å’Ã˜Â¯ Ã˜Â¬Ã˜Â¯Ã›Å’Ã˜Â¯ `join.error.*`,
  `join.cancelled`, `join.commitment_*`, `join.private_request_sent`,
  `join.cover_caption`
- `docs/ai/I18N_MIGRATION.md` Ã¢â‚¬â€ `start.py` Ã™Ë† `my_khatms.py` Ã™â€¡Ã˜Â± Ã˜Â¯Ã™Ë† `[x]` Ã˜Â´Ã˜Â¯Ã™â€ 

**Ã˜ÂªÃ˜Â³Ã˜Âª:** Ã›Â¶Ã›Â¸ unit + Ã›Â±Ã›Â´Ã›Â· integration Ã™â€¡Ã™â€¦Ã™â€¡ Ã™Â¾Ã˜Â§Ã˜Â³.

---

## 2026-09-22 Ã¢â‚¬â€ Bale join link is now a real clickable link; Telegram registration no longer accepts a typed phone number

- Owner-reported bug: the Bale invite in the "khatm created" message was
  raw text telling the recipient to manually type `/start join_<token>`
  into Bale Ã¢â‚¬â€ error-prone, not an actual link, and reported broken in
  practice. Fixed to build a real `https://ble.ir/<username>?start=join_<token>`
  clickable link, matching the format `portions.py::_invite_friends_line`
  already assumes elsewhere in this codebase (so this is now consistent,
  not a new unconfirmed guess). New test
  `tests/test_bale_invite_link_is_clickable.py`.
- Owner clarification on the phone-share ambiguity from earlier tonight:
  during **initial registration on Telegram**, only the "share my number"
  button should work Ã¢â‚¬â€ typing a number manually is no longer accepted
  there (Bale has no button-share equivalent, so Bale still allows
  typing). New i18n keys `registration.ask_phone_share_only` /
  `registration.use_share_button_only`. New test
  `tests/test_registration_phone_share_only.py`. (Scoped only to the
  initial-registration step Ã¢â‚¬â€ `change_phone.py`'s manual phone-change
  flow is a different, deliberately-typed context and is untouched.)
- Full `pytest` (74) + real-Postgres integration (147 total) pass; both
  bots restarted, `/health` OK.

## 2026-09-22 Ã¢â‚¬â€ Bale bot activated; real bug fixed: creating a khatm no longer restarts from scratch if phone/profile verification is needed mid-way

- **Bale bot activated.** New token + username set in `.env`; Bale is now
  running alongside Telegram (confirmed live in logs: both bots polling).
  Super-admin auto-promotion (`identity/service.py`) was Telegram-only Ã¢â‚¬â€
  extended to also check a new `SUPER_ADMIN_BALE_CHAT_IDS` env var
  (`config.py`), set to the owner's given Bale id, so the same
  first-admin bootstrap mechanism now works on Bale too.
- **Real, high-impact bug fixed (owner-reported):** a first-time creator
  whose phone wasn't verified yet lost their *entire* create-khatm wizard
  the moment they tapped confirm Ã¢â‚¬â€ `confirm_wizard` used to just clear the
  state and tell them to run `/verify_phone` and start over from scratch.
  Now it kicks off the same phone-verification (or profile-completion,
  if that's what's missing first) flow while keeping every answer the
  wizard already collected, and once verification succeeds, the khatm
  actually gets created immediately with those preserved answers Ã¢â‚¬â€ no
  restart. New `create_khatm.py::resume_khatm_creation_if_pending`,
  wired into both `change_phone.py`'s OTP-success handler and
  `profile.py`'s profile-completion handler (both previously just showed
  a generic "done" message and dropped back to the main menu,
  discarding any in-progress wizard). New end-to-end test
  `tests/test_create_khatm_survives_phone_verification.py` Ã¢â‚¬â€ actually
  drives a wizard into the unverified-phone case, extracts the dev-mode
  OTP code, enters it, and confirms the khatm was created with the
  original title/type.
- **New system-settings admin feature** (owner request: "Ã™â€¡Ã™â€¦Ã™â€¡ Ãšâ€ Ã›Å’Ã˜Â²
  Ã˜Â¯Ã˜Â§Ã›Å’Ã™â€ Ã˜Â§Ã™â€¦Ã›Å’ÃšÂ© Ã˜Â¨Ã˜Â§Ã˜Â´Ã™â€¡"): generic `system_settings` key/value table (migration
  `d2e3f4a5b6c7`) + `/admin_settings` / `/admin_setting_set` commands.
  First two real values wired in: `default_reminder_hour` and
  `inactivity_days` in `reminder_engine.service`, previously hardcoded
  Python constants Ã¢â‚¬â€ now live-editable without a deploy.
- **Ã¢Å¡Â Ã¯Â¸Â Flagged, not guessed at:** the owner also described a phone-share
  reply-keyboard issue in Telegram ("ÃšÂ©Ã›Å’Ã˜Â¨Ã™Ë†Ã˜Â±Ã˜Â¯ Ã˜Â¨Ã˜Â³Ã˜ÂªÃ™â€¡ Ã˜Â¨Ã˜Â´Ã™â€¡ Ã˜ÂªÃ˜Â§ Ã˜Â¯ÃšÂ©Ã™â€¦Ã™â€¡ Ã˜Â´Ã›Å’Ã˜Â± Ã˜Â¨Ã›Å’Ã˜Â§Ã˜Â¯") Ã¢â‚¬â€
  the phrasing was ambiguous enough (possible dictation artifact) that
  guessing at a fix risked solving the wrong problem. Needs a follow-up
  screenshot or clearer description before touching `registration.py`'s
  `_phone_keyboard`.
- Full `pytest` (72) + real-Postgres integration (144 total) pass;
  `alembic upgrade head` applied; both bots restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Salawat no longer asks for custom text (La'an-only now); categoryÃ¢â€ â€™devotional content link is now explicit and admin-editable

- Owner-reported bug: "Ã˜Â¨Ã˜Â±Ã˜Â§Ã›Å’ Ã˜ÂµÃ™â€žÃ™Ë†Ã˜Â§Ã˜Âª Ã™â€ Ã˜Â¨Ã˜Â§Ã›Å’Ã˜Â¯ Ã™â€¦Ã˜ÂªÃ™â€  Ã˜Â±Ã™Ë† Ã˜Â§Ã˜Â² Ã›Å’Ã™Ë†Ã˜Â²Ã˜Â± Ã˜Â¨Ã˜Â®Ã™Ë†Ã˜Â§Ã˜Â¯Ã˜â€º Ã™â€¦Ã˜ÂªÃ™â€  Ã˜ÂµÃ™â€žÃ™Ë†Ã˜Â§Ã˜Âª
  Ã™â€¡Ã™â€¦Ã›Å’Ã˜Â´Ã™â€¡ Ã˜Â«Ã˜Â§Ã˜Â¨Ã˜ÂªÃ™â€¡ Ã¢â‚¬â€ Ã˜Â§Ã›Å’Ã™â€  Ã™ÂÃ™â€šÃ˜Â· Ã˜Â¨Ã˜Â§Ã›Å’Ã˜Â¯ Ã˜Â¨Ã˜Â±Ã˜Â§Ã›Å’ Ã™â€žÃ˜Â¹Ã™â€  Ã˜Â¨Ã˜Â§Ã˜Â´Ã™â€¡." The creator-authored-text
  step in the create-khatm wizard fired for every Salawat-template khatm
  (plain Salawat, Dua, *and* La'an) when it should only ever fire for
  La'an Ã¢â‚¬â€ Salawat wording is fixed/standard, Dua text comes from the
  admin-managed devotional library. Fixed the condition in
  `bot/handlers/create_khatm.py::_after_welcome` to check
  `category_group == LAAN` instead of just the SALAWAT template type;
  reworded `create_khatm.ask_recitation_text` to say "Ã™â€žÃ˜Â¹Ã™â€ " explicitly.
- **BACKLOG.md Ã‚Â§14 follow-up, done:** replaced the fragile name-matching
  hack (checking if "Ã˜Â¹Ã˜Â§Ã˜Â´Ã™Ë†Ã˜Â±Ã˜Â§" appeared in a category's title to guess
  which devotional-library text to send) with a real, explicit
  `KhatmCategory.devotional_slug` column Ã¢â‚¬â€ admin-editable from the
  categories web panel (new migration `c1d2e3f4a5b6`). The old
  name-matching is kept only as a fallback for categories an admin
  hasn't linked yet, so nothing that worked before silently breaks.
- New tests: `tests/test_recitation_text_only_for_laan.py`,
  `tests/test_category_devotional_slug_link.py`.
- **Admin-panel dynamism audit (owner asked: "Ã™â€¡Ã™â€¦Ã™â€¡ Ãšâ€ Ã›Å’Ã˜Â² Ã™â€šÃ˜Â§Ã˜Â¨Ã™â€ž ÃšÂ©Ã™â€ Ã˜ÂªÃ˜Â±Ã™â€ž Ã™Ë†
  Ã™Ë†Ã›Å’Ã˜Â±Ã˜Â§Ã›Å’Ã˜Â´ Ã˜Â¨Ã˜Â§Ã˜Â´Ã™â€¡Ã˜Å’ Ã˜Â¯Ã˜Â§Ã›Å’Ã™â€ Ã˜Â§Ã™â€¦Ã›Å’ÃšÂ© Ã˜Â¨Ã˜Â§Ã˜Â´Ã™â€¡"):** researched what's already
  admin-editable vs. hardcoded across the whole panel. Already dynamic
  and broader than expected: pricing/plans, SMS plans, coupons, message
  templates, roles, devotional categories (now including this slug
  link), Quran cover approvals, Quran source-channel seeding. Confirmed
  hardcoded-in-Python items that would need real (migration-sized) work
  to make dynamic: the reciter whitelist (`SYSTEM_RECITERS`), Quran
  edition list, and the `KhatmCategoryGroup` enum (SALAWAT/LAAN/DUA count
  fixed at 3 Ã¢â‚¬â€ extending it needs a DB enum migration, not just an admin
  toggle). No global system-settings key/value table exists yet for
  tuning small numeric defaults (reminder hour, inactivity days) without
  a migration each time Ã¢â‚¬â€ flagged as the highest-leverage next step if
  more "make this a number I can change" requests come in.
- Full `pytest` (70) + real-Postgres integration (143 total) pass;
  `alembic upgrade head` applied cleanly; bot restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Fixed: picking a reciter never actually turned audio on

- Owner-reported bug: "Ã™â€šÃ˜Â§Ã˜Â±Ã›Å’ Ã˜Â±Ã™Ë† Ã™ÂÃ˜Â¹Ã˜Â§Ã™â€ž Ã™â€¦Ã›Å’ÃšÂ©Ã™â€ Ã™â€¦ Ã˜Â§Ã™â€¦Ã˜Â§ Ã˜ÂµÃ™Ë†Ã˜Âª Ã˜Â§Ã˜Â±Ã˜Â³Ã˜Â§Ã™â€ž Ã™â€ Ã™â€¦Ã›Å’Ã˜Â´Ã™â€¡." Root
  cause: `UserSettings.quran_audio_enabled` is a separate flag (defaults
  to `False`, lives on a different settings screen) that picking a
  reciter Ã¢â‚¬â€ via either the Ã¢Å¡â„¢Ã¯Â¸Â Ã˜ÂªÃ™â€ Ã˜Â¸Ã›Å’Ã™â€¦Ã˜Â§Ã˜Âª inline menu or the typed `/reciter`
  command Ã¢â‚¬â€ never touched. So no matter which reciter someone picked,
  `content_service.resolve_current_quran_delivery` kept skipping audio
  because the unrelated flag was still off. Fixed both entry points
  (`settings_menu.py::set_reciter`, `reciter_settings.py::set_reciter`) to
  turn audio on when a reciter is picked, matching the obvious intent.
- New tests: `tests/test_reciter_activates_audio_integration.py` (both
  entry points).
- **Real end-to-end verification, not just unit tests (owner asked to
  actually go check audio comes through):** found `quran_page_assets` was
  completely empty *again* (0 rows) Ã¢â‚¬â€ almost certainly fallout from
  tonight's Postgres crash/WAL-recovery. Re-ran the idempotent seed (604
  images + 604 audio restored, no risk of duplicates). Then ran a real
  script through the actual production code path Ã¢â‚¬â€ created a live Quran
  khatm with the real boundary-aligned allocator, called the real
  `settings_menu.py::set_reciter` handler, then called the real
  `notify_adapter.build_send_quran_pages_fn` (the function the reminder
  engine actually uses to push content) against a fake bot capturing
  calls. Result: first portion resolved to pages 1-3 (matches the earlier
  audio-boundary fix) and exactly 3 real Telegram `forward_message` calls
  went out Ã¢â‚¬â€ 2 for images (pages 1 and 2 correctly deduped into one
  shared image forward, page 3 as its own) and exactly 1 for audio
  (the combined 1-3 recording, deduped from 3 page-rows into 1 send) Ã¢â‚¬â€
  proving both the reciter/audio-toggle fix and the audio-boundary fix
  from earlier tonight work correctly together against real seeded data,
  not just in isolation.
- **Self-heal added so this can't silently recur unnoticed:** since
  `quran_page_assets` has now emptied twice this session after unrelated
  Postgres crashes, `bootstrap.py::main` now re-runs the idempotent
  `seed_verified_quran_channel_map` on every single startup (a few seconds
  of one-time cost, logs the result, never blocks startup on failure) Ã¢â‚¬â€
  confirmed live: fresh restart logged
  `Quran channel map self-heal check: {'ready': True, ...}`.
- Full `pytest` (67) + real-Postgres integration (139 total) pass; bot
  restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Committed Quran members now get their hour asked at join + content auto-pushed daily; local Postgres crash recovered; bot wrapped in an auto-restart watchdog

- Owner request: every committed member should be asked what hour to
  receive their daily portion, right at join time (not left to silently
  default to hour 9) Ã¢â‚¬â€ new `AskDeliveryHour` FSM step in
  `bot/handlers/start.py::resume_join_after_registration`, fires once for
  a fresh QURAN_PAGE COMMITMENT join with a real first portion assigned.
- Owner request ("Ã˜Â³Ã™â€¡Ã™â€¦ Ã˜Â§Ã™â€¦Ã˜Â±Ã™Ë†Ã˜Â² Ã˜Â¨Ã˜Â§Ã›Å’Ã˜Â¯ Ã˜Â§Ã˜ÂªÃ™Ë†Ã™â€¦Ã˜Â§Ã˜Âª Ã˜Â¨Ã˜Â§Ã˜Â´Ã™â€¡Ã˜Å’ Ã˜Â¯ÃšÂ©Ã™â€¦Ã™â€¡ Ã™â€ Ã˜Â¯Ã˜Â§Ã˜Â´Ã˜ÂªÃ™â€¡ Ã˜Â¨Ã˜Â§Ã˜Â´Ã™â€¡"): a
  committed Quran participant's daily portion content (image/audio/text)
  is now auto-pushed alongside the reminder text Ã¢â‚¬â€ both the first-portion
  daily digest and every later day's `deliver_due_next_portions` Ã¢â‚¬â€ reusing
  the same `send_quran_pages` mechanism already built for open-Quran
  readers (BACKLOG.md Ã‚Â§24). New `reminder_engine.service._push_portion_content`
  helper, best-effort (a delivery failure never blocks the reminder text).
- Found and fixed two more stale occurrences of the removed backup-reader
  wording ("Ã˜Â³Ã™â€¡Ã™â€¦ Ã˜Â±Ã˜Â§ Ã˜Â¨Ã™â€¡ Ã›Å’ÃšÂ©Ã›Å’ Ã˜Â§Ã˜Â² Ã˜Â¯Ã™Ë†Ã˜Â³Ã˜ÂªÃ˜Â§Ã™â€  Ã˜Â¨Ã˜Â³Ã™Â¾Ã˜Â§Ã˜Â±Ã›Å’Ã˜Â¯") in `reminder_engine.service`'s
  default reminder text Ã¢â‚¬â€ missed in the earlier sweep since they live in a
  different function than the ones already fixed.
- New tests: `tests/test_committed_quran_auto_content_push_integration.py`,
  `tests/test_join_delivery_hour_ask_integration.py`.
- **Infra, not code Ã¢â‚¬â€ real production risk found and fixed:** the local
  dev/test Postgres cluster (port 55433) crashed mid-session (an OS-level
  client-backend termination, unrelated to any code change) and the bot
  process died with it. Both recovered (`pg_ctl start`, WAL replayed
  cleanly, no data loss). Since the owner was going offline for the night,
  the bot is now run under a small restart-loop watchdog script instead of
  a bare background process, so a future crash self-heals without needing
  anyone awake to restart it.
- Documented a GitHub-based deployment alternative (owner's own
  private repo Ã¢â€ â€™ server `git clone`/`git pull`) in `Rahnama.VPS.txt`
  (new Ã‚Â§8-Ã˜Â¨), alongside the existing SCP-based method Ã¢â‚¬â€ `.env` was
  already correctly excluded via `.gitignore`.
- Full `pytest` (65) + real-Postgres integration (137 total) pass; bot
  restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Restored creator-only miss notification (owner reversed part of the earlier removal after being asked to confirm)

- Owner was asked directly whether "nobody gets notified on a miss"
  (decided earlier today) should stand, given a new request implied the
  opposite. They confirmed: creator should be notified after repeated
  misses. Implemented narrowly: participant is still never notified and
  their portion is still never released to anyone else Ã¢â‚¬â€ only the
  creator gets an informational message once a member crosses the
  khatm's own miss threshold/window (fields already existed, no
  migration). New `reminder_engine.service._maybe_record_miss_and_notify_creator`.
- New test `tests/test_creator_miss_notice_integration.py`. Full `pytest`
  (64) + real-Postgres integration (135 total) pass; bot restarted,
  `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Fixed real UX bugs from owner screenshots: language-leaking buttons, wrong post-completion keyboard, stale consent text

- `contribute_keyboard`/`commitment_quantity_keyboard` (`bot/keyboards.py`)
  had hardcoded Persian button text with no `lang` param Ã¢â‚¬â€ an English-mode
  user got an all-English message with a Persian "Ã˜Â«Ã˜Â¨Ã˜Âª Ã™â€¦Ã˜Â´Ã˜Â§Ã˜Â±ÃšÂ©Ã˜Âª" button.
  Fixed: both now take `lang` and use `t()`; all call sites
  (`portions.py`, `start.py`) updated.
- Real UX bug (owner screenshot): after tapping "Ã¢Å“â€¦ Ã˜Â§Ã™â€ Ã˜Â¬Ã˜Â§Ã™â€¦ Ã˜Â¯Ã˜Â§Ã˜Â¯Ã™â€¦", the
  confirmation message still showed "Ã°Å¸â€œâ€“ Ã™â€ Ã™â€¦Ã˜Â§Ã›Å’Ã˜Â´ Ã™â€¦Ã˜Â­Ã˜ÂªÃ™Ë†Ã˜Â§Ã›Å’ Ã˜Â³Ã™â€¡Ã™â€¦" and "Ã¢Å“â€¦ Ã˜Â§Ã™â€ Ã˜Â¬Ã˜Â§Ã™â€¦
  Ã˜Â¯Ã˜Â§Ã˜Â¯Ã™â€¦" again Ã¢â‚¬â€ buttons for a portion that was already just completed.
  Split `portion_done_keyboard` (for a still-pending portion Ã¢â‚¬â€ content +
  done + snooze) from a new `post_completion_keyboard` (snooze + undo
  only) and switched `mark_portion_done`'s three response branches to the
  latter. Also translated both keyboards' labels (were hardcoded Persian).
- Fixed stale wording in the commitment join-consent prompt
  (`start.py::resume_join_after_registration`) Ã¢â‚¬â€ it still said "if I
  can't, I'll let people know early so the portion doesn't fall behind,"
  describing the now-removed backup-reader mechanism. Reworded to be
  responsibility-framed instead (BACKLOG.md Ã‚Â§14): missing your portion
  can hold back the whole khatm and everyone else's progress.
- Full `pytest` (63) + real-Postgres integration (134 total) pass; bot
  restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Open/waitlisted Quran readers now actually receive real page content (BACKLOG.md Ã‚Â§24)

- Root cause: OPEN Quran khatms (and waitlisted, non-committed members of
  a COMMITMENT Quran khatm) only ever logged a bare contribution number Ã¢â‚¬â€
  real page delivery required a `KhatmPortion`, which only exists for
  committed participants. Confirmed via full trace before writing any code.
- New migration (`r9s0t1u2v3w4`): 3 columns on `khatm_participations`
  (`open_reading_pages_per_day`, `open_reading_next_page`,
  `open_reading_last_sent_at`).
- First "Ã˜Â«Ã˜Â¨Ã˜Âª Ã™â€¦Ã˜Â´Ã˜Â§Ã˜Â±ÃšÂ©Ã˜Âª" tap for a non-committed Quran participant now asks
  pages/day + delivery hour, then immediately sends that day's real pages;
  subsequent manual logging also delivers real content, not just a number.
- New `reminder_engine.service.deliver_due_open_quran_reading` (wired into
  the existing 30-min scan) auto-sends the daily batch at the reader's
  chosen hour, once per local day, and stops at the edition's last page.
- New `bot/notify_adapter.py::build_send_quran_pages_fn` for actual
  photo/audio delivery from the platform-agnostic reminder engine.
- New test `tests/test_open_quran_reading_integration.py`. Full `pytest`
  (63) + real-Postgres integration (134 total) pass; migration applied;
  bot restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ my_khatms.py creator commands fully translated + tone-guide pass; fixed a real NameError bug

- Translated every remaining Persian-only string in `bot/handlers/my_khatms.py`
  (all `/khatm_*` typed commands + the `cs:*` inline settings tree) to
  fa/ar/en, ~90 new `my_khatms.creator.*` i18n keys, written against
  `docs/ai/TONE_GUIDE_80YO_PERSONA.md`'s checklist (BACKLOG.md Ã‚Â§19/Ã‚Â§3).
- Fixed a real bug: `khatm_stats`'s phone-not-verified branch referenced
  an undefined `callback` variable Ã¢â‚¬â€ would have raised `NameError` for
  any creator with an unverified phone running `/khatm_stats`.
- Removed `/khatm_skip_today` and `/khatm_miss_policy` outright (not
  translated) Ã¢â‚¬â€ both configured features already removed from the UI in
  today's earlier emergency-portion-removal pass, so they no longer did
  anything visible.
- Full `pytest` (63, one assertion updated for new tone-compliant copy) +
  real-Postgres integration (133 total) pass; bot restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ "Ã˜Â®Ã˜ÂªÃ™â€¦Ã¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã™â€¦Ã™â€ " redesigned as a hierarchical menu (BACKLOG.md Ã‚Â§18)

- Replaced the single long text list with a 3-level navigable menu:
  created/joined/finished Ã¢â€ â€™ content type (Quran/Salawat/Dua/La'an) Ã¢â€ â€™
  individual khatms with their existing action buttons. No FSM state Ã¢â‚¬â€
  each navigation tap (`mk:root`/`mk:b:*`/`mk:c:*`) re-reads from the DB
  and edits the same message in place.
- New `_build_my_khatms_tree`/`_render_my_khatms_{root,branch,category}`
  in `bot/handlers/my_khatms.py`; grouping uses `Khatm.template_type` +
  `KhatmCategory.group` (`content_category_id`).
- New test `tests/test_my_khatms_hierarchy_integration.py` against real
  Postgres (creator + member, spanning Quran/Salawat/Dua). Admin web
  panel intentionally stays Persian-only Ã¢â‚¬â€ the admin's own language
  choice, per the owner.
- Full `pytest` (63) + real-Postgres integration (133 total) pass; bot
  restarted, `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Removed emergency-portion/backup-reader system; one Quran portion per day

- Owner decision: remove the entire emergency-portion/backup-reader
  concept Ã¢â‚¬â€ a missed portion no longer notifies anyone or gets released to
  a shared pool; the same member simply gets it later. Removed the
  `emergency:`/`backup_toggle:`/`skip_today:` callbacks, their keyboards,
  `reminder_engine.service._maybe_send_miss_notice`, and reduced
  `/khatm_decision` to a short "no longer available" stub. Cleaned up
  ~15 now-dead i18n keys this left behind.
- Implemented "one Quran portion per day": completing a portion no longer
  auto-advances to the next one; a new `reminder_engine.deliver_due_next_portions`
  hands out the next portion once a full day has passed in the member's
  own timezone, at their existing `/reminder` hour. New integration test
  `tests/test_one_portion_per_day_integration.py`.
- Fixed two now-stale strings that still described the removed mechanism
  as reassuring ("someone else will cover it") Ã¢â‚¬â€ rewritten to be
  responsibility-framed instead (BACKLOG.md Ã‚Â§14), since they were now
  simply false.
- Found and fixed an unrelated, pre-existing operational bug: two
  independent bot processes were both polling Telegram at once (real
  double-handling risk) Ã¢â‚¬â€ killed both, started one clean instance.
- Full `pytest` (62) + real-Postgres integration (70) pass; bot restarted,
  `/health` OK.

## 2026-09-21 Ã¢â‚¬â€ Fixed Quran portion/audio boundary mismatch (real, wide bug)

- Root-caused and fixed a real bug where most Quran-commitment portions
  (300 of 302, not just the reported "pages 7-8") got two different audio
  messages, because portion boundaries (uniform 2-per-portion from page 1)
  didn't match the real reciter's audio-segment boundaries (1-3, then
  4-5, 6-7, ...). Added `allocation_service.generate_quran_page_plan_from_boundaries`
  and used it for the canonical 604-page edition only.
- Found and fixed an unrelated incident: `quran_page_assets` was empty
  (stale local Postgres snapshot); re-ran the idempotent seed.
- Fixed two integration tests broken by an earlier `_creator()` i18n
  change (new UserSettings side effect not accounted for in teardown).
- Investigated the "add devotional audio without code" request: already
  fully supported via `/admin_devotional_text` + `/admin_devotional_audio
  <slug>` caption command; no new feature needed.
- Flagged "one Quran portion per day" as not yet built Ã¢â‚¬â€ needs an owner
  decision before touching a core, heavily-used subsystem (see BACKLOG Ã‚Â§23).
- Verified with full pytest + full real-Postgres integration suite (both
  before and after each change), multiple real-Postgres verification
  scripts, and a bot restart + `/health` check. (Claude Code)

## 2026-09-21 Ã¢â‚¬â€ Devotional content delivery + suggestions inbox

- Registered the owner-supplied Ziyarat Ashura (bold Arabic + Persian
  translation, chunked) and Salawat text into `devotional_assets` via
  `scripts/register_devotional_content.py`.
- Fixed `devotional.py`: it was HTML-escaping `text_body`, which silently
  broke all bold formatting; now sends trusted-HTML chunks split on `\x1e`.
- Added an optional creator-authored recitation-text wizard step for
  SALAWAT-family khatms (stored in the pre-existing `Khatm.description`
  column, no migration); wired delivery into `portions.py` after each
  contribution Ã¢â‚¬â€ custom text if set, else a devotional-library fallback
  matched by category title (stopgap; needs a real `devotional_slug` FK
  later, see BACKLOG Ã‚Â§14).
- Added a suggestions/bug-report inbox (`suggestions.py`): a Help-menu
  button that records feedback in `audit_logs` and pushes it live to all
  Super Admin chats.
- Verified with full pytest suite (updated `test_help.py`'s callback-set
  assertion), real-Postgres delivery-path checks, chunk-size verification,
  import smoke-tests, and a bot restart + `/health` check after each
  change. (Claude Code)

## 2026-09-21 Ã¢â‚¬â€ Creator Mini App panel localized; go-live readiness confirmed

- Localized the creator-facing web/Mini-App templates (`creator_base.html`,
  `creator_dashboard.html`, `creator_khatm_detail.html`, `creator_login.html`)
  to `t(key, lang)`; added ~60 fa/ar/en keys under `web.*`. Admin-only pages
  intentionally left Persian, same reasoning as `admin.py`.
- Confirmed via `.env` inspection and a real-Postgres end-to-end script
  that core flows (register, phone verify, create khatm, join, contribute)
  already work today without PayPing or Kavenegar configured
  (`KHATM_CREATION_PRICE_TOMAN=0`, `DEV_OTP=1`, `SMS_PROVIDER=noop`).
- Restarted local dev Postgres and the bot process after an interruption;
  verified `/health` and live polling.
- Investigated content-delivery for Salawat/Ziyarat khatms: no such
  pipeline exists yet (only Quran has one); flagged as a real fast-follow
  feature, not built today Ã¢â‚¬â€ Ziyarat Ashura's text needs a verified source
  from the owner, not a reproduction from memory.
- Verified with full pytest suite, a real-Postgres smoke test, a direct
  Jinja2 render check in 3 languages, and a bot restart + `/health` check.
  (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ Fixed language-menu reply-keyboard bug and reciter picker; investigated Quran-content report

- `settings_menu.py`: changing language now also refreshes the persistent
  bottom Reply Keyboard immediately (was only updating the inline settings
  message before).
- `content/service.py`: reciter picker now only offers Parhizgar
  (the only reciter with real registered audio) via a new
  `RECITERS_WITH_REGISTERED_AUDIO` constant; the underlying `SYSTEM_RECITERS`
  whitelist and its fallback-logic tests are untouched.
- Investigated the "content not registered" report: seed data and delivery
  queries are correct; the real cause is old test khatms using the
  superseded `iran-pocket` edition, which was never seeded with page
  assets. Not a code bug Ã¢â‚¬â€ recommended retesting with a fresh khatm.
- Verified with full pytest suite, the full real-Postgres integration
  suite (69 passed), an import smoke-test, and a bot restart + `/health`
  check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ Fixed message burst, province keyboard height, and join-invite text

- `my_khatms.py`: `list_my_khatms` no longer sends a burst of one message
  per khatm/action; everything is now one combined inline keyboard on the
  single summary message, with creator management behind a "Manage" opener
  button. New `my_khatms:manage:<id>` callback.
- `registration.py` / `profile.py`: province-selection keyboard now pairs
  two provinces per row instead of one-per-row, halving its height.
- `start.py`: `build_join_preview_message` now explains the khatm's content
  type (Quran/Salawat/Dua/La'an, with real category names) and what
  committing to it actually means (including the real pledged quantity for
  Salawat/Dua/La'an), fully localized fa/ar/en.
- Verified with full pytest suite (no regressions in `test_welcome_text.py`),
  real-Postgres one-off scripts for all three fixes, an import smoke-test,
  and a bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ Legacy settings commands localized; bot-side i18n rollout complete

- Owner resolved 3 open i18n-scope questions (DEC-PY-0075): `admin.py`
  stays Persian-only; the admin web panel needs translation (separate,
  not-yet-started task); legacy typed settings commands get translated.
- Converted all 7 legacy settings files (`digest_settings.py`,
  `font_settings.py`, `language_settings.py`, `reciter_settings.py`,
  `reminder_settings.py`, `sms_settings.py`, `timezone_settings.py`) to
  `t(key, lang)`; added 28 fa/ar/en keys.
- This completes the entire bot-side i18n rollout. Only the admin web
  panel remains, and it's a distinct task requiring its own architecture
  decisions first.
- Verified with full pytest suite, a real-Postgres key check, an import
  smoke-test for all 7 modules, and a bot restart + `/health` check.
  (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ devotional.py localized; normal-priority i18n checklist complete

- Converted `bot/handlers/devotional.py` to `t(key, lang)`; added 4
  fa/ar/en keys.
- Reviewed `broadcast.py`: no changes needed (typed admin/creator commands
  plus free-form creator-authored broadcast text, nothing translatable).
- This completes every "normal priority" file on `docs/ai/I18N_MIGRATION.md`'s
  checklist. Remaining: legacy typed-command settings files (low
  priority), `admin.py`, and the admin web panel Ã¢â‚¬â€ both need an owner
  decision before further work.
- Verified with full pytest suite, a real-Postgres key check, an import
  smoke-test, and a bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ manual_phone_verification.py: requester notification localized

- `bot/handlers/manual_phone_verification.py` is admin-only UI (stays
  Persian, like `admin.py`); localized only the approved/rejected
  notification sent to the requester Ã¢â‚¬â€ 2 fa/ar/en keys.
- Verified with full pytest suite, key checks, an import smoke-test, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ public_khatms.py fully localized

- Converted `bot/handlers/public_khatms.py` to `t(key, lang)`; added 4
  fa/ar/en keys.
- Verified with full pytest suite, a real-Postgres key check, and a bot
  restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ khatm_request.py localized (submitter side + notifications)

- Converted the submitter-facing flow in `bot/handlers/khatm_request.py`
  to `t(key, lang)`; added 11 fa/ar/en keys. Admin typed commands remain
  Persian (like `admin.py`), but the approve/reject notification back to
  the requester always uses the requester's own language.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ creator_decisions.py fully localized

- Converted `bot/handlers/creator_decisions.py` (`/khatm_decision`) to
  `t(key, lang)`; added 11 fa/ar/en keys. Fully localized despite being a
  creator typed command, because it also notifies a promoted third-party
  member.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ account.py fully localized

- Converted `bot/handlers/account.py` (delete-account confirm/cancel flow)
  to `t(key, lang)`; added 11 fa/ar/en keys under `account.*`.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ account_link.py fully localized

- Converted `bot/handlers/account_link.py` to `t(key, lang)`; added 11
  fa/ar/en keys under `account_link.*`, including the real OTP SMS text.
- Language resolved from the source account (current chat), carried via
  `state.update_data(lang=...)`.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ change_phone.py fully localized

- Converted `bot/handlers/change_phone.py` to `t(key, lang)`; added 22
  fa/ar/en keys under `change_phone.*`, including the actual OTP SMS text
  sent via Kavenegar (not just in-bot messages).
- Language carried through the multi-step OTP flow via
  `state.update_data(lang=...)`.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ wallet.py fully localized

- Converted `bot/handlers/wallet.py` (balance, invoices, PayPing top-up) to
  `t(key, lang)`; added 21 fa/ar/en keys under `wallet.*`.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ join_requests.py localized + shared join-success message localized

- Converted `bot/handlers/join_requests.py` to `t(key, lang)`, per-recipient
  (creator vs. requester) same as `leave.py`; added 10 fa/ar/en keys.
- Localized `build_join_success_message()` in `bot/handlers/start.py` (used
  by both the direct join flow and this file's approval flow); added a
  `lang` parameter and 9 new `join.*` keys. Rest of `start.py` remains
  Persian-only for now (separate checklist item).
- Verified with full pytest suite, a real-Postgres key/format check plus an
  import smoke-test, and a bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ leave.py fully localized

- Converted `bot/handlers/leave.py` to `t(key, lang)`; added 14 fa/ar/en
  keys under `leave.*`.
- First multi-recipient file this session: requester, creator, and
  promoted waitlist member each get their notification in their own
  stored language via a new `_lang_for_user(session, user_id)` helper.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ report.py fully localized

- Converted `bot/handlers/report.py` (today overview + personal report) to
  `t(key, lang)`; added 11 fa/ar/en keys under `report.*`.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ portions.py fully localized

- Converted `bot/handlers/portions.py` (portion completion, contribution
  logging, today-vs-yesterday, pause/resume/snooze, emergency-portion
  claim, friend-invite line) to `t(key, lang)`; added 60 fa/ar/en keys
  under `portions.*`.
- Plain callback handlers resolve language via `_lang_for()`; the three
  multi-message FSM flows store it once in `state.update_data(lang=...)`.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ my_khatms.py member entry point localized; NameError bug fixed

- Localized `list_my_khatms` (the "Ã°Å¸â€¢â€¹ Ã˜Â®Ã˜ÂªÃ™â€¦Ã¢â‚¬Å’Ã™â€¡Ã˜Â§Ã›Å’ Ã™â€¦Ã™â€ " button) and its follow-up
  messages in `bot/handlers/my_khatms.py`; added 21 fa/ar/en keys under
  `my_khatms.*`. Creator typed commands and the `cs:*` inline settings tree
  intentionally left in Persian pending an owner decision (same as
  `admin.py`).
- Fixed a real pre-existing bug: a block of message loops was misplaced
  inside `confirm_cancel_khatm`, referencing undefined variables Ã¢â‚¬â€ this
  would raise `NameError` on every khatm-cancellation confirmation. Removed
  the dead/broken duplicate; the correct logic already existed in
  `list_my_khatms`.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ settings_menu.py fully localized

- Converted `bot/handlers/settings_menu.py` and its keyboards in
  `bot/keyboards.py` to `t(key, lang)`; added 49 new fa/ar/en keys under
  `settings.*`.
- Language is read fresh per screen from `UserSettings.language` (no FSM
  state in this router), via a small `_lang_for()` helper.
- Verified with full pytest suite, a real-Postgres key/format check, and a
  bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ create_khatm.py wizard fully localized

- Converted the entire khatm-creation wizard (`bot/handlers/create_khatm.py`)
  to `t(key, lang, **kwargs)`; added 105 new fa/ar/en keys to
  `src/khatmsaz/i18n/__init__.py` under `create_khatm.*`.
- Language resolved once at wizard start and carried in FSM state (`lang`)
  instead of re-querying the DB on every step.
- Verified with full pytest suite, a real-Postgres one-off key/format check,
  and a bot restart + `/health` check. (Claude Code)

## 2026-09-20 Ã¢â‚¬â€ help.py fully localized

- Wired `bot/handlers/help.py` to resolve the real user's stored language
  and pass it through to `help_keyboard`/`help_*_actions_keyboard` (Codex
  had already added the translation keys and keyboard `lang` params in
  parallel, but nothing called them with a real language yet).
- Kept `HELP_TOPICS` (fa-only) for `tests/test_help.py` compatibility.
- Verified against real Postgres with an `en`-language user.

## 2026-09-20 Ã¢â‚¬â€ Multi-language (fa/ar/en) foundation started

- Added `src/khatmsaz/i18n/` (`t()`/`variants()` translation registry) and
  `UserSettings.language_prompted` (migration `c9d0e1f2a3b4`).
- `/start` now shows the welcome message then asks language once for
  first-time users; returning users get their stored language.
- Converted the 6 main-menu buttons + their filters (6 handler files) to
  the new variant-matching pattern, needed because aiogram's `F.text == X`
  filters can't look up the user's language before matching.
- Added `docs/ai/I18N_MIGRATION.md`: full continuation checklist for the
  rest of the bot's text (deliberately not attempted in one session).
- Verified against real Postgres. Fast suite: 62 passed, 64 skipped.

## 2026-09-20 Ã¢â‚¬â€ Time-limited SMS reminder subscriptions

- New module `sms_subscription` (migration `b8c9d0e1f2a3`): admin-editable
  plan options (seeded 3mo/50,000 & 6mo/87,000 toman) and a per-user
  subscription with expiry.
- `purchase()` charges the wallet, extends expiry, enables SMS;
  `process_expired()` (wired into the existing periodic scan) disables SMS
  and notifies the user exactly once per lapse.
- Replaced the free on/off SMS toggle in `settings_menu.py` with a
  plan-purchase keyboard; `/sms on` now points to it instead of enabling
  for free; `/sms off` still works directly.
- Added `/admin_sms_plan_set` for editing plan options.
- Verified end-to-end against real Postgres (purchase, expiry, single
  notification, no double-notify on repeat scan).

## 2026-09-20 Ã¢â‚¬â€ Plain-language wizard prompts + local DB recovery

- Rewrote remaining terse wizard prompts (welcome message, creator display
  name, start schedule, reminder tone, advertising opt-in) with concrete,
  verified explanations Ã¢â‚¬â€ corrected a misleading "ads are shown" framing
  to accurately describe the real mechanic (platform-funded one-time
  wallet credit, not a creator charge).
- Found the bot down: the Docker Postgres container has no published port;
  the actual local database is a separate recovery cluster that had
  stopped. Restarted it and the bot manually; noted that a `start_bot.ps1`
  terminal needs to stay open for auto-restart supervision to apply.

## 2026-09-20 Ã¢â‚¬â€ Today-vs-yesterday progress for countable khatms

- Added `open_contribution.service.today_vs_yesterday` +
  `repository.total_for_khatm_between`; shows the group's running today
  total next to yesterday's full-day total after each open-pool logging.
- Scoped to open contribution logging only (Salawat/Dua/Ziyarat/La'an);
  SALAWAT+COMMITMENT quantity logging has no per-increment timestamp yet,
  flagged as a separate, bigger feature if wanted later.
- Verified against real Postgres with a backdated row to prove the
  day-boundary split is correct.

## 2026-09-20 Ã¢â‚¬â€ Reordered creation wizard (content first, then commitment/free)

- Moved the Ã˜ÂªÃ˜Â¹Ã™â€¡Ã˜Â¯Ã›Å’/Ã˜Â¢Ã˜Â²Ã˜Â§Ã˜Â¯ question to after content family + subcategory
  selection (was asked first before); added `CreateKhatm.choosing_mode`.
- Each (template, category group) combination now shows its own concrete
  commitment/free example instead of one generic explanation.
- Verified all four combinations produce distinct text and correct state
  transitions via a direct functional test.

## 2026-09-20 Ã¢â‚¬â€ Free-tier plan member caps (DEC-PY-0074)

- Added `khatm_workflow.service._enforce_creation_cap` +
  `PlanCapExceededError`: blocks *new* khatm creation (never existing
  membership) once a FREE-tier creator's summed member count across their
  own SALAWAT-family or QURAN_PAGE khatms hits an admin-configured cap.
- Reused `PlanDefinition.entitlements` (no new table) with two new keys:
  `max_devotional_members`, `max_quran_members`. Missing key = unlimited.
- Extended `/admin_plan_set` to accept `key=value` numeric entitlements.
- Verified end-to-end against real Postgres (cap hit blocks creation,
  existing khatm still accepts new members).

## 2026-09-20 Ã¢â‚¬â€ Post-completion invite links + docs archiving

- Every portion/contribution-logged message now ends with a link inviting
  friends to the same khatm (owner-provided sample matched).
- Split `PROJECT_STATE.md`, `CHANGELOG.md`, `DECISIONS.md` into trimmed
  current files + verbatim `docs/ai/archive/*.md` files; documented the
  convention in `AI_HANDOFF_PROTOCOL.md`.
- Resolved three BACKLOG.md clarifications (100-member cap is per-creator;
  SMS plan prices are in thousands of toman; post-completion link = invite
  link).

## 2026-09-20 Ã¢â‚¬â€ Converted dashboard entry to signed Telegram Mini Apps

- Replaced token-bearing admin/creator URL buttons with Telegram `web_app`
  buttons and new visible `/admin_app` and `/creator_app` commands.
- Added server-side Telegram HMAC, freshness, duplicate-field, identity and
  authorization validation; issued only Secure, HttpOnly scoped sessions.
- Disabled legacy query-string token login and added forged/stale/wrong-bot
  regression tests plus a real PostgreSQL/ASGI authentication test.
- Kept Bale closed rather than guessing an undocumented authentication flow.
- Added a fail-closed HTTPS-origin gate so local/LAN addresses never reach
  Telegram as invalid Mini App buttons; focused entry tests: 2 passed.
- Complete real-PostgreSQL regression: **121 passed in 136.33s**; restarted
  Telegram polling and verified database-aware HTTP health.

## 2026-09-20 Ã¢â‚¬â€ Separated devotional parent families

- Made Salawat, Dua/Ziyarat and La'an independent top-level creation choices.
- Added group-filtered service/repository reads and guarded forged category
  callbacks so children cannot cross parent families.
- Limited custom content requests to Dua/Ziyarat.
- Seeded La'an Umar, Abu Bakr, Aisha, and the eightfold Imam Reza item in
  migration `ab8c9d0e1f2a`, leaving body text empty pending verified content.
- Added navigation unit coverage and real PostgreSQL family-filter coverage.

## 2026-09-20 Ã¢â‚¬â€ Added khatm search to the admin Mini App

- Added bounded search by khatm title, creator display name and UUID, combined
  with the existing status filter and active-member aggregate.
- Added a real PostgreSQL/ASGI test for every search key and empty results.
- Validation: focused integration 2 passed; fast suite 62 passed, 62 skipped.
- Added 25-row pagination for khatm and user searches, preserving search and
  status filters with mobile-friendly controls.
- PostgreSQL pagination test proves the 25+1 boundary for both lists; focused
  integration 3 passed and fast regression 62 passed, 63 skipped.

## 2026-09-20 Ã¢â‚¬â€ Paginated creator reports and fixed XLSX member export

- Added 25-row pagination to creator-owned khatms and searchable member
  reports, retaining the query and enforcing ownership on every page.
- Scoped active-member aggregation to only the visible creator khatms.
- Fixed XLSX export crashing when the Tehran join time was already rendered as
  text; integration now downloads and opens the workbook and checks member data.
- Validation: focused real-PostgreSQL tests 3 passed; fast suite 62 passed,
  64 skipped.
- Replaced raw member status/gender enums and the technical `Miss` wording
  with plain Persian labels; restored independent Salawat, Dua/Ziyarat and
  La'an labels. Focused render/PostgreSQL tests: 4 passed.

## 2026-09-20 Ã¢â‚¬â€ Hardened the one-command Windows bot launcher

- Added a real TCP readiness probe for PostgreSQL to `start_bot.ps1`.
- The launcher now tries the existing Docker database and the preserved local
  PostgreSQL recovery cluster, then stops with an actionable error instead of
  running the bot against an unavailable database.
- Pending Alembic migrations are applied before polling starts.
- Verified the script end-to-end: Telegram polling, admin web, and database-
  aware HTTP 200 health all started successfully.
- Documented `.\start_bot.ps1` as the preferred Windows command in README.

---

## 2026-09-20 Ã¢â‚¬â€ Made health database-aware and recovered stable local PostgreSQL

- Changed `/health` from a process-only response to a real PostgreSQL
  readiness check; database failure now returns HTTP 503 without leaking
  connection details.
- Added healthy/failure unit coverage; fast suite: `50 passed, 59 skipped`.
- Initialized an isolated PostgreSQL 18 cluster after Docker Desktop stopped
  publishing its configured host port, and applied every migration to head.
- Full integration-enabled suite passed: `109 passed in 131.80s`.
- Took a non-destructive custom-format backup of the Docker database and
  restored it locally (32 users, 22 khatms), then restarted the live bot.
- Confirmed the configured Telegram Super Admin already owns an active
  VERIFIED phone claim; no further OTP is required for creator testing.
- Updated `Rahnama.VPS.txt` with the new HTTP 200/503 health contract.

---

## 2026-09-19 Ã¢â‚¬â€ Recovered PostgreSQL and confirmed Quran forwarding live

- Restarted the existing `khatmsaz-py-postgres` container on port 55433.
- Ran the new private-join authorization regression against PostgreSQL:
  `1 passed`.
- Restarted the Telegram bot/admin web against the recovered database.
- Reclassified Quran-channel forwarding as live-verified: Telegram shows the
  forwarded pages 1Ã¢â‚¬â€œ2 image and one deduplicated Parhizgar audio source post
  covering pages 1Ã¢â‚¬â€œ3, with the seeded map at 604/604 coverage.

---

## 2026-09-19 Ã¢â‚¬â€ Hardened private-khatm join decisions

- Revalidated Cloud Code's recent handler changes with compileall and the full
  default test suite.
- Added creator-ownership checks for both approve and reject callbacks.
- Enforced approval ownership again in `khatm_workflow.service` to prevent a
  forged callback from bypassing the handler.
- Added independent unit and PostgreSQL regression tests. The focused unit test
  and full default suite pass (`48 passed, 59 skipped`); the PostgreSQL test
  subsequently passed after database-container recovery.
- Confirmed the running bot/admin health endpoint returns `{"status":"ok"}`.

---

## 2026-09-19 Ã¢â‚¬â€ Added optional attachments to custom khatm requests

- Users can attach a document or photo after describing a requested khatm,
  or explicitly continue without a file.
- Only platform file ID and metadata are persisted; the bot does not download
  the file automatically.
- Added migration `aa7b8c9d0e1f` and PostgreSQL integration coverage.
- Content admins now receive attached documents/photos directly while viewing
  the pending request queue.
- Full PostgreSQL integration suite after the change: 105 passed.

---

## 2026-09-19 Ã¢â‚¬â€ Regression test audit

- Full default suite: 47 passed, 57 intentionally skipped integration tests.
- Runtime health check remained `{"status":"ok"}`.

---

## 2026-09-19 Ã¢â‚¬â€ Audited payment-secret handling

- Confirmed the PayPing panel credentials are absent from project files.
- Confirmed `.env` is ignored and the API token remains unset until the owner
  creates a dedicated token manually.

---

## 2026-09-19 Ã¢â‚¬â€ Completed button-first open schedule choices

- Added workday, weekend, and specific-date choices to the open-khatm
  schedule menu.
- Specific dates are entered in Tehran-local `YYYY-MM-DD` format and pass
  through the existing ownership and service validation.
- Validation: compileall passed; focused tests 7 passed.
- Creator settings now show the currently selected schedule in plain Persian.
- Fixed-date schedules now reject past dates using the configured application
  timezone at the service boundary.

---

## 2026-09-19 Ã¢â‚¬â€ Added button-first ending and open scheduling

- Added Tehran-local historical end-date entry/clear controls to per-khatm
  settings, with future-date and ownership validation.
- Added open-khatm schedule presets for off, daily, and every three days.
- Validation: focused menu tests 3 passed; full PostgreSQL suite 103 passed.

## 2026-09-19 Ã¢â‚¬â€ Added a recoverable Windows bot launcher

- Added `start_bot.ps1` and `start_bot.bat` for the local project.
- The launcher automatically retries an unexpected bot-process exit after five
  seconds and documents the distinction between local and VPS operation.

## 2026-09-19 Ã¢â‚¬â€ Added button-first miss-alert policy presets

- Added the current miss threshold/window to commitment-khatm settings.
- Added sensitive, balanced, and relaxed one-tap policy presets with clear
  private-alert semantics and existing service-level validation.
- Validation: focused menu tests 3 passed; full PostgreSQL suite 103 passed.

## 2026-09-19 Ã¢â‚¬â€ Added button-first title and welcome editing

- Added Title and Welcome buttons to each owned khatm's settings screen.
- Added a guarded text-entry flow with cancel/back, ownership/status rechecks,
  service-level length validation, and plain-Persian welcome deletion.
- Kept structural fields immutable after activation.
- Validation: focused menu tests 3 passed; full PostgreSQL suite 103 passed.

## 2026-09-19 Ã¢â‚¬â€ Added button-first per-khatm policy settings

- Added a creator settings button to every owned-khatm management card.
- Added scoped inline controls for Quran content mode, Skip Today, commitment
  Pause and reminder Snooze, with clear Persian explanations and live state.
- Reused the existing ownership checks and domain services; inapplicable
  controls are hidden and stale/unauthorized callbacks are rejected.
- Validation: focused keyboard tests 3 passed; full PostgreSQL suite 103 passed.

## 2026-09-19 Ã¢â‚¬â€ Removed commands from first-run help/profile UX

- Added a persistent `Ã˜Â±Ã˜Â§Ã™â€¡Ã™â€ Ã™â€¦Ã˜Â§Ã›Å’ ÃšÂ©Ã˜Â§Ã™â€¦Ã™â€ž` Home-menu button and routed it to the
  complete button-driven help screen.
- Updated welcome copy to point at the button instead of `/help`.
- Made Create automatically launch profile completion when creator details are
  incomplete instead of asking the user to type `/profile`.
- Validation: full PostgreSQL suite 102 passed.

## 2026-09-19 Ã¢â‚¬â€ Made create/manage help actionable without commands

- Added direct buttons to start creation, submit a custom-khatm request, open
  My Khatms, and request creator/admin dashboard login links.
- Added a guarded FSM step for custom-khatm descriptions and preserved the old
  `/request_khatm` entry point for compatibility.
- Removed slash-command instructions from the create/manage help copy.
- Validation: focused help tests 5 passed; full PostgreSQL suite 102 passed.

## 2026-09-19 Ã¢â‚¬â€ Added live Quran-channel access diagnosis

- Extended `/admin_quran_source_status` to check whether the Telegram bot can
  currently resolve the configured private source channel.
- Kept 604-page registry coverage separate from live delivery readiness and
  added an actionable Persian message when the bot has not been added.
- Live evidence: forwarding source message 10 returned Telegram `chat not
  found`; no content was delivered and no database state changed.

## 2026-09-19 Ã¢â‚¬â€ Made creation coupons button-first

- Added a coupon button to paid-khatm confirmation and a simple code-entry
  step with retry, skip and cancel actions.
- Removed slash-command instructions from the normal and expired-coupon UX,
  while preserving `/coupon CODE` compatibility.
- Validation: focused tests 4 passed; full PostgreSQL suite 101 passed.

## 2026-09-19 Ã¢â‚¬â€ Made wallet and account settings button-first

- Added direct help buttons for wallet balance/top-up and invoice history.
- Added direct settings/help buttons for profile editing, secure phone change,
  and linking a prior account.
- Removed typed slash-command instructions from wallet/settings help and the
  successful-payment return copy while retaining command compatibility.
- Validation: focused UX tests 3 passed; full PostgreSQL suite 98 passed; live
  Telegram polling and web health both confirmed.

## 2026-09-19 Ã¢â‚¬â€ Added complete two-VPS deployment and PayPing proxy guide

- Added `Rahnama.VPS.txt`, a zero-assumption Persian runbook from first SSH
  login through production deployment, HTTPS and operations.
- Included exact Nginx and Apache configurations that preserve PayPing's POST
  body while rewriting the public service-domain path to FastAPI's real route.
- Included safe rollout, tests, backups, rollback and troubleshooting, and
  clarified that a product referral URL is not the API callback.

## 2026-09-19 Ã¢â‚¬â€ Added Health/Operations dashboard

- Added `/operations` for Super Admin/Operations with live database,
  Telegram/Bale, PayPing, Kavenegar, queue-depth and reminder-worker status.
- Added an in-process scheduler/scan heartbeat that records safe exception
  class names only and never exposes tokens or provider error payloads.
- Added Persian navigation and PostgreSQL-backed authorization/render tests.
- Validation: targeted admin suite 4 passed; full suite 98 passed.

## 2026-09-19 Ã¢â‚¬â€ Hardened category moderation and button-only profile entry

- Registered `khatm_category` models in the central SQLAlchemy model registry.
- Enforced one-way `PENDING` category-request decisions; replay attempts now
  return HTTP 409 and cannot create duplicate categories.
- Audited category create/update/toggle/request-fulfill/request-decline actions.
- Made the settings Ã‚Â«Ã™Ë†Ã›Å’Ã˜Â±Ã˜Â§Ã›Å’Ã˜Â´ Ã™â€¦Ã˜Â´Ã˜Â®Ã˜ÂµÃ˜Â§Ã˜ÂªÃ‚Â» button launch the profile wizard directly.
- Expanded real-PostgreSQL admin regression coverage to categories,
  broadcasts, foreign-number verification and replay protection.
- Validation: targeted admin integration suite 4 passed; full suite 98 passed.

## 2026-09-20 Ã¢â‚¬â€ Cross-AI handoff protocol + owner backlog

- Added `docs/ai/AI_HANDOFF_PROTOCOL.md`: shared convention for Codex,
  Claude Code, and Antigravity (owner now runs all three) to sign changes
  and hand off cleanly. `CLAUDE.md` now points to it.
- Added `docs/ai/BACKLOG.md` capturing every item from the owner's latest
  feature request in full, each with current-state context and explicit
  "needs a decision" flags where a real product question is still open
  (multi-language rollout trigger, plan/capacity semantics, SMS pricing).

## 2026-09-20 Ã¢â‚¬â€ SALAWAT+COMMITMENT waiting list

- Extended capacity/waiting-list support (previously QURAN_PAGE-only) to
  SALAWAT+COMMITMENT khatms, per explicit owner decision: a waitlisted
  participant contributes casually through the open pool, same as Quran.
- Fixed a related pre-existing gap: waitlisted participants (both templates)
  never actually got a contribute button, in the join message or in
  `my_khatms.py` on later visits. Both now show one.
- Verified end-to-end against real Postgres (capacity gate, waitlisting,
  leave-triggered promotion with a real quantity portion assigned).

## 2026-09-19 Ã¢â‚¬â€ Warmer bot copy + Quran channel live + dev OTP bypass

- Rewrote DB-backed reminder templates (`reminder.first/second/final/missed`,
  fa/FRIENDLY) to match a warmer, more explicit sample the owner provided
  (explicit Tehran-time deadline, "delegate to a friend" line, sawab
  framing); added the missing `deadline` value to `reminder.first`.
- Warmed up the per-page completion message and several terse
  creator/admin-facing approve/reject confirmations across
  `start.py`, `registration.py`, `profile.py`, `leave.py`,
  `join_requests.py`, `khatm_request.py`. Not a full-codebase pass Ã¢â‚¬â€ logged
  what's left in PROJECT_STATE.md.
- Set `DEV_OTP=1` in `.env` (local dev only, existing intentional bypass)
  so khatm creation isn't blocked while waiting on a real Kavenegar token.
- Owner added the bot as admin to the real Quran channel and ran
  `/admin_quran_source_seed`; confirmed 604/604 images and audio registered
  against the pre-built verified map for that exact channel.

## 2026-09-19 Ã¢â‚¬â€ Admin-manageable khatm categories (Ã˜ÂµÃ™â€žÃ™Ë†Ã˜Â§Ã˜Âª/Ã™â€žÃ˜Â¹Ã™â€ /Ã˜Â§Ã˜Â¯Ã˜Â¹Ã›Å’Ã™â€¡)

- New module `khatm_category` + migration `a7f8b9c0d1e2`: `khatm_categories`,
  `khatm_category_requests`, and `khatms.content_category_id`.
- `/categories` admin page: add/edit/activate/deactivate content items and
  turn a participant's "Ã˜Â¯Ã˜Â¹Ã˜Â§Ã›Å’ Ã˜Â¯Ã›Å’ÃšÂ¯Ã˜Â± (Ã˜Â¯Ã˜Â±Ã˜Â®Ã™Ë†Ã˜Â§Ã˜Â³Ã˜ÂªÃ›Å’)" request into a permanent item Ã¢â‚¬â€
  no code deploy needed for new Ã˜ÂµÃ™â€žÃ™Ë†Ã˜Â§Ã˜Âª/Ã™â€žÃ˜Â¹Ã™â€ /Ã˜Â§Ã˜Â¯Ã˜Â¹Ã›Å’Ã™â€¡ content.
- Creation wizard's SALAWAT branch now shows the live category list from the
  DB instead of a single hardcoded button.
- Seeded 6 starting categories (text left blank for the owner to paste in
  from khedmatgozaran.com via the panel).
- Verified end-to-end against real Postgres (round-tripped
  `content_category_id` on a real khatm, cleaned up test rows); fast suite
  41 passed, 56 skipped; bot restarted cleanly.
- Added `docs/ai/QA_HANDOFF_TELEGRAM_TESTING.md` for Codex to run full
  Telegram-based scenario testing and self-fix bugs.


---

## Older history

Entries from 2026-09-18 and earlier were moved to keep this file
readable: [docs/ai/archive/CHANGELOG_until_2026-09-18.md](archive/CHANGELOG_until_2026-09-18.md).
# 2026-09-20 Ã¢â‚¬â€ SMS/plan integrity fixes and verified restart [Codex]

- Prevented SMS subscription purchases from debiting the wallet when the
  user has no contact phone; invalid purchase callback payloads now fail
  safely.
- Added migration `d0e1f2a3b4c5` to idempotently restore the FREE plan row
  while preserving administrator-edited entitlement values.
- Made the free devotional-member cap aggregate SALAWAT, DUA, ZIYARAT and
  CUSTOM rows as one product family, while keeping Quran independent.
- Added PostgreSQL integration regressions; full suite passed: 128 tests.
- Restarted the Telegram bot and verified polling plus database health.
# 2026-09-20 Ã¢â‚¬â€ Admin Mini App plan controls [Codex]

- Added graphical plan-definition controls to the Finance section: pricing,
  enabled state, creation access, devotional cap and Quran cap.
- Added graphical create/edit/disable controls for paid SMS subscription
  durations and prices.
- Preserved unrecognized entitlement keys during edits and audit-logged both
  mutation types.
- Added real-PostgreSQL ASGI coverage; full suite now passes 129 tests.
# 2026-09-20 Ã¢â‚¬â€ Multilingual first-join registration [Codex]

- Localized the complete registration flow to Persian, Arabic and English.
- Added localized phone sharing, validation, gender and all 31 province
  labels while retaining canonical Persian province storage.
- Added PostgreSQL-backed Arabic/English registration tests; full suite now
  passes 131 tests.
# 2026-09-20 Ã¢â‚¬â€ Multilingual profile editing [Codex]

- Localized `/profile` and the Settings profile flow to fa/ar/en.
- Localized the verified-phone security warning without weakening its
  requirement to use `/change_phone`.
- Reused canonical province storage and localized province/gender controls.
- Full real-PostgreSQL suite: 131 passed.

## 2026-09-28 (admin finance/content UX redesign)
- **UX**: `/finance` now explains in plain Persian who an ordinary user and a creator are, what plan numbers control, and gives a concrete per-creation pricing example; technical labels were replaced with task-oriented wording.
- **UX**: `/categories` now uses a devotional-library dropdown instead of requiring admins to copy a slug, distinguishes short inline content from full devotional text, links directly to `/devotionals`, and always shows explicit active/hidden status pills.
- **UX**: `/devotionals` describes the libraryâ†’category workflow and treats the slug as an internal identifier rather than an admin workflow step.
- **Tests**: added real Jinja rendering coverage for all three redesigned pages (`tests/test_admin_template_render.py`); non-integration suite is 93 passed.
## 2026-09-28 (creator web panel khatm settings)
- **Feature**: Creator khatm detail now includes a simple settings panel alongside its existing stats, searchable member list, and Excel export.
- **Settings**: creators can edit title/welcome text and the applicable existing domain settings: pause, snooze, Quran skip-today, missed-commitment follow-up window, open-khatm schedule, and completion announcement.
- **Security**: the settings POST requires a valid creator session, CSRF token, khatm ownership, and active status; mutations call the same domain services used by the bot and are audited.
- **i18n/tests**: all new creator copy is present in fa/ar/en; real Jinja render and i18n coverage pass. Full non-integration suite: 94 passed.
## 2026-09-28 (Mini App chat entry and pending-payment safety)
- **Mini App UX**: admin/creator panel buttons now request the existing authorized chat entry callbacks; users receive the launch instruction and WebApp button in chat after role/platform/HTTPS checks.
- **Payment safety**: confirmed callback expiry checks and atomic `used=false` claim precede wallet credit. Added scheduled deletion of expired unused payment intents; consumed rows remain for audit/replay evidence.
- **Tests**: added coverage that expired callbacks never call the gateway or credit a wallet, a failed compare-and-swap never credits, and panel buttons route through chat entry. Full non-integration suite: 98 passed.
- **Infrastructure**: `api.khedmatgozaran.com` certificate mismatch remains an external blocker; no real payment was attempted.
## 2026-09-28 (Graphify code graph refresh)
- Refreshed the portable code graph after the panel and payment work: 413 files, 3,298 nodes, 12,176 edges, and 233 communities.
- Added the graph report, interactive HTML, JSON graph, labels, cost metadata, and incremental manifest; excluded local cache/backups and machine-specific paths.
## 2026-09-28 â€” Creator bot menu and direct onboarding flow

- Made the creator menu invariant across account roles and languages; participant navigation is now exclusive to member bots.
- Continued first-language selection and plain `/start` directly into create-khatm; ordinary users are promoted when they choose creation instead of being sent to an approval-request dead end.
- Updated onboarding copy and documented why the complete province list remains two columns.

## 2026-09-28 â€” Isolate member bots and normalize admin creator-menu UX

- Fixed member-facing queries and actions so data is limited to the current category-specific bot instance; public discovery also enforces Quran/Salawat/Dua-Ziyarat/La'an family boundaries.
- SUPER_ADMIN now receives the normal creator reply menu in the creator bot; `/admin_app` remains permission-gated and is the sole admin-panel entry.
- Added a guarded development reset SQL script that preserves super-admin identities and static content/configuration while deleting all khatms and other users' data.
## 2026-09-28 (member-controlled Quran and live-QA fixes)
- Quran joins now go directly to pages-per-day and delivery-hour setup; fixed automatic portions and their done/snooze controls are no longer created or shown to new readers.
- Fixed creator contact auto-fill selecting the bot username after callback navigation; it now uses the human creator's username, falling back to the registered phone.
- Made the template, intro caption/image, and deadline wizard messages ephemeral like the rest of the creation flow.
- Clarified Quran-audio toggle labels so the current on/off state cannot be mistaken for the action.
- Added regression tests for member-controlled Quran joining and the absence of fixed-portion controls; Graphify output refreshed.
## 2026-09-30 (owner spec B6â€“B10 creation and editing UX)
- Added trust-building creator copy and family-specific welcome/commitment prompts.
- Converted creation and member join setup to tracked, updating-message flows with preserved summaries and back navigation.
- Expanded creator editing in bot/web with safe repetition-goal increases, visibility, platform, tone and deadline controls.
- Added DEC-PY-0099 and dedicated B6â€“B10 regression coverage.

## 2026-09-30 (owner spec B1â€“B5 creation wizard)
- Routed the remaining creation questions through the wizard-owned message cleanup path.
- Added a localized, stateful previous-step action across active creation stages.
- Renamed the Quran family button to Â«Ø®ØªÙ… Ù‚Ø±Ø¢Ù†Â» and corrected confirmation/goal copy for B4/B5.
- Added focused regressions for B1â€“B5 and updated keyboard expectations for the new navigation action.
## 2026-09-30 (owner spec C1â€“C6 and creation wizard cleanup)
- Removed the visible cancel button from every create-khatm wizard screen while retaining back navigation and compatibility with old callback messages.
- Fixed memberâ†’creator and creatorâ†’Super Admin ticket routing, reply authorization, and exact member-bot reply delivery.
- Replaced negative moderation copy with Â«Ø¨Ø±Ø§ÛŒ ØªØ£ÛŒÛŒØ¯ Ù…Ø­ØªÙˆØ§Â» and aligned bot/web approval delivery for text and media.
- Enforced two lifetime free Telegram/Bale broadcasts under 1000 recipients for non-PRO creators; SMS is paid from the first send.
- Added composable khatm/province/gender audience filters and migration `broadcastfilters2026093001`.
- Added Section C regression and PostgreSQL integration coverage.
- Validation: 226 passed/86 skipped; one Alembic head; Graphify refreshed to 4,019 nodes and 14,246 edges. Live PostgreSQL migration apply was unavailable because the configured endpoint refused the connection.
## 2026-09-30 (owner spec D1 today-action label)
- Renamed the member action to Â«ðŸ“– Ø§Ù†Ø¬Ø§Ù… Ù‚Ø±Ø§Ø¦Øª Ø§Ù…Ø±ÙˆØ²Â» in the menu and every direct user-facing reference.
- Added regression coverage across navigation, help, i18n and today delivery. Focused suite: 22 passed. No migration.
## 2026-09-30 (owner spec D2 help synchronization)
- Updated all help topics to match current creation, joining, settings, editing and moderated-broadcast behavior.
- Removed stale feature claims and aligned Persian/Arabic/English help structure.
- Restored Â«Ø§Ù†ØµØ±Ø§ÙÂ» only on the first four-family creation screen, where a previous-step action is impossible.
## 2026-09-30 (owner spec D3 member contact menu)
- Made both member-menu constructors use one layout with direct creator contact and no generic support entry.
- Verified the menu routes into the secured C1 ticket flow. Focused suite: 28 passed.
## 2026-09-30 (owner spec D4 custom khatm contact)
- Added a custom-khatm request button to member bots and an admin-managed contact number in Operations.
- Added phone validation, CSRF protection, privacy-safe audit metadata and localized empty-state copy. No migration.
## 2026-10-01 (ephemeral wizard/profile prompts and commitment deadline repair)
- Prevented unchanged wizard summaries from spawning duplicate messages and removed completed creator/profile prompts and typed answers.
- Compressed the creator main menu into three rows.
- Added the daily deadline question/storage to every commitment devotional family, not only Quran.
- Reworded creator identity, open-khatm responsibility and member commitment guidance; hardened open/commitment enum detection.


