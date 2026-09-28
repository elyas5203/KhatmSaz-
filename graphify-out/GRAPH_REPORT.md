# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 447 files · ~286,003 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3374 nodes · 11533 edges · 230 communities (146 shown, 84 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 1499 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- new id()
- sqlalchemy
- get or create()
- t()
- wallet/service.py
- identity/service.py
- Platform
- Base
- start.py
- provider.py
- panel.py
- Khatm
- keyboards.py
- allocation/repository.py
- sqlalchemy ext asyncio
- typing
- sqlalchemy dialects
- create khatm.py
- types
- env.py
- portions.py
- Participation
- alembic
- PayPingGateway
- advertising/service.py
- reminder engine/service.py
- reporting/service.py
- PlatformIdentity
- test admin web integration.py
- plan/service.py
- UserRole
- safe answer callback()
- KhatmCategory
- creator request/service.py
- UserSettings
- sms subscription/service.py
- app.py
- test deep link clears old state before s
- test registration starts in the users sa
- bot registry/service.py
- broadcast/service.py
- member registration.py
- test fresh committed salawat join asks d
- content/service.py
- suggestions.py
- admin()
- completion/service.py
- Request
- Session
- allocation/service.py
- phone/repository.py
- notification/service.py
- creator broadcast/service.py
- DevotionalAsset
- test confirm wizard resumes and finishes
- khatm request/repository.py
- QuranAssetKind
- khatm workflow/service.py
- message template/repository.py
- complete account link()
- test recitation text only for laan.py
- admin approve request()
- ensure creator phone verified()
- bot registry.py
- KhatmSaz Project (Claude Code Instructio
- Architecture Document
- Domain Model
- AsyncSession
- AuditLog
- ReplyKeyboardMarkup
- system settings/repository.py
- Devotional texts CRUD (dua/ziyarat) admi
- create and launch khatm()
- KhatmSaz VPS Deployment Guide
- manual phone verification/repository.py
- WaitingList
- test health.py
- test bot commands.py
- list identities for user()
- begin profile()
- cancel commitment()
- show wallet()
- invite links.py
- runtime status.py
- test admin template render.py
- test bale invite is a real clickable lin
- CSS Layouts and Responsive Design Guide
- Multi-Bot Architecture Index Section
- BotRegistry Singleton Class
- confirm account deletion()
- positional range for step()
- test message template.py
- Creator Role (vs Participant)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per
- Multi-Bot (26-bot) Architecture
- qr.py
- approve join()
- receive media()
- get registry()
- content/ init .py
- test quran channel source.py
- message template/ init .py
- test broadcast shows khatm picker()
- test dispatcher routes commands while pr
- main()
- Python Requirements
- KhatmSaz PROJECT STATE Log
- PayPing v3 Adapter Integration
- commitment total keyboard()
- decide manual phone request()
- show member portion()
- test member cancel clears state()
- join public khatm()
- add devotional audio variant()
- test contribute blocked until delivery h
- FakeMessage
- test tapping a time of day button saves 
- test set font size validates and persist
- payping callback()
- set audio()
- handle creator request message()
- release portion()
- register devotional text()
- test completion announcement waits is id
- test daily digest combines multiple khat
- test next portion is withheld until next
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earli
- test i18n coverage.py
- help start creation()
- Tooltip Jinja2 Macro Component
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based m
- Settings Menu Full-Button Test Scenario
- 435027907255 add daily deadline hour to 
- . call ()
- set audio callback()
- resolve creator decision()
- receive delivery hour()
- AccountDeletionBlocked
- message template/service.py
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE
- resolve user info()
- personal report()
- AlreadyParticipatingError
- Creator Panel Base Layout Template
- start bot.ps1
- test devotional slug link does not depen
- test devotional text and platform specif
- test active categories are filtered by t
- claude watchdog.sh
- Quran Content Storage (Telegram channel-
- Roadmap Phase 10 — Messenger Mini Apps
- security headers()
- CreatorBroadcastFlow
- RequestKhatm
- ManageContentState
- CreatorKhatmEdit
- broadcast/ init .py
- web/ init .py
- Persian-first, Simple UX Principle
- Debugging Guide
- Content Category (khatm category) Index 
- INDEX — Topical Map of Documentation
- Redis (reserved for FSM / scheduler)
- dp creator Router Registration List
- 26-Bot Grid (1 creator + 12 member per p
- Khatm Category Independent Families Test
- QA Handoff: Telegram Testing Guide for C
- khatmsaz bot
- khatmsaz core
- khatmsaz core db
- khatmsaz core ids
- khatmsaz modules allocation
- khatmsaz modules identity
- khatmsaz modules invitation
- khatmsaz modules khatm models
- khatmsaz modules khatm workflow
- khatmsaz modules notification
- khatmsaz modules participation
- Module: audit log
- Module: settings
- Bot
- message
- message
- UUID
- Admins Management Page
- Audit Log Page
- Broadcasts Admin Page
- Categories Admin Page
- Finance Admin Page
- Public Khatm Join Page
- Operations/Health Admin Page
- Phone Verifications Admin Page
- Message Templates Admin Page

## God Nodes (most connected - your core abstractions)
1. `t()` - 321 edges
2. `session_scope()` - 278 edges
3. `Platform` - 247 edges
4. `new_id()` - 130 edges
5. `User` - 126 edges
6. `Khatm` - 121 edges
7. `safe_answer_callback()` - 103 edges
8. `KhatmStatus` - 78 edges
9. `Base` - 78 edges
10. `get_or_create()` - 78 edges

## Surprising Connections (you probably didn't know these)
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py
- `رفع‌شدهٔ فاز ۲ (این جلسه، با تست)` --references--> `snooze_keyboard()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/keyboards.py
- `عضو (Member bots) — تلگرام fa/ar/en و بله` --references--> `BotRole`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/modules/bot_registry/models.py
- `سازنده (Creator) — تلگرام` --references--> `personal_report()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/report.py
- `سازنده (Creator) — تلگرام` --references--> `khatm_qr()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/my_khatms.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Multi-Bot 26-Bot Split** — docs_ai_multibot_readme_botregistry, docs_ai_multibot_readme_creatorbot, docs_ai_multibot_readme_memberbots, docs_ai_multibot_readme_invitelinks, docs_ai_multibot_readme_handlerrouting [EXTRACTED 0.75]
- **VPS Production Stack** — rahnama_vps_systemdservice, rahnama_vps_nginxreverseproxy, rahnama_vps_certbothttps, rahnama_vps_postgresbackup [EXTRACTED 0.75]
- **Multi-Language Invite Link: category mapping → language selection → per-bot token → landing page** — docs_ai_multibot_overview_category_mapping, docs_ai_multibot_invite_links_link_generation_flow, docs_ai_multibot_invite_links_token_resolution, docs_ai_multibot_invite_links_web_landing_page [EXTRACTED 0.95]
- **Khatm Execution Modes (Commitment, Open, Hybrid)** — concept_khatm, concept_commitment_mode, concept_open_mode, concept_allocation, concept_waiting_list [EXTRACTED 0.95]
- **26-Bot Architecture: BotRegistry + Two Dispatchers + bot_instances** — docs_ai_multibot_bot_registry_botregistry_class, docs_ai_multibot_overview_two_dispatchers, docs_ai_multibot_bot_registry_bot_instances_table, docs_ai_multibot_handler_routing_router_classification [EXTRACTED 0.95]
- **Notification Routing: joined_via_bot_instance_id → notify_fn → correct member bot** — docs_ai_multibot_notification_routing_joined_via_bot_instance_id, docs_ai_multibot_notification_routing_notify_fn, docs_ai_multibot_member_bots_member_my_khatms, docs_ai_multibot_bot_registry_botregistry_class [EXTRACTED 0.95]
- **Multi-AI Collaborative Workflow (Codex + Claude + Antigravity)** — docs_ai_ai_handoff_protocol, claude_khatmsaz_project, agents_khatmsaz_project, docs_ai_antigravity_prompt, concept_ai_handoff [EXTRACTED 1.00]
- **Mini-App-Only Login Guard Pattern** — concept_mini_app_only_auth, src_khatmsaz_web_templates_login_adminloginpage, src_khatmsaz_web_templates_creator_login_creatorloginpage, src_khatmsaz_web_templates_mini_app_login_miniapploginpage [EXTRACTED 1.00]
- **Bot User-Facing Content (help, welcome, khatm types)** — help_strings_txt_help_strings, welcome_txt_welcome_message, concept_khatm_types [INFERRED 0.85]
- **PayPing Payment Callback Flow** — docs_dns_cloudflare_fa_payping, rahnama_vps_reverseproxycallback, rahnama_vps_paypingverify, docs_ai_codex_handoff_next_steps_paypingactivation [INFERRED 0.85]
- **Core Domain Modules (Khatm, Participation, Allocation, Workflow)** — module_khatm, module_participation, module_allocation, module_khatm_workflow, module_waiting_list [INFERRED 0.95]

## Communities (230 total, 84 thin omitted)

### Community 0 - "new id()"
Cohesion: 0.03
Nodes (102): build_join_preview_message(), Owner complaint (2026-09-20): the old preview only showed title/…, new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), User, CoverStatus (+94 more)

### Community 1 - "sqlalchemy"
Cohesion: 0.08
Nodes (35): khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, pytest, sqlalchemy, Async SQLAlchemy engine/session setup. One engine for the whole process., UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Identity module: the canonical User and external PlatformIdentity links.…, Khatm module: the core collective-recitation aggregate. (+27 more)

### Community 2 - "get or create()"
Cohesion: 0.05
Nodes (91): InlineKeyboardButton, _lang_for(), _lang_for(), _lang_for(), handle_creator_request_button(), _lang_for(), callback_query, CallbackQuery (+83 more)

### Community 3 - "t()"
Cohesion: 0.08
Nodes (88): csv, list_member_khatms(), message, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group() (+80 more)

### Community 4 - "wallet/service.py"
Cohesion: 0.06
Nodes (83): CouponDiscountType, CouponRedemption, PaymentGateway, PaymentVerification, PendingPayment, cancel_khatm(), Cancel an unused khatm and refund its recorded creation price internally., add_balance() (+75 more)

### Community 5 - "identity/service.py"
Cohesion: 0.10
Nodes (39): aiogram, aiogram_filters, aiogram_types, apscheduler_schedulers_asyncio, Process entrypoint: `python -m khatmsaz.bootstrap`. Starts both bots (whichever…, Small, user-facing Telegram command menu for the primary journeys., # TODO: If we want to check for delegated admin roles with specific permissions,, Account lifecycle commands, including safe account deletion (SPEC Q39). (+31 more)

### Community 6 - "Platform"
Cohesion: 0.11
Nodes (71): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+63 more)

### Community 7 - "Base"
Cohesion: 0.08
Nodes (42): datetime, DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's… (+34 more)

### Community 8 - "start.py"
Cohesion: 0.07
Nodes (61): عضو (Member bots) — تلگرام fa/ar/en و بله, html, handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload(), callback_query, CallbackQuery (+53 more)

### Community 9 - "provider.py"
Cohesion: 0.06
Nodes (49): BaseSettings, dataclasses, hmac, begin_account_link(), FSMContext, message, receive_link_code(), receive_link_phone() (+41 more)

### Community 10 - "panel.py"
Cohesion: 0.06
Nodes (54): QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), سازنده (Creator) — تلگرام, ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه) (+46 more)

### Community 11 - "Khatm"
Cohesion: 0.13
Nodes (54): Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+46 more)

### Community 12 - "keyboards.py"
Cohesion: 0.07
Nodes (50): base64, help_topic(), advertising_choice_keyboard(), capacity_choice_keyboard(), category_choice_keyboard(), _ck_cancel_row(), commitment_mode_keyboard(), confirm_keyboard() (+42 more)

### Community 13 - "allocation/repository.py"
Cohesion: 0.10
Nodes (50): CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion() (+42 more)

### Community 14 - "sqlalchemy ext asyncio"
Cohesion: 0.07
Nodes (36): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_fsm_context, aiogram_fsm_state, functools, pydantic_settings, sqlalchemy_exc (+28 more)

### Community 15 - "typing"
Cohesion: 0.04
Nodes (7): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 17 - "create khatm.py"
Cohesion: 0.15
Nodes (48): _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome(), _apply_coupon_code(), apply_creation_coupon(), _ask_mode() (+40 more)

### Community 18 - "types"
Cohesion: 0.06
Nodes (30): aiogram_enums, aiogram_fsm_storage_memory, contextlib, khatmsaz_bot_handlers, khatmsaz_bot_handlers_start, Update, Regression for per-khatm broadcast targeting (owner request 2026-09-27):…, _text_update() (+22 more)

### Community 19 - "env.py"
Cohesion: 0.05
Nodes (27): asyncio, fixture, logging_config, do_run_migrations(), run_migrations_online(), os, build_body(), main() (+19 more)

### Community 20 - "portions.py"
Cohesion: 0.12
Nodes (44): apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze(), ask_pause_duration(), ask_snooze(), CustomSnooze (+36 more)

### Community 21 - "Participation"
Cohesion: 0.12
Nodes (43): Participation, ParticipationStatus, advance_open_reading(), count_committed_active(), count_for_khatm(), create(), get_active(), get_by_id() (+35 more)

### Community 23 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, GatewayError, PaymentGateway, PaymentRequest, PaymentVerification, Exception, Protocol, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 24 - "advertising/service.py"
Cohesion: 0.08
Nodes (40): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+32 more)

### Community 25 - "reminder engine/service.py"
Cohesion: 0.13
Nodes (37): collections, SendQuranPagesFn, Positive khatm-completion announcements., has_started(), Return whether a scheduled khatm is allowed to deliver work yet., Scheduled positive personal monthly reports., get_preference(), record_sent() (+29 more)

### Community 26 - "reporting/service.py"
Cohesion: 0.08
Nodes (36): deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Claim each eligible announcement once, then notify creator + active members., OpenContribution, create() (+28 more)

### Community 27 - "PlatformIdentity"
Cohesion: 0.09
Nodes (31): PlatformIdentity, UserStatus, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity(), list_platform_identities() (+23 more)

### Community 28 - "test admin web integration.py"
Cohesion: 0.09
Nodes (21): hashlib, httpx, json, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl, re, Session module: opaque-token server-side sessions (used by the future web… (+13 more)

### Community 29 - "plan/service.py"
Cohesion: 0.12
Nodes (34): admin_plans(), List admin-managed plan definitions., PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan (+26 more)

### Community 30 - "UserRole"
Cohesion: 0.11
Nodes (31): BaseFilter, AdminFilter, Checks if the user has admin privileges. For now, we simply check if the user…, _authorized_admin(), _decision_keyboard(), list_manual_phone_requests(), InlineKeyboardMarkup, message (+23 more)

### Community 31 - "safe answer callback()"
Cohesion: 0.19
Nodes (34): KhatmCategoryGroup, ask_creation_coupon(), cancel_wizard(), choose_allowed_platforms(), choose_category(), choose_category_group(), choose_commitment_total(), choose_content_delivery_mode() (+26 more)

### Community 32 - "KhatmCategory"
Cohesion: 0.20
Nodes (31): resolve_bot_category(), KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str, Admin-managed content library for independent devotional families. Owner…, A participant's typed request for a دعا that isn't in the library yet (owner… (+23 more)

### Community 33 - "creator request/service.py"
Cohesion: 0.13
Nodes (31): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user() (+23 more)

### Community 34 - "UserSettings"
Cohesion: 0.08
Nodes (27): delete_account(), Safely deactivate a user while retaining non-PII history. Active committed…, UserSettings, create_for_user(), find_by_contact_phones(), get_by_user(), list_all(), AsyncSession (+19 more)

### Community 35 - "sms subscription/service.py"
Cohesion: 0.14
Nodes (30): _sms_menu_text_and_keyboard(), Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options() (+22 more)

### Community 36 - "app.py"
Cohesion: 0.11
Nodes (30): fastapi, fastapi_staticfiles, fastapi_templating, secrets, _audit_details(), _audit_label(), audit_timeline(), _chunk_devotional() (+22 more)

### Community 37 - "test deep link clears old state before s"
Cohesion: 0.10
Nodes (13): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_join_preview_cancel_always_acknowledges_callback() (+5 more)

### Community 38 - "test registration starts in the users sa"
Cohesion: 0.08
Nodes (16): ProfileEdit, StatesGroup, StatesGroup, Registration, FakeMessage, FakeState, asyncio, integration (+8 more)

### Community 39 - "bot registry/service.py"
Cohesion: 0.19
Nodes (25): cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot(), list_active(), list_active_members() (+17 more)

### Community 40 - "broadcast/service.py"
Cohesion: 0.19
Nodes (26): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, submit_khatm_message() (+18 more)

### Community 41 - "member registration.py"
Cohesion: 0.14
Nodes (27): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+19 more)

### Community 42 - "test fresh committed salawat join asks d"
Cohesion: 0.10
Nodes (20): AskDeliveryHour, JoinWorkflow, StatesGroup, Owner request (2026-09-21): every committed member should be asked what hour…, KhatmInvitation, create(), get_by_token_hash(), mark_accepted() (+12 more)

### Community 43 - "content/service.py"
Cohesion: 0.12
Nodes (26): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., encode_telegram_forward_ref(), get_allowed_reciters(), get_effective_reciter(), get_quran_total_pages(), list_all_devotional_assets(), AsyncSession (+18 more)

### Community 44 - "suggestions.py"
Cohesion: 0.14
Nodes (23): logging, back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, StatesGroup (+15 more)

### Community 45 - "admin()"
Cohesion: 0.26
Nodes (25): AdminPermission, post, RedirectResponse, _admin(), change_admin_role(), create_category(), create_coupon(), decide_broadcast() (+17 more)

### Community 46 - "completion/service.py"
Cohesion: 0.11
Nodes (19): BaseMiddleware, collections_abc, _extract_chat_id(), ModerationMiddleware, Any, Bot-wide moderation gate: a SUSPENDED/BANNED user gets a single friendly…, _reply_blocked(), Idempotent, delayed completion announcements for every platform. (+11 more)

### Community 47 - "Request"
Cohesion: 0.18
Nodes (25): get, Request, admins(), _authenticate_telegram_mini_app(), bots_page(), broadcasts_page(), categories_page(), creator_login() (+17 more)

### Community 48 - "Session"
Cohesion: 0.19
Nodes (22): generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, Session, create(), get_active_by_hash(), AsyncSession, datetime (+14 more)

### Community 49 - "allocation/service.py"
Cohesion: 0.16
Nodes (23): assign_quantity_commitment(), claim_next_open_portion(), complete_current_portion_and_advance(), count_open(), get_current_portion(), list_assigned_positional_portions(), list_for_khatm(), list_latest_portion_per_participation() (+15 more)

### Community 50 - "phone/repository.py"
Cohesion: 0.21
Nodes (23): approve(), OtpChallenge, PhoneClaim, PhoneClaimStatus, create_challenge(), create_or_verify_claim(), get_challenge(), get_user_verified_claim() (+15 more)

### Community 51 - "notification/service.py"
Cohesion: 0.23
Nodes (20): NotificationKind, NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession (+12 more)

### Community 52 - "creator broadcast/service.py"
Cohesion: 0.21
Nodes (19): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+11 more)

### Community 53 - "DevotionalAsset"
Cohesion: 0.14
Nodes (20): deliver_devotional_media(), callback_query, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional_reciter_choice(), DevotionalAsset (+12 more)

### Community 54 - "test confirm wizard resumes and finishes"
Cohesion: 0.12
Nodes (7): ChangePhone, StatesGroup, FakeCallback, FakeMessage, FakeState, integration, test_confirm_wizard_resumes_and_finishes_creation_after_otp()

### Community 55 - "khatm request/repository.py"
Cohesion: 0.27
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 56 - "QuranAssetKind"
Cohesion: 0.16
Nodes (17): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., parse_quran_channel_caption(), quran_channel_coverage(), Return exact 604-page coverage and missing pages for channel forwards., Idempotently load the repository's verified 604-page source map. (+9 more)

### Community 57 - "khatm workflow/service.py"
Cohesion: 0.16
Nodes (15): _count_creator_members(), _enforce_creation_cap(), InvalidCreatorDecisionError, KhatmCancellationError, KhatmUnavailableError, PlanCapExceededError, Exception, KhatmTemplateType (+7 more)

### Community 58 - "message template/repository.py"
Cohesion: 0.20
Nodes (15): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+7 more)

### Community 59 - "complete account link()"
Cohesion: 0.25
Nodes (17): OtpPurpose, str, _assert_pristine_source_account(), complete_account_link(), complete_phone_change(), _consume_challenge(), _hash_code(), OtpError (+9 more)

### Community 60 - "test recitation text only for laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 61 - "admin approve request()"
Cohesion: 0.23
Nodes (16): admin_approve_request(), admin_reject_request(), _lang_for(), callback_query, CallbackQuery, CommandObject, FSMContext, Message (+8 more)

### Community 62 - "ensure creator phone verified()"
Cohesion: 0.26
Nodes (15): begin_phone_change(), ensure_creator_phone_verified(), FSMContext, Message, Return true when creation may continue; otherwise start the OTP step., receive_change_code(), receive_new_phone(), verify_creator_phone() (+7 more)

### Community 63 - "bot registry.py"
Cohesion: 0.23
Nodes (7): BotRegistry, Bot, UUID, Runtime registry of all live Bot instances, built once at startup., set_registry(), BotCategory, str

### Community 64 - "KhatmSaz Project (Claude Code Instructio"
Cohesion: 0.21
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), DEC-PY-0074: Free-tier Plan Caps, DEC-PY-0075: i18n Scope, AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 65 - "Architecture Document"
Cohesion: 0.19
Nodes (14): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, Multi-Bot Architecture (26 bots), No Business Rule Invention Rule, DEC-PY-0001: Long Polling Decision, DEC-PY-0080: 26-Bot Split Architecture (+6 more)

### Community 66 - "Domain Model"
Cohesion: 0.21
Nodes (14): Allocation / Portion Assignment, Commitment Mode (Taahhodi), Khatm (Collective Recitation), Open/Free Mode (Azad), Participation, Surplus / Overflow (Mazad) Logging, Waiting List, Domain Model (+6 more)

### Community 67 - "AsyncSession"
Cohesion: 0.30
Nodes (14): Participation, allocate_next_portion_to(), approve_join_request(), _complete_join(), join_via_token(), leave_khatm(), AsyncSession, Khatm (+6 more)

### Community 68 - "AuditLog"
Cohesion: 0.21
Nodes (13): AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module., Return a bounded newest-first timeline without exposing mutation APIs., record(), list_recent(), AsyncSession (+5 more)

### Community 69 - "ReplyKeyboardMarkup"
Cohesion: 0.22
Nodes (12): creator_finance_keyboard(), creator_management_keyboard(), creator_menu_keyboard(), creator_support_keyboard(), participant_menu_keyboard(), ReplyKeyboardMarkup, test_creator_settings_are_button_driven_and_scope_sensitive(), test_every_emitted_navigation_reply_label_is_reserved_in_every_language() (+4 more)

### Community 70 - "system settings/repository.py"
Cohesion: 0.28
Nodes (10): SystemSetting, get(), list_all(), AsyncSession, set(), get_int(), list_current(), AsyncSession (+2 more)

### Community 71 - "Devotional texts CRUD (dua/ziyarat) admi"
Cohesion: 0.24
Nodes (12): Categories admin page (devotional_slug link), CONTENT_MANAGE permission gate, devotional_assets storage table, Startup devotional text seed (Ashura, Al-Yasin, Faraj, Ahd), Devotional texts CRUD (dua/ziyarat) admin feature, Grouped sidebar/mobile-dock navigation redesign, Auto text chunking (<=3500 chars joined by \x1e), CHANGELOG Archive (until 2026-09-18) (+4 more)

### Community 72 - "create and launch khatm()"
Cohesion: 0.18
Nodes (12): ContentDeliveryMode, CreatorDisplayMode, KhatmAllocationPlan, KhatmTypeEnum, KhatmVisibility, ReminderTone, generate_quran_page_plan(), generate_quran_page_plan_from_boundaries() (+4 more)

### Community 73 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 74 - "manual phone verification/repository.py"
Cohesion: 0.30
Nodes (11): ManualPhoneVerification, create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession, Persistence helpers for foreign-number manual verification. (+3 more)

### Community 75 - "WaitingList"
Cohesion: 0.30
Nodes (10): WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next(), AsyncSession (+2 more)

### Community 76 - "test health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 77 - "test bot commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 78 - "list identities for user()"
Cohesion: 0.51
Nodes (11): approve_leave(), ask_leave_reason(), _do_leave(), _lang_for(), _lang_for_user(), leave_reason_chosen(), callback_query, CallbackQuery (+3 more)

### Community 79 - "begin profile()"
Cohesion: 0.31
Nodes (11): begin_profile(), choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery (+3 more)

### Community 80 - "cancel commitment()"
Cohesion: 0.29
Nodes (10): accept_commitment(), cancel_commitment(), callback_query, CallbackQuery, FSMContext, receive_delivery_hour_button(), _save_delivery_time(), message (+2 more)

### Community 81 - "show wallet()"
Cohesion: 0.27
Nodes (10): create_topup(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery, InlineKeyboardMarkup, Message, show_topup() (+2 more)

### Community 82 - "invite links.py"
Cohesion: 0.20
Nodes (9): build_member_invite_links(), format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Build member-bot deep links for one khatm token. Returns an ordered dict keyed…, Render member-bot links as a readable, multi-line Persian block., Choose one link to encode in a QR: prefer the creator's language and platform,… (+1 more)

### Community 83 - "runtime status.py"
Cohesion: 0.22
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 84 - "test admin template render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 85 - "test bale invite is a real clickable lin"
Cohesion: 0.20
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 86 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 87 - "Multi-Bot Architecture Index Section"
Cohesion: 0.28
Nodes (9): Multi-Bot Architecture Index Section, Admin Token Panel /bots Route (2-step confirmation), bot_instances Database Table, Fernet Token Encryption for Bot Tokens, Creator Bot (ختم‌ساز) Responsibilities, Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), Creator Registration Flow (with OTP) (+1 more)

### Community 88 - "BotRegistry Singleton Class"
Cohesion: 0.22
Nodes (9): Restart Requirement After Token Change, BotRegistry Singleton Class, resolve_bot_category() Function, Post-Creation Invite Link Generation Flow, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link) (+1 more)

### Community 89 - "confirm account deletion()"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

### Community 90 - "positional range for step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 91 - "test message template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 92 - "Creator Role (vs Participant)"
Cohesion: 0.25
Nodes (8): Creator Role (vs Participant), PayPing v3 Payment Gateway, Phone Verification (OTP + Manual), Wallet (Credit + Toman Balance), DEC-PY-0076: Separate Creator/Participant Menus, PayPing Setup Guide (Persian), Module: phone, Module: wallet

### Community 93 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 94 - "Member Bot Language Isolation (fixed per"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 95 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.29
Nodes (8): BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing, allowed_platforms Column (Telegram/Bale/Both), Participant Routing & Platform Limits Task Report

### Community 96 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 97 - "approve join()"
Cohesion: 0.43
Nodes (8): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, reject_join(), Unpack two UUIDs from a short base64 string., unpack_join_callback_data()

### Community 98 - "receive media()"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 99 - "get registry()"
Cohesion: 0.36
Nodes (8): build_notify_fn(), notify(), build_send_quran_pages_fn(), send_quran_pages(), Bot, NotifyFn, Builds the callback `reminder_engine.service.deliver_due_open_quran_reading`…, get_registry()

### Community 101 - "test quran channel source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 102 - "message template/ init .py"
Cohesion: 0.25
Nodes (5): Localized, versioned message templates., Real PostgreSQL coverage for template history and activation control., asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 103 - "test broadcast shows khatm picker()"
Cohesion: 0.25
Nodes (4): khatms(), asyncio, test_broadcast_shows_khatm_picker(), fake_list()

### Community 104 - "test dispatcher routes commands while pr"
Cohesion: 0.25
Nodes (3): asyncio, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 105 - "main()"
Cohesion: 0.38
Nodes (5): Bot, _build_member_bots(), _configure_logging(), main(), _tag_bot()

### Community 106 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 107 - "KhatmSaz PROJECT STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 108 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 109 - "commitment total keyboard()"
Cohesion: 0.33
Nodes (6): _commitment_total_keyboard(), InlineKeyboardMarkup, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 110 - "decide manual phone request()"
Cohesion: 0.33
Nodes (7): decide_manual_phone_request(), callback_query, CallbackQuery, ManualVerificationError, AsyncSession, ValueError, reject()

### Community 111 - "show member portion()"
Cohesion: 0.33
Nodes (7): callback_query, CallbackQuery, FSMContext, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow…, show_member_portion(), show_member_reminder_hours()

### Community 112 - "test member cancel clears state()"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 113 - "join public khatm()"
Cohesion: 0.29
Nodes (7): join_public_khatm(), callback_query, CallbackQuery, FSMContext, create_invitation(), is_registered(), A participant is "registered" once they have a contact phone, province, city,…

### Community 114 - "add devotional audio variant()"
Cohesion: 0.29
Nodes (7): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.…, Owner request (2026-09-22): a dua's image can span more than one page…, Owner request (2026-09-22): a dua's full text as a PDF document — one slot per…, set_devotional_pdf()

### Community 115 - "test contribute blocked until delivery h"
Cohesion: 0.29
Nodes (4): _callback_update(), asyncio, Update, test_contribute_blocked_until_delivery_hour_set()

### Community 117 - "test tapping a time of day button saves "
Cohesion: 0.29
Nodes (4): FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 118 - "test set font size validates and persist"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 119 - "payping callback()"
Cohesion: 0.33
Nodes (6): HTMLResponse, PayPingGateway, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 120 - "set audio()"
Cohesion: 0.53
Nodes (6): CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), content_preferences_keyboard()

### Community 121 - "handle creator request message()"
Cohesion: 0.40
Nodes (6): admin_approve_creator(), admin_reject_creator(), handle_creator_request_message(), CommandObject, message, Submit the request directly from the participant reply-menu button.

### Community 122 - "release portion()"
Cohesion: 0.33
Nodes (6): A missed-deadline portion goes back to the shared OPEN pool — the "emergency…, release_portion(), pause_commitment(), امروز نمی‌رسم" (DOMAIN_MODEL.md §3 Q79): proactively release today's portion…, موقتاً متوقف کن" (DOMAIN_MODEL.md §3 Q80): release any current portion (same as…, skip_today()

### Community 123 - "register devotional text()"
Cohesion: 0.33
Nodes (6): _chunk(), AsyncSession, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), register_devotional_text()

### Community 124 - "test completion announcement waits is id"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 126 - "test next portion is withheld until next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 127 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 128 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 130 - "help start creation()"
Cohesion: 0.50
Nodes (5): help_open_my_khatms(), help_start_creation(), callback_query, CallbackQuery, FSMContext

### Community 131 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.40
Nodes (5): Tooltip Jinja2 Macro Component, Admin Dashboard Page, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 132 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 133 - "Identity Across Platforms (phone-based m"
Cohesion: 0.50
Nodes (4): User Identity and Registration Index Section, Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 134 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 136 - ". call ()"
Cohesion: 0.50
Nodes (3): Any, CallbackQuery, Message

### Community 137 - "set audio callback()"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 138 - "resolve creator decision()"
Cohesion: 0.50
Nodes (4): CommandObject, message, Owner decision (2026-09-21): the missed-portion/emergency-pool system this…, resolve_creator_decision()

### Community 139 - "receive delivery hour()"
Cohesion: 0.50
Nodes (4): _parse_delivery_time(), message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., receive_delivery_hour()

### Community 140 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 141 - "message template/service.py"
Cohesion: 0.50
Nodes (3): Template lookup and safe ``{{placeholder}}`` rendering., Reject malformed or unsupported placeholders before a template is stored., validate_body()

### Community 142 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 143 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 144 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 145 - "Roadmap Phase 1 — First Real Khatm (DONE"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 172 - "resolve user info()"
Cohesion: 1.00
Nodes (3): help_command(), Message, _resolve_user_info()

### Community 173 - "personal report()"
Cohesion: 1.00
Nodes (3): personal_report(), message, report_menu_button()

### Community 174 - "AlreadyParticipatingError"
Cohesion: 0.67
Nodes (3): AlreadyParticipatingError, Exception, Raised when a user tries to join a khatm they already have an ACTIVE…

### Community 175 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 177 - "test devotional slug link does not depen"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

### Community 178 - "test devotional text and platform specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 179 - "test active categories are filtered by t"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_active_categories_are_filtered_by_the_selected_parent_family()

## Knowledge Gaps
- **85 isolated node(s):** `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)`, `هدف افزوده‌شده (مالک، 2026-09-27)` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1146 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **84 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t()` to `new id()`, `get or create()`, `identity/service.py`, `start.py`, `provider.py`, `resolve creator decision()`, `receive delivery hour()`, `keyboards.py`, `panel.py`, `sqlalchemy ext asyncio`, `create khatm.py`, `types`, `env.py`, `portions.py`, `safe answer callback()`, `sms subscription/service.py`, `app.py`, `test registration starts in the users sa`, `member registration.py`, `resolve user info()`, `personal report()`, `suggestions.py`, `DevotionalAsset`, `admin approve request()`, `ensure creator phone verified()`, `ReplyKeyboardMarkup`, `list identities for user()`, `begin profile()`, `cancel commitment()`, `show wallet()`, `test admin template render.py`, `confirm account deletion()`, `approve join()`, `commitment total keyboard()`, `decide manual phone request()`, `show member portion()`, `join public khatm()`, `handle creator request message()`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `t()` to `new id()`, `sqlalchemy`, `get or create()`, `identity/service.py`, `Platform`, `. call ()`, `provider.py`, `start.py`, `allocation/repository.py`, `sqlalchemy ext asyncio`, `env.py`, `advertising/service.py`, `reporting/service.py`, `PlatformIdentity`, `test admin web integration.py`, `plan/service.py`, `UserRole`, `UserSettings`, `test registration starts in the users sa`, `broadcast/service.py`, `test fresh committed salawat join asks d`, `resolve user info()`, `personal report()`, `suggestions.py`, `completion/service.py`, `Session`, `test devotional slug link does not depen`, `test devotional text and platform specif`, `test active categories are filtered by t`, `creator broadcast/service.py`, `DevotionalAsset`, `test confirm wizard resumes and finishes`, `phone/repository.py`, `QuranAssetKind`, `message template/repository.py`, `admin approve request()`, `ensure creator phone verified()`, `AuditLog`, `manual phone verification/repository.py`, `list identities for user()`, `begin profile()`, `cancel commitment()`, `show wallet()`, `test bale invite is a real clickable lin`, `confirm account deletion()`, `approve join()`, `receive media()`, `message template/ init .py`, `decide manual phone request()`, `show member portion()`, `join public khatm()`, `test tapping a time of day button saves `, `set audio()`, `handle creator request message()`, `test completion announcement waits is id`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `new id()`, `sqlalchemy`, `get or create()`, `t()`, `identity/service.py`, `start.py`, `provider.py`, `allocation/repository.py`, `sqlalchemy ext asyncio`, `env.py`, `PlatformIdentity`, `test admin web integration.py`, `plan/service.py`, `UserRole`, `UserSettings`, `test deep link clears old state before s`, `test registration starts in the users sa`, `broadcast/service.py`, `test fresh committed salawat join asks d`, `resolve user info()`, `personal report()`, `suggestions.py`, `completion/service.py`, `phone/repository.py`, `creator broadcast/service.py`, `DevotionalAsset`, `test confirm wizard resumes and finishes`, `complete account link()`, `admin approve request()`, `ensure creator phone verified()`, `bot registry.py`, `test bot commands.py`, `list identities for user()`, `begin profile()`, `cancel commitment()`, `show wallet()`, `invite links.py`, `test bale invite is a real clickable lin`, `confirm account deletion()`, `approve join()`, `receive media()`, `get registry()`, `decide manual phone request()`, `show member portion()`, `join public khatm()`, `set audio()`, `handle creator request message()`, `test completion announcement waits is id`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 195 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 195 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `new id()` be split into smaller, more focused modules?**
  _Cohesion score 0.033129459734964326 - nodes in this community are weakly interconnected._
- **Should `sqlalchemy` be split into smaller, more focused modules?**
  _Cohesion score 0.0795959595959596 - nodes in this community are weakly interconnected._