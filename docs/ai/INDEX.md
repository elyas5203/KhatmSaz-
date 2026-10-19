## 2026-10-19 — Finance, Subscription Plans, Member Caps & Tariffs Hub (MASTER-49) [Antigravity]
- Master Document: [MASTER_49_FINANCE_PLANS_AND_TARIFFS_HUB.md](masters/MASTER_49_FINANCE_PLANS_AND_TARIFFS_HUB.md) (Centralized finance, subscription plans, member caps and tariffs hub `/finance` in web admin, 4 KPI cards, PayPing gateway connectivity and direct Shaparak payment link `https://ppng.ir/d/VFBD`, advanced invoice filtering and two-step refunds, 3-tier creator subscription plans with devotional member caps (100) and Quran member caps (302), broadcast tariffs (150,000 Toman / 1,000 members), and links to User 360 and Coupons hub).
- Key files: `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/finance.html`, `src/khatmsaz/modules/plan/`, `src/khatmsaz/modules/wallet/`, `src/khatmsaz/modules/broadcast/`.
- Tests: `tests/test_master_49_finance_hub.py`.

## 2026-10-19 — Bot Fleet Diagnostics & Real-Time System Health Hub (MASTER-48) [Antigravity]
- Master Document: [MASTER_48_BOT_FLEET_DIAGNOSTICS_AND_HEALTH_HUB.md](masters/MASTER_48_BOT_FLEET_DIAGNOSTICS_AND_HEALTH_HUB.md) (Unified operations and diagnostics command center `/operations` in web admin, real-time ping and latency testing across 18 Telegram and Bale bots, manual scheduler scan trigger with audit trail, and live error log console).
- Key files: `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/operations.html`, `src/khatmsaz/modules/bot_registry/service.py`, `src/khatmsaz/core/bot_registry.py`.
- Tests: `tests/test_master_48_diagnostics_hub.py`.

## 2026-10-19 — Advanced Analytics & Reporting Hub and Excel Export Engine (MASTER-47) [Antigravity]
- Master Document: [MASTER_47_ADVANCED_ANALYTICS_AND_REPORTING_HUB.md](masters/MASTER_47_ADVANCED_ANALYTICS_AND_REPORTING_HUB.md) (Centralized analytics and reporting hub `/reports` in web admin, 4 KPI cards with today vs yesterday trends, 5-family devotional reception matrix, platform distribution, top khatms highlights, and 3 global Excel export endpoints for khatms, users, and finances).
- Key files: `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/reports.html`, `src/khatmsaz/web/templates/base.html`, `src/khatmsaz/modules/reporting/`.
- Tests: `tests/test_master_47_reports_hub.py`.

## 2026-10-18 — Advertising, Banner Hub & Moderation Queue in Web Admin and Bot Delivery (MASTER-46) [Antigravity]
- Master Document: [MASTER_46_ADVERTISING_AND_BANNER_HUB.md](masters/MASTER_46_ADVERTISING_AND_BANNER_HUB.md) (Centralized advertising and banner management hub `/banners` in web admin, 4 KPI cards, banner creation with SYSTEM_CULTURAL and COMMERCIAL_AD types, zero-data-loss active/inactive toggle, Queue 5 `/moderation?tab=banners` for creator-submitted banners with auto-refund on rejection, and bot occurrence delivery with ethical khatm advertising controls).
- Key files: `src/khatmsaz/modules/advertising/`, `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/banners.html`, `src/khatmsaz/web/templates/moderation.html`, `src/khatmsaz/bot/occurrence_adapter.py`.
- Tests: `tests/test_master_46_advertising_hub.py`.

## 2026-10-18 — Discount Coupons, Campaign Hub & Redemption Ledger in Web Admin (MASTER-45) [Antigravity]
- Master Document: [MASTER_45_DISCOUNT_COUPONS_AND_CAMPAIGN_HUB.md](masters/MASTER_45_DISCOUNT_COUPONS_AND_CAMPAIGN_HUB.md) (Dedicated coupons and campaign management hub `/coupons` in web admin, campaign KPIs, coupon creation with percent/fixed models and ceilings, zero-data-loss active/inactive toggling, user redemption ledger table linking to user 360 profile, and coupon redemption analytics).
- Key files: `src/khatmsaz/modules/wallet/repository.py`, `src/khatmsaz/modules/wallet/service.py`, `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/coupons.html`, `src/khatmsaz/web/templates/base.html`.
- Tests: `tests/test_master_45_coupons_hub.py`.

## 2026-10-18 — User 360 Profile & Financial Wallet Management Hub in Web Admin (MASTER-44) [Antigravity]
- Master Document: [MASTER_44_USER_360_PROFILE_AND_WALLET_MANAGEMENT.md](masters/MASTER_44_USER_360_PROFILE_AND_WALLET_MANAGEMENT.md) (360-degree user profile `/users/{user_id}` in web admin, user identity, connected Telegram/Bale accounts, verified phone claim, user settings, current plan, financial wallets, created khatms, participations, support tickets, wallet manual adjustment with cash vs credit selection, and automated bot notifications).
- Key files: `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/user_detail.html`, `src/khatmsaz/web/templates/users.html`.
- Tests: `tests/test_master_44_user_profile.py`.

## 2026-10-18 — Admin Khatm Management, Direct Ownership Transfer & Intelligent Status Notifications (MASTER-43) [Antigravity]
- Master Document: [MASTER_43_ADMIN_KHATM_MANAGEMENT_AND_DIRECT_CONTROLS.md](masters/MASTER_43_ADMIN_KHATM_MANAGEMENT_AND_DIRECT_CONTROLS.md) (Direct khatm ownership transfer to any user by Super Admin without verified phone restriction, automatic invite link rotation and two-way notifications, courteous status change notices to creator and active members upon ACTIVE/COMPLETED/CANCELLED, and web panel alert banners).
- Key files: `src/khatmsaz/modules/khatm_workflow/service.py`, `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/khatm_detail.html`.
- Tests: `tests/test_master_43_khatm_management.py`.

## 2026-10-18 — Support Tickets & Direct Messaging Hub (MASTER-42) [Antigravity]
- Master Document: [MASTER_42_SUPPORT_TICKETS_AND_DIRECT_MESSAGING.md](masters/MASTER_42_SUPPORT_TICKETS_AND_DIRECT_MESSAGING.md) (Support ticket database model, Queue 8 in Web Admin Panel /moderation?tab=tickets, direct admin reply dispatch to user chat via notify_adapter, status lifecycle PENDING/ANSWERED/CLOSED, and bot suggestions integration).
- Key files: `src/khatmsaz/modules/support_ticket/`, `src/khatmsaz/web/app.py`, `src/khatmsaz/web/templates/moderation.html`, `src/khatmsaz/bot/handlers/suggestions.py`.
- Tests: `tests/test_master_42_support_tickets.py`.

## 2026-10-18 — سازندهٔ سادهٔ پرامپت و مستر [Codex]
- فرم آفلاین با یک خواستهٔ ضروری و خروجی پرامپت/پیش‌نویس مستر: `../../SUBAGENT_SWARM_BUILDER.html`. پرامپت مسترهای موجود را بررسی می‌کند؛ راهنمای SUBAGENT_SWARM_50.md در این checkout موجود نیست و اجرای آن باید مشروط گزارش شود.

## 2026-10-17 — Creator Broadcast & Wallet Recharge Overhaul (MASTER-38) [Antigravity]
- Master Document: [MASTER_38_CREATOR_BROADCAST_AND_WALLET_RECHARGE.md](masters/MASTER_38_CREATOR_BROADCAST_AND_WALLET_RECHARGE.md) (Direct broadcast button in Khatm Management, 150-Toman per-recipient pricing formula, transparent copy, and 4 wallet top-up packages: 50k, 100k, 500k, and custom).
- Key files: `src/khatmsaz/bot/keyboards.py`, `src/khatmsaz/bot/handlers/creator_broadcast.py`, `src/khatmsaz/modules/broadcast/service.py`, `src/khatmsaz/bot/handlers/wallet.py`.
- Tests: `tests/test_master_38_creator_broadcast_and_wallet_recharge.py`.

## 2026-10-17 — Open Mode Content Delivery Master (Khutbah & Dua) [Antigravity]
- Master Document: [OPEN_MODE_CONTENT_DELIVERY_MASTER.md](OPEN_MODE_CONTENT_DELIVERY_MASTER.md) (Open mode delivery, Khutbah section allocation & video captions, Dua single-asset multi-round button, and strict AI prohibitions)


## 2026-10-15 — Foreign shared-contact registration
- DEC-PY-0129 and [MASTER-33](masters/MASTER_34_FOREIGN_SHARED_CONTACT_IMMEDIATE.md): Telegram contact normalization, immediate foreign claim, Iranian OTP and production deployment gate. Existing broader rule: [MASTER-22](masters/MASTER_22_FOREIGN_PHONE_DIRECT_VERIFICATION.md).

## 2026-10-14 — Real-Time Dual-Platform Media Mirroring (MASTER-20)
- [MASTER_20_REALTIME_DUAL_PLATFORM_MEDIA_MIRRORING.md](masters/MASTER_20_REALTIME_DUAL_PLATFORM_MEDIA_MIRRORING.md) — Real-time background cross-platform media streaming (Telegram to Bale), auto-mirroring on `/set_video`, `/set_pdf`, `/set_audio`, and `/manage_content`, direct multipart upload, automatic cleanup of temporary storage messages, and Super Admin filter auto-authorization across bots.
- تصمیم محصول: `DEC-PY-0128` در [DECISIONS.md](DECISIONS.md).

## 2026-10-13 — مهاجرت خودکار رسانه‌ها از تلگرام به بله
- سند مستر: [TELEGRAM_TO_BALE_MIGRATION_MASTER.md](TELEGRAM_TO_BALE_MIGRATION_MASTER.md)
- تصمیم محصول: DEC-PY-0127 در `DECISIONS.md`.
- موتور هسته: `src/khatmsaz/modules/content/migrator.py` (`TelegramToBaleMigrator`, `get_bale_quran_coverage`).
- اسکریپت خط فرمان: `scripts/migrate_telegram_to_bale.py`.
- دستورات ادمین بات: `/admin_bale_media_status` و `/admin_sync_bale` در `src/khatmsaz/bot/handlers/admin.py`.
- تست‌ها: `tests/test_telegram_to_bale_migration.py`.

## 2026-10-13 — Dedicated Admin Bot (@khatmsaz_admin_bot), Real-Time Crash Monitoring & Custom La'n Wizard Master
- [MASTER_12_DEDICATED_ADMIN_BOT_AND_LIVE_ERROR_MONITORING.md](masters/MASTER_12_DEDICATED_ADMIN_BOT_AND_LIVE_ERROR_MONITORING.md) — Dedicated Admin Bot (`@khatmsaz_admin_bot`), complete isolation of admin functions from creator bot, live continuous file logging, real-time Telegram crash/error dispatch to super admin, custom La'n title & dhikr prompts, moderation queue, automated invitation delivery upon admin approval, direct PayPing Shaparak checkout link (`ppng.ir/d/VFBD`), card number removal, and 8-digit numeric tracking codes.

## 2026-10-13 — Laan Wizard Redesign, Direct PayPing, Numeric Tracking Code & Centralized Admin Bot Dispatch Master
- [MASTER_11_LAAN_WIZARD_DIRECT_PAYPING_AND_ADMIN_BOT_DISPATCH.md](masters/MASTER_11_LAAN_WIZARD_DIRECT_PAYPING_AND_ADMIN_BOT_DISPATCH.md) — Elimination of preset Laan options, custom title & recitation dhikr prompt, moderation queue, automated invitation delivery upon admin approval, direct PayPing checkout link (`ppng.ir/d/VFBD`), card number removal, 8-digit numeric tracking codes, and centralized admin dispatch.

## 2026-10-13 — Plans, Broadcast 1000-Tier Pricing, Receipt Upload & Creator Panel Guard Master
- [MASTER_10_PLANS_BROADCAST_RECEIPT_PAYMENT_AND_CREATOR_PANEL_GUARD.md](masters/MASTER_10_PLANS_BROADCAST_RECEIPT_PAYMENT_AND_CREATOR_PANEL_GUARD.md) — Broadcast 1,000-recipient ceiling tiers, complete removal of free broadcasts, bank receipt upload & admin approval, PayPing direct link architecture & admin-only creator panel guard.

## 2026-10-11 — Bale Native Markdown Adapter & Clean Tag Rendering Master
- [MASTER_09_BALE_ADAPTER_AND_MARKDOWN_COMPATIBILITY.md](masters/MASTER_09_BALE_ADAPTER_AND_MARKDOWN_COMPATIBILITY.md) — Bale messenger HTML-to-Markdown conversion engine, low-level `BaleAiohttpSession` request interceptor, removal of unrendered HTML tags across Bale fleet & simplified button-free member daily 14:00 digest.

## 2026-10-11 — Member Daily Progress Digest at 14:00 & Motivational Progress Master
- [MASTER_07_MEMBER_DAILY_DIGEST_AND_MOTIVATIONAL_PROGRESS.md](masters/MASTER_07_MEMBER_DAILY_DIGEST_AND_MOTIVATIONAL_PROGRESS.md) — 14:00 Tehran daily progress digest to active members via member bots, post-completion motivational progress snippet & button-free clean layout.

## 2026-10-11 — Khutbah Ghadir 8-Part Trio & Creator Daily 12:00 PM Report Master
- [KHUTBAH_GHADIR_AND_CREATOR_DAILY_REPORT_MASTER.md](KHUTBAH_GHADIR_AND_CREATOR_DAILY_REPORT_MASTER.md) — 8-part Khutbah Ghadir multi-media trio (Video+PDF+Audio), canonical seeding, Telegram commands & 12:00 PM creator daily report.

## 2026-10-11 — Payment Gateway Architecture Master & In-Bot Verification
- [MASTER_06_PAYMENT_GATEWAY_AND_CALLBACK_ARCHITECTURE.md](masters/MASTER_06_PAYMENT_GATEWAY_AND_CALLBACK_ARCHITECTURE.md) — PayPing v3 lifecycle, `ERR_TIMED_OUT` mobile carrier analysis, Apache 443 reverse proxy hardening, Port stability guarantees, In-bot self-healing verification (`wallet_check`).

## 2026-10-10 — Admin Panel Redesign Master (Parent-Child Architecture) & Bug Report Master
- **Parent Master:** [ADMIN_PANEL_REDESIGN_MASTER.md](ADMIN_PANEL_REDESIGN_MASTER.md)
- **Child Masters (`docs/ai/masters/`):**
  - [MASTER_01_KHATM_ENGINE_AND_MODES.md](masters/MASTER_01_KHATM_ENGINE_AND_MODES.md) — Khatm types, Commitment vs Open, Fixed vs Member-Choice, Numeric vs Regular, `ShareOccurrence` lifecycle.
  - [MASTER_02_CONTENT_DEVOTIONALS_AND_MEDIA.md](masters/MASTER_02_CONTENT_DEVOTIONALS_AND_MEDIA.md) — Categories, Devotionals, Khutbah sections, Quran 604 pages, Templates, `DevotionalMedia` & `file_id` uploads.
  - [MASTER_03_PLANS_BILLING_WALLET_AND_ADS.md](masters/MASTER_03_PLANS_BILLING_WALLET_AND_ADS.md) — `FREE`/`BASIC`/`PRO` plans, Wallet (`balance_toman` vs `credit_toman`), PayPing v3, Coupons, SMS plans, Broadcast pricing, `servant_ad`.
  - [MASTER_04_BOTS_USERS_MODERATION_AND_OPS.md](masters/MASTER_04_BOTS_USERS_MODERATION_AND_OPS.md) — 14-bot fleet, Identity, Phone verification, Account merge, 8 Moderation queues, Admin roles & Operations.
  - [MASTER_05_OPEN_KHATM_AND_KHUTBAH_FLOW.md](masters/MASTER_05_OPEN_KHATM_AND_KHUTBAH_FLOW.md) — Open Khatm engine, Khutbah 5-section sequential rollover, video captions & ephemeral store.
  - [MASTER_06_PAYMENT_GATEWAY_AND_CALLBACK_ARCHITECTURE.md](masters/MASTER_06_PAYMENT_GATEWAY_AND_CALLBACK_ARCHITECTURE.md) — PayPing v3 callback, ERR_TIMED_OUT resolution, Apache proxy, In-bot verification.
  - [MASTER_07_MEMBER_DAILY_DIGEST_AND_MOTIVATIONAL_PROGRESS.md](masters/MASTER_07_MEMBER_DAILY_DIGEST_AND_MOTIVATIONAL_PROGRESS.md) — 14:00 member daily progress digest & post-completion motivational progress.
  - [MASTER_08_CREATOR_PANEL_AND_USER_EXPERIENCE.md](masters/MASTER_08_CREATOR_PANEL_AND_USER_EXPERIENCE.md) — Creator panel & web mini-app ground-up redesign, invite link generation, khatm detail tabs, progress bars, zero-error UX.
  - [MASTER_09_BALE_ADAPTER_AND_MARKDOWN_COMPATIBILITY.md](masters/MASTER_09_BALE_ADAPTER_AND_MARKDOWN_COMPATIBILITY.md) — Bale native Markdown engine, `BaleAiohttpSession` interceptor & clean tag rendering.
  - [MASTER_10_PLANS_BROADCAST_RECEIPT_PAYMENT_AND_CREATOR_PANEL_GUARD.md](masters/MASTER_10_PLANS_BROADCAST_RECEIPT_PAYMENT_AND_CREATOR_PANEL_GUARD.md) — Broadcast 1000-recipient tier pricing, removal of free broadcasts, bank receipt upload & approval, PayPing direct link, and admin-only creator panel guard.
- **Bug & Gap Report Master:** [MASTER_BUG_AND_GAP_REPORT.md](MASTER_BUG_AND_GAP_REPORT.md) (16 runtime bugs/dead buttons + 11 Admin Panel gaps).

## 2026-10-06 — V3 Wizard & Flow Overhaul Master
- Master Document: [V3_WIZARD_REDESIGN_MASTER.md](V3_WIZARD_REDESIGN_MASTER.md)
- Sub-specs: [v3_specs/](v3_specs/) (Creator onboarding, commitment vs free, Khutbah cyclic allocation, La'an moderation, Member UI & daily reporting)

## 2026-10-05 — Unified shares (in progress)
- Owner's Quran numeric/regular confirmation: DEC-PY-0117 in DECISIONS.md.
- Runtime: modules/share_occurrence/delivery.py; delivery receipts and member routing: bot/occurrence_adapter.py.
- Numeric expiry/audio migration: migrations/versions/share2026100501_reservation_and_audio.py.
- PostgreSQL acceptance scenarios: tests/test_redesign_delivery_integration.py. Release status: latest PROJECT_STATE.md and REMINDER_REDESIGN_MASTER.md, not older completion claims.

## 2026-10-04 — Local fixes execution
- [FIX_EXECUTION_MASTER.md](FIX_EXECUTION_MASTER.md): current authorization for local repairs, F0–F7 and test/deployment gates.

## 2026-10-04 — Full-system audit
- Entry point: [FULL_SYSTEM_AUDIT_MASTER.md](FULL_SYSTEM_AUDIT_MASTER.md).
- Exact paths, function names and lines: [audit/ITEMS.csv](audit/ITEMS.csv); module map: [audit/MODULES.md](audit/MODULES.md).
- Results and handoff: [audit/README.md](audit/README.md), RUNS.csv, WORK_PACKAGES.csv and BUGS.md.
- Refresh inventory with `scripts/build_audit_inventory.py`; graph/AST provenance is in audit/SNAPSHOT.json.

## 2026-10-03 — Repeated La'an reminder hotfix
- Missing Persian return values: `src/khatmsaz/bot/member_copy.py`.
- Persistent member keyboard: `src/khatmsaz/bot/keyboards.py::member_menu_keyboard`.
- Repeated-scan regression: `tests/test_member_ux_regressions.py::test_regular_reminder_sends_content_before_action_message`.
- Validation and deployment limits: latest Codex entry in `PROJECT_STATE.md` and `REDESIGN_V2_MASTER.md`.

## 2026-10-03 — بازطراحی یادآوری، رزرو عددی و تعهد روزانه
- **مرجع ادامهٔ کار:** `docs/ai/REMINDER_REDESIGN_MASTER.md` — خواسته‌های R01–R21، شواهد F01–F15، پرسش‌ها، مراحل، migration و VPS؛ اجرا منتظر تأیید مالک.
- DEC-PY-0113 — دروازهٔ تأیید پیش از اجرای بازطراحی؛ DONEهای مستر قبلی اثبات این درخواست نیستند.

# INDEX — نقشهٔ موضوعی مستندات (آدرس‌دهی دقیق)

این فایل برای اینه که یک AI یا مالک پروژه بتونه مستقیم بره سراغ سندی که
دربارهٔ یک موضوع خاصه، بدون این‌که مجبور باشه کل `DECISIONS.md` یا
`PROJECT_STATE.md` (حتی بعد از تفکیک تاریخی‌شون) رو بخونه. **هیچ محتوایی
اینجا کپی یا خلاصه نشده** — فقط آدرس دقیق (فایل + شماره خط) هر موضوع.

اگه دنبال یک موضوع می‌گردی و اینجا نیست، به فایل اصلی مربوطه
(`DECISIONS.md` یا آرشیوش) مراجعه کن و بعد اینجا اضافه‌ش کن.

---

## هویت و ثبت‌نام کاربر
- DEC-PY-0103 — وضعیت گفت‌وگو در Redis و تأیید مدیر پس از انقضای OTP: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)
- DEC-PY-0000 — بازنویسی از صفر با پایتون: `docs/ai/archive/DECISIONS_until_DEC-PY-0064.md:515`
- DEC-PY-0003 — هویت: User داخلی + پلتفرم‌ها: `archive/DECISIONS_until_DEC-PY-0064.md:561`
- DEC-PY-0015 — ثبت‌نام؛ شهر متن آزاده: `archive/DECISIONS_until_DEC-PY-0064.md:840`
- DEC-PY-0022 — تشخیص سازنده صریح و قابل‌ممیزی: `archive/DECISIONS_until_DEC-PY-0064.md:456`
- DEC-PY-0061 — اتصال حساب فقط برای اکانت دست‌نخورده: `archive/DECISIONS_until_DEC-PY-0064.md:48`
- DEC-PY-0066 — تغییر شماره claim رو عوض می‌کنه نه User رو: `DECISIONS.md:109`
- DEC-PY-0070 — تأیید شماره خارجی، تصمیم دائمی ادمین: `DECISIONS.md:50`
- DEC-PY-0071 — تأیید وب و بات یک سرویس مشترکن: `DECISIONS.md:36`

## ساخت ختم / ویزارد
- DEC-PY-0103 — ادامهٔ خودکار ساخت ختم پس از تأیید دستی شماره: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)
- DEC-PY-0004 — MVP: template نوع ختم رو قفل می‌کرد (منسوخ، نگاه به ۰۰۰۷): `archive/...:575`
- DEC-PY-0007 — تعهدی/آزاد مستقل از نوع محتواست: `archive/...:595`
- DEC-PY-0018 — ختم قرآن جدید فقط نسخهٔ ۶۰۴ صفحه‌ای: `archive/...:503`
- DEC-PY-0020 — کپی فقط تنظیمات ساخت رو کپی می‌کرد (**این قابلیت کلاً حذف
  شد، ۲۰۲۶-۰۹-۱۸ — نگاه `CHANGELOG.md` آرشیو**): `archive/...:481`
- DEC-PY-0043 — انتخاب فرمت محتوا قبل از فعال‌سازی: `archive/...:272`
- DEC-PY-0072 — صلوات/دعا/زیارت/لعن خانواده‌های مستقل: `DECISIONS.md:25`
- ترتیب جدید ویزارد (اول خانواده، بعد تعهدی/آزاد) — **هنوز ساخته نشده**،
  نگاه `docs/ai/BACKLOG.md` بخش ۲.

## دسته‌بندی محتوا (صلوات/لعن/دعا) — ماژول khatm_category

- DEC-PY-0102 — محتوای عکس/PDF/متن دقیقاً پیش از یادآوری زمان‌بندی‌شده: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)
- DEC-PY-0101 — تصویر کوتاه دسته/صلوات با نام فایل از پوشهٔ ثابت سرور: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)
- DEC-PY-0096 — صلوات متن ثابت دارد و هیچ زیرگروهی ندارد؛ تصویر اختیاری از پنل: `DECISIONS.md` (ورودی ۲۰۲۶-۰۹-۲۹)
- کد: `src/khatmsaz/modules/khatm_category/`
- مایگریشن اولیه: `migrations/versions/a7f8b9c0d1e2_add_khatm_categories.py`
- مایگریشن جدا کردن خانواده‌ها: `ab8c9d0e1f2a`
- پنل ادمین: `/categories` در `src/khatmsaz/web/app.py`
- پوشهٔ تصاویر کوتاه سرور: `src/khatmsaz/web/static/devotional-images/`
- DEC-PY-0072 (بالا) — تصمیم استقلال خانواده‌ها.

## قرآن (کانال، صفحه‌بندی، assetها)
- DEC-PY-0092 — تخصیص چرخشی و دنبالهٔ شخصی هر خواننده: `DECISIONS.md:8`
- کد چرخش: `src/khatmsaz/modules/allocation/service.py` و migration
  `migrations/versions/rot2026092805_rotating_quran_allocation.py`
- DEC-PY-0040 — asset فقط برای صفحهٔ کانونیک: `archive/...:224`
- DEC-PY-0041 — تحویل محتوا asset-first: `archive/...:233`
- DEC-PY-0042 — فرمت محتوا انتخاب سازنده‌ست: `archive/...:241`
- DEC-PY-0044 — رفرنس فایل مختص پلتفرمه: `archive/...:249`
- نگاشت تأییدشدهٔ کانال واقعی: `src/khatmsaz/modules/content/quran_channel_seed.py`
  (شامل استثنای صفحهٔ ۱+۲ در یک عکس)
- دستور بارگذاری: `/admin_quran_source_seed`، وضعیت: `/admin_quran_source_status`

## تعهدی/آزاد، ظرفیت، لیست انتظار
- DEC-PY-0111 — پاسخ عضویت خصوصی و پیام گروهی از همان بات ممبر: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)
- DEC-PY-0102 — فرم ممبر تک‌پیامی، سؤال متمایز و منوی فشرده: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)
- DEC-PY-0010 — ظرفیت+لیست انتظار (اولش فقط قرآن): `archive/...:701`
- **۲۰۲۶-۰۹-۲۰: DEC-PY-0010 برای SALAWAT+COMMITMENT هم گسترش پیدا کرد**
  (تصمیم مالک پروژه: دقیقاً مثل قرآن) — نگاه
  `docs/ai/PROJECT_STATE.md` (ورودی «SALAWAT+COMMITMENT waiting list»)
  و کد در `src/khatmsaz/modules/khatm_workflow/service.py`.
- DEC-PY-0011 — ختم هیبریدی ساخته نمی‌شه: `archive/...:736`
- DEC-PY-0019 — رضایت صریح قبل از عضویت تعهدی: `archive/...:493`

## پرداخت، کیف پول، پلن
- DEC-PY-0012 — کیف پول/پلن الان ساخته شد، قیمت پیش‌فرض صفر: `archive/...:756`
- DEC-PY-0021 — کال‌بک پرداخت مستقل از درگاه: `archive/...:469`
- DEC-PY-0030 — بازپرداخت ختم پولی بی‌عضو به کیف پول: `archive/...:415`
- DEC-PY-0032 — Entitlement بر اساس کلید ویژگی: `archive/...:354`
- DEC-PY-0033 — پلن فعال هزینهٔ ساخت رو تعیین می‌کنه: `archive/...:343`
- DEC-PY-0056 — PayPing v3 اولین PSP زنده: `archive/...:122`
- DEC-PY-0057 — هر خرید یک فاکتور داخلی می‌سازه: `archive/...:108`
- DEC-PY-0058 — کد تخفیف اختیاری، مصرف مقید به فاکتور: `archive/...:94`
- DEC-PY-0074 — قوانین دقیق سقف پلن رایگان (۱۰۰ نفر مجموع، قرآن جدا و
  قابل‌تنظیم، رد شدن از سقف = فقط قفل ساخت ختم جدید): `DECISIONS.md`
  (ورودی جدید، بالای فایل)
- DEC-PY-0097 — خرید دائمی PRO از کیف پول با قیمت قابل‌تنظیم دیتابیس:
  `DECISIONS.md` (ورودی ۲۰۲۶-۰۹-۲۹)
- پلن‌های سقف‌عضو/ادیت‌پذیر ادمین — **هنوز پیاده‌سازی نشده**، نگاه
  `docs/ai/BACKLOG.md` بخش ۴.
- پلن پیامکی زمان‌دار — **ساخته شد ۲۰۲۶-۰۹-۲۰**، کد در
  `src/khatmsaz/modules/sms_subscription/`، `BACKLOG.md` بخش ۵.

## پیامک (Kavenegar)
- DEC-PY-0034 — SMS یک provider boundary صریحه: `archive/...:332`
- DEC-PY-0068 — Kavenegar اولین آداپتور تولیدیه: `DECISIONS.md:80`
- کد: `src/khatmsaz/modules/sms/provider.py`

## یادآوری‌ها، گزارش، زبان

- DEC-PY-0105 — تأیید آگاهانهٔ تعهدی/آزاد، کارت ثابت + سؤال جدا، لینک مستقیم بات: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)

- DEC-PY-0104 — ساعت یادآوری اجباری و جدا برای هر ختم + ورودی عمومی فعلاً فقط فارسی: `DECISIONS.md` (ورودی ۲۰۲۶-۱۰-۰۱)
- DEC-PY-0023 — Timezone به ازای هر عضو: `archive/...:445`
- DEC-PY-0025 — زبان لحظهٔ ارسال اعلان: `archive/...:365`
- DEC-PY-0027 — Snooze بدون خاموش‌کردن پیام‌های امنیتی: `archive/...:385`
- DEC-PY-0028 — گزارش شخصیِ مثبت در بات: `archive/...:395`
- DEC-PY-0029 — ترکیب یادآوری‌های روزانه: `archive/...:405`
- DEC-PY-0031 — Daily Digest قابل تنظیم کاربره: `archive/...:425`
- DEC-PY-0037 — قاری بر اساس policy: `archive/...:300`
- DEC-PY-0038 — سایز فونت per-user: `archive/...:290`
- DEC-PY-0039 — لایه‌های محتوای اختیاری per-user: `archive/...:280`
- پیام تشکر + لینک دعوت بعد از هر سهم — **ساخته شد ۲۰۲۶-۰۹-۲۰**، کد در
  `src/khatmsaz/bot/handlers/portions.py` (تابع `_invite_friends_line`).
- مقایسهٔ امروز/دیروز — **ساخته شد ۲۰۲۶-۰۹-۲۰** (فقط برای مشارکت آزاد
  شمارشی)، کد در `src/khatmsaz/modules/open_contribution/service.py`
  (`today_vs_yesterday`)، `BACKLOG.md` بخش ۸.
- چندزبانه‌شدن کامل UI — **زیرساخت شروع شد ۲۰۲۶-۰۹-۲۰، چندجلسه‌ایه** —
  وضعیت دقیق و چک‌لیست: `docs/ai/I18N_MIGRATION.md`. کد زیرساخت:
  `src/khatmsaz/i18n/__init__.py`.

## تبلیغات و اعتبار پاداش
- DEC-PY-0035 — پاداش تبلیغاتی opt-in و idempotent: `archive/...:320`

## عضویت، دعوت، حریم خصوصی
- DEC-PY-0036 — کشف عمومی از همون مسیر دعوت رد می‌شه: `archive/...:310`
- DEC-PY-0051 — باز کردن دعوت جدا از عضویته: `archive/...:187`
- DEC-PY-0052 — همهٔ حالت‌های دیدپذیری قابل انتخاب سازنده‌ست: `archive/...:195`
- DEC-PY-0060 — پیش‌نمایش دعوت عمومی، عضویت فقط داخل بات: `archive/...:66`

## خروج و مدیریت مشارکت
- DEC-PY-0009 — سهم‌های ازدست‌رفته به استخر اضطراری: `archive/...:670`
- DEC-PY-0016 — خروج از تعهدی نیاز به تأیید سازنده: `archive/...:902`
- DEC-PY-0053 — Skip-today کنترل سازنده: `archive/...:205`
- DEC-PY-0063 — پیام پایان منتظر پنجرهٔ Undo می‌مونه: `archive/...:21`

## مدیریت/ادمین/پنل
- DEC-PY-0013 — bootstrap ادمین با allowlist، ماجراجویی با دستور تایپی
  (منسوخ‌شونده — الان بخشی از پنل هست): `archive/...:781`
- DEC-PY-0014 — صف درخواست نوع ختم؛ اتصال به ویزارد عمداً ساخته نشد
  (بعداً با ماژول `khatm_category` این محدودیت برطرف شد): `archive/...:814`
- DEC-PY-0050 — ماجراجویی درخواست، پلتفرم فراخوان رو resolve می‌کنه: `archive/...:178`
- DEC-PY-0054 — پیام‌های سازنده نیاز به تأیید مدیریت قبل از ارسال: `archive/...:214`
- DEC-PY-0059 — مدیران تفویضی با role grant قابل‌لغو: `archive/...:80`
- DEC-PY-0062 — رویدادهای حساس audit فقط تو وب و operations: `archive/...:36`
- DEC-PY-0064 — نشست‌های وب سازنده هدف‌محور: `archive/...:7`
- DEC-PY-0067 — واجدشرایطی سازنده قبل از هر شارژ دوباره چک می‌شه: `DECISIONS.md:94`
- DEC-PY-0069 — دستورهای تلگرام آینهٔ منوی راهنمای کم‌عمق: `DECISIONS.md:68`
- DEC-PY-0073 — داشبورد = Mini App پیام‌رسان، نه سایت مستقل: `DECISIONS.md:8`
- گزارش اکسل کامل اعضا برای سازنده — کد در `src/khatmsaz/web/app.py`
  (تابع `creator_khatm_export`).
- پیام گروهی از پنل ادمین — `src/khatmsaz/web/app.py` (`/broadcasts`).
- پیام گروهی سازنده، سهمیه و فیلتر ختم/استان/جنسیت — `src/khatmsaz/modules/broadcast/service.py` + `src/khatmsaz/web/templates/creator_broadcasts.html`.
- تیکت مخاطب↔سازنده و سازنده↔ادمین اصلی — `src/khatmsaz/bot/handlers/suggestions.py`.
- «انجام قرائت امروز» و انتخاب ختم — `src/khatmsaz/i18n/__init__.py` (`menu.today`) + `src/khatmsaz/bot/handlers/report.py`.
- ساخت ختم اختصاصی از بات ممبر — `src/khatmsaz/bot/handlers/member_start.py::custom_khatm_contact` + `/operations` setting `custom_khatm_admin_phone`.

## معماری چند-باتی (۲۶ بات)
- DEC-PY-0080 — تقسیم به ۱ بات سازنده + ۱۲ بات ممبر در هر پلتفرم: `DECISIONS.md` (بالای فایل)
- مستندات کامل: `docs/ai/multibot/OVERVIEW.md` (نقطه شروع)
- جدول bot_instances و رمزنگاری توکن: `docs/ai/multibot/BOT_REGISTRY.md`
- بات سازنده (وظایف، هندلرها، منوها): `docs/ai/multibot/CREATOR_BOT.md`
- بات‌های ممبر (عضویت، زبان ثابت): `docs/ai/multibot/MEMBER_BOTS.md`
- لینک‌های دعوت چند-باتی: `docs/ai/multibot/INVITE_LINKS.md`
- مسیریابی هندلرها (دو Dispatcher): `docs/ai/multibot/HANDLER_ROUTING.md`
- دو مسیر ثبت‌نام (سازنده OTP / ممبر contact-share): `docs/ai/multibot/REGISTRATION.md`
- پنل ادمین مدیریت توکن‌ها: `docs/ai/multibot/ADMIN_TOKEN_PANEL.md`
- مسیریابی نوتیفیکیشن‌ها: `docs/ai/multibot/NOTIFICATION_ROUTING.md`
- کد ماژول: `src/khatmsaz/modules/bot_registry/`
- کلاس BotRegistry: `src/khatmsaz/core/bot_registry.py`
- هندلرهای ممبر: `src/khatmsaz/bot/handlers/member_*.py`

## معماری کلی و زیرساخت
- DEC-PY-0001 — Long polling نه webhook: `archive/...:531`
- DEC-PY-0002 — جداسازی ماژول‌ها: `archive/...:550`
- DEC-PY-0005 — FSM در حافظه، نه Redis: `archive/...:885`
- DEC-PY-0008 — موتور یادآوری/میس اولین برش: `archive/...:626`
- DEC-PY-0024 — تست PostgreSQL واقعی اختیاریه: `archive/...:435`
- DEC-PY-0055 — ویرایش بعد از فعال‌سازی فقط ظاهریه: `archive/...:139`
- راه‌انداز محلی Windows: `start_bot.ps1` / `start_bot.bat`
- `/health` واقعی (چک دیتابیس): کد در `src/khatmsaz/web/app.py`

## هماهنگی بین چند هوش مصنوعی و مستندسازی
- `docs/ai/AI_HANDOFF_PROTOCOL.md` — قانون مشترک Codex/Claude Code/Antigravity.
- `docs/ai/SHARED_EXECUTION_PLAN.md` — برنامهٔ اجرایی زنده و چک‌لیست مشترک سه عامل.
- `docs/ai/BACKLOG.md` — کارهای درخواستی هنوز نساخته.
- همین فایل (`INDEX.md`) — نقشهٔ موضوعی.
## ویرایش ختم فعال و UX ساخت (B1–B10)
- تصمیم افزایش امن هدف و قفل ساختار قرآن: `docs/ai/DECISIONS.md` → DEC-PY-0099
- ویزارد ساخت و بازگشت/خلاصهٔ تک‌پیام: `src/khatmsaz/bot/handlers/create_khatm.py`
- تنظیمات بات سازنده: `src/khatmsaz/bot/handlers/my_khatms.py`
- تنظیمات پنل سازنده: `src/khatmsaz/web/app.py::creator_khatm_settings`
