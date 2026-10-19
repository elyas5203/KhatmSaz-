# MASTER-48: مرکز پایش زندهٔ ناوگان ربات‌ها، تست اتصال برخط و عیب‌یابی لاگ‌های سیستمی در پنل وب (Bot Fleet Diagnostics & Real-Time System Health Hub)

**تاریخ تدوین:** ۲۸ مهر ۱۴۰۵ / 2026-10-19  
**وضعیت:** مصوب با تأیید مستقیم کارفرما و آماده پیاده‌سازی (Approved by Owner & Ready for Implementation)  
**دامنه:** پنل وب مدیریت (`web/app.py`، `web/templates/operations.html`)، ماژول رجیستری ربات‌ها (`modules/bot_registry`)، موتور زمان‌بندی و یادآوری (`reminder_engine`)، سیستم ثبت وقایع (`core/logging_system`)  
**وابستگی‌ها:** MASTER-04 (مدیریت بات‌ها و عملیات)، MASTER-12 (ربات اختصاصی ادمین و لاگینگ)، MASTER-37 (بازطراحی پنل وب)، DEC-PY-0140  

---

## ۱. چرایی و تصمیمات قطعی کارفرما (Context & Owner Decisions)

بر اساس استعلام مستقیم و مصوبات اخذشده از کارفرما در تاریخ ۲۸ مهر ۱۴۰۵:

1. **ارتقای یکپارچهٔ مرکز عملیات و عیب‌یابی (`/operations`):**
   - مرکز عملیات وب ادمین به عنوان «مرکز فرماندهی، پایش زنده و سلامت زیرساخت» ارتقا می‌یابد و تمام اطلاعات سلامت پایگاه داده، زمان‌بند، ناوگان ۱۸ ربات (تلگرام و بله)، صفوف سیستم و لاگ‌های خطای زنده در یک داشبورد جامع گردآوری می‌شوند.
2. **پایش برخط ناوگان ۱۸ ربات (Bot Fleet Ping & Latency Matrix):**
   - برای تمامی اسلات‌های ربات‌های سازنده، ادمین و بات‌های عضو ۵ خانواده (قرآن، صلوات، ادعیه و زیارات، لعن، خطبه‌ها) در تلگرام و بله، قابلیت تست اتصال زنده فراهم می‌شود.
   - با فراخوانی متد `getMe` روی API تلگرام و بله، زمان پاسخ‌دهی (Latency بر حسب میلی‌ثانیه)، نام کاربری دریافت شده و وضعیت برخط بودن ارزیابی می‌گردد.
   - دکمهٔ «⚡️ تست دسته‌جمعی ناوگان» امکان پایش همزمان کلیه ربات‌های دارای توکن فعال را فراهم می‌سازد.
3. **پایشگر زندهٔ زمان‌بند و اجرای دستی اسکن (Scheduler Diagnostics & Manual Trigger):**
   - وضعیت لحظه‌ای زمان‌بند (`APScheduler`) و اسنپ‌شات وضعیت اجرایی (`runtime_status`) شامل زمان راه‌اندازی، آخرین اسکن موفق و آخرین خطا نمایش داده می‌شود.
   - دکمهٔ عملیاتی «⚡️ اجرای دستی اسکن یادآوری‌ها» (`POST /operations/trigger-scan`) به مدیران ارشد اجازه می‌دهد بدون نیاز به ری‌استارت سرویس یا صبر کردن برای کرون‌جاب، فرآیند اسکن و تحویل سهم‌ها را فوراً تحریک و نتیجه را مشاهده نمایند.
4. **کنسول زندهٔ لاگ‌های خطا (Live Error Log Viewer):**
   - نمایش زندهٔ ۱۰۰ تا ۲۰۰ خط آخر فایل لاگ خطاهای سیستم (`logs/errors.log` یا `logs/khatmsaz.log`) در یک ترمینال تیره و خوانا با رنگ‌بندی تفکیک‌شده (سطوح ERROR، CRITICAL، WARNING).
   - موتور جستجو و فیلتر کلاینت‌ساید برای فیلتر آنی خطوط بر اساس کلمات کلیدی (مانند `timeout`, `aiogram`, `db`, `Traceback`).
   - دکمهٔ تازه‌سازی لاگ بدون رفرش کل صفحه و لینک مستقیم دانلود فایل لاگ.
5. **حفظ کامل سازگاری تنظیمات سراسری (Zero Breaking Changes):**
   - تمامی روت‌های قبلی شامل تنظیم لوگوی پنل (`/operations/panel-logo`)، شماره ساخت ختم اختصاصی (`/operations/custom-khatm-phone`) و تنظیمات پیش‌فرض یادآوری (`/operations/system-settings`) بدون تغییر حفظ می‌شوند.

---

## ۲. معماری جریان داده و عیب‌یابی (Architecture & Diagnostics Flow)

```mermaid
flowchart TD
    subgraph WebAdmin [پنل مدیریت وب - /operations]
        KPIs[۴ کارت شاخص سلامت: دیتابیس، زمان‌بند، بات‌ها، لاگ‌ها]
        BotFleet[ماتریس ۱۸ ربات تلگرام و بله]
        Scheduler[پایشگر زمان‌بند و اجرای دستی]
        LogConsole[کنسول زنده لاگ‌های خطا]
        Settings[تنظیمات لوگو و شماره تماس]
    end

    subgraph BotFleetDiagnostics [موتور تست اتصال ربات‌ها]
        PingAction[POST /operations/bots/{id}/ping]
        PingAllAction[POST /operations/bots/ping-all]
        TelegramAPI[Telegram Bot API /getMe]
        BaleAPI[Bale Bot API /getMe]
        PingAction --> TelegramAPI
        PingAction --> BaleAPI
    end

    subgraph SchedulerDiagnostics [موتور اسکن و زمان‌بند]
        TriggerAction[POST /operations/trigger-scan]
        ReminderEngine[khatmsaz.modules.reminder_engine.service.run_once]
        AuditService[ثبت در audit_logs]
        TriggerAction --> ReminderEngine
        TriggerAction --> AuditService
    end

    subgraph LoggingSystem [موتور وقایع و لاگ‌ها]
        ErrorLogFile[(logs/errors.log)]
        MainLogFile[(logs/khatmsaz.log)]
        LogFetcher[GET /operations/logs/tail]
        LogConsole --> LogFetcher
        LogFetcher --> ErrorLogFile
        LogFetcher --> MainLogFile
    end

    BotFleet --> PingAction
    BotFleet --> PingAllAction
    Scheduler --> TriggerAction
```

---

## ۳. فهرست روت‌ها و رابط‌های کاربری (Routes & Interfaces)

| روت | متد | شرح عملکرد | مجوز الزامی |
| :--- | :---: | :--- | :--- |
| `/operations` | `GET` | رندر داشبورد جامع عملیات، سلامت سرویس‌ها، ناوگان ربات‌ها، زمان‌بند و لاگ‌ها | `OPERATIONS_VIEW` |
| `/operations/bots/{instance_id}/ping` | `POST` | تست برخط اتصال یک بات مشخص از طریق `getMe` و محاسبه Latency بر حسب ms | `OPERATIONS_VIEW` |
| `/operations/bots/ping-all` | `POST` | تست اتصال دسته‌جمعی کلیه بات‌های دارای توکن و بازگرداندن وضعیت جامع JSON | `OPERATIONS_VIEW` |
| `/operations/trigger-scan` | `POST` | اجرای دستی و فوری یک نوبت اسکن کامل زمان‌بند یادآوری‌ها و ثبت لاگ ممیزی | `OPERATIONS_VIEW` |
| `/operations/logs/tail` | `GET` | دریافت ۱۰۰ الی ۲۰۰ خط پایانی لاگ‌های خطا با فرمت متنی/JSON | `OPERATIONS_VIEW` |
| `/operations/logs/download` | `GET` | دانلود مستقیم فایل لاگ خطای `errors.log` | `OPERATIONS_VIEW` |
| `/operations/system-settings` | `POST` | تنظیم ساعت پیش‌فرض یادآوری و روزهای عدم فعالیت (حفظ سازگاری قبلی) | `OPERATIONS_VIEW` |
| `/operations/panel-logo` | `POST` | ذخیره آدرس تصویر لوگوی پنل (حفظ سازگاری قبلی) | `OPERATIONS_VIEW` |
| `/operations/custom-khatm-phone` | `POST` | ذخیره شماره موبایل پشتیبان ساخت ختم اختصاصی (حفظ سازگاری قبلی) | `OPERATIONS_VIEW` |

---

## ۴. استانداردهای پیاده‌سازی و خطوط قرمز (Non-Negotiable Guardrails)

1. **امنیت توکن‌ها و عدم افشا در لاگ و پاسخ‌های وب:** توکن‌های خام ربات‌ها به هیچ وجه در پاسخ‌های فرانت یا HTML آشکار نمی‌شوند؛ تست اتصال مستقیماً توسط بک‌اند انجام می‌شود و فقط نتیجه (`ok`, `latency_ms`, `username`) ارسال می‌گردد.
2. **عدم مسدود شدن سرور وب (Non-blocking I/O & Timeout Guard):** کلیه تماس‌های `getMe` به تلگرام و بله باید با مهلت زمانی سخت‌گیرانه (حداکثر ۴ ثانیه) اجرا شوند تا در صورت فیلترینگ یا قطعی شبکه، پردازش وب مسدود نشود.
3. **ثبت ممیزی اجرای دستی اسکن (Audit Trail):** هر بار فشردن دکمهٔ «اجرای دستی اسکن»، اقدام با شناسه ادمین در `audit_logs` ثبت می‌شود.
4. **مدیریت خطای نبود فایل لاگ (Graceful Fallback):** در محیط‌های تستی یا پیش از وقوع خطا که فایلی در `logs/` ایجاد نشده است، سیستم پیام محترمانه «هنوز خطایی ثبت نشده است» نمایش می‌دهد و از بروز `FileNotFoundError` جلوگیری می‌کند.
5. **راست‌به‌چپ و فارسی‌نویسی در کنار ترمینال مونو LTR:** رابط کاربری کاملاً راست‌به‌چپ (RTL) طراحی شده و تنها جعبه کد لاگ و متون فنی در جهت چپ‌به‌راست (`dir="ltr" font-mono`) رندر می‌شوند.

---

## ۵. آزمون و اعتبارسنجی (Test & Acceptance Plan)

1. **تست احراز هویت:** جلوگیری از دسترسی کاربران غیرادمین به روت‌های عملیات و ریدایرکت به `/login`.
2. **تست سلامت رندرینگ صفحه `/operations`:** اطمینان از بارگذاری کامل المان‌های ناوبری، کارت‌های وضعیت، ناوگان ربات‌ها و باکس لاگ.
3. **تست پینگ بات‌ها:** آزمون موک موفقیت‌آمیز `ping` و دریافت زمان پاسخ‌دهی و مدیریت خطای اتصال یا توکن نامعتبر.
4. **تست اجرای دستی اسکن یادآوری:** فراخوانی `POST /operations/trigger-scan` و تأیید ثبت عملیات در `audit_logs`.
5. **تست روت‌های لاگ:** تایید دریافت خطوط انتهایی لاگ و دانلود فایل.
6. **پوش به مخزن و استقرار زنده بر روی سرور VPS (`91.107.137.22`):** اجرای اسکریپت دپلو، تایید اجرای موفق سرویس و بررسی لاگ‌های لایو.
