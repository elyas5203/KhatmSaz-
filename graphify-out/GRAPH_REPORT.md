# Graph Report - Khatm  (2026-09-29)

## Corpus Check
- 448 files · ~315,269 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 3776 nodes · 13559 edges · 238 communities (137 shown, 101 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 1991 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `665a3c64`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- FSMContext
- sqlalchemy
- KhatmPortion
- allocation/service.py
- t
- KhatmTemplateType
- admin.py
- DevotionalAsset
- Platform
- session_scope
- advertising/service.py
- Participation
- resume_join_after_registration
- FakeMessage
- authorization/service.py
- typing
- sqlalchemy_dialects
- khatm_workflow/service.py
- resolve_or_provision_user
- Khatm
- portions.py
- User
- alembic
- test_deep_link_clears_old_state_before_storing_new_join_context
- CHANGELOG
- suggestions.py
- provider.py
- PayPingGateway
- wallet/service.py
- BotRegistry
- panel.py
- invite_links.py
- creator_request/service.py
- get_settings
- khatmsaz_bot_handlers_join_flow
- sqlalchemy_ext_asyncio
- member_commitment.py
- bail_if_menu_button
- bot_registry/service.py
- khatm_category/service.py
- PlanTier
- FakeMessage
- test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member
- sms_subscription/service.py
- test_member_cancel_clears_state
- test_creator_wallet_button_is_wired
- Base
- handle_start_with_payload
- Session
- payping_callback
- test_notify_routing.py
- deliver_devotional_media
- safe_clear_inline_keyboard
- wallet.py
- QuranAssetKind
- test_devotional_category_navigation.py
- test_signed_telegram_admin_launch_sets_secure_scoped_cookie
- finish_invite_links
- broadcast.py
- phone/service.py
- _wiz
- test_admin_template_render.py
- Architecture Document
- بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`
- test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour
- Admin Panel Base Layout (base.html)
- append_devotional_media_from_message
- DECISIONS
- commitment.py
- DOMAIN_MODEL
- AsyncSession
- get_khatm_stats
- test_bale_invite_is_a_real_clickable_link_not_a_typed_command
- 435027907255_add_daily_deadline_hour_to_khatms.py
- test_quran_setup_waits_for_selected_hour_before_sending
- KhatmSaz Project (Claude Code Instructions)
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی
- message_template/repository.py
- FakeMessage
- test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it
- find_by_id
- test_creator_contact.py
- QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)
- KhatmSaz VPS Deployment Guide
- Multi-Bot (26-bot) Architecture
- test_member_commitment_flow.py
- install_command_menu
- KhatmCategoryGroup
- test_dispatcher_routes_commands_while_profile_phone_state_is_active
- test_recitation_text_only_for_laan.py
- test_ad_reward_requires_opt_in_and_is_idempotent
- test_fixed_salawat_content.py
- CSS Layouts and Responsive Design Guide
- _commitment_total_keyboard
- positional_range_for_step
- test_health.py
- audit_log/repository.py
- test_broadcast_shows_khatm_picker
- test_message_template.py
- list_recent
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per bot)
- runtime_status.py
- qr.py
- AccountDeletionBlocked
- UserRole
- test_quran_channel_source.py
- broadcast/__init__.py
- types
- Python Requirements
- Feature checklist
- join_requests.py
- test_creator_finance_and_support_buttons_are_wired
- test_set_font_size_validates_and_persists
- devotional_seed.py
- content/service.py
- asyncio
- test_next_portion_is_withheld_until_next_local_day_at_reminder_hour
- test_contribute_blocked_until_delivery_hour_set
- zzz_merge_three_heads_2026_09_28.py
- confirm_account_deletion
- test_tapping_a_time_of_day_button_saves_the_hour_without_typing
- Mini-App Only Authentication Pattern
- test_public_khatms_reply_button_is_wired
- Settings Menu Full-Button Test Scenario
- create_khatm.py
- khatmsaz_modules_phone
- test_salawat_category_group_always_goes_directly_to_mode
- AdminFilter
- test_quran_join_is_member_controlled_without_auto_allocation
- .__call__
- Tooltip Jinja2 Macro Component
- Multi-Bot Architecture (26 bots)
- test_registration_starts_in_the_users_saved_language
- PROJECT_STATE
- Bot Help Strings (Persian)
- Identity Across Platforms (phone-based merge key)
- register_devotional_content.py
- FakeState
- bot/__init__.py
- message_template/__init__.py
- env.py
- 1f9fe3de23a1_add_khatm_requests_table.py
- b7c8d9e0f1a2_add_bot_instances.py
- c21644dab334_add_skip_today_pause_and_leave_reason_.py
- register_devotional_content_batch2.py
- new_id
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
- reminder_engine/service.py
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
- `R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**` --references--> `handle_member_start_with_payload()`  [INFERRED]
  docs/ai/REDESIGN_PLAN_2026-09-28.md → src/khatmsaz/bot/handlers/member_start.py
- `A. زیرساخت چندبات (۲۶ بات)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX_PHASE1.md → src/khatmsaz/bot/handlers/start.py
- `E. سهم و یادآوری` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX_PHASE1.md → src/khatmsaz/bot/handlers/start.py
- `رفع‌شدهٔ live-QA (2026-09-28)` --references--> `resume_join_after_registration()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/handlers/start.py
- `رفع‌شدهٔ فاز ۲ (این جلسه، با تست)` --references--> `snooze_keyboard()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/bot/keyboards.py

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

## Communities (238 total, 101 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.08
Nodes (93): fastapi, fastapi_staticfiles, fastapi_templating, get, middleware, post, RedirectResponse, Request (+85 more)

### Community 1 - "FSMContext"
Cohesion: 0.20
Nodes (31): R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome(), _ask_creator_contact(), _ask_visibility() (+23 more)

### Community 2 - "sqlalchemy"
Cohesion: 0.06
Nodes (50): httpx, json, khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, openpyxl, pytest, re, sqlalchemy (+42 more)

### Community 3 - "KhatmPortion"
Cohesion: 0.12
Nodes (44): CommittedQuantityLog, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion(), assign_portion() (+36 more)

### Community 4 - "allocation/service.py"
Cohesion: 0.13
Nodes (35): AllocationStrategy, KhatmAllocationPlan, create_plan(), get_plan_by_khatm(), increment_plan_total(), assign_quantity_commitment(), claim_next_open_portion(), complete_current_portion_and_advance() (+27 more)

### Community 5 - "t"
Cohesion: 0.05
Nodes (99): base64, InlineKeyboardButton, help_command(), help_open_my_khatms(), help_start_creation(), help_topic(), callback_query, CallbackQuery (+91 more)

### Community 6 - "KhatmTemplateType"
Cohesion: 0.05
Nodes (64): build_join_preview_message(), build_join_success_message(), _clean_niyyat(), Shared with `join_requests.py`'s approval handler, which sends this same…, Strip a leading «به نیت»/«بنية»/«Intention» so the display label…, Owner complaint (2026-09-20): the old preview only showed title/…, KhatmTemplateType, KhatmTypeEnum (+56 more)

### Community 7 - "admin.py"
Cohesion: 0.10
Nodes (72): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+64 more)

### Community 8 - "DevotionalAsset"
Cohesion: 0.13
Nodes (15): DevotionalAsset, Admin-curated complete text/audio for a dua or ziyarat., list_all_devotional_assets(), Store the optional admin-managed image for the one fixed Salawat. Salawat is…, Mirrors `register_devotional_audio` — an image of the devotional text (owner…, Every devotional asset (enabled or not), newest first — for the admin…, Enable/disable a devotional asset by slug (admin toggle). Returns the row, or…, register_devotional_audio() (+7 more)

### Community 9 - "Platform"
Cohesion: 0.05
Nodes (92): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_fsm_storage_memory, aiogram_types, collections_abc, functools (+84 more)

### Community 10 - "session_scope"
Cohesion: 0.08
Nodes (79): csv, callback_query, CallbackQuery, quran_help(), set_audio_callback(), ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm() (+71 more)

### Community 11 - "advertising/service.py"
Cohesion: 0.11
Nodes (18): khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent. (+10 more)

### Community 12 - "Participation"
Cohesion: 0.09
Nodes (59): sqlalchemy_exc, leave_khatm(), Leave a khatm. If the leaver was a committed participant, promote the next…, Apply the creator's Q77 decision to a committed Quran participant. ``continue``…, resolve_missed_commitment(), Participation, ParticipationStatus, advance_open_reading() (+51 more)

### Community 13 - "resume_join_after_registration"
Cohesion: 0.08
Nodes (37): عضو (Member bots) — تلگرام fa/ar/en و بله, Kick off the mode picker for a freshly-joined commitment member., start_commitment_mode_picker(), handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload(), callback_query (+29 more)

### Community 14 - "FakeMessage"
Cohesion: 0.25
Nodes (3): R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, FakeCallback, FakeMessage

### Community 15 - "authorization/service.py"
Cohesion: 0.15
Nodes (26): admin_approve_request(), admin_list_requests(), admin_reject_request(), CommandObject, Message, request_khatm(), _resolve_decision(), AdminRole (+18 more)

### Community 16 - "typing"
Cohesion: 0.05
Nodes (4): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 18 - "khatm_workflow/service.py"
Cohesion: 0.08
Nodes (37): _creator_display_name(), CoverStatus, CreatorDisplayMode, KhatmScheduleKind, str, ReminderTone, approve_join_request(), _complete_join() (+29 more)

### Community 19 - "resolve_or_provision_user"
Cohesion: 0.05
Nodes (98): _lang_for(), CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), _lang_for(), CommandObject (+90 more)

### Community 20 - "Khatm"
Cohesion: 0.12
Nodes (58): Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+50 more)

### Community 21 - "portions.py"
Cohesion: 0.10
Nodes (58): accept_commitment(), cancel_commitment(), _parse_delivery_time(), callback_query, CallbackQuery, FSMContext, message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid. (+50 more)

### Community 22 - "User"
Cohesion: 0.06
Nodes (59): ChangePhone, StatesGroup, _member_creators(), Creators of the member's ACTIVE khatms, each with the member's own…, PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity() (+51 more)

### Community 24 - "test_deep_link_clears_old_state_before_storing_new_join_context"
Cohesion: 0.08
Nodes (15): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home() (+7 more)

### Community 25 - "CHANGELOG"
Cohesion: 0.15
Nodes (14): CHANGELOG Archive (until 2026-09-18), CHANGELOG, Creator wallet-charge button, Devotional content library + seed, i18n coverage guard (fa/ar/en), positional_range_for_step (rotating allocation helper), Reminder engine (APScheduler scan), DEC-PY-0072 — Devotional families are independent top-level choices (+6 more)

### Community 26 - "suggestions.py"
Cohesion: 0.14
Nodes (24): handle_creator_request_button(), callback_query, CallbackQuery, back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext (+16 more)

### Community 27 - "provider.py"
Cohesion: 0.06
Nodes (44): BaseSettings, dataclasses, hmac, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider (+36 more)

### Community 28 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, _create_topup_payment(), Shared: build a PayPing intent for `amount` and send the pay link., GatewayError, PaymentRequest, PaymentVerification, Exception, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 29 - "wallet/service.py"
Cohesion: 0.06
Nodes (95): accrue_first_completed_action(), Grant one reward only after the first completed assigned action. The…, PaymentGateway, Protocol, CouponDiscountType, CouponRedemption, DiscountCoupon, InvoiceKind (+87 more)

### Community 30 - "BotRegistry"
Cohesion: 0.33
Nodes (3): BotRegistry, Bot, UUID

### Community 31 - "panel.py"
Cohesion: 0.10
Nodes (42): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+34 more)

### Community 32 - "invite_links.py"
Cohesion: 0.29
Nodes (5): pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Choose one link to encode in a QR: prefer the creator's language and platform,…, resolve_khatm_category_value()

### Community 33 - "creator_request/service.py"
Cohesion: 0.13
Nodes (31): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user() (+23 more)

### Community 34 - "get_settings"
Cohesion: 0.10
Nodes (32): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, apscheduler_schedulers_asyncio, BaseMiddleware, _build_member_bots(), _configure_logging() (+24 more)

### Community 36 - "sqlalchemy_ext_asyncio"
Cohesion: 0.05
Nodes (60): sqlalchemy_ext_asyncio, UUID, uuid7(), KhatmRequest, KhatmRequestStatus, str, create(), get_by_id() (+52 more)

### Community 37 - "member_commitment.py"
Cohesion: 0.19
Nodes (30): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), CommitFlow, enter_count(), enter_custom_time() (+22 more)

### Community 38 - "bail_if_menu_button"
Cohesion: 0.07
Nodes (58): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+50 more)

### Community 39 - "bot_registry/service.py"
Cohesion: 0.17
Nodes (27): cryptography_fernet, Fernet, BotInstance, get_by_id(), get_by_slot(), list_active(), list_active_members(), list_all() (+19 more)

### Community 40 - "khatm_category/service.py"
Cohesion: 0.20
Nodes (29): _content_group(), Which of the four top-level content families (BACKLOG.md §18 level 2) a khatm…, KhatmCategory, KhatmCategoryRequest, KhatmCategoryRequestStatus, A participant's typed request for a دعا that isn't in the library yet (owner…, create(), create_request() (+21 more)

### Community 41 - "PlanTier"
Cohesion: 0.09
Nodes (46): PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition() (+38 more)

### Community 43 - "test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 44 - "sms_subscription/service.py"
Cohesion: 0.15
Nodes (29): _sms_menu_text_and_keyboard(), Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options() (+21 more)

### Community 45 - "test_member_cancel_clears_state"
Cohesion: 0.29
Nodes (6): MemberRegistration, StatesGroup, _cancel_update(), asyncio, Update, test_member_cancel_clears_state()

### Community 46 - "test_creator_wallet_button_is_wired"
Cohesion: 0.33
Nodes (4): asyncio, Update, test_creator_wallet_button_is_wired(), _text_update()

### Community 47 - "Base"
Cohesion: 0.06
Nodes (57): datetime, DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's… (+49 more)

### Community 48 - "handle_start_with_payload"
Cohesion: 0.20
Nodes (15): handle_start_with_payload(), CommandObject, create(), get_by_token_hash(), mark_accepted(), AsyncSession, Persistence access for invitation — the only place that runs SQL for this…, InvitationExpiredError (+7 more)

### Community 49 - "Session"
Cohesion: 0.19
Nodes (22): hashlib, secrets, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, create_invitation(), Session, create() (+14 more)

### Community 50 - "payping_callback"
Cohesion: 0.40
Nodes (5): HTMLResponse, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 51 - "test_notify_routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 52 - "deliver_devotional_media"
Cohesion: 0.14
Nodes (16): deliver_devotional_media(), callback_query, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional_reciter_choice(), DevotionalMedia (+8 more)

### Community 53 - "safe_clear_inline_keyboard"
Cohesion: 0.15
Nodes (31): C. ساخت ۴ نوع ختم, R8. ترتیب پلتفرم: «هر دو» بالا، بعد تلگرام، بعد بله — **بدون مایگریشن**, _ask_mode(), cancel_wizard(), choose_allowed_platforms(), choose_category(), choose_category_group(), choose_custom_category() (+23 more)

### Community 54 - "wallet.py"
Cohesion: 0.11
Nodes (27): سازنده (Creator) — تلگرام, handle_creator_finance(), handle_creator_support(), handle_creator_wallet(), message, The creator reply-menu button «📊 گزارش و مالی» previously had no handler at all…, «💳 شارژ کیف پول» — open the wallet overview + top-up options. The top-up flow…, «❓ راهنما و پشتیبانی» reply button had no handler either — route it to the help… (+19 more)

### Community 55 - "QuranAssetKind"
Cohesion: 0.15
Nodes (20): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), quran_channel_coverage(), Idempotently map one source-channel post to every page it covers., Return exact 604-page coverage and missing pages for channel forwards. (+12 more)

### Community 56 - "test_devotional_category_navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 57 - "test_signed_telegram_admin_launch_sets_secure_scoped_cookie"
Cohesion: 0.50
Nodes (4): asyncio, integration, _signed_init_data(), test_signed_telegram_admin_launch_sets_secure_scoped_cookie()

### Community 59 - "finish_invite_links"
Cohesion: 0.24
Nodes (10): finish_invite_links(), handle_confirm_invite_langs(), R9: on request, send the Arabic + English member-bot invite links., send_other_language_links(), show_invite_platform_keyboard(), build_member_invite_links(), format_invite_lines(), Build member-bot deep links for one khatm token. Returns an ordered dict keyed… (+2 more)

### Community 60 - "broadcast.py"
Cohesion: 0.18
Nodes (27): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, Creator message requests with mandatory admin moderation. (+19 more)

### Community 61 - "phone/service.py"
Cohesion: 0.05
Nodes (82): begin_phone_change(), ensure_creator_phone_verified(), FSMContext, Message, Return true when creation may continue; otherwise start the OTP step., receive_change_code(), receive_new_phone(), verify_creator_phone() (+74 more)

### Community 62 - "_wiz"
Cohesion: 0.19
Nodes (13): R1 (owner 2026-09-28): keep the wizard from cluttering the chat. Each new…, _wiz(), FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling… (+5 more)

### Community 63 - "test_admin_template_render.py"
Cohesion: 0.08
Nodes (25): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests… (+17 more)

### Community 64 - "Architecture Document"
Cohesion: 0.14
Nodes (18): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, No Business Rule Invention Rule, PayPing v3 Payment Gateway, Architecture Document, PayPing Setup Guide (Persian) (+10 more)

### Community 65 - "بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`"
Cohesion: 0.12
Nodes (16): R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**, R13. کمترین سؤال ممکن — اصل کلی هر دو بخش., R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک**, R5. تعهد = تعداد کلِ ختم (نه per-person) با دکمه‌ها — **کد + احتمالاً مایگریشن** (+8 more)

### Community 66 - "test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 67 - "Admin Panel Base Layout (base.html)"
Cohesion: 0.18
Nodes (18): Admin Panel Base Layout (base.html), components.html macros (tooltip), Glassmorphism Dark Design System, Permission-gated Admin Navigation, Admin Categories Page (categories.html), Creator Panel Base Layout (creator_base.html), Creator Panel i18n (t/lang) Localization, Creator Dashboard (creator_dashboard.html) (+10 more)

### Community 68 - "append_devotional_media_from_message"
Cohesion: 0.24
Nodes (10): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content() (+2 more)

### Community 69 - "DECISIONS"
Cohesion: 0.31
Nodes (10): DECISIONS, DEC-PY-0076 — Separate participant and creator menus, DEC-PY-0077 — Daily portions stack up, DEC-PY-0091 — Creation wizard no longer asks content format, DEC-PY-0092 — Rotating Quran allocation, DEC-PY-0093 — Creator bot has one fixed menu, starts creation directly, DEC-PY-0094 — Quran reading pace chosen by each member, DEC-PY-0095 — First Quran pages wait for chosen hour; automatic titles; OTP dedup (+2 more)

### Community 70 - "commitment.py"
Cohesion: 0.15
Nodes (21): CommitmentMode, is_regular_due(), log_count(), _minutes(), parse_hhmm(), datetime, str, R11 (owner 2026-09-28, revised after live QA): member-side commitment logic.… (+13 more)

### Community 71 - "DOMAIN_MODEL"
Cohesion: 0.15
Nodes (17): PayPing payment gateway, PendingPayment compare-and-swap replay protection, R11/N2 member commitment flow (regular/count), Codex Handoff — Next Steps, PayPing gateway activation (needs owner API token), DEC-PY-0068 — Kavenegar is first production SMS adapter, DEC-PY-0074 — Free-tier plan caps per-creator, admin-editable, DEC-PY-0090 — Fixed niyyat + optional niyabat (+9 more)

### Community 72 - "AsyncSession"
Cohesion: 0.19
Nodes (15): add_devotional_audio_variant(), add_devotional_image_page(), get_allowed_reciters(), get_effective_reciter(), _get_enabled_devotional_asset(), AsyncSession, Return an exact contiguous range, or None when any page is missing., Resolve all available media for one assigned Quran page range. The caller can… (+7 more)

### Community 73 - "get_khatm_stats"
Cohesion: 0.12
Nodes (16): deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Claim each eligible announcement once, then notify creator + active members., list_active_with_users(), ClosedMonthReport (+8 more)

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

### Community 80 - "message_template/repository.py"
Cohesion: 0.26
Nodes (13): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+5 more)

### Community 82 - "test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it"
Cohesion: 0.10
Nodes (17): KhatmInvitation, asyncio, integration, test_committed_quantity_today_vs_yesterday(), FakeMessage, FakeState, asyncio, integration (+9 more)

### Community 83 - "find_by_id"
Cohesion: 0.24
Nodes (12): _authorized_admin(), list_manual_phone_requests(), message, set_status(), ban(), demote_creator(), find_by_id(), promote_creator() (+4 more)

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

### Community 91 - "KhatmCategoryGroup"
Cohesion: 0.14
Nodes (21): _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, BotCategory, str, resolve_bot_category(), KhatmCategoryGroup, str, _creator_khatm_new_context() (+13 more)

### Community 92 - "test_dispatcher_routes_commands_while_profile_phone_state_is_active"
Cohesion: 0.18
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 93 - "test_recitation_text_only_for_laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 96 - "test_ad_reward_requires_opt_in_and_is_idempotent"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_ad_reward_requires_opt_in_and_is_idempotent()

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

### Community 110 - "AccountDeletionBlocked"
Cohesion: 0.50
Nodes (3): AccountDeletionBlocked, Exception, The account still owns an obligation that must be resolved first.

### Community 111 - "UserRole"
Cohesion: 0.14
Nodes (22): AuditLog, list_recent(), AsyncSession, Return a bounded newest-first timeline without exposing mutation APIs., record(), str, UserRole, asyncio (+14 more)

### Community 112 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 114 - "types"
Cohesion: 0.13
Nodes (13): contextlib, Regression for per-khatm broadcast targeting (owner request 2026-09-27):…, parametrize, test_parse_contribution_amount_accepts_localized_quran_ranges(), Regression: the creator reply-menu buttons «📊 گزارش و مالی» and «❓ راهنما و…, Regression: join_via_token used to NOT accept joined_via_bot_instance_id, so…, asyncio, test_custom_snooze_accepts_future_timezone_aware_time() (+5 more)

### Community 115 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 116 - "Feature checklist"
Cohesion: 0.25
Nodes (7): 1. Graphical creator Mini App khatm creation — DONE, 2. Real FREE → PRO purchase — DONE, 3. Configurable panel logo — DONE, 4. Reliable modern Persian panel font — IN-PROGRESS, Codex big features progress — 2026-09-29, Cross-feature validation and delivery log, Feature checklist

### Community 117 - "join_requests.py"
Cohesion: 0.19
Nodes (25): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, Creator approve/reject for a PRIVATE khatm's join request (DOMAIN_MODEL.md §2…, reject_join(), approve_leave() (+17 more)

### Community 118 - "test_creator_finance_and_support_buttons_are_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 121 - "test_set_font_size_validates_and_persists"
Cohesion: 0.32
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 123 - "devotional_seed.py"
Cohesion: 0.22
Nodes (8): logging, _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…

### Community 124 - "content/service.py"
Cohesion: 0.15
Nodes (13): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., decode_telegram_forward_ref(), get_quran_total_pages(), list_reciters(), parse_quran_channel_caption(), Quran media registry, reciter whitelist, and user delivery resolution., Total page count for a Quran khatm's edition. OPEN QURAN_PAGE khatms already… (+5 more)

### Community 126 - "asyncio"
Cohesion: 0.20
Nodes (7): asyncio, fixture, os, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 128 - "test_next_portion_is_withheld_until_next_local_day_at_reminder_hour"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 130 - "test_contribute_blocked_until_delivery_hour_set"
Cohesion: 0.15
Nodes (10): CustomSnooze, LogContribution, PauseCommitment, StatesGroup, Owner request (2026-09-21): the first time a non-committed (open or waitlisted)…, SetupOpenQuranReading, _callback_update(), asyncio (+2 more)

### Community 131 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 132 - "confirm_account_deletion"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

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

### Community 138 - "create_khatm.py"
Cohesion: 0.13
Nodes (24): _apply_coupon_code(), apply_creation_coupon(), ask_creation_coupon(), confirm_wizard(), _default_khatm_title(), _finish_creating_khatm(), CommandObject, Khatm creation wizard — a short multi-step conversation. Flow: **commitment… (+16 more)

### Community 140 - "test_salawat_category_group_always_goes_directly_to_mode"
Cohesion: 0.20
Nodes (3): _async_value(), asyncio, test_salawat_category_group_always_goes_directly_to_mode()

### Community 142 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

### Community 143 - "test_quran_join_is_member_controlled_without_auto_allocation"
Cohesion: 0.27
Nodes (6): asyncio, test_join_via_token_threads_bot_instance_id(), fake_get_khatm(), fake_join(), fake_resolve(), test_quran_join_is_member_controlled_without_auto_allocation()

### Community 145 - ".__call__"
Cohesion: 0.60
Nodes (4): _extract_chat_id(), Any, _reply_blocked(), TelegramObject

### Community 146 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.50
Nodes (4): Tooltip Jinja2 Macro Component, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 148 - "Multi-Bot Architecture (26 bots)"
Cohesion: 0.25
Nodes (8): Multi-Bot Architecture (26 bots), Multi-bot invite links (bot/invite_links.py), bot_instances table (encrypted tokens), DEC-PY-0080 — Multi-bot split (1 creator + 12 member bots per platform), Creator Bot (Multi-bot doc), dp_creator Dispatcher, dp_member Dispatcher, Task Report: Member Bot Category Attribute Fix

### Community 149 - "test_registration_starts_in_the_users_saved_language"
Cohesion: 0.08
Nodes (16): ProfileEdit, StatesGroup, StatesGroup, Registration, FakeMessage, FakeState, asyncio, integration (+8 more)

### Community 150 - "PROJECT_STATE"
Cohesion: 0.29
Nodes (8): PROJECT_STATE Archive (until 2026-09-18), DATABASE, Alembic migration workflow (reviewed, never blind autogenerate), Hand-written partial unique indexes, UUIDv7 app-generated primary keys, INDEX — Topical Documentation Map, PROJECT_STATE, Fresh-Postgres migration chain repair

### Community 151 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 152 - "Identity Across Platforms (phone-based merge key)"
Cohesion: 0.67
Nodes (3): Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 155 - "register_devotional_content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 158 - "bot/__init__.py"
Cohesion: 0.33
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 160 - "message_template/__init__.py"
Cohesion: 0.20
Nodes (6): Localized, versioned message templates., Template lookup and safe ``{{placeholder}}`` rendering., Real PostgreSQL coverage for template history and activation control., asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 168 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 176 - "register_devotional_content_batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 179 - "new_id"
Cohesion: 0.05
Nodes (40): new_id(), Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, asyncio, integration, test_delegated_admin_role_is_scoped_auditable_and_revocable(), test_non_super_admin_cannot_delegate_roles(), asyncio, integration (+32 more)

### Community 184 - "test_member_bot_fixes.py"
Cohesion: 0.25
Nodes (5): Regression for the 2026-09-29 member-bot fixes (owner live report): 1. Open-…, Owner report: pages/reminders stopped arriving on member bots. The old…, test_open_quran_hour_accepts_exact_time(), test_reminder_due_fires_at_or_after_target_not_only_in_window(), test_settings_creator_panel_button_visibility()

### Community 230 - "reminder_engine/service.py"
Cohesion: 0.07
Nodes (65): collections, SendQuranPagesFn, Positive khatm-completion announcements., has_started(), Return whether a scheduled khatm is allowed to deliver work yet., AsyncSession, render(), Scheduled positive personal monthly reports. (+57 more)

### Community 256 - "test_devotional_slug_link_does_not_depend_on_title_wording"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

## Knowledge Gaps
- **105 isolated node(s):** `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — DONE`, `4. Reliable modern Persian panel font — IN-PROGRESS`, `Cross-feature validation and delivery log` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1305 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **101 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `app.py`, `FSMContext`, `sqlalchemy`, `test_devotional_slug_link_does_not_depend_on_title_wording`, `confirm_account_deletion`, `t`, `KhatmTemplateType`, `admin.py`, `test_tapping_a_time_of_day_button_saves_the_hour_without_typing`, `Platform`, `create_khatm.py`, `DevotionalAsset`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `resume_join_after_registration`, `AdminFilter`, `authorization/service.py`, `advertising/service.py`, `.__call__`, `resolve_or_provision_user`, `Khatm`, `portions.py`, `User`, `test_registration_starts_in_the_users_saved_language`, `suggestions.py`, `register_devotional_content.py`, `PayPingGateway`, `wallet/service.py`, `panel.py`, `message_template/__init__.py`, `get_settings`, `member_commitment.py`, `bail_if_menu_button`, `PlanTier`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`, `register_devotional_content_batch2.py`, `handle_start_with_payload`, `payping_callback`, `new_id`, `deliver_devotional_media`, `safe_clear_inline_keyboard`, `wallet.py`, `QuranAssetKind`, `test_signed_telegram_admin_launch_sets_secure_scoped_cookie`, `finish_invite_links`, `broadcast.py`, `phone/service.py`, `test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour`, `append_devotional_media_from_message`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `message_template/repository.py`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `find_by_id`, `KhatmCategoryGroup`, `test_ad_reward_requires_opt_in_and_is_idempotent`, `test_health.py`, `UserRole`, `join_requests.py`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `app.py`, `FSMContext`, `confirm_account_deletion`, `KhatmTemplateType`, `test_public_khatms_reply_button_is_wired`, `Platform`, `create_khatm.py`, `session_scope`, `resume_join_after_registration`, `authorization/service.py`, `resolve_or_provision_user`, `portions.py`, `test_registration_starts_in_the_users_saved_language`, `suggestions.py`, `PayPingGateway`, `bot/__init__.py`, `panel.py`, `member_commitment.py`, `bail_if_menu_button`, `PlanTier`, `sms_subscription/service.py`, `test_creator_wallet_button_is_wired`, `handle_start_with_payload`, `deliver_devotional_media`, `safe_clear_inline_keyboard`, `wallet.py`, `test_member_bot_fixes.py`, `finish_invite_links`, `phone/service.py`, `test_admin_template_render.py`, `test_creator_contact.py`, `_commitment_total_keyboard`, `reminder_engine/service.py`, `join_requests.py`, `test_creator_finance_and_support_buttons_are_wired`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `app.py`, `FSMContext`, `sqlalchemy`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `confirm_account_deletion`, `t`, `admin.py`, `create_khatm.py`, `session_scope`, `resume_join_after_registration`, `AdminFilter`, `authorization/service.py`, `FakeMessage`, `resolve_or_provision_user`, `portions.py`, `User`, `test_registration_starts_in_the_users_saved_language`, `test_deep_link_clears_old_state_before_storing_new_join_context`, `suggestions.py`, `PayPingGateway`, `BotRegistry`, `panel.py`, `invite_links.py`, `get_settings`, `sqlalchemy_ext_asyncio`, `bail_if_menu_button`, `FakeMessage`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`, `handle_start_with_payload`, `new_id`, `deliver_devotional_media`, `safe_clear_inline_keyboard`, `wallet.py`, `test_notify_routing.py`, `test_signed_telegram_admin_launch_sets_secure_scoped_cookie`, `finish_invite_links`, `broadcast.py`, `phone/service.py`, `test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour`, `append_devotional_media_from_message`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `test_quran_setup_waits_for_selected_hour_before_sending`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `find_by_id`, `install_command_menu`, `UserRole`, `join_requests.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `t()` (e.g. with `test_both_panel_headers_support_configured_logo_and_fallback()` and `test_creator_detail_renders_manage_stats_members_export_and_settings()`) actually correct?**
  _`t()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 231 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 231 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `Khatm` (e.g. with `finish_invite_links()` and `send_other_language_links()`) actually correct?**
  _`Khatm` has 133 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — DONE` to the rest of the system?**
  _105 weakly-connected nodes found - possible documentation gaps or missing edges._