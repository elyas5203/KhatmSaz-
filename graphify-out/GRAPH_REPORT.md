# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 451 files · ~287,091 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3418 nodes · 11491 edges · 238 communities (151 shown, 87 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 1498 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- new id()
- wallet/service.py
- identity/service.py
- t()
- my khatms.py
- get or create()
- KhatmTypeEnum
- db.py
- invitation/service.py
- admin.py
- Base
- Platform
- Khatm
- allocation/repository.py
- typing
- sqlalchemy dialects
- portions.py
- Participation
- env.py
- advertising/service.py
- panel.py
- bail if menu button()
- alembic
- UserRole
- sqlalchemy ext asyncio
- PayPingGateway
- reporting/service.py
- plan/service.py
- session scope()
- create khatm.py
- creator request/service.py
- settings/models.py
- run once()
- lang()
- KhatmCategory
- test deep link clears old state before s
- test registration starts in the users sa
- sms subscription/service.py
- KavenegarSmsProvider
- main menu keyboard()
- allocation/service.py
- Request
- bot registry/service.py
- app.py
- safe clear inline keyboard()
- phone/service.py
- home keyboard for bot()
- authorization/service.py
- khatm request/models.py
- phone/repository.py
- get
- QuranAssetKind
- help.py
- content/service.py
- notification/service.py
- manage content.py
- khatm request.py
- invite links.py
- broadcast/service.py
- participation/models.py
- suggestions.py
- sqlalchemy
- after welcome()
- DevotionalAsset
- khatm workflow/service.py
- AsyncSession
- test recitation text only for laan.py
- test admin web integration.py
- bot registry.py
- KhatmSaz Project (Claude Code Instructio
- Architecture Document
- Domain Model
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ
- AuditLog
- manual phone verification/repository.py
- message template/repository.py
- test fresh committed salawat join asks d
- test i18n audit.py
- Devotional texts CRUD (dua/ziyarat) admi
- create and launch khatm()
- KhatmSaz VPS Deployment Guide
- WaitingList
- test health.py
- wallet/ init .py
- test bot commands.py
- test confirm wizard resumes and finishes
- monthly report/service.py
- start broadcast()
- runtime status.py
- devotional seed.py
- creator broadcast/service.py
- test broadcast shows khatm picker()
- test admin template render.py
- test bale invite is a real clickable lin
- test dispatcher routes commands while pr
- CSS Layouts and Responsive Design Guide
- Multi-Bot Architecture Index Section
- BotRegistry Singleton Class
- commitment total keyboard()
- confirm account deletion()
- positional range for step()
- test message template.py
- Creator Role (vs Participant)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per
- Multi-Bot (26-bot) Architecture
- qr.py
- test quran channel source.py
- manual phone verification/service.py
- test notification snooze.py
- . call ()
- main()
- Python Requirements
- KhatmSaz PROJECT STATE Log
- PayPing v3 Adapter Integration
- show member portion()
- test member cancel clears state()
- add devotional audio variant()
- UserStatus
- settings/repository.py
- test contribute blocked until delivery h
- FakeState
- test creator finance and support buttons
- FakeMessage
- test tapping a time of day button saves 
- test set font size validates and persist
- payping callback()
- release portion()
- test completion announcement waits is id
- test daily digest combines multiple khat
- test next portion is withheld until next
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earli
- zzz merge three heads 2026 09 28.py
- ask welcome()
- Tooltip Jinja2 Macro Component
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based m
- Settings Menu Full-Button Test Scenario
- 435027907255 add daily deadline hour to 
- admin web login()
- set audio callback()
- iran provinces.py
- quran editions.py
- AccountDeletionBlocked
- public creator name()
- test devotional category navigation.py
- Assignment
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE
- Creator Panel Base Layout Template
- start bot.ps1
- test devotional slug link does not depen
- test devotional text and platform specif
- test active categories are filtered by t
- test reminder tone resolves seeded local
- claude watchdog.sh
- Quran Content Storage (Telegram channel-
- Roadmap Phase 10 — Messenger Mini Apps
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
- callback query
- CallbackQuery
- CommandObject
- FSMContext
- InlineKeyboardMarkup
- Message
- Platform
- StatesGroup
- message
- message
- str
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
1. `t()` - 324 edges
2. `session_scope()` - 278 edges
3. `Platform` - 247 edges
4. `new_id()` - 130 edges
5. `User` - 126 edges
6. `Khatm` - 121 edges
7. `KhatmStatus` - 78 edges
8. `get_or_create()` - 78 edges
9. `safe_answer_callback()` - 77 edges
10. `Base` - 75 edges

## Surprising Connections (you probably didn't know these)
- `رفع‌شدهٔ فاز ۲ (این جلسه، با تست)` --references--> `snooze_keyboard()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/keyboards.py
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py
- `عضو (Member bots) — تلگرام fa/ar/en و بله` --references--> `BotRole`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/modules/bot_registry/models.py
- `سازنده (Creator) — تلگرام` --references--> `handle_creator_finance()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/panel.py
- `سازنده (Creator) — تلگرام` --references--> `handle_creator_management()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/panel.py

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

## Communities (238 total, 87 thin omitted)

### Community 0 - "new id()"
Cohesion: 0.04
Nodes (76): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity() (+68 more)

### Community 1 - "wallet/service.py"
Cohesion: 0.06
Nodes (81): CouponDiscountType, CouponRedemption, PaymentGateway, PaymentVerification, PendingPayment, add_balance(), add_credit(), bind_invoice_resource() (+73 more)

### Community 2 - "identity/service.py"
Cohesion: 0.08
Nodes (50): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types, apscheduler_schedulers_asyncio, html, logging (+42 more)

### Community 3 - "t()"
Cohesion: 0.07
Nodes (77): base64, عضو (Member bots) — تلگرام fa/ar/en و بله, InlineKeyboardButton, handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload(), callback_query (+69 more)

### Community 4 - "my khatms.py"
Cohesion: 0.08
Nodes (75): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at() (+67 more)

### Community 5 - "get or create()"
Cohesion: 0.07
Nodes (75): _lang_for(), CommandObject, send_devotional(), digest_command(), CommandObject, message, CommandObject, message (+67 more)

### Community 6 - "KhatmTypeEnum"
Cohesion: 0.04
Nodes (67): build_join_preview_message(), build_join_success_message(), Shared with `join_requests.py`'s approval handler, which sends this same…, Owner complaint (2026-09-20): the old preview only showed title/…, CoverStatus, KhatmScheduleKind, KhatmTemplateType, KhatmTypeEnum (+59 more)

### Community 7 - "db.py"
Cohesion: 0.10
Nodes (22): khatmsaz_modules_khatm_category_models, pytest, Async SQLAlchemy engine/session setup. One engine for the whole process., UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Identity module: the canonical User and external PlatformIdentity links.…, Khatm module: the core collective-recitation aggregate., Real PostgreSQL coverage for the safe account-deletion boundary., Real PostgreSQL + ASGI coverage for admin khatm search. (+14 more)

### Community 8 - "invitation/service.py"
Cohesion: 0.06
Nodes (57): dataclasses, hashlib, hmac, json, secrets, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).… (+49 more)

### Community 9 - "admin.py"
Cohesion: 0.12
Nodes (62): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+54 more)

### Community 10 - "Base"
Cohesion: 0.10
Nodes (33): datetime, DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's… (+25 more)

### Community 11 - "Platform"
Cohesion: 0.06
Nodes (51): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, functools, pydantic_settings, build_bale_bot(), Bot (+43 more)

### Community 12 - "Khatm"
Cohesion: 0.13
Nodes (53): Khatm, KhatmStatus, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings(), list_pending_completion_announcement_ids() (+45 more)

### Community 13 - "allocation/repository.py"
Cohesion: 0.10
Nodes (50): CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion() (+42 more)

### Community 14 - "typing"
Cohesion: 0.04
Nodes (7): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 16 - "portions.py"
Cohesion: 0.11
Nodes (47): apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze(), ask_pause_duration(), ask_snooze(), CustomSnooze (+39 more)

### Community 17 - "Participation"
Cohesion: 0.12
Nodes (44): Participation, ParticipationStatus, advance_open_reading(), count_committed_active(), count_for_khatm(), create(), get_active(), get_by_id() (+36 more)

### Community 18 - "env.py"
Cohesion: 0.05
Nodes (27): asyncio, fixture, logging_config, do_run_migrations(), run_migrations_online(), os, build_body(), main() (+19 more)

### Community 19 - "advertising/service.py"
Cohesion: 0.08
Nodes (44): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+36 more)

### Community 20 - "panel.py"
Cohesion: 0.08
Nodes (41): khatmsaz_bot_handlers, khatmsaz_modules_identity_models, khatmsaz_modules_wallet, khatmsaz_modules_wallet_gateway, admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel() (+33 more)

### Community 21 - "bail if menu button()"
Cohesion: 0.10
Nodes (41): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+33 more)

### Community 23 - "UserRole"
Cohesion: 0.07
Nodes (42): choose_gender(), choose_province(), callback_query, CallbackQuery, join_public_khatm(), callback_query, CallbackQuery, FSMContext (+34 more)

### Community 24 - "sqlalchemy ext asyncio"
Cohesion: 0.07
Nodes (31): collections, collections_abc, sqlalchemy_ext_asyncio, Positive khatm-completion announcements., deliver_pending(), _message(), AsyncSession, datetime (+23 more)

### Community 25 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, GatewayError, PaymentGateway, PaymentRequest, PaymentVerification, Exception, Protocol, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 26 - "reporting/service.py"
Cohesion: 0.08
Nodes (35): KhatmInvitation, OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between() (+27 more)

### Community 27 - "plan/service.py"
Cohesion: 0.11
Nodes (36): admin_plan_set(), admin_plans(), List admin-managed plan definitions., Set a plan's pricing mode, price, and comma-separated entitlements., PlanDefinition, PlanTier, PricingMode, str (+28 more)

### Community 28 - "session scope()"
Cohesion: 0.08
Nodes (32): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, Creator message requests with mandatory admin moderation. (+24 more)

### Community 29 - "create khatm.py"
Cohesion: 0.16
Nodes (36): CommandObject, FSMContext, Message, _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _apply_coupon_code() (+28 more)

### Community 30 - "creator request/service.py"
Cohesion: 0.13
Nodes (31): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user() (+23 more)

### Community 31 - "settings/models.py"
Cohesion: 0.08
Nodes (15): aiogram_fsm_storage_memory, contextlib, khatmsaz_bot_handlers_start, User settings module: per-user configurable preferences (1:1 extension of User)., Real PostgreSQL self-service platform/account linking flow., Regression for per-khatm broadcast targeting (owner request 2026-09-27):…, Regression (owner live QA 2026-09-28): right after joining a commitment khatm…, Owner-reported bug (2026-09-21/22): a first-time creator with an unverified… (+7 more)

### Community 32 - "run once()"
Cohesion: 0.16
Nodes (32): SendQuranPagesFn, has_started(), Return whether a scheduled khatm is allowed to deliver work yet., already_sent_today(), get_preference(), record_sent(), _default_reminder_hour(), delegate_inactive_portions() (+24 more)

### Community 33 - "lang()"
Cohesion: 0.16
Nodes (31): callback_query, CallbackQuery, KhatmCategoryGroup, Platform, ask_creation_coupon(), _ask_mode(), cancel_wizard(), choose_allowed_platforms() (+23 more)

### Community 34 - "KhatmCategory"
Cohesion: 0.22
Nodes (29): KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str, A participant's typed request for a دعا that isn't in the library yet (owner…, create(), create_request() (+21 more)

### Community 35 - "test deep link clears old state before s"
Cohesion: 0.10
Nodes (13): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_join_preview_cancel_always_acknowledges_callback() (+5 more)

### Community 36 - "test registration starts in the users sa"
Cohesion: 0.08
Nodes (16): ProfileEdit, StatesGroup, StatesGroup, Registration, FakeMessage, FakeState, asyncio, integration (+8 more)

### Community 37 - "sms subscription/service.py"
Cohesion: 0.15
Nodes (28): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+20 more)

### Community 38 - "KavenegarSmsProvider"
Cohesion: 0.12
Nodes (19): KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Submit one SMS and return a normalized provider result. `otp_code`, when given,…, Safe default: never sends externally and reports why it did not., Direct SMS adapter for Kavenegar's REST ``sms/send`` endpoint., SmsSendResult, asyncio (+11 more)

### Community 39 - "main menu keyboard()"
Cohesion: 0.14
Nodes (25): BaseSettings, begin_account_link(), _lang_for(), FSMContext, message, receive_link_code(), receive_link_phone(), begin_phone_change() (+17 more)

### Community 40 - "allocation/service.py"
Cohesion: 0.13
Nodes (27): KhatmAllocationPlan, assign_quantity_commitment(), claim_next_open_portion(), complete_current_portion_and_advance(), count_open(), generate_quran_page_plan(), generate_quran_page_plan_from_boundaries(), get_current_portion() (+19 more)

### Community 41 - "Request"
Cohesion: 0.28
Nodes (27): AdminPermission, post, RedirectResponse, Request, _admin(), change_admin_role(), create_category(), create_coupon() (+19 more)

### Community 42 - "bot registry/service.py"
Cohesion: 0.20
Nodes (25): cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot(), list_active(), list_active_members() (+17 more)

### Community 43 - "app.py"
Cohesion: 0.12
Nodes (26): fastapi, fastapi_staticfiles, fastapi_templating, middleware, _authenticate_telegram_mini_app(), _chunk_devotional(), _creator(), _creator_ctx() (+18 more)

### Community 44 - "safe clear inline keyboard()"
Cohesion: 0.19
Nodes (25): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, reject_join(), approve_leave(), ask_leave_reason() (+17 more)

### Community 45 - "phone/service.py"
Cohesion: 0.21
Nodes (24): sqlalchemy_exc, AccountMerge, OtpPurpose, _assert_pristine_source_account(), complete_account_link(), complete_phone_change(), _consume_challenge(), _hash_code() (+16 more)

### Community 46 - "home keyboard for bot()"
Cohesion: 0.15
Nodes (23): CommandObject, Message, Per-user translation/tafsir display preferences., _set_audio(), set_audio_command(), set_content_option(), accept_commitment(), cancel_commitment() (+15 more)

### Community 47 - "authorization/service.py"
Cohesion: 0.16
Nodes (23): admin_list_requests(), AdminRole, AdminRoleGrant, CapabilityType, str, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants() (+15 more)

### Community 48 - "khatm request/models.py"
Cohesion: 0.18
Nodes (20): KhatmRequest, KhatmRequestStatus, str, Khatm-request module: a creator asking for a khatm type not in the picker yet…, create(), get_by_id(), list_pending(), AsyncSession (+12 more)

### Community 49 - "phone/repository.py"
Cohesion: 0.20
Nodes (24): approve(), OtpChallenge, PhoneClaim, PhoneClaimStatus, str, create_challenge(), create_or_verify_claim(), get_challenge() (+16 more)

### Community 50 - "get"
Cohesion: 0.13
Nodes (24): get, admins(), _audit_details(), _audit_label(), audit_timeline(), bots_page(), broadcasts_page(), categories_page() (+16 more)

### Community 51 - "QuranAssetKind"
Cohesion: 0.13
Nodes (24): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), parse_quran_channel_caption(), quran_channel_coverage(), Idempotently map one source-channel post to every page it covers. (+16 more)

### Community 52 - "help.py"
Cohesion: 0.16
Nodes (21): help_command(), help_open_my_khatms(), help_start_creation(), help_topic(), callback_query, CallbackQuery, FSMContext, Message (+13 more)

### Community 53 - "content/service.py"
Cohesion: 0.15
Nodes (21): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., get_allowed_reciters(), get_devotional_asset(), get_effective_reciter(), list_all_devotional_assets(), AsyncSession, Quran media registry, reciter whitelist, and user delivery resolution. (+13 more)

### Community 54 - "notification/service.py"
Cohesion: 0.22
Nodes (20): NotificationKind, NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession (+12 more)

### Community 55 - "manage content.py"
Cohesion: 0.13
Nodes (17): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…, finish_manage_content(), ManageContentState (+9 more)

### Community 56 - "khatm request.py"
Cohesion: 0.22
Nodes (19): admin_approve_request(), admin_reject_request(), _lang_for(), callback_query, CallbackQuery, CommandObject, FSMContext, Message (+11 more)

### Community 57 - "invite links.py"
Cohesion: 0.12
Nodes (18): build_member_invite_links(), format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Build member-bot deep links for one khatm token. Returns an ordered dict keyed…, Render member-bot links as a readable, multi-line Persian block., Choose one link to encode in a QR: prefer the creator's language and platform,… (+10 more)

### Community 58 - "broadcast/service.py"
Cohesion: 0.29
Nodes (18): BroadcastStatus, KhatmBroadcast, str, create(), get_by_id(), list_pending(), mark_reviewed(), mark_sent() (+10 more)

### Community 59 - "participation/models.py"
Cohesion: 0.13
Nodes (10): openpyxl, Per-khatm advertising opt-in and reward-credit accrual., Open-contribution module: freely-recorded contributions in an OPEN khatm., AssignmentStatus, AssignmentUnitKind, Participation module: a user's membership in a Khatm, and per-participant…, str, Real PostgreSQL + ASGI coverage for the creator-owned dashboard. (+2 more)

### Community 60 - "suggestions.py"
Cohesion: 0.22
Nodes (17): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, StatesGroup, User feedback/bug-report inbox to admins (owner request, 2026-09-21). Updated… (+9 more)

### Community 61 - "sqlalchemy"
Cohesion: 0.20
Nodes (7): khatmsaz_modules_khatm_category, sqlalchemy, Content preferences and per-khatm reciter policy., BACKLOG.md §14 fix (2026-09-21): replace the fragile name-matching hack…, Owner request (2026-09-22): a devotional asset (dua/ziyarat) can now have more…, Real PostgreSQL filtering proof for independent devotional families., Real PostgreSQL coverage for template history and activation control.

### Community 62 - "after welcome()"
Cohesion: 0.15
Nodes (16): _after_welcome(), _compose_welcome_with_contact(), enter_creator_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, skip_creator_contact(), use_own_contact() (+8 more)

### Community 63 - "DevotionalAsset"
Cohesion: 0.16
Nodes (17): deliver_devotional_media(), InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), DevotionalAsset, DevotionalMedia, Admin-curated complete text/audio for a dua or ziyarat. (+9 more)

### Community 64 - "khatm workflow/service.py"
Cohesion: 0.15
Nodes (13): InvalidCreatorDecisionError, JoinRequiresApprovalError, KhatmCancellationError, KhatmUnavailableError, PlanCapExceededError, Exception, Cross-module orchestration for the khatm creation wizard, join/leave flow, and…, Raised by `join_via_token` for a PRIVATE khatm (DOMAIN_MODEL.md §2 Q65-66) the… (+5 more)

### Community 65 - "AsyncSession"
Cohesion: 0.25
Nodes (16): Participation, allocate_next_portion_to(), approve_join_request(), cancel_khatm(), _complete_join(), join_via_token(), leave_khatm(), AsyncSession (+8 more)

### Community 66 - "test recitation text only for laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 67 - "test admin web integration.py"
Cohesion: 0.17
Nodes (8): httpx, re, Real PostgreSQL coverage for plan controls exposed in the admin Mini App., Real PostgreSQL pagination coverage for large Mini App lists., Real PostgreSQL coverage for revocable delegated admin roles., Real PostgreSQL coverage for secure admin web sessions., Real PostgreSQL + ASGI coverage for the admin dashboard entry flow., PostgreSQL + ASGI proof for Telegram Mini App admin authentication.

### Community 68 - "bot registry.py"
Cohesion: 0.23
Nodes (7): BotRegistry, Bot, UUID, Runtime registry of all live Bot instances, built once at startup., set_registry(), BotCategory, str

### Community 69 - "KhatmSaz Project (Claude Code Instructio"
Cohesion: 0.21
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), DEC-PY-0074: Free-tier Plan Caps, DEC-PY-0075: i18n Scope, AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 70 - "Architecture Document"
Cohesion: 0.19
Nodes (14): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, Multi-Bot Architecture (26 bots), No Business Rule Invention Rule, DEC-PY-0001: Long Polling Decision, DEC-PY-0080: 26-Bot Split Architecture (+6 more)

### Community 71 - "Domain Model"
Cohesion: 0.21
Nodes (14): Allocation / Portion Assignment, Commitment Mode (Taahhodi), Khatm (Collective Recitation), Open/Free Mode (Azad), Participation, Surplus / Overflow (Mazad) Logging, Waiting List, Domain Model (+6 more)

### Community 72 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ"
Cohesion: 0.15
Nodes (13): QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), سازنده (Creator) — تلگرام, ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه) (+5 more)

### Community 73 - "AuditLog"
Cohesion: 0.19
Nodes (12): AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module., Return a bounded newest-first timeline without exposing mutation APIs., record(), list_recent(), AsyncSession (+4 more)

### Community 74 - "manual phone verification/repository.py"
Cohesion: 0.27
Nodes (13): ManualPhoneVerification, create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession, Persistence helpers for foreign-number manual verification. (+5 more)

### Community 75 - "message template/repository.py"
Cohesion: 0.26
Nodes (13): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+5 more)

### Community 76 - "test fresh committed salawat join asks d"
Cohesion: 0.18
Nodes (7): FakeMessage, FakeState, asyncio, integration, Owner request 2026-09-22: delivery-hour question must fire for salawat…, test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it(), test_fresh_committed_salawat_join_asks_delivery_hour()

### Community 77 - "test i18n audit.py"
Cohesion: 0.17
Nodes (6): ast, pathlib, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source(), Guards against the raw-slug / Persian-on-other-language class of bug the owner…

### Community 78 - "Devotional texts CRUD (dua/ziyarat) admi"
Cohesion: 0.24
Nodes (12): Categories admin page (devotional_slug link), CONTENT_MANAGE permission gate, devotional_assets storage table, Startup devotional text seed (Ashura, Al-Yasin, Faraj, Ahd), Devotional texts CRUD (dua/ziyarat) admin feature, Grouped sidebar/mobile-dock navigation redesign, Auto text chunking (<=3500 chars joined by \x1e), CHANGELOG Archive (until 2026-09-18) (+4 more)

### Community 79 - "create and launch khatm()"
Cohesion: 0.20
Nodes (12): ContentDeliveryMode, CreatorDisplayMode, KhatmTypeEnum, KhatmVisibility, ReminderTone, _count_creator_members(), create_and_launch_khatm(), _enforce_creation_cap() (+4 more)

### Community 80 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 81 - "WaitingList"
Cohesion: 0.30
Nodes (10): WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next(), AsyncSession (+2 more)

### Community 82 - "test health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 83 - "wallet/ init .py"
Cohesion: 0.18
Nodes (6): khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, Real PostgreSQL coverage for bounded, auditable coupon redemption., PostgreSQL + ASGI coverage for the public PayPing callback., Financial safety regression for SMS subscription purchases., Real PostgreSQL coverage for payment ownership and replay protection.

### Community 84 - "test bot commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 85 - "test confirm wizard resumes and finishes"
Cohesion: 0.20
Nodes (6): ChangePhone, StatesGroup, FakeCallback, FakeMessage, integration, test_confirm_wizard_resumes_and_finishes_creation_after_otp()

### Community 86 - "monthly report/service.py"
Cohesion: 0.25
Nodes (9): deliver_due(), _previous_month_bounds(), AsyncSession, datetime, NotifyFn, Timezone-aware, idempotent delivery of the previous month's progress., _render(), Personal and creator reporting services. (+1 more)

### Community 87 - "start broadcast()"
Cohesion: 0.36
Nodes (10): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+2 more)

### Community 88 - "runtime status.py"
Cohesion: 0.22
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 89 - "devotional seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 90 - "creator broadcast/service.py"
Cohesion: 0.40
Nodes (9): CreatorBroadcast, calculate_broadcast_cost(), create_broadcast(), get_broadcast_audience(), get_broadcast_count_last_7_days(), get_creator_audience_count(), AsyncSession, UUID (+1 more)

### Community 91 - "test broadcast shows khatm picker()"
Cohesion: 0.20
Nodes (6): khatms(), asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 92 - "test admin template render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 93 - "test bale invite is a real clickable lin"
Cohesion: 0.20
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 94 - "test dispatcher routes commands while pr"
Cohesion: 0.20
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 95 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 96 - "Multi-Bot Architecture Index Section"
Cohesion: 0.28
Nodes (9): Multi-Bot Architecture Index Section, Admin Token Panel /bots Route (2-step confirmation), bot_instances Database Table, Fernet Token Encryption for Bot Tokens, Creator Bot (ختم‌ساز) Responsibilities, Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), Creator Registration Flow (with OTP) (+1 more)

### Community 97 - "BotRegistry Singleton Class"
Cohesion: 0.22
Nodes (9): Restart Requirement After Token Change, BotRegistry Singleton Class, resolve_bot_category() Function, Post-Creation Invite Link Generation Flow, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link) (+1 more)

### Community 98 - "commitment total keyboard()"
Cohesion: 0.25
Nodes (8): InlineKeyboardMarkup, _commitment_total_keyboard(), _creator_contact_keyboard(), R4: creator sets a contact handle shown in the member welcome. Offers a one-tap…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 99 - "confirm account deletion()"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

### Community 100 - "positional range for step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 101 - "test message template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 102 - "Creator Role (vs Participant)"
Cohesion: 0.25
Nodes (8): Creator Role (vs Participant), PayPing v3 Payment Gateway, Phone Verification (OTP + Manual), Wallet (Credit + Toman Balance), DEC-PY-0076: Separate Creator/Participant Menus, PayPing Setup Guide (Persian), Module: phone, Module: wallet

### Community 103 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 104 - "Member Bot Language Isolation (fixed per"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 105 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.29
Nodes (8): BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing, allowed_platforms Column (Telegram/Bale/Both), Participant Routing & Platform Limits Task Report

### Community 106 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 107 - "test quran channel source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 108 - "manual phone verification/service.py"
Cohesion: 0.39
Nodes (7): ManualVerificationError, AsyncSession, ValueError, Manual verification for foreign numbers that cannot receive Iranian SMS., reject(), requires_manual_review(), submit()

### Community 109 - "test notification snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 110 - ". call ()"
Cohesion: 0.38
Nodes (6): BaseMiddleware, _extract_chat_id(), ModerationMiddleware, Any, _reply_blocked(), TelegramObject

### Community 111 - "main()"
Cohesion: 0.38
Nodes (5): Bot, _build_member_bots(), _configure_logging(), main(), _tag_bot()

### Community 112 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 113 - "KhatmSaz PROJECT STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 114 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 115 - "show member portion()"
Cohesion: 0.33
Nodes (7): callback_query, CallbackQuery, FSMContext, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow…, show_member_portion(), show_member_reminder_hours()

### Community 116 - "test member cancel clears state()"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 117 - "add devotional audio variant()"
Cohesion: 0.29
Nodes (7): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.…, Owner request (2026-09-22): a dua's image can span more than one page…, Owner request (2026-09-22): a dua's full text as a PDF document — one slot per…, set_devotional_pdf()

### Community 118 - "UserStatus"
Cohesion: 0.48
Nodes (7): UserStatus, set_status(), ban(), is_blocked(), reactivate(), suspend(), warn()

### Community 119 - "settings/repository.py"
Cohesion: 0.43
Nodes (6): create_for_user(), find_by_contact_phones(), get_by_user(), list_all(), AsyncSession, Persistence access for settings — the only place that runs SQL for this module.

### Community 120 - "test contribute blocked until delivery h"
Cohesion: 0.29
Nodes (4): _callback_update(), asyncio, Update, test_contribute_blocked_until_delivery_hour_set()

### Community 122 - "test creator finance and support buttons"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 124 - "test tapping a time of day button saves "
Cohesion: 0.29
Nodes (4): FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 125 - "test set font size validates and persist"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 126 - "payping callback()"
Cohesion: 0.33
Nodes (6): HTMLResponse, PayPingGateway, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 127 - "release portion()"
Cohesion: 0.33
Nodes (6): A missed-deadline portion goes back to the shared OPEN pool — the "emergency…, release_portion(), pause_commitment(), امروز نمی‌رسم" (DOMAIN_MODEL.md §3 Q79): proactively release today's portion…, موقتاً متوقف کن" (DOMAIN_MODEL.md §3 Q80): release any current portion (same as…, skip_today()

### Community 128 - "test completion announcement waits is id"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 130 - "test next portion is withheld until next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 131 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 132 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 133 - "zzz merge three heads 2026 09 28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 134 - "ask welcome()"
Cohesion: 0.50
Nodes (5): _ask_welcome(), _compose_niyyat(), enter_niyyat(), Owner rule (2026-09-27, DEC-PY-0090): the niyyat is FIXED for every khatm — «به…, skip_niyyat()

### Community 135 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.40
Nodes (5): Tooltip Jinja2 Macro Component, Admin Dashboard Page, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 136 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 137 - "Identity Across Platforms (phone-based m"
Cohesion: 0.50
Nodes (4): User Identity and Registration Index Section, Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 138 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 140 - "admin web login()"
Cohesion: 0.50
Nodes (4): admin_web_login(), admin_web_login_button(), callback_query, Open the signed Telegram Mini App for an authorized administrator.

### Community 141 - "set audio callback()"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 142 - "iran provinces.py"
Cohesion: 0.50
Nodes (3): province_labels(), The 31 official Iranian provinces (ostan) — stable, government-recognized list,…, Localized labels in the exact canonical `IRAN_PROVINCES` order.

### Community 143 - "quran editions.py"
Cohesion: 0.33
Nodes (3): get_quran_total_pages(), Total page count for a Quran khatm's edition. OPEN QURAN_PAGE khatms already…, Static Quran edition registry — total page counts per edition. Mirrors the…

### Community 144 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 145 - "public creator name()"
Cohesion: 0.50
Nodes (4): _public_creator_name(), public_join_landing(), Khatm, User

### Community 146 - "test devotional category navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 147 - "Assignment"
Cohesion: 0.67
Nodes (3): Base, Assignment, The Phase-4 flat per-khatm assignment (legacy shape, kept for parity). The…

### Community 148 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 149 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 150 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 151 - "Roadmap Phase 1 — First Real Khatm (DONE"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 179 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 181 - "test devotional slug link does not depen"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

### Community 182 - "test devotional text and platform specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 183 - "test active categories are filtered by t"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_active_categories_are_filtered_by_the_selected_parent_family()

### Community 184 - "test reminder tone resolves seeded local"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

## Knowledge Gaps
- **85 isolated node(s):** `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)`, `هدف افزوده‌شده (مالک، 2026-09-27)` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1167 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **87 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t()` to `new id()`, `identity/service.py`, `my khatms.py`, `get or create()`, `ask welcome()`, `KhatmTypeEnum`, `Platform`, `portions.py`, `env.py`, `panel.py`, `bail if menu button()`, `UserRole`, `session scope()`, `create khatm.py`, `lang()`, `test registration starts in the users sa`, `main menu keyboard()`, `app.py`, `safe clear inline keyboard()`, `home keyboard for bot()`, `help.py`, `khatm request.py`, `suggestions.py`, `after welcome()`, `DevotionalAsset`, `QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ`, `test admin template render.py`, `commitment total keyboard()`, `confirm account deletion()`, `show member portion()`, `test creator finance and support buttons`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `Architecture Document` connect `Architecture Document` to `identity/service.py`, `KhatmSaz README`, `KhatmSaz Project (Claude Code Instructio`, `Creator Role (vs Participant)`, `Domain Model`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session scope()` to `new id()`, `test completion announcement waits is id`, `identity/service.py`, `test next portion is withheld until next`, `my khatms.py`, `get or create()`, `KhatmTypeEnum`, `db.py`, `invitation/service.py`, `admin.py`, `Platform`, `allocation/repository.py`, `env.py`, `advertising/service.py`, `bail if menu button()`, `UserRole`, `reporting/service.py`, `plan/service.py`, `test registration starts in the users sa`, `main menu keyboard()`, `safe clear inline keyboard()`, `home keyboard for bot()`, `authorization/service.py`, `khatm request/models.py`, `phone/repository.py`, `QuranAssetKind`, `help.py`, `test devotional slug link does not depen`, `test devotional text and platform specif`, `manage content.py`, `khatm request.py`, `test active categories are filtered by t`, `test reminder tone resolves seeded local`, `suggestions.py`, `DevotionalAsset`, `AuditLog`, `manual phone verification/repository.py`, `message template/repository.py`, `test fresh committed salawat join asks d`, `test confirm wizard resumes and finishes`, `start broadcast()`, `test bale invite is a real clickable lin`, `confirm account deletion()`, `. call ()`, `show member portion()`, `test tapping a time of day button saves `?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 195 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 195 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `new id()` be split into smaller, more focused modules?**
  _Cohesion score 0.04205851619644723 - nodes in this community are weakly interconnected._
- **Should `wallet/service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05759623861298854 - nodes in this community are weakly interconnected._