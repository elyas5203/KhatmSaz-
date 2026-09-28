# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 456 files · ~291,584 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3533 nodes · 11600 edges · 234 communities (138 shown, 96 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1436 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- create khatm.py
- new id()
- bot registry/service.py
- settings/service.py
- sqlalchemy ext asyncio
- wallet/service.py
- Platform
- t()
- datetime
- identity/models.py
- get or create()
- my khatms.py
- phone/repository.py
- Khatm
- panel.py
- provider.py
- allocation/repository.py
- settings menu.py
- phone/service.py
- portions.py
- Participation
- sqlalchemy dialects
- typing
- start.py
- participation/service.py
- PayPingGateway
- safe answer callback()
- alembic
- reminder engine/service.py
- bail if menu button()
- test confirm wizard resumes and finishes
- identity/service.py
- UserRole
- plan/service.py
- types
- sqlalchemy
- sms subscription/service.py
- test deep link clears old state before s
- test admin web integration.py
- member commitment.py
- content/service.py
- notification/service.py
- test member commitment logic.py
- allocation/service.py
- test fresh committed salawat join asks d
- admin()
- db.py
- profile.py
- session scope()
- completion/service.py
- app.py
- authorization/service.py
- DevotionalAsset
- Request
- Participation
- broadcast/service.py
- QuranAssetKind
- config.py
- AsyncSession
- build my khatms tree()
- message template/repository.py
- create and launch khatm()
- member my khatms.py
- test registration phone share only.py
- open contribution/repository.py
- test wizard ephemeral.py
- creator request/repository.py
- KhatmSaz Project (Claude Code Instructio
- Architecture Document
- Domain Model
- advertising/service.py
- creator()
- test registration starts in the users sa
- admin approve request()
- JoinRequiresApprovalError
- test reciter activates audio integration
- test i18n audit.py
- Devotional texts CRUD (dua/ziyarat) admi
- KhatmSaz VPS Deployment Guide
- test member commitment flow.py
- show wallet()
- test notify routing.py
- test health.py
- test bot commands.py
- start suggestion()
- cancel commitment()
- runtime status.py
- devotional seed.py
- test admin template render.py
- test bale invite is a real clickable lin
- test dispatcher routes commands while pr
- CSS Layouts and Responsive Design Guide
- Multi-Bot Architecture Index Section
- BotRegistry Singleton Class
- positional range for step()
- test broadcast shows khatm picker()
- test message template.py
- Creator Role (vs Participant)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per
- Multi-Bot (26-bot) Architecture
- qr.py
- receive media()
- test quran channel source.py
- test notification snooze.py
- test set font size validates and persist
- main()
- Python Requirements
- KhatmSaz PROJECT STATE Log
- PayPing v3 Adapter Integration
- conftest.py
- register devotional content.py
- add devotional audio variant()
- test contribute blocked until delivery h
- FakeState
- FakeMessage
- test public khatms reply button is wired
- payping callback()
- bot/ init .py
- test completion announcement waits is id
- test next portion is withheld until next
- test open quran reading auto delivers on
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earli
- env.py
- zzz merge three heads 2026 09 28.py
- Tooltip Jinja2 Macro Component
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based m
- Settings Menu Full-Button Test Scenario
- 435027907255 add daily deadline hour to 
- register devotional content batch2.py
- request account deletion()
- list manual phone requests()
- AccountDeletionBlocked
- test devotional category navigation.py
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE
- Creator Panel Base Layout Template
- start bot.ps1
- test devotional slug link does not depen
- test devotional text and platform specif
- FakeSent
- claude watchdog.sh
- Quran Content Storage (Telegram channel-
- Roadmap Phase 10 — Messenger Mini Apps
- AccountLink
- CreatorBroadcastFlow
- RequestKhatm
- ManageContentState
- Suggestion
- broadcast/ init .py
- validate body()
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
- CommandObject
- InlineKeyboardMarkup
- ReplyKeyboardMarkup
- str
- Exception
- NotifyFn
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
1. `t()` - 298 edges
2. `session_scope()` - 273 edges
3. `Platform` - 241 edges
4. `new_id()` - 128 edges
5. `User` - 124 edges
6. `Khatm` - 114 edges
7. `safe_answer_callback()` - 86 edges
8. `KhatmStatus` - 76 edges
9. `Base` - 75 edges
10. `resolve_or_provision_user()` - 70 edges

## Surprising Connections (you probably didn't know these)
- `رفع‌شدهٔ فاز ۲ (این جلسه، با تست)` --references--> `snooze_keyboard()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/keyboards.py
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py
- `عضو (Member bots) — تلگرام fa/ar/en و بله` --references--> `BotRole`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/modules/bot_registry/models.py
- `سازنده (Creator) — تلگرام` --references--> `help_command()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/help.py
- `سازنده (Creator) — تلگرام` --references--> `creator_menu_keyboard()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/keyboards.py

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

## Communities (234 total, 96 thin omitted)

### Community 0 - "create khatm.py"
Cohesion: 0.06
Nodes (108): callback_query, CallbackQuery, CommandObject, FSMContext, KhatmCategoryGroup, Message, Platform, _after_commitment_total() (+100 more)

### Community 1 - "new id()"
Cohesion: 0.03
Nodes (108): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), User, CoverStatus, CreatorDisplayMode, KhatmScheduleKind (+100 more)

### Community 2 - "bot registry/service.py"
Cohesion: 0.05
Nodes (81): cryptography_fernet, Fernet, format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Render member-bot links as a readable, multi-line Persian block., Choose one link to encode in a QR: prefer the creator's language and platform,… (+73 more)

### Community 3 - "settings/service.py"
Cohesion: 0.08
Nodes (49): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types, apscheduler_schedulers_asyncio, logging, Process entrypoint: `python -m khatmsaz.bootstrap`. Starts both bots (whichever… (+41 more)

### Community 4 - "sqlalchemy ext asyncio"
Cohesion: 0.05
Nodes (74): hashlib, secrets, sqlalchemy_ext_asyncio, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, get_by_token_hash(), mark_accepted() (+66 more)

### Community 5 - "wallet/service.py"
Cohesion: 0.06
Nodes (81): CouponDiscountType, CouponRedemption, PaymentGateway, PaymentVerification, PendingPayment, add_balance(), add_credit(), bind_invoice_resource() (+73 more)

### Community 6 - "Platform"
Cohesion: 0.10
Nodes (73): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+65 more)

### Community 7 - "t()"
Cohesion: 0.07
Nodes (68): base64, InlineKeyboardMarkup, ReplyKeyboardMarkup, help_command(), help_topic(), Message, _resolve_user_info(), admin_menu_keyboard() (+60 more)

### Community 8 - "datetime"
Cohesion: 0.08
Nodes (41): datetime, DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's… (+33 more)

### Community 9 - "identity/models.py"
Cohesion: 0.09
Nodes (23): khatmsaz_modules_khatm_category_models, pytest, UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Identity module: the canonical User and external PlatformIdentity links.…, Khatm module: the core collective-recitation aggregate., Cross-module orchestration for the khatm creation wizard, join/leave flow, and…, Real PostgreSQL coverage for the safe account-deletion boundary., Real PostgreSQL pagination coverage for large Mini App lists. (+15 more)

### Community 10 - "get or create()"
Cohesion: 0.05
Nodes (65): CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), _lang_for(), CommandObject, message (+57 more)

### Community 11 - "my khatms.py"
Cohesion: 0.11
Nodes (61): csv, ask_cancel_khatm(), cancel_cancel_khatm(), confirm_cancel_khatm(), creator_begin_cosmetic_edit(), creator_begin_end_at(), creator_begin_schedule_date(), creator_cancel_cosmetic_edit() (+53 more)

### Community 12 - "phone/repository.py"
Cohesion: 0.07
Nodes (60): decide_manual_phone_request(), callback_query, CallbackQuery, AuditLog, list_recent(), AsyncSession, Return a bounded newest-first timeline without exposing mutation APIs., record() (+52 more)

### Community 13 - "Khatm"
Cohesion: 0.12
Nodes (56): Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+48 more)

### Community 14 - "panel.py"
Cohesion: 0.06
Nodes (53): QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), سازنده (Creator) — تلگرام, ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه) (+45 more)

### Community 15 - "provider.py"
Cohesion: 0.07
Nodes (42): dataclasses, hmac, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Protocol (+34 more)

### Community 16 - "allocation/repository.py"
Cohesion: 0.09
Nodes (51): CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion() (+43 more)

### Community 17 - "settings menu.py"
Cohesion: 0.11
Nodes (51): InlineKeyboardButton, begin_account_link(), _lang_for(), begin_profile(), buy_sms_plan(), _current_platform_user(), _lang_for(), callback_query (+43 more)

### Community 18 - "phone/service.py"
Cohesion: 0.10
Nodes (46): sqlalchemy_exc, FSMContext, message, receive_link_code(), receive_link_phone(), begin_phone_change(), ChangePhone, ensure_creator_phone_verified() (+38 more)

### Community 19 - "portions.py"
Cohesion: 0.11
Nodes (50): apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze(), ask_pause_duration(), ask_snooze(), CustomSnooze (+42 more)

### Community 20 - "Participation"
Cohesion: 0.07
Nodes (45): Base, list_member_khatms(), message, deliver_pending(), _message(), AsyncSession, datetime, NotifyFn (+37 more)

### Community 22 - "typing"
Cohesion: 0.04
Nodes (7): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 23 - "start.py"
Cohesion: 0.08
Nodes (43): عضو (Member bots) — تلگرام fa/ar/en و بله, html, Khatm, start_member_registration(), handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload() (+35 more)

### Community 24 - "participation/service.py"
Cohesion: 0.10
Nodes (39): ParticipationStatus, advance_open_reading(), count_for_khatm(), list_active_for_user(), list_active_with_users(), log_commitment_count(), mark_open_reading_sent_now(), mark_schedule_sent_now() (+31 more)

### Community 25 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, GatewayError, PaymentGateway, PaymentRequest, PaymentVerification, Exception, Protocol, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 26 - "safe answer callback()"
Cohesion: 0.10
Nodes (41): callback_query, CallbackQuery, quran_help(), set_audio_callback(), cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query (+33 more)

### Community 28 - "reminder engine/service.py"
Cohesion: 0.14
Nodes (36): collections, NotificationKind, NotifyFn, SendQuranPagesFn, Positive khatm-completion announcements., get_by_id(), _default_reminder_hour(), delegate_inactive_portions() (+28 more)

### Community 29 - "bail if menu button()"
Cohesion: 0.12
Nodes (35): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+27 more)

### Community 30 - "test confirm wizard resumes and finishes"
Cohesion: 0.08
Nodes (31): InvoiceStatus, Immutable purchase amounts plus a small paid/refunded lifecycle., Wallet, WalletInvoice, WalletTransaction, test_admin_visible_enums_have_persian_labels(), asyncio, integration (+23 more)

### Community 31 - "identity/service.py"
Cohesion: 0.13
Nodes (33): PlatformIdentity, UserStatus, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity(), list_platform_identities() (+25 more)

### Community 32 - "UserRole"
Cohesion: 0.09
Nodes (31): BaseFilter, AdminFilter, Checks if the user has admin privileges. For now, we simply check if the user…, admin_approve_creator(), admin_reject_creator(), handle_creator_request_button(), handle_creator_request_message(), callback_query (+23 more)

### Community 33 - "plan/service.py"
Cohesion: 0.13
Nodes (32): PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition() (+24 more)

### Community 34 - "types"
Cohesion: 0.09
Nodes (21): aiogram_enums, aiogram_fsm_storage_memory, contextlib, khatmsaz_bot_handlers, khatmsaz_bot_handlers_start, MemberRegistration, StatesGroup, Regression for per-khatm broadcast targeting (owner request 2026-09-27):… (+13 more)

### Community 35 - "sqlalchemy"
Cohesion: 0.09
Nodes (8): sqlalchemy, Audit records are immutable facts about privileged actions., Persistence access for the append-only audit module., Persistence access for invitation — the only place that runs SQL for this…, Phone module: phone ownership claims and OTP challenges., User settings module: per-user configurable preferences (1:1 extension of User)., Real PostgreSQL self-service platform/account linking flow., Real PostgreSQL coverage for the admin user-search query.

### Community 36 - "sms subscription/service.py"
Cohesion: 0.14
Nodes (30): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+22 more)

### Community 37 - "test deep link clears old state before s"
Cohesion: 0.10
Nodes (13): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_join_preview_cancel_always_acknowledges_callback() (+5 more)

### Community 38 - "test admin web integration.py"
Cohesion: 0.09
Nodes (17): httpx, json, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl, re, Template lookup and safe ``{{placeholder}}`` rendering., Real PostgreSQL coverage for plan controls exposed in the admin Mini App. (+9 more)

### Community 39 - "member commitment.py"
Cohesion: 0.18
Nodes (29): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), choose_weekday(), CommitFlow, enter_count() (+21 more)

### Community 40 - "content/service.py"
Cohesion: 0.11
Nodes (26): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., get_allowed_reciters(), get_effective_reciter(), get_quran_total_pages(), list_all_devotional_assets(), parse_quran_channel_caption(), AsyncSession (+18 more)

### Community 41 - "notification/service.py"
Cohesion: 0.15
Nodes (23): NotificationKind, NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession (+15 more)

### Community 42 - "test member commitment logic.py"
Cohesion: 0.12
Nodes (27): CommitmentMode, is_regular_due(), is_regular_occurrence_today(), log_count(), _minutes(), persian_dow(), datetime, R11 (owner 2026-09-28): member-side commitment logic — pure, side-effect-free.… (+19 more)

### Community 43 - "allocation/service.py"
Cohesion: 0.13
Nodes (27): assign_quantity_commitment(), claim_next_open_portion(), complete_current_portion_and_advance(), count_open(), get_current_portion(), list_assigned_positional_portions(), list_for_khatm(), list_latest_portion_per_participation() (+19 more)

### Community 44 - "test fresh committed salawat join asks d"
Cohesion: 0.09
Nodes (17): _parse_delivery_time(), message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., receive_delivery_hour(), AskDeliveryHour, Owner request (2026-09-21): every committed member should be asked what hour…, FakeState, asyncio (+9 more)

### Community 45 - "admin()"
Cohesion: 0.26
Nodes (25): AdminPermission, post, RedirectResponse, _admin(), change_admin_role(), create_category(), create_coupon(), decide_broadcast() (+17 more)

### Community 46 - "db.py"
Cohesion: 0.13
Nodes (9): khatmsaz_modules_khatm_category, os, Async SQLAlchemy engine/session setup. One engine for the whole process., Content preferences and per-khatm reciter policy., Localized, versioned message templates., BACKLOG.md §14 fix (2026-09-21): replace the fragile name-matching hack…, Owner request (2026-09-22): a devotional asset (dua/ziyarat) can now have more…, Real PostgreSQL filtering proof for independent devotional families. (+1 more)

### Community 47 - "profile.py"
Cohesion: 0.14
Nodes (23): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), _gender_keyboard(), ProfileEdit, _province_keyboard() (+15 more)

### Community 48 - "session scope()"
Cohesion: 0.13
Nodes (23): Any, CallbackQuery, Message, cancel_account_deletion(), confirm_account_deletion(), _lang_for(), callback_query, CallbackQuery (+15 more)

### Community 49 - "completion/service.py"
Cohesion: 0.12
Nodes (18): BaseMiddleware, collections_abc, _extract_chat_id(), ModerationMiddleware, Any, Bot-wide moderation gate: a SUSPENDED/BANNED user gets a single friendly…, _reply_blocked(), Idempotent, delayed completion announcements for every platform. (+10 more)

### Community 50 - "app.py"
Cohesion: 0.13
Nodes (22): fastapi, fastapi_staticfiles, fastapi_templating, middleware, _audit_details(), _audit_label(), audit_timeline(), _authenticate_telegram_mini_app() (+14 more)

### Community 51 - "authorization/service.py"
Cohesion: 0.19
Nodes (21): _authorized_admin(), AdminRole, AdminRoleGrant, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession, Persistence helpers for delegated admin roles. (+13 more)

### Community 52 - "DevotionalAsset"
Cohesion: 0.13
Nodes (22): deliver_devotional_media(), callback_query, CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional() (+14 more)

### Community 53 - "Request"
Cohesion: 0.22
Nodes (21): get, Request, admins(), bots_page(), broadcasts_page(), categories_page(), creator_login(), _ctx() (+13 more)

### Community 54 - "Participation"
Cohesion: 0.13
Nodes (20): Exception, count_committed_active(), create(), get_active(), list_active_for_khatm(), list_active_with_open_reading_plan(), list_active_with_regular_schedule(), Participation (+12 more)

### Community 55 - "broadcast/service.py"
Cohesion: 0.29
Nodes (18): BroadcastStatus, KhatmBroadcast, str, create(), get_by_id(), list_pending(), mark_reviewed(), mark_sent() (+10 more)

### Community 56 - "QuranAssetKind"
Cohesion: 0.15
Nodes (20): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), quran_channel_coverage(), Idempotently map one source-channel post to every page it covers., Return exact 604-page coverage and missing pages for channel forwards. (+12 more)

### Community 57 - "config.py"
Cohesion: 0.13
Nodes (14): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, BaseSettings, functools, pydantic_settings, build_bale_bot(), Bot (+6 more)

### Community 58 - "AsyncSession"
Cohesion: 0.23
Nodes (17): Participation, allocate_next_portion_to(), approve_join_request(), cancel_khatm(), _complete_join(), join_via_token(), leave_khatm(), AsyncSession (+9 more)

### Community 59 - "build my khatms tree()"
Cohesion: 0.17
Nodes (17): _build_my_khatms_tree(), _content_group(), _khatm_bucket(), list_my_khatms(), my_khatms_show_branch(), my_khatms_show_category(), my_khatms_show_root(), InlineKeyboardMarkup (+9 more)

### Community 60 - "message template/repository.py"
Cohesion: 0.20
Nodes (15): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+7 more)

### Community 61 - "create and launch khatm()"
Cohesion: 0.15
Nodes (16): ContentDeliveryMode, CreatorDisplayMode, KhatmAllocationPlan, KhatmTypeEnum, KhatmVisibility, ReminderTone, generate_quran_page_plan(), generate_quran_page_plan_from_boundaries() (+8 more)

### Community 62 - "member my khatms.py"
Cohesion: 0.18
Nodes (15): callback_query, CallbackQuery, FSMContext, Member bot "My Khatms" handler — lists khatms the user joined via this bot…, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow…, show_member_portion(), show_member_reminder_hours() (+7 more)

### Community 63 - "test registration phone share only.py"
Cohesion: 0.18
Nodes (8): StatesGroup, Registration, FakeMessage, FakeState, asyncio, Owner request (2026-09-22): during initial registration on Telegram, only the…, test_bale_typed_phone_is_still_accepted_during_registration(), test_telegram_typed_phone_is_rejected_during_registration()

### Community 64 - "open contribution/repository.py"
Cohesion: 0.19
Nodes (13): create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation(), log_contribution() (+5 more)

### Community 65 - "test wizard ephemeral.py"
Cohesion: 0.24
Nodes (8): asyncio, FakeBot, FakeMessage, FakeState, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_deletes_previous_prompt(), test_wiz_failed_delete_still_sends(), test_wiz_first_call_just_sends_and_tracks_id()

### Community 66 - "creator request/repository.py"
Cohesion: 0.34
Nodes (14): CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user(), list_pending() (+6 more)

### Community 67 - "KhatmSaz Project (Claude Code Instructio"
Cohesion: 0.21
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), DEC-PY-0074: Free-tier Plan Caps, DEC-PY-0075: i18n Scope, AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 68 - "Architecture Document"
Cohesion: 0.19
Nodes (14): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, Multi-Bot Architecture (26 bots), No Business Rule Invention Rule, DEC-PY-0001: Long Polling Decision, DEC-PY-0080: 26-Bot Split Architecture (+6 more)

### Community 69 - "Domain Model"
Cohesion: 0.21
Nodes (14): Allocation / Portion Assignment, Commitment Mode (Taahhodi), Khatm (Collective Recitation), Open/Free Mode (Azad), Participation, Surplus / Overflow (Mazad) Logging, Waiting List, Domain Model (+6 more)

### Community 70 - "advertising/service.py"
Cohesion: 0.21
Nodes (10): accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The…, set_reward_rate(), TxType (+2 more)

### Community 71 - "creator()"
Cohesion: 0.18
Nodes (14): _creator(), _creator_ctx(), creator_dashboard(), creator_khatm_detail(), creator_khatm_export(), creator_khatm_settings(), creator_logout(), _csrf() (+6 more)

### Community 72 - "test registration starts in the users sa"
Cohesion: 0.16
Nodes (7): FakeMessage, FakeState, asyncio, integration, parametrize, Registration language selection is loaded from real PostgreSQL., test_registration_starts_in_the_users_saved_language()

### Community 73 - "admin approve request()"
Cohesion: 0.31
Nodes (13): admin_approve_request(), admin_list_requests(), admin_reject_request(), CommandObject, FSMContext, Message, request_khatm(), request_khatm_description() (+5 more)

### Community 74 - "JoinRequiresApprovalError"
Cohesion: 0.17
Nodes (11): InvalidCreatorDecisionError, JoinRequiresApprovalError, KhatmCancellationError, KhatmUnavailableError, PlanCapExceededError, Exception, Raised by `join_via_token` for a PRIVATE khatm (DOMAIN_MODEL.md §2 Q65-66) the…, The requested missed-commitment resolution is not applicable. (+3 more)

### Community 75 - "test reciter activates audio integration"
Cohesion: 0.22
Nodes (7): FakeCallback, FakeMessage, asyncio, integration, Owner-reported bug (2026-09-21): "قاری رو فعال میکنم اما برام صوت ارسال نمیشه"…, test_picking_a_reciter_via_settings_menu_turns_on_audio(), test_picking_a_reciter_via_typed_command_turns_on_audio()

### Community 76 - "test i18n audit.py"
Cohesion: 0.17
Nodes (6): ast, pathlib, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source(), Guards against the raw-slug / Persian-on-other-language class of bug the owner…

### Community 77 - "Devotional texts CRUD (dua/ziyarat) admi"
Cohesion: 0.24
Nodes (12): Categories admin page (devotional_slug link), CONTENT_MANAGE permission gate, devotional_assets storage table, Startup devotional text seed (Ashura, Al-Yasin, Faraj, Ahd), Devotional texts CRUD (dua/ziyarat) admin feature, Grouped sidebar/mobile-dock navigation redesign, Auto text chunking (<=3500 chars joined by \x1e), CHANGELOG Archive (until 2026-09-18) (+4 more)

### Community 78 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 79 - "test member commitment flow.py"
Cohesion: 0.24
Nodes (9): importlib_util, khatmsaz_bot, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_prefix_matches_handler(), test_mode_keyboard_callbacks() (+1 more)

### Community 80 - "show wallet()"
Cohesion: 0.21
Nodes (12): create_topup(), _lang_for(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery, InlineKeyboardMarkup, Message (+4 more)

### Community 81 - "test notify routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 82 - "test health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 83 - "test bot commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 84 - "start suggestion()"
Cohesion: 0.36
Nodes (11): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, _resolve_user_context(), start_reply_to_user(), start_suggestion() (+3 more)

### Community 85 - "cancel commitment()"
Cohesion: 0.29
Nodes (10): accept_commitment(), cancel_commitment(), callback_query, CallbackQuery, FSMContext, receive_delivery_hour_button(), _save_delivery_time(), message (+2 more)

### Community 86 - "runtime status.py"
Cohesion: 0.22
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 87 - "devotional seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 88 - "test admin template render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 89 - "test bale invite is a real clickable lin"
Cohesion: 0.20
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 90 - "test dispatcher routes commands while pr"
Cohesion: 0.20
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 91 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 92 - "Multi-Bot Architecture Index Section"
Cohesion: 0.28
Nodes (9): Multi-Bot Architecture Index Section, Admin Token Panel /bots Route (2-step confirmation), bot_instances Database Table, Fernet Token Encryption for Bot Tokens, Creator Bot (ختم‌ساز) Responsibilities, Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), Creator Registration Flow (with OTP) (+1 more)

### Community 93 - "BotRegistry Singleton Class"
Cohesion: 0.22
Nodes (9): Restart Requirement After Token Change, BotRegistry Singleton Class, resolve_bot_category() Function, Post-Creation Invite Link Generation Flow, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link) (+1 more)

### Community 94 - "positional range for step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 95 - "test broadcast shows khatm picker()"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 96 - "test message template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 97 - "Creator Role (vs Participant)"
Cohesion: 0.25
Nodes (8): Creator Role (vs Participant), PayPing v3 Payment Gateway, Phone Verification (OTP + Manual), Wallet (Credit + Toman Balance), DEC-PY-0076: Separate Creator/Participant Menus, PayPing Setup Guide (Persian), Module: phone, Module: wallet

### Community 98 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 99 - "Member Bot Language Isolation (fixed per"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 100 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.29
Nodes (8): BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing, allowed_platforms Column (Telegram/Bale/Both), Participant Routing & Platform Limits Task Report

### Community 101 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 102 - "receive media()"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 103 - "test quran channel source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 104 - "test notification snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 105 - "test set font size validates and persist"
Cohesion: 0.32
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 106 - "main()"
Cohesion: 0.38
Nodes (5): Bot, _build_member_bots(), _configure_logging(), main(), _tag_bot()

### Community 107 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 108 - "KhatmSaz PROJECT STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 109 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 110 - "conftest.py"
Cohesion: 0.29
Nodes (5): fixture, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 111 - "register devotional content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 112 - "add devotional audio variant()"
Cohesion: 0.29
Nodes (7): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.…, Owner request (2026-09-22): a dua's image can span more than one page…, Owner request (2026-09-22): a dua's full text as a PDF document — one slot per…, set_devotional_pdf()

### Community 113 - "test contribute blocked until delivery h"
Cohesion: 0.29
Nodes (4): _callback_update(), asyncio, Update, test_contribute_blocked_until_delivery_hour_set()

### Community 116 - "test public khatms reply button is wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 117 - "payping callback()"
Cohesion: 0.33
Nodes (6): HTMLResponse, PayPingGateway, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 118 - "bot/ init .py"
Cohesion: 0.33
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 119 - "test completion announcement waits is id"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 120 - "test next portion is withheld until next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 121 - "test open quran reading auto delivers on"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 122 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 123 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 124 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 125 - "zzz merge three heads 2026 09 28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 126 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.40
Nodes (5): Tooltip Jinja2 Macro Component, Admin Dashboard Page, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 127 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 128 - "Identity Across Platforms (phone-based m"
Cohesion: 0.50
Nodes (4): User Identity and Registration Index Section, Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 129 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 131 - "register devotional content batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 132 - "request account deletion()"
Cohesion: 0.50
Nodes (4): _confirm_keyboard(), InlineKeyboardMarkup, message, request_account_deletion()

### Community 133 - "list manual phone requests()"
Cohesion: 0.50
Nodes (4): _decision_keyboard(), list_manual_phone_requests(), InlineKeyboardMarkup, message

### Community 134 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 135 - "test devotional category navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 136 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 137 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 138 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 139 - "Roadmap Phase 1 — First Real Khatm (DONE"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 165 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 167 - "test devotional slug link does not depen"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

### Community 168 - "test devotional text and platform specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

## Knowledge Gaps
- **85 isolated node(s):** `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)`, `هدف افزوده‌شده (مالک، 2026-09-27)` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1204 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **96 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t()` to `settings/service.py`, `request account deletion()`, `get or create()`, `my khatms.py`, `phone/repository.py`, `panel.py`, `settings menu.py`, `phone/service.py`, `portions.py`, `Participation`, `start.py`, `safe answer callback()`, `reminder engine/service.py`, `bail if menu button()`, `UserRole`, `types`, `member commitment.py`, `test fresh committed salawat join asks d`, `profile.py`, `session scope()`, `app.py`, `DevotionalAsset`, `build my khatms tree()`, `member my khatms.py`, `creator()`, `test registration starts in the users sa`, `admin approve request()`, `show wallet()`, `start suggestion()`, `cancel commitment()`, `test admin template render.py`, `test public khatms reply button is wired`, `bot/ init .py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session scope()` to `new id()`, `bot registry/service.py`, `settings/service.py`, `register devotional content batch2.py`, `list manual phone requests()`, `Platform`, `t()`, `sqlalchemy ext asyncio`, `get or create()`, `my khatms.py`, `phone/repository.py`, `allocation/repository.py`, `settings menu.py`, `phone/service.py`, `Participation`, `start.py`, `safe answer callback()`, `bail if menu button()`, `test confirm wizard resumes and finishes`, `identity/service.py`, `UserRole`, `plan/service.py`, `test devotional slug link does not depen`, `test devotional text and platform specif`, `test fresh committed salawat join asks d`, `db.py`, `profile.py`, `completion/service.py`, `authorization/service.py`, `DevotionalAsset`, `QuranAssetKind`, `build my khatms tree()`, `message template/repository.py`, `member my khatms.py`, `test registration starts in the users sa`, `admin approve request()`, `test reciter activates audio integration`, `show wallet()`, `start suggestion()`, `cancel commitment()`, `test bale invite is a real clickable lin`, `receive media()`, `register devotional content.py`, `test completion announcement waits is id`, `test next portion is withheld until next`, `test open quran reading auto delivers on`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `new id()`, `bot registry/service.py`, `settings/service.py`, `sqlalchemy ext asyncio`, `list manual phone requests()`, `t()`, `identity/models.py`, `get or create()`, `my khatms.py`, `phone/repository.py`, `allocation/repository.py`, `settings menu.py`, `phone/service.py`, `Participation`, `start.py`, `safe answer callback()`, `bail if menu button()`, `test confirm wizard resumes and finishes`, `identity/service.py`, `UserRole`, `test deep link clears old state before s`, `test fresh committed salawat join asks d`, `profile.py`, `session scope()`, `completion/service.py`, `authorization/service.py`, `DevotionalAsset`, `config.py`, `build my khatms tree()`, `member my khatms.py`, `test registration phone share only.py`, `test registration starts in the users sa`, `admin approve request()`, `test reciter activates audio integration`, `show wallet()`, `test notify routing.py`, `test bot commands.py`, `start suggestion()`, `cancel commitment()`, `test bale invite is a real clickable lin`, `receive media()`, `test completion announcement waits is id`, `test next portion is withheld until next`, `test open quran reading auto delivers on`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 190 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 190 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `create khatm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05736636245110821 - nodes in this community are weakly interconnected._
- **Should `new id()` be split into smaller, more focused modules?**
  _Cohesion score 0.031484257871064465 - nodes in this community are weakly interconnected._