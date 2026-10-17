# MASTER-31: دسترسی همگانی به ارسال پیام گروهی (مشروط به خرید بسته)، نظارت دکمه‌ای در بات ادمین همراه با پیش‌نمایش عکس، و رندر تصویر در پنل وب

> **وضعیت سند:** تصویب‌شده و اعمال‌شده بر روی سورس‌کد و سرور لایو  
> **شناسه تصمیم:** `DEC-PY-0031`  
> **مخاطب:** تیم توسعه، ادمین سیستم، ایجنت‌های بعدی  
> **تاریخ:** ۱۵ اکتبر ۲۰۲۶ (۲۳ مهر ۱۴۰۵)

---

## ۱. چرایی و زمینه تغییر (Context & Rationale)

به درخواست صریح و مستقیم کارفرما:
> «نه اشتباهه دسترسی به پیام گروهی برای پلن حرفه ای نه کسی بستشو بخره میتونه پیام گروهی بفرسته
> فایل مستر رو بررسی بکن و فایل مستر اینم بساز یا ادیت بکن تا درست پیاده سازیش بکنی برام خیلی خرابه این
> من عکسشو نمیتونم ببینم بعد میخوام تو همون بات ادمین بتونم تایید و رد بکنم»

سه ایراد اساسی در سیستم پیام گروهی شناسایی و برطرف شد:
1. **انحصار اشتباه به پلن حرفه‌ای (PRO):** ارسال پیام گروهی فقط برای کاربران دارای پلن حرفه‌ای مجاز شده بود؛ در حالی که طبق قانون بیزینس، ارسال پیام گروهی بسته‌ای است و هر سازنده‌ای با هر پلنی (رایگان، پایه یا حرفه‌ای) به شرط داشتن موجودی کافی در کیف پول برای پوشش هزینهٔ بسته‌ها می‌تواند پیام گروهی ارسال نماید.
2. **عدم نمایش تصویر پیوست در پنل وب ادمین:** در صفحهٔ `/broadcasts` فقط متن `فایل پیوست: photo (تلگرام دارد)` درج می‌شد و ادمین نمی‌توانست عکس ارسالی را ببیند.
3. **نبود امکان بررسی و تأیید/رد در بات ادمین:** هنگام ارسال درخواست پیام گروهی، تنها یک نوتیفیکیشن متنی خام به ادمین فرستاده می‌شد که ادمین را به پنل وب ارجاع می‌داد؛ دکمه‌های تأیید/رد در بات وجود نداشت و در صورت ارسال عکس، خود تصویر به بات ادمین ارسال نمی‌شد.

---

## ۲. مشخصات و اصلاحات فنی اعمال‌شده

### الف) آزادسازی دسترسی به پیام گروهی بر اساس بسته و کیف پول
1. **سرویس پیام گروهی (`src/khatmsaz/modules/broadcast/service.py`):**
   - شرط محدودیت `if plan != PlanTier.PRO:` به طور کامل از متد `submit()` حذف گردید.
   - هر کاربری که هزینه بسته‌ها (`math.ceil(audience_count / package_size) * unit_price`) را در کیف پول داشته باشد، پیامش با موفقیت کسر هزینه و در وضعیت `PENDING` ثبت می‌شود.
2. **بات سازنده (`src/khatmsaz/bot/handlers/creator_broadcast.py`):**
   - متن گمراه‌کنندهٔ `⭐ دسترسی به ارسال پیام گروهی ویژهٔ کاربران دارای پلن حرفه‌ای است.` از مراحل انتخاب مخاطب و تایید پیام حذف شد.
   - خطای `PlanFeatureUnavailableError` از فلو برداشته شد و کنترل موجودی کیف پول و مخاطب خالی با دقت بالا انجام می‌شود.
3. **پنل وب سازندگان (`src/khatmsaz/web/templates/creator_broadcasts.html` و `src/khatmsaz/web/app.py`):**
   - بنر اخطار `plan_required` حذف و با بنر شفاف `insufficient_funds` جایگزین شد که کاربر را مستقیماً به صفحهٔ شارژ کیف پول هدایت می‌کند.

### ب) ارسال نوتیفیکیشن تعاملی و تصویر به بات ادمین (`@khatmsaz_admin_bot`)
1. **تکمیل تابع نوتیفیکیشن (`src/khatmsaz/bot/handlers/creator_broadcast.py`):**
   - تابع `_notify_admins_of_broadcast_request` مجهز به ایجاد کیبورد اینلاین دو دکمه‌ای شد:
     - `[✅ تأیید و ارسال]` (`callback_data="admin_broadcast:approve:{item.id}"`)
     - `[❌ رد و عودت وجه]` (`callback_data="admin_broadcast:reject:{item.id}"`)
   - در صورت وجود رسانه از نوع `photo`، به جای پیام متنی، متد `notify_super_admins_photo` فراخوانی شده و تصویر همراه با کپشن کامل به بات ادمین فرستاده می‌شود.
2. **سرویس نوتیفیکیشن ادمین (`src/khatmsaz/bot/admin_notifications.py`):**
   - تابع `notify_super_admins_photo` برای جلوگیری از خطاهای `wrong file_id` بین بات‌ها، در صورتی که `source_bot` به صراحت مشخص نباشد، به طور خودکار از `registry.get_creator_bot(Platform.TELEGRAM)` به عنوان منبع دانلود باینری عکس استفاده می‌کند و عکس را به صورت `BufferedInputFile` برای تمام سوپرادمین‌ها در `@khatmsaz_admin_bot` ارسال می‌کند.
   - سقف کپشن تلگرام (۱۰۲۴ کاراکتر) رعایت شده و در صورت طولانی بودن متن، خلاصهٔ ایمن نمایش داده می‌شود.
3. **هندلرهای بات ادمین (`src/khatmsaz/bot/handlers/admin_bot/handlers.py`):**
   - تابع ایمن `_safe_edit_admin_message` پیاده‌سازی شد: اگر پیام نوتیفیکیشن حاوی عکس باشد از `edit_caption` و اگر متنی باشد از `edit_text` استفاده می‌کند تا خطای `TelegramBadRequest: there is no text in the message to edit` رخ ندهد.
   - با کلیک روی «تأیید و ارسال»، پیام فوراً در دیتابیس تایید شده، ماژول ارسال `deliver_broadcast` اجرا می‌گردد و کپشن پیام به `✅ پیام همگانی تأیید شد و برای X مخاطب ارسال گردید.` تغییر می‌یابد.
   - با کلیک روی «رد و عودت وجه»، پیام رد شده، کل هزینه به کیف پول سازنده بازگشت داده می‌شود و کپشن پیام به `❌ پیام همگانی رد شد و مبلغ به کیف پول عودت داده شد.` تغییر می‌یابد.

### ج) پیش‌نمایش تصویر در پنل وب ادمین
1. **اندپوینت اختصاصی استریم رسانه (`src/khatmsaz/web/app.py`):**
   - مسیر `GET /broadcasts/{broadcast_id}/media` پیاده‌سازی شد.
   - احراز هویت ادمین و سازنده به صورت ایمن بررسی می‌شود.
   - تصاویر دانلودشده در پوشهٔ لوکال `static/uploads/broadcasts/{id}.jpg` کش می‌شوند تا از دانلود مجدد از تلگرام و ایجاد کندی جلوگیری شود.
2. **قالب پنل ادمین (`src/khatmsaz/web/templates/broadcasts.html`):**
   - در صورت وجود عکس (`row.item.media_type == 'photo'`)، تگ تصویر با پیش‌نمایش زیبا، گوشه‌های گرد، حداکثر ارتفاع مناسب و fallback هوشمند جاوااسکریپتی به صفحه افزوده شد.

### د) ماژول متمرکز توزیع پیام (`src/khatmsaz/modules/broadcast/delivery.py`)
- تابع `deliver_broadcast(session, item)` پیاده‌سازی شد که ارسال پیام را برای انواع کانال‌ها (تلگرام، بله، پیامک) مدیریت کرده و وضعیت پیام را به `SENT` تغییر می‌دهد.
- هم در پنل وب (`app.py:decide_broadcast`) و هم در بات ادمین (`admin_bot:approve_broadcast_callback`) از این متد متمرکز استفاده می‌شود.

---

## ۳. تست‌ها و راستی‌آزمایی (Verification)

مجموعه تست کامل در `tests/test_master_31_broadcast_entitlement_and_moderation.py` پیاده‌سازی شد:
1. `test_broadcast_submit_free_plan_funded`: تست ارسال پیام توسط کاربر پلن FREE با کسر وجه موفق.
2. `test_broadcast_submit_insufficient_funds_raises`: تست ممانعت در صورت ناکافی بودن موجودی کیف پول.
3. `test_notify_admins_broadcast_with_photo`: تست ارسال تصویر و کیبورد دو دکمه‌ای به ادمین.
4. `test_notify_admins_broadcast_text_only`: تست ارسال پیام متنی با کیبورد دو دکمه‌ای به ادمین.
5. `test_safe_edit_admin_message_photo_vs_text`: تست متدهای `edit_caption` و `edit_text` متناسب با نوع پیام.
6. `test_admin_broadcast_approve_callback`: تست اجرای تأیید، ارسال به مخاطبان و ویرایش پیام ادمین.
7. `test_admin_broadcast_reject_callback`: تست عودت وجه و ویرایش پیام ادمین.
8. `test_broadcast_media_preview_unauthenticated`: تست رد دسترسی کاربر غیرمجاز در مسیر رسانه.
9. `test_broadcast_media_preview_cached_file`: تست تحویل تصویر از کش دیسک با هدر `image/jpeg`.
10. `test_templates_broadcast_media_and_copy`: تست صحت رندر تگ `<img>` در تمپلیت و حذف محدودیت‌های متنی.

**نتیجه اجرای تست‌ها:**
```bash
python -m pytest tests/test_master_31_broadcast_entitlement_and_moderation.py -v
# 10 passed in 7.01s (100% PASS)

python -m pytest tests/test_master_26_menu_and_button_repairs.py tests/test_master_27_creator_member_removal.py tests/test_master_28_adversarial_button_audit.py tests/test_master_29_broadcast_package_size.py tests/test_master_30_khatm_detail_debt_and_disable_laan.py tests/test_master_31_broadcast_entitlement_and_moderation.py -q
# 46 passed in 8.01s (100% PASS)
```
