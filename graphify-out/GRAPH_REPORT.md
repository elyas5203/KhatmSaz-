# Graph Report - Khatm  (2026-09-30)

## Corpus Check
- 458 files · ~332,375 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .css 3, .ini 2, .example 1)

## Summary
- 4002 nodes · 14191 edges · 273 communities (162 shown, 111 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 2093 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78b77601`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- wallet/service.py
- sqlalchemy
- t
- create_khatm.py
- Platform
- get_settings
- my_khatms.py
- Base
- phone/service.py
- portions.py
- new_id
- run_once
- KhatmTemplateType
- resolve_or_provision_user
- Khatm
- User
- Session
- session_scope
- get_or_create
- UserRole
- typing
- sqlalchemy_dialects
- Participation
- bail_if_menu_button
- content/service.py
- app.py
- OWNER_SPEC_MASTER.md
- alembic
- KhatmPortion
- PayPingGateway
- test_navigation_recovery.py
- safe_answer_callback
- khatm_request.py
- test_admin_template_render.py
- list_identities_for_user
- allocation/service.py
- test_admin_web_integration.py
- creator_request/service.py
- KhatmCategory
- provider.py
- DevotionalAsset
- wallet/repository.py
- test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it
- sms_subscription/service.py
- broadcast/service.py
- reminder_engine/service.py
- authorization/service.py
- BotRole
- بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`
- test_early_regular_share_waits_for_done_before_consuming_schedule
- NotificationKind
- wallet.py
- member_commitment.py
- PlanTier
- phone/repository.py
- participation/service.py
- message_template/repository.py
- KhatmSaz VPS Deployment Guide
- test_wizard_ephemeral.py
- bot_registry/service.py
- test_deep_link_clears_old_state_before_storing_new_join_context
- datetime
- open_contribution/repository.py
- Architecture Document
- CHANGELOG
- DECISIONS
- Multi-Bot (26-bot) Architecture
- KhatmRequest
- Admin Panel Base Layout (base.html)
- test_registration_starts_in_the_users_saved_language
- reporting/service.py
- receive_media
- FakeState
- test_recitation_text_only_for_laan.py
- wallet/__init__.py
- main
- servant_ad/service.py
- test_member_bot_fixes.py
- test_quran_setup_waits_for_selected_hour_before_sending
- KhatmSaz Project (Claude Code Instructions)
- test_notify_routing.py
- BotCategory
- invite_links.py
- QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)
- بخش B — تجربهٔ ساخت ختم (بات ختم‌ساز) — «دستِ سازنده باز باشد»
- khatm_workflow/service.py
- _finish_creating_khatm
- WalletInvoice
- finish_invite_links
- BotRegistry Singleton Class
- test_member_commitment_flow.py
- install_command_menu
- test_pro_plan_purchase.py
- test_health.py
- QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی
- confirm_account_deletion
- cancel_commitment
- test_bale_invite_is_a_real_clickable_link_not_a_typed_command
- BotRegistry
- manual_phone_verification/repository.py
- test_dispatcher_routes_commands_while_profile_phone_state_is_active
- asyncio
- suggestions.py
- positional_range_for_step
- test_quran_join_is_member_controlled_without_auto_allocation
- test_fixed_salawat_content.py
- CSS Layouts and Responsive Design Guide
- _commitment_total_keyboard
- پلن بازطراحی ویزارد ساخت ختم + فلوی عضویت (مالک 2026-09-28)
- test_broadcast_shows_khatm_picker
- test_salawat_category_group_always_goes_directly_to_mode
- add_devotional_audio_variant
- set_audio_callback
- Feature checklist
- Member Bot Language Isolation (fixed per bot)
- qr.py
- QuranAssetKind
- test_quran_channel_source.py
- test_creator_notified_with_phone_after_two_consecutive_missed_days
- system_settings/service.py
- test_notification_snooze.py
- Python Requirements
- UserStatus
- assign_quantity_commitment
- register_devotional_content.py
- seed_devotional_texts
- test_owner_spec_b6_b10.py
- test_confirm_wizard_resumes_and_finishes_creation_after_otp
- test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour
- payping_callback
- test_daily_digest_sends_each_khatm_with_its_own_done_button
- FakeMessage
- test_public_khatms_reply_button_is_wired
- help_start_creation
- test_set_font_size_validates_and_persists
- khatmsaz_modules_broadcast
- env.py
- bot/__init__.py
- test_deliver_due_next_portions_pushes_real_content_not_just_text
- test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member
- send_media
- test_next_portion_is_withheld_until_next_local_day_at_reminder_hour
- .__call__
- list_latest_portion_per_participation
- test_creator_dashboard_is_scoped_and_shows_full_member_details
- zzz_merge_three_heads_2026_09_28.py
- _default_khatm_title
- test_previous_month_report_is_positive_localized_and_sent_once
- InvoiceKind
- Mini-App Only Authentication Pattern
- Settings Menu Full-Button Test Scenario
- Codex system audit progress — 2026-09-29
- 435027907255_add_daily_deadline_hour_to_khatms.py
- _wizard_progress
- complete_current_portion_and_advance
- test_devotional_text_and_platform_specific_audio
- test_active_khatm_transitions_to_completed_once
- test_reminder_tone_resolves_seeded_locale_template
- show_member_portion
- delete_account
- message_template/__init__.py
- Tooltip Jinja2 Macro Component
- test_tapping_a_time_of_day_button_saves_the_hour_without_typing
- Bot Help Strings (Persian)
- Identity Across Platforms (phone-based merge key)
- test_skip_today_setting_integration.py
- test_keyboards.py
- PlanFeatureUnavailableError
- start_bot.ps1
- test_devotional_category_navigation.py
- claude_watchdog.sh
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
- start.py
- Admins Management Page
- Audit Log Page
- Broadcasts Admin Page
- Operations/Health Admin Page
- Phone Verifications Admin Page
- Message Templates Admin Page
- deliver_today_early
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
1. `session_scope()` - 394 edges
2. `t()` - 380 edges
3. `Platform` - 301 edges
4. `Khatm` - 159 edges
5. `User` - 142 edges
6. `new_id()` - 139 edges
7. `safe_answer_callback()` - 118 edges
8. `KhatmTemplateType` - 118 edges
9. `resolve_or_provision_user()` - 100 edges
10. `KhatmStatus` - 93 edges

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

## Communities (273 total, 111 thin omitted)

### Community 0 - "wallet/service.py"
Cohesion: 0.10
Nodes (37): PaymentGateway, Protocol, CouponDiscountType, DiscountCoupon, upsert_coupon(), cleanup_expired_pending_payments(), _coupon_discount(), create_payment_intent() (+29 more)

### Community 1 - "sqlalchemy"
Cohesion: 0.07
Nodes (41): khatmsaz_modules_khatm_category, khatmsaz_modules_khatm_category_models, pytest, sqlalchemy, Member bot "My Khatms" handler — lists khatms the user joined via this bot…, Async SQLAlchemy engine/session setup. One engine for the whole process., UUIDv7 generation. The original schema uses app-generated UUIDv7 primary keys…, Content preferences and per-khatm reciter policy. (+33 more)

### Community 2 - "t"
Cohesion: 0.06
Nodes (89): base64, InlineKeyboardButton, help_topic(), list_public_khatms(), message, admin_menu_keyboard(), advertising_choice_keyboard(), cancel_khatm_confirm_keyboard() (+81 more)

### Community 3 - "create_khatm.py"
Cohesion: 0.16
Nodes (52): R6. حذف سؤال ظرفیت — ✅ **انجام شد** (این نوبت), _after_commitment_total(), _after_creator_display(), _after_recitation_text(), _after_start_schedule(), _after_welcome(), _apply_coupon_code(), apply_creation_coupon() (+44 more)

### Community 4 - "Platform"
Cohesion: 0.08
Nodes (49): aiogram, aiogram_filters, aiogram_types, BaseFilter, Small, user-facing Telegram command menu for the primary journeys., AdminFilter, Checks if the user has admin privileges. For now, we simply check if the user…, # TODO: If we want to check for delegated admin roles with specific permissions, (+41 more)

### Community 5 - "get_settings"
Cohesion: 0.07
Nodes (31): aiogram_client_default, aiogram_client_session_aiohttp, aiogram_client_telegram, apscheduler_schedulers_asyncio, BaseMiddleware, functools, logging, pydantic_settings (+23 more)

### Community 6 - "my_khatms.py"
Cohesion: 0.08
Nodes (74): csv, ask_cancel_khatm(), _build_my_khatms_tree(), cancel_cancel_khatm(), confirm_cancel_khatm(), _content_group(), creator_begin_cosmetic_edit(), creator_begin_end_at() (+66 more)

### Community 7 - "Base"
Cohesion: 0.06
Nodes (46): DeclarativeBase, enum, sqlalchemy_dialects_postgresql, sqlalchemy_orm, Base, Shared declarative base for every module's models., Import every module's models so they register on `Base.metadata`. Alembic's…, AccountMerge (+38 more)

### Community 8 - "phone/service.py"
Cohesion: 0.08
Nodes (51): sqlalchemy_exc, begin_phone_change(), ensure_creator_phone_verified(), _lang_for(), FSMContext, Message, Self-service verified phone replacement that keeps all account history., Return true when creation may continue; otherwise start the OTP step. (+43 more)

### Community 9 - "portions.py"
Cohesion: 0.10
Nodes (58): E3 (اولیه) 🔵, E3 — ثبت مشارکت، کاستومِ هر نوع ✅ (تأیید+اصلاح ۲۰۲۶-۰۹-۳۰), _active_participation_for_current_bot(), apply_snooze(), ask_commitment_quantity(), ask_contribution_amount(), ask_custom_pause_until(), ask_custom_snooze() (+50 more)

### Community 10 - "new_id"
Cohesion: 0.04
Nodes (49): new_id(), UUID, Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]` primary-…, uuid7(), asyncio, integration, test_account_deletion_blocks_commitments_then_closes_open_membership(), asyncio (+41 more)

### Community 11 - "run_once"
Cohesion: 0.18
Nodes (24): E1 — تحویل خودکارِ سهم/پیام سرِ تایمِ درست، per-timezone، per-khatm 🔴 CRITICAL ✅ (ممیزی و رفع ۲۰۲۶-۰۹-۳۰), E1 (شرح اولیه) ⬜🔵, ماژول‌های کلیدی (نقشهٔ سریع — با graphify کامل‌تر کن), SendQuranPagesFn, has_started(), Return whether a scheduled khatm is allowed to deliver work yet., get_preference(), _default_reminder_hour() (+16 more)

### Community 12 - "KhatmTemplateType"
Cohesion: 0.06
Nodes (55): D6 — پیامِ جوین اعتمادساز: نامِ سازنده و نیابت ⬜🔵, build_join_preview_message(), build_join_success_message(), _clean_niyyat(), Shared with `join_requests.py`'s approval handler, which sends this same…, Strip a leading «به نیت»/«بنية»/«Intention» so the display label…, Owner complaint (2026-09-20): the old preview only showed title/…, KhatmTemplateType (+47 more)

### Community 13 - "resolve_or_provision_user"
Cohesion: 0.13
Nodes (43): list_member_khatms(), message, CommandObject, message, set_reciter(), buy_sms_plan(), _can_open_creator_panel(), _current_platform_user() (+35 more)

### Community 14 - "Khatm"
Cohesion: 0.11
Nodes (61): Khatm, KhatmStatus, KhatmVisibility, claim_completion_announcement(), create(), get_by_id(), list_created_by(), list_due_endings() (+53 more)

### Community 15 - "User"
Cohesion: 0.05
Nodes (47): MemberRegistration, StatesGroup, PlatformIdentity, User, attach_platform_identity(), create_user_with_platform_identity(), find_by_id(), find_by_platform_identity() (+39 more)

### Community 16 - "Session"
Cohesion: 0.08
Nodes (46): dataclasses, hashlib, hmac, secrets, generate_token(), hash_token(), Opaque token generation/hashing — used by invitations (and later sessions/OTP).…, create_invitation() (+38 more)

### Community 17 - "session_scope"
Cohesion: 0.09
Nodes (72): aiogram_exceptions, admin_activate(), admin_ad_rate(), admin_ban(), admin_coupon_set(), admin_coupon_toggle(), admin_coupons(), admin_covers() (+64 more)

### Community 18 - "get_or_create"
Cohesion: 0.07
Nodes (50): CommandObject, Message, _set_audio(), set_audio_command(), set_content_option(), digest_command(), CommandObject, message (+42 more)

### Community 19 - "UserRole"
Cohesion: 0.10
Nodes (43): A5 — حذف نقش «کریتور» و دکمه‌های ارتقا ✅ (۲۰۲۶-۰۹-۳۰), start_wizard(), help_command(), Message, _resolve_user_info(), admin_panel_keyboard(), creator_panel_keyboard(), _get_context() (+35 more)

### Community 20 - "typing"
Cohesion: 0.04
Nodes (7): # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, add bot_instances Revision ID: b7c8d9e0f1a2 Revises: 33382c085479 Create Date:…, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, # NOTE: autogenerate also proposed dropping the 6 hand-written partial, typing

### Community 22 - "Participation"
Cohesion: 0.13
Nodes (38): _member_creators(), Creators of the member's ACTIVE khatms, each with the member's own…, CommitmentMode, Participation, ParticipationStatus, advance_open_reading(), count_committed_active(), count_for_khatm() (+30 more)

### Community 23 - "bail_if_menu_button"
Cohesion: 0.07
Nodes (64): aiogram_fsm_context, aiogram_fsm_state, AccountLink, begin_account_link(), _lang_for(), FSMContext, message, StatesGroup (+56 more)

### Community 24 - "content/service.py"
Cohesion: 0.14
Nodes (22): KhatmReciter, A creator-approved reciter for one khatm, in display priority order., decode_telegram_forward_ref(), get_allowed_reciters(), get_effective_reciter(), list_all_devotional_assets(), AsyncSession, Quran media registry, reciter whitelist, and user delivery resolution. (+14 more)

### Community 25 - "app.py"
Cohesion: 0.08
Nodes (102): fastapi, fastapi_staticfiles, fastapi_templating, get, post, RedirectResponse, Request, list_recent() (+94 more)

### Community 26 - "OWNER_SPEC_MASTER.md"
Cohesion: 0.08
Nodes (25): C1 — تیکت مخاطب → سازندهٔ ختم (باگ: الان اصلاً کار نمی‌کند) 🔵, C2 — تیکت سازنده → ادمین اصلی 🔵, C3 — متن دکمهٔ تأیید مدیر: بار منفیِ «رد» را بردار ⬜, C4 — دو پیام گروهی رایگان زیرِ ۱۰۰۰ نفر (بله و تلگرام) ⬜, C5 — دسته‌بندی مخاطبانِ پیام گروهی ⬜, C6 — انواع محتوای پیام گروهی ⬜, D1 — «امروز» → «انجام قرائت امروز» (همه‌جا) ⬜, D2 — راهنمای بات‌ها به‌روز و بی‌مغایرت ⬜ (+17 more)

### Community 28 - "KhatmPortion"
Cohesion: 0.12
Nodes (41): CommittedQuantityLog, KhatmPortion, PortionStatus, Per-submission log for quantity-commitment portions (salawat, dua, laan).…, assign_portion(), bulk_create_positional_portions(), bulk_create_positional_portions_from_boundaries(), committed_quantity_total_between() (+33 more)

### Community 29 - "PayPingGateway"
Cohesion: 0.11
Nodes (21): Response, create_topup(), GatewayError, PaymentRequest, PaymentVerification, Exception, Gateway boundary; PSP-specific code must live behind this protocol., The PSP rejected or could not complete a request. (+13 more)

### Community 30 - "test_navigation_recovery.py"
Cohesion: 0.14
Nodes (8): FakeMessage, FakeState, asyncio, parametrize, test_first_language_choice_refreshes_creator_menu_and_starts_wizard(), test_global_cancel_clears_state_and_returns_role_aware_menu(), fake_home(), test_slash_command_is_never_accepted_as_free_text()

### Community 31 - "safe_answer_callback"
Cohesion: 0.18
Nodes (35): C. ساخت ۴ نوع ختم, ask_creation_coupon(), cancel_wizard(), choose_allowed_platforms(), choose_category(), choose_commitment_total(), choose_content_delivery_mode(), choose_creator_display() (+27 more)

### Community 32 - "khatm_request.py"
Cohesion: 0.22
Nodes (19): admin_approve_request(), admin_reject_request(), _lang_for(), callback_query, CallbackQuery, CommandObject, FSMContext, Message (+11 more)

### Community 33 - "test_admin_template_render.py"
Cohesion: 0.08
Nodes (26): alembic_config, alembic_script, ast, pathlib, ScriptDirectory, starlette_requests, _admin(), Render the redesigned admin pages with real Jinja templates. These tests… (+18 more)

### Community 34 - "list_identities_for_user"
Cohesion: 0.25
Nodes (18): approve_join(), _lang_for(), _lang_for_user(), callback_query, CallbackQuery, reject_join(), approve_leave(), ask_leave_reason() (+10 more)

### Community 35 - "allocation/service.py"
Cohesion: 0.17
Nodes (26): AllocationStrategy, KhatmAllocationPlan, PortionUnitKind, str, create_plan(), get_current_assigned_portion(), get_plan_by_khatm(), count_open() (+18 more)

### Community 36 - "test_admin_web_integration.py"
Cohesion: 0.09
Nodes (25): httpx, json, openpyxl, re, AuditLog, Audit records are immutable facts about privileged actions., list_recent(), AsyncSession (+17 more)

### Community 37 - "creator_request/service.py"
Cohesion: 0.13
Nodes (31): Creator-request module: manages requests from users who want to become khatm…, CreatorRequest, CreatorRequestStatus, str, approve(), create(), get_by_id(), get_pending_by_user() (+23 more)

### Community 38 - "KhatmCategory"
Cohesion: 0.15
Nodes (35): KhatmCategory, KhatmCategoryRequest, KhatmCategoryRequestStatus, A participant's typed request for a دعا that isn't in the library yet (owner…, create(), create_request(), get_by_id(), get_request_by_id() (+27 more)

### Community 39 - "provider.py"
Cohesion: 0.10
Nodes (27): BaseSettings, Settings, Pluggable SMS delivery boundary. The application depends on this small…, build_provider(), KavenegarSmsProvider, NoopSmsProvider, AsyncClient, Protocol (+19 more)

### Community 40 - "DevotionalAsset"
Cohesion: 0.14
Nodes (20): deliver_devotional_media(), CommandObject, InlineKeyboardMarkup, Message, Sends every registered piece of media for one devotional asset: PDF, image…, _reciter_picker_keyboard(), send_devotional(), DevotionalAsset (+12 more)

### Community 41 - "wallet/repository.py"
Cohesion: 0.19
Nodes (21): CouponRedemption, InvoiceStatus, PendingPayment, A payment intent created before redirecting to a payment gateway. Prevents IDOR…, claim_pending_payment(), count_coupon_redemptions(), create_coupon_redemption(), create_pending_payment() (+13 more)

### Community 42 - "test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it"
Cohesion: 0.09
Nodes (21): KhatmInvitation, create(), get_by_token_hash(), mark_accepted(), AsyncSession, asyncio, integration, test_committed_quantity_today_vs_yesterday() (+13 more)

### Community 43 - "sms_subscription/service.py"
Cohesion: 0.15
Nodes (28): Admin-managed (duration, price) choice a user can buy., One active (or most-recently-expired) subscription per user., SmsPlanOption, SmsSubscription, get_option(), get_subscription(), list_active_options(), list_newly_expired() (+20 more)

### Community 44 - "broadcast/service.py"
Cohesion: 0.17
Nodes (30): admin_approve_broadcast(), admin_broadcasts(), admin_reject_broadcast(), _is_admin(), _moderate(), CommandObject, message, submit_khatm_message() (+22 more)

### Community 45 - "reminder_engine/service.py"
Cohesion: 0.16
Nodes (22): contribute_keyboard(), portion_done_keyboard(), For a portion that's still PENDING (not completed yet) — shows the content +…, Positive khatm-completion announcements., Scheduled positive personal monthly reports., record_sent(), _maybe_record_miss_and_notify_creator(), _maybe_send_reminder() (+14 more)

### Community 46 - "authorization/service.py"
Cohesion: 0.17
Nodes (23): AdminRole, AdminRoleGrant, CapabilityType, str, A revocable role assignment. Historical rows are reactivated, not deleted., grant_role(), list_active_grants(), AsyncSession (+15 more)

### Community 47 - "BotRole"
Cohesion: 0.20
Nodes (12): khatm_matches_bot(), member_instance_id(), Hard isolation boundary for category-specific member bots., Return the instance id only for member bots; creator bots are unscoped., Keep Quran/Salawat/Dua-Ziyarat/La'an families in their own member bot., BotRole, str, _bot() (+4 more)

### Community 48 - "بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py`"
Cohesion: 0.12
Nodes (11): R1. پیام‌های جای‌گزین‌شونده (کاهش شلوغی چت) — **بدون مایگریشن**, R2. عکس معرفی ختم بعد از انتخاب تعهدی/آزاد — **نیاز به مایگریشن سبک + پنل**, R3. نیت/نیابت با مثال — **بدون مایگریشن** (i18n), R4. تماس سازنده در پیام خوش‌آمد — **نیاز به مایگریشن سبک**, R5. تعهد = تعداد کلِ ختم (نه per-person) با دکمه‌ها — **کد + احتمالاً مایگریشن**, R7. مثال برای هر ۴ مدل متن — **بدون مایگریشن** (i18n), R8. ترتیب پلتفرم: «هر دو» بالا، بعد تلگرام، بعد بله — **بدون مایگریشن**, R9. لینک بعد از تأیید: اول فارسی، بقیه on-request — **بدون مایگریشن** (+3 more)

### Community 49 - "test_early_regular_share_waits_for_done_before_consuming_schedule"
Cohesion: 0.13
Nodes (9): FakeCallback, FakeMessage, asyncio, test_early_regular_share_waits_for_done_before_consuming_schedule(), test_today_lists_khatms_before_delivering_any_share(), fake_khatm(), fake_scope(), fake_settings() (+1 more)

### Community 50 - "NotificationKind"
Cohesion: 0.22
Nodes (21): NotificationKind, NotificationLog, NotificationPreference, count_logs(), create_log(), find_log_since(), get_preference(), AsyncSession (+13 more)

### Community 51 - "wallet.py"
Cohesion: 0.15
Nodes (20): ask_custom_topup(), _create_topup_payment(), _lang_for(), _localized_amount(), open_invoices_from_button(), open_wallet_from_button(), callback_query, CallbackQuery (+12 more)

### Community 52 - "member_commitment.py"
Cohesion: 0.08
Nodes (61): _apply_log(), choose_count(), choose_freq(), choose_hour(), choose_regular(), CommitFlow, confirm_regular_occurrence(), enter_count() (+53 more)

### Community 53 - "PlanTier"
Cohesion: 0.12
Nodes (40): A1 (اولیه) ⬜, A1 — سه پلن با تنظیمات قابل‌ویرایش ادمین ✅ (بک‌بون، ۲۰۲۶-۰۹-۳۰), PlanDefinition, PlanTier, PricingMode, str, Admin-managed pricing and feature entitlements for a plan tier., UserPlan (+32 more)

### Community 54 - "phone/repository.py"
Cohesion: 0.12
Nodes (34): approve(), OtpChallenge, OtpPurpose, PhoneClaim, PhoneClaimStatus, str, create_challenge(), create_or_verify_claim() (+26 more)

### Community 55 - "participation/service.py"
Cohesion: 0.15
Nodes (23): advance_open_reading(), count_for_khatm(), get_active(), get_by_id(), is_paused(), leave(), list_active_for_khatm(), list_active_with_open_reading_plan() (+15 more)

### Community 56 - "message_template/repository.py"
Cohesion: 0.15
Nodes (18): MessageTemplate, create(), get_latest(), list_latest(), list_versions(), next_version(), AsyncSession, Persistence operations for message templates. (+10 more)

### Community 57 - "KhatmSaz VPS Deployment Guide"
Cohesion: 0.16
Nodes (16): DEC-PY-0057 Internal Invoice For Every Purchase, Cloudflare DNS Setup for khatmsaz.com, DNS A Records (api/admin/@), Kavenegar SMS Adapter, PayPing v3 Adapter Integration, Certbot HTTPS / TLS, KhatmSaz VPS Deployment Guide, Production .env File (+8 more)

### Community 58 - "test_wizard_ephemeral.py"
Cohesion: 0.19
Nodes (11): FakeBot, FakeMessage, FakeSent, FakeState, asyncio, R1 (owner 2026-09-28): wizard prompts must replace each other instead of piling…, test_wiz_can_keep_intro_beside_title_until_answered(), test_wiz_deletes_previous_prompt() (+3 more)

### Community 59 - "bot_registry/service.py"
Cohesion: 0.16
Nodes (29): cryptography_fernet, Fernet, BotInstance, get_by_id(), get_by_slot(), list_active(), list_active_members(), list_all() (+21 more)

### Community 60 - "test_deep_link_clears_old_state_before_storing_new_join_context"
Cohesion: 0.14
Nodes (7): test_deep_link_clears_old_state_before_storing_new_join_context(), test_join_preview_cancel_always_acknowledges_callback(), test_plain_start_clears_an_abandoned_state(), fake_scope(), fake_settings(), fake_start_wizard(), fake_user()

### Community 61 - "datetime"
Cohesion: 0.11
Nodes (15): aiogram_enums, aiogram_fsm_storage_memory, contextlib, datetime, inspect, Static Quran edition registry — total page counts per edition. Mirrors the…, Regression for per-khatm broadcast targeting (owner request 2026-09-27):…, Regression (owner live QA 2026-09-28): right after joining a commitment khatm… (+7 more)

### Community 62 - "open_contribution/repository.py"
Cohesion: 0.20
Nodes (16): create(), has_for_participation_since(), AsyncSession, datetime, Persistence access for open_contribution — the only place that runs SQL for…, total_for_khatm(), total_for_khatm_between(), total_for_participation() (+8 more)

### Community 63 - "Architecture Document"
Cohesion: 0.13
Nodes (19): Bootstrap (Process Entrypoint), ModerationMiddleware, Long Polling (vs Webhook), Module Isolation Rule, No Business Rule Invention Rule, PayPing v3 Payment Gateway, Architecture Document, Original Full Project Spec (Persian) (+11 more)

### Community 64 - "CHANGELOG"
Cohesion: 0.08
Nodes (27): Multi-Bot Architecture (26 bots), CHANGELOG Archive (until 2026-09-18), PROJECT_STATE Archive (until 2026-09-18), CHANGELOG, Creator wallet-charge button, Devotional content library + seed, i18n coverage guard (fa/ar/en), Multi-bot invite links (bot/invite_links.py) (+19 more)

### Community 65 - "DECISIONS"
Cohesion: 0.14
Nodes (24): PayPing payment gateway, PendingPayment compare-and-swap replay protection, DECISIONS, DEC-PY-0068 — Kavenegar is first production SMS adapter, DEC-PY-0073 — Dashboards are messenger Mini Apps, DEC-PY-0074 — Free-tier plan caps per-creator, admin-editable, DEC-PY-0076 — Separate participant and creator menus, DEC-PY-0077 — Daily portions stack up (+16 more)

### Community 66 - "Multi-Bot (26-bot) Architecture"
Cohesion: 0.14
Nodes (15): DEC-PY-0060 Public Invite Preview, Join in Bot, DEC-PY-0064 Creator Web Sessions Purpose-Scoped, DECISIONS Archive (DEC-PY-0064 and earlier), Router Classification (creator-only, member-only, shared), Two Dispatcher Architecture (dp_creator + dp_member), BotRegistry & bot_instances Table, Creator Bot, Handler Routing (dual Dispatchers) (+7 more)

### Community 67 - "KhatmRequest"
Cohesion: 0.27
Nodes (16): KhatmRequest, KhatmRequestStatus, str, create(), get_by_id(), list_pending(), AsyncSession, Persistence access for khatm_request — the only place that runs SQL for this… (+8 more)

### Community 68 - "Admin Panel Base Layout (base.html)"
Cohesion: 0.18
Nodes (18): Admin Panel Base Layout (base.html), components.html macros (tooltip), Glassmorphism Dark Design System, Permission-gated Admin Navigation, Admin Categories Page (categories.html), Creator Panel Base Layout (creator_base.html), Creator Panel i18n (t/lang) Localization, Creator Dashboard (creator_dashboard.html) (+10 more)

### Community 69 - "test_registration_starts_in_the_users_saved_language"
Cohesion: 0.08
Nodes (16): ProfileEdit, StatesGroup, StatesGroup, Registration, FakeMessage, FakeState, asyncio, integration (+8 more)

### Community 70 - "reporting/service.py"
Cohesion: 0.20
Nodes (14): OpenContribution, ClosedMonthReport, get_closed_month_report(), get_khatm_stats(), get_personal_report(), KhatmStats, PersonalReport, AsyncSession (+6 more)

### Community 71 - "receive_media"
Cohesion: 0.32
Nodes (8): finish_manage_content(), callback_query, CallbackQuery, FSMContext, message, receive_media(), receive_slug(), start_manage_content()

### Community 73 - "test_recitation_text_only_for_laan.py"
Cohesion: 0.18
Nodes (9): CreateKhatm, StatesGroup, FakeMessage, FakeState, Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر بخواد؛ متن…, _run(), test_dua_does_not_ask_for_recitation_text(), test_laan_asks_for_recitation_text() (+1 more)

### Community 74 - "wallet/__init__.py"
Cohesion: 0.18
Nodes (9): khatmsaz_modules_sms_subscription, khatmsaz_modules_sms_subscription_models, asyncio, Fast safety checks for pending-payment expiry and replay behavior., test_callback_cas_loss_never_credits_wallet(), test_cleanup_delegates_with_current_time_and_reports_count(), test_expired_callback_stops_before_gateway_or_credit(), Financial safety regression for SMS subscription purchases. (+1 more)

### Community 75 - "main"
Cohesion: 0.16
Nodes (11): _build_member_bots(), main(), Bot, _tag_bot(), mark_scan_failed(), mark_scheduler_started(), process_started_at(), datetime (+3 more)

### Community 76 - "servant_ad/service.py"
Cohesion: 0.14
Nodes (22): A3 (staged سابق), A3 — پیامک (SMS) همیشه پولی و درخواستی ✅ (۲۰۲۶-۰۹-۳۰), A4 (staged سابق), A4 — «تبلیغ خدمتگزاران» به مخاطبانِ سازنده‌های BASIC ✅ (۲۰۲۶-۰۹-۳۰), بخش A — پول‌سازی و پلن‌ها (منطق جدید، جایگزین قبلی‌ها), SendFn, audience_size(), _basic_creator_ids() (+14 more)

### Community 77 - "test_member_bot_fixes.py"
Cohesion: 0.09
Nodes (8): asyncio, Regression for the 2026-09-29 member-bot fixes (owner live report): 1. Open-…, E1 audit (2026-09-30): after allocating+sending the next committed-Quran…, Owner report: pages/reminders stopped arriving on member bots. The old…, test_next_portion_delivery_records_daily_reminder_to_prevent_duplicate(), test_niyyat_proxy_strips_repeated_be_niyyat_prefix(), test_reminder_due_fires_at_or_after_target_not_only_in_window(), test_settings_creator_panel_button_visibility()

### Community 78 - "test_quran_setup_waits_for_selected_hour_before_sending"
Cohesion: 0.13
Nodes (4): FakeMessage, FakeState, asyncio, test_quran_setup_waits_for_selected_hour_before_sending()

### Community 79 - "KhatmSaz Project (Claude Code Instructions)"
Cohesion: 0.20
Nodes (14): KhatmSaz Project (Codex Instructions), KhatmSaz Project (Claude Code Instructions), Admin Mini App (Telegram WebApp), AI Handoff Convention (Codex/Claude/Antigravity), i18n System (fa/ar/en), Admin Mini App Guide (Persian), AI Handoff Protocol, Antigravity AI Onboarding Prompt (+6 more)

### Community 80 - "test_notify_routing.py"
Cohesion: 0.20
Nodes (5): FakeBot, FakeRegistry, asyncio, Regression: notifications must go from the correct bot per platform. A user can…, test_notify_does_not_route_member_bot_to_other_platform()

### Community 81 - "BotCategory"
Cohesion: 0.22
Nodes (13): _bot_category_for(), Map a wizard's (template_type, category_group) to the member-bot category value…, BotCategory, asyncio, R2 (owner 2026-09-28): per-bot intro image shown after the creator picks…, test_dua_group_maps_to_dua_ziyarat_bot(), test_intro_caption_present_all_langs(), test_laan_group_maps_to_laan_bot() (+5 more)

### Community 82 - "invite_links.py"
Cohesion: 0.18
Nodes (11): _run_reminder_scan(), build_member_invite_links(), pick_primary_link(), Shared invite-link builder for the multi-bot architecture. A Khatm's invite…, Build member-bot deep links for one khatm token. Returns an ordered dict keyed…, Choose one link to encode in a QR: prefer the creator's language and platform,…, notify(), send_quran_pages() (+3 more)

### Community 83 - "QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)"
Cohesion: 0.17
Nodes (12): A. زیرساخت چندبات (۲۶ بات), B. ثبت‌نام, D. دعوت و عضویت, E. سهم و یادآوری, F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات, G. زبان‌ها (fa/ar/en), H. پرداخت, I. Mini App + پنل ادمین (+4 more)

### Community 84 - "بخش B — تجربهٔ ساخت ختم (بات ختم‌ساز) — «دستِ سازنده باز باشد»"
Cohesion: 0.18
Nodes (11): B10 — پرسش تعهد، کاستومِ هر خانواده ✅, B1 — شلوغیِ ابتدای بات و گیج‌کنندگی سؤال‌ها ✅, B2 — دکمهٔ «ختم صفحات قرآن» → فقط «ختم قرآن» ✅, B3 — دکمهٔ «بازگشت به مرحلهٔ قبل» در کل ویزارد ساخت ✅, B4 — پیام «قابل تغییر است» به‌جای «تغییر ممکن نیست» ✅, B5 — پیام تعداد ختم/دور + آیندهٔ افزایش (پولی، ولی الان رایگان) ✅, B6 — پیام‌های اعتمادساز هنگام ساخت + توضیح گرفتن آیدی ✅, B7 — تک‌پیامِ به‌روزشونده در ساخت ختم (و در جوین ممبر) ✅ (+3 more)

### Community 85 - "khatm_workflow/service.py"
Cohesion: 0.07
Nodes (43): sqlalchemy_ext_asyncio, approve_join_request(), cancel_khatm(), _complete_join(), _count_creator_members(), _enforce_creation_cap(), InvalidCreatorDecisionError, join_via_token() (+35 more)

### Community 86 - "_finish_creating_khatm"
Cohesion: 0.13
Nodes (20): _compose_welcome_with_contact(), _finish_creating_khatm(), _normalize_contact(), Owner-reported bug (2026-09-21/22): a creator whose phone wasn't verified yet…, R4: the creator's contact handle is appended to the welcome text so members…, Accept an @id, a bare id, a t.me/… link, or a phone number and store a clean,…, ContentDeliveryMode, CoverStatus (+12 more)

### Community 87 - "WalletInvoice"
Cohesion: 0.11
Nodes (27): Immutable purchase amounts plus a small paid/refunded lifecycle., Wallet, WalletInvoice, WalletTransaction, bind_invoice_resource(), create_for_user(), get_by_user(), bind_invoice_resource() (+19 more)

### Community 88 - "finish_invite_links"
Cohesion: 0.22
Nodes (11): سازنده (Creator) — تلگرام, finish_invite_links(), handle_confirm_invite_langs(), handle_invite_platform(), handle_toggle_lang(), show_invite_languages_keyboard(), show_invite_platform_keyboard(), format_invite_lines() (+3 more)

### Community 89 - "BotRegistry Singleton Class"
Cohesion: 0.12
Nodes (19): Bale Integration (Telegram-compatible API), Cross-Platform Invitation Links, Telegram Integration (aiogram, long polling), Legacy TypeScript/NestJS KhatmSaz Project, Legacy Reference Rule of Thumb (precedent + confirm), Legacy sendMessage Outbound Failure Bug, Admin Token Panel /bots Route (2-step confirmation), Restart Requirement After Token Change (+11 more)

### Community 90 - "test_member_commitment_flow.py"
Cohesion: 0.26
Nodes (9): importlib_util, _callback_datas(), R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line…, test_count_log_keyboard_callbacks(), test_freq_keyboard_callbacks(), test_hour_keyboard_has_presets_and_custom(), test_hour_keyboard_prefix_matches_handler(), test_mode_keyboard_callbacks() (+1 more)

### Community 91 - "install_command_menu"
Cohesion: 0.25
Nodes (7): install_command_menu(), Bot, Install Telegram's native command picker; Bale parity is unverified., FakeBot, asyncio, test_command_menu_installs_default_and_persian_for_telegram(), test_command_menu_skips_unverified_bale_api_parity()

### Community 92 - "test_pro_plan_purchase.py"
Cohesion: 0.31
Nodes (8): asyncio, parametrize, Plan tier model — OWNER_SPEC_MASTER §A (2026-09-30). Superseded the earlier…, test_ads_enabled_only_on_basic(), test_all_three_tiers_are_active(), test_free_autoupgrades_to_basic_past_cap(), test_get_plan_reads_stored_tier(), test_no_autoupgrade_under_cap_or_not_free()

### Community 93 - "test_health.py"
Cohesion: 0.24
Nodes (8): fastapi_responses, health(), Readiness probe: the HTTP process is useful only while PostgreSQL works., _HealthySession, asyncio, test_health_fails_closed_without_leaking_database_error(), test_health_reports_database_ready(), healthy_scope()

### Community 94 - "QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی"
Cohesion: 0.14
Nodes (14): Live QA — 2026-09-28 (Chrome / Telegram Web / Codex), QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی, ادمین / پنل وب, 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد, رفع‌شدهٔ live-QA (2026-09-28), رفع‌شدهٔ فاز ۲ (این جلسه، با تست), رفع‌شدهٔ همین عصر (Claude Code), ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live) (+6 more)

### Community 95 - "confirm_account_deletion"
Cohesion: 0.28
Nodes (9): cancel_account_deletion(), confirm_account_deletion(), _confirm_keyboard(), _lang_for(), callback_query, CallbackQuery, InlineKeyboardMarkup, message (+1 more)

### Community 96 - "cancel_commitment"
Cohesion: 0.22
Nodes (14): accept_commitment(), cancel_commitment(), _finish_join_prompt(), _parse_delivery_time(), callback_query, CallbackQuery, FSMContext, Message (+6 more)

### Community 97 - "test_bale_invite_is_a_real_clickable_link_not_a_typed_command"
Cohesion: 0.18
Nodes (5): FakeMessage, FakeState, asyncio, integration, test_bale_invite_is_a_real_clickable_link_not_a_typed_command()

### Community 99 - "manual_phone_verification/repository.py"
Cohesion: 0.24
Nodes (14): ManualPhoneVerification, Persistent manual phone-verification requests and their decisions., create(), decide(), get_for_update(), list_pending(), pending_for_user(), AsyncSession (+6 more)

### Community 100 - "test_dispatcher_routes_commands_while_profile_phone_state_is_active"
Cohesion: 0.18
Nodes (5): _command_update(), asyncio, Update, Regression for /profile → /start|/cancel|/public_khatms routing., test_dispatcher_routes_commands_while_profile_phone_state_is_active()

### Community 101 - "asyncio"
Cohesion: 0.15
Nodes (10): asyncio, fixture, os, build_body(), main(), Registers three new devotional texts the owner sent verbatim (2026-09-22): Dua…, get_engine(), dispose_sqlalchemy_pool_after_test() (+2 more)

### Community 102 - "suggestions.py"
Cohesion: 0.11
Nodes (33): A5 (اولیه) ⬜, admin_approve_creator(), admin_reject_creator(), handle_creator_request_button(), handle_creator_request_message(), callback_query, CallbackQuery, CommandObject (+25 more)

### Community 103 - "positional_range_for_step"
Cohesion: 0.33
Nodes (8): positional_range_for_step(), Rotating personal-journey page range (DEC-PY-0092, owner 2026-09-28). Root…, DEC-PY-0092 rotating Quran allocation — proves each committed reader's own…, test_last_portion_clamps_to_total(), test_no_same_day_duplicate_across_members(), test_personal_journey_is_sequential(), test_second_reader_also_sequential_not_jumping(), test_wraps_around_the_book()

### Community 104 - "test_quran_join_is_member_controlled_without_auto_allocation"
Cohesion: 0.27
Nodes (6): asyncio, test_join_via_token_threads_bot_instance_id(), fake_get_khatm(), fake_join(), fake_resolve(), test_quran_join_is_member_controlled_without_auto_allocation()

### Community 105 - "test_fixed_salawat_content.py"
Cohesion: 0.24
Nodes (5): FakeMessage, _plain_salawat(), asyncio, test_plain_salawat_sends_exact_owner_text_without_category(), test_plain_salawat_uses_panel_image_with_fixed_text_caption()

### Community 106 - "CSS Layouts and Responsive Design Guide"
Cohesion: 0.28
Nodes (9): Container Queries, Flexbox (1D layout), CSS Grid (2D layout), Grid Lanes (Masonry), CSS Layouts and Responsive Design Guide, Logical Properties & Intrinsic Sizing, Native Overlays & Anchor Positioning, Overflow Tracking & Layout Stability (+1 more)

### Community 107 - "_commitment_total_keyboard"
Cohesion: 0.20
Nodes (10): _commitment_total_keyboard(), _creator_contact_keyboard(), InlineKeyboardMarkup, R4 (owner 2026-09-28): the creator MUST provide a contact so members can reach…, R5: preset total-goal buttons for a commitment khatm., R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal from…, test_total_keyboard_has_presets_custom_and_unlimited(), test_total_keyboard_translates_custom_unlimited() (+2 more)

### Community 108 - "پلن بازطراحی ویزارد ساخت ختم + فلوی عضویت (مالک 2026-09-28)"
Cohesion: 0.13
Nodes (14): R11/N2 member commitment flow (regular/count), Codex Handoff — Next Steps, PayPing gateway activation (needs owner API token), DEC-PY-0090 — Fixed niyyat + optional niyabat, Minimal-interaction wizard/join redesign (R1-R13), R10. حذف پیش‌نمایش ختم — **بدون مایگریشن**, R11. توضیح دو مدل تعهد (اگر ختم تعهدی) — **کد + مایگریشن (مدل تعهد عضو)**, R12. عضو تعدادی بتواند تعداد جدید بزند — **کد** (+6 more)

### Community 109 - "test_broadcast_shows_khatm_picker"
Cohesion: 0.22
Nodes (5): asyncio, Update, test_broadcast_shows_khatm_picker(), fake_list(), _text_update()

### Community 110 - "test_salawat_category_group_always_goes_directly_to_mode"
Cohesion: 0.20
Nodes (3): _async_value(), asyncio, test_salawat_category_group_always_goes_directly_to_mode()

### Community 111 - "add_devotional_audio_variant"
Cohesion: 0.29
Nodes (7): add_devotional_audio_variant(), add_devotional_image_page(), _get_enabled_devotional_asset(), Owner request (2026-09-22): a dua can have more than one reciter's audio (e.g.…, Owner request (2026-09-22): a dua's image can span more than one page…, Owner request (2026-09-22): a dua's full text as a PDF document — one slot per…, set_devotional_pdf()

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
Cohesion: 0.13
Nodes (24): str, QuranAssetKind, QuranPageAsset, One immutable-addressable media asset for one canonical Quran page., encode_telegram_forward_ref(), parse_quran_channel_caption(), quran_channel_coverage(), Idempotently map one source-channel post to every page it covers. (+16 more)

### Community 117 - "test_quran_channel_source.py"
Cohesion: 0.29
Nodes (4): Verified Telegram message map for the canonical 604-page Quran channel.…, validate_seed(), test_parse_quran_channel_caption_accepts_persian_page_formats(), test_verified_channel_seed_covers_exactly_604_pages()

### Community 118 - "test_creator_notified_with_phone_after_two_consecutive_missed_days"
Cohesion: 0.38
Nodes (6): asyncio, integration, Owner decision (2026-09-22): creator notification must include member's phone…, test_creator_notified_only_after_threshold_and_member_never_notified(), fake_notify(), test_creator_notified_with_phone_after_two_consecutive_missed_days()

### Community 119 - "system_settings/service.py"
Cohesion: 0.23
Nodes (10): middleware, get_int(), get_str(), list_current(), AsyncSession, See `models.py` for why this module exists. `KNOWN_SETTINGS` is the whitelist…, set_int(), set_str() (+2 more)

### Community 120 - "test_notification_snooze.py"
Cohesion: 0.39
Nodes (6): asyncio, test_custom_snooze_accepts_future_timezone_aware_time(), test_custom_snooze_rejects_past_time(), test_snooze_accepts_supported_durations(), fake_set(), test_snooze_rejects_arbitrary_duration()

### Community 121 - "Python Requirements"
Cohesion: 0.29
Nodes (7): aiogram 3.x (Telegram Bot Framework), APScheduler Task Scheduler, FastAPI Web Framework, Jinja2 Template Engine, Redis Client, SQLAlchemy 2.0 ORM, Python Requirements

### Community 122 - "UserStatus"
Cohesion: 0.10
Nodes (28): collections_abc, deliver_pending(), _message(), AsyncSession, datetime, NotifyFn, Idempotent, delayed completion announcements for every platform., Claim each eligible announcement once, then notify creator + active members. (+20 more)

### Community 123 - "assign_quantity_commitment"
Cohesion: 0.33
Nodes (6): add_quantity_commitment_portion(), count_all(), increment_plan_total(), A fixed per-participant quantity commitment (e.g. "you commit to 1000…, assign_quantity_commitment(), A fixed per-participant quantity commitment (e.g. SALAWAT COMMITMENT mode:…

### Community 124 - "register_devotional_content.py"
Cohesion: 0.48
Nodes (6): build_salawat_text(), build_ziyarat_ashura_text(), main(), _pair(), One-off content-registration script — run manually, not part of the app.…, sys

### Community 125 - "seed_devotional_texts"
Cohesion: 0.33
Nodes (6): _chunk(), AsyncSession, Greedily pack blank-line-separated paragraphs into <=limit chunks, joined by…, Idempotently upsert every curated devotional text. Safe to run on every startup…, seed_devotional_texts(), register_devotional_text()

### Community 126 - "test_owner_spec_b6_b10.py"
Cohesion: 0.07
Nodes (26): Creator-to-member message moderation boundary., خدمتگزاران system promo ads (owner §A4). Admin-defined promotional message…, asyncio, test_all_three_channel_policies_are_admin_backed(), test_submit_all_targets_distinct_audience_and_uses_channel_policy(), test_submit_requires_supported_channel_and_nonempty_audience(), _message(), asyncio (+18 more)

### Community 127 - "test_confirm_wizard_resumes_and_finishes_creation_after_otp"
Cohesion: 0.11
Nodes (8): ChangePhone, StatesGroup, set_registry(), FakeCallback, FakeMessage, FakeState, integration, test_confirm_wizard_resumes_and_finishes_creation_after_otp()

### Community 128 - "test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour()

### Community 129 - "payping_callback"
Cohesion: 0.40
Nodes (5): HTMLResponse, _payment_gateway(), _payment_result_page(), payping_callback(), Receive PayPing's form POST and credit the bound wallet exactly once.

### Community 132 - "test_public_khatms_reply_button_is_wired"
Cohesion: 0.29
Nodes (4): asyncio, Update, test_public_khatms_reply_button_is_wired(), _text_update()

### Community 133 - "help_start_creation"
Cohesion: 0.50
Nodes (5): help_open_my_khatms(), help_start_creation(), callback_query, CallbackQuery, FSMContext

### Community 134 - "test_set_font_size_validates_and_persists"
Cohesion: 0.32
Nodes (4): asyncio, test_set_font_size_validates_and_persists(), test_set_language_validates_and_normalizes(), fake_get_or_create()

### Community 136 - "env.py"
Cohesion: 0.50
Nodes (3): logging_config, do_run_migrations(), run_migrations_online()

### Community 137 - "bot/__init__.py"
Cohesion: 0.33
Nodes (3): parametrize, Regression: the create-khatm wizard keyboards were hardcoded Persian, so a…, test_every_wizard_keyboard_is_localized_and_cancellable()

### Community 138 - "test_deliver_due_next_portions_pushes_real_content_not_just_text"
Cohesion: 0.33
Nodes (4): _iana_offset_for_local_hour(), asyncio, integration, test_deliver_due_next_portions_pushes_real_content_not_just_text()

### Community 139 - "test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member"
Cohesion: 0.47
Nodes (5): asyncio, integration, test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member(), notify(), test_completion_grace_allows_reopen_and_creator_can_disable_message()

### Community 140 - "send_media"
Cohesion: 0.50
Nodes (4): A2 (اولیه/staged سابق), A2 — پیام تبلیغاتی سازنده به مخاطبانش (پیام‌رسان، متن/عکس/فیلم/ویس) ✅ (۲۰۲۶-۰۹-۳۰), Deliver a photo/video/voice/document by file_id (owner §A2 promo media).…, send_media()

### Community 141 - "test_next_portion_is_withheld_until_next_local_day_at_reminder_hour"
Cohesion: 0.33
Nodes (5): _iana_offset_for_local_hour(), asyncio, integration, A fixed-offset IANA zone (Etc/GMT sign convention is inverted: `Etc/GMT-N` is…, test_next_portion_is_withheld_until_next_local_day_at_reminder_hour()

### Community 142 - ".__call__"
Cohesion: 0.50
Nodes (3): Any, CallbackQuery, Message

### Community 143 - "list_latest_portion_per_participation"
Cohesion: 0.50
Nodes (4): list_latest_portion_per_participation(), Owner request (2026-09-26): "portions should advance daily regardless of…, list_latest_portion_per_participation(), See `repository.list_latest_portion_per_participation`.

### Community 144 - "test_creator_dashboard_is_scoped_and_shows_full_member_details"
Cohesion: 0.67
Nodes (4): asyncio, integration, test_creator_dashboard_is_scoped_and_shows_full_member_details(), test_open_contribution_persists_counted_and_surplus_split()

### Community 145 - "zzz_merge_three_heads_2026_09_28.py"
Cohesion: 0.40
Nodes (4): downgrade(), No-op: merge revision only unifies history., No-op: splitting back into three heads is not supported., upgrade()

### Community 146 - "_default_khatm_title"
Cohesion: 0.50
Nodes (4): _default_khatm_title(), Build the standard title without asking the creator an extra question., test_devotional_title_uses_selected_category(), test_quran_title_is_automatic()

### Community 147 - "test_previous_month_report_is_positive_localized_and_sent_once"
Cohesion: 0.50
Nodes (3): asyncio, integration, test_previous_month_report_is_positive_localized_and_sent_once()

### Community 150 - "InvoiceKind"
Cohesion: 0.23
Nodes (16): accrue_first_completed_action(), Grant one reward only after the first completed assigned action. The…, InvoiceKind, str, TxType, add_balance(), add_credit(), create_paid_invoice() (+8 more)

### Community 152 - "Mini-App Only Authentication Pattern"
Cohesion: 0.67
Nodes (4): Mini-App Only Authentication Pattern, Creator Login Page, Admin Login Page, Telegram Mini-App Auth Login Page

### Community 153 - "Settings Menu Full-Button Test Scenario"
Cohesion: 0.67
Nodes (4): Settings Menu Full-Button Test Scenario, Tone Checklist for i18n Strings (9-point), Tone Guide: Khanom Batool 80yo Persona, UX Writing Principles for Elderly Users

### Community 154 - "Codex system audit progress — 2026-09-29"
Cohesion: 0.40
Nodes (4): Codex system audit progress — 2026-09-29, Delivery log, Evidence gathered, Requirements

### Community 156 - "_wizard_progress"
Cohesion: 0.67
Nodes (3): Show non-personal choices above the current question (B7)., _wizard_progress(), test_b7_progress_summary_contains_choices_not_contact_data()

### Community 157 - "complete_current_portion_and_advance"
Cohesion: 0.67
Nodes (3): complete_portion(), complete_current_portion_and_advance(), Mark the participant's currently-assigned portion complete. Owner decision…

### Community 158 - "test_devotional_text_and_platform_specific_audio"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_devotional_text_and_platform_specific_audio()

### Community 159 - "test_active_khatm_transitions_to_completed_once"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_active_khatm_transitions_to_completed_once()

### Community 160 - "test_reminder_tone_resolves_seeded_locale_template"
Cohesion: 0.67
Nodes (3): asyncio, integration, test_reminder_tone_resolves_seeded_locale_template()

### Community 161 - "show_member_portion"
Cohesion: 0.33
Nodes (7): callback_query, CallbackQuery, FSMContext, Show the current portion for one joined khatm, with the same action buttons the…, Per-khatm reminder-hour picker. Reuses the shared AskDeliveryHour flow…, show_member_portion(), show_member_reminder_hours()

### Community 162 - "delete_account"
Cohesion: 0.33
Nodes (5): AccountDeletionBlocked, delete_account(), Exception, Safely deactivate a user while retaining non-PII history. Active committed…, The account still owns an obligation that must be resolved first.

### Community 163 - "message_template/__init__.py"
Cohesion: 0.18
Nodes (8): Localized, versioned message templates., Real PostgreSQL coverage for template history and activation control., asyncio, parametrize, test_render_replaces_known_placeholders_and_preserves_unknown(), fake_get_latest(), test_render_uses_fallback_locale(), test_validate_body_rejects_unknown_or_malformed_placeholders()

### Community 164 - "Tooltip Jinja2 Macro Component"
Cohesion: 0.50
Nodes (4): Tooltip Jinja2 Macro Component, Khatm Detail Admin Page, Khatms List Admin Page, Users Admin Page

### Community 165 - "test_tapping_a_time_of_day_button_saves_the_hour_without_typing"
Cohesion: 0.29
Nodes (4): FakeState, asyncio, integration, test_tapping_a_time_of_day_button_saves_the_hour_without_typing()

### Community 166 - "Bot Help Strings (Persian)"
Cohesion: 0.67
Nodes (3): Khatm Types: Commitment/Free/Public/Private, Bot Help Strings (Persian), Bot Welcome Message

### Community 167 - "Identity Across Platforms (phone-based merge key)"
Cohesion: 0.67
Nodes (3): Identity Across Platforms (phone-based merge key), SMS Integration (Kavenegar adapter), Cross-Bot User Recognition (same platform_identities row)

### Community 204 - "PlanFeatureUnavailableError"
Cohesion: 0.67
Nodes (3): PlanFeatureUnavailableError, Exception, The active plan does not permit the requested feature.

### Community 206 - "test_devotional_category_navigation.py"
Cohesion: 0.83
Nodes (3): _button_pairs(), test_creation_menu_exposes_devotional_families_as_independent_parents(), test_each_parent_keyboard_contains_only_supplied_children()

### Community 252 - "start_broadcast"
Cohesion: 0.36
Nodes (10): cancel_broadcast(), choose_broadcast_target(), confirm_broadcast(), callback_query, CallbackQuery, FSMContext, message, Owner request (2026-09-27): before composing, let the creator pick WHICH… (+2 more)

### Community 263 - "start.py"
Cohesion: 0.08
Nodes (52): عضو (Member bots) — تلگرام fa/ar/en و بله, html, handle_member_cancel(), handle_member_join_callback(), handle_member_start(), handle_member_start_with_payload(), _matches_member_bot(), callback_query (+44 more)

### Community 287 - "deliver_today_early"
Cohesion: 0.20
Nodes (10): E2 (اولیه) ⬜, E2 — سیستم قاطی نکند: «انجام قرائت امروز» درست ✅ (تأیید ۲۰۲۶-۰۹-۳۰), بخش E — بخش زمان‌بندی و تحویل (بحرانی — احتمالاً بازنویسی کامل), deliver_today_early(), callback_query, CallbackQuery, Deliver one selected khatm now and mark today's scheduled send consumed., today_overview() (+2 more)

## Knowledge Gaps
- **133 isolated node(s):** `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — DONE`, `4. Reliable modern Persian panel font — DONE`, `Cross-feature validation and delivery log` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1409 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **111 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `session_scope()` connect `session_scope` to `test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour`, `sqlalchemy`, `t`, `create_khatm.py`, `Platform`, `get_settings`, `my_khatms.py`, `start.py`, `phone/service.py`, `portions.py`, `payping_callback`, `new_id`, `KhatmTemplateType`, `resolve_or_provision_user`, `.__call__`, `Khatm`, `User`, `test_deliver_due_next_portions_pushes_real_content_not_just_text`, `get_or_create`, `UserRole`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`, `test_creator_dashboard_is_scoped_and_shows_full_member_details`, `Session`, `bail_if_menu_button`, `test_previous_month_report_is_positive_localized_and_sent_once`, `app.py`, `PayPingGateway`, `test_devotional_text_and_platform_specific_audio`, `safe_answer_callback`, `khatm_request.py`, `show_member_portion`, `list_identities_for_user`, `deliver_today_early`, `test_admin_web_integration.py`, `allocation/service.py`, `KhatmCategory`, `test_tapping_a_time_of_day_button_saves_the_hour_without_typing`, `DevotionalAsset`, `test_active_khatm_transitions_to_completed_once`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `test_reminder_tone_resolves_seeded_locale_template`, `broadcast/service.py`, `authorization/service.py`, `wallet.py`, `member_commitment.py`, `PlanTier`, `phone/repository.py`, `message_template/repository.py`, `test_registration_starts_in_the_users_saved_language`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `receive_media`, `reporting/service.py`, `main`, `invite_links.py`, `_finish_creating_khatm`, `WalletInvoice`, `finish_invite_links`, `test_health.py`, `confirm_account_deletion`, `cancel_commitment`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `manual_phone_verification/repository.py`, `asyncio`, `suggestions.py`, `register_devotional_content.py`, `QuranAssetKind`, `test_creator_notified_with_phone_after_two_consecutive_missed_days`, `system_settings/service.py`, `start_broadcast`, `test_confirm_wizard_resumes_and_finishes_creation_after_otp`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `sqlalchemy`, `create_khatm.py`, `Platform`, `test_public_khatms_reply_button_is_wired`, `my_khatms.py`, `start.py`, `phone/service.py`, `portions.py`, `bot/__init__.py`, `run_once`, `KhatmTemplateType`, `resolve_or_provision_user`, `User`, `_default_khatm_title`, `UserRole`, `get_or_create`, `bail_if_menu_button`, `app.py`, `_wizard_progress`, `PayPingGateway`, `safe_answer_callback`, `khatm_request.py`, `show_member_portion`, `list_identities_for_user`, `deliver_today_early`, `test_admin_template_render.py`, `DevotionalAsset`, `reminder_engine/service.py`, `wallet.py`, `member_commitment.py`, `PlanTier`, `test_registration_starts_in_the_users_saved_language`, `test_member_bot_fixes.py`, `_finish_creating_khatm`, `finish_invite_links`, `confirm_account_deletion`, `cancel_commitment`, `suggestions.py`, `_commitment_total_keyboard`, `test_owner_spec_b6_b10.py`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `Platform` connect `Platform` to `test_open_quran_reading_auto_delivers_once_per_day_at_chosen_hour`, `sqlalchemy`, `create_khatm.py`, `get_settings`, `my_khatms.py`, `start.py`, `phone/service.py`, `portions.py`, `test_deliver_due_next_portions_pushes_real_content_not_just_text`, `test_completion_announcement_waits_is_idempotent_and_reaches_creator_and_member`, `send_media`, `resolve_or_provision_user`, `test_next_portion_is_withheld_until_next_local_day_at_reminder_hour`, `User`, `Session`, `session_scope`, `get_or_create`, `UserRole`, `test_previous_month_report_is_positive_localized_and_sent_once`, `bail_if_menu_button`, `app.py`, `PayPingGateway`, `test_navigation_recovery.py`, `safe_answer_callback`, `khatm_request.py`, `show_member_portion`, `list_identities_for_user`, `deliver_today_early`, `DevotionalAsset`, `test_fresh_committed_quran_join_asks_delivery_hour_and_saves_it`, `broadcast/service.py`, `بخش سازنده (ویزارد ساخت ختم) — `create_khatm.py``, `test_early_regular_share_waits_for_done_before_consuming_schedule`, `wallet.py`, `member_commitment.py`, `phone/repository.py`, `test_registration_starts_in_the_users_saved_language`, `receive_media`, `servant_ad/service.py`, `test_quran_setup_waits_for_selected_hour_before_sending`, `test_notify_routing.py`, `invite_links.py`, `_finish_creating_khatm`, `finish_invite_links`, `install_command_menu`, `confirm_account_deletion`, `cancel_commitment`, `test_bale_invite_is_a_real_clickable_link_not_a_typed_command`, `BotRegistry`, `suggestions.py`, `test_creator_notified_with_phone_after_two_consecutive_missed_days`, `UserStatus`, `start_broadcast`, `test_owner_spec_b6_b10.py`, `test_confirm_wizard_resumes_and_finishes_creation_after_otp`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `t()` (e.g. with `test_both_panel_headers_support_configured_logo_and_fallback()` and `test_creator_detail_renders_manage_stats_members_export_and_settings()`) actually correct?**
  _`t()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 236 inferred relationships involving `Platform` (e.g. with `build_bale_bot()` and `install_command_menu()`) actually correct?**
  _`Platform` has 236 INFERRED edges - model-reasoned connections that need verification._
- **Are the 135 inferred relationships involving `Khatm` (e.g. with `finish_invite_links()` and `send_other_language_links()`) actually correct?**
  _`Khatm` has 135 INFERRED edges - model-reasoned connections that need verification._
- **What connects `claude_watchdog.sh script`, `2. Real FREE → PRO purchase — DONE`, `3. Configurable panel logo — DONE` to the rest of the system?**
  _133 weakly-connected nodes found - possible documentation gaps or missing edges._