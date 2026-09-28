# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 459 files · ~292,939 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3560 nodes · 11622 edges · 252 communities (147 shown, 105 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1438 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- sqlalchemy
- identity/service.py
- Platform
- session scope()
- phone/service.py
- wallet/service.py
- sqlalchemy ext asyncio
- KhatmTypeEnum
- Khatm
- provider.py
- datetime
- Base
- create khatm.py
- khatm category/service.py
- khatm workflow/service.py
- sqlalchemy dialects
- app.py
- panel.py
- test fresh committed salawat join asks d
- alembic
- creator request/service.py
- participation/service.py
- User
- PayPingGateway
- t()
- allocation/repository.py
- settings menu.py
- Request
- resume join after registration()
- portions.py
- reminder engine/service.py
- typing
- keyboards.py
- bot registry/service.py
- member commitment.py
- notification/service.py
- my khatms.py
- get or create()
- allocation/service.py
- content/service.py
- sms subscription/service.py
- test deep link clears old state before s
- khatm request/repository.py
- broadcast/service.py
- find by platform()
- config.py
- phone/repository.py
- plan/service.py
- profile.py
- test member commitment logic.py
- bot registry.py
- ParticipationStatus
- invite links.py
- QuranAssetKind
- Message
- help.py
- safe clear inline keyboard()
- suggestions.py
- authorization/service.py
- Participation
- DevotionalAsset
- ReplyKeyboardMarkup
- home keyboard for bot()
- message template/repository.py
- test wizard ephemeral.py
- test registration phone share only.py
- KhatmSaz Project (Claude Code Instructio
- Architecture Document
- Domain Model
- OpenContribution
- test creator contact.py
- build my khatms tree()
- test contribute blocked until delivery h
- reporting/service.py
- test i18n audit.py
- Devotional texts CRUD (dua/ziyarat) admi
- KhatmSaz VPS Deployment Guide
- test member commitment flow.py
- show wallet()
- test notify routing.py
- advertising/service.py
- test registration starts in the users sa
- asyncio
- test health.py
- devotional seed.py
- test bot commands.py
- show member portion()
- append devotional media from message()
- runtime status.py
- test admin template render.py
- test dispatcher routes commands while pr
- CSS Layouts and Responsive Design Guide
- Multi-Bot Architecture Index Section
- BotRegistry Singleton Class
- confirm account deletion()
- positional range for step()
- test broadcast shows khatm picker()
- test message template.py
- AdminFilter
- Creator Role (vs Participant)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per
- Multi-Bot (26-bot) Architecture
- qr.py
- approve join()
- test quran channel source.py
- test notification snooze.py
- main()
- Python Requirements
- KhatmSaz PROJECT STATE Log
- PayPing v3 Adapter Integration
- register devotional content.py
- test member cancel clears state()
- FakeMessage
- FakeState
- FakeMessage
- test public khatms reply button is wired
- FakeMessage
- test set font size validates and persist
- payping callback()
- receive link phone()
- set audio()
- commitment total keyboard()
- join public khatm()
- today overview()
- bot/ init .py
- test next portion is withheld until next
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earli
- env.py
- zzz merge three heads 2026 09 28.py
- ask welcome()
- lang for()
- current platform user()
- . call ()
- Tooltip Jinja2 Macro Component
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based m
- Settings Menu Full-Button Test Scenario
- 1f9fe3de23a1 add khatm requests table.py
- 435027907255 add daily deadline hour to 
- 687e213ff34b add contact phone to user s
- b7c8d9e0f1a2 add bot instances.py
- c21644dab334 add skip today pause and le
- register devotional content batch2.py
- set audio callback()
- ask creator contact()
- set khatm content mode()
- AccountDeletionBlocked
- zoneinfo
- FakeState
- test devotional category navigation.py
- test previous month report is positive l
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE
- Creator Panel Base Layout Template
- start bot.ps1
- test devotional text and platform specif
- test current quran delivery is exact and
- claude watchdog.sh
- Quran Content Storage (Telegram channel-
- Roadmap Phase 10 — Messenger Mini Apps
- CreatorKhatmEdit
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
- CallbackQuery
- FSMContext
- InlineKeyboardMarkup
- Message
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
1. `t()` - 284 edges
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
- `عضو (Member bots) — تلگرام fa/ar/en و بله` --references--> `BotRole`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/modules/bot_registry/models.py
- `عضو (Member bots) — تلگرام fa/ar/en و بله` --references--> `handle_member_join_callback()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/member_start.py
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py
- `سازنده (Creator) — تلگرام` --references--> `_ask_mode()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/create_khatm.py
- `سازنده (Creator) — تلگرام` --references--> `finish_invite_links()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/create_khatm.py

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

## Communities (252 total, 105 thin omitted)

### Community 0 - "sqlalchemy"
Cohesion: 0.06
Nodes (57): httpx, khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl, pytest, re (+49 more)

### Community 1 - "identity/service.py"
Cohesion: 0.07
Nodes (59): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types, apscheduler_schedulers_asyncio, BaseMiddleware, html (+51 more)

### Community 2 - "Platform"
Cohesion: 0.07
Nodes (91): aiogram_exceptions, sqlalchemy_exc, build_bale_bot(), Bot, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set() (+83 more)

### Community 3 - "session scope()"
Cohesion: 0.03
Nodes (85): list_member_khatms(), message, AsyncSession, Yield a session, committing on success and rolling back on error., session_scope(), new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-… (+77 more)

### Community 4 - "phone/service.py"
Cohesion: 0.05
Nodes (79): collections_abc, ensure_creator_phone_verified(), FSMContext, Message, Return true when creation may continue; otherwise start the OTP step., receive_change_code(), receive_new_phone(), verify_creator_phone() (+71 more)

### Community 5 - "wallet/service.py"
Cohesion: 0.06
Nodes (81): CouponDiscountType, CouponRedemption, PaymentGateway, PaymentVerification, PendingPayment, add_balance(), add_credit(), bind_invoice_resource() (+73 more)

### Community 6 - "sqlalchemy ext asyncio"
Cohesion: 0.05
Nodes (65): hashlib, secrets, sqlalchemy_ext_asyncio, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, create(), get_by_token_hash() (+57 more)

### Community 7 - "KhatmTypeEnum"
Cohesion: 0.05
Nodes (59): CoverStatus, CreatorDisplayMode, KhatmScheduleKind, KhatmTemplateType, KhatmTypeEnum, str, ReminderTone, Participation (+51 more)

### Community 8 - "Khatm"
Cohesion: 0.11
Nodes (61): delete_account(), Safely deactivate a user while retaining non-PII history. Active committed…, Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id() (+53 more)

### Community 9 - "provider.py"
Cohesion: 0.06
Nodes (45): BaseSettings, dataclasses, hmac, json, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider (+37 more)

### Community 10 - "datetime"
Cohesion: 0.09
Nodes (28): datetime, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Import every module's models so they register on `Base.metadata`. Alembic's…, Account-merge module: append-only audit of completed account merges., Per-khatm advertising opt-in and reward-credit accrual., Allocation module: the generic, template-driven portion engine. A plan is… (+20 more)

### Community 11 - "Base"
Cohesion: 0.06
Nodes (54): DeclarativeBase, ChangePhone, StatesGroup, Base, Shared declarative base for every module's models., AuditLog, list_recent(), AsyncSession (+46 more)

### Community 12 - "create khatm.py"
Cohesion: 0.15
Nodes (53): callback_query, CallbackQuery, FSMContext, KhatmCategoryGroup, Platform, _after_creator_display(), _after_recitation_text(), _after_start_schedule() (+45 more)

### Community 13 - "khatm category/service.py"
Cohesion: 0.10
Nodes (42): CreateKhatm, KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str, Admin-managed content library for independent devotional families. Owner…, A participant's typed request for a دعا that isn't in the library yet (owner… (+34 more)

### Community 14 - "khatm workflow/service.py"
Cohesion: 0.08
Nodes (45): ContentDeliveryMode, CreatorDisplayMode, KhatmTypeEnum, KhatmVisibility, Participation, ReminderTone, Static Quran edition registry — total page counts per edition. Mirrors the…, approve_join_request() (+37 more)

### Community 16 - "app.py"
Cohesion: 0.09
Nodes (46): fastapi, fastapi_staticfiles, fastapi_templating, get, middleware, _audit_details(), _audit_label(), audit_timeline() (+38 more)

### Community 17 - "panel.py"
Cohesion: 0.08
Nodes (42): سازنده (Creator) — تلگرام, khatmsaz_modules_identity_models, khatmsaz_modules_wallet, khatmsaz_modules_wallet_gateway, admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel() (+34 more)

### Community 18 - "test fresh committed salawat join asks d"
Cohesion: 0.05
Nodes (30): _parse_delivery_time(), message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., receive_delivery_hour(), _save_delivery_time(), AskDeliveryHour, JoinWorkflow, StatesGroup (+22 more)

### Community 20 - "creator request/service.py"
Cohesion: 0.10
Nodes (40): admin_approve_creator(), admin_reject_creator(), handle_creator_request_button(), handle_creator_request_message(), callback_query, CallbackQuery, CommandObject, message (+32 more)

### Community 21 - "participation/service.py"
Cohesion: 0.10
Nodes (40): ParticipationStatus, advance_open_reading(), count_for_khatm(), list_active_for_user(), list_active_with_users(), log_commitment_count(), mark_open_reading_sent_now(), mark_schedule_sent_now() (+32 more)

### Community 22 - "User"
Cohesion: 0.09
Nodes (36): PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity(), list_platform_identities() (+28 more)

### Community 23 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, GatewayError, PaymentGateway, PaymentRequest, PaymentVerification, Exception, Protocol, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 24 - "t()"
Cohesion: 0.11
Nodes (40): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+32 more)

### Community 25 - "allocation/repository.py"
Cohesion: 0.13
Nodes (40): CommittedQuantityLog, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion(), assign_portion() (+32 more)

### Community 26 - "settings menu.py"
Cohesion: 0.16
Nodes (37): begin_phone_change(), _lang_for(), buy_sms_plan(), _lang_for(), callback_query, CallbackQuery, FSMContext, Fully button-driven personal settings menu. Every preference here used to be a… (+29 more)

### Community 27 - "Request"
Cohesion: 0.20
Nodes (38): AdminPermission, post, RedirectResponse, Request, _admin(), admins(), change_admin_role(), create_category() (+30 more)

### Community 28 - "resume join after registration()"
Cohesion: 0.07
Nodes (37): CommandObject, QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), عضو (Member bots) — تلگرام fa/ar/en و بله, ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک) (+29 more)

### Community 29 - "portions.py"
Cohesion: 0.15
Nodes (37): apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze(), ask_pause_duration(), ask_snooze(), _deliver_quran_pages() (+29 more)

### Community 30 - "reminder engine/service.py"
Cohesion: 0.15
Nodes (35): collections, NotificationKind, NotifyFn, SendQuranPagesFn, get_by_id(), _default_reminder_hour(), delegate_inactive_portions(), deliver_due_next_portions() (+27 more)

### Community 31 - "typing"
Cohesion: 0.06
Nodes (3): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 32 - "keyboards.py"
Cohesion: 0.12
Nodes (33): base64, InlineKeyboardButton, InlineKeyboardMarkup, advertising_choice_keyboard(), cancel_khatm_confirm_keyboard(), capacity_choice_keyboard(), category_choice_keyboard(), _ck_cancel_row() (+25 more)

### Community 33 - "bot registry/service.py"
Cohesion: 0.13
Nodes (32): AsyncSession, Base, cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot() (+24 more)

### Community 34 - "member commitment.py"
Cohesion: 0.15
Nodes (33): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), choose_weekday(), CommitFlow, enter_count() (+25 more)

### Community 35 - "notification/service.py"
Cohesion: 0.12
Nodes (28): message, set_reminder(), JobStatus, NotifChannel, NotificationKind, NotificationLog, str, count_logs() (+20 more)

### Community 36 - "my khatms.py"
Cohesion: 0.23
Nodes (32): csv, ask_cancel_khatm(), cancel_cancel_khatm(), confirm_cancel_khatm(), creator_begin_cosmetic_edit(), creator_begin_end_at(), creator_begin_schedule_date(), creator_cancel_cosmetic_edit() (+24 more)

### Community 37 - "get or create()"
Cohesion: 0.09
Nodes (33): _lang_for(), digest_command(), CommandObject, message, CommandObject, message, set_font(), language_command() (+25 more)

### Community 38 - "allocation/service.py"
Cohesion: 0.12
Nodes (31): KhatmAllocationPlan, mark_portion_done(), allocate_next_portion_to(), assign_quantity_commitment(), claim_next_open_portion(), complete_current_portion_and_advance(), count_open(), generate_quran_page_plan() (+23 more)

### Community 39 - "content/service.py"
Cohesion: 0.11
Nodes (29): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., add_devotional_audio_variant(), add_devotional_image_page(), get_allowed_reciters(), get_effective_reciter(), _get_enabled_devotional_asset(), get_quran_total_pages() (+21 more)

### Community 40 - "sms subscription/service.py"
Cohesion: 0.14
Nodes (29): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+21 more)

### Community 41 - "test deep link clears old state before s"
Cohesion: 0.10
Nodes (13): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_join_preview_cancel_always_acknowledges_callback() (+5 more)

### Community 42 - "khatm request/repository.py"
Cohesion: 0.14
Nodes (28): _lang_for(), callback_query, CallbackQuery, FSMContext, Message, request_khatm(), request_khatm_description(), request_khatm_document() (+20 more)

### Community 43 - "broadcast/service.py"
Cohesion: 0.19
Nodes (26): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, submit_khatm_message() (+18 more)

### Community 44 - "find by platform()"
Cohesion: 0.16
Nodes (28): creator_report_callback(), creator_web_login(), edit_khatm_title(), edit_khatm_welcome(), khatm_attention(), khatm_export(), khatm_member_detail(), khatm_members() (+20 more)

### Community 45 - "config.py"
Cohesion: 0.10
Nodes (17): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, aiogram_fsm_storage_memory, contextlib, functools, khatmsaz_bot_handlers (+9 more)

### Community 46 - "phone/repository.py"
Cohesion: 0.16
Nodes (26): OtpChallenge, PhoneClaim, PhoneClaimStatus, create_challenge(), create_or_verify_claim(), get_challenge(), get_user_verified_claim(), AsyncSession (+18 more)

### Community 47 - "plan/service.py"
Cohesion: 0.17
Nodes (25): PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition() (+17 more)

### Community 48 - "profile.py"
Cohesion: 0.14
Nodes (24): begin_profile(), choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), _gender_keyboard(), ProfileEdit (+16 more)

### Community 49 - "test member commitment logic.py"
Cohesion: 0.14
Nodes (24): CommitmentMode, is_regular_due(), is_regular_occurrence_today(), log_count(), _minutes(), persian_dow(), datetime, R11 (owner 2026-09-28): member-side commitment logic — pure, side-effect-free.… (+16 more)

### Community 50 - "bot registry.py"
Cohesion: 0.14
Nodes (14): khatmsaz_modules_khatm_models, _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, BotRegistry, Bot, UUID, Runtime registry of all live Bot instances, built once at startup., set_registry() (+6 more)

### Community 51 - "ParticipationStatus"
Cohesion: 0.16
Nodes (23): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+15 more)

### Community 52 - "invite links.py"
Cohesion: 0.11
Nodes (20): KhatmCategory, build_member_invite_links(), format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Build member-bot deep links for one khatm token. Returns an ordered dict keyed…, Render member-bot links as a readable, multi-line Persian block. (+12 more)

### Community 53 - "QuranAssetKind"
Cohesion: 0.14
Nodes (22): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), quran_channel_coverage(), Idempotently map one source-channel post to every page it covers., Return exact 604-page coverage and missing pages for channel forwards. (+14 more)

### Community 54 - "Message"
Cohesion: 0.16
Nodes (21): Message, _after_commitment_total(), _apply_coupon_code(), apply_creation_coupon(), _ask_visibility(), enter_capacity_number(), enter_commitment_quantity(), enter_commitment_total_custom() (+13 more)

### Community 55 - "help.py"
Cohesion: 0.18
Nodes (19): help_command(), help_open_my_khatms(), help_start_creation(), help_topic(), callback_query, CallbackQuery, FSMContext, Message (+11 more)

### Community 56 - "safe clear inline keyboard()"
Cohesion: 0.28
Nodes (20): admin_approve_request(), admin_reject_request(), CommandObject, _resolve_decision(), approve_leave(), ask_leave_reason(), _do_leave(), _lang_for() (+12 more)

### Community 57 - "suggestions.py"
Cohesion: 0.20
Nodes (20): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, StatesGroup, User feedback/bug-report inbox to admins (owner request, 2026-09-21). Updated… (+12 more)

### Community 58 - "authorization/service.py"
Cohesion: 0.20
Nodes (18): AdminRole, AdminRoleGrant, CapabilityType, str, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession (+10 more)

### Community 59 - "Participation"
Cohesion: 0.13
Nodes (20): Exception, count_committed_active(), create(), get_active(), list_active_for_khatm(), list_active_with_open_reading_plan(), list_active_with_regular_schedule(), Participation (+12 more)

### Community 60 - "DevotionalAsset"
Cohesion: 0.14
Nodes (20): deliver_devotional_media(), callback_query, CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional() (+12 more)

### Community 61 - "ReplyKeyboardMarkup"
Cohesion: 0.14
Nodes (17): khatmsaz_i18n, ReplyKeyboardMarkup, admin_menu_keyboard(), creator_finance_keyboard(), creator_management_keyboard(), creator_menu_keyboard(), creator_schedule_keyboard(), creator_settings_keyboard() (+9 more)

### Community 62 - "home keyboard for bot()"
Cohesion: 0.18
Nodes (17): accept_commitment(), cancel_commitment(), callback_query, CallbackQuery, FSMContext, receive_delivery_hour_button(), _lang_for(), list_public_khatms() (+9 more)

### Community 63 - "message template/repository.py"
Cohesion: 0.20
Nodes (15): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+7 more)

### Community 64 - "test wizard ephemeral.py"
Cohesion: 0.19
Nodes (8): FakeBot, FakeMessage, FakeSent, FakeState, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_deletes_previous_prompt(), test_wiz_failed_delete_still_sends(), test_wiz_first_call_just_sends_and_tracks_id()

### Community 65 - "test registration phone share only.py"
Cohesion: 0.18
Nodes (8): StatesGroup, Registration, FakeMessage, FakeState, asyncio, Owner request (2026-09-22): during initial registration on Telegram, only the…, test_bale_typed_phone_is_still_accepted_during_registration(), test_telegram_typed_phone_is_rejected_during_registration()

### Community 66 - "KhatmSaz Project (Claude Code Instructio"
Cohesion: 0.21
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), DEC-PY-0074: Free-tier Plan Caps, DEC-PY-0075: i18n Scope, AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 67 - "Architecture Document"
Cohesion: 0.19
Nodes (14): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, Multi-Bot Architecture (26 bots), No Business Rule Invention Rule, DEC-PY-0001: Long Polling Decision, DEC-PY-0080: 26-Bot Split Architecture (+6 more)

### Community 68 - "Domain Model"
Cohesion: 0.21
Nodes (14): Allocation / Portion Assignment, Commitment Mode (Taahhodi), Khatm (Collective Recitation), Open/Free Mode (Azad), Participation, Surplus / Overflow (Mazad) Logging, Waiting List, Domain Model (+6 more)

### Community 69 - "OpenContribution"
Cohesion: 0.25
Nodes (13): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+5 more)

### Community 70 - "test creator contact.py"
Cohesion: 0.22
Nodes (12): _compose_welcome_with_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/…, test_compose_appends_contact_line_to_welcome(), test_compose_contact_only_when_no_welcome(), test_compose_none_contact_passes_welcome_through() (+4 more)

### Community 71 - "build my khatms tree()"
Cohesion: 0.21
Nodes (13): _build_my_khatms_tree(), _content_group(), _khatm_bucket(), list_my_khatms(), InlineKeyboardMarkup, Which of the four top-level content families (BACKLOG.md §18 level 2) a khatm…, Owner request (2026-09-21, BACKLOG.md §18): "ختم‌های من" needs three top-level…, Canonical (language-independent) bucket key; translate at display time with… (+5 more)

### Community 72 - "test contribute blocked until delivery h"
Cohesion: 0.15
Nodes (10): CustomSnooze, LogContribution, PauseCommitment, StatesGroup, Owner request (2026-09-21): the first time a non-committed (open or waitlisted)…, SetupOpenQuranReading, _callback_update(), asyncio (+2 more)

### Community 73 - "reporting/service.py"
Cohesion: 0.24
Nodes (10): ClosedMonthReport, get_closed_month_report(), get_khatm_stats(), get_personal_report(), KhatmStats, PersonalReport, AsyncSession, datetime (+2 more)

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

### Community 78 - "show wallet()"
Cohesion: 0.21
Nodes (12): create_topup(), _lang_for(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery, InlineKeyboardMarkup, Message (+4 more)

### Community 79 - "test notify routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 80 - "advertising/service.py"
Cohesion: 0.29
Nodes (11): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+3 more)

### Community 81 - "test registration starts in the users sa"
Cohesion: 0.17
Nodes (6): FakeMessage, FakeState, asyncio, integration, parametrize, test_registration_starts_in_the_users_saved_language()

### Community 82 - "asyncio"
Cohesion: 0.20
Nodes (7): asyncio, fixture, os, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 83 - "test health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 84 - "devotional seed.py"
Cohesion: 0.20
Nodes (9): logging, _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a… (+1 more)

### Community 85 - "test bot commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 86 - "show member portion()"
Cohesion: 0.20
Nodes (11): callback_query, CallbackQuery, FSMContext, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow…, show_member_portion(), show_member_reminder_hours(), build_join_success_message() (+3 more)

### Community 87 - "append devotional media from message()"
Cohesion: 0.24
Nodes (10): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content() (+2 more)

### Community 88 - "runtime status.py"
Cohesion: 0.22
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 89 - "test admin template render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

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

### Community 94 - "confirm account deletion()"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

### Community 95 - "positional range for step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 96 - "test broadcast shows khatm picker()"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 97 - "test message template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 98 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

### Community 99 - "Creator Role (vs Participant)"
Cohesion: 0.25
Nodes (8): Creator Role (vs Participant), PayPing v3 Payment Gateway, Phone Verification (OTP + Manual), Wallet (Credit + Toman Balance), DEC-PY-0076: Separate Creator/Participant Menus, PayPing Setup Guide (Persian), Module: phone, Module: wallet

### Community 100 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 101 - "Member Bot Language Isolation (fixed per"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 102 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.29
Nodes (8): BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing, allowed_platforms Column (Telegram/Bale/Both), Participant Routing & Platform Limits Task Report

### Community 103 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 104 - "approve join()"
Cohesion: 0.43
Nodes (8): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, reject_join(), Unpack two UUIDs from a short base64 string., unpack_join_callback_data()

### Community 105 - "test quran channel source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 106 - "test notification snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 107 - "main()"
Cohesion: 0.38
Nodes (5): Bot, _build_member_bots(), _configure_logging(), main(), _tag_bot()

### Community 108 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 109 - "KhatmSaz PROJECT STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 110 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 111 - "register devotional content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 112 - "test member cancel clears state()"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 116 - "test public khatms reply button is wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 118 - "test set font size validates and persist"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 119 - "payping callback()"
Cohesion: 0.33
Nodes (6): HTMLResponse, PayPingGateway, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 120 - "receive link phone()"
Cohesion: 0.47
Nodes (6): begin_account_link(), _lang_for(), FSMContext, message, receive_link_code(), receive_link_phone()

### Community 121 - "set audio()"
Cohesion: 0.53
Nodes (6): CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), content_preferences_keyboard()

### Community 122 - "commitment total keyboard()"
Cohesion: 0.40
Nodes (5): _commitment_total_keyboard(), R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 123 - "join public khatm()"
Cohesion: 0.33
Nodes (6): join_public_khatm(), callback_query, CallbackQuery, FSMContext, is_registered(), A participant is "registered" once they have a contact phone, province, city,…

### Community 124 - "today overview()"
Cohesion: 0.40
Nodes (6): personal_report(), message, report_menu_button(), today_overview(), portion_done_keyboard(), For a portion that's still PENDING (not completed yet) — shows the content +…

### Community 125 - "bot/ init .py"
Cohesion: 0.33
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 126 - "test next portion is withheld until next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 127 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 128 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 129 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 130 - "zzz merge three heads 2026 09 28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 131 - "ask welcome()"
Cohesion: 0.50
Nodes (5): _ask_welcome(), _compose_niyyat(), enter_niyyat(), Owner rule (2026-09-27, DEC-PY-0090): the niyyat is FIXED for every khatm — «به…, skip_niyyat()

### Community 132 - "lang for()"
Cohesion: 0.40
Nodes (5): _lang_for(), CommandObject, message, Owner decision (2026-09-21): the missed-portion/emergency-pool system this…, resolve_creator_decision()

### Community 133 - "current platform user()"
Cohesion: 0.50
Nodes (5): _current_platform_user(), Message, settings_overview(), Every personal setting reachable by tapping — no slash command is required for…, settings_home_keyboard()

### Community 134 - ". call ()"
Cohesion: 0.60
Nodes (4): _extract_chat_id(), Any, _reply_blocked(), TelegramObject

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

### Community 144 - "register devotional content batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 145 - "set audio callback()"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 146 - "ask creator contact()"
Cohesion: 0.50
Nodes (4): _ask_creator_contact(), _creator_contact_keyboard(), enter_welcome(), R4: creator sets a contact handle shown in the member welcome. Offers a one-tap…

### Community 147 - "set khatm content mode()"
Cohesion: 0.67
Nodes (4): Creator-only content format selector: auto, photo, or text., set_khatm_content_mode(), set_content_delivery_mode(), ContentDeliveryMode

### Community 148 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 151 - "test devotional category navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 152 - "test previous month report is positive l"
Cohesion: 0.50
Nodes (3): asyncio, integration, test_previous_month_report_is_positive_localized_and_sent_once()

### Community 153 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 154 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 155 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 156 - "Roadmap Phase 1 — First Real Khatm (DONE"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 185 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 187 - "test devotional text and platform specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 188 - "test current quran delivery is exact and"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_current_quran_delivery_is_exact_and_reciter_specific()

## Knowledge Gaps
- **85 isolated node(s):** `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)`, `هدف افزوده‌شده (مالک، 2026-09-27)` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1222 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **105 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t()` to `sqlalchemy`, `identity/service.py`, `ask welcome()`, `phone/service.py`, `lang for()`, `session scope()`, `current platform user()`, `create khatm.py`, `app.py`, `panel.py`, `ask creator contact()`, `test fresh committed salawat join asks d`, `creator request/service.py`, `set khatm content mode()`, `User`, `settings menu.py`, `resume join after registration()`, `portions.py`, `reminder engine/service.py`, `member commitment.py`, `notification/service.py`, `my khatms.py`, `get or create()`, `allocation/service.py`, `khatm request/repository.py`, `find by platform()`, `profile.py`, `Message`, `help.py`, `safe clear inline keyboard()`, `suggestions.py`, `DevotionalAsset`, `home keyboard for bot()`, `test creator contact.py`, `build my khatms tree()`, `show wallet()`, `test registration starts in the users sa`, `show member portion()`, `test admin template render.py`, `confirm account deletion()`, `approve join()`, `test public khatms reply button is wired`, `receive link phone()`, `commitment total keyboard()`, `join public khatm()`, `today overview()`, `bot/ init .py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session scope()` to `sqlalchemy`, `identity/service.py`, `Platform`, `phone/service.py`, `lang for()`, `current platform user()`, `. call ()`, `KhatmTypeEnum`, `Khatm`, `Base`, `khatm category/service.py`, `register devotional content batch2.py`, `test fresh committed salawat join asks d`, `set khatm content mode()`, `creator request/service.py`, `User`, `test previous month report is positive l`, `settings menu.py`, `notification/service.py`, `my khatms.py`, `get or create()`, `khatm request/repository.py`, `broadcast/service.py`, `find by platform()`, `phone/repository.py`, `profile.py`, `ParticipationStatus`, `QuranAssetKind`, `help.py`, `safe clear inline keyboard()`, `suggestions.py`, `test devotional text and platform specif`, `DevotionalAsset`, `test current quran delivery is exact and`, `home keyboard for bot()`, `message template/repository.py`, `build my khatms tree()`, `show wallet()`, `test registration starts in the users sa`, `show member portion()`, `append devotional media from message()`, `confirm account deletion()`, `AdminFilter`, `approve join()`, `register devotional content.py`, `receive link phone()`, `set audio()`, `join public khatm()`, `today overview()`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `sqlalchemy`, `identity/service.py`, `session scope()`, `phone/service.py`, `lang for()`, `current platform user()`, `KhatmTypeEnum`, `Base`, `test fresh committed salawat join asks d`, `set khatm content mode()`, `creator request/service.py`, `User`, `test previous month report is positive l`, `settings menu.py`, `notification/service.py`, `my khatms.py`, `get or create()`, `test deep link clears old state before s`, `khatm request/repository.py`, `broadcast/service.py`, `find by platform()`, `config.py`, `phone/repository.py`, `profile.py`, `bot registry.py`, `ParticipationStatus`, `invite links.py`, `help.py`, `safe clear inline keyboard()`, `suggestions.py`, `DevotionalAsset`, `home keyboard for bot()`, `test registration phone share only.py`, `build my khatms tree()`, `show wallet()`, `test notify routing.py`, `test registration starts in the users sa`, `test bot commands.py`, `show member portion()`, `append devotional media from message()`, `confirm account deletion()`, `AdminFilter`, `approve join()`, `FakeMessage`, `FakeMessage`, `receive link phone()`, `set audio()`, `join public khatm()`, `today overview()`, `test next portion is withheld until next`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Are the 190 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 190 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `sqlalchemy` be split into smaller, more focused modules?**
  _Cohesion score 0.05506993006993007 - nodes in this community are weakly interconnected._
- **Should `identity/service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07173778602350031 - nodes in this community are weakly interconnected._