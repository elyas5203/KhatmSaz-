# Graph Report - Khatm  (2026-09-29)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 3747 nodes · 11927 edges · 244 communities (156 shown, 88 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1399 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c687b3fb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- create_khatm.py
- sqlalchemy
- KhatmPortion
- phone/service.py
- keyboards.py
- new_id
- session_scope
- reminder_engine/service.py
- identity/service.py
- my_khatms.py
- datetime
- Participation
- start.py
- t
- Khatm
- typing
- sqlalchemy_dialects
- khatm_workflow/service.py
- get_or_create
- UserRole
- portions.py
- User
- alembic
- test_deep_link_clears_old_state_before_storing_new_join_context
- DECISIONS
- resolve_or_provision_user
- provider.py
- gateway.py
- wallet/service.py
- test_create_khatm_survives_phone_verification.py
- panel.py
- home_keyboard_for_bot
- creator_request/service.py
- bootstrap.py
- test_join_delivery_hour_ask_integration.py
- Platform
- member_commitment.py
- registration.py
- bot_registry/service.py
- khatm_category/service.py
- plan/service.py
- wallet/repository.py
- notification/service.py
- sms_subscription/service.py
- test_broadcast_target_picker.py
- manual_phone_verification/service.py
- types
- profile.py
- session/service.py
- approve_join
- env.py
- DevotionalAsset
- suggestions.py
- wallet.py
- content/service.py
- commitment.py
- bot_registry.py
- test_admin_web_integration.py
- advertising/service.py
- broadcast/service.py
- test_new_bale_identity_moves_to_existing_profile_after_otp
- test_wizard_ephemeral.py
- test_i18n_audit.py
- Architecture Document
- بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`
- khatm_request/repository.py
- Admin Panel Base Layout (base.html)
- manage_content.py
- DOMAIN_MODEL
- enter_phone
- test_recitation_text_only_for_laan.py
- AsyncSession
- reporting/service.py
- test_bale_invite_link_is_clickable.py
- Wallet
- test_quran_setup_waits_for_selected_hour_before_sending
- KhatmSaz Project (Claude Code Instructions)
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی
- sqlalchemy_ext_asyncio
- OpenContribution
- FakeState
- test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it
- test_quran_join_is_member_controlled_without_auto_allocation
- test_creator_contact.py
- QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)
- KhatmSaz VPS Deployment Guide
- Multi-Bot (26-bot) Architecture
- test_member_commitment_flow.py
- test_bot_commands.py
- account_link.py
- BotCategory
- test_dispatcher_routes_commands_while_profile_phone_state_is_active
- invite_links.py
- creator_broadcast/service.py
- message_template/__init__.py
- test_admin_template_render.py
- test_picking_a_reciter_via_settings_menu_turns_on_audio
- CSS Layouts and Responsive Design Guide
- _commitment_total_keyboard
- positional_range_for_step
- invitation/models.py
- manual_phone_verification/repository.py
- test_broadcast_shows_khatm_picker
- test_message_template.py
- DECISIONS Archive (DEC-PY-0064 and earlier)
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per bot)
- conftest.py
- qr.py
- build_join_success_message
- _moderate
- test_quran_channel_source.py
- test_mini_app_entry.py
- test_notification_snooze.py
- Python Requirements
- BotRegistry Singleton Class
- register_devotional_content.py
- test_creator_finance_and_support_buttons_are_wired
- test_creator_notified_with_phone_after_two_consecutive_missed_days
- test_member_bot_scope.py
- test_set_font_size_validates_and_persists
- audit_log/service.py
- register_devotional_text
- KhatmReciter
- delete_account
- test_deliver_due_next_portions_pushes_real_content_not_just_text
- test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member
- test_next_portion_is_withheld_until_next_local_day_at_reminder_hour
- test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour
- test_payment_safety.py
- zzz_merge_three_heads_2026_09_28.py
- confirm_account_deletion
- participation/models.py
- test_active_otp_is_reused_without_returning_another_sms_code
- Mini-App Only Authentication Pattern
- Khatm Template → BotCategory Mapping
- Settings Menu Full-Button Test Scenario
- test_default_khatm_title.py
- test_otp_request_dedup.py
- 435027907255_add_daily_deadline_hour_to_khatms.py
- register_devotional_content_batch2.py
- .__call__
- request_account_deletion
- set_audio_callback
- devotional_seed.py
- Tooltip Jinja2 Macro Component
- test_devotional_category_navigation.py
- test_rotating_portion_stays_personal_when_member_is_inactive
- test_private_join_approval_rejects_non_creator_before_join
- test_channel_coverage_counts_pages_not_source_posts
- Bot Help Strings (Persian)
- Identity Across Platforms (phone-based merge key)
- Assignment
- start_bot.ps1
- test_admin_can_search_khatms_by_title_creator_and_uuid
- test_ad_reward_requires_opt_in_and_is_idempotent
- test_devotional_slug_link_does_not_depend_on_title_wording
- test_coupon_discount_invoice_and_limits_are_atomic
- test_devotional_text_and_platform_specific_audio
- test_active_categories_are_filtered_by_the_selected_parent_family
- test_paid_khatm_invoice_is_bound_and_refunded_once
- test_public_join_page_previews_without_joining_and_rejects_cancelled_link
- test_quran_page_assets_require_canonical_complete_ranges
- test_committed_quran_readers_advance_personally_and_wrap
- claude_watchdog.sh
- broadcast/__init__.py
- web/__init__.py
- Persian-first, Simple UX Principle
- PROJECT_STATE Archive (until 2026-09-18)
- Debugging Guide
- Working-tree Git Diff (creator_request wiring)
- PayPing v3 Payment Integration
- Quran Content Storage (Telegram channel-based)
- Redis (reserved for FSM / scheduler)
- 26-Bot Grid (1 creator + 12 member per platform)
- Creator Registration Flow (with OTP)
- Khatm Category Independent Families Test Scenario
- QA Handoff: Telegram Testing Guide for Codex
- InlineKeyboardMarkup
- Khatm
- khatmsaz_bot_handlers_start
- khatmsaz_core
- khatmsaz_modules_wallet
- khatmsaz_modules_wallet_gateway
- Module: audit_log
- Module: phone
- Module: plan
- Module: settings
- Bot
- KhatmTemplateType
- Platform
- CommandObject
- ReplyKeyboardMarkup
- ValueError
- AsyncSession
- datetime
- NotifyFn
- datetime
- User
- UUID
- Admins Management Page
- Audit Log Page
- Broadcasts Admin Page
- Operations/Health Admin Page
- Phone Verifications Admin Page
- Message Templates Admin Page
- asyncio
- parametrize

## God Nodes (most connected - your core abstractions)
1. `t()` - 353 edges
2. `session_scope()` - 213 edges
3. `Platform` - 182 edges
4. `new_id()` - 113 edges
5. `safe_answer_callback()` - 112 edges
6. `User` - 102 edges
7. `Khatm` - 90 edges
8. `Base` - 71 edges
9. `Participation` - 71 edges
10. `safe_clear_inline_keyboard()` - 69 edges

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
- **26-Bot Architecture: BotRegistry + Two Dispatchers + bot_instances** — docs_ai_multibot_bot_registry_botregistry_class, docs_ai_multibot_overview_two_dispatchers, docs_ai_multibot_bot_registry_bot_instances_table, docs_ai_multibot_handler_routing_router_classification [EXTRACTED 0.95]
- **Notification Routing: joined_via_bot_instance_id → notify_fn → correct member bot** — docs_ai_multibot_notification_routing_joined_via_bot_instance_id, docs_ai_multibot_notification_routing_notify_fn, docs_ai_multibot_member_bots_member_my_khatms, docs_ai_multibot_bot_registry_botregistry_class [EXTRACTED 0.95]
- **Multi-AI Collaborative Workflow (Codex + Claude + Antigravity)** — docs_ai_ai_handoff_protocol, claude_khatmsaz_project, agents_khatmsaz_project, docs_ai_antigravity_prompt, concept_ai_handoff [EXTRACTED 1.00]
- **Mini-App-Only Login Guard Pattern** — concept_mini_app_only_auth, src_khatmsaz_web_templates_login_adminloginpage, src_khatmsaz_web_templates_creator_login_creatorloginpage, src_khatmsaz_web_templates_mini_app_login_miniapploginpage [EXTRACTED 1.00]
- **Admin & creator panel redesign effort** — docs_ai_goal_panel_redesign_2026_09_29, docs_ai_project_state_panel_redesign, docs_ai_changelog_creator_wallet_button, docs_ai_decisions_dec_py_0073_mini_apps [INFERRED 0.75]
- **Admin Panel (base, dashboard, categories, devotionals, finance, creator_requests)** — src_khatmsaz_web_templates_base_base_layout, src_khatmsaz_web_templates_dashboard_admin_dashboard, src_khatmsaz_web_templates_categories_categories_page, src_khatmsaz_web_templates_devotionals_devotionals_page, src_khatmsaz_web_templates_finance_finance_page, src_khatmsaz_web_templates_creator_requests_creator_requests [INFERRED 0.85]
- **Bot User-Facing Content (help, welcome, khatm types)** — help_strings_txt_help_strings, welcome_txt_welcome_message, concept_khatm_types [INFERRED 0.85]
- **Redesigned Creator Panel (base, dashboard, khatms, detail, wallet)** — src_khatmsaz_web_templates_creator_base_creator_layout, src_khatmsaz_web_templates_creator_dashboard_creator_dashboard, src_khatmsaz_web_templates_creator_khatms_creator_khatms, src_khatmsaz_web_templates_creator_khatm_detail_creator_khatm_detail, src_khatmsaz_web_templates_creator_wallet_creator_wallet [INFERRED 0.85]
- **Multi-bot architecture (dispatchers, bot_instances, invite links, creator bot)** — docs_ai_decisions_dec_py_0080_multibot_split, docs_ai_multibot_creator_bot_dp_creator, docs_ai_multibot_creator_bot_dp_member, docs_ai_decisions_bot_instances_table, docs_ai_changelog_invite_links_multibot [INFERRED 0.85]
- **PayPing Payment Callback Flow** — docs_dns_cloudflare_fa_payping, rahnama_vps_reverseproxycallback, rahnama_vps_paypingverify [INFERRED 0.85]
- **Quran allocation evolution (rotating -> member-chosen -> wait-for-hour, bug + DB constraint)** — docs_ai_decisions_dec_py_0092_rotating_quran_allocation, docs_ai_decisions_dec_py_0094_member_chosen_quran_pace, docs_ai_decisions_dec_py_0095_first_pages_wait_hour, docs_ai_changelog_positional_range_for_step, docs_ai_qa_matrix_quran_page_allocation_bug [INFERRED 0.85]
- **Core Domain Modules (Khatm, Participation, Allocation, Workflow)** — module_khatm, module_participation, module_allocation, module_khatm_workflow, module_waiting_list [INFERRED 0.95]

## Communities (244 total, 88 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.05
Nodes (115): AdminPermission, fastapi, fastapi_responses, fastapi_staticfiles, fastapi_templating, get, HTMLResponse, middleware (+107 more)

### Community 1 - "create_khatm.py"
Cohesion: 0.09
Nodes (101): C. ساخت ۴ نوع ختم, R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), KhatmCategoryGroup, _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome() (+93 more)

### Community 2 - "sqlalchemy"
Cohesion: 0.08
Nodes (32): khatmsaz_modules_khatm_category, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, pytest, sqlalchemy, Async SQLAlchemy engine/session setup. One engine for the whole process., UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Content preferences and per-khatm reciter policy. (+24 more)

### Community 3 - "KhatmPortion"
Cohesion: 0.08
Nodes (81): AllocationStrategy, CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, Base, str (+73 more)

### Community 4 - "phone/service.py"
Cohesion: 0.06
Nodes (75): dataclasses, hashlib, hmac, json, OtpChallenge, PhoneClaim, secrets, sqlalchemy_exc (+67 more)

### Community 5 - "keyboards.py"
Cohesion: 0.05
Nodes (72): base64, InlineKeyboardButton, khatmsaz_bot_handlers_help, help_command(), help_open_my_khatms(), help_start_creation(), help_topic(), callback_query (+64 more)

### Community 6 - "new_id"
Cohesion: 0.04
Nodes (76): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), CoverStatus, CreatorDisplayMode, KhatmScheduleKind, KhatmTemplateType (+68 more)

### Community 7 - "session_scope"
Cohesion: 0.10
Nodes (74): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+66 more)

### Community 8 - "reminder_engine/service.py"
Cohesion: 0.05
Nodes (65): AsyncSession, collections, NotificationKind, NotifyFn, SendQuranPagesFn, Positive khatm-completion announcements., MessageTemplate, create() (+57 more)

### Community 9 - "identity/service.py"
Cohesion: 0.09
Nodes (39): aiogram, aiogram_filters, aiogram_types, # TODO: If we want to check for delegated admin roles with specific permissions,, Account lifecycle commands, including safe account deletion (SPEC Q39)., Creator message requests with mandatory admin moderation., Self-service verified phone replacement that keeps all account history., Per-user translation/tafsir display preferences. (+31 more)

### Community 10 - "my_khatms.py"
Cohesion: 0.10
Nodes (64): csv, ask_cancel_khatm(), cancel_cancel_khatm(), confirm_cancel_khatm(), creator_begin_cosmetic_edit(), creator_begin_end_at(), creator_begin_schedule_date(), creator_cancel_cosmetic_edit() (+56 more)

### Community 11 - "datetime"
Cohesion: 0.09
Nodes (35): datetime, DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's… (+27 more)

### Community 12 - "Participation"
Cohesion: 0.09
Nodes (59): CommitmentMode, Participation, ParticipationStatus, advance_open_reading(), count_committed_active(), count_for_khatm(), create(), get_active() (+51 more)

### Community 13 - "start.py"
Cohesion: 0.07
Nodes (55): aiogram_fsm_context, CommandObject, عضو (Member bots) — تلگرام fa/ar/en و بله, html, handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload() (+47 more)

### Community 14 - "t"
Cohesion: 0.10
Nodes (59): ReplyKeyboardMarkup, buy_sms_plan(), _can_open_creator_panel(), _current_platform_user(), _lang_for(), callback_query, CallbackQuery, FSMContext (+51 more)

### Community 15 - "Khatm"
Cohesion: 0.12
Nodes (56): Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+48 more)

### Community 16 - "typing"
Cohesion: 0.04
Nodes (7): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 18 - "khatm_workflow/service.py"
Cohesion: 0.07
Nodes (45): ContentDeliveryMode, CreatorDisplayMode, KhatmTypeEnum, KhatmVisibility, ReminderTone, approve_join_request(), cancel_khatm(), _complete_join() (+37 more)

### Community 19 - "get_or_create"
Cohesion: 0.07
Nodes (47): CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), CommandObject, message, set_font() (+39 more)

### Community 20 - "UserRole"
Cohesion: 0.09
Nodes (45): AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module., Return a bounded newest-first timeline without exposing mutation APIs., record(), AdminRole, AdminRoleGrant (+37 more)

### Community 21 - "portions.py"
Cohesion: 0.12
Nodes (46): KhatmTemplateType, Platform, _active_participation_for_current_bot(), apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze() (+38 more)

### Community 22 - "User"
Cohesion: 0.07
Nodes (40): PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity(), list_platform_identities() (+32 more)

### Community 24 - "test_deep_link_clears_old_state_before_storing_new_join_context"
Cohesion: 0.08
Nodes (15): asyncio, parametrize, FakeMessage, FakeState, test_deep_link_clears_old_state_before_storing_new_join_context(), test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home() (+7 more)

### Community 25 - "DECISIONS"
Cohesion: 0.07
Nodes (40): Multi-Bot Architecture (26 bots), CHANGELOG Archive (until 2026-09-18), CHANGELOG, Creator wallet-charge button, Devotional content library + seed, i18n coverage guard (fa/ar/en), Multi-bot invite links (bot/invite_links.py), positional_range_for_step (rotating allocation helper) (+32 more)

### Community 26 - "resolve_or_provision_user"
Cohesion: 0.07
Nodes (40): _lang_for(), CommandObject, message, Owner decision (2026-09-21): the missed-portion/emergency-pool system this…, resolve_creator_decision(), admin_approve_creator(), admin_reject_creator(), handle_creator_request_button() (+32 more)

### Community 27 - "provider.py"
Cohesion: 0.10
Nodes (27): BaseSettings, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Protocol (+19 more)

### Community 28 - "gateway.py"
Cohesion: 0.11
Nodes (20): Response, GatewayError, PaymentRequest, PaymentVerification, Exception, Gateway boundary; PSP-specific code must live behind this protocol., The PSP rejected or could not complete a request., PayPingGateway (+12 more)

### Community 29 - "wallet/service.py"
Cohesion: 0.10
Nodes (38): PaymentGateway, Protocol, CouponDiscountType, DiscountCoupon, get_coupon(), list_coupons(), set_coupon_enabled(), upsert_coupon() (+30 more)

### Community 30 - "test_create_khatm_survives_phone_verification.py"
Cohesion: 0.06
Nodes (19): khatmsaz_modules_identity, khatmsaz_modules_settings_models, ChangePhone, StatesGroup, ProfileEdit, StatesGroup, FakeCallback, FakeMessage (+11 more)

### Community 31 - "panel.py"
Cohesion: 0.12
Nodes (36): سازنده (Creator) — تلگرام, admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel(), handle_admin_panel_broadcast(), handle_admin_panel_requests(), handle_admin_panel_users() (+28 more)

### Community 32 - "home_keyboard_for_bot"
Cohesion: 0.07
Nodes (31): _parse_delivery_time(), message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., receive_delivery_hour(), list_member_khatms(), message, _lang_for(), list_public_khatms() (+23 more)

### Community 33 - "creator_request/service.py"
Cohesion: 0.12
Nodes (33): handle_creator_request_message(), Submit the request directly from the participant reply-menu button., Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create() (+25 more)

### Community 34 - "bootstrap.py"
Cohesion: 0.08
Nodes (26): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, apscheduler_schedulers_asyncio, BaseMiddleware, Bot, functools (+18 more)

### Community 35 - "test_join_delivery_hour_ask_integration.py"
Cohesion: 0.15
Nodes (25): khatmsaz_bot_handlers_join_flow, khatmsaz_core_db, khatmsaz_core_ids, khatmsaz_core_security, khatmsaz_modules_allocation, khatmsaz_modules_identity_models, khatmsaz_modules_invitation, khatmsaz_modules_invitation_models (+17 more)

### Community 36 - "Platform"
Cohesion: 0.12
Nodes (34): build_bale_bot(), Bot, admin_approve_request(), admin_list_requests(), admin_reject_request(), _lang_for(), callback_query, CallbackQuery (+26 more)

### Community 37 - "member_commitment.py"
Cohesion: 0.16
Nodes (34): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), CommitFlow, enter_count(), enter_custom_time() (+26 more)

### Community 38 - "registration.py"
Cohesion: 0.13
Nodes (30): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+22 more)

### Community 39 - "bot_registry/service.py"
Cohesion: 0.17
Nodes (29): cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot(), list_active(), list_active_members() (+21 more)

### Community 40 - "khatm_category/service.py"
Cohesion: 0.22
Nodes (29): KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str, A participant's typed request for a دعا that isn't in the library yet (owner…, create(), create_request() (+21 more)

### Community 41 - "plan/service.py"
Cohesion: 0.15
Nodes (29): PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition() (+21 more)

### Community 42 - "wallet/repository.py"
Cohesion: 0.14
Nodes (30): CouponRedemption, InvoiceKind, InvoiceStatus, PendingPayment, str, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, Immutable purchase amounts plus a small paid/refunded lifecycle., WalletInvoice (+22 more)

### Community 43 - "notification/service.py"
Cohesion: 0.15
Nodes (24): NotificationKind, NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession (+16 more)

### Community 44 - "sms_subscription/service.py"
Cohesion: 0.15
Nodes (28): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+20 more)

### Community 45 - "test_broadcast_target_picker.py"
Cohesion: 0.09
Nodes (18): aiogram_fsm_storage_memory, MemberRegistration, StatesGroup, AskDeliveryHour, StatesGroup, Owner request (2026-09-21): every committed member should be asked what hour…, Regression for per-khatm broadcast targeting (owner request 2026-09-27):…, _callback_update() (+10 more)

### Community 46 - "manual_phone_verification/service.py"
Cohesion: 0.11
Nodes (23): collections_abc, UserStatus, set_status(), ban(), reactivate(), suspend(), warn(), ManualVerificationError (+15 more)

### Community 47 - "types"
Cohesion: 0.11
Nodes (14): contextlib, khatmsaz_bot, khatmsaz_bot_handlers, khatmsaz_i18n, _make_khatm(), Regression for the 2026-09-29 member-bot fixes (owner live report): 1. Open-…, test_quran_join_card_button_suppressed_when_autosetup(), asyncio (+6 more)

### Community 48 - "profile.py"
Cohesion: 0.14
Nodes (23): begin_profile(), choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), _gender_keyboard(), _province_keyboard() (+15 more)

### Community 49 - "session/service.py"
Cohesion: 0.18
Nodes (22): generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, create_invitation(), mark_accepted(), AsyncSession, Record the first successful acceptance for invitation-funnel metrics., create() (+14 more)

### Community 50 - "approve_join"
Cohesion: 0.18
Nodes (24): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, reject_join(), approve_leave(), ask_leave_reason() (+16 more)

### Community 51 - "env.py"
Cohesion: 0.10
Nodes (11): logging_config, do_run_migrations(), run_migrations_online(), FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform() (+3 more)

### Community 52 - "DevotionalAsset"
Cohesion: 0.13
Nodes (22): deliver_devotional_media(), callback_query, CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional() (+14 more)

### Community 53 - "suggestions.py"
Cohesion: 0.19
Nodes (21): back_to_support_menu(), choose_creator(), _member_creators(), callback_query, CallbackQuery, FSMContext, message, StatesGroup (+13 more)

### Community 54 - "wallet.py"
Cohesion: 0.16
Nodes (21): ask_custom_topup(), create_topup(), _create_topup_payment(), _lang_for(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery (+13 more)

### Community 55 - "content/service.py"
Cohesion: 0.16
Nodes (20): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), get_quran_total_pages(), quran_channel_coverage(), Quran media registry, reciter whitelist, and user delivery resolution. (+12 more)

### Community 56 - "commitment.py"
Cohesion: 0.15
Nodes (20): is_regular_due(), log_count(), _minutes(), parse_hhmm(), datetime, str, R11 (owner 2026-09-28, revised after live QA): member-side commitment logic.…, Add ``amount`` to a COUNT-mode member's logged total. Returns ``(new_done,… (+12 more)

### Community 57 - "bot_registry.py"
Cohesion: 0.15
Nodes (13): build_notify_fn(), notify(), build_send_quran_pages_fn(), send_quran_pages(), Bot, NotifyFn, Builds the callback `reminder_engine.service.deliver_due_open_quran_reading`…, BotRegistry (+5 more)

### Community 58 - "test_admin_web_integration.py"
Cohesion: 0.15
Nodes (10): httpx, openpyxl, re, Admin-reviewed phone verification for users outside Iran., Real PostgreSQL coverage for plan controls exposed in the admin Mini App., Real PostgreSQL pagination coverage for large Mini App lists., Real PostgreSQL coverage for revocable delegated admin roles., Real PostgreSQL + ASGI coverage for the admin dashboard entry flow. (+2 more)

### Community 59 - "advertising/service.py"
Cohesion: 0.14
Nodes (19): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+11 more)

### Community 60 - "broadcast/service.py"
Cohesion: 0.29
Nodes (18): BroadcastStatus, KhatmBroadcast, str, create(), get_by_id(), list_pending(), mark_reviewed(), mark_sent() (+10 more)

### Community 61 - "test_new_bale_identity_moves_to_existing_profile_after_otp"
Cohesion: 0.19
Nodes (20): OtpChallenge, OtpPurpose, PhoneClaim, PhoneClaimStatus, str, asyncio, integration, test_new_bale_identity_moves_to_existing_profile_after_otp() (+12 more)

### Community 62 - "test_wizard_ephemeral.py"
Cohesion: 0.21
Nodes (11): FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_can_keep_intro_beside_title_until_answered(), test_wiz_deletes_previous_prompt() (+3 more)

### Community 63 - "test_i18n_audit.py"
Cohesion: 0.11
Nodes (12): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source() (+4 more)

### Community 64 - "Architecture Document"
Cohesion: 0.13
Nodes (19): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, No Business Rule Invention Rule, PayPing v3 Payment Gateway, Architecture Document, Original Full Project Spec (Persian) (+11 more)

### Community 65 - "بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`"
Cohesion: 0.11
Nodes (18): R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**, R13. کمترین سؤال ممکن — اصل کلی هر دو بخش., R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک** (+10 more)

### Community 66 - "khatm_request/repository.py"
Cohesion: 0.27
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 67 - "Admin Panel Base Layout (base.html)"
Cohesion: 0.18
Nodes (18): Admin Panel Base Layout (base.html), components.html macros (tooltip), Glassmorphism Dark Design System, Permission-gated Admin Navigation, Admin Categories Page (categories.html), Creator Panel Base Layout (creator_base.html), Creator Panel i18n (t/lang) Localization, Creator Dashboard (creator_dashboard.html) (+10 more)

### Community 68 - "manage_content.py"
Cohesion: 0.15
Nodes (15): aiogram_fsm_state, BaseFilter, AdminFilter, Checks if the user has admin privileges. For now, we simply check if the user…, finish_manage_content(), ManageContentState, callback_query, CallbackQuery (+7 more)

### Community 69 - "DOMAIN_MODEL"
Cohesion: 0.16
Nodes (16): PayPing payment gateway, PendingPayment compare-and-swap replay protection, R11/N2 member commitment flow (regular/count), Codex Handoff — Next Steps, PayPing gateway activation (needs owner API token), DEC-PY-0068 — Kavenegar is first production SMS adapter, DEC-PY-0074 — Free-tier plan caps per-creator, admin-editable, DEC-PY-0090 — Fixed niyyat + optional niyabat (+8 more)

### Community 70 - "enter_phone"
Cohesion: 0.18
Nodes (9): enter_phone(), StatesGroup, Registration, FakeMessage, FakeState, asyncio, Owner request (2026-09-22): during initial registration on Telegram, only the…, test_bale_typed_phone_is_still_accepted_during_registration() (+1 more)

### Community 71 - "test_recitation_text_only_for_laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 72 - "AsyncSession"
Cohesion: 0.15
Nodes (16): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), list_all_devotional_assets(), AsyncSession, Mirrors `register_devotional_audio` — an image of the devotional text (owner…, Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.…, Owner request (2026-09-22): a dua's image can span more than one page… (+8 more)

### Community 73 - "reporting/service.py"
Cohesion: 0.18
Nodes (13): ClosedMonthReport, get_closed_month_report(), get_khatm_stats(), get_personal_report(), KhatmStats, PersonalReport, AsyncSession, datetime (+5 more)

### Community 74 - "test_bale_invite_link_is_clickable.py"
Cohesion: 0.15
Nodes (8): khatmsaz_core_bot_registry, khatmsaz_modules_bot_registry_models, FakeMessage, FakeState, asyncio, integration, Owner-reported bug (2026-09-22): "لینک جوین تو بله مشکل داره... این کد رو…, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 75 - "Wallet"
Cohesion: 0.26
Nodes (15): TxType, Wallet, add_balance(), add_credit(), create_for_user(), record_transaction(), add_cash(), get_or_create_wallet() (+7 more)

### Community 76 - "test_quran_setup_waits_for_selected_hour_before_sending"
Cohesion: 0.13
Nodes (4): FakeMessage, FakeState, asyncio, test_quran_setup_waits_for_selected_hour_before_sending()

### Community 77 - "KhatmSaz Project (Claude Code Instructions)"
Cohesion: 0.20
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), Admin Mini App (Telegram WebApp), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), Admin Mini App Guide (Persian), AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 78 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی"
Cohesion: 0.14
Nodes (14): Live QA — 2026-09-28 (Chrome / Telegram Web / Codex), QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), رفع‌شدهٔ همین عصر (Claude Code), ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live) (+6 more)

### Community 79 - "sqlalchemy_ext_asyncio"
Cohesion: 0.25
Nodes (11): sqlalchemy_ext_asyncio, WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next() (+3 more)

### Community 80 - "OpenContribution"
Cohesion: 0.25
Nodes (13): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+5 more)

### Community 81 - "FakeState"
Cohesion: 0.14
Nodes (6): FakeCallback, FakeMessage, FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 82 - "test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it"
Cohesion: 0.18
Nodes (7): FakeMessage, FakeState, asyncio, integration, R11 supersedes the old bare delivery-hour question for repetitions., test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it(), test_fresh_committed_salawat_join_asks_commitment_mode()

### Community 83 - "test_quran_join_is_member_controlled_without_auto_allocation"
Cohesion: 0.21
Nodes (8): khatmsaz_modules_khatm_workflow, asyncio, Regression: join_via_token used to NOT accept joined_via_bot_instance_id, so…, test_join_via_token_threads_bot_instance_id(), fake_get_khatm(), fake_join(), fake_resolve(), test_quran_join_is_member_controlled_without_auto_allocation()

### Community 84 - "test_creator_contact.py"
Cohesion: 0.22
Nodes (12): _compose_welcome_with_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/…, test_compose_appends_contact_line_to_welcome(), test_compose_contact_only_when_no_welcome(), test_compose_none_contact_passes_welcome_through() (+4 more)

### Community 85 - "QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)"
Cohesion: 0.17
Nodes (12): A. زیرساخت چندبات (۲۶ بات), B. ثبت‌نام, D. دعوت و عضویت, E. سهم و یادآوری, F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات, G. زبان‌ها (fa/ar/en), H. پرداخت, I. Mini App + پنل ادمین (+4 more)

### Community 86 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 87 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.20
Nodes (11): Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing (+3 more)

### Community 88 - "test_member_commitment_flow.py"
Cohesion: 0.27
Nodes (8): importlib_util, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_has_presets_and_custom(), test_hour_keyboard_prefix_matches_handler(), test_mode_keyboard_callbacks()

### Community 89 - "test_bot_commands.py"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 90 - "account_link.py"
Cohesion: 0.27
Nodes (9): AccountLink, begin_account_link(), _lang_for(), FSMContext, message, StatesGroup, Self-service OTP flow for linking a new platform/chat to an existing user., receive_link_code() (+1 more)

### Community 91 - "BotCategory"
Cohesion: 0.29
Nodes (9): _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, BotCategory, str, R2 (owner 2026-09-28): per-bot intro image shown after the creator picks…, test_dua_group_maps_to_dua_ziyarat_bot(), test_laan_group_maps_to_laan_bot(), test_quran_maps_to_quran_bot() (+1 more)

### Community 92 - "test_dispatcher_routes_commands_while_profile_phone_state_is_active"
Cohesion: 0.18
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 93 - "invite_links.py"
Cohesion: 0.20
Nodes (8): format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Render member-bot links as a readable, multi-line Persian block., Choose one link to encode in a QR: prefer the creator's language and platform,…, resolve_khatm_category_value(), resolve_bot_category()

### Community 94 - "creator_broadcast/service.py"
Cohesion: 0.40
Nodes (9): CreatorBroadcast, calculate_broadcast_cost(), create_broadcast(), get_broadcast_audience(), get_broadcast_count_last_7_days(), get_creator_audience_count(), AsyncSession, UUID (+1 more)

### Community 95 - "message_template/__init__.py"
Cohesion: 0.20
Nodes (5): Localized, versioned message templates., Real PostgreSQL coverage for template history and activation control., asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 96 - "test_admin_template_render.py"
Cohesion: 0.33
Nodes (9): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_devotionals_page_renders_clear_library_workflow_and_statuses() (+1 more)

### Community 97 - "test_picking_a_reciter_via_settings_menu_turns_on_audio"
Cohesion: 0.24
Nodes (6): FakeCallback, FakeMessage, asyncio, integration, test_picking_a_reciter_via_settings_menu_turns_on_audio(), test_picking_a_reciter_via_typed_command_turns_on_audio()

### Community 98 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 99 - "_commitment_total_keyboard"
Cohesion: 0.25
Nodes (8): _commitment_total_keyboard(), _creator_contact_keyboard(), InlineKeyboardMarkup, R4 (owner 2026-09-28): the creator MUST provide a contact so members can reach…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 100 - "positional_range_for_step"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 101 - "invitation/models.py"
Cohesion: 0.39
Nodes (7): KhatmInvitation, Invitation module: owner-issued grants to join a khatm., create(), get_by_token_hash(), mark_accepted(), AsyncSession, Persistence access for invitation — the only place that runs SQL for this…

### Community 102 - "manual_phone_verification/repository.py"
Cohesion: 0.47
Nodes (8): ManualPhoneVerification, create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession, Persistence helpers for foreign-number manual verification.

### Community 103 - "test_broadcast_shows_khatm_picker"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 104 - "test_message_template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 105 - "DECISIONS Archive (DEC-PY-0064 and earlier)"
Cohesion: 0.25
Nodes (8): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 106 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 107 - "Member Bot Language Isolation (fixed per bot)"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 108 - "conftest.py"
Cohesion: 0.25
Nodes (6): fixture, os, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 109 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 110 - "build_join_success_message"
Cohesion: 0.32
Nodes (7): Participation, build_join_success_message(), Shared with `join_requests.py`'s approval handler, which sends this same…, test_creator_display_name_is_included_and_escaped(), test_creator_welcome_is_included_and_html_escaped(), test_join_preview_is_informational_and_escaped(), test_quran_welcome_does_not_expose_fixed_portion_actions()

### Community 111 - "_moderate"
Cohesion: 0.50
Nodes (8): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, submit_khatm_message()

### Community 112 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 113 - "test_mini_app_entry.py"
Cohesion: 0.36
Nodes (7): _message(), asyncio, Fail-closed behavior before a public HTTPS Mini App origin exists., test_admin_mini_app_rejects_local_http_origin(), test_creator_mini_app_rejects_local_http_origin_before_database_access(), test_panel_buttons_request_chat_entry_before_opening_mini_app(), unittest_mock

### Community 114 - "test_notification_snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 115 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 116 - "BotRegistry Singleton Class"
Cohesion: 0.29
Nodes (7): Admin Token Panel /bots Route (2-step confirmation), Restart Requirement After Token Change, bot_instances Database Table, BotRegistry Singleton Class, Fernet Token Encryption for Bot Tokens, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow

### Community 117 - "register_devotional_content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 118 - "test_creator_finance_and_support_buttons_are_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 119 - "test_creator_notified_with_phone_after_two_consecutive_missed_days"
Cohesion: 0.38
Nodes (6): asyncio, integration, Owner decision (2026-09-22): creator notification must include member's phone…, test_creator_notified_only_after_threshold_and_member_never_notified(), fake_notify(), test_creator_notified_with_phone_after_two_consecutive_missed_days()

### Community 120 - "test_member_bot_scope.py"
Cohesion: 0.48
Nodes (5): _bot(), asyncio, test_devotional_families_do_not_cross_member_bots(), test_member_participation_is_strictly_limited_to_current_bot_instance(), test_quran_khatm_never_appears_in_dua_bot()

### Community 121 - "test_set_font_size_validates_and_persists"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 122 - "audit_log/service.py"
Cohesion: 0.33
Nodes (4): Append-only audit trail for sensitive administrative actions., list_recent(), AsyncSession, Business facade for recording privileged actions.

### Community 123 - "register_devotional_text"
Cohesion: 0.33
Nodes (6): _chunk(), AsyncSession, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), register_devotional_text()

### Community 124 - "KhatmReciter"
Cohesion: 0.33
Nodes (6): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., get_allowed_reciters(), get_effective_reciter(), Favorite wins only when allowed; otherwise use whitelist then default., set_allowed_reciters()

### Community 125 - "delete_account"
Cohesion: 0.33
Nodes (5): AccountDeletionBlocked, delete_account(), Exception, Safely deactivate a user while retaining non-PII history. Active committed…, The account still owns an obligation that must be resolved first.

### Community 126 - "test_deliver_due_next_portions_pushes_real_content_not_just_text"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_deliver_due_next_portions_pushes_real_content_not_just_text()

### Community 127 - "test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 128 - "test_next_portion_is_withheld_until_next_local_day_at_reminder_hour"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 129 - "test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 130 - "test_payment_safety.py"
Cohesion: 0.47
Nodes (5): asyncio, Fast safety checks for pending-payment expiry and replay behavior., test_callback_cas_loss_never_credits_wallet(), test_cleanup_delegates_with_current_time_and_reports_count(), test_expired_callback_stops_before_gateway_or_credit()

### Community 131 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 132 - "confirm_account_deletion"
Cohesion: 0.60
Nodes (5): cancel_account_deletion(), confirm_account_deletion(), _lang_for(), callback_query, CallbackQuery

### Community 133 - "participation/models.py"
Cohesion: 0.50
Nodes (4): AssignmentStatus, AssignmentUnitKind, str, Participation module: a user's membership in a Khatm, and per-participant…

### Community 135 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 136 - "Khatm Template → BotCategory Mapping"
Cohesion: 0.50
Nodes (4): resolve_bot_category() Function, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link), Khatm Template → BotCategory Mapping

### Community 137 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 141 - "register_devotional_content_batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 142 - ".__call__"
Cohesion: 0.50
Nodes (3): Any, CallbackQuery, Message

### Community 143 - "request_account_deletion"
Cohesion: 0.50
Nodes (4): _confirm_keyboard(), InlineKeyboardMarkup, message, request_account_deletion()

### Community 144 - "set_audio_callback"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 146 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.50
Nodes (4): Tooltip Jinja2 Macro Component, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 147 - "test_devotional_category_navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 148 - "test_rotating_portion_stays_personal_when_member_is_inactive"
Cohesion: 0.50
Nodes (3): asyncio, integration, test_rotating_portion_stays_personal_when_member_is_inactive()

### Community 150 - "test_channel_coverage_counts_pages_not_source_posts"
Cohesion: 0.67
Nodes (4): asyncio, integration, test_channel_coverage_counts_pages_not_source_posts(), test_channel_range_registry_is_idempotent_and_resolves_shared_audio()

### Community 151 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 152 - "Identity Across Platforms (phone-based merge key)"
Cohesion: 0.67
Nodes (3): Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 184 - "Assignment"
Cohesion: 0.67
Nodes (3): Assignment, Base, The Phase-4 flat per-khatm assignment (legacy shape, kept for parity). The…

### Community 186 - "test_admin_can_search_khatms_by_title_creator_and_uuid"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_admin_can_search_khatms_by_title_creator_and_uuid()

### Community 187 - "test_ad_reward_requires_opt_in_and_is_idempotent"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_ad_reward_requires_opt_in_and_is_idempotent()

### Community 188 - "test_devotional_slug_link_does_not_depend_on_title_wording"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

### Community 189 - "test_coupon_discount_invoice_and_limits_are_atomic"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_coupon_discount_invoice_and_limits_are_atomic()

### Community 190 - "test_devotional_text_and_platform_specific_audio"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 191 - "test_active_categories_are_filtered_by_the_selected_parent_family"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_active_categories_are_filtered_by_the_selected_parent_family()

### Community 192 - "test_paid_khatm_invoice_is_bound_and_refunded_once"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_paid_khatm_invoice_is_bound_and_refunded_once()

### Community 193 - "test_public_join_page_previews_without_joining_and_rejects_cancelled_link"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_public_join_page_previews_without_joining_and_rejects_cancelled_link()

### Community 194 - "test_quran_page_assets_require_canonical_complete_ranges"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_quran_page_assets_require_canonical_complete_ranges()

### Community 195 - "test_committed_quran_readers_advance_personally_and_wrap"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_committed_quran_readers_advance_personally_and_wrap()

## Knowledge Gaps
- **102 isolated node(s):** `claude_watchdog.sh script`, `R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**`, `R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**`, `R13. کمترین سؤال ممکن — اصل کلی هر دو بخش.`, `R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1300 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **88 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `app.py`, `create_khatm.py`, `confirm_account_deletion`, `phone/service.py`, `keyboards.py`, `identity/service.py`, `my_khatms.py`, `start.py`, `request_account_deletion`, `get_or_create`, `portions.py`, `User`, `resolve_or_provision_user`, `test_create_khatm_survives_phone_verification.py`, `panel.py`, `home_keyboard_for_bot`, `creator_request/service.py`, `Platform`, `member_commitment.py`, `registration.py`, `types`, `profile.py`, `approve_join`, `env.py`, `DevotionalAsset`, `suggestions.py`, `wallet.py`, `enter_phone`, `test_creator_contact.py`, `account_link.py`, `test_admin_template_render.py`, `_commitment_total_keyboard`, `build_join_success_message`, `test_creator_finance_and_support_buttons_are_wired`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `Architecture Document` connect `Architecture Document` to `DECISIONS`, `KhatmSaz Project (Claude Code Instructions)`, `identity/service.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session_scope` to `create_khatm.py`, `sqlalchemy`, `KhatmPortion`, `confirm_account_deletion`, `keyboards.py`, `new_id`, `reminder_engine/service.py`, `identity/service.py`, `my_khatms.py`, `register_devotional_content_batch2.py`, `.__call__`, `start.py`, `get_or_create`, `UserRole`, `User`, `test_channel_coverage_counts_pages_not_source_posts`, `resolve_or_provision_user`, `creator_request/service.py`, `bootstrap.py`, `Platform`, `registration.py`, `plan/service.py`, `wallet/repository.py`, `approve_join`, `DevotionalAsset`, `test_ad_reward_requires_opt_in_and_is_idempotent`, `test_devotional_slug_link_does_not_depend_on_title_wording`, `test_new_bale_identity_moves_to_existing_profile_after_otp`, `test_coupon_discount_invoice_and_limits_are_atomic`, `test_devotional_text_and_platform_specific_audio`, `test_active_categories_are_filtered_by_the_selected_parent_family`, `test_paid_khatm_invoice_is_bound_and_refunded_once`, `advertising/service.py`, `test_quran_page_assets_require_canonical_complete_ranges`, `manage_content.py`, `reporting/service.py`, `message_template/__init__.py`, `test_picking_a_reciter_via_settings_menu_turns_on_audio`, `_moderate`, `register_devotional_content.py`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `t()` (e.g. with `test_creator_detail_renders_manage_stats_members_export_and_settings()` and `test_help_is_complete_and_button_driven()`) actually correct?**
  _`t()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 141 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 141 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**`, `R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05053968253968254 - nodes in this community are weakly interconnected._