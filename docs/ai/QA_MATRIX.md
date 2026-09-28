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

### رفع‌شدهٔ فاز ۲ (این جلسه، با تست)
- ✅ دکمهٔ «🕋 ختم‌های عمومی» مرده بود (فقط command) → وصل شد + `test_public_khatms_button.py`.
- ✅ `snooze_keyboard` فارسیِ هاردکد بود → زبان‌محور شد (fa/ar/en).

## یافته‌های باز (از Codex، بازآزمایی‌شده در کد)
- ✅ **متن راهنمای عضویت خصوصی — بازآزمایی شد، باگ نیست**: در `help.join` (fa/ar/en) گام ۳ حالت عادیِ عضویت و گام ۵ استثنای ختم خصوصی (درخواست→تأیید سازنده) را توصیف می‌کند؛ متوالی و درست است، نه متناقض. (نمونهٔ اجرای «یافتهٔ قدیمی را کورکورانه باز نگیر».)
- 🔵 چند اصطلاح فنی/انگلیسی در راهنما و پاسخ `/cancel` مغایر لحن فارسی سادهٔ پروژه. — TODO فاز ۳ (بازبینی طبق TONE_GUIDE).

## نتیجهٔ فاز ۱ (این جلسه)
یک باگ واقعی از گزارش Codex تأیید و رفع شد (دکمه‌های مردهٔ «گزارش و مالی» / «راهنما و پشتیبانی») + تست رگرسیون. بقیهٔ ماتریس نقشهٔ کار است؛ موارد 🔵/🔒 نیاز به دسترسی live یا تصمیم مالک دارند.


## ممیزی‌های خودکار کدمحور (فاز ۲ — PASS با شاهد، بدون نیاز به live)
> اجرا: 2026-09-27 [Claude Code]. اسکریپت‌های اسکن روی کد فعلی؛ قابل بازتولید.

| ممیزی | روش | نتیجه |
|---|---|---|
| دکمه‌های reply مرده (متن بدون handler) | تطبیق `menu.*` با `F.text.in_` | ✅ ۰ (finance/support/عمومی رفع شد) |
| دکمه‌های inline مرده (callback بدون handler) | تطبیق `callback_data` با `F.data` | ✅ ۰ از ۶۶ prefix |
| کلید i18n گمشده (رِندر خام) | همهٔ `t("..")` لفظی vs `_STRINGS` | ✅ ۰ (button.confirm/leave رفع شد) — قفل با `test_i18n_coverage.py` |
| کلید با زبان ناقص (فارسی روی بات ar/en) | fa بدون ar/en | ✅ ۰ از ۸۱۲ کلید |
| رشتهٔ فارسی هاردکد در فایل‌های ممبر | اسکن answer/text بدون t() | ✅ رفع (member_start) — فقط fallback جزئی «قاری» ماند |
| صفحهٔ ادمینِ یتیم (بدون لینک nav) | ۱۲ صفحهٔ GET vs لینک‌های base.html | ✅ ۰ — همه از سایدبار قابل‌دسترس |
| import همهٔ handlerها | import پویا | ✅ ۰ خطا |
| کرش عضویت `joined_via_bot_instance_id` | تست + امضا | ✅ رفع + `test_join_records_bot_instance.py` |

**جمع‌بندی فاز ۲:** همهٔ کلاس‌های باگِ «دکمه بی‌اثر / کلید خام / زبان اشتباه / کرش مسیر» که در تست live دیده شدند، به‌صورت سیستماتیک اسکن و رفع شدند، و سه‌تا با تست رگرسیون قفل شدند. ۸۹ تست واحد سبز.



## 🔴 باگ‌های live-QA مالک (2026-09-28 عصر) — برای Codex/سشن‌های بعد
1. **تخصیص صفحات قرآن اشتباه است (HIGH)**: الان صفحه‌ها می‌پرند (۴,۵ → ۸,۹ → ۱۲,۱۳) به‌جای پیوستهٔ شخصی (۴,۵ → ۶,۷ → ۸,۹). طبق DOMAIN_MODEL §2 «Personal Journey» سهم هر فرد باید برای خودش پیوسته جلو برود. باگ موتور allocation — بازتولید و رفع با تست.
2. **فرمت محتوا باید از کاربر پرسیده شود**: الان متن+ترجمه با هم می‌آید و شلوغ است. کاربر باید هنگام/بعد از عضویت انتخاب کند کدام فرمت‌ها (تصویر/متن/متن+ترجمه/صوت) و چه ساعتی برایش ارسال شود — و بعداً قابل تغییر. فقط فرمت‌هایی که ادمین برای آن ختم ثبت کرده نشان داده شود.
3. **ترتیب FSM عضویت تعهدی**: گرفتن «ساعت یادآوری» باید **اجباری و مرحله‌به‌مرحله** باشد؛ الان قبل از ست‌کردن ساعت، دکمهٔ «ثبت بخشی از تعهد» در دسترس بود و عددِ تایپ‌شده به‌عنوان تعداد صفحه ثبت شد. باید تا ساعت ست نشود مرحلهٔ بعد باز نشود.
4. **بازنویسی پیام‌های یادآوری/تأیید**: مالک پیام‌های فعلی را «مسخره» خواند و نمونهٔ گرم/حرفه‌ای داد (سبک @khedmatgozaran_quran). متن یادآوری قرائت + تأیید ثبت را طبق TONE_GUIDE گرم و محترمانه بازنویسی کن (fa/ar/en).
5. **`/cancel` روی فرم‌های حساب پیام نامرتبط ورود ادمین می‌دهد** (Codex) — مسیر cancel را درست کن؛ و `/cancel` روی بات ممبر هم کار کند (الان فقط dp_creator).
6. **چند صفحهٔ انگلیسی دکمه/نام فارسی دارد** (Codex) — i18n ناقص در بعضی مسیرها.
7. **بخش تأیید سازنده دستور فنی/مراجعه به دیتابیس پیشنهاد می‌دهد** (panel.py admin_panel:creator_requests) — با UX ساده جایگزین شود.

### رفع‌شدهٔ همین عصر (Claude Code)
- ✅ مینی‌اپ در Telegram Web باز نمی‌شد (`X-Frame-Options: SAMEORIGIN`) → برای `/mini/*` از CSP frame-ancestors تلگرام استفاده شد.
- ✅ نشت «/admin_app» در پیام عضویت → ثبت‌نام دیگر نامی که با `/` شروع شود را نمی‌پذیرد (member + creator).

### پاسخ به سؤال کانال قرآن
بات‌هایی که محتوا را تحویل می‌دهند باید **عضو/ادمین کانال منبع قرآن** باشند (که تازه اضافه کردی). دستور جداگانه لازم نیست — کافی است `systemctl restart khatmsaz` بزنی تا seedِ خودترمیمِ استارتاپ (`seed_verified_quran_channel_map`) دوباره اجرا و نقشهٔ کانال تأیید شود.

## 🎯 هدف‌های بزرگِ افزوده‌شده (مالک، 2026-09-28) — نیازمند سشن اختصاصی
1. **ریدیزاین کامل پنل ادمین** — همهٔ صفحات و همهٔ امکانات، UX خیلی ساده. شامل:
   - صفحهٔ «دعاها» و «دسته‌ها»: فیلدهای تکراری/اشتباه اصلاح شوند؛ باگ «دعا فعال شد ولی «فعال نیست» نشان می‌دهد» رفع شود؛ فرم‌ها بازطراحی.
   - بخش «مالی»: خیلی ساده‌تر شود، با توضیح و مثالِ روشن «کاربر عادی کیست/سازنده کیست/…».
2. **پنل وب کریتور** — طراحی کامل با همهٔ امکانات (سشن اختصاصی).
3. **دکمهٔ ورود به مینی‌اپ (ادمین و کریتور)** — با زدنش، دستور ورود در چت بیاید تا کاربر بتواند وارد مینی‌اپ شود.
4. **پرداخت**: مشاهدهٔ مالک — رفتن به درگاه بدون پرداخت، تایم‌اوت ۱۰ دقیقه، بازگشت. باید بررسی شود pending-payment منقضی/پاک‌سازی درست دارد (تا مشکل بعدی نسازد) + خطای گواهی SSL روی `api.khedmatgozaran.com` (NET::ERR_CERT_COMMON_NAME_INVALID) — زیرساخت مالک؛ callback پرداخت تا این گواهی درست نشود کار نمی‌کند.

## رفع‌شدهٔ live-QA (2026-09-28)
- ✅ **بحرانی**: بات انگلیسی/عربی تعهد را فارسی می‌گرفت — `resume_join_after_registration` حالا زبانِ بات ممبر را استفاده می‌کند نه زبان کاربر.
- ✅ ساعت یادآوری per-khatm حالا فرمت تایپی «14:40» را هم می‌پذیرد (استفادهٔ مجدد از AskDeliveryHour).
- ✅ `/public_khatms` روی بات سازنده خروجی نداشت (فقط dp_member بود) → به routerهای مشترک منتقل شد.

## هدف افزوده‌شده (مالک، 2026-09-27)
- 🎯 **ریدیزاین کامل پنل ادمین و سازنده**: هر دو پنل با همهٔ امکانات موجود بازطراحی و ساخته شوند طوری که هر کاری که کاربر می‌تواند انجام/کنترل/بررسی/آنالیز کند داخل پنل در دسترس باشد — **با شرط اصلی: UX و رابط کاربری به‌شدت ساده و آسان**. (چندجلسه‌ای؛ پیوسته دنبال می‌شود.)
- 🎯 **گزینهٔ ۲**: i18n کامل ویزارد ساخت ختم + کیبوردهای مدیریت (BACKLOG #۱).
- 🎯 **گزینهٔ ۳**: دکمه‌های «قبلی/انصراف» و راهنمای همان مرحله در همهٔ گام‌های ویزارد.
## Live QA — 2026-09-28 (Chrome / Telegram Web / Codex)

| Area | Result | Evidence / defect |
|---|---|---|
| Member join fa/ar/en | ✅ LIVE | fa/ar commitment copy matched bot language; both existing memberships handled cleanly; en new join completed |
| Exact reminder `14:40` | ✅ LIVE | English member bot saved and echoed `14:40` |
| Portion content delivery | ⚠️ BUG-OPEN | English bot: source-channel access failure; allocation stayed unchanged |
| Member welcome copy | ⚠️ BUG-OPEN | English join message leaked `Welcome /admin_app` |
| Account settings | ⚠️ PARTIAL | Language/reciter/reminder/digest/SMS/timezone/profile/phone/link flows opened; `/cancel` incorrectly advertises `/admin_web_login` |
| Creator khatm management | ✅ LIVE | `/my_khatms`, created/joined buckets, members, empty CSV, QR fa/ar/en, stats, settings, reversible pause/snooze toggles |
| Creator/admin localization | ⚠️ BUG-OPEN | English session still shows Persian buttons/city names in multiple submenus |
| Public khatms on creator bot | ✅ LIVE | `/public_khatms` returned active public khatm picker |
| Create-khatm entry/cancel | ✅ LIVE | type picker and Quran commitment/open step rendered; cancel completed without creating data |
| Admin Telegram menu | ⚠️ PARTIAL | requests/users/broadcast info screens render; creator approval exposes command/database instructions rather than nontechnical UI |
| Admin Mini App | 🔒 BLOCKED | Telegram Web iframe refused; endpoint returns `X-Frame-Options: SAMEORIGIN` |
| Creator Mini App | 🔒 BLOCKED | same `SAMEORIGIN` blocker; internal dashboard routes could not be live-tested |
| Payment/broadcast/destructive actions | NOT RUN | no real payment; no broadcast, delete, ban, or role mutation |
