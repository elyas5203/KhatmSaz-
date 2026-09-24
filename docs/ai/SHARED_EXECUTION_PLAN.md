# برنامه اجرایی مشترک Codex / Claude Code / Antigravity

> این فایل «منبع حقیقت اجرایی» برای سه عامل است. هر عامل پیش از تغییر کد،
> `AGENTS.md`، `docs/ai/PROJECT_STATE.md` و `docs/ai/AI_HANDOFF_PROTOCOL.md`
> را می‌خواند و سپس وضعیت همین فایل را بررسی می‌کند. هیچ عامل حق ندارد موردی
> را بدون تست به «انجام‌شده» تغییر دهد.

## هدف جاری

رفع مشکلات قطعی مشاهده‌شده در تست واقعی Telegram Web و هم‌راستا کردن کد،
تست‌ها، مستندات و نسخهٔ VPS، بدون حدس‌زدن قوانین محصول و بدون deploy/push
بدون تأیید مالک.

## شواهد مبنا

- تست زنده: `/profile` → `/start` → `/public_khatms` → `/cancel` کاربر را
  در مرحلهٔ شماره موبایل نگه می‌دارد.
- `src/khatmsaz/bot/handlers/start.py::handle_start` وضعیت FSM را پاک نمی‌کند.
- handler سراسری `/cancel` وجود ندارد و ورودی‌های فرم slash commandها را داده
  تلقی می‌کنند.
- کلاینت‌ها `ParseMode.HTML` دارند، ولی بعضی متن‌های i18n از Markdown استفاده
  می‌کنند و علامت‌های `**` و backtick خام دیده می‌شوند.
- callbackهای گزارش‌شده در مخزن handler دارند؛ خرابی هم‌زمان آن‌ها در VPS
  بدون بررسی SHA، log و تعداد pollerها نباید به یک handler خاص نسبت داده شود.
- منوی نسخهٔ زنده با `main@9d84138` یکسان نیست؛ deploy drift محتمل است.

## APIها و الگوهای مجاز

- پاک‌سازی FSM: `await state.clear()`؛ نمونه:
  `src/khatmsaz/bot/handlers/create_khatm.py::cancel_wizard`.
- پاسخ امن callback: `safe_answer_callback` در
  `src/khatmsaz/bot/keyboards.py`.
- حذف امن keyboard اینلاین: `safe_clear_inline_keyboard` در همان فایل.
- محافظ فعلی ورودی‌های متنی: `bail_if_menu_button`؛ باید بدون شکستن
  call-siteهای موجود، command-aware شود.
- منوی صحیح باید براساس `UserRole.CREATOR`/`SUPER_ADMIN` انتخاب شود؛ هر مسیر
  بازگشت نباید سازنده را ظاهراً به منوی participant تنزل دهد.

## فاز 0 — تثبیت ناوبری و خروج از FSM (P0)

### اجرا

- [x] `/start` ساده در هر state ابتدا state قبلی را پاک کند.
- [x] `/start join_*` state قبلی را پاک و سپس فقط context لینک جدید را بسازد.
- [x] `/cancel` سراسری و چندزبانه اضافه شود؛ برای participant و creator به منوی صحیح برمی‌گردد.
- [x] هیچ slash commandای به‌عنوان نام، شماره، شهر، عنوان یا عدد ذخیره نشود.
- [x] مسیرهای بازگشت profile برای participant و creator منوی role-aware نشان دهند.
- [x] شاخهٔ لغو `join_preview` همیشه callback را acknowledge کند.

### مانع صریح منوی مدیریت

- **BLOCKED/TBD:** نقش `SUPER_ADMIN` تجربه‌ای مستقل از participant و creator
  دارد، اما مخزن هنوز هیچ ترکیب مصوبی برای Home Reply Keyboard مدیر ندارد.
  مسیر موجود و مجاز مدیریت `/admin_app` / `/admin_web_login` و callback
  `admin:web_login` است. تا زمانی که مالک اجزای منوی مدیر را تعیین نکرده،
  recovery فقط کیبورد موقت فرم را حذف و همین مسیر موجود را معرفی می‌کند؛
  مدیر نه به منوی participant و نه creator نگاشت نمی‌شود.

### شواهد اعتبارسنجی فاز 0

- `tests/test_navigation_dispatcher.py`: مسیر واقعی Dispatcher در state فعال
  پروفایل برای `/start`، `/cancel`، `/public_khatms` و `/profile`.
- `tests/test_navigation_recovery.py`: پاک‌سازی state، deep-link تازه، زبان
  payload ناشناخته، نقش‌ها و acknowledgement لغو join preview.
- `tests/test_home_menu.py`: ترکیب دقیق منوی participant طبق DEC-PY-0076 و
  پوشش تمام برچسب‌های Reply Keyboard در `RESERVED_MENU_TEXTS`.
- نتیجهٔ متمرکز نهایی: `24 passed`؛ اجرای گستردهٔ non-integration نیز
  `79 passed` داشت و فقط یک تستِ بدون marker به‌علت در دسترس نبودن Postgres
  روی `localhost:55433` شکست خورد.

### تست پذیرش

- `/profile` → `/start` → `/public_khatms` باید فهرست عمومی را اجرا کند.
- `/profile` → `/cancel` باید فرم را تمام و منوی صحیح را نمایش دهد.
- تست برای participant، creator و super-admin.
- تست deep-link در حالی‌که یک state قدیمی فعال است.

### ضدالگوها

- جابه‌جایی تصادفی routerها بدون تست dispatcher-level ممنوع.
- اضافه‌کردن `/cancel` جداگانه به تک‌تک فرم‌ها ممنوع؛ رفتار باید مرکزی باشد.
- پاک‌کردن context جدید deep-link بعد از ذخیرهٔ آن ممنوع.

## فاز 1 — callback و بازخورد فوری (P0/P1)

### اجرا

- [ ] ماتریس تمام `callback_data`های تولیدشده و handler متناظر ساخته شود.
- [ ] هر شاخهٔ callback دقیقاً یک acknowledgement قابل اتکا داشته باشد.
- [ ] پردازش‌های DB/media طولانی بازخورد فوری بدهند و exception قبل از پاسخ
  برای کاربر پیام ساده و برای log جزئیات فنی ثبت کند.
- [ ] تست dispatcher-level برای callbackهای Help، Wallet، My Khatms، Portions،
  Settings و Create Khatm اضافه شود.

### تشخیص VPS — فقط read-only تا زمان اجازه deploy

- [ ] `git rev-parse HEAD` نسخهٔ deployشده با `origin/main` مقایسه شود.
- [ ] تعداد processهای `python -m khatmsaz.bootstrap` بررسی شود؛ فقط یک poller
  باید updateها را دریافت کند.
- [ ] هنگام یک کلیک آزمایشی، service log برای exception بررسی شود.
- [ ] وضعیت migration و restart ثبت شود.

## فاز 2 — متن و UX فوق‌ساده (P1)

- [ ] تمام متن‌های user-facing با قرارداد HTML بررسی شوند؛ Markdown خام حذف شود.
- [ ] عبارت روشن «لازم نیست دستورها را حفظ کنید» به صفحهٔ راهنما برگردد.
- [ ] profile ابتدا اطلاعات فعلی را نشان دهد و «ویرایش / انصراف» داشته باشد.
- [ ] همهٔ فرم‌ها «مرحله N از M»، «قبلی» و «لغو» داشته باشند، جایی که قانون
  محصول اجازه می‌دهد.
- [ ] validation عنوان، نام، شماره، ساعت، ظرفیت و متن اختیاری با پیام خطای
  ساده و مثال درست پوشش داده شود.
- [ ] متن‌ها با `TONE_GUIDE_80YO_PERSONA.md` و قرارداد فارسی ساده بازبینی شوند.

## فاز 3 — یکسان‌سازی مستندات سه عامل (P1)

- [ ] `PROJECT_STATE.md` و `CHANGELOG.md` با ورودی جدید و امضای عامل به‌روز شوند.
- [ ] تصمیم سراسری recovery/cancel با شناسهٔ جدید در `DECISIONS.md` ثبت شود.
- [ ] ادعاهای منسوخ auto-start و emergency/skip در اسناد با ارجاع به تصمیم
  جایگزین علامت‌گذاری شوند؛ تاریخچه حذف نشود.
- [ ] وضعیت واقعی migration نقش CREATOR و نبود backfill شفاف شود.
- [ ] فایل‌های حجیم طبق پروتکل archive شوند و `INDEX.md` دوباره معتبر شود.
- [ ] mojibake با حفظ UTF-8 و بدون بازنویسی کور تاریخچه اصلاح شود.

## فاز 4 — اعتبارسنجی و تحویل

- [ ] تست‌های متمرکز با `PYTHONPATH=src` پاس شوند.
- [ ] کل `pytest` پاس شود یا وابستگی محیطی دقیق گزارش شود.
- [ ] migrationها فقط خوانده و روی Postgres موقت/مجاز اجرا شوند؛ production نه.
- [ ] grep ضدالگو: Markdown خام، handler بدون callback answer، commandهای قابل
  بلعیده‌شدن و `main_menu_keyboard` بدون role در مسیرهای حساس.
- [ ] بازبینی کیفیت مستقل انجام شود.
- [ ] deploy/push فقط پس از تأیید صریح مالک.

## قرارداد گزارش هر عامل

هر گزارش باید شامل این موارد باشد:

1. فایل‌ها و بخش‌های خوانده‌شده؛
2. فایل‌های تغییرکرده و دلیل؛
3. فرمان‌های اجراشده و خروجی PASS/FAIL؛
4. موارد انجام‌نشده و مانع؛
5. SHA/محیطی که نتیجه روی آن تأیید شده است.

## فاز 5 — انزوای مخاطب و توانمندسازی سازنده (جدید)

طبق درخواست صریح مالک (2026-09-24):
- تغییر مسیر پشتیبانی: اعضای عادی پیامشان به سازنده‌هایشان می‌رسد (با امکان انتخاب سازنده اگر در چند ختم هستند).
- سازنده می‌تواند در ربات با یک دکمه «پاسخ به این کاربر» به کاربر جواب دهد (بدون افشای آیدی).
- تعریف پلتفرم مجاز (تلگرام، بله، هر دو) هنگام ساخت ختم.
- ارسال پیام گروهی سازنده به اعضا با فایل پلتفرم‌محور: هزینه پیام (۳ پیام اول رایگان، بعد از آن تا ۱۰۰۰ نفر ۴۳ هزارتومان یکجا مقطوع، بالای ۱۰۰۰ نفر هر پیام ۹۳ تومان).

### اجرا:
- [ ] بازنویسی `suggestions.py` (پشتیبانی هوشمند و امکان پاسخ).
- [ ] افزودن فیلد `allowed_platforms` به `khatms` و فرآیند ساخت ختم.
- [ ] ساخت دیتابیس و ماژول `creator_broadcasts` (مدیریت هزینه‌ها و ارسال).
