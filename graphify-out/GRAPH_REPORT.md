# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 448 files · ~286,936 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3401 nodes · 11475 edges · 233 communities (144 shown, 89 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 1498 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- sqlalchemy
- bot registry/service.py
- t()
- app.py
- get or create()
- identity/service.py
- Participation
- Base
- Platform
- sms subscription/service.py
- allocation/repository.py
- my khatms.py
- KhatmTypeEnum
- User
- Khatm
- panel.py
- start.py
- typing
- sqlalchemy dialects
- portions.py
- alembic
- PayPingGateway
- env.py
- create khatm.py
- session scope()
- new id()
- test admin web integration.py
- registration.py
- lang()
- test deep link clears old state before s
- allocation/service.py
- test registration starts in the users sa
- reminder engine/service.py
- KavenegarSmsProvider
- creator request/service.py
- join requests.py
- change phone.py
- wallet/repository.py
- Session
- test fresh committed salawat join asks d
- test paid khatm invoice is bound and ref
- khatm workflow/service.py
- run once()
- phone/service.py
- test bale invite is a real clickable lin
- wallet/service.py
- phone/repository.py
- profile.py
- authorization/service.py
- content/service.py
- AsyncSession
- member my khatms.py
- DevotionalAsset
- broadcast/service.py
- telegram mini app.py
- suggestions.py
- khatm request/repository.py
- after welcome()
- UserRole
- notification/service.py
- config.py
- broadcast.py
- test recitation text only for laan.py
- khatm request.py
- AsyncSession
- OpenContribution
- creator request/repository.py
- KhatmSaz Project (Claude Code Instructio
- Architecture Document
- Domain Model
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ
- message template/repository.py
- system settings/repository.py
- AsyncSession
- WaitingList
- Devotional texts CRUD (dua/ziyarat) admi
- KhatmSaz VPS Deployment Guide
- show wallet()
- advertising/service.py
- AuditLog
- manual phone verification/repository.py
- notification/repository.py
- test health.py
- test bot commands.py
- cancel commitment()
- runtime status.py
- devotional seed.py
- test admin template render.py
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
- sqlalchemy ext asyncio
- content settings.py
- receive media()
- decide manual phone request()
- test quran channel source.py
- message template/ init .py
- test notification snooze.py
- . call ()
- main()
- Python Requirements
- KhatmSaz PROJECT STATE Log
- PayPing v3 Adapter Integration
- qr.py
- test member cancel clears state()
- add devotional audio variant()
- get paid invoice by resource()
- FakeMessage
- FakeState
- test creator finance and support buttons
- FakeMessage
- test tapping a time of day button saves 
- test public khatms reply button is wired
- FakeMessage
- test set font size validates and persist
- release portion()
- test completion announcement waits is id
- test daily digest combines multiple khat
- test next portion is withheld until next
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earli
- ask welcome()
- lang for()
- help start creation()
- Tooltip Jinja2 Macro Component
- test render uses fallback locale()
- test wizard keyboards i18n.py
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based m
- Settings Menu Full-Button Test Scenario
- 435027907255 add daily deadline hour to 
- set audio callback()
- AccountDeletionBlocked
- JoinRequiresApprovalError
- ManualVerificationError
- test channel coverage counts pages not s
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE
- invite links.py
- Creator Panel Base Layout Template
- start bot.ps1
- test devotional text and platform specif
- test quran page assets require canonical
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

## Communities (233 total, 89 thin omitted)

### Community 0 - "sqlalchemy"
Cohesion: 0.07
Nodes (42): contextlib, khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, pytest, sqlalchemy, Async SQLAlchemy engine/session setup. One engine for the whole process., UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Content preferences and per-khatm reciter policy. (+34 more)

### Community 1 - "bot registry/service.py"
Cohesion: 0.05
Nodes (81): cryptography_fernet, Fernet, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., resolve_khatm_category_value(), build_notify_fn(), notify(), build_send_quran_pages_fn(), send_quran_pages() (+73 more)

### Community 2 - "t()"
Cohesion: 0.06
Nodes (86): base64, عضو (Member bots) — تلگرام fa/ar/en و بله, InlineKeyboardButton, help_command(), help_topic(), Message, Plain-language, button-driven help for inexperienced bot users., _resolve_user_info() (+78 more)

### Community 3 - "app.py"
Cohesion: 0.08
Nodes (87): AdminPermission, fastapi, fastapi_staticfiles, fastapi_templating, get, HTMLResponse, middleware, PayPingGateway (+79 more)

### Community 4 - "get or create()"
Cohesion: 0.06
Nodes (86): _lang_for(), CommandObject, send_devotional(), digest_command(), CommandObject, message, CommandObject, message (+78 more)

### Community 5 - "identity/service.py"
Cohesion: 0.07
Nodes (51): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_fsm_storage_memory, aiogram_types, apscheduler_schedulers_asyncio, logging (+43 more)

### Community 6 - "Participation"
Cohesion: 0.06
Nodes (73): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+65 more)

### Community 7 - "Base"
Cohesion: 0.08
Nodes (40): datetime, DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's… (+32 more)

### Community 8 - "Platform"
Cohesion: 0.10
Nodes (71): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+63 more)

### Community 9 - "sms subscription/service.py"
Cohesion: 0.07
Nodes (61): PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition() (+53 more)

### Community 10 - "allocation/repository.py"
Cohesion: 0.07
Nodes (60): CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion() (+52 more)

### Community 11 - "my khatms.py"
Cohesion: 0.10
Nodes (59): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at() (+51 more)

### Community 12 - "KhatmTypeEnum"
Cohesion: 0.05
Nodes (57): build_join_preview_message(), Owner complaint (2026-09-20): the old preview only showed title/…, KhatmTemplateType, KhatmTypeEnum, asyncio, integration, test_account_deletion_blocks_commitments_then_closes_open_membership(), test_admin_visible_enums_have_persian_labels() (+49 more)

### Community 13 - "User"
Cohesion: 0.07
Nodes (50): PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity(), list_platform_identities() (+42 more)

### Community 14 - "Khatm"
Cohesion: 0.13
Nodes (53): Khatm, KhatmStatus, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings(), list_pending_completion_announcement_ids() (+45 more)

### Community 15 - "panel.py"
Cohesion: 0.06
Nodes (47): khatmsaz_bot_handlers, khatmsaz_bot_handlers_start, khatmsaz_modules_identity_models, khatmsaz_modules_wallet, khatmsaz_modules_wallet_gateway, admin_panel_keyboard(), creator_panel_keyboard(), _get_context() (+39 more)

### Community 16 - "start.py"
Cohesion: 0.07
Nodes (49): html, handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload(), callback_query, CallbackQuery, CommandObject (+41 more)

### Community 17 - "typing"
Cohesion: 0.04
Nodes (7): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 19 - "portions.py"
Cohesion: 0.11
Nodes (48): apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze(), ask_pause_duration(), ask_snooze(), CustomSnooze (+40 more)

### Community 21 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, GatewayError, PaymentGateway, PaymentRequest, PaymentVerification, Exception, Protocol, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 22 - "env.py"
Cohesion: 0.06
Nodes (24): asyncio, fixture, logging_config, do_run_migrations(), run_migrations_online(), os, build_body(), main() (+16 more)

### Community 23 - "create khatm.py"
Cohesion: 0.16
Nodes (36): CommandObject, FSMContext, Message, _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _apply_coupon_code() (+28 more)

### Community 24 - "session scope()"
Cohesion: 0.12
Nodes (36): admin_approve_request(), admin_list_requests(), admin_reject_request(), CommandObject, _resolve_decision(), creator_save_cosmetic_edit(), creator_web_login(), edit_khatm_title() (+28 more)

### Community 25 - "new id()"
Cohesion: 0.07
Nodes (30): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), asyncio, integration, test_admin_khatm_and_user_searches_paginate_without_losing_filters(), asyncio (+22 more)

### Community 26 - "test admin web integration.py"
Cohesion: 0.07
Nodes (18): hashlib, httpx, io, json, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl, pathlib (+10 more)

### Community 27 - "registration.py"
Cohesion: 0.14
Nodes (30): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+22 more)

### Community 28 - "lang()"
Cohesion: 0.16
Nodes (31): callback_query, CallbackQuery, KhatmCategoryGroup, Platform, ask_creation_coupon(), _ask_mode(), cancel_wizard(), choose_allowed_platforms() (+23 more)

### Community 29 - "test deep link clears old state before s"
Cohesion: 0.10
Nodes (13): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_join_preview_cancel_always_acknowledges_callback() (+5 more)

### Community 30 - "allocation/service.py"
Cohesion: 0.13
Nodes (29): KhatmAllocationPlan, mark_portion_done(), allocate_next_portion_to(), assign_quantity_commitment(), claim_next_open_portion(), complete_current_portion_and_advance(), count_open(), generate_quran_page_plan() (+21 more)

### Community 31 - "test registration starts in the users sa"
Cohesion: 0.08
Nodes (16): ProfileEdit, StatesGroup, StatesGroup, Registration, FakeMessage, FakeState, asyncio, integration (+8 more)

### Community 32 - "reminder engine/service.py"
Cohesion: 0.09
Nodes (23): collections, collections_abc, Positive khatm-completion announcements., Scheduled positive personal monthly reports., deliver_due(), _previous_month_bounds(), AsyncSession, datetime (+15 more)

### Community 33 - "KavenegarSmsProvider"
Cohesion: 0.12
Nodes (19): KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Submit one SMS and return a normalized provider result. `otp_code`, when given,…, Safe default: never sends externally and reports why it did not., Direct SMS adapter for Kavenegar's REST ``sms/send`` endpoint., SmsSendResult, asyncio (+11 more)

### Community 34 - "creator request/service.py"
Cohesion: 0.11
Nodes (26): admin_approve_creator(), admin_reject_creator(), handle_creator_request_button(), handle_creator_request_message(), callback_query, CallbackQuery, CommandObject, message (+18 more)

### Community 35 - "join requests.py"
Cohesion: 0.18
Nodes (26): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, Creator approve/reject for a PRIVATE khatm's join request (DOMAIN_MODEL.md §2…, reject_join(), approve_leave() (+18 more)

### Community 36 - "change phone.py"
Cohesion: 0.16
Nodes (24): BaseSettings, begin_phone_change(), ChangePhone, ensure_creator_phone_verified(), _lang_for(), FSMContext, Message, StatesGroup (+16 more)

### Community 37 - "wallet/repository.py"
Cohesion: 0.14
Nodes (26): CouponDiscountType, CouponRedemption, PendingPayment, claim_pending_payment(), count_coupon_redemptions(), create_coupon_redemption(), create_for_user(), create_pending_payment() (+18 more)

### Community 38 - "Session"
Cohesion: 0.17
Nodes (24): secrets, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, Session, create(), get_active_by_hash(), AsyncSession (+16 more)

### Community 39 - "test fresh committed salawat join asks d"
Cohesion: 0.10
Nodes (19): KhatmInvitation, create(), get_by_token_hash(), mark_accepted(), AsyncSession, Persistence access for invitation — the only place that runs SQL for this…, FakeMessage, FakeState (+11 more)

### Community 40 - "test paid khatm invoice is bound and ref"
Cohesion: 0.11
Nodes (27): CouponRedemption, DiscountCoupon, InvoiceStatus, PendingPayment, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, Immutable purchase amounts plus a small paid/refunded lifecycle., Wallet, WalletInvoice (+19 more)

### Community 41 - "khatm workflow/service.py"
Cohesion: 0.11
Nodes (25): ContentDeliveryMode, CreatorDisplayMode, KhatmTypeEnum, KhatmVisibility, ReminderTone, cancel_khatm(), _count_creator_members(), create_and_launch_khatm() (+17 more)

### Community 42 - "run once()"
Cohesion: 0.18
Nodes (26): SendQuranPagesFn, has_started(), Return whether a scheduled khatm is allowed to deliver work yet., get_preference(), get_by_id(), _default_reminder_hour(), delegate_inactive_portions(), deliver_due_next_portions() (+18 more)

### Community 43 - "phone/service.py"
Cohesion: 0.20
Nodes (24): sqlalchemy_exc, Manual verification for foreign numbers that cannot receive Iranian SMS., OtpPurpose, _assert_pristine_source_account(), complete_account_link(), complete_phone_change(), _consume_challenge(), _hash_code() (+16 more)

### Community 44 - "test bale invite is a real clickable lin"
Cohesion: 0.08
Nodes (18): CoverStatus, KhatmScheduleKind, KhatmVisibility, str, ReminderTone, FakeMessage, FakeState, asyncio (+10 more)

### Community 45 - "wallet/service.py"
Cohesion: 0.13
Nodes (24): PaymentGateway, PaymentVerification, cleanup_expired_pending_payments(), _coupon_discount(), create_payment_intent(), InsufficientFundsError, InvalidCouponError, InvalidPaymentError (+16 more)

### Community 46 - "phone/repository.py"
Cohesion: 0.20
Nodes (24): approve(), OtpChallenge, PhoneClaim, PhoneClaimStatus, str, create_challenge(), create_or_verify_claim(), get_challenge() (+16 more)

### Community 47 - "profile.py"
Cohesion: 0.16
Nodes (21): begin_profile(), choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), _gender_keyboard(), _province_keyboard() (+13 more)

### Community 48 - "authorization/service.py"
Cohesion: 0.17
Nodes (22): AdminRole, AdminRoleGrant, CapabilityType, str, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession (+14 more)

### Community 49 - "content/service.py"
Cohesion: 0.14
Nodes (21): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), get_quran_total_pages(), parse_quran_channel_caption(), quran_channel_coverage() (+13 more)

### Community 50 - "AsyncSession"
Cohesion: 0.15
Nodes (24): add_balance(), add_credit(), create_paid_invoice(), record_transaction(), add_cash(), get_balances(), get_or_create_wallet(), grant_reward_credit() (+16 more)

### Community 51 - "member my khatms.py"
Cohesion: 0.13
Nodes (20): list_member_khatms(), callback_query, CallbackQuery, FSMContext, message, Member bot "My Khatms" handler — lists khatms the user joined via this bot…, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow… (+12 more)

### Community 52 - "DevotionalAsset"
Cohesion: 0.14
Nodes (20): deliver_devotional_media(), callback_query, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional_reciter_choice(), DevotionalAsset (+12 more)

### Community 53 - "broadcast/service.py"
Cohesion: 0.29
Nodes (18): BroadcastStatus, KhatmBroadcast, str, create(), get_by_id(), list_pending(), mark_reviewed(), mark_sent() (+10 more)

### Community 54 - "telegram mini app.py"
Cohesion: 0.18
Nodes (17): dataclasses, hmac, InvalidTelegramInitData, datetime, ValueError, Validation for Telegram Mini App signed launch data., The launch data is malformed, stale, or has an invalid signature., Validate Telegram's HMAC and return its authenticated user. (+9 more)

### Community 55 - "suggestions.py"
Cohesion: 0.25
Nodes (17): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, StatesGroup, User feedback/bug-report inbox to admins (owner request, 2026-09-21). Updated… (+9 more)

### Community 56 - "khatm request/repository.py"
Cohesion: 0.27
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 57 - "after welcome()"
Cohesion: 0.15
Nodes (16): _after_welcome(), _compose_welcome_with_contact(), enter_creator_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, skip_creator_contact(), use_own_contact() (+8 more)

### Community 58 - "UserRole"
Cohesion: 0.21
Nodes (17): str, UserRole, UserStatus, set_role(), set_status(), ban(), _bootstrap_super_admin_if_configured(), demote_creator() (+9 more)

### Community 59 - "notification/service.py"
Cohesion: 0.23
Nodes (16): JobStatus, NotifChannel, NotificationKind, str, already_sent_today(), AsyncSession, datetime, Notification business logic: dedup a reminder/miss send against "already sent… (+8 more)

### Community 60 - "config.py"
Cohesion: 0.15
Nodes (13): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, functools, pydantic_settings, build_bale_bot(), Bot (+5 more)

### Community 61 - "broadcast.py"
Cohesion: 0.23
Nodes (13): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, Creator message requests with mandatory admin moderation. (+5 more)

### Community 62 - "test recitation text only for laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 63 - "khatm request.py"
Cohesion: 0.25
Nodes (15): _lang_for(), callback_query, CallbackQuery, FSMContext, Message, StatesGroup, Request-a-khatm-type flow (DOMAIN_MODEL.md §2). A user submits a free-text…, request_khatm() (+7 more)

### Community 64 - "AsyncSession"
Cohesion: 0.15
Nodes (16): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., get_allowed_reciters(), get_effective_reciter(), list_all_devotional_assets(), AsyncSession, Resolve all available media for one assigned Quran page range. The caller can…, Mirrors `register_devotional_audio` — an image of the devotional text (owner… (+8 more)

### Community 65 - "OpenContribution"
Cohesion: 0.23
Nodes (14): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+6 more)

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

### Community 70 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ"
Cohesion: 0.15
Nodes (13): QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), سازنده (Creator) — تلگرام, ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه) (+5 more)

### Community 71 - "message template/repository.py"
Cohesion: 0.26
Nodes (13): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+5 more)

### Community 72 - "system settings/repository.py"
Cohesion: 0.25
Nodes (11): _inactivity_days(), SystemSetting, get(), list_all(), AsyncSession, set(), get_int(), list_current() (+3 more)

### Community 73 - "AsyncSession"
Cohesion: 0.32
Nodes (13): Participation, approve_join_request(), _complete_join(), join_via_token(), leave_khatm(), AsyncSession, Khatm, KhatmPortion (+5 more)

### Community 74 - "WaitingList"
Cohesion: 0.27
Nodes (10): WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next(), AsyncSession (+2 more)

### Community 75 - "Devotional texts CRUD (dua/ziyarat) admi"
Cohesion: 0.24
Nodes (12): Categories admin page (devotional_slug link), CONTENT_MANAGE permission gate, devotional_assets storage table, Startup devotional text seed (Ashura, Al-Yasin, Faraj, Ahd), Devotional texts CRUD (dua/ziyarat) admin feature, Grouped sidebar/mobile-dock navigation redesign, Auto text chunking (<=3500 chars joined by \x1e), CHANGELOG Archive (until 2026-09-18) (+4 more)

### Community 76 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 77 - "show wallet()"
Cohesion: 0.21
Nodes (12): create_topup(), _lang_for(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery, InlineKeyboardMarkup, Message (+4 more)

### Community 78 - "advertising/service.py"
Cohesion: 0.29
Nodes (11): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+3 more)

### Community 79 - "AuditLog"
Cohesion: 0.26
Nodes (11): AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module., Return a bounded newest-first timeline without exposing mutation APIs., record(), asyncio, integration (+3 more)

### Community 80 - "manual phone verification/repository.py"
Cohesion: 0.30
Nodes (11): ManualPhoneVerification, create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession, Persistence helpers for foreign-number manual verification. (+3 more)

### Community 81 - "notification/repository.py"
Cohesion: 0.39
Nodes (11): NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession, datetime (+3 more)

### Community 82 - "test health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 83 - "test bot commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 84 - "cancel commitment()"
Cohesion: 0.27
Nodes (11): accept_commitment(), cancel_commitment(), _parse_delivery_time(), callback_query, CallbackQuery, FSMContext, message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid. (+3 more)

### Community 85 - "runtime status.py"
Cohesion: 0.22
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 86 - "devotional seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 87 - "test admin template render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 88 - "test dispatcher routes commands while pr"
Cohesion: 0.20
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 89 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 90 - "Multi-Bot Architecture Index Section"
Cohesion: 0.28
Nodes (9): Multi-Bot Architecture Index Section, Admin Token Panel /bots Route (2-step confirmation), bot_instances Database Table, Fernet Token Encryption for Bot Tokens, Creator Bot (ختم‌ساز) Responsibilities, Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), Creator Registration Flow (with OTP) (+1 more)

### Community 91 - "BotRegistry Singleton Class"
Cohesion: 0.22
Nodes (9): Restart Requirement After Token Change, BotRegistry Singleton Class, resolve_bot_category() Function, Post-Creation Invite Link Generation Flow, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link) (+1 more)

### Community 92 - "commitment total keyboard()"
Cohesion: 0.25
Nodes (8): InlineKeyboardMarkup, _commitment_total_keyboard(), _creator_contact_keyboard(), R4: creator sets a contact handle shown in the member welcome. Offers a one-tap…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 93 - "confirm account deletion()"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

### Community 94 - "positional range for step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 95 - "test broadcast shows khatm picker()"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 96 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

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

### Community 101 - "sqlalchemy ext asyncio"
Cohesion: 0.25
Nodes (6): sqlalchemy_ext_asyncio, AsyncSession, Template lookup and safe ``{{placeholder}}`` rendering., Reject malformed or unsupported placeholders before a template is stored., render(), validate_body()

### Community 102 - "content settings.py"
Cohesion: 0.46
Nodes (7): CommandObject, Message, Per-user translation/tafsir display preferences., _set_audio(), set_audio_command(), set_content_option(), content_preferences_keyboard()

### Community 103 - "receive media()"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 104 - "decide manual phone request()"
Cohesion: 0.25
Nodes (8): _authorized_admin(), decide_manual_phone_request(), _decision_keyboard(), list_manual_phone_requests(), callback_query, CallbackQuery, InlineKeyboardMarkup, message

### Community 105 - "test quran channel source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 106 - "message template/ init .py"
Cohesion: 0.25
Nodes (4): Localized, versioned message templates., Real PostgreSQL coverage for template history and activation control., parametrize, test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 107 - "test notification snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 108 - ". call ()"
Cohesion: 0.38
Nodes (6): BaseMiddleware, _extract_chat_id(), ModerationMiddleware, Any, _reply_blocked(), TelegramObject

### Community 109 - "main()"
Cohesion: 0.38
Nodes (5): Bot, _build_member_bots(), _configure_logging(), main(), _tag_bot()

### Community 110 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 111 - "KhatmSaz PROJECT STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 112 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 113 - "qr.py"
Cohesion: 0.38
Nodes (5): qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 114 - "test member cancel clears state()"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 115 - "add devotional audio variant()"
Cohesion: 0.29
Nodes (7): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.…, Owner request (2026-09-22): a dua's image can span more than one page…, Owner request (2026-09-22): a dua's full text as a PDF document — one slot per…, set_devotional_pdf()

### Community 116 - "get paid invoice by resource()"
Cohesion: 0.29
Nodes (7): bind_invoice_resource(), get_paid_invoice_by_resource(), list_invoices_for_user(), InvoiceKind, WalletInvoice, bind_invoice_resource(), list_invoices()

### Community 119 - "test creator finance and support buttons"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 121 - "test tapping a time of day button saves "
Cohesion: 0.29
Nodes (4): FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 122 - "test public khatms reply button is wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 124 - "test set font size validates and persist"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 125 - "release portion()"
Cohesion: 0.33
Nodes (6): A missed-deadline portion goes back to the shared OPEN pool — the "emergency…, release_portion(), pause_commitment(), امروز نمی‌رسم" (DOMAIN_MODEL.md §3 Q79): proactively release today's portion…, موقتاً متوقف کن" (DOMAIN_MODEL.md §3 Q80): release any current portion (same as…, skip_today()

### Community 126 - "test completion announcement waits is id"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 128 - "test next portion is withheld until next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 129 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 130 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 131 - "ask welcome()"
Cohesion: 0.50
Nodes (5): _ask_welcome(), _compose_niyyat(), enter_niyyat(), Owner rule (2026-09-27, DEC-PY-0090): the niyyat is FIXED for every khatm — «به…, skip_niyyat()

### Community 132 - "lang for()"
Cohesion: 0.40
Nodes (5): _lang_for(), CommandObject, message, Owner decision (2026-09-21): the missed-portion/emergency-pool system this…, resolve_creator_decision()

### Community 133 - "help start creation()"
Cohesion: 0.50
Nodes (5): help_open_my_khatms(), help_start_creation(), callback_query, CallbackQuery, FSMContext

### Community 134 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.40
Nodes (5): Tooltip Jinja2 Macro Component, Admin Dashboard Page, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 135 - "test render uses fallback locale()"
Cohesion: 0.50
Nodes (4): asyncio, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale()

### Community 136 - "test wizard keyboards i18n.py"
Cohesion: 0.40
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 137 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 138 - "Identity Across Platforms (phone-based m"
Cohesion: 0.50
Nodes (4): User Identity and Registration Index Section, Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 139 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 141 - "set audio callback()"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 142 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 144 - "ManualVerificationError"
Cohesion: 0.50
Nodes (4): ManualVerificationError, AsyncSession, ValueError, reject()

### Community 145 - "test channel coverage counts pages not s"
Cohesion: 0.67
Nodes (4): asyncio, integration, test_channel_coverage_counts_pages_not_source_posts(), test_channel_range_registry_is_idempotent_and_resolves_shared_audio()

### Community 146 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 147 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 148 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 149 - "Roadmap Phase 1 — First Real Khatm (DONE"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 177 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 179 - "test devotional text and platform specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 180 - "test quran page assets require canonical"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_quran_page_assets_require_canonical_complete_ranges()

## Knowledge Gaps
- **85 isolated node(s):** `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)`, `هدف افزوده‌شده (مالک، 2026-09-27)`, `🎯 هدف‌های بزرگِ افزوده‌شده (مالک، 2026-09-28) — نیازمند سشن اختصاصی` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1157 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **89 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t()` to `ask welcome()`, `lang for()`, `identity/service.py`, `get or create()`, `app.py`, `test wizard keyboards i18n.py`, `my khatms.py`, `KhatmTypeEnum`, `panel.py`, `start.py`, `portions.py`, `create khatm.py`, `session scope()`, `registration.py`, `lang()`, `allocation/service.py`, `test registration starts in the users sa`, `creator request/service.py`, `join requests.py`, `change phone.py`, `profile.py`, `member my khatms.py`, `DevotionalAsset`, `suggestions.py`, `after welcome()`, `khatm request.py`, `QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ`, `show wallet()`, `cancel commitment()`, `test admin template render.py`, `commitment total keyboard()`, `confirm account deletion()`, `decide manual phone request()`, `test creator finance and support buttons`, `test public khatms reply button is wired`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session scope()` to `sqlalchemy`, `bot registry/service.py`, `t()`, `test next portion is withheld until next`, `lang for()`, `identity/service.py`, `Participation`, `get or create()`, `Platform`, `sms subscription/service.py`, `allocation/repository.py`, `my khatms.py`, `KhatmTypeEnum`, `User`, `start.py`, `test channel coverage counts pages not s`, `env.py`, `new id()`, `test registration starts in the users sa`, `creator request/service.py`, `join requests.py`, `change phone.py`, `Session`, `test fresh committed salawat join asks d`, `test paid khatm invoice is bound and ref`, `test bale invite is a real clickable lin`, `phone/repository.py`, `profile.py`, `authorization/service.py`, `member my khatms.py`, `DevotionalAsset`, `test devotional text and platform specif`, `test quran page assets require canonical`, `suggestions.py`, `broadcast.py`, `khatm request.py`, `message template/repository.py`, `show wallet()`, `AuditLog`, `manual phone verification/repository.py`, `cancel commitment()`, `confirm account deletion()`, `AdminFilter`, `content settings.py`, `receive media()`, `decide manual phone request()`, `. call ()`, `test tapping a time of day button saves `, `test completion announcement waits is id`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `sqlalchemy`, `bot registry/service.py`, `t()`, `test next portion is withheld until next`, `lang for()`, `identity/service.py`, `Participation`, `get or create()`, `allocation/repository.py`, `my khatms.py`, `User`, `start.py`, `env.py`, `session scope()`, `new id()`, `test deep link clears old state before s`, `test registration starts in the users sa`, `creator request/service.py`, `join requests.py`, `change phone.py`, `Session`, `test fresh committed salawat join asks d`, `phone/service.py`, `test bale invite is a real clickable lin`, `phone/repository.py`, `profile.py`, `invite links.py`, `member my khatms.py`, `DevotionalAsset`, `suggestions.py`, `UserRole`, `config.py`, `broadcast.py`, `khatm request.py`, `show wallet()`, `test bot commands.py`, `cancel commitment()`, `confirm account deletion()`, `AdminFilter`, `content settings.py`, `receive media()`, `decide manual phone request()`, `. call ()`, `FakeMessage`, `FakeMessage`, `test completion announcement waits is id`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 195 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 195 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `نتیجهٔ فاز ۱ (این جلسه)` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `sqlalchemy` be split into smaller, more focused modules?**
  _Cohesion score 0.06512605042016807 - nodes in this community are weakly interconnected._
- **Should `bot registry/service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053305879661404716 - nodes in this community are weakly interconnected._