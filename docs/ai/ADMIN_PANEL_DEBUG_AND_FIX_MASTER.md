# 🛠️ مستر جامع دیباگ، بازبینی خط‌به‌خط و پایدارسازی پنل مدیریت (Admin Panel Debug & Fix Master)
**(Admin Panel Line-by-Line Debugging, Missing Imports, Attribute Errors & Stability Master)**

> **📅 تاریخ تدوین:** ۲۰۲۶-۱۰-۱۱ (۲۰ مهر ۱۴۰۵) · **عامل:** Antigravity  
> **وضعیت:** تحلیل، پیاده‌سازی و اعتبارسنجی جامع خط‌به‌خط تکمیل شد (کلیه ۳۸۲ تست سبز)  
> **مرجع خطا:** لاگ خطای سرور واقعی (`AttributeError: module 'khatmsaz.modules.invitation.service' has no attribute 'list_for_khatm'`) و سقوط روت‌های پنل وب

---

## ۱. هشدار حیاتی و پروتکل اشتراکی هوش مصنوعی

> [!CAUTION]
> **قانون قطعی و بدون استثنا برای کلیه هوش‌های مصنوعی (Antigravity، Codex، Claude Code):**  
> بات روی VPS زنده در حال اجرا است و کاربران واقعی در حال ثبت‌نام و برگزاری ختم هستند.  
> هیچ هوش مصنوعی حق حذف قابلیت، ابداع قوانین کسب‌وکار، یا رها کردن کدهای بدون تست را ندارد.  
> هر تغییر در کد باید با تست معنادار همراه باشد و وضعیت در جدول این سند به‌روزرسانی شود.

این سند پیرو درخواست مستقیم مالک پروژه مبنی بر بررسی خط‌به‌خط و بازسازی ایمن پنل مدیریت تدوین شده است:
> *«بابا پنل ادمین چرا اینقدر باگ داره برو فایل مستر بساز دیباگ بکن خط به خط بخون برام درستش بکن. برو فایلای مستر قبلی رو همشو بخون یاد بگیر چشکلی کار میکرده دقیقا با همون رفتار برام فایل مستر رو بساز و خط به خط برام دیباگ بکن»*

---

## ۲. ریشه‌یابی و ورودی اصلی خطا

### ۲.۱. لاگ ارسالی از سرور تولید (VPS):
```text
Oct 11 08:42:12 user68-zaminhost-0Gsa python[2144216]: ERROR: Exception in ASGI application
Oct 11 08:42:12 user68-zaminhost-0Gsa python[2144216]: File ".../fastapi/routing.py", line 352, in run_endpoint_function
Oct 11 08:42:12 user68-zaminhost-0Gsa python[2144216]:   return await dependant.call(**values)
Oct 11 08:42:12 user68-zaminhost-0Gsa python[2144216]: File "/root/khatmsaz/src/khatmsaz/web/app.py", line 2105, in khatm_detail
Oct 11 08:42:12 user68-zaminhost-0Gsa python[2144216]:   invs = await invitation_service.list_for_khatm(session, khatm.id)
Oct 11 08:42:12 user68-zaminhost-0Gsa python[2144216]: AttributeError: module 'khatmsaz.modules.invitation.service' has no attribute 'list_for_khatm'
```

### ۲.۲. تحلیل علت وقوع:
در کامیت‌های بازطراحی پنل مدیریت (`d9e88b4` و موارد متعاقب آن)، تغییرات گسترده‌ای در `src/khatmsaz/web/app.py` اعمال شده بود (افزودن بیش از ۱۷۰۰ خط و ده‌ها روت جدید)، اما:
1. بسیاری از ایمپورت‌های ماژول‌ها و مدل‌ها (مانند `WaitingList`, `UserPlan`, `Wallet`, `PhoneClaim`, `Workbook`, `InvoiceKind`, `QuranPageAsset`, `advertising_service`, `khatm_request_service`, `CreatorRequest`) در بالای فایل اضافه نشده بودند.
2. توابعی روی سرویس‌ها فرض شده بودند که وجود نداشتند یا نامشان متفاوت بود (`invitation_service.list_for_khatm`, `invite_links.build_web_invite_url`, `plan_service.assign_plan`, `system_settings_service.list_all`).
3. برخی توابع سرویس‌ها با آرگومان‌های اشتباه یا ناکافی صدا زده شده بودند (`workflow_service.leave_khatm`, `wallet_service.purchase`).

---

## ۳. فهرست کالبدشکافی خط‌به‌خط باگ‌های شناسایی‌شده در پنل ادمین

| شناسه | شماره خط در app.py | روت / بخش | شدت | عنوان باگ و خطای زمان اجرا | وضعیت |
|:---:|:---:|:---|:---:|:---|:---:|
| **BUG-W01** | `L2105`, `L1741` | `GET /khatms/{id}`, `POST /moderation/laan/...` | 🔴 CRITICAL | عدم وجود `invitation_service.list_for_khatm` و دسترسی به `.token` روی شیء | ✅ RESOLVED |
| **BUG-W02** | `L2106`, `L1760` | `GET /khatms/{id}`, `POST /moderation/laan/...` | 🔴 CRITICAL | عدم وجود تابع `invite_links.build_web_invite_url` در ربات | ✅ RESOLVED |
| **BUG-W03** | `L2098-L2101` | `GET /khatms/{id}` | 🔴 CRITICAL | خطای `NameError: WaitingList` در کوئری لیست انتظار جزئیات ختم | ✅ RESOLVED |
| **BUG-W04** | `L431` | `GET /operations` | 🟠 HIGH | عدم وجود `system_settings_service.list_all` و قرمز شدن اشتباهی پایگاه‌داده | ✅ RESOLVED |
| **BUG-W05** | `L2471` | `POST /users/{id}/plan` | 🔴 CRITICAL | عدم وجود `plan_service.assign_plan` (نام صحیح: `set_plan`) | ✅ RESOLVED |
| **BUG-W06** | `L2286` | `POST /khatms/{id}/members/{pid}/remove` | 🔴 CRITICAL | ارسال آرگومان اشتباه به `workflow_service.leave_khatm` (`user_id` به جای `participation_id`) | ✅ RESOLVED |
| **BUG-W07** | `L2752` | `POST /broadcasts/{id}/decide` | 🔴 CRITICAL | عدم ارسال آرگومان اجباری `invoice_kind` در `wallet_service.purchase` | ✅ RESOLVED |
| **BUG-W08** | `L2214` | `POST /khatms/{id}/status` | 🔴 CRITICAL | خطای `NameError: InvoiceKind` در استرداد هزینه ساخت ختم لغوشده | ✅ RESOLVED |
| **BUG-W09** | `L2251-L2256` | `POST /khatms/{id}/members/{pid}/complete-share` | 🔴 CRITICAL | فراخوانی توابع ناموجود `list_open_for_participation` و `complete_my_portions` | ✅ RESOLVED |
| **BUG-W10** | `L1491`, `L2314` | `GET /khatms/{id}/export.xlsx`, `GET /creator/...` | 🔴 CRITICAL | خطای `NameError: Workbook` و `get_column_letter` در خروجی اکسل اعضا | ✅ RESOLVED |
| **BUG-W11** | `L2403-L2418` | `GET /users` | 🔴 CRITICAL | خطای `NameError: PhoneClaim`, `UserPlan`, `Wallet` در تب کاربران | ✅ RESOLVED |
| **BUG-W12** | `L3618` | `GET /quran` | 🔴 CRITICAL | خطای `NameError: QuranPageAsset` در صفحه بانک مصحف شریف | ✅ RESOLVED |
| **BUG-W13** | `L3814`, `L3937` | `GET /finance`, `POST /finance/ad-rate` | 🔴 CRITICAL | خطای `NameError: advertising_service` در مرکز مالی و نرخ پاداش | ✅ RESOLVED |
| **BUG-W14** | `L1641`, `L1842` | `GET /moderation`, `POST /moderation/...` | 🔴 CRITICAL | خطای `NameError: khatm_request_service` در مرکز نظارت | ✅ RESOLVED |
| **BUG-W15** | `L1575-L1576` | `GET /` | 🔴 CRITICAL | خطای `NameError: CreatorRequest`, `CreatorRequestStatus` در داشبورد | ✅ RESOLVED |
| **BUG-W16** | `L1892` | `GET /khatms` | 🔴 CRITICAL | خطای `NameError: KhatmCategory` در صفحه لیست ختم‌ها | ✅ RESOLVED |
| **BUG-W17** | `L2701` | `_dispatch_broadcast_delivery` | 🔴 CRITICAL | خطای `NameError: send_media` در ارسال چندرسانه‌ای پیام گروهی | ✅ RESOLVED |
| **BUG-W18** | `L3113-L3120` | `POST /users/{id}/moderate` | 🔴 CRITICAL | خطای `NameError: main_menu_keyboard`, `asyncio`, `send_with_keyboard` در ارتقا/تنزیل نقش | ✅ RESOLVED |
| **BUG-W19** | `L3528`, `L3679` | `save_devotional_media`, `save_quran_asset` | 🟡 MEDIUM | استفاده نامنظم از `import re` درون بلاک‌ها به جای بالای ماژول | ✅ RESOLVED |
| **BUG-W20** | `L561` | `payping_callback` | 🟡 MEDIUM | تایپ‌هینت نامعتبر `Any` بدون ایمپورت از `typing` | ✅ RESOLVED |

---

## ۴. بسته‌های کاری و مراحل اجرا (Work Packages Ledger)

| بسته | وضعیت | شرح اقدامات و آزمون اعتبارسنجی |
|:---:|:---:|:---|
| **WP-01** | ✅ VERIFIED | **اصلاح ایمپورت‌های سراسری `src/khatmsaz/web/app.py`:** اضافه کردن تمام مدل‌ها، سرویس‌ها، توابع کمکی و کتابخانه‌های غایب (`openpyxl`, `re`, `Any`, `WaitingList`, `Wallet`, `UserPlan`, `PhoneClaim`, `CreatorRequest`, `QuranPageAsset`, `InvoiceKind`, `khatm_request_service`, `advertising_service`, `main_menu_keyboard`, `send_media`, `send_with_keyboard`). |
| **WP-02** | ✅ VERIFIED | **تکمیل و تثبیت ماژول دعوت (`invitation`):** افزودن `list_for_khatm` و `get_or_create_for_khatm` به سرویس و ریپازیتوری، ایجاد پراپرتی امن `.token` روی مدل `KhatmInvitation` و افزودن `build_web_invite_url` در `bot/invite_links.py`. |
| **WP-03** | ✅ VERIFIED | **اصلاح فراخوانی‌های سرویس‌ها:** هماهنگی `system_settings_service.list_current`, `plan_service.set_plan`, `workflow_service.leave_khatm(session, part.id)`, و `wallet_service.purchase(..., invoice_kind=InvoiceKind.PURCHASE)`. |
| **WP-04** | ✅ VERIFIED | **تثبیت اکشن ثبت سهم و تکمیل اعضا:** استفاده از متدهای استاندارد `occ_service.list_outstanding` و `complete` به همراه `allocation_service.complete_current_portion_and_advance`. |
| **WP-05** | ✅ VERIFIED | **تست‌های اختصاصی برای کلیه روت‌های وب پنل ادمین:** ایجاد `tests/test_admin_panel_all_routes.py` (۱۰ تست اختصاصی موفق) و اطمینان از عدم پرتاب خطای ۵۰۰ یا `NameError`/`AttributeError` در تمام روت‌های پنل. |
| **WP-06** | ✅ VERIFIED | **اعتبارسنجی کامل با pytest و مستندسازی:** اجرای کل سوئیت تست‌های پروژه (۳۸۲ تست موفق، بدون هیچ خطایی) و ثبت گزارش نهایی در `PROJECT_STATE.md` و `CHANGELOG.md`. |

---

## ۵. دستورات اعتبارسنجی

```bash
# تست اسکن استاتیک نام‌ها و صفات
python .scratch/deep_scan_app.py

# اجرای آزمون‌های وب پنل ادمین
python -m pytest tests/test_admin_panel_all_routes.py -v

# اجرای تست‌های کامل غیراینتگریشن
python -m pytest -q
```
