# Graph Report - Khatm  (2026-09-29)

## Corpus Check
- 448 files · ~314,997 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3775 nodes · 13557 edges · 257 communities (156 shown, 101 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 1991 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `89aafadd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- FSMContext
- sqlalchemy
- KhatmPortion
- phone/service.py
- create_khatm.py
- new_id
- admin.py
- system_settings/service.py
- keyboards.py
- session_scope
- wallet/models.py
- Participation
- start.py
- settings_menu.py
- authorization/service.py
- typing
- sqlalchemy_dialects
- khatm_workflow/service.py
- Platform
- Khatm
- portions.py
- User
- alembic
- test_deep_link_clears_old_state_before_storing_new_join_context
- CHANGELOG
- start_suggestion
- provider.py
- PayPingGateway
- wallet/service.py
- test_confirm_wizard_resumes_and_finishes_creation_after_otp
- UserRole
- home_keyboard_for_bot
- creator_request/service.py
- get_settings
- khatmsaz_bot_handlers_join_flow
- KhatmRequest
- member_commitment.py
- _phone_keyboard
- bot_registry/service.py
- KhatmCategoryGroup
- PlanTier
- wallet/repository.py
- notification/repository.py
- sms_subscription/service.py
- test_member_cancel_clears_state
- deliver_pending
- datetime
- KhatmInvitation
- Session
- reminder_engine/service.py
- test_notify_routing.py
- DevotionalAsset
- safe_answer_callback
- _create_topup_payment
- QuranAssetKind
- test_payment_intent_is_owned_single_use_and_amount_bound
- record
- participation/service.py
- finish_invite_links
- KhatmBroadcast
- phone/repository.py
- _wiz
- test_i18n_audit.py
- Architecture Document
- بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`
- test_deliver_due_next_portions_pushes_real_content_not_just_text
- Admin Panel Base Layout (base.html)
- receive_media
- DECISIONS
- commitment.py
- DOMAIN_MODEL
- content/service.py
- OpenContribution
- test_bale_invite_is_a_real_clickable_link_not_a_typed_command
- 435027907255_add_daily_deadline_hour_to_khatms.py
- test_quran_setup_waits_for_selected_hour_before_sending
- KhatmSaz Project (Claude Code Instructions)
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی
- WaitingList
- message_template/repository.py
- FakeMessage
- test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it
- UserSettings
- test_creator_contact.py
- QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)
- KhatmSaz VPS Deployment Guide
- Multi-Bot (26-bot) Architecture
- test_member_commitment_flow.py
- install_command_menu
- WalletInvoice
- BotCategory
- test_dispatcher_routes_commands_while_profile_phone_state_is_active
- test_recitation_text_only_for_laan.py
- creator_broadcast/service.py
- ensure_creator_phone_verified
- test_admin_template_render.py
- test_fixed_salawat_content.py
- CSS Layouts and Responsive Design Guide
- _commitment_total_keyboard
- positional_range_for_step
- test_health.py
- manual_phone_verification/repository.py
- test_broadcast_shows_khatm_picker
- test_message_template.py
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per bot)
- runtime_status.py
- qr.py
- delete_account
- sqlalchemy_ext_asyncio
- test_quran_channel_source.py
- test_mini_app_entry.py
- test_notification_snooze.py
- Python Requirements
- Feature checklist
- list_identities_for_user
- test_creator_finance_and_support_buttons_are_wired
- test_set_font_size_validates_and_persists
- help_topic
- devotional_seed.py
- test_current_quran_delivery_is_exact_and_reciter_specific
- config.py
- asyncio
- str
- test_next_portion_is_withheld_until_next_local_day_at_reminder_hour
- InvoiceKind
- test_contribute_blocked_until_delivery_hour_set
- zzz_merge_three_heads_2026_09_28.py
- t
- test_tapping_a_time_of_day_button_saves_the_hour_without_typing
- test_active_otp_is_reused_without_returning_another_sms_code
- Mini-App Only Authentication Pattern
- test_public_khatms_reply_button_is_wired
- Settings Menu Full-Button Test Scenario
- _default_khatm_title
- khatmsaz_modules_phone
- test_salawat_category_group_always_goes_directly_to_mode
- test_daily_digest_combines_multiple_khatms_for_one_user
- AdminFilter
- test_quran_join_is_member_controlled_without_auto_allocation
- set_audio_callback
- ModerationMiddleware
- Tooltip Jinja2 Macro Component
- FakeState
- Multi-Bot Architecture (26 bots)
- test_registration_starts_in_the_users_saved_language
- PROJECT_STATE
- Bot Help Strings (Persian)
- Identity Across Platforms (phone-based merge key)
- Base
- register_devotional_content.py
- monthly_report/service.py
- FakeState
- bot/__init__.py
- test_reminder_tone_resolves_seeded_locale_template
- deliver_due
- system_settings/__init__.py
- test_payment_safety.py
- env.py
- 1f9fe3de23a1_add_khatm_requests_table.py
- b7c8d9e0f1a2_add_bot_instances.py
- c21644dab334_add_skip_today_pause_and_leave_reason_.py
- register_devotional_content_batch2.py
- test_private_join_approval_rejects_non_creator_before_join
- _compose_niyyat
- test_member_bot_fixes.py
- start_bot.ps1
- khatmsaz_bot
- khatmsaz_bot_handlers
- khatmsaz_bot_handlers_create_khatm
- khatmsaz_bot_handlers_help
- khatmsaz_core_bot_registry
- khatmsaz_core_db
- khatmsaz_core_ids
- claude_watchdog.sh
- khatmsaz_core_security
- web/__init__.py
- Persian-first, Simple UX Principle
- khatmsaz_i18n
- Debugging Guide
- Working-tree Git Diff (creator_request wiring)
- PayPing v3 Payment Integration
- Quran Content Storage (Telegram channel-based)
- Redis (reserved for FSM / scheduler)
- 26-Bot Grid (1 creator + 12 member per platform)
- Creator Registration Flow (with OTP)
- Khatm Category Independent Families Test Scenario
- QA Handoff: Telegram Testing Guide for Codex
- khatmsaz_modules_allocation
- khatmsaz_modules_bot_registry_models
- khatmsaz_bot_handlers_start
- khatmsaz_core
- khatmsaz_modules_wallet
- khatmsaz_modules_wallet_gateway
- Module: audit_log
- Module: phone
- Module: plan
- Module: settings
- khatmsaz_modules_identity
- khatmsaz_modules_identity_models
- khatmsaz_modules_invitation
- khatmsaz_modules_invitation_models
- khatmsaz_modules_khatm
- khatmsaz_modules_khatm_models
- run_once
- khatmsaz_modules_khatm_workflow
- khatmsaz_modules_notification
- khatmsaz_modules_notification_models
- khatmsaz_modules_participation
- khatmsaz_modules_phone_models
- Admins Management Page
- Audit Log Page
- Broadcasts Admin Page
- Operations/Health Admin Page
- Phone Verifications Admin Page
- Message Templates Admin Page
- khatmsaz_modules_reminder_engine
- khatmsaz_modules_session
- khatmsaz_modules_session_models
- khatmsaz_modules_settings
- khatmsaz_modules_settings_models
- str
- test_devotional_slug_link_does_not_depend_on_title_wording

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 388 edges
2. `t()` - 360 edges
3. `Platform` - 291 edges
4. `Khatm` - 156 edges
5. `User` - 143 edges
6. `new_id()` - 140 edges
7. `KhatmTemplateType` - 117 edges
8. `safe_answer_callback()` - 112 edges
9. `resolve_or_provision_user()` - 98 edges
10. `KhatmStatus` - 94 edges

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

## Communities (257 total, 101 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.08
Nodes (70): fastapi, fastapi_staticfiles, fastapi_templating, get, HTMLResponse, middleware, Request, search_users() (+62 more)

### Community 1 - "FSMContext"
Cohesion: 0.17
Nodes (38): R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome(), _apply_coupon_code(), apply_creation_coupon() (+30 more)

### Community 2 - "sqlalchemy"
Cohesion: 0.06
Nodes (50): httpx, khatmsaz_modules_khatm_category, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl, pytest, re, sqlalchemy (+42 more)

### Community 3 - "KhatmPortion"
Cohesion: 0.08
Nodes (77): AllocationStrategy, CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).… (+69 more)

### Community 4 - "phone/service.py"
Cohesion: 0.23
Nodes (23): AccountMerge, OtpPurpose, _assert_pristine_source_account(), complete_account_link(), complete_phone_change(), _consume_challenge(), _hash_code(), normalize_e164() (+15 more)

### Community 5 - "create_khatm.py"
Cohesion: 0.12
Nodes (29): InlineKeyboardButton, Khatm creation wizard — a short multi-step conversation. Flow: **commitment…, advertising_choice_keyboard(), capacity_choice_keyboard(), category_choice_keyboard(), _ck_cancel_row(), commitment_mode_keyboard(), commitment_weekday_keyboard() (+21 more)

### Community 6 - "new_id"
Cohesion: 0.03
Nodes (100): build_join_preview_message(), build_join_success_message(), _clean_niyyat(), Shared with `join_requests.py`'s approval handler, which sends this same…, Strip a leading «به نیت»/«بنية»/«Intention» so the display label…, Owner complaint (2026-09-20): the old preview only showed title/…, new_id(), UUID (+92 more)

### Community 7 - "admin.py"
Cohesion: 0.09
Nodes (71): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+63 more)

### Community 8 - "system_settings/service.py"
Cohesion: 0.23
Nodes (14): _inactivity_days(), Generic admin-editable key/value store for small system-wide numeric defaults…, SystemSetting, get(), list_all(), AsyncSession, set(), get_int() (+6 more)

### Community 9 - "keyboards.py"
Cohesion: 0.06
Nodes (73): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types, apscheduler_schedulers_asyncio, base64, logging (+65 more)

### Community 10 - "session_scope"
Cohesion: 0.07
Nodes (87): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at() (+79 more)

### Community 11 - "wallet/models.py"
Cohesion: 0.15
Nodes (22): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+14 more)

### Community 12 - "Participation"
Cohesion: 0.14
Nodes (32): _member_creators(), Creators of the member's ACTIVE khatms, each with the member's own…, Participation, ParticipationStatus, count_committed_active(), count_for_khatm(), create(), get_active() (+24 more)

### Community 13 - "start.py"
Cohesion: 0.06
Nodes (58): عضو (Member bots) — تلگرام fa/ar/en و بله, html, Kick off the mode picker for a freshly-joined commitment member., start_commitment_mode_picker(), choose_gender(), choose_province(), callback_query, CallbackQuery (+50 more)

### Community 14 - "settings_menu.py"
Cohesion: 0.11
Nodes (49): begin_phone_change(), buy_sms_plan(), _can_open_creator_panel(), _current_platform_user(), _lang_for(), callback_query, CallbackQuery, FSMContext (+41 more)

### Community 15 - "authorization/service.py"
Cohesion: 0.14
Nodes (26): admin_approve_request(), admin_reject_request(), CommandObject, _resolve_decision(), AdminRole, AdminRoleGrant, CapabilityType, str (+18 more)

### Community 16 - "typing"
Cohesion: 0.05
Nodes (4): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 18 - "khatm_workflow/service.py"
Cohesion: 0.08
Nodes (42): _finish_creating_khatm(), Owner-reported bug (2026-09-21/22): a creator whose phone wasn't verified yet…, ContentDeliveryMode, CoverStatus, CreatorDisplayMode, KhatmScheduleKind, KhatmVisibility, str (+34 more)

### Community 19 - "Platform"
Cohesion: 0.04
Nodes (113): begin_account_link(), _lang_for(), FSMContext, message, receive_link_code(), receive_link_phone(), _lang_for(), CommandObject (+105 more)

### Community 20 - "Khatm"
Cohesion: 0.12
Nodes (56): creator_save_cosmetic_edit(), Khatm, KhatmStatus, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+48 more)

### Community 21 - "portions.py"
Cohesion: 0.07
Nodes (65): _parse_delivery_time(), Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., callback_query, CallbackQuery, FSMContext, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow…, show_member_portion() (+57 more)

### Community 22 - "User"
Cohesion: 0.10
Nodes (36): PlatformIdentity, User, UserStatus, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity() (+28 more)

### Community 24 - "test_deep_link_clears_old_state_before_storing_new_join_context"
Cohesion: 0.08
Nodes (15): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home() (+7 more)

### Community 25 - "CHANGELOG"
Cohesion: 0.15
Nodes (14): CHANGELOG Archive (until 2026-09-18), CHANGELOG, Creator wallet-charge button, Devotional content library + seed, i18n coverage guard (fa/ar/en), positional_range_for_step (rotating allocation helper), Reminder engine (APScheduler scan), DEC-PY-0072 — Devotional families are independent top-level choices (+6 more)

### Community 26 - "start_suggestion"
Cohesion: 0.18
Nodes (19): handle_creator_request_button(), callback_query, CallbackQuery, back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext (+11 more)

### Community 27 - "provider.py"
Cohesion: 0.06
Nodes (45): BaseSettings, dataclasses, hmac, json, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider (+37 more)

### Community 28 - "PayPingGateway"
Cohesion: 0.11
Nodes (20): Response, GatewayError, PaymentRequest, PaymentVerification, Exception, Gateway boundary; PSP-specific code must live behind this protocol., The PSP rejected or could not complete a request., PayPingGateway (+12 more)

### Community 29 - "wallet/service.py"
Cohesion: 0.11
Nodes (27): PaymentGateway, Protocol, DiscountCoupon, get_coupon(), get_pending_payment_by_id(), list_coupons(), set_coupon_enabled(), upsert_coupon() (+19 more)

### Community 30 - "test_confirm_wizard_resumes_and_finishes_creation_after_otp"
Cohesion: 0.13
Nodes (10): ChangePhone, StatesGroup, BotRegistry, Bot, UUID, set_registry(), FakeCallback, FakeMessage (+2 more)

### Community 31 - "UserRole"
Cohesion: 0.12
Nodes (39): سازنده (Creator) — تلگرام, help_command(), Message, _resolve_user_info(), admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel() (+31 more)

### Community 32 - "home_keyboard_for_bot"
Cohesion: 0.13
Nodes (21): accept_commitment(), cancel_commitment(), callback_query, CallbackQuery, FSMContext, message, receive_delivery_hour(), receive_delivery_hour_button() (+13 more)

### Community 33 - "creator_request/service.py"
Cohesion: 0.12
Nodes (32): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, Data model for creator-role requests. A user submits a request to become a…, approve(), create(), get_by_id() (+24 more)

### Community 34 - "get_settings"
Cohesion: 0.33
Nodes (10): _build_member_bots(), _configure_logging(), main(), Bot, _tag_bot(), build_bale_bot(), Bot, build_telegram_bot() (+2 more)

### Community 36 - "KhatmRequest"
Cohesion: 0.21
Nodes (19): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+11 more)

### Community 37 - "member_commitment.py"
Cohesion: 0.19
Nodes (30): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), CommitFlow, enter_count(), enter_custom_time() (+22 more)

### Community 38 - "_phone_keyboard"
Cohesion: 0.10
Nodes (26): enter_city(), enter_name(), enter_phone(), FSMContext, Message, receive_shared_contact(), enter_city(), enter_name() (+18 more)

### Community 39 - "bot_registry/service.py"
Cohesion: 0.17
Nodes (29): cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot(), list_active(), list_active_members() (+21 more)

### Community 40 - "KhatmCategoryGroup"
Cohesion: 0.17
Nodes (35): resolve_bot_category(), KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str, Admin-managed content library for independent devotional families. Owner…, A participant's typed request for a دعا that isn't in the library yet (owner… (+27 more)

### Community 41 - "PlanTier"
Cohesion: 0.09
Nodes (45): PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition() (+37 more)

### Community 42 - "wallet/repository.py"
Cohesion: 0.14
Nodes (27): CouponRedemption, PendingPayment, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, Wallet, add_balance(), add_credit(), claim_pending_payment(), count_coupon_redemptions() (+19 more)

### Community 43 - "notification/repository.py"
Cohesion: 0.39
Nodes (11): NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession, datetime (+3 more)

### Community 44 - "sms_subscription/service.py"
Cohesion: 0.14
Nodes (29): Time-limited SMS reminder subscriptions (owner request, 2026-09-20). SMS…, Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options() (+21 more)

### Community 45 - "test_member_cancel_clears_state"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 46 - "deliver_pending"
Cohesion: 0.33
Nodes (6): deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Claim each eligible announcement once, then notify creator + active members.

### Community 47 - "datetime"
Cohesion: 0.05
Nodes (41): aiogram_enums, aiogram_fsm_storage_memory, contextlib, datetime, enum, khatmsaz_modules_khatm_category_models, sqlalchemy_dialects_postgresql, sqlalchemy_orm (+33 more)

### Community 48 - "KhatmInvitation"
Cohesion: 0.52
Nodes (6): KhatmInvitation, create(), get_by_token_hash(), mark_accepted(), AsyncSession, Persistence access for invitation — the only place that runs SQL for this…

### Community 49 - "Session"
Cohesion: 0.14
Nodes (28): hashlib, secrets, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, create_invitation(), mark_accepted(), AsyncSession (+20 more)

### Community 50 - "reminder_engine/service.py"
Cohesion: 0.18
Nodes (21): collections, Positive khatm-completion announcements., Scheduled positive personal monthly reports., NotificationKind, already_sent_today(), AsyncSession, datetime, Notification business logic: dedup a reminder/miss send against "already sent… (+13 more)

### Community 51 - "test_notify_routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 52 - "DevotionalAsset"
Cohesion: 0.11
Nodes (23): deliver_devotional_media(), callback_query, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional_reciter_choice(), DevotionalAsset (+15 more)

### Community 53 - "safe_answer_callback"
Cohesion: 0.16
Nodes (38): ask_creation_coupon(), _ask_mode(), cancel_wizard(), choose_allowed_platforms(), choose_category(), choose_category_group(), choose_commitment_total(), choose_content_delivery_mode() (+30 more)

### Community 54 - "_create_topup_payment"
Cohesion: 0.19
Nodes (13): ask_custom_topup(), _create_topup_payment(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery, FSMContext, Message (+5 more)

### Community 55 - "QuranAssetKind"
Cohesion: 0.13
Nodes (22): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), parse_quran_channel_caption(), quran_channel_coverage(), Idempotently map one source-channel post to every page it covers. (+14 more)

### Community 56 - "test_payment_intent_is_owned_single_use_and_amount_bound"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_payment_intent_is_owned_single_use_and_amount_bound()

### Community 57 - "record"
Cohesion: 0.23
Nodes (36): post, RedirectResponse, get_notify_fn(), record(), find_by_id(), _admin(), change_admin_role(), _chunk_devotional() (+28 more)

### Community 58 - "participation/service.py"
Cohesion: 0.09
Nodes (30): sqlalchemy_exc, advance_open_reading(), log_commitment_count(), Reserve the next `pages` pages for this open reader, advancing the cursor, and…, COUNT mode: pledge to read `target` repetitions, resetting progress., Add `amount` to a COUNT-mode member's logged total. Returns (new_done, target,…, REGULAR mode: recurring schedule delivered by the reminder engine. Reused…, set_commitment_count() (+22 more)

### Community 59 - "finish_invite_links"
Cohesion: 0.13
Nodes (22): _run_reminder_scan(), finish_invite_links(), handle_confirm_invite_langs(), handle_invite_platform(), handle_toggle_lang(), show_invite_languages_keyboard(), show_invite_platform_keyboard(), build_member_invite_links() (+14 more)

### Community 60 - "KhatmBroadcast"
Cohesion: 0.19
Nodes (26): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, submit_khatm_message() (+18 more)

### Community 61 - "phone/repository.py"
Cohesion: 0.14
Nodes (33): approve(), OtpChallenge, PhoneClaim, PhoneClaimStatus, str, create_challenge(), create_or_verify_claim(), get_challenge() (+25 more)

### Community 62 - "_wiz"
Cohesion: 0.19
Nodes (13): R1 (owner 2026-09-28): keep the wizard from cluttering the chat. Each new…, _wiz(), FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling… (+5 more)

### Community 63 - "test_i18n_audit.py"
Cohesion: 0.11
Nodes (12): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source() (+4 more)

### Community 64 - "Architecture Document"
Cohesion: 0.14
Nodes (18): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, No Business Rule Invention Rule, PayPing v3 Payment Gateway, Architecture Document, PayPing Setup Guide (Persian) (+10 more)

### Community 65 - "بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`"
Cohesion: 0.08
Nodes (20): R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**, R13. کمترین سؤال ممکن — اصل کلی هر دو بخش., R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک** (+12 more)

### Community 66 - "test_deliver_due_next_portions_pushes_real_content_not_just_text"
Cohesion: 0.15
Nodes (8): _iana_offset_for_local_hour(), asyncio, integration, test_deliver_due_next_portions_pushes_real_content_not_just_text(), _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 67 - "Admin Panel Base Layout (base.html)"
Cohesion: 0.18
Nodes (18): Admin Panel Base Layout (base.html), components.html macros (tooltip), Glassmorphism Dark Design System, Permission-gated Admin Navigation, Admin Categories Page (categories.html), Creator Panel Base Layout (creator_base.html), Creator Panel i18n (t/lang) Localization, Creator Dashboard (creator_dashboard.html) (+10 more)

### Community 68 - "receive_media"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 69 - "DECISIONS"
Cohesion: 0.31
Nodes (10): DECISIONS, DEC-PY-0076 — Separate participant and creator menus, DEC-PY-0077 — Daily portions stack up, DEC-PY-0091 — Creation wizard no longer asks content format, DEC-PY-0092 — Rotating Quran allocation, DEC-PY-0093 — Creator bot has one fixed menu, starts creation directly, DEC-PY-0094 — Quran reading pace chosen by each member, DEC-PY-0095 — First Quran pages wait for chosen hour; automatic titles; OTP dedup (+2 more)

### Community 70 - "commitment.py"
Cohesion: 0.15
Nodes (21): CommitmentMode, is_regular_due(), log_count(), _minutes(), parse_hhmm(), datetime, str, R11 (owner 2026-09-28, revised after live QA): member-side commitment logic.… (+13 more)

### Community 71 - "DOMAIN_MODEL"
Cohesion: 0.15
Nodes (17): PayPing payment gateway, PendingPayment compare-and-swap replay protection, R11/N2 member commitment flow (regular/count), Codex Handoff — Next Steps, PayPing gateway activation (needs owner API token), DEC-PY-0068 — Kavenegar is first production SMS adapter, DEC-PY-0074 — Free-tier plan caps per-creator, admin-editable, DEC-PY-0090 — Fixed niyyat + optional niyabat (+9 more)

### Community 72 - "content/service.py"
Cohesion: 0.10
Nodes (30): add_devotional_audio_variant(), add_devotional_image_page(), decode_telegram_forward_ref(), get_allowed_reciters(), get_effective_reciter(), _get_enabled_devotional_asset(), get_quran_total_pages(), list_all_devotional_assets() (+22 more)

### Community 73 - "OpenContribution"
Cohesion: 0.08
Nodes (33): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+25 more)

### Community 74 - "test_bale_invite_is_a_real_clickable_link_not_a_typed_command"
Cohesion: 0.18
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 76 - "test_quran_setup_waits_for_selected_hour_before_sending"
Cohesion: 0.13
Nodes (4): FakeMessage, FakeState, asyncio, test_quran_setup_waits_for_selected_hour_before_sending()

### Community 77 - "KhatmSaz Project (Claude Code Instructions)"
Cohesion: 0.20
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), Admin Mini App (Telegram WebApp), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), Admin Mini App Guide (Persian), AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 78 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی"
Cohesion: 0.14
Nodes (14): Live QA — 2026-09-28 (Chrome / Telegram Web / Codex), QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), رفع‌شدهٔ همین عصر (Claude Code), ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live) (+6 more)

### Community 79 - "WaitingList"
Cohesion: 0.27
Nodes (10): WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next(), AsyncSession (+2 more)

### Community 80 - "message_template/repository.py"
Cohesion: 0.15
Nodes (18): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+10 more)

### Community 82 - "test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it"
Cohesion: 0.18
Nodes (7): FakeMessage, FakeState, asyncio, integration, R11 supersedes the old bare delivery-hour question for repetitions., test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it(), test_fresh_committed_salawat_join_asks_commitment_mode()

### Community 83 - "UserSettings"
Cohesion: 0.13
Nodes (21): _decision_keyboard(), list_manual_phone_requests(), InlineKeyboardMarkup, message, UserSettings, create_for_user(), find_by_contact_phones(), get_by_user() (+13 more)

### Community 84 - "test_creator_contact.py"
Cohesion: 0.22
Nodes (12): _compose_welcome_with_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/…, test_compose_appends_contact_line_to_welcome(), test_compose_contact_only_when_no_welcome(), test_compose_none_contact_passes_welcome_through() (+4 more)

### Community 85 - "QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)"
Cohesion: 0.17
Nodes (12): A. زیرساخت چندبات (۲۶ بات), B. ثبت‌نام, D. دعوت و عضویت, E. سهم و یادآوری, F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات, G. زبان‌ها (fa/ar/en), H. پرداخت, I. Mini App + پنل ادمین (+4 more)

### Community 86 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.12
Nodes (20): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution, Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter (+12 more)

### Community 87 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.12
Nodes (18): Admin Token Panel /bots Route (2-step confirmation), Restart Requirement After Token Change, bot_instances Database Table, BotRegistry Singleton Class, Fernet Token Encryption for Bot Tokens, Handler Bot Role Check Pattern (bot.khatmsaz_role), Router Classification (creator-only, member-only, shared), Multi-Bot Invite Link Generation Flow (+10 more)

### Community 88 - "test_member_commitment_flow.py"
Cohesion: 0.27
Nodes (8): importlib_util, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_has_presets_and_custom(), test_hour_keyboard_prefix_matches_handler(), test_mode_keyboard_callbacks()

### Community 89 - "install_command_menu"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 90 - "WalletInvoice"
Cohesion: 0.15
Nodes (20): Immutable purchase amounts plus a small paid/refunded lifecycle., WalletInvoice, bind_invoice_resource(), create_paid_invoice(), list_invoices_for_user(), add_cash(), bind_invoice_resource(), get_balances() (+12 more)

### Community 91 - "BotCategory"
Cohesion: 0.18
Nodes (16): _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, khatm_matches_bot(), Keep Quran/Salawat/Dua-Ziyarat/La'an families in their own member bot., BotCategory, str, R2 (owner 2026-09-28): per-bot intro image shown after the creator picks…, test_dua_group_maps_to_dua_ziyarat_bot() (+8 more)

### Community 92 - "test_dispatcher_routes_commands_while_profile_phone_state_is_active"
Cohesion: 0.18
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 93 - "test_recitation_text_only_for_laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 94 - "creator_broadcast/service.py"
Cohesion: 0.21
Nodes (19): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+11 more)

### Community 95 - "ensure_creator_phone_verified"
Cohesion: 0.23
Nodes (15): ensure_creator_phone_verified(), FSMContext, Message, Return true when creation may continue; otherwise start the OTP step., receive_change_code(), receive_new_phone(), verify_creator_phone(), notify_admins_of_manual_request() (+7 more)

### Community 96 - "test_admin_template_render.py"
Cohesion: 0.26
Nodes (13): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_both_panel_headers_support_configured_logo_and_fallback(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings() (+5 more)

### Community 97 - "test_fixed_salawat_content.py"
Cohesion: 0.24
Nodes (5): FakeMessage, _plain_salawat(), asyncio, test_plain_salawat_sends_exact_owner_text_without_category(), test_plain_salawat_uses_panel_image_with_fixed_text_caption()

### Community 98 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 99 - "_commitment_total_keyboard"
Cohesion: 0.25
Nodes (8): _commitment_total_keyboard(), _creator_contact_keyboard(), InlineKeyboardMarkup, R4 (owner 2026-09-28): the creator MUST provide a contact so members can reach…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 100 - "positional_range_for_step"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 101 - "test_health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 102 - "manual_phone_verification/repository.py"
Cohesion: 0.30
Nodes (11): ManualPhoneVerification, create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession, Persistence helpers for foreign-number manual verification. (+3 more)

### Community 103 - "test_broadcast_shows_khatm_picker"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 104 - "test_message_template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 106 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.20
Nodes (12): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, resolve_bot_category() Function, Token Resolution on Member Bot (category validation) (+4 more)

### Community 107 - "Member Bot Language Isolation (fixed per bot)"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 108 - "runtime_status.py"
Cohesion: 0.22
Nodes (7): mark_scan_failed(), mark_scheduler_started(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins., snapshot()

### Community 109 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 110 - "delete_account"
Cohesion: 0.33
Nodes (5): AccountDeletionBlocked, delete_account(), Exception, Safely deactivate a user while retaining non-PII history. Active committed…, The account still owns an obligation that must be resolved first.

### Community 111 - "sqlalchemy_ext_asyncio"
Cohesion: 0.15
Nodes (17): sqlalchemy_ext_asyncio, Append-only audit trail for sensitive administrative actions., AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module., Return a bounded newest-first timeline without exposing mutation APIs., record() (+9 more)

### Community 112 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 113 - "test_mini_app_entry.py"
Cohesion: 0.43
Nodes (6): _message(), asyncio, Fail-closed behavior before a public HTTPS Mini App origin exists., test_admin_mini_app_rejects_local_http_origin(), test_creator_mini_app_rejects_local_http_origin_before_database_access(), unittest_mock

### Community 114 - "test_notification_snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 115 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 116 - "Feature checklist"
Cohesion: 0.25
Nodes (7): 1. Graphical creator Mini App khatm creation — DONE, 2. Real FREE → PRO purchase — DONE, 3. Configurable panel logo — IN-PROGRESS, 4. Reliable modern Persian panel font — TODO, Codex big features progress — 2026-09-29, Cross-feature validation and delivery log, Feature checklist

### Community 117 - "list_identities_for_user"
Cohesion: 0.30
Nodes (15): approve_leave(), ask_leave_reason(), _do_leave(), _lang_for(), _lang_for_user(), leave_reason_chosen(), callback_query, CallbackQuery (+7 more)

### Community 118 - "test_creator_finance_and_support_buttons_are_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 121 - "test_set_font_size_validates_and_persists"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 122 - "help_topic"
Cohesion: 0.20
Nodes (13): help_open_my_khatms(), help_start_creation(), help_topic(), callback_query, CallbackQuery, FSMContext, help_create_actions_keyboard(), help_manage_actions_keyboard() (+5 more)

### Community 123 - "devotional_seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 124 - "test_current_quran_delivery_is_exact_and_reciter_specific"
Cohesion: 0.33
Nodes (6): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., set_allowed_reciters(), asyncio, integration, test_current_quran_delivery_is_exact_and_reciter_specific()

### Community 125 - "config.py"
Cohesion: 0.22
Nodes (8): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, functools, pydantic_settings, Bale Bot instance factory. Bale's bot platform speaks a Telegram-compatible Bot…, Telegram Bot instance factory., Central application settings, loaded once from environment / .env. Every other…

### Community 126 - "asyncio"
Cohesion: 0.20
Nodes (7): asyncio, fixture, os, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 127 - "str"
Cohesion: 0.67
Nodes (3): AssignmentStatus, AssignmentUnitKind, str

### Community 128 - "test_next_portion_is_withheld_until_next_local_day_at_reminder_hour"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 129 - "InvoiceKind"
Cohesion: 0.24
Nodes (11): cancel_khatm(), Cancel an unused khatm and refund its recorded creation price internally., InvoiceKind, get_paid_invoice_by_resource(), Refund to the wallet's real-money balance — never to a bank account…, Refund a paid purchase once; return None when no invoice exists., refund_cash(), refund_purchase_invoice() (+3 more)

### Community 130 - "test_contribute_blocked_until_delivery_hour_set"
Cohesion: 0.29
Nodes (4): _callback_update(), asyncio, Update, test_contribute_blocked_until_delivery_hour_set()

### Community 131 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 132 - "t"
Cohesion: 0.09
Nodes (40): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+32 more)

### Community 133 - "test_tapping_a_time_of_day_button_saves_the_hour_without_typing"
Cohesion: 0.29
Nodes (4): FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 135 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 136 - "test_public_khatms_reply_button_is_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 137 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 138 - "_default_khatm_title"
Cohesion: 0.50
Nodes (4): _default_khatm_title(), Build the standard title without asking the creator an extra question., test_devotional_title_uses_selected_category(), test_quran_title_is_automatic()

### Community 140 - "test_salawat_category_group_always_goes_directly_to_mode"
Cohesion: 0.20
Nodes (3): _async_value(), asyncio, test_salawat_category_group_always_goes_directly_to_mode()

### Community 142 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

### Community 143 - "test_quran_join_is_member_controlled_without_auto_allocation"
Cohesion: 0.27
Nodes (6): asyncio, test_join_via_token_threads_bot_instance_id(), fake_get_khatm(), fake_join(), fake_resolve(), test_quran_join_is_member_controlled_without_auto_allocation()

### Community 144 - "set_audio_callback"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 145 - "ModerationMiddleware"
Cohesion: 0.38
Nodes (6): BaseMiddleware, _extract_chat_id(), ModerationMiddleware, Any, _reply_blocked(), TelegramObject

### Community 146 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.50
Nodes (4): Tooltip Jinja2 Macro Component, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 148 - "Multi-Bot Architecture (26 bots)"
Cohesion: 0.25
Nodes (8): Multi-Bot Architecture (26 bots), Multi-bot invite links (bot/invite_links.py), bot_instances table (encrypted tokens), DEC-PY-0080 — Multi-bot split (1 creator + 12 member bots per platform), Creator Bot (Multi-bot doc), dp_creator Dispatcher, dp_member Dispatcher, Task Report: Member Bot Category Attribute Fix

### Community 149 - "test_registration_starts_in_the_users_saved_language"
Cohesion: 0.22
Nodes (7): ProfileEdit, StatesGroup, FakeMessage, asyncio, integration, parametrize, test_registration_starts_in_the_users_saved_language()

### Community 150 - "PROJECT_STATE"
Cohesion: 0.29
Nodes (8): PROJECT_STATE Archive (until 2026-09-18), DATABASE, Alembic migration workflow (reviewed, never blind autogenerate), Hand-written partial unique indexes, UUIDv7 app-generated primary keys, INDEX — Topical Documentation Map, PROJECT_STATE, Fresh-Postgres migration chain repair

### Community 151 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 152 - "Identity Across Platforms (phone-based merge key)"
Cohesion: 0.67
Nodes (3): Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 154 - "Base"
Cohesion: 0.29
Nodes (7): DeclarativeBase, Base, Shared declarative base for every module's models., UserCapability, NotificationJob, Assignment, The Phase-4 flat per-khatm assignment (legacy shape, kept for parity). The…

### Community 155 - "register_devotional_content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 156 - "monthly_report/service.py"
Cohesion: 0.22
Nodes (5): collections_abc, Timezone-aware, idempotent delivery of the previous month's progress., Open-contribution business logic: log a free-form amount toward an OPEN khatm's…, Personal and creator reporting services., zoneinfo

### Community 158 - "bot/__init__.py"
Cohesion: 0.33
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 160 - "test_reminder_tone_resolves_seeded_locale_template"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 161 - "deliver_due"
Cohesion: 0.40
Nodes (6): deliver_due(), _previous_month_bounds(), AsyncSession, datetime, NotifyFn, _render()

### Community 164 - "system_settings/__init__.py"
Cohesion: 0.40
Nodes (4): asyncio, parametrize, test_panel_logo_accepts_https_and_blank(), test_panel_logo_rejects_unsafe_or_relative_urls()

### Community 165 - "test_payment_safety.py"
Cohesion: 0.47
Nodes (5): asyncio, Fast safety checks for pending-payment expiry and replay behavior., test_callback_cas_loss_never_credits_wallet(), test_cleanup_delegates_with_current_time_and_reports_count(), test_expired_callback_stops_before_gateway_or_credit()

### Community 168 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 176 - "register_devotional_content_batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 181 - "_compose_niyyat"
Cohesion: 0.67
Nodes (3): C. ساخت ۴ نوع ختم, _compose_niyyat(), Owner rule (2026-09-27, DEC-PY-0090): the niyyat is FIXED for every khatm — «به…

### Community 184 - "test_member_bot_fixes.py"
Cohesion: 0.22
Nodes (7): _make_khatm(), Regression for the 2026-09-29 member-bot fixes (owner live report): 1. Open-…, Owner report: pages/reminders stopped arriving on member bots. The old…, test_open_quran_hour_accepts_exact_time(), test_quran_join_card_button_suppressed_when_autosetup(), test_reminder_due_fires_at_or_after_target_not_only_in_window(), test_settings_creator_panel_button_visibility()

### Community 230 - "run_once"
Cohesion: 0.16
Nodes (26): SendQuranPagesFn, has_started(), Return whether a scheduled khatm is allowed to deliver work yet., get_preference(), get_by_id(), _default_reminder_hour(), delegate_inactive_portions(), deliver_due_next_portions() (+18 more)

### Community 255 - "str"
Cohesion: 0.67
Nodes (3): JobStatus, NotifChannel, str

### Community 256 - "test_devotional_slug_link_does_not_depend_on_title_wording"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

## Knowledge Gaps
- **105 isolated node(s):** `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — IN-PROGRESS`, `4. Reliable modern Persian panel font — TODO`, `Cross-feature validation and delivery log` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1304 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **101 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `app.py`, `FSMContext`, `sqlalchemy`, `test_devotional_slug_link_does_not_depend_on_title_wording`, `t`, `create_khatm.py`, `new_id`, `admin.py`, `InvoiceKind`, `keyboards.py`, `test_tapping_a_time_of_day_button_saves_the_hour_without_typing`, `wallet/models.py`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `start.py`, `AdminFilter`, `authorization/service.py`, `settings_menu.py`, `ModerationMiddleware`, `khatm_workflow/service.py`, `Platform`, `Khatm`, `portions.py`, `User`, `test_registration_starts_in_the_users_saved_language`, `start_suggestion`, `register_devotional_content.py`, `test_confirm_wizard_resumes_and_finishes_creation_after_otp`, `UserRole`, `home_keyboard_for_bot`, `test_reminder_tone_resolves_seeded_locale_template`, `get_settings`, `KhatmRequest`, `member_commitment.py`, `KhatmCategoryGroup`, `PlanTier`, `wallet/repository.py`, `register_devotional_content_batch2.py`, `Session`, `DevotionalAsset`, `safe_answer_callback`, `_create_topup_payment`, `QuranAssetKind`, `test_payment_intent_is_owned_single_use_and_amount_bound`, `record`, `finish_invite_links`, `KhatmBroadcast`, `phone/repository.py`, `test_deliver_due_next_portions_pushes_real_content_not_just_text`, `receive_media`, `OpenContribution`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `message_template/repository.py`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `UserSettings`, `WalletInvoice`, `creator_broadcast/service.py`, `ensure_creator_phone_verified`, `test_health.py`, `manual_phone_verification/repository.py`, `sqlalchemy_ext_asyncio`, `list_identities_for_user`, `test_current_quran_delivery_is_exact_and_reciter_specific`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `app.py`, `FSMContext`, `create_khatm.py`, `new_id`, `test_public_khatms_reply_button_is_wired`, `keyboards.py`, `_default_khatm_title`, `session_scope`, `start.py`, `settings_menu.py`, `authorization/service.py`, `khatm_workflow/service.py`, `Platform`, `Khatm`, `portions.py`, `User`, `test_registration_starts_in_the_users_saved_language`, `start_suggestion`, `bot/__init__.py`, `UserRole`, `home_keyboard_for_bot`, `member_commitment.py`, `_phone_keyboard`, `PlanTier`, `reminder_engine/service.py`, `DevotionalAsset`, `safe_answer_callback`, `_compose_niyyat`, `_create_topup_payment`, `test_member_bot_fixes.py`, `finish_invite_links`, `test_creator_contact.py`, `ensure_creator_phone_verified`, `test_admin_template_render.py`, `_commitment_total_keyboard`, `run_once`, `list_identities_for_user`, `test_creator_finance_and_support_buttons_are_wired`, `help_topic`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `Architecture Document` connect `Architecture Document` to `keyboards.py`, `Multi-Bot Architecture (26 bots)`, `KhatmSaz Project (Claude Code Instructions)`, `DOMAIN_MODEL`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `t()` (e.g. with `test_both_panel_headers_support_configured_logo_and_fallback()` and `test_creator_detail_renders_manage_stats_members_export_and_settings()`) actually correct?**
  _`t()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 231 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 231 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `Khatm` (e.g. with `finish_invite_links()` and `send_other_language_links()`) actually correct?**
  _`Khatm` has 133 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — IN-PROGRESS` to the rest of the system?**
  _105 weakly-connected nodes found - possible documentation gaps or missing edges._