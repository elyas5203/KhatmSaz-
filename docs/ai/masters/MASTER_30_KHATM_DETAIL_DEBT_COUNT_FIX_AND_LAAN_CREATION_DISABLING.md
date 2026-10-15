# MASTER-30: رفع خطای UndefinedError بدهی در جزییات ختم و غیرفعال‌سازی سراسری ساخت ختم لعن

> **وضعیت سند:** تصویب‌شده و اعمال‌شده بر روی سورس‌کد و سرور لایو  
> **شناسه تصمیم:** `DEC-PY-0030`  
> **مخاطب:** تیم توسعه، ادمین سیستم، ایجنت‌های بعدی  
> **تاریخ:** ۱۵ اکتبر ۲۰۲۶ (۲۳ مهر ۱۴۰۵)

---

## ۱. چرایی و زمینه تغییر (Context & Rationale)

به درخواست مستقیم کارفرما و گزارش لاگ‌های خطای زنده سرور:
1. **رفع خطای رندر جزئیات ختم در پنل وب:**
   در مسیر `/khatms/{khatm_id}` لاگ زیر ثبت شده بود:
   ```
   File "/root/khatmsaz/src/khatmsaz/web/templates/khatm_detail.html", line 282, in block 'content'
     {% if row.debt_count > 0 %}
   jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'debt_count'
   ```
   دلیل: تابع `_load_creator_member_rows` در فایل `app.py` اقلام سطر اعضا را بدون فیلدهای `debt_count`، `read_count`، `is_debtor` و `account` برمی‌گرداند و قالب `khatm_detail.html` نیز به صورت غیر دیفندد به این فیلدها ارجاع داده بود.
2. **غیرفعال‌سازی کامل ساخت ختم لعن:**
   دستور صریح کاربر:
   > «کلا ساخت ختم لعن رو فعلا وردار و غیر فعالش بکن برام. اشتباهه کسی نتونه انتخاب بکنه و بسازه»
   لذا هرگونه امکان ساخت ختم از نوع یا دسته «لعن» در تمامی بسترها (بات تلگرام، بات بله، پنل وب سازندگان و پنل وب ادمین) باید کاملاً مسدود و غیرقابل انتخاب شود.

---

## ۲. مشخصات و اصلاحات فنی اعمال‌شده

### الف) اصلاح خطای جزئیات ختم و غنی‌سازی سطرهای اعضا
1. **سرویس وب (`src/khatmsaz/web/app.py`):**
   - به تابع `_load_creator_member_rows` پرس‌وجوی `debt_by_participation` (تعداد سهم‌های با وضعیت `ASSIGNED`) اضافه شد.
   - شناسه و اطلاعات پلتفرم کاربران از مدل `PlatformIdentity` واکشی شد (`account = identities_by_user.get(user.id)`).
   - دیکشنری خروجی هر سطر اکنون شامل فیلدهای زیر است:
     - `read_count`: تعداد سهم‌های خوانده‌شده (`completed_val`).
     - `debt_count`: تعداد سهم‌های باز/بدهی (`debt_val`).
     - `is_debtor`: مقدار بولی (`debt_val > 0`).
     - `account`: آبجکت هویت پلتفرم کاربر (`PlatformIdentity`).
2. **قالب وب (`src/khatmsaz/web/templates/khatm_detail.html`):**
   - دسترسی به فیلدهای دیکشنری با متد امن `.get(...)` مقاوم‌سازی شد:
     - `row.get('read_count', row.get('completed', 0))`
     - `row.get('debt_count', 0)`
     - `{% if row.get('debt_count', 0) > 0 %}`
     - `{% if row.get('account') %}`

### ب) غیرفعال‌سازی کامل و سراسری ساخت ختم لعن
1. **کیبورد انتخاب قالب بات (`src/khatmsaz/bot/keyboards.py`):**
   - گزینه `[🗡 ختم لعن]` (`ck:group:LAAN`) از `template_choice_keyboard` به طور کامل حذف شد.
2. **هندلرهای بات سازنده (`src/khatmsaz/bot/handlers/create_khatm.py`):**
   - در هندلرهای `choose_category_group` و `_show_category_group`، بررسی اضافه شد که در صورت ارسال کال‌بک مربوط به لعن، پیام آلرت «امکان ساخت ختم لعن در حال حاضر غیرفعال است.» نمایش داده شود.
   - هندلرهای دریافت عنوان و متن لعن (`entering_laan_title` و `entering_laan_text`) ایالت FSM را فوراً پاک کرده و اعلام می‌کنند که ساخت ختم لعن غیرفعال است.
   - در متد نهایی `_finish_creating_khatm`، در صورت وجود `category_group == LAAN`، ایجاد لغو شده و پیام خطا برگردانده می‌شود.
3. **فرم ایجاد ختم در پنل سازنده (`src/khatmsaz/web/templates/creator_khatm_new.html`):**
   - گزینه رادیویی لعن (`('laan','✨','لعن')`) از لیست قالب‌ها و ستون‌های گرید حذف شد.
   - گروه انتخابی `<optgroup label="لعن" id="laan-options">` از منوی آبشاری حذف شد.
   - توابع جاوااسکریپت همگام‌سازی (`sync()`) پالایش شدند.
   - متد POST `/creator/khatms/create` در صورت دریافت `content_kind == "laan"` خطای HTTP 400 برمی‌گرداند.
4. **فرم ایجاد ختم در پنل ادمین (`src/khatmsaz/web/templates/khatms.html`):**
   - گزینه `<option value="laan">🔥 ختم لعن</option>` از انتخاب‌گر خانواده ختم حذف شد.
   - متد POST `/khatms/create` در صورت دریافت `content_kind == "laan"` خطای HTTP 400 برمی‌گرداند.

---

## ۳. تضمین سازگاری و ختم‌های گذشته
- ختم‌های لعن که در گذشته ساخته شده و در دیتابیس وجود دارند برای قرائت و گزارش‌گیری بدون مشکل باقی می‌مانند.
- فقط مسیرهای «ثبت و ساخت جدید» در تمام سطوح مسدود شده‌اند.

---

## ۴. نتایج آزمون‌ها و اعتبارسنجی
- تست‌های اختصاصی `tests/test_master_30_khatm_detail_debt_and_disable_laan.py`: ۵ از ۵ پاس شد (۱۰۰٪).
- تست‌های رگرسیون پنل سازندگان و آدیت دکمه‌ها: ۲۴ از ۲۴ پاس شد (۱۰۰٪).
