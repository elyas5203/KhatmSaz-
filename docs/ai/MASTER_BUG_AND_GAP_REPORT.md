# 🐛 مستر جامع گزارش باگ‌ها، دکمه‌های مرده، ناهماهنگی‌ها و شکاف‌های مدیریتی
**(Master Bug, Dead Button, Regression & Admin Gap Report)**

> **🔗 موقعیت در درختوارهٔ اسناد (والد و فرزندی):**
> - **⬆️ سند مادر (والد):** [ADMIN_PANEL_REDESIGN_MASTER.md](ADMIN_PANEL_REDESIGN_MASTER.md) (مستر اصلی بازطراحی کامل پنل مدیریت)
> - **⬅️ اسناد فرزند مرتبط:**
>   - **[مستر فرزند ۰۱](masters/MASTER_01_KHATM_ENGINE_AND_MODES.md):** موتور ختم‌ها، تعهدی/آزاد و سهم‌بندی
>   - **[مستر فرزند ۰۲](masters/MASTER_02_CONTENT_DEVOTIONALS_AND_MEDIA.md):** مدیریت محتوا، ادعیه، خطبه، قرآن و فایل‌های چندرسانه‌ای
>   - **[مستر فرزند ۰۳](masters/MASTER_03_PLANS_BILLING_WALLET_AND_ADS.md):** پلن‌های پولی/رایگان، کیف پول، درگاه پرداخت، کد تخفیف و تبلیغات
>   - **[مستر فرزند ۰۴](masters/MASTER_04_BOTS_USERS_MODERATION_AND_OPS.md):** معماری مولتی‌بات، کاربران، احراز شماره، صف‌های تأیید و عملیات سرور

---

## 📌 هدف این سند
این فایل خروجی کالبدشکافی **خط‌به‌خط (Line-by-Line Audit)** کل کدهای پروژه (وب‌پنل ادمین، وب‌پنل سازنده، ۴۰ هندلر بات و ۳۶ ماژول دیتابیس/سرویس) است. تمام باگ‌های زمان اجرا، دکمه‌های مرده، کال‌بک‌های بدون هندلر، ناهماهنگی‌های Enum، کوئری‌های N+1 و قابلیت‌هایی که در کد ناقص رها شده‌اند، با **آدرس دقیق فایل و شماره خط** و **راهکار دقیق اصلاح** در این سند ثبت شده‌اند تا در فاز کدنویسی یکی‌یکی و بدون جا افتادن هیچ موردی برطرف شوند.

---

## بخش اول: باگ‌های بحرانی (CRITICAL — کرش ۵۰۰، خطای زمان اجرا یا نقض امنیت/مالی)

### `BUG-01` — کرش ۵۰۰ در صفحهٔ مدیریت بات‌ها (`GET /bots`) به دلیل نبودن `intro_image_khutbah`
- **شدت:** 🔴 **CRITICAL (کرش صفحه وب و بات)**
- **محل دقیق در کد:**
  - [src/khatmsaz/web/app.py](../../src/khatmsaz/web/app.py#L2758-L2761) (`GET /bots`) و [L2785-L2806](../../src/khatmsaz/web/app.py#L2785-L2806) (`POST /bots/family-intro-images`)
  - [src/khatmsaz/modules/bot_registry/service.py](../../src/khatmsaz/modules/bot_registry/service.py#L106-L109) (`get_intro_image_for_category`)
  - [src/khatmsaz/modules/system_settings/service.py](../../src/khatmsaz/modules/system_settings/service.py#L30-L37) (`KNOWN_STRING_SETTINGS`)
- **رفتار فعلی (مشکل چیست؟):**
  صفحهٔ `/bots` در پنل ادمین برای خواندن تصویر معرفی خانوادهٔ خطبه، تابع `system_settings_service.get_str(session, "intro_image_khutbah")` را صدا می‌زند. اما در `system_settings/service.py:30-37` کلید `"intro_image_khutbah"` داخل مجموعهٔ `KNOWN_STRING_SETTINGS` تعریف نشده است! در نتیجه، باز کردن صفحهٔ `/bots` در پنل وب با خطای `ValueError: unknown string system setting: intro_image_khutbah` (خطای ۵۰۰) کرش می‌کند و ذخیرهٔ تصاویر معرفی هم خطای ۴۰۰ می‌دهد.
- **نحوهٔ اصلاح دقیق:**
  اضافه کردن `"intro_image_khutbah"` به `KNOWN_STRING_SETTINGS` در `src/khatmsaz/modules/system_settings/service.py:30-37`.

---

### `BUG-02` — غیبت یا برچسب اشتباه خانوادهٔ `KHUTBAH` در ۷ نقطه از پنل وب و بات
- **شدت:** 🔴 **CRITICAL (عدم نمایش و عدم امکان مدیریت خطبه)**
- **محل‌های دقیق در کد:**
  1. **فرم ساخت دسته و فرم تأیید درخواست در پنل وب ([categories.html](../../src/khatmsaz/web/templates/categories.html#L46-L49) و [L106-L109](../../src/khatmsaz/web/templates/categories.html#L106-L109)):** تگ `<select name="group">` فقط `LAAN` و `DUA` دارد و گزینهٔ `KHUTBAH` ندارد.
  2. **عنوان آکاردئون در صفحه دسته‌بندی‌ها ([categories.html](../../src/khatmsaz/web/templates/categories.html#L163)):** کد نوشته است `{% if group_key == 'DUA' %}دعاها و زیارت‌ها{% else %}لعن‌ها{% endif %}`؛ در نتیجه دستهٔ «خطبه‌ها» در پنل ادمین با عنوان اشتباه **«لعن‌ها»** نمایش داده می‌شود!
  3. **صفحه کتابخانه ادعیه ([web/app.py](../../src/khatmsaz/web/app.py#L2263) و [L2312-L2315](../../src/khatmsaz/web/app.py#L2312-L2315) و [devotionals.html](../../src/khatmsaz/web/templates/devotionals.html#L51-L54)):** دیکشنری `_DEVOTIONAL_TYPE_LABELS` و `grouped_rows` فقط `DUA` و `ZIYARAT` دارند و `KHUTBAH` را کاملاً دور می‌اندازند (در لیست نمایش داده نمی‌شود). همچنین محدودیت قدیمی دیتابیس `ck_devotional_assets_type` باید مقدار `'KHUTBAH'` را بپذیرد.
  4. **منوی «ختم‌های من» در بات سازنده ([bot/handlers/my_khatms.py](../../src/khatmsaz/bot/handlers/my_khatms.py#L1075-L1100) و [L1202](../../src/khatmsaz/bot/handlers/my_khatms.py#L1202)):** تاپل `_CATEGORY_ORDER = ("quran", "salawat", "dua", "laan")` فاقد `"khutbah"` است؛ بنابراین ختم‌های خطبه که سازنده می‌سازد در لیست «ختم‌های من» در بات سازنده **کاملاً نامرئی** می‌شوند!
  5. **فیلتر ختم‌های عمومی در بات عضو ([bot/member_scope.py](../../src/khatmsaz/bot/member_scope.py#L43-L65)):** در تابع `khatm_matches_bot`، دیکشنری نگاشت در خطوط ۶۰ تا ۶۴ فاقد `"KHUTBAH"` است (و برای صلواتِ ساده که `content_category_id = None` دارد هم `None` برمی‌گرداند!)؛ در نتیجه در بات عضو، ختم‌های عمومیِ صلوات و خطبه در لیست «ختم‌های عمومی» نمایش داده نمی‌شوند!
  6. **پنل وب سازنده ([web/app.py](../../src/khatmsaz/web/app.py#L705-L717) و [L906](../../src/khatmsaz/web/app.py#L906)):** در `/creator/khatms/new` امکان ساخت ختم خطبه وجود ندارد و در `/creator/khatms` همهٔ ختم‌های دعا، لعن و خطبه به دلیل `template_type == SALAWAT` اشتباهاً زیر شاخهٔ «صلوات» قرار می‌گیرند.
  7. **مسیریابی بات برای خطبه ([modules/bot_registry/service.py](../../src/khatmsaz/modules/bot_registry/service.py#L58-L59)):** تابع `resolve_bot_category` گروه `KHUTBAH` را به `BotCategory.DUA_ZIYARAT` نگاشت می‌کند؛ در کارت دعوت ([bot/handlers/create_khatm.py](../../src/khatmsaz/bot/handlers/create_khatm.py#L2149)) شرط `elif khatm_bot_cat == "DUA":` نوشته شده در حالی که مقدار واقعی `"DUA_ZIYARAT"` است.
- **نحوهٔ اصلاح دقیق:**
  یکپارچه‌سازی کامل `KHUTBAH` در تمام ۷ نقطه و استفاده از تابع واحد تشخیص خانوادهٔ ختم از روی `(template_type, category.group)`.

---

### `BUG-03` — رها شدن کامل مکانیزم تأیید «لعن سفارشی» (`pending_lan_approval`)
- **شدت:** 🔴 **CRITICAL (نقص امنیتی/محتوایی و نبود کامل دکمه تأیید برای ادمین)**
- **محل دقیق در کد:**
  - [src/khatmsaz/bot/handlers/create_khatm.py](../../src/khatmsaz/bot/handlers/create_khatm.py#L944) و [L1986-L2023](../../src/khatmsaz/bot/handlers/create_khatm.py#L1986-L2023)
  - [src/khatmsaz/modules/khatm_workflow/service.py](../../src/khatmsaz/modules/khatm_workflow/service.py#L194-L254)
- **رفتار فعلی (مشکل چیست؟):**
  وقتی سازنده در ویزارد ساخت ختم لعن گزینهٔ «سایر» را انتخاب می‌کند و متن لعن دلخواه می‌نویسد:
  ۱. ستون `pending_lan_approval = True` روی ختم ذخیره می‌شود و به سوپرادمین پیام می‌رود که: *«برای تأیید یا رد این ختم، به پنل ادمین مراجعه کنید.»*
  ۲. **اما در کل پروژه هیچ صفحهٔ وب، هیچ روت FastAPI، هیچ سرویس و هیچ دستور باتی برای مشاهده، تأیید یا رد `pending_lan_approval` وجود ندارد!**
  ۳. بدتر اینکه ختم بلافاصله با وضعیت `ACTIVE` ساخته می‌شود، لینک دعوت در همان لحظه به سازنده داده می‌شود و اعضا می‌توانند قبل از تأیید ادمین عضو شوند و متن لعن تاییدنشده را دریافت کنند!
- **نحوهٔ اصلاح دقیق:**
  ۱. تا زمان تأیید ادمین (`pending_lan_approval == True`)، عضوگیری و ارسال متن لعن سفارشی مسدود بماند (یا وضعیت در انتظار تایید باشد).
  ۲. اضافه شدن دکمه‌های اینلاین `lan_approve:<khatm_id>` و `lan_reject:<khatm_id>` روی پیام ارسالی به ادمین در بات **و همچنین** اضافه شدن تب اختصاصی «🔥 تأیید لعن‌های سفارشی» در پنل وب ادمین.

---

### `BUG-04` — دکمهٔ مرده (Dead Button) در انتخاب ساعت تحویل پس از تأیید عضویت در ختم خصوصی
- **شدت:** 🔴 **CRITICAL (دکمهٔ کاملاً مرده در بات)**
- **محل دقیق در کد:**
  - [src/khatmsaz/bot/handlers/join_requests.py](../../src/khatmsaz/bot/handlers/join_requests.py#L177-L185)
  - [src/khatmsaz/bot/keyboards.py](../../src/khatmsaz/bot/keyboards.py#L185-L204) (`join_delivery_hour_keyboard`)
- **رفتار فعلی (مشکل چیست؟):**
  وقتی یک ختم خصوصی (`PRIVATE`) از نوع تعهد ثابت روزانه (`FIXED_DAILY`) است و سازنده درخواست عضویت کاربر را تأیید می‌کند (`approve_join:`)، بات کیبورد انتخاب ساعت با کال‌بک‌های `jhour:<participation_id>:<hour>` و `jhour_custom:<participation_id>` برای عضو می‌فرستد. **اما در کل کدهای پروژه هیچ هندلری (`@router.callback_query`) برای `jhour:` و `jhour_custom:` نوشته نشده است!** کاربر هر چقدر روی دکمه‌های ساعت می‌زند هیچ اتفاقی نمی‌افتد.
- **نحوهٔ اصلاح دقیق:**
  ثبت هندلرهای `@router.callback_query(F.data.startswith("jhour:"))` و `jhour_custom:` در `join_flow.py` برای ذخیرهٔ ساعت یادآوری عضو.

---

### `BUG-05` — کرش `NameError` در دستور `/report` در بات عضو
- **شدت:** 🔴 **CRITICAL (کرش دستور `/report`)**
- **محل دقیق در کد:**
  - [src/khatmsaz/bot/handlers/report.py](../../src/khatmsaz/bot/handlers/report.py#L30) و [L400](../../src/khatmsaz/bot/handlers/report.py#L400)
- **رفتار فعلی (مشکل چیست؟):**
  در خط ۴۰۰ تابع `personal_report`، تابع `member_instance_id(message.bot)` صدا زده شده است، اما در خط ۳۰ فقط `ensure_participation_matches_bot` از `khatmsaz.bot.member_scope` ایمپورت شده و `member_instance_id` ایمپورت نشده است! زدن `/report` همیشه با `NameError: name 'member_instance_id' is not defined` کرش می‌کند.
- **نحوهٔ اصلاح دقیق:**
  ایمپورت کردن `member_instance_id` از `khatmsaz.bot.member_scope` در بالای فایل `report.py`.

---

### `BUG-06` — پاک شدن ویرایش‌های ادمین روی ادعیهٔ پیش‌فرض در هر بار ری‌استارت سرویس (`Startup Seed Overwrite`)
- **شدت:** 🔴 **CRITICAL (از دست رفتن تغییرات ادمین پس از ری‌استارت)**
- **محل دقیق در کد:**
  - [src/khatmsaz/bootstrap.py](../../src/khatmsaz/bootstrap.py#L317-L342)
  - [src/khatmsaz/modules/content/devotional_seed.py](../../src/khatmsaz/modules/content/devotional_seed.py#L66-L80)
  - [src/khatmsaz/modules/khatm_category/service.py](../../src/khatmsaz/modules/khatm_category/service.py#L135-L167)
- **رفتار فعلی (مشکل چیست؟):**
  در هر بار اجرای `systemctl restart khatmsaz`، تابع `seed_devotional_texts` متن و عنوان و وضعیت فعال بودن (`enabled = True`) چهار دعای پیش‌فرض (`ziyarat-ashura`، `dua-ale-yasin`، `dua-faraj`، `dua-ahd`) را از روی فایل پایتون روی دیتابیس بازنویسی (Overwrite) می‌کند! همچنین `seed_canonical_categories` وضعیت `khutbah-fadakiah` را مجدداً `is_active = True` می‌کند. یعنی اگر ادمین در پنل وب متن زیارت عاشورا را اصلاح کند یا آن را غیرفعال کند، با اولین ری‌استارت سرور تمام تغییراتش پاک می‌شود!
- **نحوهٔ اصلاح دقیق:**
  تغییر منطق Seed به «فقط در صورتی که رکورد در دیتابیس وجود ندارد (`if existing is None`) ایجاد شود» تا ویرایش‌های ادمین در دیتابیس همیشه حفظ شوند.

---

### `BUG-07` — کرش `UniqueConstraint` هنگام آپلود دومین صوت یا بروزرسانی PDF در `/manage_content` و خطای `wrong file identifier` در انتخاب مداح
- **شدت:** 🔴 **CRITICAL (کرش آپلود رسانه و کرش دکمه انتخاب مداح)**
- **محل دقیق در کد:**
  1. [src/khatmsaz/modules/content/service.py](../../src/khatmsaz/modules/content/service.py#L732-L810) (`append_devotional_media_from_message`)
  2. [src/khatmsaz/bot/handlers/devotional.py](../../src/khatmsaz/bot/handlers/devotional.py#L176-L179) (`send_devotional_reciter_choice`)
- **رفتار فعلی (مشکل چیست؟):**
  ۱. وقتی ادمین در `/manage_content` یک فایل صوتی دوم یا یک PDF جدید می‌فرستد، تابع `append_devotional_media_from_message` همیشه `page_num = 0` و `reciter_id = ""` می‌گذارد و بدون چک کردنِ رکورد قبلی، `session.add` می‌زند که به دلیل قید یکتایی `uq_devotional_media_identity` با `IntegrityError` کرش می‌کند!
  ۲. وقتی یک دعا چند مداح دارد و کاربر در بات عضو روی دکمهٔ نام مداح (`devotional_reciter:`) می‌زند، هندلر در خط ۱۷۶ به جای استفاده از `_send_portable_media` مستقیماً `callback.message.answer_audio(chosen.asset_ref)` را صدا می‌زند؛ چون `file_id` متعلق به بات سازنده است، بات عضو با خطای `TelegramBadRequest: wrong file identifier` کرش می‌کند!
- **نحوهٔ اصلاح دقیق:**
  ۱. در `append_devotional_media_from_message` برای `PDF` به صورت Upsert (بروزرسانی رکورد قبلی) و برای `AUDIO` با تخصیص `reciter_id` یکتا یا Upsert عمل شود.
  ۲. در `send_devotional_reciter_choice` از `_send_portable_media` استفاده شود.

---

### `BUG-08` — باگ مالی تبدیل «اعتبار هدیه» به «پول نقد» در لغو ختم و پاک شدن سقف نفرات در فرم پلن‌ها
- **شدت:** 🔴 **CRITICAL (منطق مالی و پلن‌ها)**
- **محل دقیق در کد:**
  1. [src/khatmsaz/modules/wallet/service.py](../../src/khatmsaz/modules/wallet/service.py#L117-L125) (`spend`) در برابر [L309-L335](../../src/khatmsaz/modules/wallet/service.py#L309-L335) (`refund_purchase_invoice`)
  2. [src/khatmsaz/web/app.py](../../src/khatmsaz/web/app.py#L2577-L2579) در برابر [finance.html](../../src/khatmsaz/web/templates/finance.html#L74-L150)
  3. [src/khatmsaz/modules/wallet/repository.py](../../src/khatmsaz/modules/wallet/repository.py#L35-L48) (`add_balance` / `add_credit`)
- **رفتار فعلی (مشکل چیست؟):**
  ۱. هنگام ساخت ختم پولی، تابع `spend` ابتدا از `credit_toman` (اعتبار هدیه/تبلیغاتی) کم می‌کند؛ اما اگر سازنده قبل از ورود اعضا ختم را لغو کند، تابع `refund_purchase_invoice` کل مبلغ فاکتور را با `refund_cash` به `balance_toman` (موجودی نقدیِ قابل برداشت) اضافه می‌کند!
  ۲. در `web/app.py:2577-2578` هنگام ذخیرهٔ فرم پلن در `/finance`، کلیدهای `max_devotional_members` و `max_quran_members` از دیکشنری `entitlements` حذف (`pop`) می‌شوند، اما در `finance.html` اصلاً فیلدی برای آن‌ها وجود ندارد و ذخیرهٔ پلن باعث پاک شدن دائمی آن‌ها می‌شود.
  ۳. در ` finance.html:246` تیک `is_active` در فرم ساخت کد تخفیف وجود دارد اما `app.py:2649` اصلاً آن را نمی‌خواند و همیشه کوپن را فعال می‌سازد.
- **نحوهٔ اصلاح دقیق:**
  ثبت سهم نقدی و اعتباری در تراکنش فاکتور و بازگرداندن هر بخش به همان حساب مبدأ هنگام Refund؛ اصلاح فرم پلن‌ها و کوپن‌ها در پنل جدید؛ و استفاده از قفل ردیف (`with_for_update`) در تراکنش‌های کیف پول.

---

## بخش دوم: باگ‌های مهم و قابلیت‌های قطع‌شده (HIGH — صف‌های بی‌پشتوانه، لینک‌های گم‌شده و کارگرهای خاموش)

### `BUG-09` — عدم تطابق شمارنده‌های داشبورد و نبود کامل صفحهٔ تأیید برای «کاور ختم» و «درخواست نوع ختم»
- **شدت:** 🟠 **HIGH**
- **محل دقیق در کد:**
  - [src/khatmsaz/web/app.py](../../src/khatmsaz/web/app.py#L1385-L1418) (`dashboard`) و [dashboard.html](../../src/khatmsaz/web/templates/dashboard.html#L76-L89)
- **رفتار فعلی (مشکل چیست؟):**
  ۱. در داشبورد پنل ادمین، کارت «پیشنهادهای نوع ختم» تعداد رکوردهای جدول `KhatmRequest` را می‌شمارد اما لینک آن به `/categories` می‌رود که جدول دیگری (`KhatmCategoryRequest`) را نشان می‌دهد! برای جدول `KhatmRequest` هیچ صفحه‌ای در پنل وب وجود ندارد.
  ۲. کارت «کاورهای ختم» در داشبورد تعداد کاورهای `cover_status == 'PENDING'` را می‌شمارد و به `/khatms` لینک می‌دهد، اما در `/khatms` و `/khatms/{id}` هیچ تصویری از کاور و هیچ دکمه‌ای برای تأیید یا رد کاور وجود ندارد!
  ۳. صفحهٔ `/creator-requests` (تأیید درخواست‌های سازنده‌شدن در `app.py:1834`) ساخته شده اما در منوی سمت راست (`base.html:178`)، منوی موبایل (`base.html:264`) و داشبورد (`dashboard.html`) **هیچ لینکی به آن وجود ندارد** (صفحهٔ یتیم / Orphan Route)!

---

### `BUG-10` — عدم نمایش فایل پیوست در صف «پیام‌های گروهی» و ارسال مسدودکننده (Synchronous) در ترد وب و بات اشتباه در `servant_ad`
- **شدت:** 🟠 **HIGH**
- **محل دقیق در کد:**
  - [src/khatmsaz/web/templates/broadcasts.html](../../src/khatmsaz/web/templates/broadcasts.html#L52-L53)
  - [src/khatmsaz/web/app.py](../../src/khatmsaz/web/app.py#L1694-L1723) (`decide_broadcast`) و [L1779-L1791](../../src/khatmsaz/web/app.py#L1779-L1791) (`servant_ad_send`)
- **رفتار فعلی (مشکل چیست؟):**
  ۱. وقتی سازنده در بات یک پیام گروهی همراه با عکس، ویدیو، ویس یا فایل می‌فرستد، در صفحهٔ `/broadcasts` پنل وب فقط متن (`row.item.body`) نشان داده می‌شود و هیچ پیش‌نمایش یا علامتی از فایل پیوست (`media_type` / `media_file_id`) وجود ندارد!
  ۲. وقتی ادمین دکمهٔ «تأیید» پیام گروهی یا «ارسال تبلیغ خدمتگزاران» را در پنل وب می‌زند، حلقهٔ ارسال به هزاران کاربر **به‌صورت هم‌زمان (Synchronous) داخل همان درخواست HTTP** اجرا می‌شود که باعث Timeout شدن مرورگر و Nginx می‌شود.
  ۳. در `servant_ad_send` (`app.py:1781-1783`)، تبلیغ خدمتگزاران بدون `bot_instance_id` (یعنی از طریق بات سازنده به جای بات عضو!) ارسال می‌شود؛ از آنجا که اعضای ختم فقط بات عضو را استارت زده‌اند، ارسال به اکثر مخاطبان با خطای تلگرام مواجه می‌شود!

---

### `BUG-11` — ۴ کارگر زمان‌بند (Scheduler Workers) که در `reminder_engine/service.py` نوشته شده‌اند اما هرگز صدا زده نمی‌شوند!
- **شدت:** 🟠 **HIGH (قابلیت‌های غیرفعال در زمان اجرا)**
- **محل دقیق در کد:**
  - [src/khatmsaz/modules/reminder_engine/service.py](../../src/khatmsaz/modules/reminder_engine/service.py#L131-L148) (`run_once`) در برابر خطوط ۵۳۲ تا ۷۳۵ همان فایل
- **رفتار فعلی (مشکل چیست؟):**
  تابع `run_once` که هر دقیقه اجرا می‌شود، ۴ قابلیت زیر را اصلاً صدا نمی‌زند:
  1. **`delegate_inactive_portions` (خطوط ۵۳۲ تا ۵۷۸):** واگذاری سهم اعضای غیرفعال پس از `inactivity_days` به اعضای پشتیبان (`backup_reader_opt_in`) هرگز اجرا نمی‌شود.
  2. **`_send_open_schedule_reminders` (خطوط ۵۸۱ تا ۶۳۶):** زمان‌بندی کلی ختم آزاد که سازنده در تنظیمات ختم (`schedule_kind`) تنظیم می‌کند هیچ اثری ندارد.
  3. **`_maybe_record_miss_and_notify_creator` (خطوط ۶۹۹ تا ۷۳۵) و بررسی عبور از `deadline_at` در `ShareOccurrence`:** وقتی مهلت روزانهٔ یک سهم تعهدی (`deadline_at`) می‌گذرد، هیچ ثبت غیبت (`miss`) یا اطلاع‌رسانی به سازنده (`miss_notice_threshold`) برای رکوردهای `ShareOccurrence` انجام نمی‌شود.
  4. **`daily_digest_enabled` (خلاصهٔ روزانه در تنظیمات کاربر):** در موتور جدید `ShareOccurrence` نادیده گرفته شده است.

---

### `BUG-12` — قفل شدن ورود سازندگان جدید به مینی‌اپ/پنل سازنده (`403 Forbidden`)
- **شدت:** 🟠 **HIGH**
- **محل دقیق در کد:**
  - [src/khatmsaz/web/app.py](../../src/khatmsaz/web/app.py#L642-L643) (`_authenticate_telegram_mini_app`)
- **رفتار فعلی (مشکل چیست؟):**
  هنگام ورود سازنده به مینی‌اپ (`/mini/creator/auth`)، خط ۶۴۲ چک می‌کند: `if not await khatm_service.list_my_created(session, user.id): raise PermissionError`. یعنی کاربری که نقش `CREATOR` دارد اما هنوز اولین ختم خود را نساخته و می‌خواهد از طریق مینی‌اپ اولین ختمش را بسازد، با خطای `403 این بخش برای حساب شما فعال نیست` مسدود می‌شود!

---

### `BUG-13` — ناهماهنگی ساعت مهلت روزانه (`daily_deadline_hour=24` در برابر بازهٔ مجاز `0..23`)
- **شدت:** 🟠 **HIGH**
- **محل دقیق در کد:**
  - [src/khatmsaz/bot/handlers/create_khatm.py](../../src/khatmsaz/bot/handlers/create_khatm.py#L1063) در برابر [src/khatmsaz/modules/khatm/service.py](../../src/khatmsaz/modules/khatm/service.py#L305)
- **رفتار فعلی (مشکل چیست؟):**
  ویزارد ساخت ختم مقدار `daily_deadline_hour` را روی `24` (پایان شب) می‌گذارد، اما تابع ویرایش تنظیمات ختم در `khatm/service.py:305` فقط اعداد `0 <= daily_deadline_hour <= 23` را مجاز می‌داند! همچنین در مرحلهٔ تأیید نهایی ویزارد (`create_khatm.py:1445-1476` و `1575-1583`)، سیاست `FIXED_DAILY` نمایش داده نمی‌شود و در صورت ویرایش «مقدار هدف» از صفحهٔ تأیید، مرحلهٔ پرسیدن `commitment_policy` و `daily_commitment_amount` جا می‌افتد.

---

### `BUG-14` — گزارش ماهانه (`ClosedMonthReport`) که تمام دعاها، زیارات، خطبه‌ها و لعن‌ها را «صلوات» حساب می‌کند و `ShareOccurrence` را نمی‌شمارد!
- **شدت:** 🟠 **HIGH**
- **محل دقیق در کد:**
  - [src/khatmsaz/modules/reporting/service.py](../../src/khatmsaz/modules/reporting/service.py#L88-L181)
  - [src/khatmsaz/modules/monthly_report/service.py](../../src/khatmsaz/modules/monthly_report/service.py#L44-L86)
- **رفتار فعلی (مشکل چیست؟):**
  ۱. کلاس `ClosedMonthReport` فیلدهای `dua_count` و `laan_count` دارد، اما تابع `get_closed_month_report` هرگز آن‌ها را پر نمی‌کند (همیشه صفر می‌مانند) و چون ختم‌های دعا/زیارت/لعن/خطبه دارای `template_type = SALAWAT` هستند، همهٔ آن‌ها را جمعِ صلوات حساب می‌کند!
  ۲. گزارش ماهانه اصلاً جدول `share_occurrences` (موتور جدید سهم‌ها) را کوئری نمی‌زند!
  ۳. پیام گزارش ماهانه بدون `bot_instance_id` (از طریق بات سازنده به جای بات عضو) ارسال می‌شود.

---

### `BUG-15` — ناهماهنگی ظرفیت (`capacity`) و لیست انتظار (`WaitingList`) برای ختم قرآن و عدم обернуть (Wrap-Around) در ختم آزاد چنددورهٔ قرآن
- **شدت:** 🟡 **MEDIUM**
- **محل دقیق در کد:**
  - [src/khatmsaz/modules/khatm_workflow/service.py](../../src/khatmsaz/modules/khatm_workflow/service.py#L355-L357) و [L414-L420](../../src/khatmsaz/modules/khatm_workflow/service.py#L414-L420)
  - [src/khatmsaz/modules/participation/service.py](../../src/khatmsaz/modules/participation/service.py#L98-L115) (`advance_open_reading`)
- **رفتار فعلی (مشکل چیست؟):**
  ۱. در `_complete_join` (خط ۳۵۶)، ظرفیت (`khatm.capacity`) فقط زمانی بررسی می‌شود که `template_type == SALAWAT` باشد و برای `QURAN_PAGE` نادیده گرفته می‌شود؛ برعکس در `leave_khatm` (خط ۴۱۴) هنگام ارتقای نفر بعدی از لیست انتظار، فقط برای `QURAN_PAGE` سهم تخصیص داده می‌شود!
  ۲. در `advance_open_reading`، سقف پیش‌فرض `max_page = 604` است و برای ختم آزادِ قرآن که بیش از ۱ دور (`repetition_target > 604`) دارد، در حالت منظم روزانه پس از صفحهٔ ۶۰۴ به صفحهٔ ۱ برنمی‌گردد.

---

### `BUG-16` — کوئری در هر درخواست HTTP (Middleware)، کوئری‌های N+1، نبود صفحه‌بندی (Pagination) و جا افتادن مدل‌ها در Alembic
- **شدت:** 🟡 **MEDIUM (کارایی و نگهداری)**
- **محل دقیق در کد:**
  1. **کوئری دیتابیس در تمام درخواست‌های HTTP ([web/app.py](../../src/khatmsaz/web/app.py#L220-L226)):** میدل‌ور `security_headers` در هر بار لود شدن هر صفحه‌ای یک سشن دیتابیس باز می‌کند تا `panel_logo_url` را بخواند (باید در حافظه کش شود و فقط هنگام تغییر لوگو بروز گردد).
  2. **کوئری‌های N+1:** در `/phone-verifications` (`L1535`)، `/broadcasts` (`L1628`)، `/creator-requests` (`L1845`) و `/categories` (`L2084`) داخل حلقهٔ `for` به ازای هر ردیف ۱ یا ۲ کوئری جداگانه به دیتابیس زده می‌شود.
  3. **نبود صفحه‌بندی (Pagination):** در `/khatms/{id}` (محدود به ۱۰۰ عضو بدون جستجو)، `/audit` (محدود به ۱۰۰ لاگ)، `/templates` (محدود به ۲۵۰ قالب)، `/finance` (محدود به ۳۰ فاکتور) و `/users` (نمایش فقط اولین اکانت لینک‌شده و عدم نمایش شماره موبایل در جدول).
  4. **جا افتادن مدل‌ها در رجیستری Alembic ([core/model_registry.py](../../src/khatmsaz/core/model_registry.py#L1-L33)):** مدل‌های `sms_subscription.models` و `system_settings.models` در `model_registry.py` ایمپورت نشده‌اند.

---

### `BUG-17` — پاک شدن کپشن اصلی ویدیوی خطبه فدک هنگام ارسال سهم و عدم ذخیرهٔ کپشن ویدیوها
- **شدت:** 🔴 **CRITICAL (گزارش مستقیم مالک)**
- **محل دقیق در کد:**
  - [src/khatmsaz/bot/handlers/devotional.py](../../src/khatmsaz/bot/handlers/devotional.py#L112-L118) (`send_devotional_share_card`)
  - [src/khatmsaz/bot/handlers/manage_content.py](../../src/khatmsaz/bot/handlers/manage_content.py#L52-L127) (`set_video_direct`)
  - [src/khatmsaz/modules/content/service.py](../../src/khatmsaz/modules/content/service.py#L584-L635) (`add_devotional_video_page` و `append_devotional_media_from_message`)
  - [src/khatmsaz/modules/content/models.py](../../src/khatmsaz/modules/content/models.py#L101) (`DevotionalMedia.reciter_label`)
  - [src/khatmsaz/bot/occurrence_adapter.py](../../src/khatmsaz/bot/occurrence_adapter.py#L54-L98) (`build_occurrence_delivery_components`)
- **رفتار فعلی (مشکل چیست؟):**
  ۱. وقتی پیام سهم خطبه فدک برای عضو ارسال می‌شود، ویدیوی مربوط به آن قسمت ارسال می‌گردد اما کپشن اصلی ویدیو (شامل هشتگ `#کلیپ_تصویری_خطابه_فدک قسمت X`، `🕯طرح ختم خطابه فدک` و لینک شرح خطبه در سایت خدمتگزاران) پاک شده و به جای آن فقط یک عبارت کوتاه `🎬 خطبه فدکیه حضرت زهرا (س) — بخش X` قرار می‌گیرد!
  ۲. در `manage_content.py` و `content/service.py` هنگام ثبت ویدیو از طریق `/set_video` یا پنل مدیریت، `target_msg.caption` اصلاً خوانده و ذخیره نمی‌شود و ستون `reciter_label` هم محدود به ۱۰۰ کاراکتر (`String(100)`) است.
  ۳. حتی اگر برای یک `ShareOccurrence` قبلاً `delivery_components` کش شده باشد، کپشن قدیمی در کش باقی مانده است.
- **رفتار درست (چگونه اصلاح می‌شود؟):**
  ۱. تغییر نوع ستون `DevotionalMedia.reciter_label` به `String` (`TEXT` نامحدود) در مدل و در self-heal استارتاپ (`bootstrap.py`).
  ۲. ذخیرهٔ کپشن کامل ویدیو در `reciter_label` هنگام ثبت ویدیو از بات (`set_video_direct` و `append_devotional_media_from_message`)، اسکریپت `register_khutbah_fadakiah.py` و پنل وب ادمین (`/devotionals/media/save`).
  ۳. افزودن دیکشنری کپشن‌های پیش‌فرض ۵ قسمت ویدیوی خطبه فدکیه (`KHUTBAH_FADAKIAH_VIDEO_CAPTIONS`) و تابع `resolve_devotional_video_caption` در `content/service.py` تا حتی برای ویدیوهای قبلی که بدون کپشن ثبت شده‌اند، کپشن کامل و اصلی کانال `@khedmatgozaran_group` زیر ویدیو ارسال شود.
  ۴. به‌روزرسانی خودکار کپشن ویدیو در `occurrence_adapter.py` هنگام خواندن `delivery_components` کش‌شدهٔ قبلی.

---

### `BUG-18` — ختم آزاد: ایجاد رزرو ۷ روزه، قفل ظرفیت، انقضای سهم و ارسال پیام منسوخ «این رزرو ۷ روز اعتبار دارد»
- **شدت:** 🔴 **CRITICAL (مغایر با سند مشخصات V3 و دستور مستقیم مالک)**
- **محل دقیق در کد:**
  - [src/khatmsaz/modules/share_occurrence/delivery.py](../../src/khatmsaz/modules/share_occurrence/delivery.py#L272-L285) (`prepare_numeric`)
  - [src/khatmsaz/bot/handlers/member_commitment.py](../../src/khatmsaz/bot/handlers/member_commitment.py#L247-L255) (`enter_count`)
- **رفتار قبلی (مشکل):**
  هنگامی که مخاطب در ختم آزاد عددی درخواست سهم می‌کرد، تابع `reservations.create_reservation` فراخوانی می‌شد و سهم را با `reservation_id` و انقضای ۱۶۸ ساعته ثبت می‌کرد. در نتیجه ظرفیت ختم به مدت ۷ روز قفل می‌شد و ربات به کاربر پیام می‌داد: «این رزرو ۷ روز اعتبار دارد و اگر نخوانید آزاد می‌شود!».
- **اصلاح انجام‌شده:**
  طبق قانون صریح سند V3 (`02_COMMITMENT_VS_FREE_AND_REMINDERS.md` بند ۲-ب)، رزرو ۷ روزه در ختم آزاد به طور کامل حذف شد. سهم‌ها با `committed = False` و `reservation_id = None` به صورت فوری و بدون قفل ظرفیت صادر می‌شوند و پیام انقضا حذف گردید.

---

### `BUG-19` — ختم آزاد: هدایت اشتباه به منوی انتخاب شیوهٔ تعهد («این ختم تعهدی است 🌱 دو راه برای شرکت داری...»)
- **شدت:** 🔴 **CRITICAL (تجربه کاربری و انطباق با مستندات)**
- **محل دقیق در کد:**
  - [src/khatmsaz/bot/handlers/portions.py](../../src/khatmsaz/bot/handlers/portions.py#L640-L670) (`ask_contribution_amount`)
- **رفتار قبلی (مشکل):**
  شرط `is_member_choice` شامل `khatm.khatm_type == KhatmTypeEnum.OPEN` بود. در نتیجه وقتی کاربر در ختم آزاد دکمهٔ «دریافت سهم» را می‌زد، به تابع `start_commitment_mode_picker` هدایت می‌شد و پیامی دریافت می‌کرد که می‌گفت «این ختم تعهدی است! آیا می‌خواهی تعهد منظم انتخاب کنی یا تعهد تعدادی؟»؛ در حالی که ختم از اساس آزاد بوده و تعهدی نیست!
- **اصلاح انجام‌شده:**
  شرط بررسی شد تا منوی تعهد منحصراً برای ختم‌های تعهدی (`COMMITMENT`) اجرا شود. برای ختم‌های آزاد (`OPEN`)، مستقیماً از کاربر پرسیده می‌شود: «می‌خواهید چند {واحد} از این ختم قرائت کنید؟ عدد مورد نظر را بفرستید:» و مستقیماً وارد صدور سهم آزاد می‌شود.

---

### `BUG-20` — خطبه فدکیه: بسته شدن و تکمیل زودهنگام کل ختم پس از قرائت فقط ۱ بخش
- **شدت:** 🔴 **CRITICAL (محاسبه دور و هدف کل خطبه)**
- **محل دقیق در کد:**
  - [src/khatmsaz/modules/share_occurrence/delivery.py](../../src/khatmsaz/modules/share_occurrence/delivery.py#L324-L342) (`record_progress`)
  - [src/khatmsaz/modules/khatm_workflow/service.py](../../src/khatmsaz/modules/khatm_workflow/service.py#L225-L235) (`create_khatm_workflow`)
- **رفتار قبلی (مشکل):**
  هنگامی که سازنده در ویزارد هدف کل ختم را ۱ دور وارد می‌کرد، در دیتابیس `repetition_target = 1` ذخیره می‌شد. وقتی عضوی بخش اول (بخش ۱ از ۵) را می‌خواند، سیستم `total = 1 >= target (1)` تشخیص داده و کل ختم را بلافاصله به وضعیت `COMPLETED` تغییر می‌داد و می‌بست!
- **اصلاح انجام‌شده:**
  ۱. در ویزارد و سرویس ساخت/ویرایش ختم، واحد هدف «دور» تعیین شد و عدد ورودی سازنده در ۵ ضرب می‌شود ($1 \times 5 = 5$ بخش).
  ۲. در `record_progress` و `prepare_numeric` مکانیسم خودترمیمی اضافه شد: اگر هدف خطبه کمتر از ۵ باشد، به عنوان دور در نظر گرفته شده و در ۵ ضرب می‌شود تا با خواندن بخش ۱ بسته نشود و تا پایان بخش ۵ فعال بماند.

---

### `BUG-21` — خطبه فدکیه: تقلیل درخواست چند بخش (مثلاً ۲ بخش) در ختم آزاد به سقف ۱ بخش
- **شدت:** 🔴 **CRITICAL**
- **محل دقیق در کد:**
  - [src/khatmsaz/modules/share_occurrence/delivery.py](../../src/khatmsaz/modules/share_occurrence/delivery.py#L260-L285) (`prepare_numeric`)
- **رفتار قبلی (مشکل):**
  در ختم آزاد، فرمول `available = max(target - total, 0)` با مقدار `target = 1` مقایسه می‌شد؛ لذا اگر کاربری عدد ۲ (۲ بخش) را درخواست می‌کرد، مقدار به سقف باقی‌ماندهٔ هدف ۱ تقلیل می‌یافت و فقط ۱ بخش ارسال می‌شد.
- **اصلاح انجام‌شده:**
  محاسبهٔ سقف در `prepare_numeric` قبل از چک باقی‌مانده بر مبنای `effective_target` (هدف دور ضرب‌در ۵) اصلاح شد تا درخواست ۲ بخش دقیقاً ۲ بخش (بخش ۱ و ۲) را تخصیص دهد.

---

### `BUG-22` — ختم آزاد: سوال بیجای ساعت تحویل روزانه (`AskDeliveryHour`) در فلوی ورود
- **شدت:** 🟡 **MEDIUM**
- **محل دقیق در کد:**
  - [src/khatmsaz/bot/handlers/start.py](../../src/khatmsaz/bot/handlers/start.py#L510-L540) (`resume_join_after_registration`)
- **رفتار قبلی (مشکل):**
  هنگامی که کاربر جدید پس از ثبت شماره به ختم آزاد ملحق می‌شد، ربات از او ساعت یادآوری روزانه می‌پرسید؛ در حالی که ختم آزاد هیچ‌گونه ارسال ساعتی یا ریمایندری ندارد.
- **اصلاح انجام‌شده:**
  برای ختم‌های `OPEN` مرحلهٔ `AskDeliveryHour` کلاً دور زده شده و مستقیماً کارت خوش‌آمد و مشارکت آزاد به کاربر نمایش داده می‌شود.

---

### `BUG-23` — درگاه پی‌پینگ: کسر پول از کارت اما عدم بازگشت (Callback)، عدم تأیید و عدم شارژ کیف پول
- **شدت:** 🔴 **CRITICAL (اختلال کامل سیستم مالی و تراکنش‌های بانکی)**
- **محل دقیق در کد:**
  - [src/khatmsaz/web/app.py](../../src/khatmsaz/web/app.py#L557-L586) (`payping_callback`)
  - [src/khatmsaz/config.py](../../src/khatmsaz/config.py#L69) (`payping_callback_url`)
  - [src/khatmsaz/modules/wallet/payping.py](../../src/khatmsaz/modules/wallet/payping.py#L90-L157) (`PayPingGateway`)
  - تنظیمات سرور زنده: `/root/khatmsaz/.env` و کانفیگ Apache در `/etc/apache2/sites-enabled/`
- **کشف و اثبات روی سرور زنده (`91.107.137.22`):**
  با اتصال SSH و بررسی لاگ‌های آپاچی (`/var/log/apache2/other_vhosts_access.log`) و پایگاه‌داده مشخص شد:
  1. در لاگ آپاچی فراخوانی‌های بازگشت با خطای `405 Method Not Allowed` ثبت شده‌اند:
     `api.khatmsaz.com:443 ... "GET /payments/payping/callback HTTP/1.1" 405`
  2. با شبیه‌سازی درخواست POST نیز خطای `400 Bad Request` دریافت شد:
     `curl -X POST -d 'status=1&clientRefId=...&paymentCode=...&paymentRefId=...&amount=...' -> 400 Bad Request ("پاسخ پرداخت نامعتبر است")`
- **علل ریشه‌ای (Root Causes):**
  1. **خطای ساختاری در پارس اطلاعات فرم پی‌پینگ:** کد در `web/app.py:571` نوشته است:
     ```python
     raw_data = form.get("data", "")
     data = json.loads(str(raw_data))
     ```
     طبق مستندات رسمی پی‌پینگ (`application/x-www-form-urlencoded`)، پی‌پینگ اصلاً فیلدی به نام `data` حاوی رشتهٔ JSON ارسال نمی‌کند! مقادیر `status`، `clientRefId`، `paymentCode`، `paymentRefId` و `amount` مستقیماً به عنوان کلیدهای سطح اول فرم ارسال می‌شوند. به همین دلیل `form.get("data")` همیشه خالی است، `json.loads("")` خطای `JSONDecodeError` می‌دهد و کد با پاسخ ۴۰۰ تراکنش را دور می‌اندازد و هرگز تابع Verify پی‌پینگ را صدا نمی‌زند!
  2. **محدود بودن متد به POST (`@app.post`):** در صورتی که مرورگر کاربر یا پی‌پینگ به صورت `GET` (همراه با کوئری‌پارامترهای `refid` و `clientrefid`) ریدایرکت شود یا کاربر روی دکمهٔ بازگشت به سایت کلیک کند، سرور خطای `405 Method Not Allowed` داده و کاربر صفحه خطا می‌بیند.
  3. **عدم تطابق دامنه در پنل پی‌پینگ:** در فایل `.env` سرور آدرس `PAYPING_CALLBACK_URL` برابر با `https://api.khedmatgozaran.com/...` تنظیم شده در حالی که دامنه‌های اصلی سیستم `api.khatmsaz.com` هستند. اگر توکن پی‌پینگ در پنل روی دامنهٔ دیگری ثبت شده باشد، شاپرک/پی‌پینگ ریدایرکت را مسدود یا دچار مغایرت دامنه می‌کند.
  4. **علت کسر وجه و عدم شارژ کیف پول:** شبکه شاپرک هنگام پرداخت وجه را موقتاً از حساب کاربر کسر می‌کند، اما تا زمانی که پذیرنده متد `/v3/pay/verify` را ظرف مهلت ۱۵ الی ۳۰ دقیقه صدا نزند، تراکنش قطعی نمی‌شود. به دلیل کرش کردن کال‌بک، تابع Verify فراخوانی نشده و کیف پول شارژ نمی‌شود؛ وجه کسر شده نیز طبق قوانین شاپرک پس از اتمام مهلت به کارت کاربر برگشت داده می‌شود.
- **راهکار اصلاح در زمان کدنویسی:**
  ۱. پشتیبانی هم‌زمان از متدهای `GET` و `POST` در روت کال‌بک پی‌پینگ.
  ۲. خواندن پارامترها به‌صورت منعطف و Case-Insensitive هم از فرم و هم از کوئری‌استرینگ (`clientRefId`/`clientrefid`، `paymentCode`/`code`، `paymentRefId`/`refid`/`refId`، `amount`).
  ۳. حذف کامل انتظار رشتهٔ ساختگی JSON در کلید `data`.
  ۴. تطبیق دامنهٔ بازگشت در `.env` با دامنهٔ مجاز تأییدشده در پنل پی‌پینگ.

---

این جدول دقیقاً نشان می‌دهد چرا ادمین تا امروز مجبور بوده برای کارهای روزمره دستورات پیچیده در بات بزند و چرا در **پنل ادمین جدید** تمام این موارد دارای صفحه و دکمهٔ گرافیکی می‌شوند:

| ردیف | قابلیت / عملیات مدیریتی | در حال حاضر چطور انجام می‌شود؟ | وضعیت در پنل وب فعلی | طراحی در پنل وب جدید (مستر مادر) |
| :---: | :--- | :--- | :--- | :--- |
| **۱** | **مدیریت ویدیوهای بخش‌های خطبه، چند مداح برای یک دعا، تصاویر چندصفحه‌ای و PDF (`DevotionalMedia`)** | فقط با دستورات متنی بات (`/manage_content`، `/set_video`، `/admin_devotional_audio`، `/admin_devotional_pdf`) | ❌ **کاملاً ناموجود!** پنل وب فقط ۲ فیلد قدیمی تک‌فایلی `image_ref` و `audio_ref` را نشان می‌دهد | **استودیوی کامل چندرسانه‌ای در پنل وب:** آپلود مستقیم ویدیو (بخش ۱ تا ۵ خطبه)، آپلود چند صوت با نام مداح، آپلود چند عکس و PDF، پیش‌نمایش، مرتب‌سازی و حذف |
| **۲** | **مدیریت ۶۰۴ صفحهٔ قرآن کریم، صوت قاریان و وضعیت کانال منبع (`QuranPageAsset` / `KhatmReciter`)** | فقط با دستورات بات (`/admin_quran_asset`، `/admin_quran_source_status`، `/admin_quran_source_seed`) | ❌ **کاملاً ناموجود!** | **صفحهٔ مدیریت بانک قرآن و قاریان:** مشاهده جدول ۶۰۴ صفحه، وضعیت تصویر/صوت هر صفحه در تلگرام و بله، دکمهٔ بارگذاری خودکار نقشهٔ کانال و مدیریت قاریان |
| **۳** | **تأیید یا رد ختم‌های لعن سفارشی (`pending_lan_approval`)** | ❌ هیچ دستوری ندارد! (`BUG-03`) | ❌ **کاملاً ناموجود!** | **تب «تأیید لعن‌های سفارشی» در مرکز نظارت:** مشاهده متن، ویرایش متن، تأیید و فعال‌سازی یا رد با ذکر دلیل |
| **۴** | **تأیید یا رد کاور ختم‌ها (`cover_status = PENDING`)** | فقط با دستور متنی `/admin_covers` و `/admin_review_cover <id> approve` | ❌ **فقط شمارنده دارد، صفحه و دکمه ندارد!** | **تب «بررسی کاور ختم‌ها» در مرکز نظارت:** پیش‌نمایش تصویر کاور و تأیید/رد تک‌کلیکی |
| **۵** | **بررسی درخواست‌های کلی نوع ختم جدید (`KhatmRequest`)** | فقط با دستور متنی `/admin_requests` و `/admin_approve_request <id>` | ❌ **فقط در داشبورد شمرده می‌شود، صفحه ندارد!** | **تب «پیشنهادهای نوع ختم» در مرکز نظارت:** مشاهده توضیحات و فایل پیوست کاربر + تأیید/رد با یادداشت |
| **۶** | **شارژ/کسر دستی کیف پول کاربر، اهدای اعتبار هدیه و استرداد (Refund) فاکتور** | فقط با دستور متنی `/admin_grant_credit <chat_id> <amount> <reason>` | ❌ **کاملاً ناموجود!** | **عملیات کامل کیف پول و فاکتور در پنل وب:** فرم شارژ/کسر نقدی و اعتباری + دکمهٔ استرداد وجه کنار هر فاکتور |
| **۷** | **تغییر دستی پلن یک کاربر (`FREE` / `BASIC` / `PRO`) و اشتراک پیامک او** | فقط با دستور `/admin_plan_set` در بات | ❌ **کاملاً ناموجود!** | **مدیریت پلن و اشتراک پیامک در پروفایل کاربر:** تغییر پلن کاربر و تمدید/افزودن اشتراک پیامک با یک کلیک |
| **۸** | **ساخت و ویرایش متن قالب‌های پیام چندزبانه (`MessageTemplate`)** | فقط با دستور `/admin_template_set <key> <locale> <body>` | ⚠️ **فقط نمایش و خاموش/روشن کردن!** امکان ساخت یا ویرایش متن ندارد | **ویرایشگر زندهٔ قالب‌های پیام و متون بات (i18n):** ویرایش متن فارسی، عربی و انگلیسی با پیش‌نمایش متغیرها |
| **۹** | **تنظیمات سراسری سیستم (`default_reminder_hour`, `inactivity_days`) و نرخ پاداش تبلیغات (`AdRewardRate`)** | فقط با دستورات `/admin_settings`، `/admin_setting_set` و `/admin_ad_rate` | ❌ **کاملاً ناموجود!** | **صفحهٔ تنظیمات سراسری و زمان‌بندی:** فرم گرافیکی برای تمام پارامترهای سیستم، ساعت پیش‌فرض یادآوری، روزهای عدم فعالیت و نرخ پاداش تبلیغات |
| **۱۰** | **مدیریت کامل یک ختم توسط ادمین (ویرایش، توقف، لغو، تکمیل، مدیریت اعضا و سهم‌ها، خروجی اکسل)** | سازنده در پنل خودش بخشی را دارد، اما ادمین در `/khatms/{id}` فقط لیست ۱۰۰ نفر اول را بدون هیچ دکمه‌ای می‌بیند! | ⚠️ **صرفاً خواندنی (Read-Only)!** | **کنترل کامل ادمین روی هر ختم و هر عضو:** ویرایش تمام فیلدهای ختم، ثبت دستی سهم، حذف عضو، ارتقای لیست انتظار، خروجی اکسل و تولید لینک/QR دعوت |
| **۱۱** | **صندوق تیکت‌ها، پیشنهادات و پیام مستقیم ادمین به هر کاربر** | فقط از طریق فوروارد در چت تلگرام (`suggestions.py`) | ❌ **کاملاً ناموجود!** | **مرکز پشتیبانی و ارتباط با کاربر در پنل وب:** مشاهده پیام‌های کاربران و ارسال پاسخ مستقیم از وب به چت تلگرام/بله کاربر |
