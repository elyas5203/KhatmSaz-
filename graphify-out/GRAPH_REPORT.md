# Graph Report - Khatm  (2026-09-30)

## Corpus Check
- 461 files · ~334,078 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 4019 nodes · 14246 edges · 288 communities (171 shown, 117 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 2116 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9e13495`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- wallet/service.py
- sqlalchemy
- keyboards.py
- create_khatm.py
- identity/service.py
- .__call__
- _build_my_khatms_tree
- db.py
- phone/service.py
- portions.py
- new_id
- reminder_engine/service.py
- KhatmTemplateType
- t
- Khatm
- User
- _authenticate_telegram_mini_app
- session_scope
- resolve_or_provision_user
- panel.py
- typing
- sqlalchemy_dialects
- Participation
- registration.py
- content/service.py
- AdminPermission
- OWNER_SPEC_MASTER.md
- alembic
- KhatmPortion
- PayPingGateway
- test_deep_link_clears_old_state_before_storing_new_join_context
- safe_answer_callback
- admin_approve_request
- test_admin_template_render.py
- leave.py
- Session
- profile.py
- creator_request/service.py
- KhatmCategory
- provider.py
- DevotionalAsset
- wallet/repository.py
- test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it
- sms_subscription/service.py
- broadcast/service.py
- commitment.py
- UserRole
- test_home_menu.py
- بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`
- test_early_regular_share_waits_for_done_before_consuming_schedule
- notification/service.py
- plan/repository.py
- member_commitment.py
- plan/service.py
- test_registration_starts_in_the_users_saved_language
- content/__init__.py
- message_template/repository.py
- KhatmSaz VPS Deployment Guide
- test_wizard_ephemeral.py
- bot_registry/service.py
- test_contribute_blocked_until_delivery_hour_set
- datetime
- open_contribution/repository.py
- Architecture Document
- CHANGELOG
- DOMAIN_MODEL
- Multi-Bot (26-bot) Architecture
- KhatmRequest
- Admin Panel Base Layout (base.html)
- test_registration_phone_share_only.py
- OpenContribution
- receive_media
- FakeState
- test_recitation_text_only_for_laan.py
- advertising/service.py
- operations_page
- servant_ad/service.py
- test_next_portion_delivery_records_daily_reminder_to_prevent_duplicate
- test_quran_setup_waits_for_selected_hour_before_sending
- KhatmSaz Project (Claude Code Instructions)
- test_notify_routing.py
- KhatmCategoryGroup
- finish_invite_links
- QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)
- بخش B — تجربهٔ ساخت ختم (بات ختم‌ساز) — «دستِ سازنده باز باشد»
- khatm_workflow/service.py
- test_creator_contact.py
- WalletInvoice
- WaitingList
- Multi-Bot System (26-Bot Architecture)
- test_member_commitment_flow.py
- test_bot_commands.py
- PlanTier
- test_health.py
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی
- confirm_account_deletion
- cancel_commitment
- FakeState
- BotRegistry
- manual_phone_verification/repository.py
- test_dispatcher_routes_commands_while_profile_phone_state_is_active
- asyncio
- suggestions.py
- participation/models.py
- test_quran_join_is_member_controlled_without_auto_allocation
- test_fixed_salawat_content.py
- CSS Layouts and Responsive Design Guide
- test_owner_spec_b1_b5.py
- پلن بازطراحی ویزارد ساخت ختم + فلوی عضویت (مالک 2026-09-28)
- test_broadcast_shows_khatm_picker
- test_salawat_category_group_always_goes_directly_to_mode
- DECISIONS
- set_audio_callback
- Feature checklist
- Member Bot Language Isolation (fixed per bot)
- qr.py
- QuranAssetKind
- test_quran_channel_source.py
- join_requests.py
- create_and_launch_khatm
- test_notification_snooze.py
- Python Requirements
- monthly_report/service.py
- completion/service.py
- register_devotional_content.py
- devotional_seed.py
- test_owner_spec_b6_b10.py
- FakeMessage
- test_broadcast_policy.py
- app.py
- test_daily_digest_sends_each_khatm_with_its_own_done_button
- FakeMessage
- test_public_khatms_reply_button_is_wired
- help.py
- test_set_font_size_validates_and_persists
- khatmsaz_modules_broadcast
- env.py
- bot/__init__.py
- PROJECT_STATE
- test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member
- broadcast.py
- test_next_portion_is_withheld_until_next_local_day_at_reminder_hour
- AdminFilter
- sqlalchemy_ext_asyncio
- BotRegistry Singleton Class
- zzz_merge_three_heads_2026_09_28.py
- _default_khatm_title
- seed_verified_quran_channel_map
- notification/models.py
- Wallet
- Mini-App Only Authentication Pattern
- Settings Menu Full-Button Test Scenario
- Codex system audit progress — 2026-09-29
- FakeState
- test_creator_finance_and_support_buttons_are_wired
- بخش D — بات ممبر (مخاطب)
- test_devotional_text_and_platform_specific_audio
- decide_manual_phone_request
- بخش A — پول‌سازی و پلن‌ها (منطق جدید، جایگزین قبلی‌ها)
- بخش عضو (بات ممبر) — `member_start.py`, `resume_join_after_registration`, `portions.py`
- delete_account
- message_template/__init__.py
- Tooltip Jinja2 Macro Component
- start.py
- Bot Help Strings (Persian)
- Identity Across Platforms (phone-based merge key)
- creator_begin_schedule_date
- test_member_can_choose_each_creator_and_keeps_exact_member_bot_route
- c21644dab334_add_skip_today_pause_and_leave_reason_.py
- register_devotional_content_batch2.py
- join_public_khatm
- test_creation_price_resolves_fixed_and_usage_based_plan_definitions
- A5 — حذف نقش «کریتور» و دکمه‌های ارتقا ✅ (۲۰۲۶-۰۹-۳۰)
- _compose_niyyat
- PlanFeatureUnavailableError
- start_bot.ps1
- test_devotional_category_navigation.py
- claude_watchdog.sh
- test_devotional_slug_link_does_not_depend_on_title_wording
- test_active_categories_are_filtered_by_the_selected_parent_family
- web/__init__.py
- collections
- Persian-first, Simple UX Principle
- Debugging Guide
- Working-tree Git Diff (creator_request wiring)
- PayPing v3 Payment Integration
- Quran Content Storage (Telegram channel-based)
- Redis (reserved for FSM / scheduler)
- 26-Bot Grid (1 creator + 12 member per platform)
- Creator Registration Flow (with OTP)
- Khatm Category Independent Families Test Scenario
- QA Handoff: Telegram Testing Guide for Codex
- test_reminder_due_fires_at_or_after_target_not_only_in_window
- khatmsaz_bot_handlers_create_khatm
- khatmsaz_bot_handlers_join_flow
- khatmsaz_bot_handlers_start
- khatmsaz_core_bot_registry
- khatmsaz_core_db
- khatmsaz_core_ids
- khatmsaz_core_security
- khatmsaz_i18n
- khatmsaz_modules_allocation
- khatmsaz_modules_identity
- khatmsaz_modules_invitation
- khatmsaz_modules_invitation_models
- khatmsaz_modules_khatm_models
- khatmsaz_modules_notification
- khatmsaz_modules_participation
- khatmsaz_modules_phone
- khatmsaz_modules_phone_models
- khatmsaz_modules_session
- khatmsaz_modules_session_models
- khatmsaz_modules_settings
- khatmsaz_modules_settings_models
- khatmsaz_modules_wallet
- khatmsaz_modules_wallet_gateway
- Module: audit_log
- Module: phone
- Module: plan
- Module: settings
- start_broadcast
- CommitFlow
- str
- resume_join_after_registration
- Admins Management Page
- Audit Log Page
- Broadcasts Admin Page
- Operations/Health Admin Page
- Phone Verifications Admin Page
- Message Templates Admin Page
- member_my_khatms.py
- khatmsaz_bot
- khatmsaz_bot_handlers
- khatmsaz_bot_handlers_help
- khatmsaz_bot_navigation
- khatmsaz_core
- khatmsaz_modules_allocation_models
- khatmsaz_modules_bot_registry
- khatmsaz_modules_bot_registry_models
- khatmsaz_modules_content
- khatmsaz_modules_identity_models
- khatmsaz_modules_khatm
- khatmsaz_modules_khatm_workflow
- khatmsaz_modules_notification_models
- khatmsaz_modules_participation_commitment
- khatmsaz_modules_participation_models
- khatmsaz_modules_plan
- khatmsaz_modules_reminder_engine
- khatmsaz_modules_system_settings

## God Nodes (most connected - your core abstractions)
1. `session_scope()` - 395 edges
2. `t()` - 379 edges
3. `Platform` - 301 edges
4. `Khatm` - 162 edges
5. `User` - 143 edges
6. `new_id()` - 140 edges
7. `KhatmTemplateType` - 119 edges
8. `safe_answer_callback()` - 118 edges
9. `resolve_or_provision_user()` - 100 edges
10. `KhatmStatus` - 94 edges

## Surprising Connections (you probably didn't know these)
- `G1 — چهار عکس (قرآن/صلوات/دعا/لعن) با پیام نیت ⬜` --references--> `_show_intro_image()`  [INFERRED]
  docs/ai/OWNER_SPEC_MASTER.md → src/khatmsaz/bot/handlers/create_khatm.py
- `B1 — شلوغیِ ابتدای بات و گیج‌کنندگی سؤال‌ها ✅` --references--> `_wiz()`  [INFERRED]
  docs/ai/OWNER_SPEC_MASTER.md → src/khatmsaz/bot/handlers/create_khatm.py
- `B7 — تک‌پیامِ به‌روزشونده در ساخت ختم (و در جوین ممبر) ✅` --references--> `_wiz()`  [INFERRED]
  docs/ai/OWNER_SPEC_MASTER.md → src/khatmsaz/bot/handlers/create_khatm.py
- `R8. ترتیب پلتفرم: «هر دو» بالا، بعد تلگرام، بعد بله — **بدون مایگریشن**` --references--> `choose_allowed_platforms()`  [INFERRED]
  docs/ai/REDESIGN_PLAN_2026-09-28.md → src/khatmsaz/bot/handlers/create_khatm.py
- `B3 — دکمهٔ «بازگشت به مرحلهٔ قبل» در کل ویزارد ساخت ✅` --references--> `previous_wizard_step()`  [INFERRED]
  docs/ai/OWNER_SPEC_MASTER.md → src/khatmsaz/bot/handlers/create_khatm.py

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

## Communities (288 total, 117 thin omitted)

### Community 0 - "wallet/service.py"
Cohesion: 0.12
Nodes (30): PaymentGateway, Protocol, CouponDiscountType, cleanup_expired_pending_payments(), _coupon_discount(), create_payment_intent(), get_balances(), InvalidCouponError (+22 more)

### Community 1 - "sqlalchemy"
Cohesion: 0.09
Nodes (29): khatmsaz_modules_khatm_category_models, pytest, sqlalchemy, UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Identity module: the canonical User and external PlatformIdentity links.…, Khatm module: the core collective-recitation aggregate., Positive personal progress reporting for the bot., Real PostgreSQL coverage for the safe account-deletion boundary. (+21 more)

### Community 2 - "keyboards.py"
Cohesion: 0.10
Nodes (36): base64, ادمین / پنل وب, رفع‌شدهٔ فاز ۲ (این جلسه، با تست), InlineKeyboardButton, advertising_choice_keyboard(), capacity_choice_keyboard(), category_choice_keyboard(), _ck_back_row() (+28 more)

### Community 3 - "create_khatm.py"
Cohesion: 0.11
Nodes (60): R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome(), _apply_coupon_code(), apply_creation_coupon() (+52 more)

### Community 4 - "identity/service.py"
Cohesion: 0.05
Nodes (88): aiogram, aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, aiogram_filters, aiogram_fsm_context, aiogram_fsm_state, aiogram_types (+80 more)

### Community 5 - ".__call__"
Cohesion: 0.60
Nodes (4): _extract_chat_id(), Any, _reply_blocked(), TelegramObject

### Community 6 - "_build_my_khatms_tree"
Cohesion: 0.21
Nodes (13): _build_my_khatms_tree(), _content_group(), _khatm_bucket(), list_my_khatms(), InlineKeyboardMarkup, Which of the four top-level content families (BACKLOG.md §18 level 2) a khatm…, Owner request (2026-09-21, BACKLOG.md §18): "ختم‌های من" needs three top-level…, Canonical (language-independent) bucket key; translate at display time with… (+5 more)

### Community 7 - "db.py"
Cohesion: 0.06
Nodes (47): DeclarativeBase, enum, httpx, khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, openpyxl, re, sqlalchemy_dialects_postgresql (+39 more)

### Community 8 - "phone/service.py"
Cohesion: 0.06
Nodes (71): begin_phone_change(), ensure_creator_phone_verified(), FSMContext, Message, Return true when creation may continue; otherwise start the OTP step., receive_change_code(), verify_creator_phone(), AccountMerge (+63 more)

### Community 9 - "portions.py"
Cohesion: 0.12
Nodes (51): E3 (اولیه) 🔵, E3 — ثبت مشارکت، کاستومِ هر نوع ✅ (تأیید+اصلاح ۲۰۲۶-۰۹-۳۰), _parse_delivery_time(), Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid., _active_participation_for_current_bot(), apply_snooze(), ask_commitment_quantity(), ask_contribution_amount() (+43 more)

### Community 10 - "new_id"
Cohesion: 0.08
Nodes (35): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), AuditLog, list_recent(), AsyncSession, Persistence access for the append-only audit module. (+27 more)

### Community 11 - "reminder_engine/service.py"
Cohesion: 0.11
Nodes (49): E1 — تحویل خودکارِ سهم/پیام سرِ تایمِ درست، per-timezone، per-khatm 🔴 CRITICAL ✅ (ممیزی و رفع ۲۰۲۶-۰۹-۳۰), E1 (شرح اولیه) ⬜🔵, ماژول‌های کلیدی (نقشهٔ سریع — با graphify کامل‌تر کن), SendQuranPagesFn, portion_done_keyboard(), For a portion that's still PENDING (not completed yet) — shows the content +…, Positive khatm-completion announcements., has_started() (+41 more)

### Community 12 - "KhatmTemplateType"
Cohesion: 0.04
Nodes (71): build_join_success_message(), Shared with `join_requests.py`'s approval handler, which sends this same…, CoverStatus, KhatmScheduleKind, KhatmTemplateType, KhatmTypeEnum, str, asyncio (+63 more)

### Community 13 - "t"
Cohesion: 0.11
Nodes (54): begin_account_link(), FSMContext, message, receive_link_code(), receive_link_phone(), begin_profile(), buy_sms_plan(), _can_open_creator_panel() (+46 more)

### Community 14 - "Khatm"
Cohesion: 0.10
Nodes (64): Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+56 more)

### Community 15 - "User"
Cohesion: 0.05
Nodes (61): ChangePhone, StatesGroup, set_registry(), PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity(), find_by_id() (+53 more)

### Community 16 - "_authenticate_telegram_mini_app"
Cohesion: 0.12
Nodes (23): dataclasses, hashlib, hmac, secrets, Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, _authenticate_telegram_mini_app(), telegram_admin_mini_app_auth(), telegram_creator_mini_app_auth() (+15 more)

### Community 17 - "session_scope"
Cohesion: 0.06
Nodes (134): aiogram_exceptions, csv, html, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle() (+126 more)

### Community 18 - "resolve_or_provision_user"
Cohesion: 0.05
Nodes (72): _lang_for(), _lang_for(), CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), _lang_for() (+64 more)

### Community 19 - "panel.py"
Cohesion: 0.07
Nodes (53): سازنده (Creator) — تلگرام, admin_panel_keyboard(), creator_panel_keyboard(), _get_context(), handle_admin_panel(), handle_admin_panel_broadcast(), handle_admin_panel_requests(), handle_admin_panel_users() (+45 more)

### Community 20 - "typing"
Cohesion: 0.04
Nodes (6): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 22 - "Participation"
Cohesion: 0.08
Nodes (70): confirm_regular_occurrence(), Confirm the current scheduled occurrence once, by its owning member., _count_creator_members(), leave_khatm(), pause_commitment(), AsyncSession, Leave a khatm. If the leaver was a committed participant, promote the next…, Pause future reminders without releasing or completing the owed share. (+62 more)

### Community 23 - "registration.py"
Cohesion: 0.12
Nodes (33): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), MemberRegistration, callback_query, CallbackQuery (+25 more)

### Community 24 - "content/service.py"
Cohesion: 0.10
Nodes (31): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., add_devotional_audio_variant(), add_devotional_image_page(), decode_telegram_forward_ref(), get_allowed_reciters(), get_effective_reciter(), _get_enabled_devotional_asset() (+23 more)

### Community 25 - "AdminPermission"
Cohesion: 0.18
Nodes (55): post, RedirectResponse, Request, record(), AdminPermission, find_by_id(), search_users(), _admin() (+47 more)

### Community 26 - "OWNER_SPEC_MASTER.md"
Cohesion: 0.11
Nodes (18): C1 — تیکت مخاطب → سازندهٔ ختم ✅, C2 — تیکت سازنده → ادمین اصلی ✅, C3 — متن دکمهٔ تأیید مدیر: بار منفیِ «رد» را بردار ✅, C4 — دو پیام گروهی رایگان زیرِ ۱۰۰۰ نفر (بله و تلگرام) ✅, C5 — دسته‌بندی مخاطبانِ پیام گروهی ✅, F1 — غیرفعال‌سازی موقتِ عربی و انگلیسی ⬜, F2 — حذف «(عج)» از همه‌جا ⬜, F3 — فونت پنل (انجام‌شده؟) 🔵 — Estedad ست شده؛ verify روی وب‌ویو. (+10 more)

### Community 28 - "KhatmPortion"
Cohesion: 0.06
Nodes (91): AllocationStrategy, CommittedQuantityLog, KhatmPortion, PortionStatus, PortionUnitKind, str, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, add_quantity_commitment_portion() (+83 more)

### Community 29 - "PayPingGateway"
Cohesion: 0.11
Nodes (20): Response, GatewayError, PaymentRequest, PaymentVerification, Exception, Gateway boundary; PSP-specific code must live behind this protocol., The PSP rejected or could not complete a request., PayPingGateway (+12 more)

### Community 30 - "test_deep_link_clears_old_state_before_storing_new_join_context"
Cohesion: 0.08
Nodes (15): FakeMessage, FakeState, asyncio, parametrize, test_deep_link_clears_old_state_before_storing_new_join_context(), test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home() (+7 more)

### Community 31 - "safe_answer_callback"
Cohesion: 0.18
Nodes (42): ask_creation_coupon(), cancel_wizard(), choose_allowed_platforms(), choose_category(), choose_category_group(), choose_commitment_total(), choose_content_delivery_mode(), choose_creator_display() (+34 more)

### Community 32 - "admin_approve_request"
Cohesion: 0.35
Nodes (12): admin_approve_request(), admin_reject_request(), CommandObject, FSMContext, Message, request_khatm(), request_khatm_description(), request_khatm_document() (+4 more)

### Community 33 - "test_admin_template_render.py"
Cohesion: 0.06
Nodes (27): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests… (+19 more)

### Community 34 - "leave.py"
Cohesion: 0.32
Nodes (15): approve_leave(), ask_leave_reason(), _do_leave(), _lang_for(), _lang_for_user(), leave_reason_chosen(), callback_query, CallbackQuery (+7 more)

### Community 35 - "Session"
Cohesion: 0.14
Nodes (28): generate_token(), hash_token(), create_invitation(), Session, create(), get_active_by_hash(), AsyncSession, datetime (+20 more)

### Community 36 - "profile.py"
Cohesion: 0.13
Nodes (25): choose_gender(), choose_province(), enter_city(), enter_name(), enter_phone(), _gender_keyboard(), _province_keyboard(), callback_query (+17 more)

### Community 37 - "creator_request/service.py"
Cohesion: 0.13
Nodes (31): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user() (+23 more)

### Community 38 - "KhatmCategory"
Cohesion: 0.23
Nodes (27): KhatmCategory, KhatmCategoryRequest, KhatmCategoryRequestStatus, A participant's typed request for a دعا that isn't in the library yet (owner…, create(), create_request(), get_by_id(), get_request_by_id() (+19 more)

### Community 39 - "provider.py"
Cohesion: 0.10
Nodes (27): BaseSettings, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Protocol (+19 more)

### Community 40 - "DevotionalAsset"
Cohesion: 0.14
Nodes (20): deliver_devotional_media(), callback_query, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional_reciter_choice(), DevotionalAsset (+12 more)

### Community 41 - "wallet/repository.py"
Cohesion: 0.18
Nodes (24): CouponRedemption, DiscountCoupon, InvoiceStatus, PendingPayment, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, claim_pending_payment(), count_coupon_redemptions(), create_coupon_redemption() (+16 more)

### Community 42 - "test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it"
Cohesion: 0.07
Nodes (27): KhatmAllocationPlan, KhatmInvitation, create(), get_by_token_hash(), mark_accepted(), AsyncSession, Persistence access for invitation — the only place that runs SQL for this…, _iana_offset_for_local_hour() (+19 more)

### Community 43 - "sms_subscription/service.py"
Cohesion: 0.15
Nodes (28): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+20 more)

### Community 44 - "broadcast/service.py"
Cohesion: 0.21
Nodes (25): BroadcastStatus, KhatmBroadcast, str, count_lifetime_digital_for_creator(), count_recent_for_creator_channel(), create(), get_by_id(), list_pending() (+17 more)

### Community 45 - "commitment.py"
Cohesion: 0.15
Nodes (20): is_regular_due(), log_count(), _minutes(), parse_hhmm(), datetime, str, R11 (owner 2026-09-28, revised after live QA): member-side commitment logic.…, Add ``amount`` to a COUNT-mode member's logged total. Returns ``(new_done,… (+12 more)

### Community 46 - "UserRole"
Cohesion: 0.15
Nodes (30): AdminRole, AdminRoleGrant, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession, Persistence helpers for delegated admin roles., revoke_role() (+22 more)

### Community 47 - "test_home_menu.py"
Cohesion: 0.16
Nodes (16): admin_menu_keyboard(), creator_finance_keyboard(), creator_management_keyboard(), creator_menu_keyboard(), creator_schedule_keyboard(), creator_settings_keyboard(), creator_support_keyboard(), participant_menu_keyboard() (+8 more)

### Community 48 - "بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`"
Cohesion: 0.12
Nodes (11): R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک**, R5. تعهد = تعداد کلِ ختم (نه per-person) با دکمه‌ها — **کد + احتمالاً مایگریشن**, R7. مثال برای هر ۴ مدل متن — **بدون مایگریشن** (i18n), R8. ترتیب پلتفرم: «هر دو» بالا، بعد تلگرام، بعد بله — **بدون مایگریشن**, R9. لینک بعد از تأیید: اول فارسی، بقیه on-request — **بدون مایگریشن** (+3 more)

### Community 49 - "test_early_regular_share_waits_for_done_before_consuming_schedule"
Cohesion: 0.13
Nodes (9): FakeCallback, FakeMessage, asyncio, test_early_regular_share_waits_for_done_before_consuming_schedule(), test_today_lists_khatms_before_delivering_any_share(), fake_khatm(), fake_scope(), fake_settings() (+1 more)

### Community 50 - "notification/service.py"
Cohesion: 0.22
Nodes (18): NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession, datetime (+10 more)

### Community 51 - "plan/repository.py"
Cohesion: 0.24
Nodes (14): A1 (اولیه) ⬜, PlanDefinition, PricingMode, Admin-managed pricing and feature entitlements for a plan tier., UserPlan, get_by_user(), get_definition(), lock_plan_change() (+6 more)

### Community 52 - "member_commitment.py"
Cohesion: 0.16
Nodes (37): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), enter_count(), enter_custom_time(), enter_log_amount() (+29 more)

### Community 53 - "plan/service.py"
Cohesion: 0.18
Nodes (23): A1 — سه پلن با تنظیمات قابل‌ویرایش ادمین ✅ (بک‌بون، ۲۰۲۶-۰۹-۳۰), _enforce_creation_cap(), DEC-PY-0074: a FREE-tier creator's member cap is summed across all their own…, ads_enabled_for_creator(), count_total_active_members(), get_creation_price(), get_definition(), get_free_total_member_cap() (+15 more)

### Community 54 - "test_registration_starts_in_the_users_saved_language"
Cohesion: 0.14
Nodes (8): ProfileEdit, StatesGroup, FakeMessage, FakeState, asyncio, integration, parametrize, test_registration_starts_in_the_users_saved_language()

### Community 55 - "content/__init__.py"
Cohesion: 0.19
Nodes (5): khatmsaz_modules_khatm_category, Content preferences and per-khatm reciter policy., BACKLOG.md §14 fix (2026-09-21): replace the fragile name-matching hack…, Owner request (2026-09-22): a devotional asset (dua/ziyarat) can now have more…, Real PostgreSQL filtering proof for independent devotional families.

### Community 56 - "message_template/repository.py"
Cohesion: 0.26
Nodes (13): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+5 more)

### Community 57 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.16
Nodes (16): DEC-PY-0057 Internal Invoice For Every Purchase, Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, PayPing v3 Adapter Integration, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File (+8 more)

### Community 58 - "test_wizard_ephemeral.py"
Cohesion: 0.19
Nodes (11): FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_can_keep_intro_beside_title_until_answered(), test_wiz_deletes_previous_prompt() (+3 more)

### Community 59 - "bot_registry/service.py"
Cohesion: 0.17
Nodes (28): cryptography_fernet, Fernet, BotInstance, get_by_id(), get_by_slot(), list_active(), list_active_members(), list_all() (+20 more)

### Community 60 - "test_contribute_blocked_until_delivery_hour_set"
Cohesion: 0.15
Nodes (10): CustomSnooze, LogContribution, PauseCommitment, StatesGroup, Owner request (2026-09-21): the first time a non-committed (open or waitlisted)…, SetupOpenQuranReading, _callback_update(), asyncio (+2 more)

### Community 61 - "datetime"
Cohesion: 0.08
Nodes (20): aiogram_enums, aiogram_fsm_storage_memory, contextlib, datetime, inspect, Runtime registry of all live Bot instances, built once at startup., Owner-reported bug (2026-09-22): "لینک جوین تو بله مشکل داره... این کد رو…, Regression for per-khatm broadcast targeting (owner request 2026-09-27):… (+12 more)

### Community 62 - "open_contribution/repository.py"
Cohesion: 0.20
Nodes (16): create(), has_for_participation_since(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+8 more)

### Community 63 - "Architecture Document"
Cohesion: 0.14
Nodes (18): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, No Business Rule Invention Rule, PayPing v3 Payment Gateway, Architecture Document, PayPing Setup Guide (Persian) (+10 more)

### Community 64 - "CHANGELOG"
Cohesion: 0.11
Nodes (19): Multi-Bot Architecture (26 bots), CHANGELOG Archive (until 2026-09-18), CHANGELOG, Creator wallet-charge button, Devotional content library + seed, i18n coverage guard (fa/ar/en), positional_range_for_step (rotating allocation helper), Reminder engine (APScheduler scan) (+11 more)

### Community 65 - "DOMAIN_MODEL"
Cohesion: 0.24
Nodes (12): PayPing payment gateway, PendingPayment compare-and-swap replay protection, DEC-PY-0068 — Kavenegar is first production SMS adapter, DEC-PY-0074 — Free-tier plan caps per-creator, admin-editable, DOMAIN_MODEL, Backup Reader + Emergency Pool, Central identity = verified phone, Commitment engine (+4 more)

### Community 66 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.14
Nodes (15): DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Multi-bot invite links (bot/invite_links.py), Creator Bot (Multi-bot doc), dp_creator Dispatcher, BotRegistry & bot_instances Table, Creator Bot (+7 more)

### Community 67 - "KhatmRequest"
Cohesion: 0.27
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 68 - "Admin Panel Base Layout (base.html)"
Cohesion: 0.18
Nodes (18): Admin Panel Base Layout (base.html), components.html macros (tooltip), Glassmorphism Dark Design System, Permission-gated Admin Navigation, Admin Categories Page (categories.html), Creator Panel Base Layout (creator_base.html), Creator Panel i18n (t/lang) Localization, Creator Dashboard (creator_dashboard.html) (+10 more)

### Community 69 - "test_registration_phone_share_only.py"
Cohesion: 0.18
Nodes (8): StatesGroup, Registration, FakeMessage, FakeState, asyncio, Owner request (2026-09-22): during initial registration on Telegram, only the…, test_bale_typed_phone_is_still_accepted_during_registration(), test_telegram_typed_phone_is_rejected_during_registration()

### Community 70 - "OpenContribution"
Cohesion: 0.11
Nodes (19): OpenContribution, get_khatm_stats(), KhatmStats, asyncio, integration, test_ad_reward_requires_opt_in_and_is_idempotent(), asyncio, integration (+11 more)

### Community 71 - "receive_media"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 73 - "test_recitation_text_only_for_laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 74 - "advertising/service.py"
Cohesion: 0.15
Nodes (11): json, AdvertisingRewardRate, Append-only reward-rate history; the newest effective rate is active., get_active_rate(), AsyncSession, datetime, Advertising rewards: opt-in is per khatm and accrual is idempotent., set_reward_rate() (+3 more)

### Community 75 - "operations_page"
Cohesion: 0.18
Nodes (9): mark_scan_failed(), mark_scheduler_started(), process_started_at(), datetime, Exception, In-process operational heartbeat exposed read-only to Operations admins., snapshot(), operations_page() (+1 more)

### Community 76 - "servant_ad/service.py"
Cohesion: 0.09
Nodes (32): middleware, SendFn, audience_size(), _basic_creator_ids(), get_ad(), AsyncSession, خدمتگزاران system-ad service (owner §A4). Reads/writes the single active system…, Deliver the active ad to the BASIC audience once each. Returns the number of… (+24 more)

### Community 77 - "test_next_portion_delivery_records_daily_reminder_to_prevent_duplicate"
Cohesion: 0.13
Nodes (3): asyncio, E1 audit (2026-09-30): after allocating+sending the next committed-Quran…, test_next_portion_delivery_records_daily_reminder_to_prevent_duplicate()

### Community 78 - "test_quran_setup_waits_for_selected_hour_before_sending"
Cohesion: 0.13
Nodes (4): FakeMessage, FakeState, asyncio, test_quran_setup_waits_for_selected_hour_before_sending()

### Community 79 - "KhatmSaz Project (Claude Code Instructions)"
Cohesion: 0.20
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), Admin Mini App (Telegram WebApp), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), Admin Mini App Guide (Persian), AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 80 - "test_notify_routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 81 - "KhatmCategoryGroup"
Cohesion: 0.12
Nodes (25): _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, khatm_matches_bot(), Keep Quran/Salawat/Dua-Ziyarat/La'an families in their own member bot., BotCategory, str, resolve_bot_category(), KhatmCategoryGroup (+17 more)

### Community 82 - "finish_invite_links"
Cohesion: 0.21
Nodes (12): finish_invite_links(), show_invite_platform_keyboard(), build_member_invite_links(), format_invite_lines(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm., Build member-bot deep links for one khatm token. Returns an ordered dict keyed… (+4 more)

### Community 83 - "QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)"
Cohesion: 0.18
Nodes (11): A. زیرساخت چندبات (۲۶ بات), B. ثبت‌نام, E. سهم و یادآوری, F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات, G. زبان‌ها (fa/ar/en), H. پرداخت, I. Mini App + پنل ادمین, QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه) (+3 more)

### Community 84 - "بخش B — تجربهٔ ساخت ختم (بات ختم‌ساز) — «دستِ سازنده باز باشد»"
Cohesion: 0.18
Nodes (11): B10 — پرسش تعهد، کاستومِ هر خانواده ✅, B1 — شلوغیِ ابتدای بات و گیج‌کنندگی سؤال‌ها ✅, B2 — دکمهٔ «ختم صفحات قرآن» → فقط «ختم قرآن» ✅, B3 — دکمهٔ «بازگشت به مرحلهٔ قبل» در کل ویزارد ساخت ✅, B4 — پیام «قابل تغییر است» به‌جای «تغییر ممکن نیست» ✅, B5 — پیام تعداد ختم/دور + آیندهٔ افزایش (پولی، ولی الان رایگان) ✅, B6 — پیام‌های اعتمادساز هنگام ساخت + توضیح گرفتن آیدی ✅, B7 — تک‌پیامِ به‌روزشونده در ساخت ختم (و در جوین ممبر) ✅ (+3 more)

### Community 85 - "khatm_workflow/service.py"
Cohesion: 0.12
Nodes (21): CreatorDisplayMode, approve_join_request(), _complete_join(), InvalidCreatorDecisionError, join_via_token(), JoinRequiresApprovalError, KhatmCancellationError, KhatmUnavailableError (+13 more)

### Community 86 - "test_creator_contact.py"
Cohesion: 0.22
Nodes (12): _compose_welcome_with_contact(), _normalize_contact(), R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, R4 (owner 2026-09-28): the creator is asked for a contact handle (Telegram/…, test_compose_appends_contact_line_to_welcome(), test_compose_contact_only_when_no_welcome(), test_compose_none_contact_passes_welcome_through() (+4 more)

### Community 87 - "WalletInvoice"
Cohesion: 0.11
Nodes (23): Immutable purchase amounts plus a small paid/refunded lifecycle., WalletInvoice, WalletTransaction, bind_invoice_resource(), bind_invoice_resource(), asyncio, integration, test_coupon_discount_invoice_and_limits_are_atomic() (+15 more)

### Community 88 - "WaitingList"
Cohesion: 0.27
Nodes (10): WaitingList, add(), pop_first(), AsyncSession, Persistence access for waiting_list — the only place that runs SQL for this…, join(), promote_next(), AsyncSession (+2 more)

### Community 89 - "Multi-Bot System (26-Bot Architecture)"
Cohesion: 0.15
Nodes (15): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, resolve_bot_category() Function, Router Classification (creator-only, member-only, shared) (+7 more)

### Community 90 - "test_member_commitment_flow.py"
Cohesion: 0.26
Nodes (9): importlib_util, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_has_presets_and_custom(), test_hour_keyboard_prefix_matches_handler(), test_mode_keyboard_callbacks() (+1 more)

### Community 91 - "test_bot_commands.py"
Cohesion: 0.36
Nodes (4): FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 92 - "PlanTier"
Cohesion: 0.29
Nodes (10): PlanTier, str, asyncio, parametrize, Plan tier model — OWNER_SPEC_MASTER §A (2026-09-30). Superseded the earlier…, test_ads_enabled_only_on_basic(), test_all_three_tiers_are_active(), test_free_autoupgrades_to_basic_past_cap() (+2 more)

### Community 93 - "test_health.py"
Cohesion: 0.28
Nodes (6): fastapi_responses, _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 94 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی"
Cohesion: 0.22
Nodes (9): Live QA — 2026-09-28 (Chrome / Telegram Web / Codex), QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, رفع‌شدهٔ live-QA (2026-09-28), ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live), موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک), نتیجهٔ فاز ۱ (این جلسه), هدف افزوده‌شده (مالک، 2026-09-27), 🎯 هدف‌های بزرگِ افزوده‌شده (مالک، 2026-09-28) — نیازمند سشن اختصاصی (+1 more)

### Community 95 - "confirm_account_deletion"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

### Community 96 - "cancel_commitment"
Cohesion: 0.31
Nodes (11): accept_commitment(), cancel_commitment(), _finish_join_prompt(), callback_query, CallbackQuery, FSMContext, Message, Replace only the bot-owned join wizard message, never unrelated chat history. (+3 more)

### Community 98 - "BotRegistry"
Cohesion: 0.33
Nodes (3): BotRegistry, Bot, UUID

### Community 99 - "manual_phone_verification/repository.py"
Cohesion: 0.47
Nodes (8): ManualPhoneVerification, create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession, Persistence helpers for foreign-number manual verification.

### Community 100 - "test_dispatcher_routes_commands_while_profile_phone_state_is_active"
Cohesion: 0.18
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 101 - "asyncio"
Cohesion: 0.20
Nodes (7): asyncio, fixture, os, get_engine(), dispose_sqlalchemy_pool_after_test(), Shared pytest configuration for unit and opt-in integration tests., Prevent asyncpg connections from crossing pytest event loops on Windows.

### Community 102 - "suggestions.py"
Cohesion: 0.17
Nodes (21): back_to_support_menu(), choose_creator(), callback_query, CallbackQuery, FSMContext, message, StatesGroup, User feedback/bug-report inbox to admins (owner request, 2026-09-21). Updated… (+13 more)

### Community 103 - "participation/models.py"
Cohesion: 0.18
Nodes (8): Per-khatm advertising opt-in and reward-credit accrual., Assignment, AssignmentStatus, AssignmentUnitKind, str, Participation module: a user's membership in a Khatm, and per-participant…, The Phase-4 flat per-khatm assignment (legacy shape, kept for parity). The…, Real PostgreSQL coverage for positive, timezone-aware monthly delivery.

### Community 104 - "test_quran_join_is_member_controlled_without_auto_allocation"
Cohesion: 0.27
Nodes (6): asyncio, test_join_via_token_threads_bot_instance_id(), fake_get_khatm(), fake_join(), fake_resolve(), test_quran_join_is_member_controlled_without_auto_allocation()

### Community 105 - "test_fixed_salawat_content.py"
Cohesion: 0.24
Nodes (5): FakeMessage, _plain_salawat(), asyncio, test_plain_salawat_sends_exact_owner_text_without_category(), test_plain_salawat_uses_panel_image_with_fixed_text_caption()

### Community 106 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 107 - "test_owner_spec_b1_b5.py"
Cohesion: 0.14
Nodes (14): _commitment_total_keyboard(), _creator_contact_keyboard(), InlineKeyboardMarkup, R4 (owner 2026-09-28): the creator MUST provide a contact so members can reach…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited() (+6 more)

### Community 108 - "پلن بازطراحی ویزارد ساخت ختم + فلوی عضویت (مالک 2026-09-28)"
Cohesion: 0.20
Nodes (9): R11/N2 member commitment flow (regular/count), Codex Handoff — Next Steps, PayPing gateway activation (needs owner API token), DEC-PY-0090 — Fixed niyyat + optional niyabat, Minimal-interaction wizard/join redesign (R1-R13), اصول, ترتیب اجرا (کم‌ریسک → پرریسک), وابستگی‌های مایگریشن (نیاز به Postgres تستی + بازبینی مالک) (+1 more)

### Community 109 - "test_broadcast_shows_khatm_picker"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 110 - "test_salawat_category_group_always_goes_directly_to_mode"
Cohesion: 0.20
Nodes (3): _async_value(), asyncio, test_salawat_category_group_always_goes_directly_to_mode()

### Community 111 - "DECISIONS"
Cohesion: 0.31
Nodes (10): DECISIONS, DEC-PY-0076 — Separate participant and creator menus, DEC-PY-0077 — Daily portions stack up, DEC-PY-0091 — Creation wizard no longer asks content format, DEC-PY-0092 — Rotating Quran allocation, DEC-PY-0093 — Creator bot has one fixed menu, starts creation directly, DEC-PY-0094 — Quran reading pace chosen by each member, DEC-PY-0095 — First Quran pages wait for chosen hour; automatic titles; OTP dedup (+2 more)

### Community 112 - "set_audio_callback"
Cohesion: 0.67
Nodes (4): callback_query, CallbackQuery, quran_help(), set_audio_callback()

### Community 113 - "Feature checklist"
Cohesion: 0.25
Nodes (7): 1. Graphical creator Mini App khatm creation — DONE, 2. Real FREE → PRO purchase — DONE, 3. Configurable panel logo — DONE, 4. Reliable modern Persian panel font — DONE, Codex big features progress — 2026-09-29, Cross-feature validation and delivery log, Feature checklist

### Community 114 - "Member Bot Language Isolation (fixed per bot)"
Cohesion: 0.25
Nodes (8): dp_member Router Registration List, Member Bot Language Isolation (fixed per bot), Member My Khatms (filtered by joined_via_bot_instance_id), Cross-Bot Notification Pattern (recipient context wins), joined_via_bot_instance_id Column on khatm_participations, notify_fn Signature with bot_instance_id, Member Registration Flow (no OTP, trust-based), Shared Execution Plan Phase 5 — Audience Isolation and Creator Empowerment

### Community 115 - "qr.py"
Cohesion: 0.32
Nodes (6): io, qrcode, build_qr_png(), In-memory QR generation for shareable bot invite links., test_build_qr_png_is_nonempty_png(), test_build_qr_png_rejects_non_web_values()

### Community 116 - "QuranAssetKind"
Cohesion: 0.15
Nodes (20): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), parse_quran_channel_caption(), Idempotently map one source-channel post to every page it covers., Return an exact contiguous range, or None when any page is missing. (+12 more)

### Community 117 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 118 - "join_requests.py"
Cohesion: 0.40
Nodes (9): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, Creator approve/reject for a PRIVATE khatm's join request (DOMAIN_MODEL.md §2…, reject_join(), Unpack two UUIDs from a short base64 string. (+1 more)

### Community 119 - "create_and_launch_khatm"
Cohesion: 0.24
Nodes (10): cancel_khatm(), create_and_launch_khatm(), datetime, `creation_price_toman` (DOMAIN_MODEL.md §7: creating a khatm costs money,…, Cancel an unused khatm and refund its recorded creation price internally., InvoiceKind, str, purchase() (+2 more)

### Community 120 - "test_notification_snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 121 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 122 - "monthly_report/service.py"
Cohesion: 0.18
Nodes (14): deliver_due(), _previous_month_bounds(), AsyncSession, datetime, NotifyFn, Timezone-aware, idempotent delivery of the previous month's progress., _render(), Personal and creator reporting services. (+6 more)

### Community 123 - "completion/service.py"
Cohesion: 0.28
Nodes (8): collections_abc, deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Idempotent, delayed completion announcements for every platform., Claim each eligible announcement once, then notify creator + active members.

### Community 124 - "register_devotional_content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 125 - "devotional_seed.py"
Cohesion: 0.22
Nodes (8): _chunk(), AsyncSession, Startup seed for admin-curated devotional TEXT (dua / ziyarat). Owner workflow:…, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), Raw devotional texts (Arabic + Persian translation), owner-provided. Kept in a…, register_devotional_text()

### Community 126 - "test_owner_spec_b6_b10.py"
Cohesion: 0.09
Nodes (23): خدمتگزاران system promo ads (owner §A4). Admin-defined promotional message…, _message(), asyncio, Fail-closed behavior before a public HTTPS Mini App origin exists., test_admin_mini_app_rejects_local_http_origin(), test_creator_mini_app_rejects_local_http_origin_before_database_access(), _callbacks(), Regression coverage for OWNER_SPEC_MASTER B6 through B10. (+15 more)

### Community 128 - "test_broadcast_policy.py"
Cohesion: 0.33
Nodes (7): Creator-to-member message moderation boundary., asyncio, test_all_three_channel_policies_are_admin_backed(), test_sms_is_paid_from_first_message(), test_submit_all_targets_uses_first_two_lifetime_digital_messages(), test_submit_requires_supported_channel_and_nonempty_audience(), test_third_digital_message_requires_pro_and_pro_is_unlimited()

### Community 129 - "app.py"
Cohesion: 0.08
Nodes (49): fastapi, fastapi_staticfiles, fastapi_templating, get, HTMLResponse, list_recent(), AsyncSession, _audit_details() (+41 more)

### Community 132 - "test_public_khatms_reply_button_is_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 133 - "help.py"
Cohesion: 0.18
Nodes (19): help_command(), help_open_my_khatms(), help_start_creation(), help_topic(), callback_query, CallbackQuery, FSMContext, Message (+11 more)

### Community 134 - "test_set_font_size_validates_and_persists"
Cohesion: 0.33
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 136 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 137 - "bot/__init__.py"
Cohesion: 0.33
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_without_cancel()

### Community 138 - "PROJECT_STATE"
Cohesion: 0.29
Nodes (8): PROJECT_STATE Archive (until 2026-09-18), DATABASE, Alembic migration workflow (reviewed, never blind autogenerate), Hand-written partial unique indexes, UUIDv7 app-generated primary keys, INDEX — Topical Documentation Map, PROJECT_STATE, Fresh-Postgres migration chain repair

### Community 139 - "test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 140 - "broadcast.py"
Cohesion: 0.23
Nodes (16): A2 (اولیه/staged سابق), A2 — پیام تبلیغاتی سازنده به مخاطبانش (پیام‌رسان، متن/عکس/فیلم/ویس) ✅ (۲۰۲۶-۰۹-۳۰), C6 — انواع محتوای پیام گروهی ✅, admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate() (+8 more)

### Community 141 - "test_next_portion_is_withheld_until_next_local_day_at_reminder_hour"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 142 - "AdminFilter"
Cohesion: 0.25
Nodes (6): BaseFilter, AdminFilter, Any, CallbackQuery, Message, Checks if the user has admin privileges. For now, we simply check if the user…

### Community 143 - "sqlalchemy_ext_asyncio"
Cohesion: 0.25
Nodes (6): sqlalchemy_ext_asyncio, AsyncSession, Template lookup and safe ``{{placeholder}}`` rendering., Reject malformed or unsupported placeholders before a template is stored., render(), validate_body()

### Community 144 - "BotRegistry Singleton Class"
Cohesion: 0.29
Nodes (7): Admin Token Panel /bots Route (2-step confirmation), Restart Requirement After Token Change, bot_instances Database Table, BotRegistry Singleton Class, Fernet Token Encryption for Bot Tokens, Handler Bot Role Check Pattern (bot.khatmsaz_role), Multi-Bot Invite Link Generation Flow

### Community 145 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 146 - "_default_khatm_title"
Cohesion: 0.50
Nodes (4): _default_khatm_title(), Build the standard title without asking the creator an extra question., test_devotional_title_uses_selected_category(), test_quran_title_is_automatic()

### Community 147 - "seed_verified_quran_channel_map"
Cohesion: 0.29
Nodes (7): 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد, رفع‌شدهٔ همین عصر (Claude Code), پاسخ به سؤال کانال قرآن, quran_channel_coverage(), Return exact 604-page coverage and missing pages for channel forwards., Idempotently load the repository's verified 604-page source map., seed_verified_quran_channel_map()

### Community 148 - "notification/models.py"
Cohesion: 0.33
Nodes (5): JobStatus, NotifChannel, NotificationJob, str, Notification module: scheduled reminder jobs, per-participation preferences,…

### Community 150 - "Wallet"
Cohesion: 0.22
Nodes (18): accrue_first_completed_action(), Grant one reward only after the first completed assigned action. The…, TxType, Wallet, add_balance(), add_credit(), create_for_user(), get_by_user() (+10 more)

### Community 152 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 153 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 154 - "Codex system audit progress — 2026-09-29"
Cohesion: 0.40
Nodes (4): Codex system audit progress — 2026-09-29, Delivery log, Evidence gathered, Requirements

### Community 156 - "test_creator_finance_and_support_buttons_are_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_creator_finance_and_support_buttons_are_wired(), _text_update()

### Community 157 - "بخش D — بات ممبر (مخاطب)"
Cohesion: 0.33
Nodes (6): D1 — «امروز» → «انجام قرائت امروز» (همه‌جا) ⬜, D2 — راهنمای بات‌ها به‌روز و بی‌مغایرت ⬜, D3 — تیکتینگ ممبر (همان C1) 🔵 — و منوی «ارتباط با سازندهٔ ختم» ⬜🔵, D4 — بخش «ساخت ختم اختصاصی» در بات ممبر ⬜, D5 — تک‌پیامِ به‌روزشوندهٔ جوین (فقط پیام‌های همین جوین) ⬜🔵, بخش D — بات ممبر (مخاطب)

### Community 158 - "test_devotional_text_and_platform_specific_audio"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 159 - "decide_manual_phone_request"
Cohesion: 0.33
Nodes (6): _authorized_admin(), decide_manual_phone_request(), list_manual_phone_requests(), callback_query, CallbackQuery, message

### Community 160 - "بخش A — پول‌سازی و پلن‌ها (منطق جدید، جایگزین قبلی‌ها)"
Cohesion: 0.40
Nodes (5): A3 (staged سابق), A3 — پیامک (SMS) همیشه پولی و درخواستی ✅ (۲۰۲۶-۰۹-۳۰), A4 (staged سابق), A4 — «تبلیغ خدمتگزاران» به مخاطبانِ سازنده‌های BASIC ✅ (۲۰۲۶-۰۹-۳۰), بخش A — پول‌سازی و پلن‌ها (منطق جدید، جایگزین قبلی‌ها)

### Community 161 - "بخش عضو (بات ممبر) — `member_start.py`, `resume_join_after_registration`, `portions.py`"
Cohesion: 0.40
Nodes (5): R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد**, R13. کمترین سؤال ممکن — اصل کلی هر دو بخش., بخش عضو (بات ممبر) — `member_start.py`, `resume_join_after_registration`, `portions.py`

### Community 162 - "delete_account"
Cohesion: 0.33
Nodes (5): AccountDeletionBlocked, delete_account(), Exception, Safely deactivate a user while retaining non-PII history. Active committed…, The account still owns an obligation that must be resolved first.

### Community 163 - "message_template/__init__.py"
Cohesion: 0.13
Nodes (11): Localized, versioned message templates., Real PostgreSQL coverage for template history and activation control., asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders() (+3 more)

### Community 164 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.50
Nodes (4): Tooltip Jinja2 Macro Component, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 165 - "start.py"
Cohesion: 0.10
Nodes (24): D6 — پیامِ جوین اعتمادساز: نامِ سازنده و نیابت ⬜🔵, accept_join_preview(), AskDeliveryHour, build_join_preview_message(), cancel_current_flow(), _clean_niyyat(), _creator_display_name(), _get_fallback_markup_for_bot() (+16 more)

### Community 166 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 167 - "Identity Across Platforms (phone-based merge key)"
Cohesion: 0.67
Nodes (3): Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 168 - "creator_begin_schedule_date"
Cohesion: 0.60
Nodes (5): creator_begin_cosmetic_edit(), creator_begin_end_at(), creator_begin_schedule_date(), FSMContext, creator_edit_cancel_keyboard()

### Community 170 - "test_member_can_choose_each_creator_and_keeps_exact_member_bot_route"
Cohesion: 0.40
Nodes (5): _member_creators(), Creators of the member's ACTIVE khatms, each with the member's own…, asyncio, integration, test_member_can_choose_each_creator_and_keeps_exact_member_bot_route()

### Community 180 - "register_devotional_content_batch2.py"
Cohesion: 0.67
Nodes (3): build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…

### Community 181 - "join_public_khatm"
Cohesion: 0.50
Nodes (4): join_public_khatm(), callback_query, CallbackQuery, FSMContext

### Community 182 - "test_creation_price_resolves_fixed_and_usage_based_plan_definitions"
Cohesion: 0.67
Nodes (4): asyncio, integration, test_creation_price_resolves_fixed_and_usage_based_plan_definitions(), test_plan_entitlement_lookup_uses_definition_not_plan_name_branching()

### Community 183 - "A5 — حذف نقش «کریتور» و دکمه‌های ارتقا ✅ (۲۰۲۶-۰۹-۳۰)"
Cohesion: 0.67
Nodes (3): A5 (اولیه) ⬜, A5 — حذف نقش «کریتور» و دکمه‌های ارتقا ✅ (۲۰۲۶-۰۹-۳۰), promote_creator()

### Community 185 - "_compose_niyyat"
Cohesion: 0.67
Nodes (3): C. ساخت ۴ نوع ختم, _compose_niyyat(), Owner rule (2026-09-27, DEC-PY-0090): the niyyat is FIXED for every khatm — «به…

### Community 204 - "PlanFeatureUnavailableError"
Cohesion: 0.67
Nodes (3): PlanFeatureUnavailableError, Exception, The active plan does not permit the requested feature.

### Community 206 - "test_devotional_category_navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 209 - "test_devotional_slug_link_does_not_depend_on_title_wording"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_slug_link_does_not_depend_on_title_wording()

### Community 210 - "test_active_categories_are_filtered_by_the_selected_parent_family"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_active_categories_are_filtered_by_the_selected_parent_family()

### Community 252 - "start_broadcast"
Cohesion: 0.36
Nodes (10): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+2 more)

### Community 263 - "resume_join_after_registration"
Cohesion: 0.11
Nodes (33): D. دعوت و عضویت, عضو (Member bots) — تلگرام fa/ar/en و بله, handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload(), _matches_member_bot(), callback_query (+25 more)

### Community 287 - "member_my_khatms.py"
Cohesion: 0.12
Nodes (21): E2 (اولیه) ⬜, E2 — سیستم قاطی نکند: «انجام قرائت امروز» درست ✅ (تأیید ۲۰۲۶-۰۹-۳۰), بخش E — بخش زمان‌بندی و تحویل (بحرانی — احتمالاً بازنویسی کامل), callback_query, CallbackQuery, FSMContext, Member bot "My Khatms" handler — lists khatms the user joined via this bot…, Show the current portion for one joined khatm, with the same action buttons the… (+13 more)

## Knowledge Gaps
- **132 isolated node(s):** `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — DONE`, `4. Reliable modern Persian panel font — DONE`, `Cross-feature validation and delivery log` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1419 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **117 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `app.py`, `create_khatm.py`, `identity/service.py`, `help.py`, `_build_my_khatms_tree`, `resume_join_after_registration`, `phone/service.py`, `portions.py`, `.__call__`, `db.py`, `broadcast.py`, `t`, `AdminFilter`, `KhatmTemplateType`, `_authenticate_telegram_mini_app`, `User`, `resolve_or_provision_user`, `panel.py`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `Participation`, `registration.py`, `AdminPermission`, `test_devotional_text_and_platform_specific_audio`, `safe_answer_callback`, `admin_approve_request`, `decide_manual_phone_request`, `leave.py`, `member_my_khatms.py`, `profile.py`, `start.py`, `Session`, `message_template/__init__.py`, `DevotionalAsset`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `test_member_can_choose_each_creator_and_keeps_exact_member_bot_route`, `UserRole`, `new_id`, `register_devotional_content_batch2.py`, `member_commitment.py`, `join_public_khatm`, `test_creation_price_resolves_fixed_and_usage_based_plan_definitions`, `message_template/repository.py`, `test_registration_starts_in_the_users_saved_language`, `OpenContribution`, `receive_media`, `Khatm`, `operations_page`, `servant_ad/service.py`, `test_devotional_slug_link_does_not_depend_on_title_wording`, `finish_invite_links`, `test_active_categories_are_filtered_by_the_selected_parent_family`, `WalletInvoice`, `confirm_account_deletion`, `cancel_commitment`, `suggestions.py`, `register_devotional_content.py`, `QuranAssetKind`, `join_requests.py`, `start_broadcast`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `Platform` connect `session_scope` to `sqlalchemy`, `app.py`, `create_khatm.py`, `identity/service.py`, `help.py`, `_build_my_khatms_tree`, `resume_join_after_registration`, `phone/service.py`, `portions.py`, `new_id`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`, `broadcast.py`, `t`, `AdminFilter`, `User`, `_authenticate_telegram_mini_app`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `resolve_or_provision_user`, `panel.py`, `Participation`, `registration.py`, `test_deep_link_clears_old_state_before_storing_new_join_context`, `decide_manual_phone_request`, `admin_approve_request`, `safe_answer_callback`, `leave.py`, `member_my_khatms.py`, `profile.py`, `start.py`, `DevotionalAsset`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `broadcast/service.py`, `بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py``, `test_early_regular_share_waits_for_done_before_consuming_schedule`, `member_commitment.py`, `join_public_khatm`, `test_registration_starts_in_the_users_saved_language`, `datetime`, `test_registration_phone_share_only.py`, `OpenContribution`, `receive_media`, `servant_ad/service.py`, `test_quran_setup_waits_for_selected_hour_before_sending`, `test_notify_routing.py`, `finish_invite_links`, `test_bot_commands.py`, `confirm_account_deletion`, `cancel_commitment`, `BotRegistry`, `suggestions.py`, `join_requests.py`, `start_broadcast`, `test_owner_spec_b6_b10.py`, `FakeMessage`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `app.py`, `keyboards.py`, `create_khatm.py`, `identity/service.py`, `help.py`, `_build_my_khatms_tree`, `resume_join_after_registration`, `phone/service.py`, `portions.py`, `test_public_khatms_reply_button_is_wired`, `reminder_engine/service.py`, `KhatmTemplateType`, `bot/__init__.py`, `User`, `session_scope`, `_default_khatm_title`, `resolve_or_provision_user`, `panel.py`, `Participation`, `registration.py`, `test_creator_finance_and_support_buttons_are_wired`, `decide_manual_phone_request`, `admin_approve_request`, `safe_answer_callback`, `leave.py`, `member_my_khatms.py`, `profile.py`, `start.py`, `test_admin_template_render.py`, `DevotionalAsset`, `creator_begin_schedule_date`, `test_home_menu.py`, `member_commitment.py`, `join_public_khatm`, `plan/service.py`, `test_registration_starts_in_the_users_saved_language`, `_compose_niyyat`, `datetime`, `finish_invite_links`, `test_creator_contact.py`, `confirm_account_deletion`, `cancel_commitment`, `suggestions.py`, `test_owner_spec_b1_b5.py`, `join_requests.py`, `test_owner_spec_b6_b10.py`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `t()` (e.g. with `test_both_panel_headers_support_configured_logo_and_fallback()` and `test_creator_detail_renders_manage_stats_members_export_and_settings()`) actually correct?**
  _`t()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 236 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 236 INFERRED edges - model-reasoned connections that need verification._
- **Are the 137 inferred relationships involving `Khatm` (e.g. with `finish_invite_links()` and `send_other_language_links()`) actually correct?**
  _`Khatm` has 137 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — DONE` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._