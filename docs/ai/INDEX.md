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
