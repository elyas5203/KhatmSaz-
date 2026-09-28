# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 458 files · ~292,578 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3556 nodes · 11682 edges · 218 communities (149 shown, 69 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1438 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- sqlalchemy
- new id()
- create khatm.py
- db.py
- identity/service.py
- t()
- my khatms.py
- wallet/service.py
- Platform
- datetime
- settings menu.py
- invitation/service.py
- sqlalchemy dialects
- Khatm
- start.py
- portions.py
- member my khatms.py
- allocation/repository.py
- khatm category/service.py
- phone/repository.py
- provider.py
- reminder engine/service.py
- app.py
- safe answer callback()
- creator request/service.py
- session scope()
- bot registry.py
- participation/repository.py
- Request
- safe clear inline keyboard()
- bot registry/service.py
- notification/service.py
- UserRole
- test deep link clears old state before s
- member registration.py
- test registration starts in the users sa
- sms subscription/service.py
- participation/service.py
- khatm workflow/service.py
- PlatformIdentity
- test member commitment logic.py
- content/service.py
- wallet/models.py
- plan/models.py
- QuranAssetKind
- get settings()
- panel.py
- phone/service.py
- typing
- PayPingGateway
- DevotionalAsset
- broadcast/service.py
- test confirm wizard resumes and finishes
- suggestions.py
- completion/service.py
- khatm request/repository.py
- approve join()
- message template/repository.py
- broadcast.py
- OpenContribution
- test wizard ephemeral.py
- KhatmSaz Project (Claude Code Instructio
- Architecture Document
- Domain Model
- create and launch khatm()
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ
- sqlalchemy ext asyncio
- UserSettings
- test tapping a time of day button saves 
- admin approve request()
- reporting/service.py
- system settings/repository.py
- test admin visible enums have persian la
- test reciter activates audio integration
- test i18n audit.py
- Devotional texts CRUD (dua/ziyarat) admi
- KhatmSaz VPS Deployment Guide
- test member commitment flow.py
- begin profile()
- test notify routing.py
- test deliver due next portions pushes re
- test health.py
- test commitment hour gate.py
- test bot commands.py
- cancel commitment()
- manual phone verification/service.py
- ParticipationStatus
- conftest.py
- runtime status.py
- advertising/service.py
- devotional seed.py
- test admin template render.py
- test bale invite is a real clickable lin
- CSS Layouts and Responsive Design Guide
- Multi-Bot Architecture Index Section
- BotRegistry Singleton Class
- test payment safety.py
- positional range for step()
- manual phone verification/repository.py
- test broadcast shows khatm picker()
- test message template.py
- AdminFilter
- Creator Role (vs Participant)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per
- Multi-Bot (26-bot) Architecture
- qr.py
- test mini app entry.py
- receive media()
- test quran channel source.py
- test dispatcher routes commands while pr
- test notification snooze.py
- test set font size validates and persist
- . call ()
- main()
- Python Requirements
- KhatmSaz PROJECT STATE Log
- PayPing v3 Adapter Integration
- test sms subscription safety integration
- register devotional content.py
- test member cancel clears state()
- test creator finance and support buttons
- test public khatms reply button is wired
- payping callback()
- pause commitment()
- plan/ init .py
- FakeState
- test next portion is withheld until next
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earli
- env.py
- zzz merge three heads 2026 09 28.py
- str
- Tooltip Jinja2 Macro Component
- test join via token threads bot instance
- test wizard keyboards i18n.py
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based m
- Settings Menu Full-Button Test Scenario
- 1f9fe3de23a1 add khatm requests table.py
- cf308fcab881 add khatm visibility.py
- register devotional content batch2.py
- request account deletion()
- resolve creator decision()
- AccountDeletionBlocked
- test private join approval rejects non c
- Base
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE
- PlanFeatureUnavailableError
- Creator Panel Base Layout Template
- start bot.ps1
- test finance admin can edit product and 
- test devotional text and platform specif
- FakeSent
- claude watchdog.sh
- Quran Content Storage (Telegram channel-
- Roadmap Phase 10 — Messenger Mini Apps
- security headers()
- get quran total pages()
- quran editions.py
- validate body()
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
- AsyncSession
- str
- Exception
- NotifyFn
- datetime
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
1. `t()` - 345 edges
2. `session_scope()` - 273 edges
3. `Platform` - 241 edges
4. `new_id()` - 128 edges
5. `User` - 124 edges
6. `Khatm` - 112 edges
7. `safe_answer_callback()` - 86 edges
8. `KhatmStatus` - 76 edges
9. `Base` - 73 edges
10. `resolve_or_provision_user()` - 70 edges

## Surprising Connections (you probably didn't know these)
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py
- `رفع‌شدهٔ فاز ۲ (این جلسه، با تست)` --references--> `snooze_keyboard()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/keyboards.py
- `سازنده (Creator) — تلگرام` --references--> `personal_report()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/report.py
- `سازنده (Creator) — تلگرام` --references--> `khatm_qr()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/my_khatms.py
- `سازنده (Creator) — تلگرام` --references--> `handle_creator_finance()`  [INFERRED]
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

## Communities (218 total, 69 thin omitted)

### Community 0 - "sqlalchemy"
Cohesion: 0.02
Nodes (6): alembic, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, sqlalchemy

### Community 1 - "new id()"
Cohesion: 0.03
Nodes (133): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), User, KhatmTemplateType, KhatmTypeEnum, Participation (+125 more)

### Community 2 - "create khatm.py"
Cohesion: 0.06
Nodes (110): callback_query, CallbackQuery, CommandObject, FSMContext, KhatmCategoryGroup, Message, Platform, _after_commitment_total() (+102 more)

### Community 3 - "db.py"
Cohesion: 0.06
Nodes (41): contextlib, httpx, khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, openpyxl, pytest, Async SQLAlchemy engine/session setup. One engine for the whole process., UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys… (+33 more)

### Community 4 - "identity/service.py"
Cohesion: 0.06
Nodes (62): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_fsm_storage_memory, aiogram_types, apscheduler_schedulers_asyncio, functools (+54 more)

### Community 5 - "t()"
Cohesion: 0.06
Nodes (87): base64, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, help_command(), help_topic(), Message, Plain-language, button-driven help for inexperienced bot users. (+79 more)

### Community 6 - "my khatms.py"
Cohesion: 0.06
Nodes (83): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at(), creator_begin_schedule_date() (+75 more)

### Community 7 - "wallet/service.py"
Cohesion: 0.06
Nodes (80): CouponDiscountType, CouponRedemption, PaymentGateway, PaymentVerification, PendingPayment, add_balance(), add_credit(), bind_invoice_resource() (+72 more)

### Community 8 - "Platform"
Cohesion: 0.11
Nodes (73): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+65 more)

### Community 9 - "datetime"
Cohesion: 0.08
Nodes (40): datetime, DeclarativeBase, enum, re, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models. (+32 more)

### Community 10 - "settings menu.py"
Cohesion: 0.07
Nodes (71): _lang_for(), _lang_for(), _lang_for(), CommandObject, message, set_font(), language_command(), CommandObject (+63 more)

### Community 11 - "invitation/service.py"
Cohesion: 0.06
Nodes (60): dataclasses, hashlib, hmac, json, secrets, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).… (+52 more)

### Community 13 - "Khatm"
Cohesion: 0.11
Nodes (59): creator_save_cosmetic_edit(), delete_account(), Safely deactivate a user while retaining non-PII history. Active committed…, Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create() (+51 more)

### Community 14 - "start.py"
Cohesion: 0.06
Nodes (55): عضو (Member bots) — تلگرام fa/ar/en و بله, Khatm, begin_account_link(), FSMContext, message, receive_link_code(), receive_link_phone(), receive_change_code() (+47 more)

### Community 15 - "portions.py"
Cohesion: 0.10
Nodes (50): request_khatm_description(), apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze(), ask_pause_duration(), ask_snooze() (+42 more)

### Community 16 - "member my khatms.py"
Cohesion: 0.07
Nodes (47): KhatmAllocationPlan, list_member_khatms(), callback_query, CallbackQuery, FSMContext, message, Member bot "My Khatms" handler — lists khatms the user joined via this bot…, Show the current portion for one joined khatm, with the same action buttons the… (+39 more)

### Community 17 - "allocation/repository.py"
Cohesion: 0.12
Nodes (42): CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Allocation module: the generic, template-driven portion engine. A plan is…, Per-submission log for quantity-commitment portions (salawat, dua, laan).… (+34 more)

### Community 18 - "khatm category/service.py"
Cohesion: 0.13
Nodes (39): KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str, Admin-managed content library for independent devotional families. Owner…, A participant's typed request for a دعا that isn't in the library yet (owner…, create() (+31 more)

### Community 19 - "phone/repository.py"
Cohesion: 0.11
Nodes (37): AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module., Return a bounded newest-first timeline without exposing mutation APIs., record(), approve(), OtpChallenge (+29 more)

### Community 20 - "provider.py"
Cohesion: 0.10
Nodes (27): BaseSettings, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Protocol (+19 more)

### Community 21 - "reminder engine/service.py"
Cohesion: 0.13
Nodes (36): collections, NotificationKind, NotifyFn, SendQuranPagesFn, Positive khatm-completion announcements., Scheduled positive personal monthly reports., _default_reminder_hour(), delegate_inactive_portions() (+28 more)

### Community 22 - "app.py"
Cohesion: 0.12
Nodes (38): fastapi, fastapi_staticfiles, fastapi_templating, get, RedirectResponse, admins(), _audit_details(), _audit_label() (+30 more)

### Community 23 - "safe answer callback()"
Cohesion: 0.13
Nodes (38): callback_query, CallbackQuery, quran_help(), set_audio_callback(), help_open_my_khatms(), help_start_creation(), callback_query, CallbackQuery (+30 more)

### Community 24 - "creator request/service.py"
Cohesion: 0.11
Nodes (34): handle_creator_request_button(), callback_query, CallbackQuery, Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve() (+26 more)

### Community 25 - "session scope()"
Cohesion: 0.08
Nodes (36): cancel_account_deletion(), confirm_account_deletion(), _lang_for(), callback_query, CallbackQuery, CommandObject, Message, _set_audio() (+28 more)

### Community 26 - "bot registry.py"
Cohesion: 0.09
Nodes (25): KhatmCategory, khatmsaz_modules_khatm_models, _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, build_notify_fn(), notify(), build_send_quran_pages_fn(), send_quran_pages() (+17 more)

### Community 27 - "participation/repository.py"
Cohesion: 0.11
Nodes (34): ParticipationStatus, CommitmentMode, advance_open_reading(), count_committed_active(), count_for_khatm(), create(), get_active(), get_by_id() (+26 more)

### Community 28 - "Request"
Cohesion: 0.21
Nodes (33): AdminPermission, post, Request, _admin(), _authenticate_telegram_mini_app(), change_admin_role(), create_category(), create_coupon() (+25 more)

### Community 29 - "safe clear inline keyboard()"
Cohesion: 0.15
Nodes (31): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), CreatorBroadcastFlow, callback_query, CallbackQuery, FSMContext, message (+23 more)

### Community 30 - "bot registry/service.py"
Cohesion: 0.15
Nodes (29): AsyncSession, cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot(), list_active() (+21 more)

### Community 31 - "notification/service.py"
Cohesion: 0.13
Nodes (26): message, set_reminder(), NotificationKind, NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since() (+18 more)

### Community 32 - "UserRole"
Cohesion: 0.14
Nodes (29): AdminRole, AdminRoleGrant, CapabilityType, str, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession (+21 more)

### Community 33 - "test deep link clears old state before s"
Cohesion: 0.10
Nodes (13): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_join_preview_cancel_always_acknowledges_callback() (+5 more)

### Community 34 - "member registration.py"
Cohesion: 0.13
Nodes (29): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+21 more)

### Community 35 - "test registration starts in the users sa"
Cohesion: 0.08
Nodes (16): ProfileEdit, StatesGroup, StatesGroup, Registration, FakeMessage, FakeState, asyncio, integration (+8 more)

### Community 36 - "sms subscription/service.py"
Cohesion: 0.15
Nodes (28): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+20 more)

### Community 37 - "participation/service.py"
Cohesion: 0.13
Nodes (28): Exception, sqlalchemy_exc, advance_open_reading(), AlreadyParticipatingError, count_for_khatm(), get_active(), is_paused(), join() (+20 more)

### Community 38 - "khatm workflow/service.py"
Cohesion: 0.13
Nodes (26): Participation, approve_join_request(), cancel_khatm(), _complete_join(), InvalidCreatorDecisionError, join_via_token(), JoinRequiresApprovalError, KhatmCancellationError (+18 more)

### Community 39 - "PlatformIdentity"
Cohesion: 0.13
Nodes (28): PlatformIdentity, UserStatus, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity(), list_platform_identities() (+20 more)

### Community 40 - "test member commitment logic.py"
Cohesion: 0.12
Nodes (26): is_regular_due(), is_regular_occurrence_today(), log_count(), _minutes(), persian_dow(), datetime, R11 (owner 2026-09-28): member-side commitment logic — pure, side-effect-free.…, Add ``amount`` to a COUNT-mode member's logged total. Returns ``(new_done,… (+18 more)

### Community 41 - "content/service.py"
Cohesion: 0.13
Nodes (25): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., add_devotional_audio_variant(), add_devotional_image_page(), get_allowed_reciters(), get_effective_reciter(), _get_enabled_devotional_asset(), list_all_devotional_assets() (+17 more)

### Community 42 - "wallet/models.py"
Cohesion: 0.13
Nodes (26): CouponDiscountType, CouponRedemption, DiscountCoupon, InvoiceKind, InvoiceStatus, PendingPayment, str, Wallet module: toman balance + advertising credit, append-only ledger, and… (+18 more)

### Community 43 - "plan/models.py"
Cohesion: 0.20
Nodes (23): PlanDefinition, PlanTier, PricingMode, str, Plan module: assigned plan tier per user (FREE / BASIC / PRO). Missing row…, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user() (+15 more)

### Community 44 - "QuranAssetKind"
Cohesion: 0.12
Nodes (24): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), parse_quran_channel_caption(), quran_channel_coverage(), Idempotently map one source-channel post to every page it covers. (+16 more)

### Community 45 - "get settings()"
Cohesion: 0.13
Nodes (22): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, build_bale_bot(), Bot, Bale Bot instance factory. Bale's bot platform speaks a Telegram-compatible Bot…, begin_phone_change() (+14 more)

### Community 46 - "panel.py"
Cohesion: 0.19
Nodes (23): admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel(), handle_admin_panel_broadcast(), handle_admin_panel_requests(), handle_admin_panel_users(), handle_creator_finance() (+15 more)

### Community 47 - "phone/service.py"
Cohesion: 0.22
Nodes (23): OtpPurpose, str, _assert_pristine_source_account(), complete_account_link(), complete_phone_change(), _consume_challenge(), _hash_code(), normalize_e164() (+15 more)

### Community 48 - "typing"
Cohesion: 0.14
Nodes (12): PaymentGateway, PaymentRequest, PaymentVerification, Protocol, Gateway boundary; PSP-specific code must live behind this protocol., PayPing v3 payment-gateway adapter. The endpoint names and payloads follow…, CallbackGateway, PostgreSQL + ASGI coverage for the public PayPing callback. (+4 more)

### Community 49 - "PayPingGateway"
Cohesion: 0.18
Nodes (13): Response, GatewayError, Exception, The PSP rejected or could not complete a request., PayPingGateway, Any, AsyncClient, asyncio (+5 more)

### Community 50 - "DevotionalAsset"
Cohesion: 0.13
Nodes (22): deliver_devotional_media(), callback_query, CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional() (+14 more)

### Community 51 - "broadcast/service.py"
Cohesion: 0.25
Nodes (19): Creator-to-member message moderation boundary., BroadcastStatus, KhatmBroadcast, str, create(), get_by_id(), list_pending(), mark_reviewed() (+11 more)

### Community 52 - "test confirm wizard resumes and finishes"
Cohesion: 0.11
Nodes (9): ChangePhone, StatesGroup, Gender, FakeCallback, FakeMessage, FakeState, integration, Owner-reported bug (2026-09-21/22): a first-time creator with an unverified… (+1 more)

### Community 53 - "suggestions.py"
Cohesion: 0.20
Nodes (20): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, StatesGroup, User feedback/bug-report inbox to admins (owner request, 2026-09-21). Updated… (+12 more)

### Community 54 - "completion/service.py"
Cohesion: 0.15
Nodes (16): collections_abc, deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Idempotent, delayed completion announcements for every platform., Claim each eligible announcement once, then notify creator + active members. (+8 more)

### Community 55 - "khatm request/repository.py"
Cohesion: 0.25
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 56 - "approve join()"
Cohesion: 0.15
Nodes (18): admin_approve_creator(), admin_reject_creator(), handle_creator_request_message(), CommandObject, message, Submit the request directly from the participant reply-menu button., approve_join(), _lang_for() (+10 more)

### Community 57 - "message template/repository.py"
Cohesion: 0.20
Nodes (15): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+7 more)

### Community 58 - "broadcast.py"
Cohesion: 0.23
Nodes (13): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, Creator message requests with mandatory admin moderation. (+5 more)

### Community 59 - "OpenContribution"
Cohesion: 0.23
Nodes (14): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+6 more)

### Community 60 - "test wizard ephemeral.py"
Cohesion: 0.24
Nodes (8): asyncio, FakeBot, FakeMessage, FakeState, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_deletes_previous_prompt(), test_wiz_failed_delete_still_sends(), test_wiz_first_call_just_sends_and_tracks_id()

### Community 61 - "KhatmSaz Project (Claude Code Instructio"
Cohesion: 0.21
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), DEC-PY-0074: Free-tier Plan Caps, DEC-PY-0075: i18n Scope, AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 62 - "Architecture Document"
Cohesion: 0.19
Nodes (14): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, Multi-Bot Architecture (26 bots), No Business Rule Invention Rule, DEC-PY-0001: Long Polling Decision, DEC-PY-0080: 26-Bot Split Architecture (+6 more)

### Community 63 - "Domain Model"
Cohesion: 0.21
Nodes (14): Allocation / Portion Assignment, Commitment Mode (Taahhodi), Khatm (Collective Recitation), Open/Free Mode (Azad), Participation, Surplus / Overflow (Mazad) Logging, Waiting List, Domain Model (+6 more)

### Community 64 - "create and launch khatm()"
Cohesion: 0.19
Nodes (14): ContentDeliveryMode, CreatorDisplayMode, KhatmTypeEnum, KhatmVisibility, ReminderTone, _count_creator_members(), create_and_launch_khatm(), _enforce_creation_cap() (+6 more)

### Community 65 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ"
Cohesion: 0.14
Nodes (13): QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), سازنده (Creator) — تلگرام, ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه) (+5 more)

### Community 66 - "sqlalchemy ext asyncio"
Cohesion: 0.25
Nodes (11): sqlalchemy_ext_asyncio, WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next() (+3 more)

### Community 67 - "UserSettings"
Cohesion: 0.25
Nodes (12): UserSettings, create_for_user(), find_by_contact_phones(), get_by_user(), list_all(), AsyncSession, Persistence access for settings — the only place that runs SQL for this module., asyncio (+4 more)

### Community 68 - "test tapping a time of day button saves "
Cohesion: 0.14
Nodes (6): FakeCallback, FakeMessage, FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 69 - "admin approve request()"
Cohesion: 0.29
Nodes (13): admin_approve_request(), admin_list_requests(), admin_reject_request(), _lang_for(), CommandObject, FSMContext, Message, request_khatm() (+5 more)

### Community 70 - "reporting/service.py"
Cohesion: 0.24
Nodes (10): ClosedMonthReport, get_closed_month_report(), get_khatm_stats(), get_personal_report(), KhatmStats, PersonalReport, AsyncSession, datetime (+2 more)

### Community 71 - "system settings/repository.py"
Cohesion: 0.28
Nodes (10): SystemSetting, get(), list_all(), AsyncSession, set(), get_int(), list_current(), AsyncSession (+2 more)

### Community 72 - "test admin visible enums have persian la"
Cohesion: 0.21
Nodes (12): _creator(), _creator_ctx(), creator_dashboard(), creator_khatm_detail(), creator_khatm_export(), _csrf(), _fa_label(), _load_creator_member_rows() (+4 more)

### Community 73 - "test reciter activates audio integration"
Cohesion: 0.22
Nodes (7): FakeCallback, FakeMessage, asyncio, integration, Owner-reported bug (2026-09-21): "قاری رو فعال میکنم اما برام صوت ارسال نمیشه"…, test_picking_a_reciter_via_settings_menu_turns_on_audio(), test_picking_a_reciter_via_typed_command_turns_on_audio()

### Community 74 - "test i18n audit.py"
Cohesion: 0.17
Nodes (6): ast, pathlib, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source(), Guards against the raw-slug / Persian-on-other-language class of bug the owner…

### Community 75 - "Devotional texts CRUD (dua/ziyarat) admi"
Cohesion: 0.24
Nodes (12): Categories admin page (devotional_slug link), CONTENT_MANAGE permission gate, devotional_assets storage table, Startup devotional text seed (Ashura, Al-Yasin, Faraj, Ahd), Devotional texts CRUD (dua/ziyarat) admin feature, Grouped sidebar/mobile-dock navigation redesign, Auto text chunking (<=3500 chars joined by \x1e), CHANGELOG Archive (until 2026-09-18) (+4 more)

### Community 76 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 77 - "test member commitment flow.py"
Cohesion: 0.24
Nodes (9): importlib_util, khatmsaz_bot, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_prefix_matches_handler(), test_mode_keyboard_callbacks() (+1 more)

### Community 78 - "begin profile()"
Cohesion: 0.23
Nodes (12): begin_profile(), choose_province(), enter_city(), enter_name(), _gender_keyboard(), _province_keyboard(), callback_query, CallbackQuery (+4 more)

### Community 79 - "test notify routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 80 - "test deliver due next portions pushes re"
Cohesion: 0.15
Nodes (8): _iana_offset_for_local_hour(), asyncio, integration, test_deliver_due_next_portions_pushes_real_content_not_just_text(), _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 81 - "test health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 82 - "test commitment hour gate.py"
Cohesion: 0.20
Nodes (7): khatmsaz_bot_handlers, khatmsaz_bot_handlers_start, _callback_update(), asyncio, Update, Regression (owner live QA 2026-09-28): right after joining a commitment khatm…, test_contribute_blocked_until_delivery_hour_set()

### Community 83 - "test bot commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 84 - "cancel commitment()"
Cohesion: 0.27
Nodes (11): accept_commitment(), cancel_commitment(), _parse_delivery_time(), callback_query, CallbackQuery, FSMContext, message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid. (+3 more)

### Community 85 - "manual phone verification/service.py"
Cohesion: 0.27
Nodes (10): decide_manual_phone_request(), callback_query, CallbackQuery, ManualVerificationError, AsyncSession, ValueError, Manual verification for foreign numbers that cannot receive Iranian SMS., reject() (+2 more)

### Community 86 - "ParticipationStatus"
Cohesion: 0.38
Nodes (10): CreatorBroadcast, calculate_broadcast_cost(), create_broadcast(), get_broadcast_audience(), get_broadcast_count_last_7_days(), get_creator_audience_count(), AsyncSession, UUID (+2 more)

### Community 87 - "conftest.py"
Cohesion: 0.20
Nodes (6): fixture, os, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 88 - "runtime status.py"
Cohesion: 0.22
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 89 - "advertising/service.py"
Cohesion: 0.36
Nodes (9): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+1 more)

### Community 90 - "devotional seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 91 - "test admin template render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 92 - "test bale invite is a real clickable lin"
Cohesion: 0.20
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 93 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 94 - "Multi-Bot Architecture Index Section"
Cohesion: 0.28
Nodes (9): Multi-Bot Architecture Index Section, Admin Token Panel /bots Route (2-step confirmation), bot_instances Database Table, Fernet Token Encryption for Bot Tokens, Creator Bot (ختم‌ساز) Responsibilities, Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), Creator Registration Flow (with OTP) (+1 more)

### Community 95 - "BotRegistry Singleton Class"
Cohesion: 0.22
Nodes (9): Restart Requirement After Token Change, BotRegistry Singleton Class, resolve_bot_category() Function, Post-Creation Invite Link Generation Flow, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link) (+1 more)

### Community 96 - "test payment safety.py"
Cohesion: 0.28
Nodes (8): khatmsaz_modules_wallet, khatmsaz_modules_wallet_gateway, asyncio, Fast safety checks for pending-payment expiry and replay behavior., test_callback_cas_loss_never_credits_wallet(), test_cleanup_delegates_with_current_time_and_reports_count(), test_expired_callback_stops_before_gateway_or_credit(), unittest_mock

### Community 97 - "positional range for step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 98 - "manual phone verification/repository.py"
Cohesion: 0.47
Nodes (8): ManualPhoneVerification, create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession, Persistence helpers for foreign-number manual verification.

### Community 99 - "test broadcast shows khatm picker()"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 100 - "test message template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 101 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

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

### Community 107 - "test mini app entry.py"
Cohesion: 0.36
Nodes (7): khatmsaz_modules_identity_models, _message(), asyncio, Fail-closed behavior before a public HTTPS Mini App origin exists., test_admin_mini_app_rejects_local_http_origin(), test_creator_mini_app_rejects_local_http_origin_before_database_access(), test_panel_buttons_request_chat_entry_before_opening_mini_app()

### Community 108 - "receive media()"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 109 - "test quran channel source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 110 - "test dispatcher routes commands while pr"
Cohesion: 0.25
Nodes (3): asyncio, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 111 - "test notification snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 112 - "test set font size validates and persist"
Cohesion: 0.32
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 113 - ". call ()"
Cohesion: 0.38
Nodes (6): BaseMiddleware, _extract_chat_id(), ModerationMiddleware, Any, _reply_blocked(), TelegramObject

### Community 114 - "main()"
Cohesion: 0.38
Nodes (5): Bot, _build_member_bots(), _configure_logging(), main(), _tag_bot()

### Community 115 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 116 - "KhatmSaz PROJECT STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 117 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 118 - "test sms subscription safety integration"
Cohesion: 0.29
Nodes (6): khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, asyncio, integration, Financial safety regression for SMS subscription purchases., test_missing_phone_is_rejected_before_any_sms_plan_debit_or_invoice()

### Community 119 - "register devotional content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 120 - "test member cancel clears state()"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 121 - "test creator finance and support buttons"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 122 - "test public khatms reply button is wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 123 - "payping callback()"
Cohesion: 0.33
Nodes (6): HTMLResponse, PayPingGateway, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 124 - "pause commitment()"
Cohesion: 0.33
Nodes (6): A missed-deadline portion goes back to the shared OPEN pool — the "emergency…, release_portion(), pause_commitment(), امروز نمی‌رسم" (DOMAIN_MODEL.md §3 Q79): proactively release today's portion…, موقتاً متوقف کن" (DOMAIN_MODEL.md §3 Q80): release any current portion (same as…, skip_today()

### Community 125 - "plan/ init .py"
Cohesion: 0.47
Nodes (4): asyncio, integration, test_creation_price_resolves_fixed_and_usage_based_plan_definitions(), test_plan_entitlement_lookup_uses_definition_not_plan_name_branching()

### Community 127 - "test next portion is withheld until next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 128 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 129 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 130 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 131 - "zzz merge three heads 2026 09 28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 132 - "str"
Cohesion: 0.40
Nodes (5): CoverStatus, CreatorDisplayMode, KhatmScheduleKind, str, ReminderTone

### Community 133 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.40
Nodes (5): Tooltip Jinja2 Macro Component, Admin Dashboard Page, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 135 - "test wizard keyboards i18n.py"
Cohesion: 0.40
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 136 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 137 - "Identity Across Platforms (phone-based m"
Cohesion: 0.50
Nodes (4): User Identity and Registration Index Section, Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 138 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 141 - "register devotional content batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 142 - "request account deletion()"
Cohesion: 0.50
Nodes (4): _confirm_keyboard(), InlineKeyboardMarkup, message, request_account_deletion()

### Community 143 - "resolve creator decision()"
Cohesion: 0.50
Nodes (4): CommandObject, message, Owner decision (2026-09-21): the missed-portion/emergency-pool system this…, resolve_creator_decision()

### Community 144 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 146 - "Base"
Cohesion: 0.67
Nodes (3): Base, Assignment, The Phase-4 flat per-khatm assignment (legacy shape, kept for parity). The…

### Community 147 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 148 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 149 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 150 - "Roadmap Phase 1 — First Real Khatm (DONE"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 151 - "PlanFeatureUnavailableError"
Cohesion: 0.67
Nodes (3): PlanFeatureUnavailableError, Exception, The active plan does not permit the requested feature.

### Community 152 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 154 - "test finance admin can edit product and "
Cohesion: 0.67
Nodes (3): asyncio, integration, test_finance_admin_can_edit_product_and_sms_plans_from_mini_app()

### Community 155 - "test devotional text and platform specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

## Knowledge Gaps
- **85 isolated node(s):** `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)`, `هدف افزوده‌شده (مالک، 2026-09-27)`, `🎯 هدف‌های بزرگِ افزوده‌شده (مالک، 2026-09-28) — نیازمند سشن اختصاصی` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1217 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **69 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t()` to `create khatm.py`, `identity/service.py`, `my khatms.py`, `test wizard keyboards i18n.py`, `Platform`, `settings menu.py`, `Khatm`, `request account deletion()`, `start.py`, `resolve creator decision()`, `portions.py`, `member my khatms.py`, `reminder engine/service.py`, `app.py`, `safe answer callback()`, `creator request/service.py`, `session scope()`, `safe clear inline keyboard()`, `notification/service.py`, `member registration.py`, `test registration starts in the users sa`, `get settings()`, `panel.py`, `DevotionalAsset`, `suggestions.py`, `approve join()`, `admin approve request()`, `test admin visible enums have persian la`, `begin profile()`, `cancel commitment()`, `manual phone verification/service.py`, `test admin template render.py`, `test creator finance and support buttons`, `test public khatms reply button is wired`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session scope()` to `new id()`, `db.py`, `identity/service.py`, `t()`, `my khatms.py`, `Platform`, `settings menu.py`, `invitation/service.py`, `register devotional content batch2.py`, `start.py`, `Khatm`, `member my khatms.py`, `khatm category/service.py`, `phone/repository.py`, `creator request/service.py`, `test finance admin can edit product and `, `test devotional text and platform specif`, `safe clear inline keyboard()`, `notification/service.py`, `UserRole`, `test registration starts in the users sa`, `wallet/models.py`, `QuranAssetKind`, `get settings()`, `DevotionalAsset`, `test confirm wizard resumes and finishes`, `suggestions.py`, `approve join()`, `message template/repository.py`, `broadcast.py`, `UserSettings`, `test tapping a time of day button saves `, `admin approve request()`, `test reciter activates audio integration`, `begin profile()`, `test deliver due next portions pushes re`, `cancel commitment()`, `manual phone verification/service.py`, `test bale invite is a real clickable lin`, `AdminFilter`, `receive media()`, `. call ()`, `test sms subscription safety integration`, `register devotional content.py`, `plan/ init .py`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `new id()`, `db.py`, `identity/service.py`, `t()`, `my khatms.py`, `settings menu.py`, `invitation/service.py`, `Khatm`, `start.py`, `member my khatms.py`, `phone/repository.py`, `creator request/service.py`, `session scope()`, `bot registry.py`, `safe clear inline keyboard()`, `notification/service.py`, `UserRole`, `test deep link clears old state before s`, `test registration starts in the users sa`, `PlatformIdentity`, `get settings()`, `phone/service.py`, `DevotionalAsset`, `test confirm wizard resumes and finishes`, `suggestions.py`, `approve join()`, `broadcast.py`, `UserSettings`, `admin approve request()`, `test reciter activates audio integration`, `begin profile()`, `test notify routing.py`, `test deliver due next portions pushes re`, `test bot commands.py`, `cancel commitment()`, `manual phone verification/service.py`, `test bale invite is a real clickable lin`, `AdminFilter`, `receive media()`, `. call ()`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 190 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 190 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `sqlalchemy` be split into smaller, more focused modules?**
  _Cohesion score 0.016855865153078776 - nodes in this community are weakly interconnected._
- **Should `new id()` be split into smaller, more focused modules?**
  _Cohesion score 0.028674203494347378 - nodes in this community are weakly interconnected._