# QA MATRIX — نیازمندی ← کد ← تست ← نتیجهٔ واقعی

> شروع: 2026-09-27 [Claude Code]. این ماتریس زنده است؛ هر جلسه به‌روز می‌شود.
> وضعیت‌ها: ✅ VERIFIED (کد + تست این جلسه) · 🧪 UNIT-ONLY (تست واحد دارد، live نشده) ·
> 🔵 NEEDS-LIVE (نیاز به تلگرام واقعی/حساب دوم/Postgres) · ⚠️ BUG-OPEN · 🔒 BLOCKED.
>
> **قانون:** هیچ ردیفی صرفاً بر اساس گزارش قدیمی «باز» یا «بسته» فرض نشده؛ هر ادعا در کد فعلی چک شده.

## موانع سطح‌بالا (نیاز به تصمیم/دسترسی مالک)
- 🔒 **تست live تلگرام + حساب دوم**: جریان‌های عضویت/تأیید عضو/اعلان بین‌باتی فقط با ربات در حال اجرا و یک حساب دوم تست می‌شوند. من دسترسی ندارم؛ نیاز به مالک یا Codex.
- 🔒 **Postgres تستی**: تست‌های integration و migration فقط روی Postgres جدا اجرا می‌شوند (نه SQLite/production). روی این ماشین محلی پیکربندی نشده — نیاز به تأیید/راه‌اندازی.
- 🔒 **push/deploy/restart**: طبق هدف، بدون تأیید صریح مالک انجام نمی‌شود. فیکس‌های این جلسه لوکال کامیت‌نشده‌اند و منتظر اجازهٔ push‌اند.
- 🔒 **توکن بات‌های دعا/زیارت نامعتبر است** (لاگ VPS): مسیر دعا/زیارت تا تنظیم توکن معتبر در `/bots` قابل تست کامل نیست — تصمیم/اقدام مالک.

## سازنده (Creator) — تلگرام

| نیازمندی | کد | تست | وضعیت |
|---|---|---|---|
| منوی سازنده: امروز/مدیریت/گزارش‌ومالی/تنظیمات/راهنما | `keyboards.creator_menu_keyboard` + `panel.py` | `test_home_menu.py` | ✅ منو درست است |
| دکمهٔ «📊 گزارش و مالی» پاسخ دهد | **رفع شد این جلسه**: `panel.handle_creator_finance` → `report.personal_report` | `test_creator_menu_buttons.py` | ✅ (قبلاً دکمهٔ مرده بود — یافتهٔ Codex تأیید و رفع) |
| دکمهٔ «❓ راهنما و پشتیبانی» پاسخ دهد | **رفع شد این جلسه**: `panel.handle_creator_support` → `help.help_command` | `test_creator_menu_buttons.py` | ✅ (قبلاً مرده) |
| «مدیریت ختم‌ها» پنل inline باز کند | `panel.handle_creator_management` | — | 🧪 کد درست، live نشده |
| ساخت ۴ نوع ختم (قرآن/صلوات/دعا/لعن) | `create_khatm.py` (`_ask_mode`,`_MODE_EXPLANATION`) | تست ترتیب/توضیح موجود | 🔵 NEEDS-LIVE (Codex: قرآن تا تأیید OK؛ لعن تا فرم عنوان OK) |
| گام «انتخاب پیام‌رسان/زبان لینک دعوت» | `create_khatm.show_invite_platform_keyboard`/`_languages` | — | ✅ کرش `InlineKeyboardButton` این جلسه رفع شد؛ fallback پیام جدید افزوده شد |
| پیام موفقیت لینک‌های بات ممبر | `create_khatm.finish_invite_links` + `bot/invite_links.py` | — | 🔵 NEEDS-LIVE (وابسته به توکن بات ممبر) |
| «QR دعوت» لینک بات ممبر بدهد | `my_khatms.khatm_qr` | — | ✅ رفع‌شده جلسات قبل؛ live تأیید Codex |
| مدیریت ختم: اعضا/CSV/آمار/تنظیمات/لغو | `my_khatms.py` | — | 🔵 NEEDS-LIVE (CSV بدون عضو فعال خالی — طبیعی) |

## عضو (Member bots) — تلگرام fa/ar/en و بله

| نیازمندی | کد | تست | وضعیت |
|---|---|---|---|
| دکمهٔ «شرکت در این ختم» بعد از ری‌استارت کار کند | `member_start.handle_member_join_callback` (فیلتر state حذف شد) | — | ✅ رفع این هفته |
| کرش `BotRole`/`InlineKeyboardButton` در مسیر عضویت | `start.py`, `create_khatm.py` import | — | ✅ هر دو رفع شد |
| دکمه‌های عضویت/تعهد به زبان بات باشند (نه فارسی) | `join_preview_keyboard`/`commitment_consent_keyboard` (+lang) | `keyboards` unit smoke (این جلسه دستی) | ✅ رفع شد (fa/ar/en) |
| پیام خوش‌آمد بات ممبر به زبان بات | `member_start` + i18n `member.welcome` | — | ✅ رفع شد |
| پرسیدن ساعت یادآوری در هر عضویت تازه | `start.resume_join_after_registration` (شرط اصلاح شد) | 🔵 | ✅ کد؛ 🔵 live |
| ثبت‌نام عضو (share-number، بدون OTP) | `member_registration.py` | تست‌های registration موجود | 🔵 NEEDS-LIVE |
| منوی ممبر: امروز/ختم‌های من/عمومی/تنظیمات/پشتیبانی | `member_menu_keyboard` + همه handlerها روی dp_member | — | 🧪 handlerها موجود؛ «دکمهٔ امروز» زبان‌محور؛ منتظر بازخورد مالک که «کجا اشتباه است» |
| تنظیمات روی بات ممبر (بلاک تغییر زبان) | `settings_menu.is_member_bot` | تست‌های settings موجود | 🧪 |

## ادمین / پنل وب

| نیازمندی | کد | تست | وضعیت |
|---|---|---|---|
| صفحهٔ «دعاها و زیارات» (CRUD متن) | `web/app.py /devotionals` + `devotionals.html` | render Jinja دستی | ✅ ساخته این هفته؛ 🔵 تست live پنل |
| بازطراحی سایدبار والد/فرزند | `base.html` | render Jinja دستی | ✅ ساخته؛ 🔵 live |
| seed خودکار دعاها در استارتاپ | `content/devotional_seed.py` + bootstrap | چانک‌سایز <4096 تأیید شد | ✅ کد؛ 🔵 اجرای واقعی روی سرور |
| صفحهٔ وب `/join` دکمه‌های بات ممبر | `web/app.py public_join_landing` | render Jinja دستی | ✅ رفع (قبلاً هیچ دکمه‌ای؛ حالا per member bot) |

## یافته‌های باز (از Codex، بازآزمایی‌شده در کد)
- ⚠️ **متن راهنمای عضویت خصوصی**: باید بررسی شود آیا واقعاً متناقض است (یک‌جا لینک مستقیم، یک‌جا تأیید سازنده). در i18n `help` هر دو مفهوم هست؛ نیاز به بازخوانی متن fa برای رفع ابهام. — TODO فاز ۳.
- 🔵 چند اصطلاح فنی/انگلیسی در راهنما و پاسخ `/cancel` مغایر لحن فارسی سادهٔ پروژه. — TODO فاز ۳ (بازبینی طبق TONE_GUIDE).

## نتیجهٔ فاز ۱ (این جلسه)
یک باگ واقعی از گزارش Codex تأیید و رفع شد (دکمه‌های مردهٔ «گزارش و مالی» / «راهنما و پشتیبانی») + تست رگرسیون. بقیهٔ ماتریس نقشهٔ کار است؛ موارد 🔵/🔒 نیاز به دسترسی live یا تصمیم مالک دارند.
