# Graph Report - Khatm  (2026-09-29)

## Corpus Check
- 447 files · ~314,236 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3765 nodes · 13522 edges · 237 communities (140 shown, 97 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 1989 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `46dbe3b0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- session_scope
- create_khatm.py
- sqlalchemy
- KhatmPortion
- phone/service.py
- t
- Khatm
- Platform
- system_settings/repository.py
- start.py
- my_khatms.py
- Base
- Participation
- main_menu_keyboard
- resolve_or_provision_user
- AdminRoleGrant
- typing
- sqlalchemy_dialects
- khatm_workflow/service.py
- get_or_create
- User
- portions.py
- PlatformIdentity
- alembic
- test_deep_link_clears_old_state_before_storing_new_join_context
- CHANGELOG
- creator_request.py
- provider.py
- PayPingGateway
- wallet/service.py
- test_confirm_wizard_resumes_and_finishes_creation_after_otp
- panel.py
- cancel_commitment
- creator_request/service.py
- get_settings
- khatmsaz_bot_handlers_join_flow
- suggestions.py
- member_commitment.py
- bail_if_menu_button
- bot_registry/service.py
- KhatmCategoryGroup
- PlanTier
- wallet/models.py
- notification/models.py
- sms_subscription/service.py
- test_member_cancel_clears_state
- completion/service.py
- types
- invitation/models.py
- sqlalchemy_ext_asyncio
- reminder_engine/service.py
- env.py
- DevotionalAsset
- show_member_portion
- create_topup
- content/service.py
- wallet/__init__.py
- BotRole
- test_creator_notified_with_phone_after_two_consecutive_missed_days
- audit_log/service.py
- broadcast.py
- phone/repository.py
- test_wizard_ephemeral.py
- test_i18n_audit.py
- Architecture Document
- بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`
- test_deliver_due_next_portions_pushes_real_content_not_just_text
- Admin Panel Base Layout (base.html)
- receive_media
- DECISIONS
- test_registration_phone_share_only.py
- DOMAIN_MODEL
- AsyncSession
- OpenContribution
- test_bale_invite_is_a_real_clickable_link_not_a_typed_command
- 435027907255_add_daily_deadline_hour_to_khatms.py
- test_quran_setup_waits_for_selected_hour_before_sending
- KhatmSaz Project (Claude Code Instructions)
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی
- waiting_list/models.py
- message_template/repository.py
- FakeMessage
- test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it
- test_new_bale_identity_moves_to_existing_profile_after_otp
- test_creator_contact.py
- QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)
- KhatmSaz VPS Deployment Guide
- Multi-Bot (26-bot) Architecture
- test_member_commitment_flow.py
- install_command_menu
- test_signed_telegram_admin_launch_sets_secure_scoped_cookie
- BotCategory
- test_dispatcher_routes_commands_while_profile_phone_state_is_active
- test_channel_coverage_counts_pages_not_source_posts
- creator_broadcast/service.py
- manual_phone_verification/service.py
- test_admin_template_render.py
- test_fixed_salawat_content.py
- CSS Layouts and Responsive Design Guide
- _commitment_total_keyboard
- positional_range_for_step
- test_health.py
- manual_phone_verification/repository.py
- test_broadcast_shows_khatm_picker
- message_template/__init__.py
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per bot)
- runtime_status.py
- qr.py
- UserStatus
- new_id
- test_quran_channel_source.py
- test_mini_app_entry.py
- test_notification_snooze.py
- Python Requirements
- Feature checklist
- change_phone.py
- test_creator_finance_and_support_buttons_are_wired
- test_set_font_size_validates_and_persists
- devotional_seed.py
- test_current_quran_delivery_is_exact_and_reciter_specific
- digest_command
- str
- test_next_portion_is_withheld_until_next_local_day_at_reminder_hour
- test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour
- test_contribute_blocked_until_delivery_hour_set
- zzz_merge_three_heads_2026_09_28.py
- confirm_account_deletion
- FakeState
- test_active_otp_is_reused_without_returning_another_sms_code
- Mini-App Only Authentication Pattern
- test_public_khatms_reply_button_is_wired
- Settings Menu Full-Button Test Scenario
- _default_khatm_title
- khatmsaz_modules_phone
- test_content_preferences_are_independent_and_persisted
- test_daily_digest_combines_multiple_khatms_for_one_user
- AdminFilter
- test_devotional_text_and_platform_specific_audio
- content_settings.py
- .__call__
- Tooltip Jinja2 Macro Component
- FakeState
- test_quran_page_assets_require_canonical_complete_ranges
- FakeMessage
- fc2337bfe5d5_add_khatm_capacity_and_participation_is_.py
- Bot Help Strings (Persian)
- Identity Across Platforms (phone-based merge key)
- resolve_creator_decision
- zoneinfo
- test_reminder_tone_resolves_seeded_locale_template
- test_sms_opt_in_requires_phone_and_can_be_disabled
- test_reminder_due_fires_at_or_after_target_not_only_in_window
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

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 386 edges
2. `t()` - 359 edges
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

## Communities (237 total, 97 thin omitted)

### Community 0 - "session_scope"
Cohesion: 0.08
Nodes (103): fastapi, fastapi_staticfiles, fastapi_templating, get, HTMLResponse, middleware, post, RedirectResponse (+95 more)

### Community 1 - "create_khatm.py"
Cohesion: 0.09
Nodes (92): C. ساخت ۴ نوع ختم, R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome(), _apply_coupon_code() (+84 more)

### Community 2 - "sqlalchemy"
Cohesion: 0.05
Nodes (62): datetime, functools, httpx, khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl (+54 more)

### Community 3 - "KhatmPortion"
Cohesion: 0.08
Nodes (78): AllocationStrategy, CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).… (+70 more)

### Community 4 - "phone/service.py"
Cohesion: 0.23
Nodes (22): AccountMerge, _assert_pristine_source_account(), complete_account_link(), complete_phone_change(), _consume_challenge(), _hash_code(), normalize_e164(), OtpError (+14 more)

### Community 5 - "t"
Cohesion: 0.05
Nodes (105): base64, InlineKeyboardButton, _confirm_keyboard(), InlineKeyboardMarkup, message, request_account_deletion(), help_command(), help_open_my_khatms() (+97 more)

### Community 6 - "Khatm"
Cohesion: 0.04
Nodes (149): build_join_success_message(), Shared with `join_requests.py`'s approval handler, which sends this same…, Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum, claim_completion_announcement(), create() (+141 more)

### Community 7 - "Platform"
Cohesion: 0.10
Nodes (77): aiogram_exceptions, _lang_for(), admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons() (+69 more)

### Community 8 - "system_settings/repository.py"
Cohesion: 0.22
Nodes (12): _inactivity_days(), Generic admin-editable key/value store for small system-wide numeric defaults…, SystemSetting, get(), list_all(), AsyncSession, set(), get_int() (+4 more)

### Community 9 - "start.py"
Cohesion: 0.05
Nodes (88): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types, عضو (Member bots) — تلگرام fa/ar/en و بله, html, Small, user-facing Telegram command menu for the primary journeys. (+80 more)

### Community 10 - "my_khatms.py"
Cohesion: 0.07
Nodes (77): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at() (+69 more)

### Community 11 - "Base"
Cohesion: 0.10
Nodes (29): DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Account-merge module: append-only audit of completed account merges., AdvertisingRewardRate (+21 more)

### Community 12 - "Participation"
Cohesion: 0.07
Nodes (72): sqlalchemy_exc, leave_khatm(), Leave a khatm. If the leaver was a committed participant, promote the next…, CommitmentMode, Participation, ParticipationStatus, advance_open_reading(), count_committed_active() (+64 more)

### Community 13 - "main_menu_keyboard"
Cohesion: 0.22
Nodes (13): FSMContext, message, receive_link_code(), receive_link_phone(), accept_join_preview(), choose_first_language(), handle_start(), callback_query (+5 more)

### Community 14 - "resolve_or_provision_user"
Cohesion: 0.11
Nodes (49): begin_account_link(), list_member_khatms(), message, message, set_reminder(), today_overview(), buy_sms_plan(), _can_open_creator_panel() (+41 more)

### Community 15 - "AdminRoleGrant"
Cohesion: 0.26
Nodes (11): AdminRoleGrant, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession, Persistence helpers for delegated admin roles., revoke_role(), asyncio (+3 more)

### Community 16 - "typing"
Cohesion: 0.04
Nodes (6): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 18 - "khatm_workflow/service.py"
Cohesion: 0.06
Nodes (47): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, Creator approve/reject for a PRIVATE khatm's join request (DOMAIN_MODEL.md §2…, reject_join(), Unpack two UUIDs from a short base64 string. (+39 more)

### Community 19 - "get_or_create"
Cohesion: 0.09
Nodes (42): CommandObject, message, set_font(), language_command(), CommandObject, message, CommandObject, message (+34 more)

### Community 20 - "User"
Cohesion: 0.14
Nodes (26): grant_role(), has_permission(), is_admin(), list_roles(), permissions_for(), AsyncSession, Role-to-permission policy for bot and web administration., revoke_role() (+18 more)

### Community 21 - "portions.py"
Cohesion: 0.09
Nodes (60): _parse_delivery_time(), Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., _active_participation_for_current_bot(), apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze() (+52 more)

### Community 22 - "PlatformIdentity"
Cohesion: 0.12
Nodes (23): PlatformIdentity, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity(), get_platform_identity(), list_platform_identities(), AsyncSession (+15 more)

### Community 24 - "test_deep_link_clears_old_state_before_storing_new_join_context"
Cohesion: 0.08
Nodes (15): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home() (+7 more)

### Community 25 - "CHANGELOG"
Cohesion: 0.08
Nodes (27): Multi-Bot Architecture (26 bots), CHANGELOG Archive (until 2026-09-18), PROJECT_STATE Archive (until 2026-09-18), CHANGELOG, Creator wallet-charge button, Devotional content library + seed, i18n coverage guard (fa/ar/en), Multi-bot invite links (bot/invite_links.py) (+19 more)

### Community 26 - "creator_request.py"
Cohesion: 0.21
Nodes (12): admin_approve_creator(), admin_reject_creator(), handle_creator_request_button(), handle_creator_request_message(), _lang_for(), callback_query, CallbackQuery, CommandObject (+4 more)

### Community 27 - "provider.py"
Cohesion: 0.06
Nodes (45): BaseSettings, dataclasses, hmac, json, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider (+37 more)

### Community 28 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, _create_topup_payment(), Shared: build a PayPing intent for `amount` and send the pay link., GatewayError, PaymentRequest, PaymentVerification, Exception, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 29 - "wallet/service.py"
Cohesion: 0.09
Nodes (41): PaymentGateway, Protocol, DiscountCoupon, PendingPayment, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, claim_pending_payment(), create_pending_payment(), delete_expired_unused_payments() (+33 more)

### Community 30 - "test_confirm_wizard_resumes_and_finishes_creation_after_otp"
Cohesion: 0.12
Nodes (6): set_registry(), FakeCallback, FakeMessage, FakeState, integration, test_confirm_wizard_resumes_and_finishes_creation_after_otp()

### Community 31 - "panel.py"
Cohesion: 0.11
Nodes (39): سازنده (Creator) — تلگرام, admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel(), handle_admin_panel_broadcast(), handle_admin_panel_requests(), handle_admin_panel_users() (+31 more)

### Community 32 - "cancel_commitment"
Cohesion: 0.36
Nodes (9): accept_commitment(), cancel_commitment(), callback_query, CallbackQuery, FSMContext, message, receive_delivery_hour(), receive_delivery_hour_button() (+1 more)

### Community 33 - "creator_request/service.py"
Cohesion: 0.12
Nodes (32): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, Data model for creator-role requests. A user submits a request to become a…, approve(), create(), get_by_id() (+24 more)

### Community 34 - "get_settings"
Cohesion: 0.11
Nodes (28): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, apscheduler_schedulers_asyncio, BaseMiddleware, _build_member_bots(), _configure_logging(), main() (+20 more)

### Community 36 - "suggestions.py"
Cohesion: 0.06
Nodes (77): logging, admin_approve_request(), admin_reject_request(), _lang_for(), callback_query, CallbackQuery, CommandObject, FSMContext (+69 more)

### Community 37 - "member_commitment.py"
Cohesion: 0.10
Nodes (46): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), CommitFlow, enter_count(), enter_custom_time() (+38 more)

### Community 38 - "bail_if_menu_button"
Cohesion: 0.06
Nodes (65): D. دعوت و عضویت, choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery (+57 more)

### Community 39 - "bot_registry/service.py"
Cohesion: 0.16
Nodes (28): cryptography_fernet, Fernet, BotInstance, get_by_id(), get_by_slot(), list_active(), list_active_members(), list_all() (+20 more)

### Community 40 - "KhatmCategoryGroup"
Cohesion: 0.06
Nodes (53): CreateKhatm, StatesGroup, resolve_bot_category(), KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str (+45 more)

### Community 41 - "PlanTier"
Cohesion: 0.11
Nodes (39): PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition() (+31 more)

### Community 42 - "wallet/models.py"
Cohesion: 0.10
Nodes (50): CouponDiscountType, CouponRedemption, InvoiceKind, InvoiceStatus, str, Wallet module: toman balance + advertising credit, append-only ledger, and…, Immutable purchase amounts plus a small paid/refunded lifecycle., TxType (+42 more)

### Community 43 - "notification/models.py"
Cohesion: 0.15
Nodes (24): JobStatus, NotifChannel, NotificationJob, NotificationLog, NotificationPreference, str, Notification module: scheduled reminder jobs, per-participation preferences,…, count_logs() (+16 more)

### Community 44 - "sms_subscription/service.py"
Cohesion: 0.14
Nodes (29): Time-limited SMS reminder subscriptions (owner request, 2026-09-20). SMS…, Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options() (+21 more)

### Community 45 - "test_member_cancel_clears_state"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 46 - "completion/service.py"
Cohesion: 0.15
Nodes (16): collections_abc, deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Idempotent, delayed completion announcements for every platform., Claim each eligible announcement once, then notify creator + active members. (+8 more)

### Community 47 - "types"
Cohesion: 0.10
Nodes (12): aiogram_enums, aiogram_fsm_storage_memory, contextlib, Regression for per-khatm broadcast targeting (owner request 2026-09-27):…, Regression (owner live QA 2026-09-28): right after joining a commitment khatm…, Regression: the creator reply-menu buttons «📊 گزارش و مالی» and «❓ راهنما و…, Regression for the 2026-09-29 member-bot fixes (owner live report): 1. Open-…, Regression: /cancel had no handler on member bots, so a member could get stuck… (+4 more)

### Community 48 - "invitation/models.py"
Cohesion: 0.39
Nodes (7): KhatmInvitation, Invitation module: owner-issued grants to join a khatm., create(), get_by_token_hash(), mark_accepted(), AsyncSession, Persistence access for invitation — the only place that runs SQL for this…

### Community 49 - "sqlalchemy_ext_asyncio"
Cohesion: 0.16
Nodes (26): hashlib, secrets, sqlalchemy_ext_asyncio, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, create_invitation(), mark_accepted() (+18 more)

### Community 50 - "reminder_engine/service.py"
Cohesion: 0.21
Nodes (20): collections, Positive khatm-completion announcements., Scheduled positive personal monthly reports., NotificationKind, already_sent_today(), record_sent(), _maybe_record_miss_and_notify_creator(), _maybe_send_reminder() (+12 more)

### Community 51 - "env.py"
Cohesion: 0.06
Nodes (24): asyncio, fixture, logging_config, do_run_migrations(), run_migrations_online(), os, build_body(), main() (+16 more)

### Community 52 - "DevotionalAsset"
Cohesion: 0.13
Nodes (22): deliver_devotional_media(), callback_query, CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional() (+14 more)

### Community 53 - "show_member_portion"
Cohesion: 0.33
Nodes (7): callback_query, CallbackQuery, FSMContext, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow…, show_member_portion(), show_member_reminder_hours()

### Community 54 - "create_topup"
Cohesion: 0.31
Nodes (9): ask_custom_topup(), create_topup(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery, FSMContext, Owner (2026-09-29): let the user charge the wallet with any amount. (+1 more)

### Community 55 - "content/service.py"
Cohesion: 0.14
Nodes (25): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., decode_telegram_forward_ref(), encode_telegram_forward_ref(), get_quran_total_pages(), parse_quran_channel_caption() (+17 more)

### Community 56 - "wallet/__init__.py"
Cohesion: 0.18
Nodes (9): Real PostgreSQL coverage for bounded, auditable coupon redemption., asyncio, test_purchase_pro_never_recharges_existing_paid_plan(), test_purchase_pro_requires_enabled_positive_admin_price(), test_purchase_pro_uses_database_price_spends_once_and_sets_plan(), asyncio, integration, Real PostgreSQL coverage for payment ownership and replay protection. (+1 more)

### Community 57 - "BotRole"
Cohesion: 0.23
Nodes (6): BotRegistry, Bot, UUID, Runtime registry of all live Bot instances, built once at startup., BotRole, str

### Community 58 - "test_creator_notified_with_phone_after_two_consecutive_missed_days"
Cohesion: 0.38
Nodes (6): asyncio, integration, Owner decision (2026-09-22): creator notification must include member's phone…, test_creator_notified_only_after_threshold_and_member_never_notified(), fake_notify(), test_creator_notified_with_phone_after_two_consecutive_missed_days()

### Community 59 - "audit_log/service.py"
Cohesion: 0.33
Nodes (4): Append-only audit trail for sensitive administrative actions., list_recent(), AsyncSession, Business facade for recording privileged actions.

### Community 60 - "broadcast.py"
Cohesion: 0.17
Nodes (28): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, Creator message requests with mandatory admin moderation. (+20 more)

### Community 61 - "phone/repository.py"
Cohesion: 0.18
Nodes (25): OtpChallenge, OtpPurpose, PhoneClaim, PhoneClaimStatus, str, create_challenge(), create_or_verify_claim(), get_challenge() (+17 more)

### Community 62 - "test_wizard_ephemeral.py"
Cohesion: 0.21
Nodes (11): FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_can_keep_intro_beside_title_until_answered(), test_wiz_deletes_previous_prompt() (+3 more)

### Community 63 - "test_i18n_audit.py"
Cohesion: 0.11
Nodes (12): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source() (+4 more)

### Community 64 - "Architecture Document"
Cohesion: 0.18
Nodes (15): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, No Business Rule Invention Rule, Architecture Document, Module: allocation, Module: bot_registry (+7 more)

### Community 65 - "بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`"
Cohesion: 0.11
Nodes (18): R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**, R13. کمترین سؤال ممکن — اصل کلی هر دو بخش., R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک** (+10 more)

### Community 66 - "test_deliver_due_next_portions_pushes_real_content_not_just_text"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_deliver_due_next_portions_pushes_real_content_not_just_text()

### Community 67 - "Admin Panel Base Layout (base.html)"
Cohesion: 0.18
Nodes (18): Admin Panel Base Layout (base.html), components.html macros (tooltip), Glassmorphism Dark Design System, Permission-gated Admin Navigation, Admin Categories Page (categories.html), Creator Panel Base Layout (creator_base.html), Creator Panel i18n (t/lang) Localization, Creator Dashboard (creator_dashboard.html) (+10 more)

### Community 68 - "receive_media"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 69 - "DECISIONS"
Cohesion: 0.23
Nodes (13): DECISIONS, DEC-PY-0073 — Dashboards are messenger Mini Apps, DEC-PY-0076 — Separate participant and creator menus, DEC-PY-0077 — Daily portions stack up, DEC-PY-0091 — Creation wizard no longer asks content format, DEC-PY-0092 — Rotating Quran allocation, DEC-PY-0093 — Creator bot has one fixed menu, starts creation directly, DEC-PY-0094 — Quran reading pace chosen by each member (+5 more)

### Community 70 - "test_registration_phone_share_only.py"
Cohesion: 0.18
Nodes (8): StatesGroup, Registration, FakeMessage, FakeState, asyncio, Owner request (2026-09-22): during initial registration on Telegram, only the…, test_bale_typed_phone_is_still_accepted_during_registration(), test_telegram_typed_phone_is_rejected_during_registration()

### Community 71 - "DOMAIN_MODEL"
Cohesion: 0.15
Nodes (17): PayPing payment gateway, PendingPayment compare-and-swap replay protection, R11/N2 member commitment flow (regular/count), Codex Handoff — Next Steps, PayPing gateway activation (needs owner API token), DEC-PY-0068 — Kavenegar is first production SMS adapter, DEC-PY-0074 — Free-tier plan caps per-creator, admin-editable, DEC-PY-0090 — Fixed niyyat + optional niyabat (+9 more)

### Community 72 - "AsyncSession"
Cohesion: 0.13
Nodes (18): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), list_all_devotional_assets(), AsyncSession, Store the optional admin-managed image for the one fixed Salawat. Salawat is…, Mirrors `register_devotional_audio` — an image of the devotional text (owner…, Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.… (+10 more)

### Community 73 - "OpenContribution"
Cohesion: 0.12
Nodes (22): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+14 more)

### Community 74 - "test_bale_invite_is_a_real_clickable_link_not_a_typed_command"
Cohesion: 0.18
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 76 - "test_quran_setup_waits_for_selected_hour_before_sending"
Cohesion: 0.13
Nodes (4): FakeMessage, FakeState, asyncio, test_quran_setup_waits_for_selected_hour_before_sending()

### Community 77 - "KhatmSaz Project (Claude Code Instructions)"
Cohesion: 0.15
Nodes (17): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), Admin Mini App (Telegram WebApp), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), PayPing v3 Payment Gateway, Admin Mini App Guide (Persian), AI Handoff Protocol (+9 more)

### Community 78 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی"
Cohesion: 0.14
Nodes (14): Live QA — 2026-09-28 (Chrome / Telegram Web / Codex), QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), رفع‌شدهٔ همین عصر (Claude Code), ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live) (+6 more)

### Community 79 - "waiting_list/models.py"
Cohesion: 0.26
Nodes (11): Waiting-list module: queue for full-capacity COMMITMENT khatms., WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next() (+3 more)

### Community 80 - "message_template/repository.py"
Cohesion: 0.26
Nodes (13): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+5 more)

### Community 82 - "test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it"
Cohesion: 0.18
Nodes (7): FakeMessage, FakeState, asyncio, integration, R11 supersedes the old bare delivery-hour question for repetitions., test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it(), test_fresh_committed_salawat_join_asks_commitment_mode()

### Community 83 - "test_new_bale_identity_moves_to_existing_profile_after_otp"
Cohesion: 0.67
Nodes (4): asyncio, integration, test_new_bale_identity_moves_to_existing_profile_after_otp(), test_nonempty_provisional_account_cannot_be_silently_merged()

### Community 84 - "test_creator_contact.py"
Cohesion: 0.22
Nodes (12): _compose_welcome_with_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/…, test_compose_appends_contact_line_to_welcome(), test_compose_contact_only_when_no_welcome(), test_compose_none_contact_passes_welcome_through() (+4 more)

### Community 85 - "QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)"
Cohesion: 0.18
Nodes (11): A. زیرساخت چندبات (۲۶ بات), B. ثبت‌نام, E. سهم و یادآوری, F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات, G. زبان‌ها (fa/ar/en), H. پرداخت, I. Mini App + پنل ادمین, QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه) (+3 more)

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

### Community 90 - "test_signed_telegram_admin_launch_sets_secure_scoped_cookie"
Cohesion: 0.50
Nodes (4): asyncio, integration, _signed_init_data(), test_signed_telegram_admin_launch_sets_secure_scoped_cookie()

### Community 91 - "BotCategory"
Cohesion: 0.21
Nodes (13): _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, BotCategory, R2 (owner 2026-09-28): per-bot intro image shown after the creator picks…, test_dua_group_maps_to_dua_ziyarat_bot(), test_laan_group_maps_to_laan_bot(), test_quran_maps_to_quran_bot(), test_salawat_default() (+5 more)

### Community 92 - "test_dispatcher_routes_commands_while_profile_phone_state_is_active"
Cohesion: 0.18
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 93 - "test_channel_coverage_counts_pages_not_source_posts"
Cohesion: 0.67
Nodes (4): asyncio, integration, test_channel_coverage_counts_pages_not_source_posts(), test_channel_range_registry_is_idempotent_and_resolves_shared_audio()

### Community 94 - "creator_broadcast/service.py"
Cohesion: 0.21
Nodes (19): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+11 more)

### Community 95 - "manual_phone_verification/service.py"
Cohesion: 0.24
Nodes (13): decide_manual_phone_request(), callback_query, CallbackQuery, approve(), ManualVerificationError, AsyncSession, ValueError, Manual verification for foreign numbers that cannot receive Iranian SMS. (+5 more)

### Community 96 - "test_admin_template_render.py"
Cohesion: 0.29
Nodes (11): starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests…, _render(), _request(), test_categories_page_renders_library_picker_and_explicit_statuses(), test_creator_detail_renders_manage_stats_members_export_and_settings(), test_creator_new_khatm_form_renders_all_four_types_and_creation_route() (+3 more)

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

### Community 104 - "message_template/__init__.py"
Cohesion: 0.12
Nodes (12): Localized, versioned message templates., AsyncSession, Template lookup and safe ``{{placeholder}}`` rendering., Reject malformed or unsupported placeholders before a template is stored., render(), validate_body(), asyncio, parametrize (+4 more)

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

### Community 110 - "UserStatus"
Cohesion: 0.15
Nodes (18): str, UserStatus, set_status(), AccountDeletionBlocked, ban(), _bootstrap_super_admin_if_configured(), delete_account(), demote_creator() (+10 more)

### Community 111 - "new_id"
Cohesion: 0.10
Nodes (25): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), AuditLog, Audit records are immutable facts about privileged actions., list_recent(), AsyncSession (+17 more)

### Community 112 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 113 - "test_mini_app_entry.py"
Cohesion: 0.20
Nodes (12): _message(), asyncio, Fail-closed behavior before a public HTTPS Mini App origin exists., test_admin_mini_app_rejects_local_http_origin(), test_creator_mini_app_rejects_local_http_origin_before_database_access(), test_panel_buttons_request_chat_entry_before_opening_mini_app(), asyncio, Fast safety checks for pending-payment expiry and replay behavior. (+4 more)

### Community 114 - "test_notification_snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 115 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 116 - "Feature checklist"
Cohesion: 0.25
Nodes (7): 1. Graphical creator Mini App khatm creation — DONE, 2. Real FREE → PRO purchase — IN-PROGRESS, 3. Configurable panel logo — TODO, 4. Reliable modern Persian panel font — TODO, Codex big features progress — 2026-09-29, Cross-feature validation and delivery log, Feature checklist

### Community 117 - "change_phone.py"
Cohesion: 0.16
Nodes (20): begin_phone_change(), ChangePhone, ensure_creator_phone_verified(), _lang_for(), FSMContext, Message, StatesGroup, Self-service verified phone replacement that keeps all account history. (+12 more)

### Community 118 - "test_creator_finance_and_support_buttons_are_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 121 - "test_set_font_size_validates_and_persists"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 123 - "devotional_seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 124 - "test_current_quran_delivery_is_exact_and_reciter_specific"
Cohesion: 0.22
Nodes (9): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., get_allowed_reciters(), get_effective_reciter(), Favorite wins only when allowed; otherwise use whitelist then default., set_allowed_reciters(), asyncio, integration (+1 more)

### Community 126 - "digest_command"
Cohesion: 0.67
Nodes (3): digest_command(), CommandObject, message

### Community 127 - "str"
Cohesion: 0.67
Nodes (3): AssignmentStatus, AssignmentUnitKind, str

### Community 128 - "test_next_portion_is_withheld_until_next_local_day_at_reminder_hour"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 129 - "test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 130 - "test_contribute_blocked_until_delivery_hour_set"
Cohesion: 0.29
Nodes (4): _callback_update(), asyncio, Update, test_contribute_blocked_until_delivery_hour_set()

### Community 131 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 132 - "confirm_account_deletion"
Cohesion: 0.60
Nodes (5): cancel_account_deletion(), confirm_account_deletion(), _lang_for(), callback_query, CallbackQuery

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

### Community 140 - "test_content_preferences_are_independent_and_persisted"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_content_preferences_are_independent_and_persisted()

### Community 142 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

### Community 143 - "test_devotional_text_and_platform_specific_audio"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 144 - "content_settings.py"
Cohesion: 0.30
Nodes (11): callback_query, CallbackQuery, CommandObject, Message, quran_help(), Per-user translation/tafsir display preferences., _set_audio(), set_audio_callback() (+3 more)

### Community 145 - ".__call__"
Cohesion: 0.60
Nodes (4): _extract_chat_id(), Any, _reply_blocked(), TelegramObject

### Community 146 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.50
Nodes (4): Tooltip Jinja2 Macro Component, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 148 - "test_quran_page_assets_require_canonical_complete_ranges"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_quran_page_assets_require_canonical_complete_ranges()

### Community 151 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 152 - "Identity Across Platforms (phone-based merge key)"
Cohesion: 0.67
Nodes (3): Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 154 - "resolve_creator_decision"
Cohesion: 0.50
Nodes (4): CommandObject, message, Owner decision (2026-09-21): the missed-portion/emergency-pool system this…, resolve_creator_decision()

### Community 160 - "test_reminder_tone_resolves_seeded_locale_template"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 161 - "test_sms_opt_in_requires_phone_and_can_be_disabled"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_sms_opt_in_requires_phone_and_can_be_disabled()

### Community 230 - "run_once"
Cohesion: 0.20
Nodes (21): SendQuranPagesFn, has_started(), Return whether a scheduled khatm is allowed to deliver work yet., get_preference(), get_by_id(), _default_reminder_hour(), delegate_inactive_portions(), deliver_due_next_portions() (+13 more)

## Knowledge Gaps
- **105 isolated node(s):** `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — IN-PROGRESS`, `3. Configurable panel logo — TODO`, `4. Reliable modern Persian panel font — TODO`, `Cross-feature validation and delivery log` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1303 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **97 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `create_khatm.py`, `sqlalchemy`, `test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour`, `confirm_account_deletion`, `t`, `Khatm`, `Platform`, `start.py`, `my_khatms.py`, `test_content_preferences_are_independent_and_persisted`, `main_menu_keyboard`, `AdminFilter`, `resolve_or_provision_user`, `content_settings.py`, `.__call__`, `khatm_workflow/service.py`, `get_or_create`, `User`, `portions.py`, `AdminRoleGrant`, `test_devotional_text_and_platform_specific_audio`, `PlatformIdentity`, `test_quran_page_assets_require_canonical_complete_ranges`, `creator_request.py`, `PayPingGateway`, `test_confirm_wizard_resumes_and_finishes_creation_after_otp`, `panel.py`, `cancel_commitment`, `test_reminder_tone_resolves_seeded_locale_template`, `get_settings`, `test_sms_opt_in_requires_phone_and_can_be_disabled`, `suggestions.py`, `member_commitment.py`, `bail_if_menu_button`, `KhatmCategoryGroup`, `PlanTier`, `wallet/models.py`, `env.py`, `DevotionalAsset`, `show_member_portion`, `create_topup`, `wallet/__init__.py`, `test_creator_notified_with_phone_after_two_consecutive_missed_days`, `broadcast.py`, `phone/repository.py`, `Participation`, `test_deliver_due_next_portions_pushes_real_content_not_just_text`, `receive_media`, `OpenContribution`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `message_template/repository.py`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `test_new_bale_identity_moves_to_existing_profile_after_otp`, `test_signed_telegram_admin_launch_sets_secure_scoped_cookie`, `test_channel_coverage_counts_pages_not_source_posts`, `creator_broadcast/service.py`, `manual_phone_verification/service.py`, `test_health.py`, `manual_phone_verification/repository.py`, `new_id`, `change_phone.py`, `test_current_quran_delivery_is_exact_and_reciter_specific`, `digest_command`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `session_scope`, `create_khatm.py`, `confirm_account_deletion`, `Khatm`, `test_public_khatms_reply_button_is_wired`, `start.py`, `_default_khatm_title`, `my_khatms.py`, `main_menu_keyboard`, `resolve_or_provision_user`, `khatm_workflow/service.py`, `get_or_create`, `User`, `portions.py`, `creator_request.py`, `resolve_creator_decision`, `PayPingGateway`, `panel.py`, `cancel_commitment`, `suggestions.py`, `member_commitment.py`, `bail_if_menu_button`, `PlanTier`, `reminder_engine/service.py`, `DevotionalAsset`, `show_member_portion`, `create_topup`, `test_creator_contact.py`, `manual_phone_verification/service.py`, `test_admin_template_render.py`, `_commitment_total_keyboard`, `run_once`, `change_phone.py`, `test_creator_finance_and_support_buttons_are_wired`, `digest_command`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `session_scope`, `create_khatm.py`, `sqlalchemy`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `confirm_account_deletion`, `t`, `phone/service.py`, `Khatm`, `test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour`, `start.py`, `my_khatms.py`, `main_menu_keyboard`, `AdminFilter`, `resolve_or_provision_user`, `content_settings.py`, `khatm_workflow/service.py`, `get_or_create`, `portions.py`, `PlatformIdentity`, `FakeMessage`, `test_deep_link_clears_old_state_before_storing_new_join_context`, `creator_request.py`, `PayPingGateway`, `test_confirm_wizard_resumes_and_finishes_creation_after_otp`, `panel.py`, `cancel_commitment`, `get_settings`, `suggestions.py`, `bail_if_menu_button`, `env.py`, `DevotionalAsset`, `show_member_portion`, `create_topup`, `BotRole`, `test_creator_notified_with_phone_after_two_consecutive_missed_days`, `broadcast.py`, `test_deliver_due_next_portions_pushes_real_content_not_just_text`, `receive_media`, `test_registration_phone_share_only.py`, `OpenContribution`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `test_quran_setup_waits_for_selected_hour_before_sending`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `test_new_bale_identity_moves_to_existing_profile_after_otp`, `install_command_menu`, `test_signed_telegram_admin_launch_sets_secure_scoped_cookie`, `creator_broadcast/service.py`, `manual_phone_verification/service.py`, `UserStatus`, `new_id`, `test_mini_app_entry.py`, `change_phone.py`, `digest_command`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `t()` (e.g. with `test_creator_detail_renders_manage_stats_members_export_and_settings()` and `test_creator_new_khatm_form_renders_all_four_types_and_creation_route()`) actually correct?**
  _`t()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 231 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 231 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `Khatm` (e.g. with `finish_invite_links()` and `send_other_language_links()`) actually correct?**
  _`Khatm` has 133 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — IN-PROGRESS`, `3. Configurable panel logo — TODO` to the rest of the system?**
  _105 weakly-connected nodes found - possible documentation gaps or missing edges._