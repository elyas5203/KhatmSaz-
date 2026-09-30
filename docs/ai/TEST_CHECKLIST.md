# TEST_CHECKLIST — چک‌لیست تستِ جامع (OWNER_SPEC_MASTER §M)

> این فایل نتیجهٔ فاز تستِ خودکار + سناریوهای دستی است. علامت‌ها: ✅ پاس ·
> ❌ خطا (باید دیباگ) · ⏳ فقط دستی (در `MANUAL_TEST_NOTES.md`).
> تاریخ اجرا: ۲۰۲۶-۱۰-۰۱ [Claude Code].

## بخش ۱ — تستِ خودکار (اجرا شد)
- ✅ `python -m pytest -m "not integration"` → **۲۳۶ پاس، ۸۶ deselect**.
- ✅ i18n audit (جزو pytest): همهٔ کلیدهای استفاده‌شده در هر سه زبان موجودند.
- ✅ کامپایلِ Jinja همهٔ ۲۹ تمپلیت وب → بدون خطای نحوی.
- ✅ ممیزی روت‌ها: همهٔ لینک‌های ناوبریِ پنل ادمین و کریتور روتِ متناظر دارند
  (`/`, `/khatms`, `/users`, `/phone-verifications`, `/broadcasts`, `/servant-ad`,
  `/finance`, `/categories`, `/devotionals`, `/templates`, `/bots`, `/operations`,
  `/audit`, `/admins`, `/creator`, `/creator/khatms`, `/creator/wallet`,
  `/creator/khatms/new`).
- ✅ import smoke: `khatmsaz.web.app` و همهٔ هندلرهای بات import می‌شوند.
- ✅ رندرِ تمپلیت‌های کلیدی با دادهٔ ساختگی: `finance.html`, `creator_wallet.html`,
  `creator_dashboard/khatms.html`, `creator_requests.html`, `servant_ad.html`,
  `devotionals.html` → بدون کلید i18n جاافتاده.

## بخش ۲ — تستِ واحدِ رفتارهای بحرانی (pytest، پاس)
- ✅ زمان‌بندی: `_is_reminder_due` «در/بعد از ساعت، یک‌بار در روز»
  (`test_member_bot_fixes.py`).
- ✅ عدم ارسال دوباره سهم بعدی قرآن (`deliver_due_next_portions` → record DAILY_REMINDER).
- ✅ L4 هفتگیِ چندروزه: `is_regular_due(weekdays=…)` روی روزِ درست فایر می‌کند
  (تست inline تأییدشده؛ نگاشت فارسی 0=شنبه → py).
- ✅ پلن‌ها: tier ذخیره‌شده، ارتقای FREE→BASIC، `ads_enabled_for_creator` فقط BASIC
  (`test_pro_plan_purchase.py`).
- ✅ تیکتینگ: مسیر پاسخِ سازنده→مخاطب از بات ممبرِ درست (`test_panel_redesign`/سایر).
- ✅ کیبورد فرکانس تعهد بدون «ماهانه»؛ head مایگریشن = `schedweekdays2026100101`.

## بخش ۳ — سناریوهای دستی (نیازِ بات زنده — در MANUAL_TEST_NOTES.md)
موارد ⏳ که فقط با تلگرام/بله واقعی قابل‌تست‌اند (جوین، ارسال سهم سرِ ساعت، تیکت
دوطرفه، پیام گروهیِ مدیا، تبلیغ خدمتگزاران، شارژ کیف پول/پرداخت) در فایل جدا
`docs/ai/MANUAL_TEST_NOTES.md` دانه‌دانه فهرست شده‌اند.

## پیش‌نیازِ استقرار (مهم)
- ⚠️ روی سرور قبل از ری‌استارت: `alembic upgrade head` (به‌خاطر ستون جدیدِ
  `khatm_participations.schedule_weekdays` — مهاجرت `schedweekdays2026100101`).
  اگر این اجرا نشود، بات با خطای ستونِ ناموجود بالا نمی‌آید.

## نتیجهٔ فعلی
همهٔ تست‌های خودکار سبز. باگِ بازِ خودکار وجود ندارد. تست‌های دستی منتظرِ اجرای
مالک روی بات زنده‌اند (فایل جدا).
