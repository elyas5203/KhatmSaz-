# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 450 files · ~286,675 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3413 nodes · 11488 edges · 222 communities (135 shown, 87 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 1498 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- identity/service.py
- sqlalchemy
- bot registry/service.py
- t()
- wallet/service.py
- Platform
- new id()
- sqlalchemy ext asyncio
- Base
- session scope()
- phone/service.py
- portions.py
- KhatmTypeEnum
- admin.py
- Khatm
- allocation/repository.py
- bail if menu button()
- typing
- sqlalchemy dialects
- Participation
- env.py
- alembic
- panel.py
- PayPingGateway
- reporting/service.py
- provider.py
- test confirm wizard resumes and finishes
- plan/service.py
- config.py
- create khatm.py
- settings menu.py
- reminder engine/service.py
- get notify fn()
- creator request/service.py
- app.py
- lang()
- authorization/service.py
- test registration starts in the users sa
- test deep link clears old state before s
- sms subscription/service.py
- Request
- allocation/service.py
- admin()
- resume join after registration()
- message template/repository.py
- DevotionalAsset
- UserRole
- notification/service.py
- completion/service.py
- content/service.py
- AsyncSession
- khatm request/repository.py
- AsyncSession
- after welcome()
- QuranAssetKind
- khatm workflow/service.py
- create and launch khatm()
- test recitation text only for laan.py
- test mini app auth integration.py
- KhatmSaz Project (Claude Code Instructio
- Architecture Document
- Domain Model
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ
- test fresh committed salawat join asks d
- start suggestion()
- JoinRequiresApprovalError
- test i18n audit.py
- Devotional texts CRUD (dua/ziyarat) admi
- KhatmSaz VPS Deployment Guide
- test health.py
- get settings()
- test bot commands.py
- cancel commitment()
- test picking a reciter via settings menu
- runtime status.py
- devotional seed.py
- test admin template render.py
- test bale invite is a real clickable lin
- test dispatcher routes commands while pr
- CSS Layouts and Responsive Design Guide
- Multi-Bot Architecture Index Section
- BotRegistry Singleton Class
- commitment total keyboard()
- confirm account deletion()
- positional range for step()
- test broadcast shows khatm picker()
- AdminFilter
- Creator Role (vs Participant)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per
- Multi-Bot (26-bot) Architecture
- qr.py
- moderate()
- receive media()
- test quran channel source.py
- creator broadcast/service.py
- system settings/service.py
- system settings/repository.py
- test notification snooze.py
- test set font size validates and persist
- . call ()
- main()
- Python Requirements
- KhatmSaz PROJECT STATE Log
- PayPing v3 Adapter Integration
- test member cancel clears state()
- test contribute blocked until delivery h
- FakeState
- test creator finance and support buttons
- FakeMessage
- test tapping a time of day button saves 
- test public khatms reply button is wired
- payping callback()
- release portion()
- delete account()
- test completion announcement waits is id
- test daily digest combines multiple khat
- test next portion is withheld until next
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earli
- zzz merge three heads 2026 09 28.py
- ask welcome()
- Tooltip Jinja2 Macro Component
- test render uses fallback locale()
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based m
- Settings Menu Full-Button Test Scenario
- 435027907255 add daily deadline hour to 
- resolve creator decision()
- audit log/service.py
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE
- str
- str
- AlreadyParticipatingError
- Creator Panel Base Layout Template
- start bot.ps1
- test devotional slug link does not depen
- test devotional text and platform specif
- test reminder tone resolves seeded local
- claude watchdog.sh
- Quran Content Storage (Telegram channel-
- Roadmap Phase 10 — Messenger Mini Apps
- broadcast/ init .py
- completion/ init .py
- monthly report/ init .py
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
8. `Base` - 78 edges
9. `get_or_create()` - 78 edges
10. `safe_answer_callback()` - 77 edges

## Surprising Connections (you probably didn't know these)
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py
- `رفع‌شدهٔ فاز ۲ (این جلسه، با تست)` --references--> `snooze_keyboard()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/keyboards.py
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

## Communities (222 total, 87 thin omitted)

### Community 0 - "identity/service.py"
Cohesion: 0.06
Nodes (75): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types, apscheduler_schedulers_asyncio, html, logging (+67 more)

### Community 1 - "sqlalchemy"
Cohesion: 0.07
Nodes (40): khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, pytest, sqlalchemy, Async SQLAlchemy engine/session setup. One engine for the whole process., UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Persistence access for the append-only audit module., Content preferences and per-khatm reciter policy. (+32 more)

### Community 2 - "bot registry/service.py"
Cohesion: 0.05
Nodes (83): cryptography_fernet, Fernet, format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Render member-bot links as a readable, multi-line Persian block., Choose one link to encode in a QR: prefer the creator's language and platform,… (+75 more)

### Community 3 - "t()"
Cohesion: 0.06
Nodes (92): base64, InlineKeyboardButton, help_command(), help_open_my_khatms(), help_start_creation(), help_topic(), callback_query, CallbackQuery (+84 more)

### Community 4 - "wallet/service.py"
Cohesion: 0.05
Nodes (91): CouponDiscountType, CouponRedemption, PaymentGateway, PaymentVerification, PendingPayment, AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action() (+83 more)

### Community 5 - "Platform"
Cohesion: 0.04
Nodes (94): _lang_for(), _lang_for(), CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), _lang_for() (+86 more)

### Community 6 - "new id()"
Cohesion: 0.04
Nodes (84): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), AuditLog, list_recent(), AsyncSession, Return a bounded newest-first timeline without exposing mutation APIs. (+76 more)

### Community 7 - "sqlalchemy ext asyncio"
Cohesion: 0.05
Nodes (75): dataclasses, hashlib, hmac, secrets, sqlalchemy_ext_asyncio, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).… (+67 more)

### Community 8 - "Base"
Cohesion: 0.07
Nodes (43): datetime, DeclarativeBase, enum, openpyxl, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models. (+35 more)

### Community 9 - "session scope()"
Cohesion: 0.08
Nodes (80): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at() (+72 more)

### Community 10 - "phone/service.py"
Cohesion: 0.06
Nodes (75): sqlalchemy_exc, ensure_creator_phone_verified(), FSMContext, Message, Return true when creation may continue; otherwise start the OTP step., receive_new_phone(), verify_creator_phone(), notify_admins_of_manual_request() (+67 more)

### Community 11 - "portions.py"
Cohesion: 0.07
Nodes (76): callback_query, CallbackQuery, quran_help(), set_audio_callback(), cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query (+68 more)

### Community 12 - "KhatmTypeEnum"
Cohesion: 0.04
Nodes (64): build_join_preview_message(), Owner complaint (2026-09-20): the old preview only showed title/…, CoverStatus, KhatmScheduleKind, KhatmTemplateType, KhatmTypeEnum, str, ReminderTone (+56 more)

### Community 13 - "admin.py"
Cohesion: 0.12
Nodes (57): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+49 more)

### Community 14 - "Khatm"
Cohesion: 0.13
Nodes (54): Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+46 more)

### Community 15 - "allocation/repository.py"
Cohesion: 0.09
Nodes (53): CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion() (+45 more)

### Community 16 - "bail if menu button()"
Cohesion: 0.06
Nodes (54): begin_account_link(), FSMContext, message, receive_link_code(), receive_link_phone(), receive_change_code(), choose_gender(), choose_province() (+46 more)

### Community 17 - "typing"
Cohesion: 0.04
Nodes (7): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 19 - "Participation"
Cohesion: 0.12
Nodes (45): get_broadcast_audience(), Participation, ParticipationStatus, advance_open_reading(), count_committed_active(), count_for_khatm(), create(), get_active() (+37 more)

### Community 20 - "env.py"
Cohesion: 0.05
Nodes (27): asyncio, fixture, logging_config, do_run_migrations(), run_migrations_online(), os, build_body(), main() (+19 more)

### Community 22 - "panel.py"
Cohesion: 0.09
Nodes (40): khatmsaz_modules_identity_models, khatmsaz_modules_wallet, khatmsaz_modules_wallet_gateway, admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel(), handle_admin_panel_broadcast() (+32 more)

### Community 23 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, GatewayError, PaymentGateway, PaymentRequest, PaymentVerification, Exception, Protocol, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 24 - "reporting/service.py"
Cohesion: 0.08
Nodes (36): KhatmInvitation, OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between() (+28 more)

### Community 25 - "provider.py"
Cohesion: 0.10
Nodes (27): BaseSettings, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Protocol (+19 more)

### Community 26 - "test confirm wizard resumes and finishes"
Cohesion: 0.08
Nodes (34): ChangePhone, StatesGroup, CouponRedemption, DiscountCoupon, InvoiceKind, InvoiceStatus, str, Immutable purchase amounts plus a small paid/refunded lifecycle. (+26 more)

### Community 27 - "plan/service.py"
Cohesion: 0.11
Nodes (36): admin_plan_set(), admin_plans(), List admin-managed plan definitions., Set a plan's pricing mode, price, and comma-separated entitlements., PlanDefinition, PlanTier, PricingMode, str (+28 more)

### Community 28 - "config.py"
Cohesion: 0.08
Nodes (22): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, aiogram_fsm_storage_memory, contextlib, functools, khatmsaz_bot_handlers (+14 more)

### Community 29 - "create khatm.py"
Cohesion: 0.16
Nodes (36): CommandObject, FSMContext, Message, _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _apply_coupon_code() (+28 more)

### Community 30 - "settings menu.py"
Cohesion: 0.15
Nodes (36): begin_phone_change(), buy_sms_plan(), _current_platform_user(), _lang_for(), callback_query, CallbackQuery, FSMContext, Message (+28 more)

### Community 31 - "reminder engine/service.py"
Cohesion: 0.17
Nodes (34): collections, SendQuranPagesFn, has_started(), Return whether a scheduled khatm is allowed to deliver work yet., NotificationKind, already_sent_today(), get_preference(), record_sent() (+26 more)

### Community 32 - "get notify fn()"
Cohesion: 0.13
Nodes (34): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, reject_join(), admin_approve_request(), admin_reject_request() (+26 more)

### Community 33 - "creator request/service.py"
Cohesion: 0.13
Nodes (31): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user() (+23 more)

### Community 34 - "app.py"
Cohesion: 0.10
Nodes (31): fastapi, fastapi_staticfiles, fastapi_templating, middleware, _audit_details(), _audit_label(), audit_timeline(), _chunk_devotional() (+23 more)

### Community 35 - "lang()"
Cohesion: 0.16
Nodes (31): callback_query, CallbackQuery, KhatmCategoryGroup, Platform, ask_creation_coupon(), _ask_mode(), cancel_wizard(), choose_allowed_platforms() (+23 more)

### Community 36 - "authorization/service.py"
Cohesion: 0.13
Nodes (29): _admin_role_help(), admin_role_list(), _change_admin_role(), admin_list_requests(), AdminRole, AdminRoleGrant, CapabilityType, str (+21 more)

### Community 37 - "test registration starts in the users sa"
Cohesion: 0.08
Nodes (17): ProfileEdit, StatesGroup, enter_phone(), StatesGroup, Registration, FakeMessage, FakeState, asyncio (+9 more)

### Community 38 - "test deep link clears old state before s"
Cohesion: 0.10
Nodes (13): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_join_preview_cancel_always_acknowledges_callback() (+5 more)

### Community 39 - "sms subscription/service.py"
Cohesion: 0.15
Nodes (28): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+20 more)

### Community 40 - "Request"
Cohesion: 0.18
Nodes (26): get, Request, admins(), _authenticate_telegram_mini_app(), bots_page(), broadcasts_page(), categories_page(), creator_login() (+18 more)

### Community 41 - "allocation/service.py"
Cohesion: 0.15
Nodes (25): assign_quantity_commitment(), claim_next_open_portion(), complete_current_portion_and_advance(), count_open(), get_current_portion(), list_assigned_positional_portions(), list_for_khatm(), list_latest_portion_per_participation() (+17 more)

### Community 42 - "admin()"
Cohesion: 0.26
Nodes (25): AdminPermission, post, RedirectResponse, _admin(), change_admin_role(), create_category(), create_coupon(), decide_broadcast() (+17 more)

### Community 43 - "resume join after registration()"
Cohesion: 0.12
Nodes (24): عضو (Member bots) — تلگرام fa/ar/en و بله, start_member_registration(), handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload(), callback_query, CallbackQuery (+16 more)

### Community 44 - "message template/repository.py"
Cohesion: 0.14
Nodes (20): admin_template_set(), Create a new immutable version of a locale-keyed template. Format:…, MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version() (+12 more)

### Community 45 - "DevotionalAsset"
Cohesion: 0.14
Nodes (20): deliver_devotional_media(), callback_query, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional_reciter_choice(), DevotionalAsset (+12 more)

### Community 46 - "UserRole"
Cohesion: 0.16
Nodes (20): _authorized_admin(), _decision_keyboard(), list_manual_phone_requests(), InlineKeyboardMarkup, message, str, UserRole, UserStatus (+12 more)

### Community 47 - "notification/service.py"
Cohesion: 0.22
Nodes (18): NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession, datetime (+10 more)

### Community 48 - "completion/service.py"
Cohesion: 0.15
Nodes (16): collections_abc, deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Idempotent, delayed completion announcements for every platform., Claim each eligible announcement once, then notify creator + active members. (+8 more)

### Community 49 - "content/service.py"
Cohesion: 0.13
Nodes (16): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., encode_telegram_forward_ref(), get_quran_total_pages(), Quran media registry, reciter whitelist, and user delivery resolution., Idempotently map one source-channel post to every page it covers., Mirrors `register_devotional_audio` — an image of the devotional text (owner…, Total page count for a Quran khatm's edition. OPEN QURAN_PAGE khatms already… (+8 more)

### Community 50 - "AsyncSession"
Cohesion: 0.15
Nodes (18): add_devotional_audio_variant(), add_devotional_image_page(), get_allowed_reciters(), get_effective_reciter(), _get_enabled_devotional_asset(), list_all_devotional_assets(), AsyncSession, Return an exact contiguous range, or None when any page is missing. (+10 more)

### Community 51 - "khatm request/repository.py"
Cohesion: 0.27
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 52 - "AsyncSession"
Cohesion: 0.23
Nodes (17): Participation, allocate_next_portion_to(), approve_join_request(), cancel_khatm(), _complete_join(), join_via_token(), leave_khatm(), AsyncSession (+9 more)

### Community 53 - "after welcome()"
Cohesion: 0.15
Nodes (16): _after_welcome(), _compose_welcome_with_contact(), enter_creator_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, skip_creator_contact(), use_own_contact() (+8 more)

### Community 54 - "QuranAssetKind"
Cohesion: 0.16
Nodes (17): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., parse_quran_channel_caption(), quran_channel_coverage(), Return exact 604-page coverage and missing pages for channel forwards., Idempotently load the repository's verified 604-page source map. (+9 more)

### Community 55 - "khatm workflow/service.py"
Cohesion: 0.19
Nodes (11): Cross-module orchestration for the khatm creation wizard, join/leave flow, and…, WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next() (+3 more)

### Community 56 - "create and launch khatm()"
Cohesion: 0.15
Nodes (16): ContentDeliveryMode, CreatorDisplayMode, KhatmAllocationPlan, KhatmTypeEnum, KhatmVisibility, ReminderTone, generate_quran_page_plan(), generate_quran_page_plan_from_boundaries() (+8 more)

### Community 57 - "test recitation text only for laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 58 - "test mini app auth integration.py"
Cohesion: 0.15
Nodes (9): httpx, json, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, re, Real PostgreSQL coverage for plan controls exposed in the admin Mini App., PostgreSQL + ASGI proof for Telegram Mini App admin authentication., PostgreSQL + ASGI coverage for the public PayPing callback. (+1 more)

### Community 59 - "KhatmSaz Project (Claude Code Instructio"
Cohesion: 0.21
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), DEC-PY-0074: Free-tier Plan Caps, DEC-PY-0075: i18n Scope, AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 60 - "Architecture Document"
Cohesion: 0.19
Nodes (14): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, Multi-Bot Architecture (26 bots), No Business Rule Invention Rule, DEC-PY-0001: Long Polling Decision, DEC-PY-0080: 26-Bot Split Architecture (+6 more)

### Community 61 - "Domain Model"
Cohesion: 0.21
Nodes (14): Allocation / Portion Assignment, Commitment Mode (Taahhodi), Khatm (Collective Recitation), Open/Free Mode (Azad), Participation, Surplus / Overflow (Mazad) Logging, Waiting List, Domain Model (+6 more)

### Community 62 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ"
Cohesion: 0.15
Nodes (13): QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), سازنده (Creator) — تلگرام, ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه) (+5 more)

### Community 63 - "test fresh committed salawat join asks d"
Cohesion: 0.18
Nodes (7): FakeMessage, FakeState, asyncio, integration, Owner request 2026-09-22: delivery-hour question must fire for salawat…, test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it(), test_fresh_committed_salawat_join_asks_delivery_hour()

### Community 64 - "start suggestion()"
Cohesion: 0.29
Nodes (13): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, receive_reply(), receive_suggestion() (+5 more)

### Community 65 - "JoinRequiresApprovalError"
Cohesion: 0.17
Nodes (11): InvalidCreatorDecisionError, JoinRequiresApprovalError, KhatmCancellationError, KhatmUnavailableError, PlanCapExceededError, Exception, Raised by `join_via_token` for a PRIVATE khatm (DOMAIN_MODEL.md §2 Q65-66) the…, The requested missed-commitment resolution is not applicable. (+3 more)

### Community 66 - "test i18n audit.py"
Cohesion: 0.17
Nodes (6): ast, pathlib, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source(), Guards against the raw-slug / Persian-on-other-language class of bug the owner…

### Community 67 - "Devotional texts CRUD (dua/ziyarat) admi"
Cohesion: 0.24
Nodes (12): Categories admin page (devotional_slug link), CONTENT_MANAGE permission gate, devotional_assets storage table, Startup devotional text seed (Ashura, Al-Yasin, Faraj, Ahd), Devotional texts CRUD (dua/ziyarat) admin feature, Grouped sidebar/mobile-dock navigation redesign, Auto text chunking (<=3500 chars joined by \x1e), CHANGELOG Archive (until 2026-09-18) (+4 more)

### Community 68 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 69 - "test health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 70 - "get settings()"
Cohesion: 0.18
Nodes (11): build_bale_bot(), Bot, admin_quran_source_status(), admin_web_login(), admin_web_login_button(), callback_query, Open the signed Telegram Mini App for an authorized administrator., _short_missing() (+3 more)

### Community 71 - "test bot commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 72 - "cancel commitment()"
Cohesion: 0.27
Nodes (11): accept_commitment(), cancel_commitment(), _parse_delivery_time(), callback_query, CallbackQuery, FSMContext, message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid. (+3 more)

### Community 73 - "test picking a reciter via settings menu"
Cohesion: 0.22
Nodes (6): FakeCallback, FakeMessage, asyncio, integration, test_picking_a_reciter_via_settings_menu_turns_on_audio(), test_picking_a_reciter_via_typed_command_turns_on_audio()

### Community 74 - "runtime status.py"
Cohesion: 0.22
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 75 - "devotional seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 76 - "test admin template render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 77 - "test bale invite is a real clickable lin"
Cohesion: 0.20
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 78 - "test dispatcher routes commands while pr"
Cohesion: 0.20
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 79 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 80 - "Multi-Bot Architecture Index Section"
Cohesion: 0.28
Nodes (9): Multi-Bot Architecture Index Section, Admin Token Panel /bots Route (2-step confirmation), bot_instances Database Table, Fernet Token Encryption for Bot Tokens, Creator Bot (ختم‌ساز) Responsibilities, Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), Creator Registration Flow (with OTP) (+1 more)

### Community 81 - "BotRegistry Singleton Class"
Cohesion: 0.22
Nodes (9): Restart Requirement After Token Change, BotRegistry Singleton Class, resolve_bot_category() Function, Post-Creation Invite Link Generation Flow, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link) (+1 more)

### Community 82 - "commitment total keyboard()"
Cohesion: 0.25
Nodes (8): InlineKeyboardMarkup, _commitment_total_keyboard(), _creator_contact_keyboard(), R4: creator sets a contact handle shown in the member welcome. Offers a one-tap…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 83 - "confirm account deletion()"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

### Community 84 - "positional range for step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 85 - "test broadcast shows khatm picker()"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 86 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

### Community 87 - "Creator Role (vs Participant)"
Cohesion: 0.25
Nodes (8): Creator Role (vs Participant), PayPing v3 Payment Gateway, Phone Verification (OTP + Manual), Wallet (Credit + Toman Balance), DEC-PY-0076: Separate Creator/Participant Menus, PayPing Setup Guide (Persian), Module: phone, Module: wallet

### Community 88 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 89 - "Member Bot Language Isolation (fixed per"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 90 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.29
Nodes (8): BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing, allowed_platforms Column (Telegram/Bale/Both), Participant Routing & Platform Limits Task Report

### Community 91 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 92 - "moderate()"
Cohesion: 0.50
Nodes (8): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, submit_khatm_message()

### Community 93 - "receive media()"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 94 - "test quran channel source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 95 - "creator broadcast/service.py"
Cohesion: 0.50
Nodes (7): CreatorBroadcast, create_broadcast(), get_broadcast_count_last_7_days(), get_creator_audience_count(), AsyncSession, UUID, Distinct active members across all the creator's khatms, or scoped to a single…

### Community 96 - "system settings/service.py"
Cohesion: 0.32
Nodes (6): _inactivity_days(), get_int(), list_current(), AsyncSession, See `models.py` for why this module exists. `KNOWN_SETTINGS` is the whitelist…, set_int()

### Community 97 - "system settings/repository.py"
Cohesion: 0.46
Nodes (6): Generic admin-editable key/value store for small system-wide numeric defaults…, SystemSetting, get(), list_all(), AsyncSession, set()

### Community 98 - "test notification snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 99 - "test set font size validates and persist"
Cohesion: 0.32
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 100 - ". call ()"
Cohesion: 0.38
Nodes (6): BaseMiddleware, _extract_chat_id(), ModerationMiddleware, Any, _reply_blocked(), TelegramObject

### Community 101 - "main()"
Cohesion: 0.38
Nodes (5): Bot, _build_member_bots(), _configure_logging(), main(), _tag_bot()

### Community 102 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 103 - "KhatmSaz PROJECT STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 104 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 105 - "test member cancel clears state()"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 106 - "test contribute blocked until delivery h"
Cohesion: 0.29
Nodes (4): _callback_update(), asyncio, Update, test_contribute_blocked_until_delivery_hour_set()

### Community 108 - "test creator finance and support buttons"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 110 - "test tapping a time of day button saves "
Cohesion: 0.29
Nodes (4): FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 111 - "test public khatms reply button is wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 112 - "payping callback()"
Cohesion: 0.33
Nodes (6): HTMLResponse, PayPingGateway, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 113 - "release portion()"
Cohesion: 0.33
Nodes (6): A missed-deadline portion goes back to the shared OPEN pool — the "emergency…, release_portion(), pause_commitment(), امروز نمی‌رسم" (DOMAIN_MODEL.md §3 Q79): proactively release today's portion…, موقتاً متوقف کن" (DOMAIN_MODEL.md §3 Q80): release any current portion (same as…, skip_today()

### Community 114 - "delete account()"
Cohesion: 0.33
Nodes (5): AccountDeletionBlocked, delete_account(), Exception, Safely deactivate a user while retaining non-PII history. Active committed…, The account still owns an obligation that must be resolved first.

### Community 115 - "test completion announcement waits is id"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 117 - "test next portion is withheld until next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 118 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 119 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 120 - "zzz merge three heads 2026 09 28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 121 - "ask welcome()"
Cohesion: 0.50
Nodes (5): _ask_welcome(), _compose_niyyat(), enter_niyyat(), Owner rule (2026-09-27, DEC-PY-0090): the niyyat is FIXED for every khatm — «به…, skip_niyyat()

### Community 122 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.40
Nodes (5): Tooltip Jinja2 Macro Component, Admin Dashboard Page, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 123 - "test render uses fallback locale()"
Cohesion: 0.50
Nodes (4): asyncio, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale()

### Community 124 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 125 - "Identity Across Platforms (phone-based m"
Cohesion: 0.50
Nodes (4): User Identity and Registration Index Section, Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 126 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 128 - "resolve creator decision()"
Cohesion: 0.50
Nodes (4): CommandObject, message, Owner decision (2026-09-21): the missed-portion/emergency-pool system this…, resolve_creator_decision()

### Community 129 - "audit log/service.py"
Cohesion: 0.50
Nodes (3): list_recent(), AsyncSession, Business facade for recording privileged actions.

### Community 130 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 131 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 132 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 133 - "Roadmap Phase 1 — First Real Khatm (DONE"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 160 - "str"
Cohesion: 0.67
Nodes (3): JobStatus, NotifChannel, str

### Community 161 - "str"
Cohesion: 0.67
Nodes (3): AssignmentStatus, AssignmentUnitKind, str

### Community 162 - "AlreadyParticipatingError"
Cohesion: 0.67
Nodes (3): AlreadyParticipatingError, Exception, Raised when a user tries to join a khatm they already have an ACTIVE…

### Community 163 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 165 - "test devotional slug link does not depen"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

### Community 166 - "test devotional text and platform specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 167 - "test reminder tone resolves seeded local"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

## Knowledge Gaps
- **85 isolated node(s):** `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)`, `هدف افزوده‌شده (مالک، 2026-09-27)` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1164 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **87 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Platform` connect `Platform` to `identity/service.py`, `sqlalchemy`, `bot registry/service.py`, `t()`, `new id()`, `sqlalchemy ext asyncio`, `session scope()`, `phone/service.py`, `portions.py`, `admin.py`, `allocation/repository.py`, `bail if menu button()`, `env.py`, `test confirm wizard resumes and finishes`, `plan/service.py`, `config.py`, `settings menu.py`, `get notify fn()`, `authorization/service.py`, `test registration starts in the users sa`, `test deep link clears old state before s`, `resume join after registration()`, `message template/repository.py`, `DevotionalAsset`, `UserRole`, `test fresh committed salawat join asks d`, `start suggestion()`, `get settings()`, `test bot commands.py`, `cancel commitment()`, `test picking a reciter via settings menu`, `test bale invite is a real clickable lin`, `confirm account deletion()`, `AdminFilter`, `moderate()`, `receive media()`, `. call ()`, `test completion announcement waits is id`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session scope()` to `identity/service.py`, `sqlalchemy`, `bot registry/service.py`, `t()`, `Platform`, `new id()`, `sqlalchemy ext asyncio`, `phone/service.py`, `portions.py`, `KhatmTypeEnum`, `admin.py`, `allocation/repository.py`, `bail if menu button()`, `env.py`, `reporting/service.py`, `test confirm wizard resumes and finishes`, `plan/service.py`, `settings menu.py`, `get notify fn()`, `authorization/service.py`, `test devotional slug link does not depen`, `test devotional text and platform specif`, `test registration starts in the users sa`, `test reminder tone resolves seeded local`, `resume join after registration()`, `message template/repository.py`, `DevotionalAsset`, `UserRole`, `QuranAssetKind`, `test fresh committed salawat join asks d`, `start suggestion()`, `get settings()`, `cancel commitment()`, `test picking a reciter via settings menu`, `test bale invite is a real clickable lin`, `confirm account deletion()`, `AdminFilter`, `moderate()`, `receive media()`, `. call ()`, `test tapping a time of day button saves `, `test completion announcement waits is id`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `t()` connect `t()` to `identity/service.py`, `resolve creator decision()`, `Platform`, `session scope()`, `phone/service.py`, `portions.py`, `KhatmTypeEnum`, `bail if menu button()`, `env.py`, `panel.py`, `create khatm.py`, `settings menu.py`, `get notify fn()`, `app.py`, `lang()`, `test registration starts in the users sa`, `resume join after registration()`, `DevotionalAsset`, `after welcome()`, `QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ`, `start suggestion()`, `cancel commitment()`, `test admin template render.py`, `commitment total keyboard()`, `confirm account deletion()`, `test creator finance and support buttons`, `test public khatms reply button is wired`, `ask welcome()`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 195 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 195 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `identity/service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.056496409700582575 - nodes in this community are weakly interconnected._
- **Should `sqlalchemy` be split into smaller, more focused modules?**
  _Cohesion score 0.07026652821045344 - nodes in this community are weakly interconnected._