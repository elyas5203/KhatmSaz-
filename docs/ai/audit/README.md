# پرونده‌های اجرای ممیزی

**دستور مالک: اکنون فقط تحلیل، اجرای تست‌های موجود روی محیط آزمایشی آماده و ثبت گزارش. هیچ کد یا تستی تغییر نکند؛ رفع باگ فقط پس از دستور بعدی مالک.**

مرجع دستور کار: [FULL_SYSTEM_AUDIT_MASTER.md](../FULL_SYSTEM_AUDIT_MASTER.md).

- `FILES.csv`، `ITEMS.csv`، `EDGES.csv` و `SNAPSHOT.json` خروجی تولیدی `scripts/build_audit_inventory.py` هستند. ستون status در ITEMS فقط وضعیت اولیهٔ NOT_RUN است؛ نتیجه را آنجا تغییر ندهید.
- `MODULES.md` نقشهٔ بسته‌ها و مسیرهاست؛ تست‌های «نامزد» با نام فایل پیدا شده‌اند و اثبات پوشش نیستند. برای هر تابع تست واقعی و assertion را دستی نگاشت کنید.
- `WORK_PACKAGES.csv` وضعیت جاری بسته‌هاست؛ پیش از شروع owner/status/started_at/head را ثبت کنید؛ در پایان next_step را مشخص کنید.
- `RUNS.csv` تاریخچهٔ append-only نتایج است. برای بازآزمایی سطر جدید بنویسید؛ PASS قدیمی را حذف نکنید. مقدار item_id باید ID موجود در ITEMS یا case معتبر مانند R01 باشد. برای چند item، برای هرکدام سطر بنویسید یا فایل نگاشت صریح در evidence بسازید.
- `BUGS.md` الگوی باگ و سرنخ‌های پیشین را دارد. هر باگ شناسهٔ `BUG-YYYYMMDD-NNN` بگیرد.
- `evidence/` فقط خروجی پاک‌سازی‌شده، seed مصنوعی، test node، انتظار/مشاهده و نگاشت itemهاست. فایل خالی یا جملهٔ «تست شد» مدرک نیست. تصویر چت واقعی شامل مشخصات اشخاص را ثبت نکنید.

نمونهٔ فرم سطر (این نمونه نتیجهٔ اجرا نیست):

```text
run_id: RUN-YYYYMMDD-001
package_id: A05
item_id: <ID تابع از ITEMS.csv یا R08>
agent: Codex
started_at: <ISO-8601 با offset>
head: <git rev-parse HEAD>
source_hash: <FILES.sha256 برای فایل تحت بررسی>
environment: isolated-postgres + mocked Telegram/Bale
command: python -m pytest tests/<file>.py::<test> -q
expected: بعد از دو اسکن، یک محتوا و یک action؛ یک ثبت DB
observed: <مشاهدهٔ واقعی و تعدادها>
status: PASS / FAIL / BLOCKED / NEEDS_DECISION / NOT_APPLICABLE
evidence: docs/ai/audit/evidence/RUN-YYYYMMDD-001.md
bug_id: <در صورت وجود>
```

هنگام تغییر کد، hash و HEAD قبلی را حفظ کنید. نتیجهٔ سابق فقط برای snapshot سابق معتبر است؛ توابع تغییرکرده و callers متأثر دوباره تست شوند. ID تابع از مسیر/نام ساخته می‌شود؛ با rename تغییر می‌کند. ID محل لینک شامل خط است؛ پس از جابه‌جایی خط، نگاشت old→new را در evidence ثبت کنید.

برای تکمیل پوشش، join کردن ITEMS با آخرین RUNS کافی نیست: نتیجه باید evidence معتبر، محیط مناسب و تطبیق snapshot داشته باشد. اقلام دینامیک جدید را در مدرک بسته با شناسهٔ `DYN-<package>-NNN` ثبت کنید و در RUNS به همان شناسه ارجاع دهید.
