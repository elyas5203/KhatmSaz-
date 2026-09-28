# Graph Report - Khatm  (2026-09-28)

## Corpus Check
- 437 files · ~298,086 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3602 nodes · 13051 edges · 195 communities (138 shown, 57 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 1903 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `294f9293`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- db.py
- Platform
- admin.py
- KhatmTemplateType
- phone/service.py
- wallet/service.py
- Session
- Participation
- Khatm
- provider.py
- Base
- resolve_or_provision_user
- create_khatm.py
- KhatmCategoryGroup
- sqlalchemy_ext_asyncio
- sqlalchemy
- app.py
- UserRole
- safe_answer_callback
- bot_registry/service.py
- creator_request/service.py
- participation/service.py
- User
- PayPingGateway
- Wallet
- KhatmPortion
- finish_invite_links
- new_id
- start.py
- session_scope
- reminder_engine/service.py
- creator_broadcast/service.py
- t
- test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it
- member_commitment.py
- test_registration_phone_share_only.py
- my_khatms.py
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی
- khatm_request.py
- content/service.py
- sms_subscription/service.py
- test_deep_link_clears_old_state_before_storing_new_join_context
- KhatmRequest
- broadcast.py
- test_reminder_tone_resolves_seeded_locale_template
- types
- devotional_seed.py
- PlanTier
- positional_range_for_step
- OpenContribution
- PaymentVerification
- FakeMessage
- invite_links.py
- QuranAssetKind
- seed_verified_quran_channel_map
- wallet/repository.py
- FakeMessage
- suggestions.py
- authorization/service.py
- list_identities_for_user
- message_template/__init__.py
- test_admin_visible_enums_have_persian_labels
- asyncio
- message_template/repository.py
- test_wizard_ephemeral.py
- bail_if_menu_button
- KhatmSaz Project (Claude Code Instructions)
- Architecture Document
- Domain Model
- get_closed_month_report
- test_creator_contact.py
- cancel_commitment
- notification/service.py
- system_settings/repository.py
- test_i18n_audit.py
- Devotional texts CRUD (dua/ziyarat) admin feature
- KhatmSaz VPS Deployment Guide
- test_member_commitment_flow.py
- payping_callback
- test_notify_routing.py
- advertising/service.py
- completion/service.py
- FakeState
- test_health.py
- DevotionalAsset
- install_command_menu
- render
- append_devotional_media_from_message
- runtime_status.py
- test_admin_template_render.py
- test_dispatcher_routes_commands_while_profile_phone_state_is_active
- CSS Layouts and Responsive Design Guide
- Multi-Bot Architecture Index Section
- BotRegistry Singleton Class
- test_mini_app_auth_integration.py
- member_my_khatms.py
- test_broadcast_shows_khatm_picker
- test_message_template.py
- get_khatm_stats
- Creator Role (vs Participant)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per bot)
- Multi-Bot (26-bot) Architecture
- test_contribute_blocked_until_delivery_hour_set
- FakeMessage
- test_quran_channel_source.py
- test_notification_snooze.py
- bootstrap.py
- Python Requirements
- KhatmSaz PROJECT_STATE Log
- PayPing v3 Adapter Integration
- test_deliver_due_next_portions_pushes_real_content_not_just_text
- test_member_cancel_clears_state
- get_quran_total_pages
- test_public_khatms_reply_button_is_wired
- بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`
- test_set_font_size_validates_and_persists
- set_audio_callback
- _commitment_total_keyboard
- test_creator_finance_and_support_buttons_are_wired
- bot/__init__.py
- test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member
- KhatmSaz README
- DECISIONS Archive (DEC-PY-0064 and earlier)
- register_devotional_content.py
- zzz_merge_three_heads_2026_09_28.py
- FakeState
- .__call__
- Tooltip Jinja2 Macro Component
- Mini-App Only Authentication Pattern
- Identity Across Platforms (phone-based merge key)
- Settings Menu Full-Button Test Scenario
- env.py
- test_daily_digest_combines_multiple_khatms_for_one_user
- register_devotional_content_batch2.py
- create_and_launch_khatm
- help_start_creation
- AccountDeletionBlocked
- test_bale_invite_is_a_real_clickable_link_not_a_typed_command
- BotCategory
- Bot Help Strings (Persian)
- Database Documentation
- PayPing v3 Payment Integration
- Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15)
- monthly_report/__init__.py
- Creator Panel Base Layout Template
- start_bot.ps1
- claude_watchdog.sh
- Quran Content Storage (Telegram channel-based)
- Roadmap Phase 10 — Messenger Mini Apps
- web/__init__.py
- Persian-first, Simple UX Principle
- Debugging Guide
- Content Category (khatm_category) Index Section
- INDEX — Topical Map of Documentation
- Redis (reserved for FSM / scheduler)
- dp_creator Router Registration List
- 26-Bot Grid (1 creator + 12 member per platform)
- Khatm Category Independent Families Test Scenario
- QA Handoff: Telegram Testing Guide for Codex
- khatmsaz_core
- khatmsaz_core_db
- khatmsaz_core_ids
- khatmsaz_modules_allocation
- khatmsaz_modules_identity
- khatmsaz_modules_invitation
- khatmsaz_modules_khatm_workflow
- khatmsaz_modules_notification
- khatmsaz_modules_participation
- Module: audit_log
- Module: settings
- khatmsaz_bot
- khatmsaz_bot_handlers
- khatmsaz_bot_handlers_start
- khatmsaz_i18n
- khatmsaz_modules_identity_models
- khatmsaz_modules_khatm_models
- khatmsaz_modules_wallet
- khatmsaz_modules_wallet_gateway
- audit_log/service.py
- quran_editions.py
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
1. `session_scope()` - 374 edges
2. `t()` - 348 edges
3. `Platform` - 288 edges
4. `Khatm` - 152 edges
5. `User` - 140 edges
6. `new_id()` - 139 edges
7. `safe_answer_callback()` - 113 edges
8. `KhatmTemplateType` - 112 edges
9. `resolve_or_provision_user()` - 96 edges
10. `KhatmStatus` - 91 edges

## Surprising Connections (you probably didn't know these)
- `R8. ترتیب پلتفرم: «هر دو» بالا، بعد تلگرام، بعد بله — **بدون مایگریشن**` --references--> `choose_allowed_platforms()`  [INFERRED]
  docs/ai/REDESIGN_PLAN_2026-09-28.md → src/khatmsaz/bot/handlers/create_khatm.py
- `R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**` --references--> `handle_member_start_with_payload()`  [INFERRED]
  docs/ai/REDESIGN_PLAN_2026-09-28.md → src/khatmsaz/bot/handlers/member_start.py
- `A. زیرساخت چندبات (۲۶ بات)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX_PHASE1.md → src/khatmsaz/bot/handlers/start.py
- `E. سهم و یادآوری` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX_PHASE1.md → src/khatmsaz/bot/handlers/start.py
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py

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

## Communities (195 total, 57 thin omitted)

### Community 0 - "db.py"
Cohesion: 0.06
Nodes (46): httpx, khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, pytest, re, Async SQLAlchemy engine/session setup. One engine for the whole process. (+38 more)

### Community 1 - "Platform"
Cohesion: 0.05
Nodes (77): aiogram, aiogram_filters, aiogram_types, BaseFilter, Small, user-facing Telegram command menu for the primary journeys., AdminFilter, Checks if the user has admin privileges. For now, we simply check if the user…, # TODO: If we want to check for delegated admin roles with specific permissions, (+69 more)

### Community 2 - "admin.py"
Cohesion: 0.10
Nodes (72): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+64 more)

### Community 3 - "KhatmTemplateType"
Cohesion: 0.04
Nodes (65): build_join_preview_message(), Owner complaint (2026-09-20): the old preview only showed title/…, KhatmTemplateType, KhatmTypeEnum, asyncio, integration, test_admin_can_search_khatms_by_title_creator_and_uuid(), asyncio (+57 more)

### Community 4 - "phone/service.py"
Cohesion: 0.06
Nodes (78): sqlalchemy_exc, decide_manual_phone_request(), callback_query, CallbackQuery, AccountMerge, UserStatus, set_status(), ban() (+70 more)

### Community 5 - "wallet/service.py"
Cohesion: 0.11
Nodes (40): CouponDiscountType, DiscountCoupon, InvoiceKind, str, TxType, create_paid_invoice(), get_coupon(), list_coupons() (+32 more)

### Community 6 - "Session"
Cohesion: 0.16
Nodes (25): hashlib, secrets, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, create_invitation(), mark_accepted(), AsyncSession (+17 more)

### Community 7 - "Participation"
Cohesion: 0.09
Nodes (40): approve_join_request(), cancel_khatm(), _complete_join(), _count_creator_members(), InvalidCreatorDecisionError, join_via_token(), JoinRequiresApprovalError, KhatmCancellationError (+32 more)

### Community 8 - "Khatm"
Cohesion: 0.13
Nodes (55): creator_save_cosmetic_edit(), Khatm, KhatmStatus, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+47 more)

### Community 9 - "provider.py"
Cohesion: 0.07
Nodes (42): dataclasses, hmac, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Protocol (+34 more)

### Community 10 - "Base"
Cohesion: 0.07
Nodes (46): datetime, DeclarativeBase, enum, openpyxl, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models. (+38 more)

### Community 11 - "resolve_or_provision_user"
Cohesion: 0.07
Nodes (72): digest_command(), CommandObject, message, CommandObject, message, set_font(), language_command(), CommandObject (+64 more)

### Community 12 - "create_khatm.py"
Cohesion: 0.16
Nodes (47): R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome(), _apply_coupon_code(), apply_creation_coupon() (+39 more)

### Community 13 - "KhatmCategoryGroup"
Cohesion: 0.08
Nodes (52): _bot_category_for(), CreateKhatm, StatesGroup, Map a wizard's (template_type, category_group) to the member-bot category value…, KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus (+44 more)

### Community 14 - "sqlalchemy_ext_asyncio"
Cohesion: 0.25
Nodes (11): sqlalchemy_ext_asyncio, WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next() (+3 more)

### Community 15 - "sqlalchemy"
Cohesion: 0.01
Nodes (13): alembic, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial (+5 more)

### Community 16 - "app.py"
Cohesion: 0.11
Nodes (77): fastapi, fastapi_staticfiles, fastapi_templating, get, middleware, post, RedirectResponse, Request (+69 more)

### Community 17 - "UserRole"
Cohesion: 0.11
Nodes (38): _resolve_lang(), start_wizard(), admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel(), handle_admin_panel_broadcast(), handle_admin_panel_requests() (+30 more)

### Community 18 - "safe_answer_callback"
Cohesion: 0.16
Nodes (38): ask_creation_coupon(), cancel_wizard(), choose_allowed_platforms(), choose_category(), choose_category_group(), choose_commitment_total(), choose_custom_category(), choose_edition() (+30 more)

### Community 19 - "bot_registry/service.py"
Cohesion: 0.17
Nodes (29): cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot(), list_active(), list_active_members() (+21 more)

### Community 20 - "creator_request/service.py"
Cohesion: 0.13
Nodes (31): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user() (+23 more)

### Community 21 - "participation/service.py"
Cohesion: 0.09
Nodes (51): CommitmentMode, ParticipationStatus, advance_open_reading(), count_committed_active(), count_for_khatm(), create(), get_active(), list_active_for_khatm() (+43 more)

### Community 22 - "User"
Cohesion: 0.07
Nodes (54): ChangePhone, StatesGroup, PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity() (+46 more)

### Community 23 - "PayPingGateway"
Cohesion: 0.14
Nodes (16): Response, GatewayError, Exception, Gateway boundary; PSP-specific code must live behind this protocol., The PSP rejected or could not complete a request., PayPingGateway, Any, AsyncClient (+8 more)

### Community 24 - "Wallet"
Cohesion: 0.12
Nodes (22): Wallet, WalletTransaction, add_balance(), create_for_user(), get_by_user(), record_transaction(), get_balances(), get_or_create_wallet() (+14 more)

### Community 25 - "KhatmPortion"
Cohesion: 0.08
Nodes (77): AllocationStrategy, CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).… (+69 more)

### Community 26 - "finish_invite_links"
Cohesion: 0.10
Nodes (21): A. زیرساخت چندبات (۲۶ بات), B. ثبت‌نام, C. ساخت ۴ نوع ختم, D. دعوت و عضویت, E. سهم و یادآوری, F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات, G. زبان‌ها (fa/ar/en), H. پرداخت (+13 more)

### Community 27 - "new_id"
Cohesion: 0.08
Nodes (38): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module. (+30 more)

### Community 28 - "start.py"
Cohesion: 0.08
Nodes (55): عضو (Member bots) — تلگرام fa/ar/en و بله, html, Kick off the mode picker for a freshly-joined commitment member., start_commitment_mode_picker(), handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload() (+47 more)

### Community 29 - "session_scope"
Cohesion: 0.10
Nodes (55): Any, CallbackQuery, Message, deliver_devotional_media(), CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image… (+47 more)

### Community 30 - "reminder_engine/service.py"
Cohesion: 0.14
Nodes (34): collections, SendQuranPagesFn, Positive khatm-completion announcements., has_started(), Return whether a scheduled khatm is allowed to deliver work yet., schedule_is_due(), _default_reminder_hour(), delegate_inactive_portions() (+26 more)

### Community 31 - "creator_broadcast/service.py"
Cohesion: 0.21
Nodes (19): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+11 more)

### Community 32 - "t"
Cohesion: 0.07
Nodes (78): base64, InlineKeyboardButton, help_command(), help_topic(), Message, Plain-language, button-driven help for inexperienced bot users., _resolve_user_info(), admin_menu_keyboard() (+70 more)

### Community 33 - "test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it"
Cohesion: 0.09
Nodes (22): KhatmInvitation, create(), get_by_token_hash(), mark_accepted(), AsyncSession, Persistence access for invitation — the only place that runs SQL for this…, asyncio, integration (+14 more)

### Community 34 - "member_commitment.py"
Cohesion: 0.10
Nodes (46): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), CommitFlow, enter_count(), enter_custom_time() (+38 more)

### Community 35 - "test_registration_phone_share_only.py"
Cohesion: 0.18
Nodes (8): StatesGroup, Registration, FakeMessage, FakeState, asyncio, Owner request (2026-09-22): during initial registration on Telegram, only the…, test_bale_typed_phone_is_still_accepted_during_registration(), test_telegram_typed_phone_is_rejected_during_registration()

### Community 36 - "my_khatms.py"
Cohesion: 0.06
Nodes (88): csv, io, qrcode, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group() (+80 more)

### Community 37 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی"
Cohesion: 0.17
Nodes (11): Live QA — 2026-09-28 (Chrome / Telegram Web / Codex), QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه) (+3 more)

### Community 38 - "khatm_request.py"
Cohesion: 0.21
Nodes (20): admin_approve_request(), admin_list_requests(), admin_reject_request(), _lang_for(), callback_query, CallbackQuery, CommandObject, FSMContext (+12 more)

### Community 39 - "content/service.py"
Cohesion: 0.15
Nodes (25): DevotionalMedia, KhatmReciter, A creator-approved reciter for one khatm, in display priority order., Owner request (2026-09-22): a devotional asset (dua/ziyarat) can have MORE than…, add_devotional_audio_variant(), add_devotional_image_page(), get_allowed_reciters(), get_devotional_pdf() (+17 more)

### Community 40 - "sms_subscription/service.py"
Cohesion: 0.15
Nodes (28): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+20 more)

### Community 41 - "test_deep_link_clears_old_state_before_storing_new_join_context"
Cohesion: 0.08
Nodes (15): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home() (+7 more)

### Community 42 - "KhatmRequest"
Cohesion: 0.27
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 43 - "broadcast.py"
Cohesion: 0.18
Nodes (27): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, Creator message requests with mandatory admin moderation. (+19 more)

### Community 44 - "test_reminder_tone_resolves_seeded_locale_template"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 45 - "types"
Cohesion: 0.08
Nodes (25): aiogram_enums, aiogram_fsm_storage_memory, contextlib, Regression for per-khatm broadcast targeting (owner request 2026-09-27):…, Regression (owner live QA 2026-09-28): right after joining a commitment khatm…, Regression: the creator reply-menu buttons «📊 گزارش و مالی» and «❓ راهنما و…, _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents() (+17 more)

### Community 46 - "devotional_seed.py"
Cohesion: 0.22
Nodes (8): logging, _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…

### Community 47 - "PlanTier"
Cohesion: 0.12
Nodes (34): _enforce_creation_cap(), DEC-PY-0074: a FREE-tier creator's member cap is summed across all their own…, PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan (+26 more)

### Community 48 - "positional_range_for_step"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 49 - "OpenContribution"
Cohesion: 0.11
Nodes (25): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+17 more)

### Community 50 - "PaymentVerification"
Cohesion: 0.21
Nodes (8): PaymentGateway, PaymentRequest, PaymentVerification, Protocol, create_payment_intent(), Ask a PSP for an authority, then bind it to this exact user/amount., CallbackGateway, FakeGateway

### Community 51 - "FakeMessage"
Cohesion: 0.25
Nodes (3): R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, FakeCallback, FakeMessage

### Community 52 - "invite_links.py"
Cohesion: 0.17
Nodes (14): _run_reminder_scan(), build_member_invite_links(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Build member-bot deep links for one khatm token. Returns an ordered dict keyed…, Choose one link to encode in a QR: prefer the creator's language and platform,…, build_notify_fn(), notify() (+6 more)

### Community 53 - "QuranAssetKind"
Cohesion: 0.15
Nodes (20): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), parse_quran_channel_caption(), Idempotently map one source-channel post to every page it covers., Return an exact contiguous range, or None when any page is missing. (+12 more)

### Community 54 - "seed_verified_quran_channel_map"
Cohesion: 0.29
Nodes (7): 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد, رفع‌شدهٔ همین عصر (Claude Code), پاسخ به سؤال کانال قرآن, quran_channel_coverage(), Return exact 604-page coverage and missing pages for channel forwards., Idempotently load the repository's verified 604-page source map., seed_verified_quran_channel_map()

### Community 55 - "wallet/repository.py"
Cohesion: 0.17
Nodes (24): CouponRedemption, InvoiceStatus, PendingPayment, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, Immutable purchase amounts plus a small paid/refunded lifecycle., WalletInvoice, add_credit(), bind_invoice_resource() (+16 more)

### Community 57 - "suggestions.py"
Cohesion: 0.14
Nodes (27): admin_approve_creator(), admin_reject_creator(), handle_creator_request_button(), handle_creator_request_message(), callback_query, CallbackQuery, CommandObject, message (+19 more)

### Community 58 - "authorization/service.py"
Cohesion: 0.15
Nodes (25): _authorized_admin(), list_manual_phone_requests(), message, AdminRole, AdminRoleGrant, CapabilityType, str, A revocable role assignment. Historical rows are reactivated, not deleted. (+17 more)

### Community 59 - "list_identities_for_user"
Cohesion: 0.53
Nodes (10): approve_leave(), ask_leave_reason(), _do_leave(), _lang_for(), _lang_for_user(), leave_reason_chosen(), callback_query, CallbackQuery (+2 more)

### Community 60 - "message_template/__init__.py"
Cohesion: 0.33
Nodes (3): Localized, versioned message templates., Template lookup and safe ``{{placeholder}}`` rendering., Real PostgreSQL coverage for template history and activation control.

### Community 61 - "test_admin_visible_enums_have_persian_labels"
Cohesion: 0.47
Nodes (5): _creator_ctx(), _fa_label(), _web_label(), test_admin_visible_enums_have_persian_labels(), test_unknown_machine_value_is_made_readable_without_crashing()

### Community 62 - "asyncio"
Cohesion: 0.20
Nodes (7): asyncio, fixture, os, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 63 - "message_template/repository.py"
Cohesion: 0.26
Nodes (13): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+5 more)

### Community 64 - "test_wizard_ephemeral.py"
Cohesion: 0.21
Nodes (11): FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_can_keep_intro_beside_title_until_answered(), test_wiz_deletes_previous_prompt() (+3 more)

### Community 65 - "bail_if_menu_button"
Cohesion: 0.05
Nodes (79): aiogram_fsm_state, AccountLink, begin_account_link(), _lang_for(), FSMContext, message, StatesGroup, Self-service OTP flow for linking a new platform/chat to an existing user. (+71 more)

### Community 66 - "KhatmSaz Project (Claude Code Instructions)"
Cohesion: 0.21
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), DEC-PY-0074: Free-tier Plan Caps, DEC-PY-0075: i18n Scope, AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 67 - "Architecture Document"
Cohesion: 0.19
Nodes (14): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, Multi-Bot Architecture (26 bots), No Business Rule Invention Rule, DEC-PY-0001: Long Polling Decision, DEC-PY-0080: 26-Bot Split Architecture (+6 more)

### Community 68 - "Domain Model"
Cohesion: 0.21
Nodes (14): Allocation / Portion Assignment, Commitment Mode (Taahhodi), Khatm (Collective Recitation), Open/Free Mode (Azad), Participation, Surplus / Overflow (Mazad) Logging, Waiting List, Domain Model (+6 more)

### Community 69 - "get_closed_month_report"
Cohesion: 0.29
Nodes (7): ClosedMonthReport, get_closed_month_report(), get_personal_report(), PersonalReport, AsyncSession, datetime, Aggregate one already-closed calendar month; never includes misses.

### Community 70 - "test_creator_contact.py"
Cohesion: 0.22
Nodes (12): _compose_welcome_with_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/…, test_compose_appends_contact_line_to_welcome(), test_compose_contact_only_when_no_welcome(), test_compose_none_contact_passes_welcome_through() (+4 more)

### Community 71 - "cancel_commitment"
Cohesion: 0.27
Nodes (11): accept_commitment(), cancel_commitment(), _parse_delivery_time(), callback_query, CallbackQuery, FSMContext, message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid. (+3 more)

### Community 72 - "notification/service.py"
Cohesion: 0.20
Nodes (23): NotificationKind, NotificationLog, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession, datetime (+15 more)

### Community 73 - "system_settings/repository.py"
Cohesion: 0.25
Nodes (11): _inactivity_days(), SystemSetting, get(), list_all(), AsyncSession, set(), get_int(), list_current() (+3 more)

### Community 74 - "test_i18n_audit.py"
Cohesion: 0.11
Nodes (12): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source() (+4 more)

### Community 75 - "Devotional texts CRUD (dua/ziyarat) admin feature"
Cohesion: 0.24
Nodes (12): Categories admin page (devotional_slug link), CONTENT_MANAGE permission gate, devotional_assets storage table, Startup devotional text seed (Ashura, Al-Yasin, Faraj, Ahd), Devotional texts CRUD (dua/ziyarat) admin feature, Grouped sidebar/mobile-dock navigation redesign, Auto text chunking (<=3500 chars joined by \x1e), CHANGELOG Archive (until 2026-09-18) (+4 more)

### Community 76 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 77 - "test_member_commitment_flow.py"
Cohesion: 0.27
Nodes (8): importlib_util, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_has_presets_and_custom(), test_hour_keyboard_prefix_matches_handler(), test_mode_keyboard_callbacks()

### Community 78 - "payping_callback"
Cohesion: 0.40
Nodes (5): HTMLResponse, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 79 - "test_notify_routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 80 - "advertising/service.py"
Cohesion: 0.36
Nodes (9): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+1 more)

### Community 81 - "completion/service.py"
Cohesion: 0.15
Nodes (16): collections_abc, deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Idempotent, delayed completion announcements for every platform., Claim each eligible announcement once, then notify creator + active members. (+8 more)

### Community 83 - "test_health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 84 - "DevotionalAsset"
Cohesion: 0.12
Nodes (17): callback_query, send_devotional_reciter_choice(), DevotionalAsset, Admin-curated complete text/audio for a dua or ziyarat., get_devotional_asset(), list_all_devotional_assets(), list_devotional_audio_variants(), Every devotional asset (enabled or not), newest first — for the admin… (+9 more)

### Community 85 - "install_command_menu"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 87 - "append_devotional_media_from_message"
Cohesion: 0.24
Nodes (10): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content() (+2 more)

### Community 88 - "runtime_status.py"
Cohesion: 0.22
Nodes (7): mark_scan_failed(), mark_scheduler_started(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins., snapshot()

### Community 89 - "test_admin_template_render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 90 - "test_dispatcher_routes_commands_while_profile_phone_state_is_active"
Cohesion: 0.18
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

### Community 94 - "test_mini_app_auth_integration.py"
Cohesion: 0.29
Nodes (6): json, asyncio, integration, PostgreSQL + ASGI proof for Telegram Mini App admin authentication., _signed_init_data(), test_signed_telegram_admin_launch_sets_secure_scoped_cookie()

### Community 95 - "member_my_khatms.py"
Cohesion: 0.08
Nodes (39): aiogram_fsm_context, CommandObject, Message, Per-user translation/tafsir display preferences., _set_audio(), set_audio_command(), set_content_option(), list_member_khatms() (+31 more)

### Community 96 - "test_broadcast_shows_khatm_picker"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 97 - "test_message_template.py"
Cohesion: 0.13
Nodes (8): FakeCallback, FakeMessage, asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 99 - "Creator Role (vs Participant)"
Cohesion: 0.25
Nodes (8): Creator Role (vs Participant), PayPing v3 Payment Gateway, Phone Verification (OTP + Manual), Wallet (Credit + Toman Balance), DEC-PY-0076: Separate Creator/Participant Menus, PayPing Setup Guide (Persian), Module: phone, Module: wallet

### Community 100 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 101 - "Member Bot Language Isolation (fixed per bot)"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 102 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.29
Nodes (8): BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing, allowed_platforms Column (Telegram/Bale/Both), Participant Routing & Platform Limits Task Report

### Community 103 - "test_contribute_blocked_until_delivery_hour_set"
Cohesion: 0.15
Nodes (10): CustomSnooze, LogContribution, PauseCommitment, StatesGroup, Owner request (2026-09-21): the first time a non-committed (open or waitlisted)…, SetupOpenQuranReading, _callback_update(), asyncio (+2 more)

### Community 105 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 106 - "test_notification_snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 107 - "bootstrap.py"
Cohesion: 0.12
Nodes (26): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, apscheduler_schedulers_asyncio, BaseMiddleware, BaseSettings, functools, pydantic_settings (+18 more)

### Community 108 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 109 - "KhatmSaz PROJECT_STATE Log"
Cohesion: 0.43
Nodes (7): PROJECT_STATE Archive (until 2026-09-18), Working-tree Git Diff (creator_request wiring), creator_request Module & CREATOR Role, One Quran Portion Per Day, Participant/Creator Menu Split, KhatmSaz PROJECT_STATE Log, Reminder Engine (cron scan, delivery hours)

### Community 110 - "PayPing v3 Adapter Integration"
Cohesion: 0.33
Nodes (7): Bale Bot Pending Real Token, Codex Handoff Next Steps, PayPing Gateway Activation (needs API token), Never Login With Panel Password Rule, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 111 - "test_deliver_due_next_portions_pushes_real_content_not_just_text"
Cohesion: 0.08
Nodes (18): NotificationPreference, _iana_offset_for_local_hour(), asyncio, integration, test_deliver_due_next_portions_pushes_real_content_not_just_text(), FakeState, asyncio, integration (+10 more)

### Community 112 - "test_member_cancel_clears_state"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 116 - "test_public_khatms_reply_button_is_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 117 - "بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`"
Cohesion: 0.11
Nodes (17): R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**, R13. کمترین سؤال ممکن — اصل کلی هر دو بخش., R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک**, R5. تعهد = تعداد کلِ ختم (نه per-person) با دکمه‌ها — **کد + احتمالاً مایگریشن** (+9 more)

### Community 118 - "test_set_font_size_validates_and_persists"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 121 - "set_audio_callback"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 122 - "_commitment_total_keyboard"
Cohesion: 0.25
Nodes (8): _commitment_total_keyboard(), _creator_contact_keyboard(), InlineKeyboardMarkup, R4: creator sets a contact handle shown in the member welcome. Offers a one-tap…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 123 - "test_creator_finance_and_support_buttons_are_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 125 - "bot/__init__.py"
Cohesion: 0.33
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 126 - "test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 127 - "KhatmSaz README"
Cohesion: 0.40
Nodes (5): Admin Mini App (Telegram WebApp), DEC-PY-0073: Dashboard as Mini App, Admin Mini App Guide (Persian), Deploy Guide (Persian), KhatmSaz README

### Community 128 - "DECISIONS Archive (DEC-PY-0064 and earlier)"
Cohesion: 0.40
Nodes (5): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution

### Community 129 - "register_devotional_content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 130 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 134 - ".__call__"
Cohesion: 0.60
Nodes (4): _extract_chat_id(), Any, _reply_blocked(), TelegramObject

### Community 135 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.40
Nodes (5): Tooltip Jinja2 Macro Component, Admin Dashboard Page, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 136 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 137 - "Identity Across Platforms (phone-based merge key)"
Cohesion: 0.50
Nodes (4): User Identity and Registration Index Section, Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 138 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 140 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 144 - "register_devotional_content_batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 145 - "create_and_launch_khatm"
Cohesion: 0.09
Nodes (23): CoverStatus, CreatorDisplayMode, KhatmScheduleKind, KhatmVisibility, str, create_and_launch_khatm(), `creation_price_toman` (DOMAIN_MODEL.md §7: creating a khatm costs money,…, _public_creator_name() (+15 more)

### Community 146 - "help_start_creation"
Cohesion: 0.50
Nodes (5): help_open_my_khatms(), help_start_creation(), callback_query, CallbackQuery, FSMContext

### Community 148 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 149 - "test_bale_invite_is_a_real_clickable_link_not_a_typed_command"
Cohesion: 0.18
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 150 - "BotCategory"
Cohesion: 0.15
Nodes (12): BotRegistry, Bot, UUID, Runtime registry of all live Bot instances, built once at startup., BotCategory, str, resolve_bot_category(), _bot() (+4 more)

### Community 153 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 154 - "Database Documentation"
Cohesion: 0.67
Nodes (3): Partial Unique Indexes (Hand-written), UUIDv7 Primary Keys, Database Documentation

### Community 155 - "PayPing v3 Payment Integration"
Cohesion: 0.67
Nodes (3): Payment / Wallet / Plan Index Section, PayPing v3 Payment Integration, Roadmap Phase 5 — Money (PayPing)

### Community 156 - "Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15)"
Cohesion: 0.67
Nodes (3): Roadmap Phase 0 — Bootstrap (DONE 2026-09-15), Roadmap Phase 1 — First Real Khatm (DONE 2026-09-15), Roadmap Phase 2 — Commitment Engine + Quran (PARTIAL)

### Community 185 - "Creator Panel Base Layout Template"
Cohesion: 0.67
Nodes (3): Creator Panel Base Layout Template, Creator Dashboard Page, Creator Khatm Detail Page

### Community 241 - "audit_log/service.py"
Cohesion: 0.33
Nodes (4): Append-only audit trail for sensitive administrative actions., list_recent(), AsyncSession, Business facade for recording privileged actions.

## Knowledge Gaps
- **107 isolated node(s):** `claude_watchdog.sh script`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `یافته‌های باز (از Codex، بازآزمایی‌شده در کد)`, `نتیجهٔ فاز ۱ (این جلسه)`, `ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)` (+102 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1227 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `db.py`, `register_devotional_content.py`, `Platform`, `admin.py`, `phone/service.py`, `KhatmTemplateType`, `.__call__`, `Khatm`, `resolve_or_provision_user`, `create_khatm.py`, `KhatmCategoryGroup`, `register_devotional_content_batch2.py`, `UserRole`, `safe_answer_callback`, `app.py`, `create_and_launch_khatm`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `User`, `Wallet`, `finish_invite_links`, `new_id`, `start.py`, `creator_broadcast/service.py`, `t`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `member_commitment.py`, `my_khatms.py`, `khatm_request.py`, `broadcast.py`, `test_reminder_tone_resolves_seeded_locale_template`, `PlanTier`, `OpenContribution`, `invite_links.py`, `QuranAssetKind`, `suggestions.py`, `authorization/service.py`, `list_identities_for_user`, `message_template/repository.py`, `bail_if_menu_button`, `cancel_commitment`, `payping_callback`, `test_health.py`, `DevotionalAsset`, `append_devotional_media_from_message`, `test_mini_app_auth_integration.py`, `member_my_khatms.py`, `bootstrap.py`, `test_deliver_due_next_portions_pushes_real_content_not_just_text`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `db.py`, `admin.py`, `phone/service.py`, `Khatm`, `resolve_or_provision_user`, `create_khatm.py`, `app.py`, `UserRole`, `safe_answer_callback`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `BotCategory`, `User`, `new_id`, `start.py`, `session_scope`, `creator_broadcast/service.py`, `t`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `test_registration_phone_share_only.py`, `my_khatms.py`, `khatm_request.py`, `test_deep_link_clears_old_state_before_storing_new_join_context`, `broadcast.py`, `types`, `FakeMessage`, `invite_links.py`, `FakeMessage`, `suggestions.py`, `authorization/service.py`, `list_identities_for_user`, `bail_if_menu_button`, `cancel_commitment`, `test_notify_routing.py`, `DevotionalAsset`, `install_command_menu`, `append_devotional_media_from_message`, `test_mini_app_auth_integration.py`, `member_my_khatms.py`, `FakeMessage`, `bootstrap.py`, `test_deliver_due_next_portions_pushes_real_content_not_just_text`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `Platform`, `KhatmTemplateType`, `phone/service.py`, `Khatm`, `resolve_or_provision_user`, `create_khatm.py`, `app.py`, `UserRole`, `safe_answer_callback`, `finish_invite_links`, `start.py`, `session_scope`, `reminder_engine/service.py`, `member_commitment.py`, `my_khatms.py`, `khatm_request.py`, `suggestions.py`, `list_identities_for_user`, `test_admin_visible_enums_have_persian_labels`, `bail_if_menu_button`, `test_creator_contact.py`, `cancel_commitment`, `test_admin_template_render.py`, `member_my_khatms.py`, `test_public_khatms_reply_button_is_wired`, `_commitment_total_keyboard`, `test_creator_finance_and_support_buttons_are_wired`, `bot/__init__.py`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `t()` (e.g. with `test_creator_detail_renders_manage_stats_members_export_and_settings()` and `test_help_is_complete_and_button_driven()`) actually correct?**
  _`t()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 228 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 228 INFERRED edges - model-reasoned connections that need verification._
- **Are the 129 inferred relationships involving `Khatm` (e.g. with `finish_invite_links()` and `send_other_language_links()`) actually correct?**
  _`Khatm` has 129 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)`, `یافته‌های باز (از Codex، بازآزمایی‌شده در کد)` to the rest of the system?**
  _107 weakly-connected nodes found - possible documentation gaps or missing edges._