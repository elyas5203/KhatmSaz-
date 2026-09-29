# Graph Report - Khatm  (2026-09-29)

## Corpus Check
- 87 files · ~303,113 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3676 nodes · 12031 edges · 224 communities (141 shown, 83 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1435 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- app.py
- identity/service.py
- t()
- sqlalchemy
- create_khatm.py
- KhatmPortion
- my_khatms.py
- get_or_create()
- Platform
- User
- new_id()
- Participation
- start.py
- portions.py
- handle_member_start_with_payload()
- test_broadcast_target_picker.py
- phone/service.py
- panel.py
- sqlalchemy_ext_asyncio
- env.py
- khatm_workflow/service.py
- reminder_engine/service.py
- PayPingGateway
- settings_menu.py
- provider.py
- test_navigation_recovery.py
- datetime
- types
- typing
- sqlalchemy_dialects
- test_join_delivery_hour_ask_integration.
- wallet/service.py
- session_scope()
- wallet/models.py
- khatm_category/service.py
- plan/models.py
- join_requests.py
- Khatm
- sms_subscription/service.py
- bot_registry/service.py
- wallet/repository.py
- choose_gender()
- khatm/repository.py
- test_mini_app_auth_integration.py
- member_commitment.py
- test_ad_reward_requires_opt_in_and_is_id
- content/service.py
- ParticipationStatus
- khatm_request/models.py
- commitment.py
- alembic
- test_panel_redesign.py
- ensure_creator_phone_verified()
- creator_request/service.py
- DevotionalAsset
- broadcast/service.py
- main()
- creator_broadcast/service.py
- test_wizard_ephemeral.py
- test_i18n_audit.py
- Architecture Document
- monthly_report/service.py
- Admin Panel Base Layout (base.html)
- DOMAIN_MODEL
- test_registration_i18n_integration.py
- AsyncSession
- test_recitation_text_only_for_laan.py
- admin_approve_request()
- test_registration_phone_share_only.py
- suggestions.py
- KhatmStatus
- CHANGELOG
- creator_request/repository.py
- system_settings/repository.py
- KhatmSaz Project (Claude Code Instructio
- FakeState
- test_fresh_committed_quran_join_asks_del
- test_mini_app_entry.py
- test_quran_join_is_member_controlled_wit
- test_creator_contact.py
- BotRegistry
- notification/repository.py
- WaitingList
- KhatmSaz VPS Deployment Guide
- notification/service.py
- test_daily_digest_combines_multiple_khat
- Multi-Bot (26-bot) Architecture
- QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← 
- install_command_menu()
- BotCategory
- message_template/repository.py
- test_dispatcher_routes_commands_while_pr
- DECISIONS
- devotional_seed.py
- test_picking_a_reciter_via_settings_menu
- CSS Layouts and Responsive Design Guide
- _commitment_total_keyboard()
- invite_links.py
- runtime_status.py
- positional_range_for_step()
- message_template/__init__.py
- test_message_template.py
- Multi-Bot Architecture (26 bots)
- DECISIONS Archive (DEC-PY-0064 and earli
- Multi-Bot System (26-Bot Architecture)
- Member Bot Language Isolation (fixed per
- qr.py
- receive_media()
- test_quran_channel_source.py
- test_notification_snooze.py
- test_set_font_size_validates_and_persist
- Python Requirements
- DATABASE
- BotRegistry Singleton Class
- add_devotional_audio_variant()
- test_creator_notified_with_phone_after_t
- test_member_bot_scope.py
- notification/models.py
- test_deliver_due_next_portions_pushes_re
- test_completion_announcement_waits_is_id
- test_next_portion_is_withheld_until_next
- test_open_quran_reading_auto_delivers_on
- zzz_merge_three_heads_2026_09_28.py
- Mini-App Only Authentication Pattern
- Khatm Template → BotCategory Mapping
- Settings Menu Full-Button Test Scenario
- 435027907255_add_daily_deadline_hour_to_
- b7c8d9e0f1a2_add_bot_instances.py
- c21644dab334_add_skip_today_pause_and_le
- cf308fcab881_add_khatm_visibility.py
- set_audio_callback()
- receive_delivery_hour()
- Tooltip Jinja2 Macro Component
- test_devotional_category_navigation.py
- test_rotating_portion_stays_personal_whe
- test_previous_month_report_is_positive_l
- test_channel_coverage_counts_pages_not_s
- Bot Help Strings (Persian)
- Identity Across Platforms (phone-based m
- start_bot.ps1
- test_admin_can_search_khatms_by_title_cr
- test_devotional_slug_link_does_not_depen
- test_devotional_text_and_platform_specif
- test_active_categories_are_filtered_by_t
- test_template_version_toggle_falls_back_
- test_payping_callback_credits_once_and_r
- test_public_join_page_previews_without_j
- test_payment_intent_is_owned_single_use_
- claude_watchdog.sh
- web/__init__.py
- Persian-first, Simple UX Principle
- PROJECT_STATE Archive (until 2026-09-18)
- Debugging Guide
- Working-tree Git Diff (creator_request w
- PayPing v3 Payment Integration
- Quran Content Storage (Telegram channel-
- Redis (reserved for FSM / scheduler)
- 26-Bot Grid (1 creator + 12 member per p
- Creator Registration Flow (with OTP)
- Khatm Category Independent Families Test
- QA Handoff: Telegram Testing Guide for C
- khatmsaz_bot_handlers_start
- khatmsaz_core
- khatmsaz_i18n
- khatmsaz_modules_wallet
- khatmsaz_modules_wallet_gateway
- Module: audit_log
- Module: phone
- Module: plan
- Module: settings
- ValueError
- NotifyFn
- UUID
- Admins Management Page
- Audit Log Page
- Broadcasts Admin Page
- Operations/Health Admin Page
- Phone Verifications Admin Page
- Message Templates Admin Page

## God Nodes (most connected - your core abstractions)
1. `t()` - 350 edges
2. `session_scope()` - 227 edges
3. `Platform` - 191 edges
4. `new_id()` - 113 edges
5. `safe_answer_callback()` - 112 edges
6. `User` - 106 edges
7. `Khatm` - 92 edges
8. `Participation` - 86 edges
9. `Base` - 71 edges
10. `safe_clear_inline_keyboard()` - 69 edges

## Surprising Connections (you probably didn't know these)
- `پاسخ به سؤال کانال قرآن` --references--> `seed_verified_quran_channel_map()`  [INFERRED]
  docs/ai/QA_MATRIX.md → src/khatmsaz/modules/content/service.py
- `R8. ترتیب پلتفرم: «هر دو» بالا، بعد تلگرام، بعد بله — **بدون مایگریشن**` --references--> `choose_allowed_platforms()`  [INFERRED]
  docs/ai/REDESIGN_PLAN_2026-09-28.md → src/khatmsaz/bot/handlers/create_khatm.py
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
- **Bot User-Facing Content (help, welcome, khatm types)** — help_strings_txt_help_strings, welcome_txt_welcome_message, concept_khatm_types [INFERRED 0.85]
- **PayPing Payment Callback Flow** — docs_dns_cloudflare_fa_payping, rahnama_vps_reverseproxycallback, rahnama_vps_paypingverify [INFERRED 0.85]
- **Core Domain Modules (Khatm, Participation, Allocation, Workflow)** — module_khatm, module_participation, module_allocation, module_khatm_workflow, module_waiting_list [INFERRED 0.95]
- **Multi-bot architecture (dispatchers, bot_instances, invite links, creator bot)** — docs_ai_decisions_dec_py_0080_multibot_split, docs_ai_multibot_creator_bot_dp_creator, docs_ai_multibot_creator_bot_dp_member, docs_ai_decisions_bot_instances_table, docs_ai_changelog_invite_links_multibot [INFERRED 0.85]
- **Quran allocation evolution (rotating -> member-chosen -> wait-for-hour, bug + DB constraint)** — docs_ai_decisions_dec_py_0092_rotating_quran_allocation, docs_ai_decisions_dec_py_0094_member_chosen_quran_pace, docs_ai_decisions_dec_py_0095_first_pages_wait_hour, docs_ai_changelog_positional_range_for_step, docs_ai_qa_matrix_quran_page_allocation_bug [INFERRED 0.85]
- **Admin & creator panel redesign effort** — docs_ai_goal_panel_redesign_2026_09_29, docs_ai_project_state_panel_redesign, docs_ai_changelog_creator_wallet_button, docs_ai_decisions_dec_py_0073_mini_apps [INFERRED 0.75]
- **Redesigned Creator Panel (base, dashboard, khatms, detail, wallet)** — src_khatmsaz_web_templates_creator_base_creator_layout, src_khatmsaz_web_templates_creator_dashboard_creator_dashboard, src_khatmsaz_web_templates_creator_khatms_creator_khatms, src_khatmsaz_web_templates_creator_khatm_detail_creator_khatm_detail, src_khatmsaz_web_templates_creator_wallet_creator_wallet [INFERRED 0.85]
- **Admin Panel (base, dashboard, categories, devotionals, finance, creator_requests)** — src_khatmsaz_web_templates_base_base_layout, src_khatmsaz_web_templates_dashboard_admin_dashboard, src_khatmsaz_web_templates_categories_categories_page, src_khatmsaz_web_templates_devotionals_devotionals_page, src_khatmsaz_web_templates_finance_finance_page, src_khatmsaz_web_templates_creator_requests_creator_requests [INFERRED 0.85]

## Communities (224 total, 83 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.05
Nodes (118): AdminPermission, fastapi, fastapi_responses, fastapi_staticfiles, fastapi_templating, get, HTMLResponse, middleware (+110 more)

### Community 1 - "identity/service.py"
Cohesion: 0.06
Nodes (65): aiogram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types, apscheduler_schedulers_asyncio, BaseFilter, functools (+57 more)

### Community 2 - "t()"
Cohesion: 0.05
Nodes (101): base64, InlineKeyboardButton, khatmsaz_bot_handlers_help, _confirm_keyboard(), InlineKeyboardMarkup, message, request_account_deletion(), help_command() (+93 more)

### Community 3 - "sqlalchemy"
Cohesion: 0.07
Nodes (42): httpx, khatmsaz_modules_khatm_category, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl, pytest, re, sqlalchemy (+34 more)

### Community 4 - "create_khatm.py"
Cohesion: 0.10
Nodes (90): C. ساخت ۴ نوع ختم, R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), KhatmCategoryGroup, _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome() (+82 more)

### Community 5 - "KhatmPortion"
Cohesion: 0.08
Nodes (81): AllocationStrategy, CommittedQuantityLog, KhatmAllocationPlan, KhatmPortion, PortionStatus, PortionUnitKind, Base, str (+73 more)

### Community 6 - "my_khatms.py"
Cohesion: 0.07
Nodes (79): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at() (+71 more)

### Community 7 - "get_or_create()"
Cohesion: 0.05
Nodes (76): CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), _lang_for(), CommandObject, message (+68 more)

### Community 8 - "Platform"
Cohesion: 0.11
Nodes (75): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+67 more)

### Community 9 - "User"
Cohesion: 0.06
Nodes (70): AdminRole, AdminRoleGrant, CapabilityType, str, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession (+62 more)

### Community 10 - "new_id()"
Cohesion: 0.05
Nodes (68): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), CoverStatus, KhatmScheduleKind, KhatmTemplateType, KhatmTypeEnum (+60 more)

### Community 11 - "Participation"
Cohesion: 0.07
Nodes (66): leave_khatm(), Leave a khatm. If the leaver was a committed participant, promote the next…, Apply the creator's Q77 decision to a committed Quran participant. ``continue``…, resolve_missed_commitment(), Assignment, Participation, Base, The Phase-4 flat per-khatm assignment (legacy shape, kept for parity). The… (+58 more)

### Community 12 - "start.py"
Cohesion: 0.06
Nodes (63): D. دعوت و عضویت, عضو (Member bots) — تلگرام fa/ar/en و بله, Kick off the mode picker for a freshly-joined commitment member., start_commitment_mode_picker(), handle_member_cancel(), handle_member_join_callback(), handle_member_start(), callback_query (+55 more)

### Community 13 - "portions.py"
Cohesion: 0.08
Nodes (63): list_member_khatms(), callback_query, CallbackQuery, FSMContext, message, Member bot "My Khatms" handler — lists khatms the user joined via this bot…, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow… (+55 more)

### Community 14 - "handle_member_start_with_payload()"
Cohesion: 0.06
Nodes (55): R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**, R13. کمترین سؤال ممکن — اصل کلی هر دو بخش., R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک** (+47 more)

### Community 15 - "test_broadcast_target_picker.py"
Cohesion: 0.04
Nodes (35): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_enums, aiogram_fsm_storage_memory, contextlib, Bale Bot instance factory. Bale's bot platform speaks a Telegram-compatible Bot…, MemberRegistration (+27 more)

### Community 16 - "phone/service.py"
Cohesion: 0.09
Nodes (56): OtpChallenge, PhoneClaim, sqlalchemy_exc, receive_new_phone(), decide_manual_phone_request(), callback_query, CallbackQuery, approve() (+48 more)

### Community 17 - "panel.py"
Cohesion: 0.07
Nodes (50): Live QA — 2026-09-28 (Chrome / Telegram Web / Codex), QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), رفع‌شدهٔ همین عصر (Claude Code), سازنده (Creator) — تلگرام (+42 more)

### Community 18 - "sqlalchemy_ext_asyncio"
Cohesion: 0.08
Nodes (40): sqlalchemy_ext_asyncio, Append-only audit trail for sensitive administrative actions., AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module., Return a bounded newest-first timeline without exposing mutation APIs., record() (+32 more)

### Community 19 - "env.py"
Cohesion: 0.05
Nodes (27): asyncio, fixture, logging_config, do_run_migrations(), run_migrations_online(), os, build_body(), main() (+19 more)

### Community 20 - "khatm_workflow/service.py"
Cohesion: 0.08
Nodes (42): ContentDeliveryMode, CreatorDisplayMode, KhatmTypeEnum, KhatmVisibility, ReminderTone, approve_join_request(), cancel_khatm(), _complete_join() (+34 more)

### Community 21 - "reminder_engine/service.py"
Cohesion: 0.12
Nodes (39): collections, NotificationKind, NotifyFn, SendQuranPagesFn, list_assigned_positional_portions(), Positive khatm-completion announcements., Scheduled positive personal monthly reports., get_by_id() (+31 more)

### Community 22 - "PayPingGateway"
Cohesion: 0.10
Nodes (22): Response, GatewayError, PaymentGateway, PaymentRequest, PaymentVerification, Exception, Protocol, Gateway boundary; PSP-specific code must live behind this protocol. (+14 more)

### Community 23 - "settings_menu.py"
Cohesion: 0.13
Nodes (40): begin_account_link(), _lang_for(), FSMContext, message, receive_link_code(), receive_link_phone(), message, set_reminder() (+32 more)

### Community 24 - "provider.py"
Cohesion: 0.10
Nodes (28): BaseSettings, dataclasses, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient (+20 more)

### Community 25 - "test_navigation_recovery.py"
Cohesion: 0.09
Nodes (16): khatmsaz_bot_handlers, FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu() (+8 more)

### Community 26 - "datetime"
Cohesion: 0.12
Nodes (20): datetime, DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's… (+12 more)

### Community 27 - "types"
Cohesion: 0.07
Nodes (18): khatmsaz_core_bot_registry, khatmsaz_modules_bot_registry_models, khatmsaz_modules_identity, ChangePhone, StatesGroup, FakeMessage, FakeState, asyncio (+10 more)

### Community 28 - "typing"
Cohesion: 0.05
Nodes (4): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 30 - "test_join_delivery_hour_ask_integration."
Cohesion: 0.14
Nodes (26): khatmsaz_bot_handlers_join_flow, khatmsaz_core_db, khatmsaz_core_ids, khatmsaz_core_security, khatmsaz_modules_allocation, khatmsaz_modules_identity_models, khatmsaz_modules_invitation, khatmsaz_modules_invitation_models (+18 more)

### Community 31 - "wallet/service.py"
Cohesion: 0.11
Nodes (35): CouponDiscountType, DiscountCoupon, get_coupon(), upsert_coupon(), cleanup_expired_pending_payments(), _coupon_discount(), create_payment_intent(), get_balances() (+27 more)

### Community 32 - "session_scope()"
Cohesion: 0.09
Nodes (34): Any, CallbackQuery, Message, cancel_account_deletion(), confirm_account_deletion(), _lang_for(), callback_query, CallbackQuery (+26 more)

### Community 33 - "wallet/models.py"
Cohesion: 0.11
Nodes (33): AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., accrue_first_completed_action(), get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., Grant one reward only after the first completed assigned action. The… (+25 more)

### Community 34 - "khatm_category/service.py"
Cohesion: 0.20
Nodes (30): KhatmCategory, KhatmCategoryGroup, KhatmCategoryRequest, KhatmCategoryRequestStatus, str, Admin-managed content library for independent devotional families. Owner…, A participant's typed request for a دعا that isn't in the library yet (owner…, create() (+22 more)

### Community 35 - "plan/models.py"
Cohesion: 0.14
Nodes (30): PlanDefinition, PlanTier, PricingMode, str, Plan module: assigned plan tier per user (FREE / BASIC / PRO). Missing row…, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user() (+22 more)

### Community 36 - "join_requests.py"
Cohesion: 0.14
Nodes (30): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, Creator approve/reject for a PRIVATE khatm's join request (DOMAIN_MODEL.md §2…, reject_join(), approve_leave() (+22 more)

### Community 37 - "Khatm"
Cohesion: 0.17
Nodes (31): Khatm, get_by_id(), update_cosmetic(), close_due_khatms(), complete_khatm(), create_draft_khatm(), has_started(), list_my_created() (+23 more)

### Community 38 - "sms_subscription/service.py"
Cohesion: 0.14
Nodes (29): Time-limited SMS reminder subscriptions (owner request, 2026-09-20). SMS…, Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options() (+21 more)

### Community 39 - "bot_registry/service.py"
Cohesion: 0.17
Nodes (29): cryptography_fernet, Fernet, BotInstance, BotRole, get_by_id(), get_by_slot(), list_active(), list_active_members() (+21 more)

### Community 40 - "wallet/repository.py"
Cohesion: 0.14
Nodes (30): CouponRedemption, InvoiceStatus, PendingPayment, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, Immutable purchase amounts plus a small paid/refunded lifecycle., WalletInvoice, bind_invoice_resource(), claim_pending_payment() (+22 more)

### Community 41 - "choose_gender()"
Cohesion: 0.12
Nodes (29): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), callback_query, CallbackQuery, FSMContext (+21 more)

### Community 42 - "khatm/repository.py"
Cohesion: 0.13
Nodes (27): deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Claim each eligible announcement once, then notify creator + active members., KhatmVisibility, claim_completion_announcement() (+19 more)

### Community 43 - "test_mini_app_auth_integration.py"
Cohesion: 0.13
Nodes (23): hashlib, hmac, json, InvalidTelegramInitData, datetime, ValueError, Validation for Telegram Mini App signed launch data., The launch data is malformed, stale, or has an invalid signature. (+15 more)

### Community 44 - "member_commitment.py"
Cohesion: 0.23
Nodes (26): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), CommitFlow, enter_count(), enter_custom_time() (+18 more)

### Community 45 - "test_ad_reward_requires_opt_in_and_is_id"
Cohesion: 0.11
Nodes (23): OpenContribution, create(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+15 more)

### Community 46 - "content/service.py"
Cohesion: 0.13
Nodes (22): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), get_quran_total_pages(), parse_quran_channel_caption(), quran_channel_coverage() (+14 more)

### Community 47 - "ParticipationStatus"
Cohesion: 0.12
Nodes (19): AccountDeletionBlocked, delete_account(), Exception, Safely deactivate a user while retaining non-PII history. Active committed…, The account still owns an obligation that must be resolved first., AssignmentStatus, AssignmentUnitKind, ParticipationStatus (+11 more)

### Community 48 - "khatm_request/models.py"
Cohesion: 0.20
Nodes (20): KhatmRequest, KhatmRequestStatus, str, Khatm-request module: a creator asking for a khatm type not in the picker yet…, create(), get_by_id(), list_pending(), AsyncSession (+12 more)

### Community 49 - "commitment.py"
Cohesion: 0.15
Nodes (21): CommitmentMode, is_regular_due(), log_count(), _minutes(), parse_hhmm(), datetime, str, R11 (owner 2026-09-28, revised after live QA): member-side commitment logic.… (+13 more)

### Community 51 - "test_panel_redesign.py"
Cohesion: 0.12
Nodes (15): importlib_util, khatmsaz_bot, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_has_presets_and_custom(), test_hour_keyboard_prefix_matches_handler() (+7 more)

### Community 52 - "ensure_creator_phone_verified()"
Cohesion: 0.15
Nodes (22): begin_phone_change(), ensure_creator_phone_verified(), _lang_for(), FSMContext, Message, Return true when creation may continue; otherwise start the OTP step., receive_change_code(), verify_creator_phone() (+14 more)

### Community 53 - "creator_request/service.py"
Cohesion: 0.14
Nodes (20): handle_creator_request_button(), callback_query, CallbackQuery, Creator-request module: manages requests from users who want to become khatm…, AlreadyCreatorError, approve_request(), has_pending_request(), list_pending() (+12 more)

### Community 54 - "DevotionalAsset"
Cohesion: 0.13
Nodes (22): deliver_devotional_media(), callback_query, CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional() (+14 more)

### Community 55 - "broadcast/service.py"
Cohesion: 0.26
Nodes (19): BroadcastStatus, KhatmBroadcast, str, Moderated creator messages for a khatm., create(), get_by_id(), list_pending(), mark_reviewed() (+11 more)

### Community 56 - "main()"
Cohesion: 0.15
Nodes (19): _build_member_bots(), _configure_logging(), main(), _run_reminder_scan(), Bot, _tag_bot(), build_bale_bot(), Bot (+11 more)

### Community 57 - "creator_broadcast/service.py"
Cohesion: 0.21
Nodes (19): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+11 more)

### Community 58 - "test_wizard_ephemeral.py"
Cohesion: 0.21
Nodes (11): FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_can_keep_intro_beside_title_until_answered(), test_wiz_deletes_previous_prompt() (+3 more)

### Community 59 - "test_i18n_audit.py"
Cohesion: 0.11
Nodes (12): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather than a…, The dict literal must not define the same key twice (Python would keep only the…, test_no_duplicate_keys_in_source() (+4 more)

### Community 60 - "Architecture Document"
Cohesion: 0.13
Nodes (19): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, No Business Rule Invention Rule, PayPing v3 Payment Gateway, Architecture Document, Original Full Project Spec (Persian) (+11 more)

### Community 61 - "monthly_report/service.py"
Cohesion: 0.16
Nodes (15): BaseMiddleware, collections_abc, _extract_chat_id(), ModerationMiddleware, Any, Bot-wide moderation gate: a SUSPENDED/BANNED user gets a single friendly…, _reply_blocked(), deliver_due() (+7 more)

### Community 62 - "Admin Panel Base Layout (base.html)"
Cohesion: 0.18
Nodes (18): Admin Panel Base Layout (base.html), components.html macros (tooltip), Glassmorphism Dark Design System, Permission-gated Admin Navigation, Admin Categories Page (categories.html), Creator Panel Base Layout (creator_base.html), Creator Panel i18n (t/lang) Localization, Creator Dashboard (creator_dashboard.html) (+10 more)

### Community 63 - "DOMAIN_MODEL"
Cohesion: 0.16
Nodes (16): PayPing payment gateway, PendingPayment compare-and-swap replay protection, R11/N2 member commitment flow (regular/count), Codex Handoff — Next Steps, PayPing gateway activation (needs owner API token), DEC-PY-0068 — Kavenegar is first production SMS adapter, DEC-PY-0074 — Free-tier plan caps per-creator, admin-editable, DEC-PY-0090 — Fixed niyyat + optional niyabat (+8 more)

### Community 64 - "test_registration_i18n_integration.py"
Cohesion: 0.13
Nodes (10): khatmsaz_modules_settings_models, ProfileEdit, StatesGroup, FakeMessage, FakeState, asyncio, integration, parametrize (+2 more)

### Community 65 - "AsyncSession"
Cohesion: 0.15
Nodes (17): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., get_allowed_reciters(), get_effective_reciter(), list_all_devotional_assets(), AsyncSession, Return an exact contiguous range, or None when any page is missing., Resolve all available media for one assigned Quran page range. The caller can… (+9 more)

### Community 66 - "test_recitation_text_only_for_laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 67 - "admin_approve_request()"
Cohesion: 0.23
Nodes (16): admin_approve_request(), admin_reject_request(), _lang_for(), callback_query, CallbackQuery, CommandObject, FSMContext, Message (+8 more)

### Community 68 - "test_registration_phone_share_only.py"
Cohesion: 0.18
Nodes (8): StatesGroup, Registration, FakeMessage, FakeState, asyncio, Owner request (2026-09-22): during initial registration on Telegram, only the…, test_bale_typed_phone_is_still_accepted_during_registration(), test_telegram_typed_phone_is_rejected_during_registration()

### Community 69 - "suggestions.py"
Cohesion: 0.27
Nodes (15): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, StatesGroup, User feedback/bug-report inbox to admins (owner request, 2026-09-21). Updated… (+7 more)

### Community 70 - "KhatmStatus"
Cohesion: 0.14
Nodes (16): KhatmStatus, set_status(), activate_khatm(), cancel_khatm(), asyncio, integration, test_open_khatm_schedule_validation_and_due_rules(), asyncio (+8 more)

### Community 71 - "CHANGELOG"
Cohesion: 0.15
Nodes (15): CHANGELOG Archive (until 2026-09-18), CHANGELOG, Creator wallet-charge button, Devotional content library + seed, i18n coverage guard (fa/ar/en), positional_range_for_step (rotating allocation helper), Reminder engine (APScheduler scan), DEC-PY-0072 — Devotional families are independent top-level choices (+7 more)

### Community 72 - "creator_request/repository.py"
Cohesion: 0.34
Nodes (14): CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user(), list_pending() (+6 more)

### Community 73 - "system_settings/repository.py"
Cohesion: 0.24
Nodes (11): Generic admin-editable key/value store for small system-wide numeric defaults…, SystemSetting, get(), list_all(), AsyncSession, set(), get_int(), list_current() (+3 more)

### Community 74 - "KhatmSaz Project (Claude Code Instructio"
Cohesion: 0.20
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), Admin Mini App (Telegram WebApp), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), Admin Mini App Guide (Persian), AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 75 - "FakeState"
Cohesion: 0.14
Nodes (6): FakeCallback, FakeMessage, FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 76 - "test_fresh_committed_quran_join_asks_del"
Cohesion: 0.18
Nodes (7): FakeMessage, FakeState, asyncio, integration, R11 supersedes the old bare delivery-hour question for repetitions., test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it(), test_fresh_committed_salawat_join_asks_commitment_mode()

### Community 77 - "test_mini_app_entry.py"
Cohesion: 0.20
Nodes (12): _message(), asyncio, Fail-closed behavior before a public HTTPS Mini App origin exists., test_admin_mini_app_rejects_local_http_origin(), test_creator_mini_app_rejects_local_http_origin_before_database_access(), test_panel_buttons_request_chat_entry_before_opening_mini_app(), asyncio, Fast safety checks for pending-payment expiry and replay behavior. (+4 more)

### Community 78 - "test_quran_join_is_member_controlled_wit"
Cohesion: 0.21
Nodes (8): khatmsaz_modules_khatm_workflow, asyncio, Regression: join_via_token used to NOT accept joined_via_bot_instance_id, so…, test_join_via_token_threads_bot_instance_id(), fake_get_khatm(), fake_join(), fake_resolve(), test_quran_join_is_member_controlled_without_auto_allocation()

### Community 79 - "test_creator_contact.py"
Cohesion: 0.22
Nodes (12): _compose_welcome_with_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/…, test_compose_appends_contact_line_to_welcome(), test_compose_contact_only_when_no_welcome(), test_compose_none_contact_passes_welcome_through() (+4 more)

### Community 80 - "BotRegistry"
Cohesion: 0.26
Nodes (5): BotRegistry, Bot, UUID, Runtime registry of all live Bot instances, built once at startup., set_registry()

### Community 81 - "notification/repository.py"
Cohesion: 0.38
Nodes (12): NotificationKind, NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession (+4 more)

### Community 82 - "WaitingList"
Cohesion: 0.27
Nodes (10): WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next(), AsyncSession (+2 more)

### Community 83 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.21
Nodes (12): Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File, GitHub-based Deployment (git pull), /health Endpoint (DB check) (+4 more)

### Community 84 - "notification/service.py"
Cohesion: 0.29
Nodes (11): _save_delivery_time(), already_sent_today(), get_preference(), AsyncSession, datetime, Notification business logic: dedup a reminder/miss send against "already sent…, record_sent(), set_reminder_preference() (+3 more)

### Community 85 - "test_daily_digest_combines_multiple_khat"
Cohesion: 0.17
Nodes (5): asyncio, test_daily_digest_combines_multiple_khatms_for_one_user(), asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 86 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.20
Nodes (11): Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers), Member Bots & Language Isolation, Multi-Bot (26-bot) Architecture, Notification Routing (+3 more)

### Community 87 - "QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← "
Cohesion: 0.18
Nodes (11): A. زیرساخت چندبات (۲۶ بات), B. ثبت‌نام, E. سهم و یادآوری, F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات, G. زبان‌ها (fa/ar/en), H. پرداخت, I. Mini App + پنل ادمین, QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه) (+3 more)

### Community 88 - "install_command_menu()"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 89 - "BotCategory"
Cohesion: 0.29
Nodes (9): _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, BotCategory, str, R2 (owner 2026-09-28): per-bot intro image shown after the creator picks…, test_dua_group_maps_to_dua_ziyarat_bot(), test_laan_group_maps_to_laan_bot(), test_quran_maps_to_quran_bot() (+1 more)

### Community 90 - "message_template/repository.py"
Cohesion: 0.38
Nodes (10): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+2 more)

### Community 91 - "test_dispatcher_routes_commands_while_pr"
Cohesion: 0.18
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 92 - "DECISIONS"
Cohesion: 0.31
Nodes (10): DECISIONS, DEC-PY-0076 — Separate participant and creator menus, DEC-PY-0077 — Daily portions stack up, DEC-PY-0091 — Creation wizard no longer asks content format, DEC-PY-0092 — Rotating Quran allocation, DEC-PY-0093 — Creator bot has one fixed menu, starts creation directly, DEC-PY-0094 — Quran reading pace chosen by each member, DEC-PY-0095 — First Quran pages wait for chosen hour; automatic titles; OTP dedup (+2 more)

### Community 93 - "devotional_seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 94 - "test_picking_a_reciter_via_settings_menu"
Cohesion: 0.24
Nodes (6): FakeCallback, FakeMessage, asyncio, integration, test_picking_a_reciter_via_settings_menu_turns_on_audio(), test_picking_a_reciter_via_typed_command_turns_on_audio()

### Community 95 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 96 - "_commitment_total_keyboard()"
Cohesion: 0.25
Nodes (8): _commitment_total_keyboard(), _creator_contact_keyboard(), InlineKeyboardMarkup, R4 (owner 2026-09-28): the creator MUST provide a contact so members can reach…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited()

### Community 97 - "invite_links.py"
Cohesion: 0.22
Nodes (8): format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Render member-bot links as a readable, multi-line Persian block., Choose one link to encode in a QR: prefer the creator's language and platform,…, resolve_khatm_category_value(), resolve_bot_category()

### Community 98 - "runtime_status.py"
Cohesion: 0.25
Nodes (5): mark_scan_failed(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins.

### Community 99 - "positional_range_for_step()"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 100 - "message_template/__init__.py"
Cohesion: 0.22
Nodes (6): Localized, versioned message templates., AsyncSession, Template lookup and safe ``{{placeholder}}`` rendering., Reject malformed or unsupported placeholders before a template is stored., render(), validate_body()

### Community 101 - "test_message_template.py"
Cohesion: 0.28
Nodes (6): asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 102 - "Multi-Bot Architecture (26 bots)"
Cohesion: 0.25
Nodes (8): Multi-Bot Architecture (26 bots), Multi-bot invite links (bot/invite_links.py), bot_instances table (encrypted tokens), DEC-PY-0080 — Multi-bot split (1 creator + 12 member bots per platform), Creator Bot (Multi-bot doc), dp_creator Dispatcher, dp_member Dispatcher, Task Report: Member Bot Category Attribute Fix

### Community 103 - "DECISIONS Archive (DEC-PY-0064 and earli"
Cohesion: 0.25
Nodes (8): DEC-PY-0057 Internal Invoice For Every Purchase, DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Invite Links & Token Resolution, PayPing v3 Adapter Integration, PayPing Server-to-Server Verify, PayPing Callback Reverse Proxy

### Community 104 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.32
Nodes (8): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Web Landing Page /join/{token} Multi-Bot Updates, Multi-Bot System (26-Bot Architecture)

### Community 105 - "Member Bot Language Isolation (fixed per"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 106 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 107 - "receive_media()"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 108 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 109 - "test_notification_snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 110 - "test_set_font_size_validates_and_persist"
Cohesion: 0.32
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 111 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 112 - "DATABASE"
Cohesion: 0.33
Nodes (7): DATABASE, Alembic migration workflow (reviewed, never blind autogenerate), Hand-written partial unique indexes, UUIDv7 app-generated primary keys, INDEX — Topical Documentation Map, PROJECT_STATE, Fresh-Postgres migration chain repair

### Community 113 - "BotRegistry Singleton Class"
Cohesion: 0.29
Nodes (7): Admin Token Panel /bots Route (2-step confirmation), Restart Requirement After Token Change, bot_instances Database Table, BotRegistry Singleton Class, Fernet Token Encryption for Bot Tokens, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow

### Community 114 - "add_devotional_audio_variant()"
Cohesion: 0.29
Nodes (7): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.…, Owner request (2026-09-22): a dua's image can span more than one page…, Owner request (2026-09-22): a dua's full text as a PDF document — one slot per…, set_devotional_pdf()

### Community 115 - "test_creator_notified_with_phone_after_t"
Cohesion: 0.38
Nodes (6): asyncio, integration, Owner decision (2026-09-22): creator notification must include member's phone…, test_creator_notified_only_after_threshold_and_member_never_notified(), fake_notify(), test_creator_notified_with_phone_after_two_consecutive_missed_days()

### Community 116 - "test_member_bot_scope.py"
Cohesion: 0.48
Nodes (5): _bot(), asyncio, test_devotional_families_do_not_cross_member_bots(), test_member_participation_is_strictly_limited_to_current_bot_instance(), test_quran_khatm_never_appears_in_dua_bot()

### Community 117 - "notification/models.py"
Cohesion: 0.40
Nodes (5): JobStatus, NotifChannel, NotificationJob, str, Notification module: scheduled reminder jobs, per-participation preferences,…

### Community 118 - "test_deliver_due_next_portions_pushes_re"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_deliver_due_next_portions_pushes_real_content_not_just_text()

### Community 119 - "test_completion_announcement_waits_is_id"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 120 - "test_next_portion_is_withheld_until_next"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 121 - "test_open_quran_reading_auto_delivers_on"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 122 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 123 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 124 - "Khatm Template → BotCategory Mapping"
Cohesion: 0.50
Nodes (4): resolve_bot_category() Function, Token Resolution on Member Bot (category validation), Member Bot /start Behavior (with/without deep link), Khatm Template → BotCategory Mapping

### Community 125 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 130 - "set_audio_callback()"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 131 - "receive_delivery_hour()"
Cohesion: 0.50
Nodes (4): _parse_delivery_time(), message, Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., receive_delivery_hour()

### Community 132 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.50
Nodes (4): Tooltip Jinja2 Macro Component, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 133 - "test_devotional_category_navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 134 - "test_rotating_portion_stays_personal_whe"
Cohesion: 0.50
Nodes (3): asyncio, integration, test_rotating_portion_stays_personal_when_member_is_inactive()

### Community 135 - "test_previous_month_report_is_positive_l"
Cohesion: 0.50
Nodes (3): asyncio, integration, test_previous_month_report_is_positive_localized_and_sent_once()

### Community 136 - "test_channel_coverage_counts_pages_not_s"
Cohesion: 0.67
Nodes (4): asyncio, integration, test_channel_coverage_counts_pages_not_source_posts(), test_channel_range_registry_is_idempotent_and_resolves_shared_audio()

### Community 137 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 138 - "Identity Across Platforms (phone-based m"
Cohesion: 0.67
Nodes (3): Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 181 - "test_admin_can_search_khatms_by_title_cr"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_admin_can_search_khatms_by_title_creator_and_uuid()

### Community 182 - "test_devotional_slug_link_does_not_depen"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

### Community 183 - "test_devotional_text_and_platform_specif"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 184 - "test_active_categories_are_filtered_by_t"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_active_categories_are_filtered_by_the_selected_parent_family()

### Community 185 - "test_template_version_toggle_falls_back_"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_template_version_toggle_falls_back_to_previous_enabled_version()

### Community 186 - "test_payping_callback_credits_once_and_r"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_payping_callback_credits_once_and_replay_is_idempotent()

### Community 187 - "test_public_join_page_previews_without_j"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_public_join_page_previews_without_joining_and_rejects_cancelled_link()

### Community 188 - "test_payment_intent_is_owned_single_use_"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_payment_intent_is_owned_single_use_and_amount_bound()

## Knowledge Gaps
- **102 isolated node(s):** `R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**`, `R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**`, `R13. کمترین سؤال ممکن — اصل کلی هر دو بخش.`, `R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**`, `R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n)` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1245 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **83 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t()` to `app.py`, `identity/service.py`, `receive_delivery_hour()`, `create_khatm.py`, `my_khatms.py`, `get_or_create()`, `start.py`, `portions.py`, `handle_member_start_with_payload()`, `test_broadcast_target_picker.py`, `phone/service.py`, `panel.py`, `env.py`, `reminder_engine/service.py`, `settings_menu.py`, `session_scope()`, `join_requests.py`, `choose_gender()`, `member_commitment.py`, `test_panel_redesign.py`, `ensure_creator_phone_verified()`, `creator_request/service.py`, `DevotionalAsset`, `test_registration_i18n_integration.py`, `admin_approve_request()`, `suggestions.py`, `test_creator_contact.py`, `_commitment_total_keyboard()`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `Architecture Document` connect `Architecture Document` to `identity/service.py`, `KhatmSaz Project (Claude Code Instructio`, `Multi-Bot Architecture (26 bots)`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `session_scope()` connect `session_scope()` to `identity/service.py`, `t()`, `sqlalchemy`, `my_khatms.py`, `get_or_create()`, `Platform`, `User`, `new_id()`, `test_previous_month_report_is_positive_l`, `start.py`, `test_channel_coverage_counts_pages_not_s`, `handle_member_start_with_payload()`, `phone/service.py`, `sqlalchemy_ext_asyncio`, `env.py`, `wallet/models.py`, `plan/models.py`, `join_requests.py`, `wallet/repository.py`, `choose_gender()`, `test_mini_app_auth_integration.py`, `test_ad_reward_requires_opt_in_and_is_id`, `content/service.py`, `khatm_request/models.py`, `creator_request/service.py`, `DevotionalAsset`, `test_devotional_slug_link_does_not_depen`, `main()`, `creator_broadcast/service.py`, `test_devotional_text_and_platform_specif`, `test_active_categories_are_filtered_by_t`, `test_template_version_toggle_falls_back_`, `monthly_report/service.py`, `test_payping_callback_credits_once_and_r`, `test_payment_intent_is_owned_single_use_`, `admin_approve_request()`, `suggestions.py`, `KhatmStatus`, `notification/service.py`, `test_daily_digest_combines_multiple_khat`, `test_picking_a_reciter_via_settings_menu`, `receive_media()`, `test_completion_announcement_waits_is_id`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `t()` (e.g. with `test_creator_detail_renders_manage_stats_members_export_and_settings()` and `test_help_is_complete_and_button_driven()`) actually correct?**
  _`t()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 148 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 148 INFERRED edges - model-reasoned connections that need verification._
- **What connects `R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**`, `R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**`, `R13. کمترین سؤال ممکن — اصل کلی هر دو بخش.` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053806451612903226 - nodes in this community are weakly interconnected._