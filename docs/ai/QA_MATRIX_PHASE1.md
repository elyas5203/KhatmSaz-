# QA MATRIX — فاز ۱ کامل (نیازمندی ← کد ← تست ← نتیجه)

> ساخت: 2026-09-28 [Claude Code]. پوششِ همهٔ بخش‌های خواسته‌شدهٔ هدف. هر ادعا در کد فعلی چک شده.
> وضعیت: ✅ VERIFIED (کد+تست) · 🧪 UNIT/RENDER-ONLY · 🔵 NEEDS-LIVE (تلگرام/حساب دوم/Postgres) · ⚠️ BUG-OPEN · 🔒 BLOCKED.
> **قانون:** «تست‌نشده» = PASS نیست. جریان‌های بات که تلگرام زنده می‌خواهند = 🔵 (مالک live تست می‌کند).

## A. زیرساخت چندبات (۲۶ بات)
| نیازمندی | کد | وضعیت |
|---|---|---|
| ۲۶ بات: ۲ سازنده + ۲۴ ممبر (۴ دسته × ۳ زبان × ۲ پلتفرم) | `modules/bot_registry/models.py` (BotCategory: QURAN/SALAWAT/DUA_ZIYARAT/LAAN)، `core/bot_registry.py` | 🧪 ساختار موجود |
| دو Dispatcher (dp_creator/dp_member) + routerهای مشترک | `bootstrap.py` | ✅ کد + import‌های تمیز |
| تلگرام + بله (API سازگار) | `bot/telegram/client.py`، `bot/bale/client.py` | 🧪 هر دو موجود؛ 🔵 بله live تست‌نشده |
| توکن رمزنگاری‌شده (Fernet) در `bot_instances` | `modules/bot_registry/service.py` | 🧪 |
| زبان ثابت هر بات ممبر روی همهٔ پیام‌ها | `member_start`, `resume_join_after_registration` (رفع 2026-09-28) | ✅ رفع بحرانی en/ar |

## B. ثبت‌نام
| نیازمندی | کد | وضعیت |
|---|---|---|
| ثبت‌نام عضو (اشتراک شماره، بدون OTP) | `member_registration.py` | 🔵 NEEDS-LIVE |
| ثبت‌نام سازنده (OTP) | `registration.py` + `modules/phone` | 🔵 NEEDS-LIVE |
| رد دستور به‌عنوان نام (`/admin_app`) | enter_name (رفع 2026-09-28) | ✅ رفع + هر دو مسیر |
| نام/شهر/استان/جنسیت | registration FSM | 🧪 تست‌های موجود |

## C. ساخت ۴ نوع ختم
| نیازمندی | کد | وضعیت |
|---|---|---|
| انواع: QURAN_PAGE/QURAN_SURAH/SALAWAT/DUA/ZIYARAT | `khatm/models.py KhatmTemplateType` | 🔵 NEEDS-LIVE (Codex: قرآن/لعن OK) |
| نیت ثابت + نیابت اختیاری | `_compose_niyyat` (DEC-PY-0090) | ✅ کد + رفع تکرار نیابت |
| حذف مرحلهٔ فرمت محتوا (AUTO) | `choose_edition` (DEC-PY-0091) | ✅ کد |
| گام انتخاب پیام‌رسان/زبان لینک | `show_invite_platform/languages_keyboard` | ✅ کرش رفع + fallback |
| ⚠️ **تخصیص صفحات قرآن پیوستهٔ شخصی** (۴,۵→۶,۷) | allocation engine | ⚠️ **BUG-OPEN** (پرش دیده شد؛ باگ بحرانی) |
| ⚠️ ترتیب اجباری FSM (ساعت قبل از ثبت سهم) | join flow | ⚠️ **BUG-OPEN** |

## D. دعوت و عضویت
| نیازمندی | کد | وضعیت |
|---|---|---|
| لینک دعوت بات ممبر (per lang×platform) | `bot/invite_links.py`, `finish_invite_links` | ✅ + QR |
| صفحهٔ وب `/join/{token}` دکمهٔ بات ممبر | `public_join_landing` | ✅ render-verified |
| دکمهٔ «شرکت» مقاوم به ری‌استارت | `member_start.handle_member_join_callback` | ✅ فیلتر state حذف شد |
| دکمه‌های عضویت/تعهد به زبان بات | `join_preview/commitment_consent_keyboard(lang)` | ✅ fa/ar/en |
| ختم خصوصی → تأیید سازنده | `join_requests.py` | 🔵 NEEDS-LIVE (حساب دوم) |

## E. سهم و یادآوری
| نیازمندی | کد | وضعیت |
|---|---|---|
| پرسیدن ساعت در هر عضویت تازه | `resume_join_after_registration` | ✅ کد؛ 🔵 live |
| ساعت per-khatm + فرمت تایپی «14:40» | `member_my_khatms` + AskDeliveryHour | ✅ |
| تکمیل سهم/تعویق/snooze زبان‌محور | `portions.py`, `snooze_keyboard(lang)` | ✅ i18n |
| ⚠️ انتخاب فرمت محتوا توسط کاربر (تصویر/متن/ترجمه/صوت) | — | ⚠️ **BUG-OPEN** (الان متن+ترجمه شلوغ) |
| ⚠️ بازنویسی گرمِ پیام‌های یادآوری/تأیید | i18n | ⚠️ **BUG-OPEN** (مالک «مسخره» خواند) |

## F. مدیریت ختم / گزارش / پشتیبانی / تنظیمات
| نیازمندی | کد | وضعیت |
|---|---|---|
| مدیریت ختم: اعضا/CSV/QR/آمار/تنظیمات/لغو | `my_khatms.py` | 🔵 NEEDS-LIVE |
| منوی سازنده + دکمه‌های مالی/راهنما | `panel.py` (رفع دکمه‌های مرده) | ✅ + تست |
| گزارش شخصی | `report.py` | 🔵 live |
| پشتیبانی/تیکت | `suggestions.py` | 🔵 (Codex: تیکت ثبت شد) |
| تنظیمات (زبان/قاری/یادآوری/پیامک/…) | `settings_menu.py` + خانواده | 🧪 تست‌های موجود |
| `/public_khatms` روی هر دو بات | shared router (رفع 2026-09-28) | ✅ |

## G. زبان‌ها (fa/ar/en)
| نیازمندی | کد | وضعیت |
|---|---|---|
| هر i18n key سه‌زبانه | `i18n/__init__.py` | ✅ ۰ کلید ناقص از ۸۱۲ (گارد: `test_i18n_coverage.py`) |
| ⚠️ چند صفحهٔ انگلیسی دکمه/نام فارسی | متفرق | ⚠️ BUG-OPEN (Codex) |

## H. پرداخت
| نیازمندی | کد | وضعیت |
|---|---|---|
| درگاه PayPing پشت Provider | `wallet/payping.py`, `/payments/payping/callback` | 🧪 کد؛ 🔵 live |
| ضدجعل/replay (compare-and-swap روی `used`) | `wallet/models.py PendingPayment` | 🧪 نیاز تأیید cleanup |
| ⚠️ گواهی SSL callback نامعتبر | زیرساخت `api.khedmatgozaran.com` | 🔒 BLOCKED (اقدام مالک) |
| پیامک (کاوه‌نگار، فقط outbound، بدون وب‌هوک) | `modules/sms/provider.py` | ✅ تست‌های provider موجود؛ نیاز `.env` |

## I. Mini App + پنل ادمین
| نیازمندی | کد | وضعیت |
|---|---|---|
| مینی‌اپ ادمین/کریتور (احراز initData) | `/mini/admin`, `/mini/creator`, `telegram_mini_app.py` | ✅ iframe در تلگرام‌وب رفع شد (CSP) |
| دستور ورود مینی‌اپ در چت | `/admin_app`, `/creator_app` | ⚠️ BUG-OPEN (باید دستور در چت بیاید) |
| پنل ادمین: ۱۲ صفحه، همه از nav قابل‌دسترس | `web/app.py`, `base.html` | ✅ ۰ صفحهٔ یتیم |
| داشبورد هاب + کارت‌های دسترسی سریع | `dashboard.html` | ✅ render-verified |
| صفحهٔ دعاها (CRUD + وضعیت صریح) | `/devotionals` | ✅ render-verified |
| ⚠️ **ریدیزاین کامل پنل ادمین+کریتور** (finance ساده با مثال، فرم‌ها) | — | ⚠️ BUG-OPEN (سشن اختصاصی — سپرده به Codex) |

## جمع‌بندی فاز ۱
- **✅ رفع‌شده با شاهد کدمحور:** زیرساخت بات، زبان بات ممبر، دعوت/عضویت، دکمه‌های مرده، i18n coverage، مینی‌اپ iframe، صفحهٔ دعاها/داشبورد.
- **⚠️ BUG-OPEN (اولویت‌دار، برای Codex/سشن بعد):** تخصیص صفحات قرآن، ترتیب FSM، فرمت محتوا، بازنویسی پیام‌ها، i18n متفرق، دستور مینی‌اپ در چت، ریدیزاین کامل پنل.
- **🔵 NEEDS-LIVE (مالک):** ثبت‌نام، جریان عضویت/تأیید عضو، پرداخت، بله.
- **🔒 BLOCKED (مالک):** گواهی SSL پرداخت، Postgres تستی.
