# MASTER-21 — Admin Panel User Analytics & Devotional Breakdown (قرآن، لعن، صلوات، دعا، خطبه)

**Author:** Antigravity  
**Date:** 2026-10-14  
**Status:** IMPLEMENTED  
**Owner Mandate:**
> "یک مورد دیگ میخوام تو پنل ادمین میخوام مجموع تمام یوزر هایی ک هست تو تمام بات ها هم ببینم بعد به تفکیک هم ببینم اینطوری باشه بعد به تفکیک یوزر های قران و لعن و صلوات و دعا و خطبه هم باشه ک ببینم استقبال از کدوم بیشتره"

---

## ۱. اهداف و نیازمندی‌ها (Requirements)

۱. **مجموع کل کاربران سامانه (Total System Users):**
   - نمایش تجمیعی تعداد کل کاربران ثبت‌شده در سیستم در سراسر ربات‌ها و پلتفرم‌ها (`users` table).
   - نمایش تعداد کاربران فعال (Active Users).
   - تفکیک نقش‌ها: کاربران عادی، سازندگان ختم (Creators)، و مدیران ارشد (Super Admins).

۲. **تفکیک بر اساس پلتفرم و ربات‌ها (Platform & Bot Breakdown):**
   - تعداد کاربران پلتفرم تلگرام (`Platform.TELEGRAM`).
   - تعداد کاربران پلتفرم بله (`Platform.BALE`).
   - تعداد کاربران چندپلتفرمی (Dual-platform: کاربرانی که هم در تلگرام و هم در بله شناسه متصل دارند).
   - وضعیت و تعداد ربات‌های فعال در هر پلتفرم (ربات سازنده، ربات‌های اعضا، ربات ادمین مرکزی).

۳. **تفکیک بر اساس ۵ دستهٔ عبادی برای تحلیل استقبال مخاطبان (Devotional Reception Breakdown):**
   - طبق خواست صریح کارفرما: تفکیک کاربران ۵ دستهٔ اصلی ختم:
     ۱. **قرآن کریم (Quran):** صفحات، سوره‌ها و ختم قرآن (`QURAN_PAGE`, `QURAN_SURAH`, `SURAH`).
     ۲. **لعن (La'an):** ختم‌های لعن عمومی و سفارشی (`group == 'LAAN'` یا `pending_lan_approval IS TRUE`).
     ۳. **صلوات (Salawat):** صلوات عام و خاص (`group == 'SALAWAT'` یا صلوات بدون دسته).
     ۴. **دعا و زیارت (Dua & Ziyarat):** ادعیه و زیارات مأثوره (`group == 'DUA'`, `DUA`, `ZIYARAT`).
     ۵. **خطبه (Khutbah):** خطبه‌های شریف فدکیه، غدیر، متقین و... (`group == 'KHUTBAH'`).
   - برای هر دسته، محاسبه و نمایش:
     - تعداد کاربران علاقه‌مند و درگیر (Engaged Users: مجموع شرکت‌کنندگان و سازندگان ختم آن دسته).
     - تعداد قاریان/خوانندگان فعال جاری (Active Readers).
     - تعداد کل ختم‌های ایجادشده در این دسته (Total Khatms).
     - تعداد ختم‌های در حال برگزاری (Active Khatms).
     - مجموع سهم‌ها و مشارکت‌های قرائت‌شده (Total Participations).
     - درصد استقبال و سهم بازار از کل مخاطبان (Popularity Share Percentage).
     - رتبه‌بندی خودکار از ۱ تا ۵ به همراه نشان ویژهٔ **«بیشترین استقبال 🏆»** برای دستهٔ اول.

۴. **نقاط نمایش در سیستم (Display Surfaces):**
   - **داشبورد مدیریت کل (`/` - `dashboard.html`):** سکشن تحلیلی مدرن شامل نمودار پیشرفت، رتبه‌بندی استقبال و کارت‌های تفکیک پلتفرم.
   - **صفحه مدیریت کاربران ۳۶۰ درجه (`/users` - `users.html`):** نوار خلاصهٔ تحلیلی بالای فرم جستجو.
   - **ربات ادمین مرکزی (`@khatmsaz_admin_bot`):** گزارش تحلیلی در دستور `/status` و دکمهٔ اختصاصی «📊 آمار و تفکیک کاربران».

---

## ۲. طراحی مدل داده و کوئری‌ها (Data Queries Design)

سرویس تحلیلی `get_system_user_analytics(session)` در `src/khatmsaz/modules/reporting/service.py`:

```python
category_case = case(
    (
        Khatm.template_type.in_((
            KhatmTemplateType.QURAN_PAGE,
            KhatmTemplateType.QURAN_SURAH,
            KhatmTemplateType.SURAH,
        )),
        "QURAN",
    ),
    (
        (KhatmCategory.group == KhatmCategoryGroup.LAAN) | (Khatm.pending_lan_approval.is_(True)),
        "LAAN",
    ),
    (
        KhatmCategory.group == KhatmCategoryGroup.KHUTBAH,
        "KHUTBAH",
    ),
    (
        (KhatmCategory.group == KhatmCategoryGroup.DUA) | Khatm.template_type.in_((KhatmTemplateType.DUA, KhatmTemplateType.ZIYARAT)),
        "DUA",
    ),
    else_="SALAWAT",
)
```

کوئری‌ها به صورت استاندارد، سازگار با هر دو محیط SQLite (تست‌های محلی) و PostgreSQL (سرور پروداکشن) پیاده‌سازی شدند.

---

## ۳. تغییرات فایل‌ها (Files Changed)

۱. `src/khatmsaz/modules/reporting/service.py`:
   - افزودن متادیتای ۵ دستهٔ عبادی (`DEVOTIONAL_METADATA`).
   - افزودن تابع `get_system_user_analytics(session: AsyncSession) -> dict[str, Any]`.
۲. `src/khatmsaz/web/app.py`:
   - بارگذاری و پاس دادن `user_analytics` در اندپوینت‌های `dashboard` (`/`) و `users` (`/users`).
۳. `src/khatmsaz/web/templates/dashboard.html`:
   - غنی‌سازی کارت «کل کاربران» با نشانگر تلگرام و بله.
   - افزودن پنل تحلیلی مجلل `📊 گزارش تحلیلی استقبال و تفکیک کاربران سامانه`:
     - رتبه‌بندی ۵ دستهٔ عبادی همراه با نوار درصد و بج رتبه.
     - باکس تفکیک کاربران تلگرام، بله و کاربران چندپلتفرمی.
۴. `src/khatmsaz/web/templates/users.html`:
   - افزودن نوار ۵ کارته بالای جستجوی کاربران جهت نمایش خلاصهٔ تفکیک پلتفرمی و دسته‌ها.
۵. `src/khatmsaz/bot/handlers/admin_bot/handlers.py`:
   - افزودن آمار دسته‌ها و پلتفرم‌ها در دستور `/status` و callback `admin:status`.
   - افزودن دکمهٔ «📊 آمار و تفکیک کاربران» (`admin:user_analytics`) و هندلر اختصاصی.
۶. `tests/test_master_20_user_analytics.py`:
   - تست کامل کوئری‌های تحلیلی، رتبه‌بندی، دسته‌بندی ۵ گانه و رندر وب‌پیج‌ها.
